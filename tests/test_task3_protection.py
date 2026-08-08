from __future__ import annotations

from pathlib import Path

from google.cloud import modelarmor_v1

from hisaarai.config import Settings
from hisaarai.contracts import IncidentState, PaymentProposal
from hisaarai.invoice_flow import InvoiceFlow
from hisaarai.screening import (
    ModelArmorScreen,
    ScreeningDecision,
    ScreeningResult,
    extract_pdf_text,
)
from hisaarai.store import InMemoryStore


def settings() -> Settings:
    project = "hisaarai-agentic-2026"
    return Settings(
        project_id=project,
        location="us-central1",
        firestore_database="hisaarai",
        event_topic="hisaar-events",
        pubsub_audience="https://example/internal/pubsub/events",
        commander_oauth_client_id="client.apps.googleusercontent.com",
        commander_subject="commander",
        app_service_account=f"hisaar-app@{project}.iam.gserviceaccount.com",
        ap_runtime_service_account=f"hisaar-ap-runtime@{project}.iam.gserviceaccount.com",
        recovery_runtime_service_account=(
            f"hisaar-recovery-runtime@{project}.iam.gserviceaccount.com"
        ),
        recovery_runtime_name="projects/1/locations/us-central1/reasoningEngines/1",
        ap_runtime_name="projects/1/locations/us-central1/reasoningEngines/2",
        model_armor_template="hisaarai-ingress",
        environment="test",
    )


def response(
    *,
    invocation: modelarmor_v1.InvocationResult,
    overall: modelarmor_v1.FilterMatchState,
    execution: modelarmor_v1.FilterExecutionState,
    pi_match: modelarmor_v1.FilterMatchState,
) -> modelarmor_v1.SanitizeUserPromptResponse:
    return modelarmor_v1.SanitizeUserPromptResponse(
        sanitization_result=modelarmor_v1.SanitizationResult(
            invocation_result=invocation,
            filter_match_state=overall,
            filter_results={
                "pi_and_jailbreak": modelarmor_v1.FilterResult(
                    pi_and_jailbreak_filter_result=(
                        modelarmor_v1.PiAndJailbreakFilterResult(
                            execution_state=execution,
                            match_state=pi_match,
                        )
                    )
                )
            },
        )
    )


def test_model_armor_only_releases_conclusive_clear() -> None:
    clear = response(
        invocation=modelarmor_v1.InvocationResult.SUCCESS,
        overall=modelarmor_v1.FilterMatchState.NO_MATCH_FOUND,
        execution=modelarmor_v1.FilterExecutionState.EXECUTION_SUCCESS,
        pi_match=modelarmor_v1.FilterMatchState.NO_MATCH_FOUND,
    )
    match = response(
        invocation=modelarmor_v1.InvocationResult.SUCCESS,
        overall=modelarmor_v1.FilterMatchState.MATCH_FOUND,
        execution=modelarmor_v1.FilterExecutionState.EXECUTION_SUCCESS,
        pi_match=modelarmor_v1.FilterMatchState.MATCH_FOUND,
    )
    skipped = response(
        invocation=modelarmor_v1.InvocationResult.PARTIAL,
        overall=modelarmor_v1.FilterMatchState.NO_MATCH_FOUND,
        execution=modelarmor_v1.FilterExecutionState.EXECUTION_SKIPPED,
        pi_match=modelarmor_v1.FilterMatchState.NO_MATCH_FOUND,
    )
    assert ModelArmorScreen._decision(clear) == ScreeningDecision.CLEAR
    assert ModelArmorScreen._decision(match) == ScreeningDecision.MATCH
    assert ModelArmorScreen._decision(skipped) == ScreeningDecision.UNAVAILABLE


class FakeScreen:
    def __init__(self, decision: ScreeningDecision, fixture_name: str) -> None:
        self.decision = decision
        self.fixture_name = fixture_name

    def screen_pdf_and_text(self, _path: Path) -> ScreeningResult:
        text = extract_pdf_text(Path("fixtures/invoices") / self.fixture_name)
        return ScreeningResult(
            decision=self.decision,
            pdf_decision=self.decision,
            text_decision=self.decision,
            extracted_text=text,
            detail="test",
        )


class FakeAP:
    def __init__(self, bank_fingerprint: str) -> None:
        self.bank_fingerprint = bank_fingerprint
        self.calls = 0

    def propose(self, *, incident_id: str, screened_text: str) -> PaymentProposal:
        self.calls += 1
        invoice = "INV-2026-0819" if "0819" in screened_text else "INV-2026-0820"
        return PaymentProposal(
            invoice_id=invoice,
            vendor_id="vendor-northstar",
            amount_minor=427_500_000,
            currency="PKR",
            bank_fingerprint=self.bank_fingerprint,
            requested_model="gemini-3.6-flash",
            actual_model="gemini-3.6-flash",
            thinking_level="MEDIUM",
            source_context_id=f"screened:{incident_id}",
        )


def test_injection_match_blocks_before_gemini() -> None:
    ap = FakeAP("PK-NSTAR-TRUSTED-8842")
    flow = InvoiceFlow(
        settings=settings(),
        store=InMemoryStore(),
        ap_client=ap,
        screen=FakeScreen(ScreeningDecision.MATCH, "injection-control.pdf"),
    )
    incident = flow.process_fixture(
        fixture="injection-control",
        event_id="event-injection",
        correlation_id="corr-injection",
    )
    assert incident.state == IncidentState.BLOCKED
    assert incident.reason == "MODEL_ARMOR_MATCH"
    assert incident.gemini_invocations == 0
    assert ap.calls == 0


def test_unavailable_screening_blocks_before_gemini() -> None:
    ap = FakeAP("PK-NSTAR-TRUSTED-8842")
    flow = InvoiceFlow(
        settings=settings(),
        store=InMemoryStore(),
        ap_client=ap,
        screen=FakeScreen(ScreeningDecision.UNAVAILABLE, "injection-control.pdf"),
    )
    incident = flow.process_fixture(
        fixture="injection-control",
        event_id="event-unavailable",
        correlation_id="corr-unavailable",
    )
    assert incident.state == IncidentState.BLOCKED
    assert incident.reason == "SCREENING_UNAVAILABLE"
    assert incident.gemini_invocations == 0
    assert ap.calls == 0


def test_semantic_tamper_reaches_quarantine_after_real_agent_stage() -> None:
    ap = FakeAP("PK-ATTACKER-9911")
    flow = InvoiceFlow(
        settings=settings(),
        store=InMemoryStore(),
        ap_client=ap,
        screen=FakeScreen(ScreeningDecision.CLEAR, "semantic-tamper.pdf"),
    )
    incident = flow.process_fixture(
        fixture="semantic-tamper",
        event_id="event-semantic",
        correlation_id="corr-semantic",
    )
    assert incident.state == IncidentState.QUARANTINED
    assert incident.reason == "BANK_FINGERPRINT_MISMATCH"
    assert incident.gemini_invocations == 1
    assert incident.proposal is not None
    assert incident.proposal.actual_model == "gemini-3.6-flash"
