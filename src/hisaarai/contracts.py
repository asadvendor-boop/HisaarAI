"""Typed contracts crossing agent, authority and sandbox boundaries."""

from __future__ import annotations

import datetime as dt
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IncidentState(StrEnum):
    DETECTED = "DETECTED"
    QUARANTINED = "QUARANTINED"
    INVESTIGATING = "INVESTIGATING"
    PLAN_READY = "PLAN_READY"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"
    BLOCKED = "BLOCKED"


class StateEvent(StrictModel):
    state: IncidentState
    version: int = Field(ge=1)
    at: dt.datetime
    reason: str | None = None


class VendorRecord(StrictModel):
    vendor_id: str
    display_name: str
    bank_fingerprint: str
    version: int = Field(ge=1)


class PaymentProposal(StrictModel):
    invoice_id: str
    vendor_id: str
    amount_minor: int = Field(gt=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    bank_fingerprint: str
    requested_model: str
    actual_model: str
    thinking_level: str
    source_context_id: str


class AgentFinding(StrictModel):
    agent: str
    summary: str = Field(min_length=5, max_length=400)
    evidence_ids: list[str] = Field(min_length=1, max_length=8)
    requested_model: str
    actual_model: str
    thinking_level: str


class RecoveryAgentOutput(StrictModel):
    summary: str = Field(min_length=5, max_length=400)
    evidence_ids: list[str] = Field(min_length=1, max_length=8)


class RecoveryPlanOutput(RecoveryAgentOutput):
    action: Literal["RECONSTRUCT_FROM_TRUSTED_VENDOR_MASTER"]


class StandbyOutput(StrictModel):
    decision: Literal["EXECUTE_APPROVED_WARRANT"]
    incident_id: str
    warrant_digest: str
    vendor_id: str
    amount_minor: int
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    bank_fingerprint: str


class WitnessOutput(StrictModel):
    verdict: Literal["MATCH", "MISMATCH"]
    summary: str = Field(min_length=5, max_length=300)


class RecoveryWarrant(StrictModel):
    warrant_id: str
    incident_id: str
    attempt_id: str
    invoice_id: str
    vendor_id: str
    amount_minor: int
    currency: str
    bank_fingerprint: str
    trusted_vendor_version: int
    continuity_revision_name: str
    expires_at: dt.datetime
    digest: str


class CleanExecutionRequest(StrictModel):
    incident_id: str
    attempt_id: str
    warrant_id: str
    warrant_digest: str
    business_idempotency_key: str
    vendor_id: str
    amount_minor: int
    currency: str
    bank_fingerprint: str


class SandboxReceipt(StrictModel):
    receipt_id: str
    business_idempotency_key: str
    incident_id: str
    attempt_id: str
    warrant_digest: str
    vendor_id: str
    amount_minor: int
    currency: str
    bank_fingerprint: str
    executor_identity: str
    created_at: dt.datetime


class Incident(StrictModel):
    incident_id: str
    attempt_id: str
    invoice_id: str
    business_idempotency_key: str
    state: IncidentState
    version: int = Field(ge=1)
    reason: str | None = None
    correlation_id: str
    trace_id: str
    proposal: PaymentProposal | None = None
    trusted_vendor: VendorRecord | None = None
    findings: list[AgentFinding] = Field(default_factory=list)
    warrant: RecoveryWarrant | None = None
    receipt_id: str | None = None
    verification: str | None = None
    witness_summary: str | None = None
    continuity_revision_name: str | None = None
    approved_by: str | None = None
    approved_at: dt.datetime | None = None
    rejected_by: str | None = None
    rejection_rationale: str | None = None
    screening_decision: str | None = None
    screening_pdf_decision: str | None = None
    screening_text_decision: str | None = None
    gemini_invocations: int = Field(default=0, ge=0)
    created_at: dt.datetime
    updated_at: dt.datetime
    state_history: list[StateEvent] = Field(default_factory=list)


class ProtectedAPOutput(StrictModel):
    invoice_id: str
    vendor_id: str
    amount_minor: int
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    bank_fingerprint: str
