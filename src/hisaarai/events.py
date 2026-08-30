"""Strict Pub/Sub event envelope for the one authenticated push endpoint."""

from __future__ import annotations

import base64
import binascii
import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


EventType = Literal[
    "invoice.received",
    "continuity.checkpoint",
    "recovery.execute",
]


class EventEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(min_length=8, max_length=128)
    event_type: EventType
    idempotency_key: str = Field(min_length=4, max_length=160)
    correlation_id: str = Field(min_length=4, max_length=128)
    payload: dict[str, Any]


class PubSubMessage(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    data: str
    message_id: str | None = Field(default=None, alias="messageId")


class PubSubPush(BaseModel):
    model_config = ConfigDict(extra="ignore")

    message: PubSubMessage
    subscription: str | None = None


def decode_push(push: PubSubPush) -> EventEnvelope:
    try:
        decoded = base64.b64decode(push.message.data, validate=True)
        raw = json.loads(decoded)
        return EventEnvelope.model_validate(raw)
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError, ValidationError) as exc:
        raise ValueError("Pub/Sub message is not a valid HisaarAI event") from exc

