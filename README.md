# Job-hunt-2

GCP-ready synchronization service for tracking job applications from email metadata.

## Components

- `app/main.py` - FastAPI synchronization server (Cloud Run friendly)
- `scripts/email_metadata_tracker.py` - automated email metadata tracker
- `migrations/001_init.sql` - PostgreSQL schema migration
- `Dockerfile` - Python 3.11 container image
- `scripts/deploy_cloud_run.sh` - deploy pipeline using `gcloud run deploy`

## Local setup

```bash
pip install -r requirements.txt
```

## Run FastAPI server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## Apply PostgreSQL migration

```bash
psql "$DATABASE_URL" -f migrations/001_init.sql
```

## Run email metadata sync

Required environment variables:

- `DATABASE_URL`
- `IMAP_HOST`
- `IMAP_USERNAME`
- `IMAP_PASSWORD`
- Optional: `IMAP_MAILBOX`, `JOB_EMAIL_SUBJECT_FILTER`, `SYNC_SINCE_DAYS`

Single run:

```bash
python scripts/email_metadata_tracker.py
```

Continuous run:

```bash
python scripts/email_metadata_tracker.py --loop --interval 900
```

## Build container

```bash
docker build -t job-hunt-sync:latest .
```

## Deploy to Cloud Run

Set environment variables and deploy:

```bash
export GCP_PROJECT="your-project-id"
export GCP_REGION="us-central1"
export SERVICE_NAME="job-hunt-sync"
export IMAGE_TAG="latest"

bash scripts/deploy_cloud_run.sh
```
