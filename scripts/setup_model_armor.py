"""Create the committed Model Armor template and calibrate all three fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import AlreadyExists, NotFound
from google.cloud import modelarmor_v1

from hisaarai.screening import ModelArmorScreen


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--location", default="us-central1")
    parser.add_argument("--template-id", default="hisaarai-ingress")
    parser.add_argument(
        "--evidence",
        type=Path,
        default=Path("docs/evidence/model-armor-calibration.json"),
    )
    args = parser.parse_args()

    endpoint = f"modelarmor.{args.location}.rep.googleapis.com"
    client = modelarmor_v1.ModelArmorClient(
        transport="rest",
        client_options=ClientOptions(api_endpoint=endpoint),
    )
    parent = f"projects/{args.project}/locations/{args.location}"
    name = f"{parent}/templates/{args.template_id}"
    try:
        template = client.get_template(name=name)
    except NotFound:
        template = modelarmor_v1.Template(
            filter_config=modelarmor_v1.FilterConfig(
                pi_and_jailbreak_filter_settings=(
                    modelarmor_v1.PiAndJailbreakFilterSettings(
                        filter_enforcement=(
                            modelarmor_v1.PiAndJailbreakFilterSettings.PiAndJailbreakFilterEnforcement.ENABLED
                        ),
                        confidence_level=(
                            modelarmor_v1.DetectionConfidenceLevel.MEDIUM_AND_ABOVE
                        ),
                    )
                )
            ),
            labels={"app": "hisaarai", "purpose": "invoice-ingress"},
        )
        try:
            template = client.create_template(
                parent=parent,
                template=template,
                template_id=args.template_id,
            )
        except AlreadyExists:
            template = client.get_template(name=name)

    screen = ModelArmorScreen(
        project=args.project,
        location=args.location,
        template_id=args.template_id,
    )
    results: dict[str, object] = {
        "template_name": template.name,
        "template_endpoint": endpoint,
        "fixtures": {},
    }
    for path in sorted(Path("fixtures/invoices").glob("*.pdf")):
        result = screen.screen_pdf_and_text(path)
        results["fixtures"][path.name] = {
            "decision": result.decision.value,
            "pdf_decision": result.pdf_decision.value,
            "text_decision": result.text_decision.value,
            "extracted_text_length": len(result.extracted_text),
        }
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

