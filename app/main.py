import os
from datetime import datetime, timezone

from fastapi import FastAPI

from scripts.email_metadata_tracker import run_sync

app = FastAPI(title="Job Hunt Sync Server", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/sync")
def sync() -> dict[str, str | int]:
    sync_mode = os.getenv("SYNC_MODE", "email-metadata")
    result = run_sync()
    return {
        "status": result["status"],
        "processed": result["processed"],
        "mode": sync_mode,
    }
