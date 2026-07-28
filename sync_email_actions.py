import imaplib
import email
from email.header import decode_header
import os
import json
import re
from datetime import datetime

# --- Configuration ---
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
IMAP_SERVER = "://gmail.com"
JSON_FILE = "applications.json"

# Keywords to identify job-related emails
KEYWORDS = ["application", "interview", "offer", "rejected", "hiring", "job", "candidate"]

def clean_text(text):
    """Cleans and standardizes text fields."""
    if text:
        return text.strip().replace("\r", "").replace("\n", " ")
    return ""

def get_email_body(msg):
    """Extracts the plain text body from the email."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                return part.get_payload(decode=True).decode()
    else:
        return msg.get_payload(decode=True).decode()
    return ""

def extract_company_name(subject, sender):
    """
    Attempts to extract a company name from the subject or sender.
    Custom logic: Matches 'at [Company]' or checks sender name.
    """
    # Try finding "at [Company]" in subject
    match = re.search(r"\bat\s+([A-Za-z0-9\s]+)", subject, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Fallback: Use the sender's display name
    if "<" in sender:
        name = sender.split("<")[0].strip().replace('"', '')
        return name
    return "Unknown Company"

def sync_emails():
    # 1. Load existing applications
    applications = []
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as f:
            try:
                applications = json.load(f)
            except json.JSONDecodeError:
                applications = []
    
    print(f"Loaded {len(applications)} existing applications.")

    # 2. Connect to Email
    if not EMAIL_USER or not EMAIL_PASS:
        print("Error: EMAIL_USER or EMAIL_PASS environment variables not set.")
        return

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 3. Search for Emails (Last 7 days to save time, or adjust as needed)
    # Search criteria: ALL or specific keywords in SUBJECT
    # Using 'ALL' and filtering in python for flexibility
    status, messages = mail.search(None, 'ALL')
    
    if status != "OK":
        print("No messages found!")
        return

    email_ids = messages[0].split()
    # Process only the last 50 emails to prevent timeouts
    latest_email_ids = email_ids[-50:] 

    new_entries = 0

    for eid in reversed(latest_email_ids):
        res, msg_data = mail.fetch(eid, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                
                # Decode Subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")
                
                # Filter by Keywords
                if not any(keyword in subject.lower() for keyword in KEYWORDS):
                    continue

                sender = msg.get("From")
                date_str = msg.get("Date")
                
                # Extract Data
                company = extract_company_name(subject, sender)
                status_update = "Applied" # Default, logic can be improved
                if "interview" in subject.lower():
                    status_update = "Interview"
                elif "reject" in subject.lower():
                    status_update = "Rejected"
                elif "offer" in subject.lower():
                    status_update = "Offer"

                # Check if already exists (prevent duplicates based on company/date)
                is_duplicate = False
                for app in applications:
                    if app.get("company") == company and app.get("subject") == subject:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    new_app = {
                        "company": company,
                        "status": status_update,
                        "date": date_str,
                        "subject": clean_text(subject),
                        "sender": clean_text(sender)
                    }
                    applications.append(new_app)
                    new_entries += 1
                    print(f"Added: {company} - {status_update}")

    mail.close()
    mail.logout()

    # 4. Save updates to JSON
    if new_entries > 0:
        with open(JSON_FILE, "w") as f:
            json.dump(applications, f, indent=4)
        print(f"Successfully added {new_entries} new applications to {JSON_FILE}.")
    else:
        print("No new relevant emails found.")

if __name__ == "__main__":
    sync_emails()

