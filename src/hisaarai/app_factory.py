"""Application factory for the command room and deterministic authority."""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import urlparse
import uuid

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from google.cloud import pubsub_v1
from pydantic import BaseModel, ConfigDict, Field

from hisaarai.auth import AuthenticatedCaller, require_google_caller
from hisaarai.config import Settings
from hisaarai.continuity.service import create_checkpoint, get_checkpoint
from hisaarai.events import EventEnvelope, PubSubPush, decode_push
from hisaarai.governance import GovernedRecovery
from hisaarai.invoice_flow import InvoiceFlow
from hisaarai.observability import configure_tracing
from hisaarai.recovery_flow import RecoveryFlow
from hisaarai.store import ConflictError, FirestoreStore, NotFoundError


class ApprovalBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    warrant_digest: str = Field(min_length=64, max_length=64)


class RejectionBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rationale: str = Field(min_length=3, max_length=300)


class LaunchBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fixture: str


class EventPublisher(Protocol):
    def publish(self, event: EventEnvelope) -> str: ...


class GoogleEventPublisher:
    def __init__(self, settings: Settings) -> None:
        self.client = pubsub_v1.PublisherClient()
        self.topic = self.client.topic_path(settings.project_id, settings.event_topic)

    def publish(self, event: EventEnvelope) -> str:
        future = self.client.publish(
            self.topic,
            event.model_dump_json().encode(),
            event_type=event.event_type,
        )
        return str(future.result(timeout=20))


def _is_exact_approval_retry(
    incident: Any,
    *,
    commander_subject: str,
    warrant_digest: str,
) -> bool:
    return (
        incident.state.value in {"APPROVED", "COMPLETED", "VERIFIED"}
        and incident.warrant is not None
        and incident.approved_by == commander_subject
        and incident.warrant.digest == warrant_digest
    )


def _same_origin_json(request: Request) -> None:
    content_type = request.headers.get("content-type", "")
    if not content_type.lower().startswith("application/json"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Commander actions require JSON",
        )
    origin = request.headers.get("origin")
    if not origin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Commander action origin is required",
        )
    parsed = urlparse(origin)
    request_host = request.headers.get("host", "")
    if parsed.netloc != request_host or parsed.scheme not in {"http", "https"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Commander action must be same-origin",
        )


