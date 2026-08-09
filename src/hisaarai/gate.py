"""Deterministic Hisaar Gate authority."""

from __future__ import annotations

import datetime as dt
import uuid

from hisaarai.contracts import (
    Incident,
    IncidentState,
    PaymentProposal,
    SandboxReceipt,
    StateEvent,
    VendorRecord,
)
from hisaarai.observability import trace_id_for
from hisaarai.store import AuthorityStore, ConflictError


LEGAL_TRANSITIONS: dict[IncidentState, set[IncidentState]] = {
    IncidentState.DETECTED: {
        IncidentState.QUARANTINED,
        IncidentState.PLAN_READY,
        IncidentState.BLOCKED,
    },
    IncidentState.QUARANTINED: {IncidentState.INVESTIGATING, IncidentState.BLOCKED},
    IncidentState.INVESTIGATING: {IncidentState.PLAN_READY, IncidentState.BLOCKED},
    IncidentState.PLAN_READY: {
        IncidentState.AWAITING_APPROVAL,
        IncidentState.BLOCKED,
    },
    IncidentState.AWAITING_APPROVAL: {
        IncidentState.APPROVED,
        IncidentState.BLOCKED,
    },
    IncidentState.APPROVED: {IncidentState.COMPLETED, IncidentState.BLOCKED},
    IncidentState.COMPLETED: {IncidentState.VERIFIED, IncidentState.BLOCKED},
    IncidentState.VERIFIED: set(),
    IncidentState.BLOCKED: set(),
}


class HisaarGate:
    def __init__(self, store: AuthorityStore) -> None:
        self.store = store

    def open_incident(
        self,
        *,
        invoice_id: str,
        correlation_id: str,
        business_idempotency_key: str,
        incident_id: str | None = None,
        attempt_id: str | None = None,
    ) -> Incident:
        now = dt.datetime.now(dt.UTC)
        incident = Incident(
            incident_id=incident_id or f"inc-{uuid.uuid4().hex[:12]}",
            attempt_id=attempt_id or f"att-{uuid.uuid4().hex[:10]}",
            invoice_id=invoice_id,
            business_idempotency_key=business_idempotency_key,
            state=IncidentState.DETECTED,
            version=1,
            correlation_id=correlation_id,
            trace_id=trace_id_for(correlation_id),
            created_at=now,
            updated_at=now,
            state_history=[
                StateEvent(
                    state=IncidentState.DETECTED,
                    version=1,
                    at=now,
                )
            ],
        )
        return self.store.create_incident(incident)

    def transition(
        self,
        incident: Incident,
        new_state: IncidentState,
        *,
        reason: str | None = None,
        changes: dict[str, object] | None = None,
    ) -> Incident:
        if new_state not in LEGAL_TRANSITIONS[incident.state]:
            raise ConflictError(
                f"Illegal transition {incident.state.value} -> {new_state.value}"
            )
        if new_state == IncidentState.BLOCKED and not reason:
            raise ValueError("BLOCKED requires a reason")
        payload: dict[str, object] = {
            "reason": reason,
            "updated_at": dt.datetime.now(dt.UTC),
        }
        payload.update(changes or {})
        return self.store.transition(
            incident.incident_id,
            expected_state=incident.state,
            expected_version=incident.version,
            new_state=new_state,
            changes=payload,
        )

    def evaluate_proposal(
        self,
        incident: Incident,
        proposal: PaymentProposal,
        vendor: VendorRecord,
        evidence_changes: dict[str, object] | None = None,
    ) -> Incident:
        if incident.state != IncidentState.DETECTED:
            raise ConflictError("Proposal can only be evaluated from DETECTED")
        changes: dict[str, object] = {
            "proposal": proposal,
            "trusted_vendor": vendor,
        }
        changes.update(evidence_changes or {})
        if proposal.vendor_id != vendor.vendor_id:
            return self.transition(
                incident,
                IncidentState.BLOCKED,
                reason="VENDOR_ID_MISMATCH",
                changes=changes,
            )
        if proposal.bank_fingerprint != vendor.bank_fingerprint:
            return self.transition(
                incident,
                IncidentState.QUARANTINED,
                reason="BANK_FINGERPRINT_MISMATCH",
                changes=changes,
            )
        return self.transition(
            incident,
            IncidentState.PLAN_READY,
            reason="CLEAN_CONTROL_READY",
            changes=changes,
        )

    @staticmethod
    def receipt_matches(incident: Incident, receipt: SandboxReceipt) -> bool:
        if incident.warrant is None:
            return False
        warrant = incident.warrant
        return (
            receipt.business_idempotency_key == incident.business_idempotency_key
            and receipt.incident_id == incident.incident_id
            and receipt.attempt_id == incident.attempt_id
            and receipt.warrant_digest == warrant.digest
            and receipt.vendor_id == warrant.vendor_id
            and receipt.amount_minor == warrant.amount_minor
            and receipt.currency == warrant.currency
            and receipt.bank_fingerprint == warrant.bank_fingerprint
            and incident.trusted_vendor is not None
            and receipt.bank_fingerprint == incident.trusted_vendor.bank_fingerprint
            and warrant.trusted_vendor_version == incident.trusted_vendor.version
        )

    def verify_receipt(
        self,
        incident: Incident,
        receipt: SandboxReceipt,
        *,
        witness_summary: str | None = None,
    ) -> Incident:
        if incident.state != IncidentState.COMPLETED or incident.warrant is None:
            raise ConflictError("Verification requires COMPLETED incident and warrant")
        matches = self.receipt_matches(incident, receipt)
        if not matches:
            return self.transition(
                incident,
                IncidentState.BLOCKED,
                reason="VERIFICATION_DISAGREEMENT",
                changes={
                    "verification": "MISMATCH",
                    "witness_summary": witness_summary,
                },
            )
        return self.transition(
            incident,
            IncidentState.VERIFIED,
            changes={
                "verification": "MATCH",
                "witness_summary": witness_summary,
            },
        )
