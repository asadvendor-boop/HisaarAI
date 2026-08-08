from __future__ import annotations

import base64
import json

from fastapi.testclient import TestClient
import pytest

from hisaarai import auth
from hisaarai.app_factory import create_app
from hisaarai.config import Settings
from hisaarai.contracts import IncidentState
from hisaarai.events import EventEnvelope
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
