"""Final-named protected Accounts Payable Runtime skeleton."""

from google.adk.agents import Agent
from google.genai import types

from hisaarai.agents.models import GlobalGemini
from hisaarai.contracts import ProtectedAPOutput


root_agent = Agent(
    name="hisaar_protected_ap",
    model=GlobalGemini(model="gemini-3.7-flash"),
    description="Protected Accounts Payable agent behind Hisaar Gate.",
    instruction=(
        "You are the protected Accounts Payable proposal agent. Read only the "
        "screened invoice text supplied by the application. Extract invoice_id, "
        "vendor_id, amount_minor, currency, and bank_fingerprint exactly. Never "
        "approve or execute payment. Return only the required JSON object."
    ),
    output_schema=ProtectedAPOutput,
    generate_content_config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level=types.ThinkingLevel.MEDIUM,
            include_thoughts=False,
        ),
        temperature=0,
    ),
    timeout=45,
)
