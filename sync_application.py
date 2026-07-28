import os
import json
import sys
from datetime import datetime

def update_json_tracker(company, role, status):
    file_path = "applications.json"
    
    # 1. Load existing tracking data securely
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Clean inputs to prevent trailing whitespaces or formatting issues
    company = company.strip()
    role = role.strip()
    status = status.strip()

    # 2. Build the structural application item
    new_entry = {
        "id": len(data) + 1,
        "company": company,
        "role": role,
        "status": status,
        "date_logged": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # 3. Look for explicit duplicates to prevent messy sync overlaps
    is_duplicate = any(
        item["company"].lower() == company.lower() and 
        item["role"].lower() == role.lower() and
        item["status"].lower() == status.lower()
        for item in data
    )

    if not is_duplicate:
        data.append(new_entry)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"[SUCCESS] Successfully appended record: {role} at {company}")
    else:
        print(f"[INFO] Duplicate record detected for {company} ({role}). Skipping rewrite.")

if __name__ == "__main__":
    # Ensure all required inputs are forwarded from the runner execution context
    if len(sys.argv) < 4:
        print("[ERROR] Missing required tracking parameters. Usage: script.py <company> <role> <status>")
        sys.exit(1)
        
    input_company = sys.argv[1]
    input_role = sys.argv[2]
    input_status = sys.argv[3]
    
    update_json_tracker(input_company, input_role, input_status)
