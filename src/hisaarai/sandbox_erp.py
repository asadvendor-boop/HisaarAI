"""Idempotent sandbox-ledger execution behind Hisaar Gate."""

from __future__ import annotations

import datetime as dt
import uuid

from hisaarai.contracts import CleanExecutionRequest, IncidentState, SandboxReceipt
from hisaarai.store import AuthorityStore, ConflictError


class SandboxERP:
    def __init__(self, store: AuthorityStore) -> None:
        self.store = store

    def execute(
        self,
        request: CleanExecutionRequest,
        *,
        executor_identity: str,
        reasoning_runtime_identity: str | None = None,
    ) -> SandboxReceipt:
        incident = self.store.get_incident(request.incident_id)
        if incident.state != IncidentState.APPROVED:
            existing = self.store.get_receipt(request.business_idempotency_key)
            if existing and incident.state in {
                IncidentState.COMPLETED,
                IncidentState.VERIFIED,
            }:
                return existing
            raise ConflictError("APPROVAL_REQUIRED")
        if incident.warrant is None:
            raise ConflictError("Approved incident has no warrant")
        warrant = incident.warrant
        if (
            request.attempt_id != incident.attempt_id
            or request.warrant_id != warrant.warrant_id
            or request.warrant_digest != warrant.digest
            or request.vendor_id != warrant.vendor_id
            or request.amount_minor != warrant.amount_minor
            or request.currency != warrant.currency
            or request.bank_fingerprint != warrant.bank_fingerprint
            or request.business_idempotency_key
            != incident.business_idempotency_key
        ):
            raise ConflictError("Execution request disagrees with approved warrant")
        receipt = SandboxReceipt(
            receipt_id=f"rcpt-{uuid.uuid4().hex[:12]}",
            business_idempotency_key=request.business_idempotency_key,
            incident_id=incident.incident_id,
            attempt_id=incident.attempt_id,
            warrant_digest=warrant.digest,
            vendor_id=request.vendor_id,
            amount_minor=request.amount_minor,
            currency=request.currency,
            bank_fingerprint=request.bank_fingerprint,
            executor_identity=executor_identity,
            reasoning_runtime_identity=reasoning_runtime_identity,
            created_at=dt.datetime.now(dt.UTC),
        )
        _completed, stored_receipt = self.store.complete_once(
            incident.incident_id,
            expected_version=incident.version,
            receipt=receipt,
        )
        return stored_receipt
