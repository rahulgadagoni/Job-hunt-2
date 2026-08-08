import hashlib
import os
import sys
from datetime import datetime, timezone

import psycopg

def build_message_id(company, role, status):
    normalized = "|".join(part.strip().lower() for part in (company, role, status))
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return f"manual:{digest}"


def upsert_application(company, role, status):
    company = company.strip()
    role = role.strip()
    status = status.strip()
    message_id = build_message_id(company, role, status)
    received_at = datetime.now(timezone.utc)

    dsn = os.environ["DATABASE_URL"]
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
    """
    INSERT INTO job_applications (message_id, sender, subject, received_at, source)
    VALUES (%s, %s, %s, %s, %s)
    ...
    """,
    (message_id, company, role, received_at, status),
)
        conn.commit()

    print(f"[SUCCESS] Successfully upserted record: {role} at {company}")

if __name__ == "__main__":
    # Ensure all required inputs are forwarded from the runner execution context
    if len(sys.argv) < 4:
        print("[ERROR] Missing required tracking parameters. Usage: script.py <company> <role> <status>")
        sys.exit(1)
        
    input_company = sys.argv[1]
    input_role = sys.argv[2]
    input_status = sys.argv[3]
    
    upsert_application(input_company, input_role, input_status)
