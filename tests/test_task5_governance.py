from __future__ import annotations

import datetime as dt

import pytest

from hisaarai.config import Settings
from hisaarai.contracts import (
    AgentFinding,
    IncidentState,
    PaymentProposal,
    StandbyOutput,
    VendorRecord,
    WitnessOutput,
)
from hisaarai.gate import HisaarGate
from hisaarai.governance import GovernedRecovery
from hisaarai.recovery_flow import RecoveryFlow
from hisaarai.store import ConflictError, InMemoryStore


def settings() -> Settings:
    project = "hisaarai-agentic-2026"
    return Settings(
        project_id=project,
        location="us-central1",
        firestore_database="hisaarai",
        event_topic="hisaar-events",
        pubsub_audience="https://example/internal/pubsub/events",
        commander_oauth_client_id="client.apps.googleusercontent.com",
        commander_subject="commander-sub",
        app_service_account=f"hisaar-app@{project}.iam.gserviceaccount.com",
        ap_runtime_service_account=f"hisaar-ap-runtime@{project}.iam.gserviceaccount.com",
        recovery_runtime_service_account=(
            f"hisaar-recovery-runtime@{project}.iam.gserviceaccount.com"
        ),
        recovery_runtime_name="projects/1/locations/us-central1/reasoningEngines/1",
        ap_runtime_name="projects/1/locations/us-central1/reasoningEngines/2",
        model_armor_template="hisaarai-ingress",
        environment="test",
    )


class FakeRuntime:
    def __init__(self, witness_verdict: str = "MATCH") -> None:
        self.execute_payload: dict[str, object] | None = None
        self.witness_verdict = witness_verdict

    def plan(self, payload: dict[str, object]) -> list[AgentFinding]:
        configs = [
            ("Raasid", "gemini-3.5-flash-lite", "DEFAULT"),
            ("Kashif", "gemini-3.7-flash", "HIGH"),
            ("Muslih", "gemini-3.7-flash", "HIGH"),
        ]
        return [
            AgentFinding(
                agent=name,
                summary=f"{name} supplied bounded recovery evidence.",
                evidence_ids=[str(payload["incident_id"])],
                requested_model=model,
                actual_model=model,
                thinking_level=thinking,
            )
            for name, model, thinking in configs
        ]

    def execute(self, payload: dict[str, object]) -> StandbyOutput:
        self.execute_payload = payload
        return StandbyOutput(
            decision="EXECUTE_APPROVED_WARRANT",
            incident_id=str(payload["incident_id"]),
            warrant_digest=str(payload["warrant_digest"]),
            vendor_id=str(payload["vendor_id"]),
            amount_minor=int(payload["amount_minor"]),
            currency=str(payload["currency"]),
            bank_fingerprint=str(payload["bank_fingerprint"]),
        )

    def witness(self, payload: dict[str, object]) -> WitnessOutput:
        return WitnessOutput(
            verdict=self.witness_verdict,
            summary="Deterministic warrant, source and receipt fields agree.",
        )


CHECKPOINT = {
    "fact": "Recovery uses the trusted vendor master and excludes quarantine.",
    "memory_revision_name": "projects/p/locations/l/reasoningEngines/r/memories/m/revisions/v",
}


def awaiting(runtime: FakeRuntime) -> tuple[InMemoryStore, object]:
    store = InMemoryStore()
    gate = HisaarGate(store)
    vendor = VendorRecord(
        vendor_id="vendor-northstar",
        display_name="Northstar Medical Supplies",
        bank_fingerprint="PK-NSTAR-TRUSTED-8842",
        version=7,
    )
    store.put_vendor(vendor)
    incident = gate.open_incident(
        invoice_id="INV-2026-0819",
        correlation_id="corr-governance",
        business_idempotency_key="pay:INV-2026-0819",
    )
    proposal = PaymentProposal(
        invoice_id=incident.invoice_id,
        vendor_id=vendor.vendor_id,
        amount_minor=427_500_000,
        currency="PKR",
        bank_fingerprint="PK-ATTACKER-9911",
        requested_model="gemini-3.7-flash",
        actual_model="gemini-3.7-flash",
        thinking_level="MEDIUM",
        source_context_id="screened:contaminated-session",
    )
    quarantined = gate.evaluate_proposal(incident, proposal, vendor)
    planned = RecoveryFlow(
        settings=settings(),
        store=store,
        runtime=runtime,
        checkpoint_loader=lambda: CHECKPOINT,
    ).plan(quarantined.incident_id)
    return store, planned


def test_wrong_commander_cannot_change_state() -> None:
    runtime = FakeRuntime()
    store, incident = awaiting(runtime)
    recovery = GovernedRecovery(settings=settings(), store=store, runtime=runtime)
    with pytest.raises(PermissionError):
        recovery.approve(
            incident.incident_id,
            commander_subject="wrong-sub",
            warrant_digest=incident.warrant.digest,
        )
    assert store.get_incident(incident.incident_id).state == IncidentState.AWAITING_APPROVAL


