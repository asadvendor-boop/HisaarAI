"""Deploy the minimal recovery runtime and create a genuine Day-0 memory.

This script intentionally performs only the calendar-sensitive bootstrap. The
same Agent Runtime resource is updated with the full recovery fleet later.
"""

from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

import vertexai
from vertexai.agent_engines import AdkApp

from hisaarai.continuity.recovery_skeleton import root_agent


DAY0_FACT = (
    "HisaarAI Day 0 continuity policy: recovery must exclude quarantined "
    "invoice-derived context and use the trusted vendor master before any "
    "sandbox payment."
)
DAY0_SCOPE = {
    "app_name": "hisaarai",
    "timeline": "all-things-agentic-2026",
}
RUNTIME_REQUIREMENTS = [
    "cloudpickle==3.1.2",
    "google-adk==2.6.3",
    "google-cloud-aiplatform[adk,agent-engines]==1.163.0",
    "pydantic==2.13.4",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--location", default="us-central1")
    parser.add_argument("--staging-bucket", required=True)
    parser.add_argument("--service-account", required=True)
    parser.add_argument(
        "--runtime-name",
        help="Update this Runtime instead of creating a second resource.",
    )
    parser.add_argument(
        "--memory-name",
        help="Re-read this Day-0 Memory instead of creating a second record.",
    )
    parser.add_argument(
        "--readback-only",
        action="store_true",
        help="Do not deploy; only verify the existing Runtime, Memory and revision.",
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        default=Path("docs/evidence/day-0-continuity.json"),
    )
    return parser.parse_args()


def isoformat(value: Any) -> str:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


async def probe_runtime(remote_runtime: Any) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    async for event in remote_runtime.async_stream_query(
        user_id="day0-verifier",
        message="State the continuity policy in one short sentence.",
    ):
        if not isinstance(event, dict):
            raise RuntimeError(f"Unexpected Runtime event type: {type(event)!r}")
        events.append(event)

    errors = [event for event in events if event.get("error_code") or event.get("code")]
    text_parts = [
        part["text"]
        for event in events
        for part in event.get("content", {}).get("parts", [])
        if isinstance(part, dict) and part.get("text")
    ]
    if errors or not text_parts:
        raise RuntimeError(f"Remote Runtime probe failed: {errors or events}")
    return {
        "event_count": len(events),
        "response_text": " ".join(text_parts).strip(),
    }


def main() -> None:
    args = parse_args()
    os.environ["GOOGLE_GENAI_USE_ENTERPRISE"] = "TRUE"

    client = vertexai.Client(project=args.project, location=args.location)
    project_root = Path(__file__).resolve().parent.parent
    runtime_config = {
        "display_name": "HisaarAI Recovery Fleet",
        "description": (
            "Final-named recovery runtime bootstrapped for genuine Day-0 "
            "Memory Bank continuity."
        ),
        "staging_bucket": args.staging_bucket,
        "requirements": RUNTIME_REQUIREMENTS,
        # The deployer preserves archive paths. Package from within src/ so the
        # remote archive contains top-level hisaarai/, which cloudpickle can
        # import when it restores GlobalGemini.
        "extra_packages": ["hisaarai"],
        "service_account": args.service_account,
        "agent_framework": "google-adk",
        "env_vars": {"GOOGLE_GENAI_USE_ENTERPRISE": "TRUE"},
        "labels": {
            "app": "hisaarai",
            "role": "recovery-fleet",
            "phase": "day0",
        },
    }
    if args.readback_only:
        if not args.runtime_name or not args.memory_name:
            raise ValueError("--readback-only requires --runtime-name and --memory-name")
        remote_runtime = client.agent_engines.get(name=args.runtime_name)
    else:
        original_working_directory = Path.cwd()
        try:
            os.chdir(project_root / "src")
            if args.runtime_name:
                remote_runtime = client.agent_engines.update(
                    name=args.runtime_name,
                    agent=AdkApp(agent=root_agent),
                    config=runtime_config,
                )
            else:
                remote_runtime = client.agent_engines.create(
                    agent=AdkApp(agent=root_agent),
                    config=runtime_config,
                )
        finally:
            os.chdir(original_working_directory)
    runtime_name = remote_runtime.api_resource.name
    runtime_spec = remote_runtime.api_resource.spec
    runtime_service_account = runtime_spec.service_account
    runtime_effective_identity = runtime_spec.effective_identity
    if runtime_service_account != args.service_account:
        raise RuntimeError(
            "Runtime service account does not match the requested identity: "
            f"{runtime_service_account!r}"
        )
    if runtime_effective_identity != args.service_account:
        raise RuntimeError(
            "Runtime effective identity does not match the requested identity: "
            f"{runtime_effective_identity!r}"
        )

    if args.memory_name:
        memory_name = args.memory_name
    else:
        operation = client.agent_engines.memories.create(
            name=runtime_name,
            fact=DAY0_FACT,
            scope=DAY0_SCOPE,
            config={
                "memory_id": "hisaarai-continuity-day0",
                "wait_for_completion": True,
                "disable_memory_revisions": False,
                "revision_ttl": "31536000s",
            },
        )
        if operation.error is not None or operation.response is None:
            raise RuntimeError(f"Day-0 Memory creation failed: {operation.error}")
        memory_name = operation.response.name
    confirmed = client.agent_engines.memories.get(name=memory_name)

    if not confirmed.name.startswith(f"{runtime_name}/memories/"):
        raise RuntimeError("Retrieved Day-0 Memory is not a child of the Runtime")
    if confirmed.fact != DAY0_FACT:
        raise RuntimeError("Retrieved Day-0 fact does not match the created fact")
    if dict(confirmed.scope) != DAY0_SCOPE:
        raise RuntimeError("Retrieved Day-0 scope does not match the created scope")

    revisions = list(client.agent_engines.memories.revisions.list(name=memory_name))
    matching_revisions = [revision for revision in revisions if revision.fact == DAY0_FACT]
    if len(matching_revisions) != 1:
        raise RuntimeError(
            "Expected exactly one immutable revision matching the Day-0 fact, "
            f"found {len(matching_revisions)}"
        )
    revision = client.agent_engines.memories.revisions.get(
        name=matching_revisions[0].name
    )
    if not revision.name.startswith(f"{confirmed.name}/revisions/"):
        raise RuntimeError("Retrieved revision is not a child of the Day-0 Memory")
    if revision.fact != DAY0_FACT:
        raise RuntimeError("Retrieved Day-0 revision does not match the created fact")

    probe = asyncio.run(probe_runtime(remote_runtime))
    evidence = {
        "schema_version": 1,
        "day": 0,
        "project_id": args.project,
        "location": args.location,
        "runtime_name": runtime_name,
        "runtime_service_account": runtime_service_account,
        "runtime_effective_identity": runtime_effective_identity,
        "memory_creation_actor": (
            "Local deployer application-default credentials; Memory is stored "
            "under the deployed Recovery Runtime"
        ),
        "memory_name": memory_name,
        "memory_create_time": isoformat(confirmed.create_time),
        "memory_update_time": isoformat(confirmed.update_time),
        "memory_revision_name": revision.name,
        "memory_revision_create_time": isoformat(revision.create_time),
        "memory_revision_expire_time": isoformat(revision.expire_time),
        "scope": dict(confirmed.scope),
        "fact": confirmed.fact,
        "requested_model": "gemini-3.5-flash-lite",
        "configured_model_endpoint": "global",
        "runtime_probe": probe,
        "calendar": {
            "timezone": "Asia/Karachi",
            "day_0": "2026-08-09",
            "day_7": "2026-08-16",
            "day_14": "2026-08-23",
            "day_21": "2026-08-30",
        },
        "recorded_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "source": (
            "Callable Google Agent Runtime plus Memory Bank and immutable "
            "MemoryRevision API readback"
        ),
    }
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(evidence, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
