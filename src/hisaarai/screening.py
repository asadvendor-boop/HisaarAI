"""Fail-closed dual Model Armor screening for exact invoice context."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from google.api_core.client_options import ClientOptions
from google.cloud import modelarmor_v1
from pypdf import PdfReader


class ScreeningDecision(StrEnum):
    CLEAR = "CLEAR"
    MATCH = "MATCH"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class ScreeningResult:
    decision: ScreeningDecision
    pdf_decision: ScreeningDecision
    text_decision: ScreeningDecision
    extracted_text: str
    detail: str


def extract_pdf_text(path: Path, *, max_bytes: int = 4_000_000) -> str:
    if path.stat().st_size > max_bytes:
        raise ValueError("Invoice PDF exceeds the committed screening limit")
    reader = PdfReader(path)
    if not reader.pages or len(reader.pages) > 5:
        raise ValueError("Invoice PDF page count is outside the committed limit")
    text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if not text:
        raise ValueError("Invoice PDF contains no extractable text")
    return text


class ModelArmorScreen:
    def __init__(self, *, project: str, location: str, template_id: str) -> None:
        self.template_name = (
            f"projects/{project}/locations/{location}/templates/{template_id}"
        )
        self.client = modelarmor_v1.ModelArmorClient(
            transport="rest",
            client_options=ClientOptions(
                api_endpoint=f"modelarmor.{location}.rep.googleapis.com"
            ),
        )

    @staticmethod
    def _decision(response: object) -> ScreeningDecision:
        result = response.sanitization_result
        if result.invocation_result != modelarmor_v1.InvocationResult.SUCCESS:
            return ScreeningDecision.UNAVAILABLE
        if result.filter_match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND:
            return ScreeningDecision.MATCH
        if result.filter_match_state != modelarmor_v1.FilterMatchState.NO_MATCH_FOUND:
            return ScreeningDecision.UNAVAILABLE
        pi_result = result.filter_results.get("pi_and_jailbreak")
        if pi_result is None or not pi_result.pi_and_jailbreak_filter_result:
            return ScreeningDecision.UNAVAILABLE
        typed = pi_result.pi_and_jailbreak_filter_result
        if typed.execution_state != modelarmor_v1.FilterExecutionState.EXECUTION_SUCCESS:
            return ScreeningDecision.UNAVAILABLE
        if typed.match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND:
            return ScreeningDecision.MATCH
        if typed.match_state != modelarmor_v1.FilterMatchState.NO_MATCH_FOUND:
            return ScreeningDecision.UNAVAILABLE
        return ScreeningDecision.CLEAR

    def _sanitize(self, data: modelarmor_v1.DataItem) -> tuple[ScreeningDecision, str]:
        try:
            response = self.client.sanitize_user_prompt(
                request=modelarmor_v1.SanitizeUserPromptRequest(
                    name=self.template_name,
                    user_prompt_data=data,
                ),
                timeout=20,
            )
        except Exception as exc:
            return ScreeningDecision.UNAVAILABLE, type(exc).__name__
        return self._decision(response), str(response.sanitization_result)

    def screen_pdf_and_text(self, path: Path) -> ScreeningResult:
        extracted_text = extract_pdf_text(path)
        pdf_data = modelarmor_v1.DataItem(
            byte_item=modelarmor_v1.ByteDataItem(
                byte_data_type=modelarmor_v1.ByteDataItem.ByteItemType.PDF,
                byte_data=path.read_bytes(),
            )
        )
        pdf_decision, pdf_detail = self._sanitize(pdf_data)
        text_decision, text_detail = self._sanitize(
            modelarmor_v1.DataItem(text=extracted_text)
        )
        if ScreeningDecision.UNAVAILABLE in {pdf_decision, text_decision}:
            overall = ScreeningDecision.UNAVAILABLE
        elif ScreeningDecision.MATCH in {pdf_decision, text_decision}:
            overall = ScreeningDecision.MATCH
        else:
            overall = ScreeningDecision.CLEAR
        return ScreeningResult(
            decision=overall,
            pdf_decision=pdf_decision,
            text_decision=text_decision,
            extracted_text=extracted_text,
            detail=f"pdf={pdf_detail}; text={text_detail}",
        )
