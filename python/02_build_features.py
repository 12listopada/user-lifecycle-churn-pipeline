"""
02_build_features.py
Builds behavioral features per user using ONLY the observation window,
and a churn label based on activity in the outcome window (3 months
after the cutoff). No leakage between the two.
"""
import sqlite3
import pandas as pd

DB_PATH = "user_lifecycle_churn.db"
OUTCOME_WINDOW_DAYS = 92  # ~3 months

conn = sqlite3.connect(DB_PATH)

events = pd.read_sql(
    "SELECT user_id, invoice_no, event_ts, event_value FROM stg_events", conn
)
events["event_ts"] = pd.to_datetime(events["event_ts"])

max_date = events["event_ts"].max()
cutoff_date = max_date - pd.Timedelta(days=OUTCOME_WINDOW_DAYS)

print(f"Data range: {events['event_ts'].min().date()} -> {max_date.date()}")
print(f"Cutoff (observation window ends): {cutoff_date.date()}")

obs = events[events["event_ts"] <= cutoff_date].copy()
outcome = events[events["event_ts"] > cutoff_date].copy()

active_before_cutoff = obs["user_id"].unique()
churned_ids = set(active_before_cutoff) - set(outcome["user_id"].unique())

print(f"Users active before cutoff: {len(active_before_cutoff)}")
print(f"Churned (no activity after cutoff): {len(churned_ids)} "
      f"({100*len(churned_ids)/len(active_before_cutoff):.1f}%)")

# --- Feature engineering (observation window only) ---
grp = obs.groupby("user_id")

feat = pd.DataFrame(index=pd.Index(active_before_cutoff, name="user_id"))
first_event = grp["event_ts"].min()
last_event = grp["event_ts"].max()

feat["tenure_days"] = (last_event - first_event).dt.days
feat["recency_days"] = (cutoff_date - last_event).dt.days
feat["frequency"] = grp["invoice_no"].nunique()
feat["monetary_total"] = grp["event_value"].sum()
feat["monetary_avg"] = grp["event_value"].mean()
feat = feat.reset_index()

# Purchase gaps (already computed in SQL with LAG), restricted to the
# observation window so we don't leak post-cutoff orders into features
gaps = pd.read_sql("SELECT * FROM vw_user_purchase_gaps", conn)
gaps["order_date"] = pd.to_datetime(gaps["order_date"])
gaps = gaps[gaps["order_date"] <= cutoff_date]

gap_stats = gaps.groupby("user_id")["days_since_prev_order"].agg(["mean", "max"])
gap_stats.columns = ["avg_days_between_orders", "max_days_between_orders"]
gap_stats = gap_stats.reset_index()

feat = feat.merge(gap_stats, on="user_id", how="left")
feat["avg_days_between_orders"] = feat["avg_days_between_orders"].fillna(feat["tenure_days"])
feat["max_days_between_orders"] = feat["max_days_between_orders"].fillna(feat["tenure_days"])

feat["churned"] = feat["user_id"].isin(churned_ids).astype(int)

conn.close()

feat.to_csv("data/processed_features.csv", index=False)
print(f"\nSaved: data/processed_features.csv ({len(feat)} users)")
print(feat.head())