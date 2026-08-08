"""Create or update only the two final-named HisaarAI Agent Runtimes."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import vertexai
from vertexai.agent_engines import AdkApp

from hisaarai.agents.ap_skeleton import root_agent as ap_agent
from hisaarai.agents.recovery_fleet import root_agent as recovery_agent


REQUIREMENTS = [
    "cloudpickle==3.1.2",
    "google-adk==2.6.3",
    "google-cloud-aiplatform[adk,agent-engines]==1.163.0",
    "pydantic==2.13.4",
]


def _find_by_display_name(client: Any, display_name: str) -> Any | None:
    matches = [
        item
        for item in client.agent_engines.list()
        if item.api_resource.display_name == display_name
    ]
    if len(matches) > 1:
        raise RuntimeError(f"Multiple Runtimes have display name {display_name!r}")
    return matches[0] if matches else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--location", default="us-central1")
    parser.add_argument("--staging-bucket", required=True)
    parser.add_argument("--ap-service-account", required=True)
    parser.add_argument("--recovery-service-account")
    parser.add_argument(
        "--target",
        choices=("ap", "recovery", "all"),
        default="all",
    )
    args = parser.parse_args()

    os.environ["GOOGLE_GENAI_USE_ENTERPRISE"] = "TRUE"
    client = vertexai.Client(project=args.project, location=args.location)
    if args.target in {"recovery", "all"} and not args.recovery_service_account:
        parser.error("--recovery-service-account is required for recovery deployment")
    project_root = Path(__file__).resolve().parent.parent
    original = Path.cwd()
    try:
        os.chdir(project_root / "src")
        deployments = []
        targets = []
        if args.target in {"ap", "all"}:
            targets.append(
                (
                    "HisaarAI Protected AP",
                    "Protected AP proposal agent; Hisaar Gate retains authority.",
                    "protected-ap",
                    args.ap_service_account,
                    ap_agent,
                )
            )
        if args.target in {"recovery", "all"}:
            targets.append(
                (
                    "HisaarAI Recovery Fleet",
                    "Five-role governed recovery fleet with clean-session execution.",
                    "recovery-fleet",
                    args.recovery_service_account,
                    recovery_agent,
                )
            )
        for display_name, description, role, service_account, agent in targets:
            config = {
                "display_name": display_name,
                "description": description,
                "staging_bucket": args.staging_bucket,
                "requirements": REQUIREMENTS,
                "extra_packages": ["hisaarai"],
                "service_account": service_account,
                "agent_framework": "google-adk",
                "env_vars": {"GOOGLE_GENAI_USE_ENTERPRISE": "TRUE"},
                "labels": {"app": "hisaarai", "role": role},
            }
            existing = _find_by_display_name(client, display_name)
            if existing:
                remote = client.agent_engines.update(
                    name=existing.api_resource.name,
                    agent=AdkApp(agent=agent),
                    config=config,
                )
            else:
                remote = client.agent_engines.create(
                    agent=AdkApp(agent=agent),
                    config=config,
                )
            if remote.api_resource.spec.effective_identity != service_account:
                raise RuntimeError(f"{display_name} effective identity is incorrect")
            deployments.append(remote.api_resource.name)
    finally:
        os.chdir(original)
    for name in deployments:
        print(name)


if __name__ == "__main__":
    main()
