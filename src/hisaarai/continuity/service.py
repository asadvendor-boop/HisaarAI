"""Genuine, date-bound Memory Bank continuity checkpoints."""

from __future__ import annotations

import datetime as dt
from typing import Any
from zoneinfo import ZoneInfo

from google.cloud import firestore
import vertexai

from hisaarai.config import Settings


KARACHI = ZoneInfo("Asia/Karachi")
CHECKPOINT_DATES = {
    0: dt.date(2026, 8, 9),
    7: dt.date(2026, 8, 16),
    14: dt.date(2026, 8, 23),
    21: dt.date(2026, 8, 30),
}
DAY0_REVISION = (
    "projects/957109932069/locations/us-central1/reasoningEngines/"
    "6980660236528910336/memories/6243621652144324608/revisions/"
    "2389586264371232768"
)


def _firestore(settings: Settings) -> firestore.Client:
    return firestore.Client(
        project=settings.project_id,
        database=settings.firestore_database,
    )


def get_checkpoint(settings: Settings, day: int) -> dict[str, Any] | None:
    snap = _firestore(settings).collection("continuity_checkpoints").document(
        f"day-{day}"
    ).get()
    return snap.to_dict() if snap.exists else None


def latest_checkpoint(settings: Settings) -> dict[str, Any]:
    for day in (21, 14, 7, 0):
        checkpoint = get_checkpoint(settings, day)
        if checkpoint is not None:
            return checkpoint
    raise RuntimeError("No genuine continuity checkpoint is available")


def create_checkpoint(
    settings: Settings,
    *,
    day: int,
    requested_date: str,
) -> dict[str, Any]:
    expected_date = CHECKPOINT_DATES.get(day)
    if expected_date is None or requested_date != expected_date.isoformat():
        raise ValueError("Checkpoint day/date does not match the approved calendar")
    if dt.datetime.now(KARACHI).date() < expected_date:
        raise ValueError("A future continuity checkpoint cannot be created early")

    db = _firestore(settings)
    ref = db.collection("continuity_checkpoints").document(f"day-{day}")
    existing = ref.get()
    if existing.exists:
        return existing.to_dict() or {}

    previous_day = 0 if day == 7 else day - 7
    previous = get_checkpoint(settings, previous_day)
    if not previous:
        raise RuntimeError("Previous genuine checkpoint is missing")
    previous_revision = str(previous["memory_revision_name"])
    fact = (
        f"HisaarAI Day {day} continuity policy: exclude quarantined invoice "
        "context, reconstruct from the trusted vendor master, and require one "
        f"human decision. Previous revision: {previous_revision}."
    )

    client = vertexai.Client(project=settings.project_id, location=settings.location)
    operation = client.agent_engines.memories.create(
        name=settings.recovery_runtime_name,
        fact=fact,
        scope={
            "app_name": "hisaarai",
            "timeline": "all-things-agentic-2026",
            "day": str(day),
        },
        config={
            "memory_id": f"hisaarai-continuity-day{day}",
            "wait_for_completion": True,
            "disable_memory_revisions": False,
            "revision_ttl": "31536000s",
        },
    )
    if operation.error is not None or operation.response is None:
        raise RuntimeError(f"Memory Bank checkpoint creation failed: {operation.error}")
    memory = client.agent_engines.memories.get(name=operation.response.name)
    revisions = list(client.agent_engines.memories.revisions.list(name=memory.name))
    matching = [revision for revision in revisions if revision.fact == fact]
    if len(matching) != 1:
        raise RuntimeError("Expected one exact immutable checkpoint revision")
    revision = client.agent_engines.memories.revisions.get(name=matching[0].name)
    checkpoint = {
        "day": day,
        "calendar_date": expected_date.isoformat(),
        "calendar_timezone": "Asia/Karachi",
        "fact": fact,
        "previous_revision_name": previous_revision,
        "memory_name": memory.name,
        "memory_revision_name": revision.name,
        "memory_create_time": memory.create_time,
        "revision_create_time": revision.create_time,
        "created_at": firestore.SERVER_TIMESTAMP,
        "creation_actor": settings.app_service_account,
    }
    ref.create(checkpoint)
    stored = ref.get().to_dict()
    if not stored:
        raise RuntimeError("Checkpoint was not persisted to Firestore")
    return stored
