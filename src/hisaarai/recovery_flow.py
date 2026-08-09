"""Bounded recovery planning with Gate-owned authority."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import logging
from collections.abc import Callable
from typing import Any
import uuid

from hisaarai.config import Settings
from hisaarai.continuity.service import latest_checkpoint
from hisaarai.contracts import (
    Incident,
    IncidentState,
    PaymentProposal,
    RecoveryWarrant,
    VendorRecord,
)
from hisaarai.gate import HisaarGate
from hisaarai.observability import stage_span
from hisaarai.recovery_runtime import RecoveryRuntimeClient
from hisaarai.store import AuthorityStore


logger = logging.getLogger(__name__)


def _warrant_digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=lambda value: value.isoformat(),
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


class RecoveryFlow:
    def __init__(
        self,
        *,
        settings: Settings,
        store: AuthorityStore,
        runtime: RecoveryRuntimeClient | None = None,
        checkpoint_loader: Callable[[], dict[str, Any]] | None = None,
    ) -> None:
        self.settings = settings
        self.store = store
        self.gate = HisaarGate(store)
        self.runtime = runtime or RecoveryRuntimeClient(settings)
        self.checkpoint_loader = checkpoint_loader or (
            lambda: latest_checkpoint(settings)
        )

    @staticmethod
    def _materialize_warrant(
        incident: Incident,
        *,
        proposal: PaymentProposal,
        vendor: VendorRecord,
        revision_name: str,
    ) -> RecoveryWarrant:
        now = dt.datetime.now(dt.UTC)
        warrant_payload: dict[str, Any] = {
            "warrant_id": f"war-{uuid.uuid4().hex[:12]}",
            "incident_id": incident.incident_id,
            "attempt_id": incident.attempt_id,
            "invoice_id": incident.invoice_id,
            "vendor_id": vendor.vendor_id,
            "amount_minor": proposal.amount_minor,
            "currency": proposal.currency,
            "bank_fingerprint": vendor.bank_fingerprint,
            "trusted_vendor_version": vendor.version,
            "continuity_revision_name": revision_name,
            "expires_at": now + dt.timedelta(minutes=10),
        }
        return RecoveryWarrant(
            **warrant_payload,
            digest=_warrant_digest(warrant_payload),
        )

    def prepare_clean(self, incident_id: str) -> Incident:
        incident = self.store.get_incident(incident_id)
        if incident.state != IncidentState.PLAN_READY or incident.proposal is None:
            raise ValueError("Clean approval preparation requires PLAN_READY")
        checkpoint = self.checkpoint_loader()
        revision_name = str(checkpoint["memory_revision_name"])
        vendor = self.store.get_vendor(incident.proposal.vendor_id)
        if (
            incident.proposal.bank_fingerprint != vendor.bank_fingerprint
            or incident.proposal.vendor_id != vendor.vendor_id
        ):
            raise ValueError("Clean proposal no longer matches the trusted source")
        warrant = self._materialize_warrant(
            incident,
            proposal=incident.proposal,
            vendor=vendor,
            revision_name=revision_name,
        )
        return self.gate.transition(
            incident,
            IncidentState.AWAITING_APPROVAL,
            changes={
                "warrant": warrant,
                "continuity_revision_name": revision_name,
                "reason": None,
            },
        )

    def plan(self, incident_id: str) -> Incident:
        incident = self.store.get_incident(incident_id)
        if incident.state != IncidentState.QUARANTINED:
            raise ValueError("Recovery planning requires a quarantined incident")
        investigating = self.gate.transition(
            incident,
            IncidentState.INVESTIGATING,
            changes={"reason": None},
        )
        try:
            checkpoint = self.checkpoint_loader()
            revision_name = str(checkpoint["memory_revision_name"])
            policy = str(checkpoint["fact"])
            if "trusted vendor master" not in policy.lower():
                raise ValueError("Continuity policy does not select trusted reconstruction")
            vendor = self.store.get_vendor("vendor-northstar")
            proposal = investigating.proposal
            if proposal is None:
                raise ValueError("Quarantined proposal evidence is missing")
            evidence_ids = [
                f"incident:{investigating.incident_id}:v{investigating.version}",
                f"vendor:{vendor.vendor_id}:v{vendor.version}",
                revision_name,
            ]
            with stage_span(
                investigating.correlation_id,
                "recovery_fleet_plan",
                incident_id=investigating.incident_id,
            ):
                findings = self.runtime.plan({
                    "incident_id": investigating.incident_id,
                    "correlation_id": investigating.correlation_id,
                    "invoice_id": investigating.invoice_id,
                    "proposal": {
                        "vendor_id": proposal.vendor_id,
                        "amount_display": proposal.amount_minor / 100,
                        "currency": proposal.currency,
                        "proposed_bank_fingerprint": proposal.bank_fingerprint,
                    },
                    "trusted_vendor": vendor.model_dump(mode="json"),
                    "continuity": {
                        "revision_name": revision_name,
                        "playbook": "TRUSTED_VENDOR_RECONSTRUCTION",
                    },
                    "evidence_ids": evidence_ids,
                    "receipt_id": investigating.receipt_id,
                })
            if len(findings) != 3:
                raise ValueError("All three planning findings are required")
        except Exception:
            logger.exception(
                "Recovery planning failed closed for %s",
                investigating.incident_id,
            )
            return self.gate.transition(
                investigating,
                IncidentState.BLOCKED,
                reason="RECOVERY_EVIDENCE_OR_AGENT_FAILED",
            )

        plan_ready = self.gate.transition(
            investigating,
            IncidentState.PLAN_READY,
            changes={
                "findings": findings,
                "continuity_revision_name": revision_name,
                "reason": None,
            },
        )
        warrant = self._materialize_warrant(
            plan_ready,
            proposal=proposal,
            vendor=vendor,
            revision_name=revision_name,
        )
        return self.gate.transition(
            plan_ready,
            IncidentState.AWAITING_APPROVAL,
            changes={"warrant": warrant, "reason": None},
        )
