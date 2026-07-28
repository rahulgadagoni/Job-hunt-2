#!/usr/bin/env bash
set -euo pipefail

: "${GCP_PROJECT:?Set GCP_PROJECT}"
: "${GCP_REGION:?Set GCP_REGION}"
: "${SERVICE_NAME:?Set SERVICE_NAME}"

IMAGE="gcr.io/${GCP_PROJECT}/${SERVICE_NAME}:${IMAGE_TAG:-latest}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

gcloud config set project "$GCP_PROJECT"
gcloud builds submit --tag "$IMAGE" .
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE" \
  --region "$GCP_REGION" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "SYNC_MODE=email-metadata"
