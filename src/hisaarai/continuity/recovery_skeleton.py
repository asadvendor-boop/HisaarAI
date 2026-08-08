"""Minimal recovery-fleet agent used to start the genuine continuity clock."""

from functools import cached_property
import os

from google import genai
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types


class GlobalGemini(Gemini):
    """Route the approved Gemini models through their supported global endpoint."""

    @cached_property
    def api_client(self) -> genai.Client:
        return genai.Client(
            enterprise=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location="global",
            http_options=types.HttpOptions(api_version="v1"),
        )


root_agent = Agent(
    name="hisaar_recovery_skeleton",
    model=GlobalGemini(model="gemini-3.5-flash-lite"),
    description="Minimal deployed recovery-fleet skeleton for Day-0 continuity.",
    instruction=(
        "You are the temporary HisaarAI recovery-fleet skeleton. "
        "Acknowledge continuity-policy queries concisely. Do not propose, approve, "
        "or execute payments."
    ),
)
