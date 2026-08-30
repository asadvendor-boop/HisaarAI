"""Mirror the genuine Day-0 MemoryRevision evidence into Firestore once."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

from google.cloud import firestore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--database", default="hisaarai")
    parser.add_argument(
        "--evidence",
        type=Path,
        default=Path("docs/evidence/day-0-continuity.json"),
    )
    args = parser.parse_args()

    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    if evidence["calendar"]["day_0"] != "2026-08-09":
        raise RuntimeError("Day-0 evidence does not match the approved calendar")
    if not evidence["memory_revision_name"].startswith(
        evidence["memory_name"] + "/revisions/"
    ):
        raise RuntimeError("Day-0 MemoryRevision is not parent-bound")

    checkpoint = {
        "day": 0,
        "calendar_date": "2026-08-09",
        "calendar_timezone": "Asia/Karachi",
        "fact": evidence["fact"],
        "previous_revision_name": None,
        "memory_name": evidence["memory_name"],
        "memory_revision_name": evidence["memory_revision_name"],
        "memory_create_time": dt.datetime.fromisoformat(
            evidence["memory_create_time"]
        ),
        "revision_create_time": dt.datetime.fromisoformat(
            evidence["memory_revision_create_time"]
        ),
        "created_at": firestore.SERVER_TIMESTAMP,
        "creation_actor": evidence["memory_creation_actor"],
        "source": "genuine Day-0 API readback",
    }
    db = firestore.Client(project=args.project, database=args.database)
    ref = db.collection("continuity_checkpoints").document("day-0")
    existing = ref.get()
    if existing.exists:
        stored = existing.to_dict() or {}
        if stored.get("memory_revision_name") != checkpoint["memory_revision_name"]:
            raise RuntimeError("Existing Day-0 checkpoint disagrees with evidence")
    else:
        ref.create(checkpoint)
    print(json.dumps(ref.get().to_dict(), indent=2, default=str, sort_keys=True))


if __name__ == "__main__":
    main()

