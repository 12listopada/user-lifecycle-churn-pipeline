"""
04_export_powerbi.py
Exports three CSV files, ready for Power BI import: a fact table of
events, a user dimension enriched with RFM + churn score, and a date
dimension for time-intelligence DAX measures.
"""
import sqlite3
import pandas as pd

conn = sqlite3.connect("user_lifecycle_churn.db")

# --- Fact table: raw events ---
# --- Fact table: raw events ---
fact_events = pd.read_sql("SELECT * FROM stg_events", conn)
fact_events["event_ts"] = pd.to_datetime(fact_events["event_ts"])
fact_events["event_date"] = fact_events["event_ts"].dt.date  # NEW: date-only column for the relationship
fact_events.to_csv("data/powerbi_fact_events.csv", index=False)
print(f"fact_events: {len(fact_events)} rows")

# --- User dimension: dim_users + RFM + churn score ---
dim_users = pd.read_sql("SELECT * FROM dim_users", conn)
rfm = pd.read_sql("SELECT * FROM vw_rfm", conn)
churn = pd.read_csv("data/churn_scores.csv")[["user_id", "churn_score", "risk_band", "churned"]]
dim_users = dim_users.merge(rfm, on="user_id", how="left")
dim_users = dim_users.merge(churn, on="user_id", how="left")
dim_users["risk_band"] = dim_users["risk_band"].fillna("Not Scored (Recent)")

dim_users.to_csv("data/powerbi_dim_users.csv", index=False)
print(f"dim_users: {len(dim_users)} rows")

# --- Date dimension ---
date_range = pd.date_range(fact_events["event_ts"].min(), fact_events["event_ts"].max())
dim_date = pd.DataFrame({"date_key": date_range.date})
dim_date["year"] = date_range.year
dim_date["month"] = date_range.month
dim_date["year_month"] = date_range.strftime("%Y-%m")
dim_date["day_name"] = date_range.day_name()

dim_date.to_csv("data/powerbi_dim_date.csv", index=False)
print(f"dim_date: {len(dim_date)} rows")

# --- Cohort retention (for the heatmap visual) ---
cohort = pd.read_sql("SELECT * FROM vw_cohort_retention", conn)
cohort.to_csv("data/powerbi_cohort_retention.csv", index=False)
print(f"cohort_retention: {len(cohort)} rows")

conn.close()
print("\nDone. Files in data/ folder, ready for Power BI import.")