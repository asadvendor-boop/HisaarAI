"""Authority-store implementations with short atomic transitions."""

from __future__ import annotations

import copy
import threading
from typing import Any, Protocol

from google.cloud import firestore

from hisaarai.contracts import Incident, IncidentState, SandboxReceipt, VendorRecord


class ConflictError(RuntimeError):
    pass


class NotFoundError(RuntimeError):
    pass


def _receipt_binding(receipt: SandboxReceipt) -> tuple[object, ...]:
    return (
        receipt.business_idempotency_key,
        receipt.incident_id,
        receipt.attempt_id,
        receipt.warrant_digest,
        receipt.vendor_id,
        receipt.amount_minor,
        receipt.currency,
        receipt.bank_fingerprint,
        receipt.executor_identity,
        receipt.reasoning_runtime_identity,
    )


class AuthorityStore(Protocol):
    def create_incident(self, incident: Incident) -> Incident: ...

    def get_incident(self, incident_id: str) -> Incident: ...

    def transition(
        self,
        incident_id: str,
        *,
        expected_state: IncidentState,
        expected_version: int,
        new_state: IncidentState,
        changes: dict[str, Any] | None = None,
    ) -> Incident: ...

    def complete_once(
        self,
        incident_id: str,
        *,
        expected_version: int,
        receipt: SandboxReceipt,
    ) -> tuple[Incident, SandboxReceipt]: ...

    def get_receipt(self, business_idempotency_key: str) -> SandboxReceipt | None: ...

    def put_vendor(self, vendor: VendorRecord) -> None: ...

    def get_vendor(self, vendor_id: str) -> VendorRecord: ...


class InMemoryStore:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._incidents: dict[str, Incident] = {}
        self._receipts: dict[str, SandboxReceipt] = {}
        self._vendors: dict[str, VendorRecord] = {}

    def create_incident(self, incident: Incident) -> Incident:
        with self._lock:
            if incident.incident_id in self._incidents:
                raise ConflictError("Incident already exists")
            self._incidents[incident.incident_id] = copy.deepcopy(incident)
            return copy.deepcopy(incident)

    def get_incident(self, incident_id: str) -> Incident:
        with self._lock:
            try:
                return copy.deepcopy(self._incidents[incident_id])
            except KeyError as exc:
                raise NotFoundError("Incident not found") from exc

    def transition(
        self,
        incident_id: str,
        *,
        expected_state: IncidentState,
        expected_version: int,
        new_state: IncidentState,
        changes: dict[str, Any] | None = None,
    ) -> Incident:
        with self._lock:
            current = self.get_incident(incident_id)
            if current.state != expected_state or current.version != expected_version:
                raise ConflictError("Incident state/version changed")
            payload = current.model_dump()
            payload.update(changes or {})
            payload["state"] = new_state
            payload["version"] = current.version + 1
            payload["state_history"] = [
                *current.state_history,
                {
                    "state": new_state,
                    "version": current.version + 1,
                    "at": payload.get("updated_at"),
                    "reason": payload.get("reason"),
                },
            ]
            updated = Incident.model_validate(payload)
            self._incidents[incident_id] = copy.deepcopy(updated)
            return copy.deepcopy(updated)

    def complete_once(
        self,
        incident_id: str,
        *,
        expected_version: int,
        receipt: SandboxReceipt,
    ) -> tuple[Incident, SandboxReceipt]:
        with self._lock:
            existing = self._receipts.get(receipt.business_idempotency_key)
            current = self.get_incident(incident_id)
            if existing:
                if _receipt_binding(existing) != _receipt_binding(receipt):
                    raise ConflictError("Idempotency key is bound to another receipt")
                return current, copy.deepcopy(existing)
            if current.state != IncidentState.APPROVED:
                raise ConflictError("Execution requires APPROVED state")
            if current.version != expected_version:
                raise ConflictError("Incident version changed")
            completed = self.transition(
                incident_id,
                expected_state=IncidentState.APPROVED,
                expected_version=expected_version,
                new_state=IncidentState.COMPLETED,
                changes={"receipt_id": receipt.receipt_id},
            )
            self._receipts[receipt.business_idempotency_key] = copy.deepcopy(receipt)
            return completed, copy.deepcopy(receipt)

    def get_receipt(self, business_idempotency_key: str) -> SandboxReceipt | None:
        with self._lock:
            receipt = self._receipts.get(business_idempotency_key)
            return copy.deepcopy(receipt) if receipt else None

    def put_vendor(self, vendor: VendorRecord) -> None:
        with self._lock:
            self._vendors[vendor.vendor_id] = copy.deepcopy(vendor)

    def get_vendor(self, vendor_id: str) -> VendorRecord:
        with self._lock:
            try:
                return copy.deepcopy(self._vendors[vendor_id])
            except KeyError as exc:
                raise NotFoundError("Vendor not found") from exc


