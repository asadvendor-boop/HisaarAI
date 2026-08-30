"""Real invoice intake: PDF -> Model Armor -> Protected AP -> Hisaar Gate."""

from __future__ import annotations

from pathlib import Path
import re

from hisaarai.config import Settings
from hisaarai.contracts import Incident, IncidentState, VendorRecord
from hisaarai.gate import HisaarGate
from hisaarai.observability import stage_span
from hisaarai.protected_ap import ProtectedAPClient
from hisaarai.screening import ModelArmorScreen, ScreeningDecision
from hisaarai.store import AuthorityStore, NotFoundError


FIXTURES = {
    "injection-control": Path("fixtures/invoices/injection-control.pdf"),
    "semantic-tamper": Path("fixtures/invoices/semantic-tamper.pdf"),
    "clean-control": Path("fixtures/invoices/clean-control.pdf"),
}
TRUSTED_VENDOR = VendorRecord(
    vendor_id="vendor-northstar",
    display_name="Northstar Medical Supplies",
    bank_fingerprint="PK-NSTAR-TRUSTED-8842",
    version=7,
)


def _invoice_id(text: str) -> str:
    match = re.search(r"INV-\d{4}-\d{4}", text)
    if not match:
        raise ValueError("Screened invoice is missing its invoice identifier")
    return match.group(0)


class InvoiceFlow:
    def __init__(
        self,
        *,
        settings: Settings,
        store: AuthorityStore,
        ap_client: ProtectedAPClient | None = None,
        screen: ModelArmorScreen | None = None,
    ) -> None:
        self.settings = settings
        self.store = store
        self.gate = HisaarGate(store)
        self.ap_client = ap_client or ProtectedAPClient(settings)
        self.screen = screen or ModelArmorScreen(
            project=settings.project_id,
            location=settings.location,
            template_id=settings.model_armor_template,
        )

    def process_fixture(
        self,
        *,
        fixture: str,
        event_id: str,
        correlation_id: str,
    ) -> Incident:
        path = FIXTURES.get(fixture)
        if path is None:
            raise ValueError("Unknown committed invoice fixture")
        with stage_span(correlation_id, "model_armor", fixture=fixture):
            result = self.screen.screen_pdf_and_text(path)
        invoice_id = _invoice_id(result.extracted_text)
        safe_event_id = re.sub(r"[^a-zA-Z0-9-]", "-", event_id)[:64]
        incident_id = f"inc-{safe_event_id}"
        try:
            return self.store.get_incident(incident_id)
        except NotFoundError:
            pass
        incident = self.gate.open_incident(
            invoice_id=invoice_id,
            correlation_id=correlation_id,
            # The Pub/Sub event ID is stable across redelivery, while each explicit
            # sandbox launch gets a fresh event. This keeps retries idempotent and
            # makes independent judge/rehearsal runs repeatable.
            business_idempotency_key=f"pay:{invoice_id}:{safe_event_id}",
            incident_id=incident_id,
            attempt_id=f"att-{safe_event_id}",
        )
        screening_changes = {
            "screening_decision": result.decision.value,
            "screening_pdf_decision": result.pdf_decision.value,
            "screening_text_decision": result.text_decision.value,
        }
        if result.decision == ScreeningDecision.MATCH:
            return self.gate.transition(
                incident,
                IncidentState.BLOCKED,
                reason="MODEL_ARMOR_MATCH",
                changes={**screening_changes, "gemini_invocations": 0},
            )
        if result.decision == ScreeningDecision.UNAVAILABLE:
            return self.gate.transition(
                incident,
                IncidentState.BLOCKED,
                reason="SCREENING_UNAVAILABLE",
                changes={**screening_changes, "gemini_invocations": 0},
            )
        self.store.put_vendor(TRUSTED_VENDOR)
        try:
            with stage_span(
                correlation_id,
                "protected_ap",
                incident_id=incident.incident_id,
            ):
                proposal = self.ap_client.propose(
                    incident_id=incident.incident_id,
                    screened_text=result.extracted_text,
                )
        except Exception as exc:
            return self.gate.transition(
                incident,
                IncidentState.BLOCKED,
                reason="PROTECTED_AP_FAILED",
                changes={**screening_changes, "gemini_invocations": 1},
            )
        return self.gate.evaluate_proposal(
            incident,
            proposal,
            TRUSTED_VENDOR,
            evidence_changes={**screening_changes, "gemini_invocations": 1},
        )
