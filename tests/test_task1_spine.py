from __future__ import annotations

import base64
import json

from fastapi.testclient import TestClient
import pytest

from hisaarai import auth
from hisaarai.app_factory import create_app
from hisaarai.config import Settings
from hisaarai.contracts import (
    AgentFinding,
    CleanExecutionRequest,
    IncidentState,
    PaymentProposal,
    StandbyOutput,
    VendorRecord,
    WitnessOutput,
)
from hisaarai.events import EventEnvelope
from hisaarai.gate import HisaarGate
from hisaarai.governance import GovernedRecovery
from hisaarai.recovery_flow import RecoveryFlow
from hisaarai.store import InMemoryStore


APP_SA = "hisaar-app@hisaarai-agentic-2026.iam.gserviceaccount.com"


@pytest.fixture
def settings() -> Settings:
    return Settings(
        project_id="hisaarai-agentic-2026",
        location="us-central1",
        firestore_database="hisaarai",
        event_topic="hisaar-events",
        pubsub_audience="https://hisaar.example/internal/pubsub/events",
        commander_oauth_client_id="client.apps.googleusercontent.com",
        commander_subject="commander-subject",
        app_service_account=APP_SA,
        ap_runtime_service_account=(
            "hisaar-ap-runtime@hisaarai-agentic-2026.iam.gserviceaccount.com"
        ),
        recovery_runtime_service_account=(
            "hisaar-recovery-runtime@hisaarai-agentic-2026.iam.gserviceaccount.com"
        ),
        recovery_runtime_name="projects/1/locations/us-central1/reasoningEngines/1",
        ap_runtime_name="projects/1/locations/us-central1/reasoningEngines/2",
        model_armor_template="hisaarai-ingress",
        environment="test",
    )


def _push(event: dict[str, object]) -> dict[str, object]:
    data = base64.b64encode(json.dumps(event).encode()).decode()
    return {"message": {"data": data, "messageId": "pubsub-1"}}


class FakeRecoveryRuntime:
    def plan(self, payload: dict[str, object]) -> list[AgentFinding]:
        return [
            AgentFinding(
                agent=name,
                summary=f"{name} supplied bounded recovery evidence.",
                evidence_ids=[str(payload["incident_id"])],
                requested_model=model,
                actual_model=model,
                thinking_level=thinking,
            )
            for name, model, thinking in [
                ("Raasid", "gemini-3.5-flash-lite", "DEFAULT"),
                ("Kashif", "gemini-3.6-flash", "HIGH"),
                ("Muslih", "gemini-3.6-flash", "HIGH"),
            ]
        ]

    def execute(self, payload: dict[str, object]) -> StandbyOutput:
        return StandbyOutput(
            decision="EXECUTE_APPROVED_WARRANT",
            incident_id=str(payload["incident_id"]),
            warrant_digest=str(payload["warrant_digest"]),
            vendor_id=str(payload["vendor_id"]),
            amount_minor=int(payload["amount_minor"]),
            currency=str(payload["currency"]),
            bank_fingerprint=str(payload["bank_fingerprint"]),
        )

    def witness(self, _payload: dict[str, object]) -> WitnessOutput:
        return WitnessOutput(
            verdict="MATCH",
            summary="Deterministic warrant, source and receipt fields agree.",
        )


class RecordingPublisher:
    def __init__(self, *, fail_first: bool = False) -> None:
        self.fail_first = fail_first
        self.events: list[EventEnvelope] = []

    def publish(self, event: EventEnvelope) -> str:
        self.events.append(event)
        if self.fail_first and len(self.events) == 1:
            raise RuntimeError("simulated publisher outage")
        return event.event_id


def _awaiting_approval(
    settings: Settings,
) -> tuple[InMemoryStore, object, GovernedRecovery]:
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
        correlation_id="corr-command-room",
        business_idempotency_key="pay:INV-2026-0819",
    )
    quarantined = gate.evaluate_proposal(
        incident,
        PaymentProposal(
            invoice_id=incident.invoice_id,
            vendor_id=vendor.vendor_id,
            amount_minor=427_500_000,
            currency="PKR",
            bank_fingerprint="PK-ATTACKER-9911",
            requested_model="gemini-3.6-flash",
            actual_model="gemini-3.6-flash",
            thinking_level="MEDIUM",
            source_context_id="screened:contaminated-session",
        ),
        vendor,
    )
    runtime = FakeRecoveryRuntime()
    awaiting = RecoveryFlow(
        settings=settings,
        store=store,
        runtime=runtime,
        checkpoint_loader=lambda: {
            "fact": "Recovery uses the trusted vendor master.",
            "memory_revision_name": "memory-revision-1",
        },
    ).plan(quarantined.incident_id)
    return store, awaiting, GovernedRecovery(
        settings=settings,
        store=store,
        runtime=runtime,
    )


