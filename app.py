import os

import pandas as pd
import psycopg
from psycopg.rows import dict_row
import streamlit as st

# Page Config
st.set_page_config(page_title="Job Hunt Tracker", layout="wide")

# Title
st.title("🚀 Job Application Dashboard")

@st.cache_data(ttl=60)
def load_applications(database_url: str) -> pd.DataFrame:
    query = """
        SELECT sender, subject, received_at, source
        FROM job_applications
        ORDER BY COALESCE(received_at, created_at) DESC, id DESC
    """

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    return pd.DataFrame(rows)


database_url = os.getenv("DATABASE_URL")
if not database_url:
    st.warning("DATABASE_URL is not set. Configure the database connection to load applications.")
    data = pd.DataFrame()
else:
    try:
        data = load_applications(database_url)
    except Exception as exc:
        st.error(f"Failed to load applications from Postgres: {exc}")
        data = pd.DataFrame()

# 2. Display Metrics
if not data.empty:
    # Convert to DataFrame for easier manipulation
    df = data.copy()
    
    # metrics
    total_apps = len(df)
    email_sourced = int((df["source"] == "email").sum()) if "source" in df.columns else 0
    manual_sourced = total_apps - email_sourced
    recent_cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=7)
    recent_apps = int(df["received_at"].ge(recent_cutoff).sum()) if "received_at" in df.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Applications", total_apps)
    col2.metric("Email Records", email_sourced)
    col3.metric("Manual Records", manual_sourced)
    col4.metric("Last 7 Days", recent_apps)

    # 3. Data Table
    st.subheader("Application History")
    
    # Search filter
    search = st.text_input("Search sender, subject, or source", "")
    if search:
        df = df[df.astype(str).apply(lambda column: column.str.contains(search, case=False, na=False)).any(axis=1)]

    display_df = df.rename(
        columns={
            "sender": "Sender",
            "subject": "Subject",
            "received_at": "Received At",
            "source": "Source",
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "Sender": "Sender",
            "Subject": "Subject",
            "Received At": "Received At",
            "Source": "Source",
        }
    )
else:
    st.info("No applications tracked yet. Your sync jobs will populate Postgres here.")
