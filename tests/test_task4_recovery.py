from __future__ import annotations

import datetime as dt

from hisaarai.config import Settings
from hisaarai.contracts import (
    AgentFinding,
    IncidentState,
    PaymentProposal,
    VendorRecord,
)
from hisaarai.gate import HisaarGate
from hisaarai.recovery_flow import RecoveryFlow
from hisaarai.store import InMemoryStore


def settings() -> Settings:
    project = "hisaarai-agentic-2026"
    return Settings(
        project_id=project,
        location="us-central1",
        firestore_database="hisaarai",
        event_topic="hisaar-events",
        pubsub_audience="https://example/internal/pubsub/events",
        commander_oauth_client_id="client.apps.googleusercontent.com",
        commander_subject="commander",
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
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.payload: dict[str, object] | None = None

    def plan(self, payload: dict[str, object]) -> list[AgentFinding]:
        self.payload = payload
        if self.fail:
            raise TimeoutError("bounded role timeout")
        return [
            AgentFinding(
                agent="Raasid",
                summary="Observed the vendor fingerprint mismatch.",
                evidence_ids=[str(payload["incident_id"])],
                requested_model="gemini-3.5-flash-lite",
                actual_model="gemini-3.5-flash-lite",
                thinking_level="DEFAULT",
            ),
            AgentFinding(
                agent="Kashif",
                summary="The blast radius is one unexecuted proposal.",
                evidence_ids=[str(payload["incident_id"])],
                requested_model="gemini-3.6-flash",
                actual_model="gemini-3.6-flash",
                thinking_level="HIGH",
            ),
            AgentFinding(
                agent="Muslih",
                summary="Reconstruct payment from the trusted vendor master.",
                evidence_ids=[str(payload["incident_id"])],
                requested_model="gemini-3.6-flash",
                actual_model="gemini-3.6-flash",
                thinking_level="HIGH",
            ),
        ]


def quarantined(store: InMemoryStore):
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
        correlation_id="corr-recovery",
        business_idempotency_key="pay:INV-2026-0819",
    )
    proposal = PaymentProposal(
        invoice_id=incident.invoice_id,
        vendor_id=vendor.vendor_id,
        amount_minor=427_500_000,
        currency="PKR",
        bank_fingerprint="PK-ATTACKER-9911",
        requested_model="gemini-3.6-flash",
        actual_model="gemini-3.6-flash",
        thinking_level="MEDIUM",
        source_context_id="screened:contaminated-session",
    )
    return gate.evaluate_proposal(incident, proposal, vendor)


CHECKPOINT = {
    "fact": (
        "HisaarAI Day 0 continuity policy: exclude quarantined context and use "
        "the trusted vendor master."
    ),
    "memory_revision_name": "projects/p/locations/l/reasoningEngines/r/memories/m/revisions/v",
}


def test_recovery_uses_revision_and_excludes_contaminated_context() -> None:
    store = InMemoryStore()
    incident = quarantined(store)
    runtime = FakeRuntime()
    awaiting = RecoveryFlow(
        settings=settings(),
        store=store,
        runtime=runtime,
        checkpoint_loader=lambda: CHECKPOINT,
    ).plan(incident.incident_id)
    assert awaiting.state == IncidentState.AWAITING_APPROVAL
    assert awaiting.warrant is not None
    assert awaiting.warrant.continuity_revision_name == CHECKPOINT["memory_revision_name"]
    assert awaiting.warrant.bank_fingerprint == "PK-NSTAR-TRUSTED-8842"
    assert len(awaiting.findings) == 3
    payload = str(runtime.payload)
    assert "contaminated-session" not in payload
    assert "invoice text" not in payload.lower()


def test_recovery_planning_receives_major_currency_display_not_minor_units() -> None:
    store = InMemoryStore()
    incident = quarantined(store)
    runtime = FakeRuntime()

    RecoveryFlow(
        settings=settings(),
        store=store,
        runtime=runtime,
        checkpoint_loader=lambda: CHECKPOINT,
    ).plan(incident.incident_id)

    assert runtime.payload is not None
    proposal = runtime.payload["proposal"]
    assert proposal["amount_display"] == 4_275_000.0
    assert "amount_minor" not in proposal


def test_recovery_agent_failure_is_terminal_and_creates_no_warrant() -> None:
    store = InMemoryStore()
    incident = quarantined(store)
    blocked = RecoveryFlow(
        settings=settings(),
        store=store,
        runtime=FakeRuntime(fail=True),
        checkpoint_loader=lambda: CHECKPOINT,
    ).plan(incident.incident_id)
    assert blocked.state == IncidentState.BLOCKED
    assert blocked.reason == "RECOVERY_EVIDENCE_OR_AGENT_FAILED"
    assert blocked.warrant is None
    assert blocked.receipt_id is None