def _commander_claims(settings: Settings) -> dict[str, object]:
    return {
        "iss": "https://accounts.google.com",
        "sub": settings.commander_subject,
        "email": "commander@example.com",
    }


def _commander_headers() -> dict[str, str]:
    return {
        "Authorization": "Bearer signed-google-token",
        "Origin": "http://testserver",
    }


def test_event_envelope_rejects_unknown_types() -> None:
    with pytest.raises(ValueError):
        EventEnvelope.model_validate(
            {
                "event_id": "event-001",
                "event_type": "unknown",
                "idempotency_key": "key-1",
                "correlation_id": "corr-1",
                "payload": {},
            }
        )


def test_health_is_public(settings: Settings) -> None:
    client = TestClient(create_app(settings))
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["project"] == "hisaarai-agentic-2026"


def test_pubsub_route_requires_bearer(settings: Settings) -> None:
    client = TestClient(create_app(settings))
    response = client.post(
        "/internal/pubsub/events",
        json=_push(
            {
                "event_id": "event-001",
                "event_type": "invoice.received",
                "idempotency_key": "invoice-001",
                "correlation_id": "corr-001",
                "payload": {},
            }
        ),
    )
    assert response.status_code == 401


def test_pubsub_route_accepts_only_expected_identity(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    def verified_claims(_token: str, _request: object, audience: str) -> dict[str, object]:
        assert audience == settings.pubsub_audience
        return {
            "iss": "https://accounts.google.com",
            "sub": "service-subject",
            "email": APP_SA,
            "email_verified": True,
        }

    monkeypatch.setattr(auth.id_token, "verify_oauth2_token", verified_claims)
    class StubInvoiceFlow:
        def process_fixture(self, **_kwargs: object) -> object:
            return type(
                "StubIncident",
                (),
                {"incident_id": "inc-event-001", "state": IncidentState.BLOCKED},
            )()

    client = TestClient(
        create_app(
            settings,
            store=InMemoryStore(),
            invoice_flow=StubInvoiceFlow(),
        )
    )
    response = client.post(
        "/internal/pubsub/events",
        headers={"Authorization": "Bearer signed-google-token"},
        json=_push(
            {
                "event_id": "event-001",
                "event_type": "invoice.received",
                "idempotency_key": "invoice-001",
                "correlation_id": "corr-001",
                "payload": {"fixture": "injection-control"},
            }
        ),
    )
    assert response.status_code == 200
    assert response.json() == {
        "accepted": True,
        "event_id": "event-001",
        "incident_id": "inc-event-001",
        "state": "BLOCKED",
    }


def test_pubsub_route_rejects_wrong_service_account(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        auth.id_token,
        "verify_oauth2_token",
        lambda *_args, **_kwargs: {
            "iss": "accounts.google.com",
            "sub": "other",
            "email": "other@hisaarai-agentic-2026.iam.gserviceaccount.com",
            "email_verified": True,
        },
    )
    client = TestClient(create_app(settings))
    response = client.post(
        "/internal/pubsub/events",
        headers={"Authorization": "Bearer signed-google-token"},
        json=_push(
            {
                "event_id": "event-001",
                "event_type": "invoice.received",
                "idempotency_key": "invoice-001",
                "correlation_id": "corr-001",
                "payload": {},
            }
        ),
    )
    assert response.status_code == 403


def test_exact_approval_retry_republishes_stable_event_after_publisher_failure(
    settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, incident, governed = _awaiting_approval(settings)
    publisher = RecordingPublisher(fail_first=True)
    monkeypatch.setattr(
        auth.id_token,
        "verify_oauth2_token",
        lambda *_args, **_kwargs: _commander_claims(settings),
    )
    client = TestClient(
        create_app(
            settings,
            store=store,
            governed_recovery=governed,
            publisher=publisher,
        ),
        raise_server_exceptions=False,
    )
    payload = {"warrant_digest": incident.warrant.digest}

    failed = client.post(
        f"/api/commander/incidents/{incident.incident_id}/approve",
        headers=_commander_headers(),
        json=payload,
    )

    assert failed.status_code == 503
    assert store.get_incident(incident.incident_id).state == IncidentState.APPROVED

    wrong_digest = client.post(
        f"/api/commander/incidents/{incident.incident_id}/approve",
        headers=_commander_headers(),
        json={"warrant_digest": "0" * 64},
    )

    assert wrong_digest.status_code == 409
    assert len(publisher.events) == 1

    retried = client.post(
        f"/api/commander/incidents/{incident.incident_id}/approve",
        headers=_commander_headers(),
        json=payload,
    )

    assert retried.status_code == 202
    assert retried.json() == {"accepted": True, "state": "APPROVED"}
    assert [event.event_id for event in publisher.events] == [
        f"execute-{incident.attempt_id}",
        f"execute-{incident.attempt_id}",
    ]


def test_terminal_approval_retry_does_not_publish_and_replay_returns_receipt(
    settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, incident, governed = _awaiting_approval(settings)
    publisher = RecordingPublisher()
    monkeypatch.setattr(
        auth.id_token,
        "verify_oauth2_token",
        lambda *_args, **_kwargs: _commander_claims(settings),
    )
    client = TestClient(
        create_app(
            settings,
            store=store,
            governed_recovery=governed,
            publisher=publisher,
        )
    )
    payload = {"warrant_digest": incident.warrant.digest}
    approved = client.post(
        f"/api/commander/incidents/{incident.incident_id}/approve",
        headers=_commander_headers(),
        json=payload,
    )
    assert approved.status_code == 202
    verified, receipt = governed.execute_and_verify(incident.incident_id)
    assert verified.state == IncidentState.VERIFIED
    assert receipt is not None

    terminal = client.post(
        f"/api/commander/incidents/{incident.incident_id}/approve",
        headers=_commander_headers(),
        json=payload,
    )
    replayed = client.post(
        f"/api/commander/incidents/{incident.incident_id}/replay",
        headers=_commander_headers(),
        json={},
    )

    assert terminal.status_code == 202
    assert terminal.json() == {"accepted": False, "state": "VERIFIED"}
    assert len(publisher.events) == 1
    assert replayed.status_code == 200
    assert replayed.json() == {
        "state": "VERIFIED",
        "receipt_id": receipt.receipt_id,
        "replay": "MATCH",
    }


def test_replay_recomputes_the_bound_receipt_comparison(
    settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, incident, governed = _awaiting_approval(settings)
    monkeypatch.setattr(
        auth.id_token,
        "verify_oauth2_token",
        lambda *_args, **_kwargs: _commander_claims(settings),
    )
    governed.approve(
        incident.incident_id,
        commander_subject=settings.commander_subject,
        warrant_digest=incident.warrant.digest,
    )
    verified, receipt = governed.execute_and_verify(incident.incident_id)
    assert verified.state == IncidentState.VERIFIED
    assert receipt is not None
    store._receipts[incident.business_idempotency_key] = receipt.model_copy(
        update={"bank_fingerprint": "PK-DISAGREEMENT-0000"}
    )
    client = TestClient(
        create_app(settings, store=store, governed_recovery=governed)
    )

    replayed = client.post(
        f"/api/commander/incidents/{incident.incident_id}/replay",
        headers=_commander_headers(),
        json={},
    )

    assert replayed.status_code == 409
    assert replayed.json()["detail"] == "Replay receipt comparison failed"


def test_completed_receipt_resumes_verification_without_a_second_mutation(
    settings: Settings,
) -> None:
    store, incident, governed = _awaiting_approval(settings)
    approved = governed.approve(
        incident.incident_id,
        commander_subject=settings.commander_subject,
        warrant_digest=incident.warrant.digest,
    )
    assert approved.warrant is not None
    warrant = approved.warrant
    receipt = governed.erp.execute(
        CleanExecutionRequest(
            incident_id=approved.incident_id,
            attempt_id=approved.attempt_id,
            warrant_id=warrant.warrant_id,
            warrant_digest=warrant.digest,
            business_idempotency_key=approved.business_idempotency_key,
            vendor_id=warrant.vendor_id,
            amount_minor=warrant.amount_minor,
            currency=warrant.currency,
            bank_fingerprint=warrant.bank_fingerprint,
        ),
        executor_identity=settings.recovery_runtime_service_account,
    )
    assert store.get_incident(approved.incident_id).state == IncidentState.COMPLETED

    resumed, same_receipt = governed.execute_and_verify(approved.incident_id)

    assert resumed.state == IncidentState.VERIFIED
    assert same_receipt == receipt
    assert store.get_receipt(approved.business_idempotency_key) == receipt


def test_replay_rejects_non_verified_incident(
    settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, incident, governed = _awaiting_approval(settings)
    monkeypatch.setattr(
        auth.id_token,
        "verify_oauth2_token",
        lambda *_args, **_kwargs: _commander_claims(settings),
    )
    client = TestClient(
        create_app(settings, store=store, governed_recovery=governed)
    )

    response = client.post(
        f"/api/commander/incidents/{incident.incident_id}/replay",
        headers=_commander_headers(),
        json={},
    )

    assert response.status_code == 409
