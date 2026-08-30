"""Human approval and clean, exactly-once sandbox recovery."""

from __future__ import annotations

import datetime as dt
import uuid

from hisaarai.config import Settings
from hisaarai.contracts import (
    CleanExecutionRequest,
    Incident,
    IncidentState,
    SandboxReceipt,
)
from hisaarai.gate import HisaarGate
from hisaarai.observability import stage_span
from hisaarai.recovery_runtime import RecoveryRuntimeClient
from hisaarai.sandbox_erp import SandboxERP
from hisaarai.store import AuthorityStore, ConflictError


class GovernedRecovery:
    def __init__(
        self,
        *,
        settings: Settings,
        store: AuthorityStore,
        runtime: RecoveryRuntimeClient | None = None,
    ) -> None:
        self.settings = settings
        self.store = store
        self.gate = HisaarGate(store)
        self.runtime = runtime or RecoveryRuntimeClient(settings)
        self.erp = SandboxERP(store)

    def approve(
        self,
        incident_id: str,
        *,
        commander_subject: str,
        warrant_digest: str,
        now: dt.datetime | None = None,
    ) -> Incident:
        if commander_subject != self.settings.commander_subject:
            raise PermissionError("Commander identity is not allowlisted")
        incident = self.store.get_incident(incident_id)
        if incident.state != IncidentState.AWAITING_APPROVAL or incident.warrant is None:
            raise ConflictError("Incident is not awaiting a current warrant approval")
        warrant = incident.warrant
        current_time = now or dt.datetime.now(dt.UTC)
        if current_time >= warrant.expires_at:
            return self.gate.transition(
                incident,
                IncidentState.BLOCKED,
                reason="WARRANT_EXPIRED",
            )
        if warrant_digest != warrant.digest:
            raise ConflictError("Approval digest does not match the current warrant")
        vendor = self.store.get_vendor(warrant.vendor_id)
        if (
            vendor.version != warrant.trusted_vendor_version
            or vendor.bank_fingerprint != warrant.bank_fingerprint
        ):
            return self.gate.transition(
                incident,
                IncidentState.BLOCKED,
                reason="TRUSTED_SOURCE_CHANGED",
            )
        return self.gate.transition(
            incident,
            IncidentState.APPROVED,
            changes={
                "reason": None,
                "approved_by": commander_subject,
                "approved_at": current_time,
            },
        )

    def reject(
        self,
        incident_id: str,
        *,
        commander_subject: str,
        rationale: str,
    ) -> Incident:
        if commander_subject != self.settings.commander_subject:
            raise PermissionError("Commander identity is not allowlisted")
        incident = self.store.get_incident(incident_id)
        if incident.state != IncidentState.AWAITING_APPROVAL:
            raise ConflictError("Incident is not awaiting approval")
        rationale = rationale.strip()
        if not rationale:
            raise ValueError("Rejection rationale is required")
        return self.gate.transition(
            incident,
            IncidentState.BLOCKED,
            reason="HUMAN_REJECTED",
            changes={
                "rejected_by": commander_subject,
                "rejection_rationale": rationale[:300],
            },
        )

    def retry_expired(self, incident_id: str) -> Incident:
        expired = self.store.get_incident(incident_id)
        if (
            expired.state != IncidentState.BLOCKED
            or expired.reason != "WARRANT_EXPIRED"
            or expired.proposal is None
            or expired.trusted_vendor is None
        ):
            raise ConflictError("Only an expired warrant can start a new attempt")
        suffix = uuid.uuid4().hex[:10]
        fresh = self.gate.open_incident(
            invoice_id=expired.invoice_id,
            correlation_id=f"{expired.correlation_id}:retry:{suffix}",
            business_idempotency_key=expired.business_idempotency_key,
            incident_id=f"{expired.incident_id}-retry-{suffix}",
            attempt_id=f"att-{suffix}",
        )
        return self.gate.evaluate_proposal(
            fresh,
            expired.proposal,
            expired.trusted_vendor,
            evidence_changes={
                "screening_decision": expired.screening_decision,
                "screening_pdf_decision": expired.screening_pdf_decision,
                "screening_text_decision": expired.screening_text_decision,
                "gemini_invocations": expired.gemini_invocations,
            },
        )

    def execute_and_verify(
        self,
        incident_id: str,
    ) -> tuple[Incident, SandboxReceipt | None]:
        incident = self.store.get_incident(incident_id)
        existing = self.store.get_receipt(incident.business_idempotency_key)
        if existing and incident.state == IncidentState.VERIFIED:
            if not self.gate.receipt_matches(incident, existing):
                raise ConflictError("VERIFIED_RECEIPT_DISAGREEMENT")
            return incident, existing
        if incident.warrant is None:
            raise ConflictError("APPROVAL_REQUIRED")
        warrant = incident.warrant
        if incident.state == IncidentState.COMPLETED:
            if existing is None:
                raise ConflictError("COMPLETED_RECEIPT_MISSING")
            if not self.gate.receipt_matches(incident, existing):
                return self.gate.verify_receipt(incident, existing), existing
            completed = incident
            receipt = existing
        else:
            if incident.state != IncidentState.APPROVED:
                raise ConflictError("APPROVAL_REQUIRED")
            clean_payload = {
                "incident_id": incident.incident_id,
                "attempt_id": incident.attempt_id,
                "warrant_id": warrant.warrant_id,
                "warrant_digest": warrant.digest,
                "vendor_id": warrant.vendor_id,
                "amount_minor": warrant.amount_minor,
                "currency": warrant.currency,
                "bank_fingerprint": warrant.bank_fingerprint,
            }
            with stage_span(
                incident.correlation_id,
                "clean_standby",
                incident_id=incident.incident_id,
            ):
                standby = self.runtime.execute(clean_payload)
            if standby.model_dump(exclude={"decision"}) != {
                "incident_id": incident.incident_id,
                "warrant_digest": warrant.digest,
                "vendor_id": warrant.vendor_id,
                "amount_minor": warrant.amount_minor,
                "currency": warrant.currency,
                "bank_fingerprint": warrant.bank_fingerprint,
            }:
                return self.gate.transition(
                    incident,
                    IncidentState.BLOCKED,
                    reason="STANDBY_OUTPUT_DISAGREEMENT",
                ), None
            request = CleanExecutionRequest(
                **clean_payload,
                business_idempotency_key=incident.business_idempotency_key,
            )
            with stage_span(
                incident.correlation_id,
                "sandbox_receipt",
                incident_id=incident.incident_id,
            ):
                receipt = self.erp.execute(
                    request,
                    executor_identity=self.settings.app_service_account,
                    reasoning_runtime_identity=(
                        self.settings.recovery_runtime_service_account
                    ),
                )
            completed = self.store.get_incident(incident.incident_id)
        deterministic_verdict = (
            "MATCH" if self.gate.receipt_matches(completed, receipt) else "MISMATCH"
        )
        try:
            with stage_span(
                incident.correlation_id,
                "shaahid_witness",
                incident_id=incident.incident_id,
            ):
                witness = self.runtime.witness({
                    "incident_id": incident.incident_id,
                    "receipt_id": receipt.receipt_id,
                    "deterministic_verdict": deterministic_verdict,
                    "checks": {
                        "warrant_digest": receipt.warrant_digest == warrant.digest,
                        "vendor": receipt.vendor_id == warrant.vendor_id,
                        "amount": receipt.amount_minor == warrant.amount_minor,
                        "currency": receipt.currency == warrant.currency,
                        "bank_fingerprint": (
                            receipt.bank_fingerprint == warrant.bank_fingerprint
                        ),
                    },
                })
        except Exception:
            blocked = self.gate.transition(
                completed,
                IncidentState.BLOCKED,
                reason="WITNESS_FAILED",
            )
            return blocked, receipt
        if witness.verdict != deterministic_verdict:
            blocked = self.gate.transition(
                completed,
                IncidentState.BLOCKED,
                reason="WITNESS_DISAGREEMENT",
                changes={"witness_summary": witness.summary},
            )
            return blocked, receipt
        verified = self.gate.verify_receipt(
            completed,
            receipt,
            witness_summary=witness.summary,
        )
        return verified, receipt