class FirestoreStore:
    def __init__(self, *, project: str, database: str) -> None:
        self.client = firestore.Client(project=project, database=database)

    @staticmethod
    def _incident_from_snapshot(snapshot: Any) -> Incident:
        if not snapshot.exists:
            raise NotFoundError("Incident not found")
        return Incident.model_validate(snapshot.to_dict())

    def create_incident(self, incident: Incident) -> Incident:
        ref = self.client.collection("incidents").document(incident.incident_id)
        try:
            ref.create(incident.model_dump(mode="json"))
        except Exception as exc:
            raise ConflictError("Incident already exists") from exc
        return self.get_incident(incident.incident_id)

    def get_incident(self, incident_id: str) -> Incident:
        ref = self.client.collection("incidents").document(incident_id)
        return self._incident_from_snapshot(ref.get())

    def transition(
        self,
        incident_id: str,
        *,
        expected_state: IncidentState,
        expected_version: int,
        new_state: IncidentState,
        changes: dict[str, Any] | None = None,
    ) -> Incident:
        ref = self.client.collection("incidents").document(incident_id)
        transaction = self.client.transaction()

        @firestore.transactional
        def apply(txn: Any) -> dict[str, Any]:
            snapshot = ref.get(transaction=txn)
            current = self._incident_from_snapshot(snapshot)
            if current.state != expected_state or current.version != expected_version:
                raise ConflictError("Incident state/version changed")
            payload = current.model_dump(mode="json")
            payload.update(changes or {})
            payload["state"] = new_state.value
            payload["version"] = current.version + 1
            payload["state_history"] = [
                *current.model_dump(mode="json")["state_history"],
                {
                    "state": new_state.value,
                    "version": current.version + 1,
                    "at": payload.get("updated_at"),
                    "reason": payload.get("reason"),
                },
            ]
            updated = Incident.model_validate(payload)
            encoded = updated.model_dump(mode="json")
            txn.set(ref, encoded)
            return encoded

        return Incident.model_validate(apply(transaction))

    def complete_once(
        self,
        incident_id: str,
        *,
        expected_version: int,
        receipt: SandboxReceipt,
    ) -> tuple[Incident, SandboxReceipt]:
        incident_ref = self.client.collection("incidents").document(incident_id)
        receipt_ref = self.client.collection("sandbox_receipts").document(
            receipt.business_idempotency_key
        )
        transaction = self.client.transaction()

        @firestore.transactional
        def apply(txn: Any) -> tuple[dict[str, Any], dict[str, Any]]:
            incident_snapshot = incident_ref.get(transaction=txn)
            receipt_snapshot = receipt_ref.get(transaction=txn)
            current = self._incident_from_snapshot(incident_snapshot)
            expected_receipt = receipt.model_dump(mode="json")
            if receipt_snapshot.exists:
                existing = receipt_snapshot.to_dict() or {}
                parsed_existing = SandboxReceipt.model_validate(existing)
                if _receipt_binding(parsed_existing) != _receipt_binding(receipt):
                    raise ConflictError("Idempotency key is bound to another receipt")
                return current.model_dump(mode="json"), parsed_existing.model_dump(
                    mode="json"
                )
            if current.state != IncidentState.APPROVED:
                raise ConflictError("Execution requires APPROVED state")
            if current.version != expected_version:
                raise ConflictError("Incident version changed")
            payload = current.model_dump(mode="json")
            payload.update(
                {
                    "state": IncidentState.COMPLETED.value,
                    "version": current.version + 1,
                    "receipt_id": receipt.receipt_id,
                    "updated_at": receipt.created_at,
                    "state_history": [
                        *current.model_dump(mode="json")["state_history"],
                        {
                            "state": IncidentState.COMPLETED.value,
                            "version": current.version + 1,
                            "at": receipt.created_at,
                            "reason": None,
                        },
                    ],
                }
            )
            completed = Incident.model_validate(payload).model_dump(mode="json")
            txn.create(receipt_ref, expected_receipt)
            txn.set(incident_ref, completed)
            return completed, expected_receipt

        completed, stored_receipt = apply(transaction)
        return Incident.model_validate(completed), SandboxReceipt.model_validate(
            stored_receipt
        )

    def get_receipt(self, business_idempotency_key: str) -> SandboxReceipt | None:
        snap = self.client.collection("sandbox_receipts").document(
            business_idempotency_key
        ).get()
        return SandboxReceipt.model_validate(snap.to_dict()) if snap.exists else None

    def put_vendor(self, vendor: VendorRecord) -> None:
        self.client.collection("vendor_master").document(vendor.vendor_id).set(
            vendor.model_dump(mode="json")
        )

    def get_vendor(self, vendor_id: str) -> VendorRecord:
        snap = self.client.collection("vendor_master").document(vendor_id).get()
        if not snap.exists:
            raise NotFoundError("Vendor not found")
        return VendorRecord.model_validate(snap.to_dict())