def test_expired_warrant_blocks_without_receipt() -> None:
    runtime = FakeRuntime()
    store, incident = awaiting(runtime)
    recovery = GovernedRecovery(settings=settings(), store=store, runtime=runtime)
    blocked = recovery.approve(
        incident.incident_id,
        commander_subject="commander-sub",
        warrant_digest=incident.warrant.digest,
        now=incident.warrant.expires_at + dt.timedelta(seconds=1),
    )
    assert blocked.state == IncidentState.BLOCKED
    assert blocked.reason == "WARRANT_EXPIRED"
    assert store.get_receipt(incident.business_idempotency_key) is None


def test_expired_warrant_retry_uses_new_attempt_and_same_business_key() -> None:
    runtime = FakeRuntime()
    store, incident = awaiting(runtime)
    governed = GovernedRecovery(settings=settings(), store=store, runtime=runtime)
    expired = governed.approve(
        incident.incident_id,
        commander_subject="commander-sub",
        warrant_digest=incident.warrant.digest,
        now=incident.warrant.expires_at + dt.timedelta(seconds=1),
    )
    fresh = governed.retry_expired(expired.incident_id)
    replanned = RecoveryFlow(
        settings=settings(),
        store=store,
        runtime=runtime,
        checkpoint_loader=lambda: CHECKPOINT,
    ).plan(fresh.incident_id)
    assert replanned.incident_id != expired.incident_id
    assert replanned.attempt_id != expired.attempt_id
    assert replanned.business_idempotency_key == expired.business_idempotency_key
    assert replanned.state == IncidentState.AWAITING_APPROVAL
    assert replanned.warrant.digest != incident.warrant.digest


def test_one_human_decision_completes_once_and_replay_is_stable() -> None:
    runtime = FakeRuntime()
    store, incident = awaiting(runtime)
    recovery = GovernedRecovery(settings=settings(), store=store, runtime=runtime)
    approved = recovery.approve(
        incident.incident_id,
        commander_subject="commander-sub",
        warrant_digest=incident.warrant.digest,
    )
    assert approved.state == IncidentState.APPROVED
    verified, receipt = recovery.execute_and_verify(incident.incident_id)
    assert verified.state == IncidentState.VERIFIED
    assert receipt is not None
    assert receipt.executor_identity == settings().app_service_account
    assert (
        receipt.reasoning_runtime_identity
        == settings().recovery_runtime_service_account
    )
    replayed, same_receipt = recovery.execute_and_verify(incident.incident_id)
    assert replayed.state == IncidentState.VERIFIED
    assert same_receipt == receipt
    assert runtime.execute_payload is not None
    assert "contaminated-session" not in str(runtime.execute_payload)


def test_execution_before_approval_is_denied() -> None:
    runtime = FakeRuntime()
    store, incident = awaiting(runtime)
    with pytest.raises(ConflictError, match="APPROVAL_REQUIRED"):
        GovernedRecovery(
            settings=settings(),
            store=store,
            runtime=runtime,
        ).execute_and_verify(incident.incident_id)


def test_clean_control_completes_normally() -> None:
    runtime = FakeRuntime()
    store = InMemoryStore()
    gate = HisaarGate(store)
    vendor = VendorRecord(
        vendor_id="vendor-northstar",
        display_name="Northstar Medical Supplies",
        bank_fingerprint="PK-NSTAR-TRUSTED-8842",
        version=7,
    )
    store.put_vendor(vendor)
    incident = gate.open_incident(
        invoice_id="INV-2026-0820",
        correlation_id="corr-clean",
        business_idempotency_key="pay:INV-2026-0820",
    )
    clean = gate.evaluate_proposal(
        incident,
        PaymentProposal(
            invoice_id=incident.invoice_id,
            vendor_id=vendor.vendor_id,
            amount_minor=427_500_000,
            currency="PKR",
            bank_fingerprint=vendor.bank_fingerprint,
            requested_model="gemini-3.7-flash",
            actual_model="gemini-3.7-flash",
            thinking_level="MEDIUM",
            source_context_id="screened:clean-control",
        ),
        vendor,
    )
    assert clean.state == IncidentState.PLAN_READY
    awaiting_clean = RecoveryFlow(
        settings=settings(),
        store=store,
        runtime=runtime,
        checkpoint_loader=lambda: CHECKPOINT,
    ).prepare_clean(clean.incident_id)
    governed = GovernedRecovery(settings=settings(), store=store, runtime=runtime)
    governed.approve(
        awaiting_clean.incident_id,
        commander_subject="commander-sub",
        warrant_digest=awaiting_clean.warrant.digest,
    )
    verified, receipt = governed.execute_and_verify(awaiting_clean.incident_id)
    assert verified.state == IncidentState.VERIFIED
    assert receipt is not None
    assert receipt.bank_fingerprint == vendor.bank_fingerprint