def create_app(
    settings: Settings | None = None,
    *,
    store: Any | None = None,
    invoice_flow: Any | None = None,
    recovery_flow: Any | None = None,
    governed_recovery: Any | None = None,
    publisher: EventPublisher | None = None,
) -> FastAPI:
    settings = settings or Settings.from_env(require_auth=True)
    if settings.environment == "production":
        configure_tracing(settings.project_id)
    store = store or FirestoreStore(
        project=settings.project_id,
        database=settings.firestore_database,
    )
    invoice_flow = invoice_flow or InvoiceFlow(settings=settings, store=store)
    recovery_flow = recovery_flow or RecoveryFlow(settings=settings, store=store)
    governed_recovery = governed_recovery or GovernedRecovery(
        settings=settings,
        store=store,
    )
    publisher = publisher or GoogleEventPublisher(settings)
    app = FastAPI(title="HisaarAI", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": "hisaarai",
            "project": settings.project_id,
        }

    web_dist = Path(os.getenv("HISAAR_WEB_DIST", "web/dist"))
    if (web_dist / "index.html").exists():
        app.mount("/assets", StaticFiles(directory=web_dist / "assets"), name="assets")

        @app.get("/", response_class=FileResponse)
        def command_room() -> FileResponse:
            return FileResponse(web_dist / "index.html")
    else:
        @app.get("/", response_class=HTMLResponse)
        def placeholder() -> str:
            return """
            <!doctype html><html lang="en"><head><meta charset="utf-8">
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <title>HisaarAI</title></head><body style="background:#07110f;color:#e6fff6;
            font-family:system-ui;padding:4rem"><main><p>HISAARAI // COMMAND</p>
            <h1>The agent was compromised.<br>The payment was not.</h1>
            <p>The governed recovery command room is ready for its web build.</p>
            </main></body></html>
            """

    @app.get("/api/config")
    def browser_config() -> dict[str, str]:
        return {
            "google_oauth_client_id": settings.commander_oauth_client_id,
            "project": settings.project_id,
        }

    @app.get("/api/incidents/{incident_id}")
    def read_incident(incident_id: str) -> dict[str, Any]:
        try:
            incident = store.get_incident(incident_id)
            receipt = store.get_receipt(incident.business_idempotency_key)
            if receipt is not None and receipt.incident_id != incident.incident_id:
                receipt = None
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail="Incident not found") from exc
        return {
            "incident": incident.model_dump(mode="json"),
            "receipt": receipt.model_dump(mode="json") if receipt else None,
        }

    @app.get("/api/continuity")
    def read_continuity() -> dict[str, object]:
        return {
            f"day_{day}": get_checkpoint(settings, day)
            for day in (0, 7, 14, 21)
        }

    commander_auth = require_google_caller(
        audience=settings.commander_oauth_client_id,
        expected_subject=settings.commander_subject,
    )
    identity_auth = require_google_caller(
        audience=settings.commander_oauth_client_id,
    )

    @app.get("/api/identity")
    def verified_identity(
        caller: AuthenticatedCaller = Depends(identity_auth),
    ) -> dict[str, str | None]:
        return {"subject": caller.subject, "email": caller.email}

    @app.post("/api/commander/launch", status_code=202)
    def launch(
        body: LaunchBody,
        request: Request,
        _caller: AuthenticatedCaller = Depends(commander_auth),
    ) -> dict[str, str]:
        _same_origin_json(request)
        if body.fixture not in {"injection-control", "semantic-tamper", "clean-control"}:
            raise HTTPException(status_code=400, detail="Unknown committed fixture")
        event_id = f"invoice-{uuid.uuid4().hex[:16]}"
        incident_id = f"inc-{event_id}"
        event = EventEnvelope(
            event_id=event_id,
            event_type="invoice.received",
            idempotency_key=f"fixture:{body.fixture}:{event_id}",
            correlation_id=f"corr-{uuid.uuid4().hex[:16]}",
            payload={"fixture": body.fixture},
        )
        publisher.publish(event)
        return {"incident_id": incident_id, "event_id": event_id}

    @app.post("/api/commander/incidents/{incident_id}/approve", status_code=202)
    def approve(
        incident_id: str,
        body: ApprovalBody,
        request: Request,
        caller: AuthenticatedCaller = Depends(commander_auth),
    ) -> dict[str, object]:
        _same_origin_json(request)
        try:
            approved = governed_recovery.approve(
                incident_id,
                commander_subject=caller.subject,
                warrant_digest=body.warrant_digest,
            )
        except (ConflictError, NotFoundError) as exc:
            try:
                approved = store.get_incident(incident_id)
            except NotFoundError:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            if not _is_exact_approval_retry(
                approved,
                commander_subject=caller.subject,
                warrant_digest=body.warrant_digest,
            ):
                raise HTTPException(status_code=409, detail=str(exc)) from exc
        if approved.state.value != "APPROVED":
            return {"accepted": False, "state": approved.state.value}
        event = EventEnvelope(
            event_id=f"execute-{approved.attempt_id}",
            event_type="recovery.execute",
            idempotency_key=approved.business_idempotency_key,
            correlation_id=approved.correlation_id,
            payload={"incident_id": approved.incident_id},
        )
        try:
            publisher.publish(event)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Recovery execution publish failed; retry the exact approval",
            ) from exc
        return {"accepted": True, "state": approved.state.value}

    @app.post("/api/commander/incidents/{incident_id}/replay")
    def replay(
        incident_id: str,
        request: Request,
        _caller: AuthenticatedCaller = Depends(commander_auth),
    ) -> dict[str, str]:
        _same_origin_json(request)
        try:
            incident = store.get_incident(incident_id)
            receipt = store.get_receipt(incident.business_idempotency_key)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail="Incident not found") from exc
        if (
            incident.state.value != "VERIFIED"
            or incident.verification != "MATCH"
            or receipt is None
            or receipt.incident_id != incident.incident_id
            or receipt.receipt_id != incident.receipt_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Replay requires a verified incident with its stable receipt",
            )
        return {
            "state": "VERIFIED",
            "receipt_id": receipt.receipt_id,
            "replay": "MATCH",
        }

    @app.post("/api/commander/incidents/{incident_id}/reject")
    def reject(
        incident_id: str,
        body: RejectionBody,
        request: Request,
        caller: AuthenticatedCaller = Depends(commander_auth),
    ) -> dict[str, str]:
        _same_origin_json(request)
        try:
            blocked = governed_recovery.reject(
                incident_id,
                commander_subject=caller.subject,
                rationale=body.rationale,
            )
        except (ConflictError, NotFoundError, ValueError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {"state": blocked.state.value, "reason": blocked.reason or ""}

    @app.post("/api/commander/incidents/{incident_id}/retry-expired")
    def retry_expired(
        incident_id: str,
        request: Request,
        _caller: AuthenticatedCaller = Depends(commander_auth),
    ) -> dict[str, str]:
        _same_origin_json(request)
        try:
            fresh = governed_recovery.retry_expired(incident_id)
            if fresh.state.value == "QUARANTINED":
                fresh = recovery_flow.plan(fresh.incident_id)
            elif fresh.state.value == "PLAN_READY":
                fresh = recovery_flow.prepare_clean(fresh.incident_id)
        except (ConflictError, NotFoundError, ValueError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {"incident_id": fresh.incident_id, "state": fresh.state.value}

    pubsub_auth = require_google_caller(
        audience=settings.pubsub_audience,
        expected_email=settings.app_service_account,
    )

    @app.post("/internal/pubsub/events")
    def pubsub_events(
        push: PubSubPush,
        _caller: AuthenticatedCaller = Depends(pubsub_auth),
    ) -> dict[str, object]:
        try:
            event = decode_push(push)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        if event.event_type == "continuity.checkpoint":
            try:
                day = int(event.payload["day"])
                requested_date = str(event.payload["calendar_date"])
                checkpoint = create_checkpoint(
                    settings,
                    day=day,
                    requested_date=requested_date,
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid continuity event: {exc}",
                ) from exc
            return {
                "accepted": True,
                "event_id": event.event_id,
                "checkpoint_day": checkpoint["day"],
            }

        if event.event_type == "invoice.received":
            try:
                incident = invoice_flow.process_fixture(
                    fixture=str(event.payload["fixture"]),
                    event_id=event.event_id,
                    correlation_id=event.correlation_id,
                )
                if incident.state.value == "QUARANTINED":
                    incident = recovery_flow.plan(incident.incident_id)
                elif incident.state.value == "PLAN_READY":
                    incident = recovery_flow.prepare_clean(incident.incident_id)
            except (KeyError, TypeError, ValueError) as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            return {
                "accepted": True,
                "event_id": event.event_id,
                "incident_id": incident.incident_id,
                "state": incident.state.value,
            }

        if event.event_type == "recovery.execute":
            try:
                incident, receipt = governed_recovery.execute_and_verify(
                    str(event.payload["incident_id"])
                )
            except (KeyError, ConflictError, NotFoundError) as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            return {
                "accepted": True,
                "event_id": event.event_id,
                "incident_id": incident.incident_id,
                "state": incident.state.value,
                "receipt_id": receipt.receipt_id if receipt else None,
            }

        raise HTTPException(status_code=400, detail="Unsupported event type")

    return app
