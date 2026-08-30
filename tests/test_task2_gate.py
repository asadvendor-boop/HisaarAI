from __future__ import annotations

import datetime as dt
from concurrent.futures import ThreadPoolExecutor

import pytest

from hisaarai.contracts import (
    CleanExecutionRequest,
    Incident,
    IncidentState,
    PaymentProposal,
    RecoveryWarrant,
    SandboxReceipt,
    VendorRecord,
)
from hisaarai.gate import HisaarGate
from hisaarai.sandbox_erp import SandboxERP
from hisaarai.store import ConflictError, InMemoryStore


VENDOR = VendorRecord(
    vendor_id="vendor-northstar",
    display_name="Northstar Medical Supplies",
    bank_fingerprint="PK-NSTAR-TRUSTED-8842",
    version=7,
)


def proposal(bank: str = "PK-ATTACKER-9911") -> PaymentProposal:
    return PaymentProposal(
        invoice_id="INV-2026-0819",
        vendor_id=VENDOR.vendor_id,
        amount_minor=427_500_000,
        currency="PKR",
        bank_fingerprint=bank,
        requested_model="gemini-3.7-flash",
        actual_model="gemini-3.7-flash",
        thinking_level="MEDIUM",
        source_context_id="ctx-contaminated-invoice-1",
    )


def approved_incident() -> tuple[InMemoryStore, HisaarGate, Incident, RecoveryWarrant]:
    store = InMemoryStore()
    gate = HisaarGate(store)
    incident = gate.open_incident(
        invoice_id="INV-2026-0819",
        correlation_id="corr-flagship-1",
        business_idempotency_key="pay:INV-2026-0819",
    )
    incident = gate.evaluate_proposal(incident, proposal(), VENDOR)
    incident = gate.transition(incident, IncidentState.INVESTIGATING)
    incident = gate.transition(incident, IncidentState.PLAN_READY)
    warrant = RecoveryWarrant(
        warrant_id="warrant-flagship-1",
        incident_id=incident.incident_id,
        attempt_id=incident.attempt_id,
        invoice_id=incident.invoice_id,
        vendor_id=VENDOR.vendor_id,
        amount_minor=427_500_000,
        currency="PKR",
        bank_fingerprint=VENDOR.bank_fingerprint,
        trusted_vendor_version=VENDOR.version,
        continuity_revision_name="projects/p/locations/l/reasoningEngines/r/memories/m/revisions/v",
        expires_at=dt.datetime.now(dt.UTC) + dt.timedelta(minutes=10),
        digest="a" * 64,
    )
    incident = gate.transition(
        incident,
        IncidentState.AWAITING_APPROVAL,
        changes={"warrant": warrant},
    )
    incident = gate.transition(incident, IncidentState.APPROVED)
    return store, gate, incident, warrant


def execution_request(incident: Incident, warrant: RecoveryWarrant) -> CleanExecutionRequest:
    return CleanExecutionRequest(
        incident_id=incident.incident_id,
        attempt_id=incident.attempt_id,
        warrant_id=warrant.warrant_id,
        warrant_digest=warrant.digest,
        business_idempotency_key=incident.business_idempotency_key,
        vendor_id=warrant.vendor_id,
        amount_minor=warrant.amount_minor,
        currency=warrant.currency,
        bank_fingerprint=warrant.bank_fingerprint,
    )


def test_illegal_transition_is_denied() -> None:
    store = InMemoryStore()
    gate = HisaarGate(store)
    incident = gate.open_incident(
        invoice_id="invoice-1",
        correlation_id="corr-1",
        business_idempotency_key="pay:invoice-1",
    )
    with pytest.raises(ConflictError, match="Illegal transition"):
        gate.transition(incident, IncidentState.APPROVED)


def test_mismatch_is_quarantined_without_receipt() -> None:
    store = InMemoryStore()
    gate = HisaarGate(store)
    incident = gate.open_incident(
        invoice_id="INV-2026-0819",
        correlation_id="corr-1",
        business_idempotency_key="pay:INV-2026-0819",
    )
    quarantined = gate.evaluate_proposal(incident, proposal(), VENDOR)
    assert quarantined.state == IncidentState.QUARANTINED
    assert quarantined.reason == "BANK_FINGERPRINT_MISMATCH"
    assert store.get_receipt(quarantined.business_idempotency_key) is None


def test_execution_before_approval_is_denied() -> None:
    store = InMemoryStore()
    gate = HisaarGate(store)
    incident = gate.open_incident(
        invoice_id="INV-2026-0819",
        correlation_id="corr-1",
        business_idempotency_key="pay:INV-2026-0819",
    )
    incident = gate.evaluate_proposal(incident, proposal(), VENDOR)
    erp = SandboxERP(store)
    request = CleanExecutionRequest(
        incident_id=incident.incident_id,
        attempt_id=incident.attempt_id,
        warrant_id="none",
        warrant_digest="none",
        business_idempotency_key=incident.business_idempotency_key,
        vendor_id=VENDOR.vendor_id,
        amount_minor=427_500_000,
        currency="PKR",
        bank_fingerprint=VENDOR.bank_fingerprint,
    )
    with pytest.raises(ConflictError, match="APPROVAL_REQUIRED"):
        erp.execute(request, executor_identity="hisaar-recovery-runtime")


def test_ten_concurrent_executions_return_one_receipt() -> None:
    store, _gate, incident, warrant = approved_incident()
    erp = SandboxERP(store)
    request = execution_request(incident, warrant)

    def execute() -> SandboxReceipt:
        return erp.execute(
            request,
            executor_identity="hisaar-recovery-runtime",
        )

    with ThreadPoolExecutor(max_workers=10) as pool:
        receipts = list(pool.map(lambda _index: execute(), range(10)))

    assert len({receipt.receipt_id for receipt in receipts}) == 1
    assert store.get_incident(incident.incident_id).state == IncidentState.COMPLETED


def test_verification_disagreement_fails_closed() -> None:
    store, gate, incident, warrant = approved_incident()
    erp = SandboxERP(store)
    receipt = erp.execute(
        execution_request(incident, warrant),
        executor_identity="hisaar-recovery-runtime",
    )
    completed = store.get_incident(incident.incident_id)
    tampered = receipt.model_copy(update={"bank_fingerprint": "PK-TAMPERED"})
    blocked = gate.verify_receipt(completed, tampered)
    assert blocked.state == IncidentState.BLOCKED
    assert blocked.reason == "VERIFICATION_DISAGREEMENT"
    assert blocked.verification == "MISMATCH"
