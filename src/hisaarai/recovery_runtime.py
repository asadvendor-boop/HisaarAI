"""Callable client for the five-role Recovery Fleet Runtime."""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any

import vertexai

from hisaarai.config import Settings
from hisaarai.contracts import (
    AgentFinding,
    RecoveryAgentOutput,
    RecoveryPlanOutput,
    StandbyOutput,
    WitnessOutput,
)


ROLE_CONFIG = {
    "raasid_observer": ("Raasid", "gemini-3.5-flash-lite", "DEFAULT"),
    "kashif_investigator": ("Kashif", "gemini-3.7-flash", "HIGH"),
    "muslih_planner": ("Muslih", "gemini-3.7-flash", "HIGH"),
}


def _event_text(event: dict[str, Any]) -> str:
    content = event.get("content")
    if not isinstance(content, dict):
        return ""
    parts = content.get("parts", [])
    if not isinstance(parts, list):
        return ""
    return "".join(
        str(part.get("text", ""))
        for part in parts
        if isinstance(part, dict) and part.get("text")
    )


class RecoveryRuntimeClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def _query(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        client = vertexai.Client(
            project=self.settings.project_id,
            location=self.settings.location,
        )
        runtime = client.agent_engines.get(name=self.settings.recovery_runtime_name)
        events: list[dict[str, Any]] = []
        user_id = (
            f"{payload.get('incident_id', 'hisaar')}:{payload['operation']}:"
            f"{uuid.uuid4().hex}"
        )
        async with asyncio.timeout(150):
            async for event in runtime.async_stream_query(
                user_id=user_id,
                message=json.dumps(payload, sort_keys=True, separators=(",", ":")),
            ):
                if not isinstance(event, dict):
                    raise RuntimeError("Recovery Runtime returned an invalid event")
                if event.get("error_code") or event.get("code"):
                    raise RuntimeError(f"Recovery Runtime failed: {event}")
                events.append(event)
        return events

    @staticmethod
    def _last_by_author(
        events: list[dict[str, Any]],
        author: str,
    ) -> dict[str, Any]:
        matches = [event for event in events if event.get("author") == author and _event_text(event)]
        if not matches:
            raise RuntimeError(f"Recovery Runtime returned no output for {author}")
        return matches[-1]

    def plan(self, payload: dict[str, Any]) -> list[AgentFinding]:
        events = asyncio.run(self._query({**payload, "operation": "PLAN"}))
        findings: list[AgentFinding] = []
        for author, (display_name, expected_model, thinking) in ROLE_CONFIG.items():
            event = self._last_by_author(events, author)
            actual_model = str(event.get("model_version", ""))
            if actual_model != expected_model:
                raise RuntimeError(
                    f"{display_name} used unexpected model {actual_model!r}"
                )
            raw = json.loads(_event_text(event))
            if author == "muslih_planner":
                output = RecoveryPlanOutput.model_validate(raw)
            else:
                output = RecoveryAgentOutput.model_validate(raw)
            findings.append(
                AgentFinding(
                    agent=display_name,
                    summary=output.summary,
                    evidence_ids=output.evidence_ids,
                    requested_model=expected_model,
                    actual_model=actual_model,
                    thinking_level=thinking,
                )
            )
        return findings

    def execute(self, payload: dict[str, Any]) -> StandbyOutput:
        events = asyncio.run(self._query({**payload, "operation": "EXECUTE"}))
        event = self._last_by_author(events, "clean_ap_standby")
        actual_model = str(event.get("model_version", ""))
        if actual_model != "gemini-3.7-flash":
            raise RuntimeError(f"Clean standby used unexpected model {actual_model!r}")
        output = StandbyOutput.model_validate_json(_event_text(event))
        if output.amount_minor <= 0:
            raise RuntimeError("Clean standby returned a non-positive amount")
        return output

    def witness(self, payload: dict[str, Any]) -> WitnessOutput:
        events = asyncio.run(self._query({**payload, "operation": "WITNESS"}))
        event = self._last_by_author(events, "shaahid_witness")
        actual_model = str(event.get("model_version", ""))
        if actual_model != "gemini-3.5-flash-lite":
            raise RuntimeError(f"Shaahid used unexpected model {actual_model!r}")
        return WitnessOutput.model_validate_json(_event_text(event))
