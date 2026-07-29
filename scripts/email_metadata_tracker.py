#!/usr/bin/env python3
import argparse
import imaplib
import os
from datetime import datetime, timedelta, timezone
from email import message_from_bytes
from email.utils import parsedate_to_datetime

import psycopg


def fetch_email_metadata() -> list[dict[str, str | datetime | None]]:
    host = os.environ["IMAP_HOST"]
    username = os.environ["IMAP_USERNAME"]
    password = os.environ["IMAP_PASSWORD"]
    mailbox = os.getenv("IMAP_MAILBOX", "INBOX")
    subject_filter = os.getenv("JOB_EMAIL_SUBJECT_FILTER", "application")
    since_days = int(os.getenv("SYNC_SINCE_DAYS", "30"))

    mail = imaplib.IMAP4_SSL(host)
    mail.login(username, password)
    mail.select(mailbox)

    since_date = (datetime.now(timezone.utc) - timedelta(days=since_days)).strftime("%d-%b-%Y")
    status, data = mail.search(None, f'(SINCE "{since_date}" SUBJECT "{subject_filter}")')
    if status != "OK":
        mail.logout()
        return []

    records: list[dict[str, str | datetime | None]] = []
    for raw_id in data[0].split():
        fetch_status, msg_data = mail.fetch(raw_id, "(RFC822.HEADER)")
        if fetch_status != "OK" or not msg_data or not isinstance(msg_data[0], tuple):
            continue

        message = message_from_bytes(msg_data[0][1])
        received_at = None
        if message.get("Date"):
            try:
                received_at = parsedate_to_datetime(message.get("Date"))
            except (TypeError, ValueError):
                received_at = None

        records.append(
            {
                "message_id": message.get("Message-ID", "").strip(),
                "sender": message.get("From", "").strip(),
                "subject": message.get("Subject", "").strip(),
                "received_at": received_at,
            }
        )

    mail.logout()
    return [r for r in records if r["message_id"]]


def persist_records(records: list[dict[str, str | datetime | None]]) -> int:
    if not records:
        return 0

    dsn = os.environ["DATABASE_URL"]
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO job_applications (message_id, sender, subject, received_at, source)
                VALUES (%(message_id)s, %(sender)s, %(subject)s, %(received_at)s, 'email')
                ON CONFLICT (message_id) DO UPDATE
                SET sender = EXCLUDED.sender,
                    subject = EXCLUDED.subject,
                    received_at = EXCLUDED.received_at,
                    updated_at = NOW();
                """,
                records,
            )
        conn.commit()

    return len(records)


def record_sync_run(processed_count: int, status: str) -> None:
    dsn = os.environ["DATABASE_URL"]
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO email_sync_runs (processed_count, status, ran_at)
                VALUES (%s, %s, NOW())
                """,
                (processed_count, status),
            )
        conn.commit()


def run_sync() -> dict[str, int | str]:
    records = fetch_email_metadata()
    processed = persist_records(records)
    record_sync_run(processed, "success")
    return {"processed": processed, "status": "success"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Track job applications from email metadata")
    parser.add_argument("--loop", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=900, help="Loop interval in seconds")
    args = parser.parse_args()

    if not args.loop:
        result = run_sync()
        print(f"Processed {result['processed']} email metadata records")
        return

    import time

    while True:
        try:
            result = run_sync()
            print(f"[{datetime.now(timezone.utc).isoformat()}] Processed {result['processed']} records")
        except Exception as exc:
            print(f"[{datetime.now(timezone.utc).isoformat()}] Sync failed: {exc}")
            try:
                record_sync_run(0, "failure")
            except Exception:
                pass
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
