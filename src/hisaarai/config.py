"""Environment-backed configuration for the single HisaarAI application."""

from __future__ import annotations

from dataclasses import dataclass
import os


PROJECT_ID_DEFAULT = "hisaarai-agentic-2026"
LOCATION_DEFAULT = "us-central1"
RECOVERY_RUNTIME_DEFAULT = (
    "projects/957109932069/locations/us-central1/"
    "reasoningEngines/6980660236528910336"
)
AP_RUNTIME_DEFAULT = (
    "projects/957109932069/locations/us-central1/"
    "reasoningEngines/9065615757768916992"
)


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Required environment variable {name} is not configured")
    return value


@dataclass(frozen=True)
class Settings:
    project_id: str
    location: str
    firestore_database: str
    event_topic: str
    pubsub_audience: str
    commander_oauth_client_id: str
    commander_subject: str
    app_service_account: str
    ap_runtime_service_account: str
    recovery_runtime_service_account: str
    recovery_runtime_name: str
    ap_runtime_name: str
    model_armor_template: str
    environment: str

    @classmethod
    def from_env(cls, *, require_auth: bool = True) -> "Settings":
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", PROJECT_ID_DEFAULT)
        app_sa = f"hisaar-app@{project_id}.iam.gserviceaccount.com"
        ap_sa = f"hisaar-ap-runtime@{project_id}.iam.gserviceaccount.com"
        recovery_sa = (
            f"hisaar-recovery-runtime@{project_id}.iam.gserviceaccount.com"
        )
        return cls(
            project_id=project_id,
            location=os.getenv("HISAAR_LOCATION", LOCATION_DEFAULT),
            firestore_database=os.getenv("HISAAR_FIRESTORE_DATABASE", "hisaarai"),
            event_topic=os.getenv("HISAAR_EVENT_TOPIC", "hisaar-events"),
            pubsub_audience=(
                _required("HISAAR_PUBSUB_AUDIENCE")
                if require_auth
                else os.getenv("HISAAR_PUBSUB_AUDIENCE", "")
            ),
            commander_oauth_client_id=(
                _required("HISAAR_COMMANDER_OAUTH_CLIENT_ID")
                if require_auth
                else os.getenv("HISAAR_COMMANDER_OAUTH_CLIENT_ID", "")
            ),
            commander_subject=(
                _required("HISAAR_COMMANDER_SUBJECT")
                if require_auth
                else os.getenv("HISAAR_COMMANDER_SUBJECT", "")
            ),
            app_service_account=os.getenv("HISAAR_APP_SERVICE_ACCOUNT", app_sa),
            ap_runtime_service_account=os.getenv(
                "HISAAR_AP_RUNTIME_SERVICE_ACCOUNT", ap_sa
            ),
            recovery_runtime_service_account=os.getenv(
                "HISAAR_RECOVERY_RUNTIME_SERVICE_ACCOUNT", recovery_sa
            ),
            recovery_runtime_name=os.getenv(
                "HISAAR_RECOVERY_RUNTIME_NAME", RECOVERY_RUNTIME_DEFAULT
            ),
            ap_runtime_name=os.getenv("HISAAR_AP_RUNTIME_NAME", AP_RUNTIME_DEFAULT),
            model_armor_template=os.getenv(
                "HISAAR_MODEL_ARMOR_TEMPLATE", "hisaarai-ingress"
            ),
            environment=os.getenv("HISAAR_ENVIRONMENT", "production"),
        )
