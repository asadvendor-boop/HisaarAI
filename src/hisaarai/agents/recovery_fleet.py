"""Five-role recovery fleet behind one deterministic ADK router."""

from __future__ import annotations

from collections.abc import AsyncGenerator
import json

from google.adk.agents import Agent, BaseAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

from hisaarai.agents.models import GlobalGemini
from hisaarai.contracts import (
    RecoveryAgentOutput,
    RecoveryPlanOutput,
    StandbyOutput,
    WitnessOutput,
)


def _flash_config(level: types.ThinkingLevel) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level=level,
            include_thoughts=False,
        ),
        temperature=0,
    )


LITE_CONFIG = types.GenerateContentConfig(temperature=0)


raasid = Agent(
    name="raasid_observer",
    model=GlobalGemini(model="gemini-3.5-flash-lite"),
    description="Observer of bounded, persisted incident evidence.",
    instruction=(
        "Observe only the bounded incident JSON supplied by HisaarAI. State what "
        "was proposed, what trusted source disagreed, and which genuine continuity "
        "revision governs recovery. proposal.amount_display is expressed in major "
        "currency units; never infer or request minor units. Never approve or "
        "execute. Cite only evidence "
        "identifiers present in the input. Keep the summary under 500 characters."
    ),
    output_schema=RecoveryAgentOutput,
    output_key="raasid_output",
    generate_content_config=LITE_CONFIG,
    timeout=35,
)

kashif = Agent(
    name="kashif_investigator",
    model=GlobalGemini(model="gemini-3.7-flash"),
    description="Investigator of the bounded payment blast radius.",
    instruction=(
        "Investigate only the current input and Raasid output below. Determine the "
        "bounded blast radius and explain why the quarantined invoice-derived "
        "destination must not flow into execution. There is no evidence of any "
        "payment unless a receipt identifier is supplied. Cite only supplied "
        "evidence identifiers. Keep the summary under 500 characters.\nRaasid: "
        "{raasid_output}"
    ),
    output_schema=RecoveryAgentOutput,
    output_key="kashif_output",
    generate_content_config=_flash_config(types.ThinkingLevel.HIGH),
    timeout=45,
)

muslih = Agent(
    name="muslih_planner",
    model=GlobalGemini(model="gemini-3.7-flash"),
    description="Draft-only recovery planner with no approval authority.",
    instruction=(
        "Draft the smallest recovery action from the trusted vendor master. The "
        "only allowed action is RECONSTRUCT_FROM_TRUSTED_VENDOR_MASTER. Do not "
        "approve, execute, or invent evidence. Cite only identifiers supplied in "
        "the input or prior findings. Keep the summary under 500 characters.\n"
        "Raasid: {raasid_output}\nKashif: "
        "{kashif_output}"
    ),
    output_schema=RecoveryPlanOutput,
    output_key="muslih_output",
    generate_content_config=_flash_config(types.ThinkingLevel.HIGH),
    timeout=45,
)

planning_pipeline = SequentialAgent(
    name="recovery_planning_pipeline",
    description="Deterministic Raasid to Kashif to Muslih planning order.",
    sub_agents=[raasid, kashif, muslih],
)

clean_standby = Agent(
    name="clean_ap_standby",
    model=GlobalGemini(model="gemini-3.7-flash"),
    description="Clean-session executor of one approved trusted-source warrant.",
    instruction=(
        "Validate the clean execution request supplied by Hisaar Gate. It contains "
        "only the approved warrant and trusted vendor values—never invoice text or "
        "a quarantined session identifier. Echo the exact authorized fields with "
        "decision EXECUTE_APPROVED_WARRANT. Never modify values or self-approve."
    ),
    output_schema=StandbyOutput,
    generate_content_config=_flash_config(types.ThinkingLevel.MEDIUM),
    timeout=40,
)

shaahid = Agent(
    name="shaahid_witness",
    model=GlobalGemini(model="gemini-3.5-flash-lite"),
    description="Readable witness for a deterministic comparison result.",
    instruction=(
        "Narrate only the deterministic comparison supplied by Hisaar Gate. Echo "
        "its MATCH or MISMATCH verdict and explain it in one short sentence. You "
        "cannot change the verdict or incident state."
    ),
    output_schema=WitnessOutput,
    generate_content_config=LITE_CONFIG,
    timeout=30,
)


class RecoveryFleetRouter(BaseAgent):
    """Route an explicit operation without spending another model call."""

    async def _run_async_impl(
        self,
        ctx: InvocationContext,
    ) -> AsyncGenerator[Event, None]:
        if ctx.user_content is None:
            raise ValueError("Recovery operation payload is missing")
        text = "".join(part.text or "" for part in ctx.user_content.parts)
        try:
            operation = str(json.loads(text)["operation"])
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise ValueError("Recovery operation must be explicit JSON") from exc
        targets = {
            "PLAN": "recovery_planning_pipeline",
            "EXECUTE": "clean_ap_standby",
            "WITNESS": "shaahid_witness",
        }
        target = targets.get(operation)
        if target is None:
            raise ValueError(f"Unsupported recovery operation: {operation}")
        selected = next(agent for agent in self.sub_agents if agent.name == target)
        async for event in selected.run_async(ctx):
            yield event


root_agent = RecoveryFleetRouter(
    name="hisaar_recovery_fleet",
    description="Five-role governed recovery fleet with deterministic routing.",
    sub_agents=[planning_pipeline, clean_standby, shaahid],
)
