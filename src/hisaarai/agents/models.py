"""Approved Gemini routing through the supported global endpoint."""

from functools import cached_property
import os

from google import genai
from google.adk.models import Gemini
from google.genai import types


class GlobalGemini(Gemini):
    @cached_property
    def api_client(self) -> genai.Client:
        return genai.Client(
            enterprise=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location="global",
            http_options=types.HttpOptions(api_version="v1"),
        )

