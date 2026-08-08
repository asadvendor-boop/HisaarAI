"""Callable client for the protected AP Agent Runtime."""

from __future__ import annotations

import asyncio
import json

import vertexai

from hisaarai.config import Settings
from hisaarai.contracts import PaymentProposal, ProtectedAPOutput


class ProtectedAPClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def _query(self, *, incident_id: str, screened_text: str) -> PaymentProposal:
        client = vertexai.Client(
            project=self.settings.project_id,
            location=self.settings.location,
        )
        runtime = client.agent_engines.get(name=self.settings.ap_runtime_name)
        events: list[dict[str, object]] = []
        async with asyncio.timeout(55):
            async for event in runtime.async_stream_query(
                user_id=incident_id,
                message=(
                    "Extract the payment proposal from this already-screened invoice.\n\n"
                    + screened_text
                ),
            ):
                if not isinstance(event, dict):
                    raise RuntimeError("Protected AP Runtime returned an invalid event")
                if event.get("error_code") or event.get("code"):
                    raise RuntimeError(f"Protected AP Runtime failed: {event}")
                events.append(event)
        model_events = [event for event in events if event.get("content")]
        if not model_events:
            raise RuntimeError("Protected AP Runtime returned no model output")
        final = model_events[-1]
        parts = final.get("content", {}).get("parts", [])
        texts = [part.get("text") for part in parts if isinstance(part, dict)]
        text = "".join(part for part in texts if part)
        parsed = ProtectedAPOutput.model_validate(json.loads(text))
        if parsed.amount_minor <= 0:
            raise RuntimeError("Protected AP returned a non-positive amount")
        actual_model = str(final.get("model_version", ""))
        if actual_model != "gemini-3.6-flash":
            raise RuntimeError(f"Protected AP used unexpected model {actual_model!r}")
        return PaymentProposal(
            **parsed.model_dump(),
            requested_model="gemini-3.6-flash",
            actual_model=actual_model,
            thinking_level="MEDIUM",
            source_context_id=f"screened:{incident_id}",
        )

    def propose(self, *, incident_id: str, screened_text: str) -> PaymentProposal:
        return asyncio.run(self._query(incident_id=incident_id, screened_text=screened_text))
