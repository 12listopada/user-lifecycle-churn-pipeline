"""
01_load_data.py
Sanity check: connect to the SQLite database and load the RFM view
into pandas to confirm everything is wired up correctly.
"""
import sqlite3
import pandas as pd

DB_PATH = "user_lifecycle_churn.db"

conn = sqlite3.connect(DB_PATH)

rfm = pd.read_sql("SELECT * FROM vw_rfm", conn)

print(f"Shape: {rfm.shape}")
print(rfm.head())
print(rfm["rfm_segment"].value_counts())

conn.close()