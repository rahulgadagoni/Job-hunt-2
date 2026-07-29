import streamlit as st
import json
import os
import pandas as pd

# Page Config
st.set_page_config(page_title="Job Hunt Tracker", layout="wide")

# Title
st.title("🚀 Job Application Dashboard")

# 1. Load Data
file_path = "applications.json"
data = []

if os.path.exists(file_path):
    with open(file_path, "r") as f:
        try:
            content = f.read().strip()
            if content:  # Check if file has content
                data = json.loads(content)
            else:
                data = []  # File is completely empty
        except json.JSONDecodeError:
            data = []  # File contains invalid text or empty list brackets
else:
    st.warning("applications.json not found. Waiting for the first email sync...")

# 2. Display Metrics
if data:
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(data)
    
    # metrics
    total_apps = len(df)
    
    # flexible status checking (case insensitive)
    if "status" in df.columns:
        interviews = df[df['status'].str.contains("Interview", case=False, na=False)].shape[0]
        offers = df[df['status'].str.contains("Offer", case=False, na=False)].shape[0]
        rejections = df[df['status'].str.contains("Reject", case=False, na=False)].shape[0]
    else:
        interviews = 0
        offers = 0
        rejections = 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Applications", total_apps)
    col2.metric("Interviews", interviews)
    col3.metric("Offers", offers)
    col4.metric("Rejections", rejections)

    # 3. Data Table
    st.subheader("Application History")
    
    # Search filter
    search = st.text_input("Search Company or Status", "")
    if search:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "company": "Company",
            "status": "Status",
            "date": "Date Applied",
            "subject": "Email Subject"
        }
    )
else:
    st.info("No applications tracked yet. Your email bot is watching! 👀")
