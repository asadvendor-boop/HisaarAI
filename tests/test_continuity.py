from __future__ import annotations

from types import SimpleNamespace

from hisaarai.config import Settings
from hisaarai.continuity import service


class _Snapshot:
    def __init__(self, value: dict[str, object] | None) -> None:
        self._value = value
        self.exists = value is not None

    def to_dict(self) -> dict[str, object] | None:
        return self._value


class _Document:
    def __init__(self, records: dict[str, dict[str, object]], key: str) -> None:
        self.records = records
        self.key = key

    def get(self) -> _Snapshot:
        return _Snapshot(self.records.get(self.key))

    def create(self, value: dict[str, object]) -> None:
        self.records[self.key] = value


class _Collection:
    def __init__(self, records: dict[str, dict[str, object]]) -> None:
        self.records = records

    def document(self, key: str) -> _Document:
        return _Document(self.records, key)


class _Firestore:
    def __init__(self) -> None:
        self.records = {
            "day-0": {
                "memory_revision_name": "projects/p/memories/day0/revisions/r0",
            }
        }

    def collection(self, _name: str) -> _Collection:
        return _Collection(self.records)


class _Memories:
    def __init__(self) -> None:
        revision = SimpleNamespace(
            name="projects/p/memories/day7/revisions/r7",
            fact="",
            create_time="2026-08-25T00:00:00Z",
        )
        self.revisions = SimpleNamespace(
            list=lambda **_kwargs: [revision],
            get=lambda **_kwargs: revision,
        )
        self._revision = revision

    def create(self, *, fact: str, config: dict[str, object], **_kwargs: object):
        if "revision_ttl" in config and "disable_memory_revisions" in config:
            raise ValueError("revision TTL and disable flag are mutually exclusive")
        self._revision.fact = fact
        return SimpleNamespace(
            error=None,
            response=SimpleNamespace(name="projects/p/memories/day7"),
        )

    def get(self, **_kwargs: object):
        return SimpleNamespace(
            name="projects/p/memories/day7",
            create_time="2026-08-25T00:00:00Z",
        )


def test_checkpoint_request_keeps_revisions_enabled_without_conflicting_flag(
    monkeypatch,
) -> None:
    fake_firestore = _Firestore()
    memories = _Memories()
    fake_client = SimpleNamespace(agent_engines=SimpleNamespace(memories=memories))
    monkeypatch.setattr(service, "_firestore", lambda _settings: fake_firestore)
    monkeypatch.setattr(service.vertexai, "Client", lambda **_kwargs: fake_client)
    settings = Settings.from_env(require_auth=False)

    checkpoint = service.create_checkpoint(
        settings,
        day=7,
        requested_date="2026-08-16",
    )

    assert checkpoint["day"] == 7
