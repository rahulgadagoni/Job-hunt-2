import os
from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(title="Job Hunt Sync Server", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/sync")
def sync() -> dict[str, str | int]:
    # Cloud Run friendly endpoint for triggering sync jobs.
    sync_mode = os.getenv("SYNC_MODE", "email-metadata")
    return {
        "status": "accepted",
        "mode": sync_mode,
        "message": "Invoke scripts/email_metadata_tracker.py from scheduler/worker to run full sync.",
    }
