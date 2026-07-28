import streamlit as st
import json
import os

st.set_page_config(page_title="Job Hunt Dashboard", layout="wide")
st.title("💼 Job Application Tracker Dashboard")

# Load data
if os.path.exists("applications.json"):
    with open("applications.json", "r") as f:
        data = json.load(f)
else:
    data = []

# Metrics
total_apps = len(data)
interviews = sum(1 for x in data if x.get("status") == "Interview")
rejections = sum(1 for x in data if x.get("status") == "Rejected")

col1, col2, col3 = st.columns(3)
col1.metric("Total Applications", total_apps)
col2.metric("Interviews Scheduled", interviews)
col3.metric("Rejections", rejections)

# Table display
st.subheader("All Application Logs")
if data:
    st.dataframe(data, use_container_width=True)
else:
    st.info("No applications found yet. Wait for the email sync to run!")
