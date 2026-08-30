#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-hisaarai-agentic-2026}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-hisaarai}"
REPOSITORY="${REPOSITORY:-hisaarai}"
APP_SA="hisaar-app@${PROJECT_ID}.iam.gserviceaccount.com"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/app:manual"

: "${HISAAR_COMMANDER_OAUTH_CLIENT_ID:?Set HISAAR_COMMANDER_OAUTH_CLIENT_ID}"
: "${HISAAR_COMMANDER_SUBJECT:?Set HISAAR_COMMANDER_SUBJECT}"

CURRENT_URL="$(gcloud run services describe "${SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --format='value(status.url)' 2>/dev/null || true)"
EVENT_AUDIENCE="${HISAAR_PUBSUB_AUDIENCE:-${CURRENT_URL:+${CURRENT_URL}/internal/pubsub/events}}"
: "${EVENT_AUDIENCE:?Set HISAAR_PUBSUB_AUDIENCE for the first deployment}"

gcloud builds submit \
  --project="${PROJECT_ID}" \
  --service-account="projects/${PROJECT_ID}/serviceAccounts/${APP_SA}" \
  --gcs-log-dir="gs://${PROJECT_ID}-agent-runtime/build-logs" \
  --gcs-source-staging-dir="gs://${PROJECT_ID}-agent-runtime/build-source" \
  --tag="${IMAGE}" .

gcloud run deploy "${SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --image="${IMAGE}" \
  --service-account="${APP_SA}" \
  --allow-unauthenticated \
  --set-env-vars="HISAAR_ENVIRONMENT=production,HISAAR_LOCATION=${REGION},HISAAR_FIRESTORE_DATABASE=hisaarai,HISAAR_EVENT_TOPIC=hisaar-events,HISAAR_PUBSUB_AUDIENCE=${EVENT_AUDIENCE},HISAAR_COMMANDER_OAUTH_CLIENT_ID=${HISAAR_COMMANDER_OAUTH_CLIENT_ID},HISAAR_COMMANDER_SUBJECT=${HISAAR_COMMANDER_SUBJECT},HISAAR_APP_SERVICE_ACCOUNT=${APP_SA},HISAAR_AP_RUNTIME_NAME=projects/957109932069/locations/us-central1/reasoningEngines/9065615757768916992,HISAAR_RECOVERY_RUNTIME_NAME=projects/957109932069/locations/us-central1/reasoningEngines/6980660236528910336,HISAAR_MODEL_ARMOR_TEMPLATE=hisaarai-ingress"

APP_URL="$(gcloud run services describe "${SERVICE}" --project="${PROJECT_ID}" --region="${REGION}" --format='value(status.url)')"
printf '%s\n' "${APP_URL}"
