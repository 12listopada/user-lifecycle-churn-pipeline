# User Lifecycle & Churn Risk Pipeline

**Event-based cohort & monetization analytics — Gaming/Fintech-style churn prediction, built end-to-end on real e-commerce transaction data.**

An end-to-end analytics pipeline that takes raw transaction-level events, models customer lifecycle behavior, predicts churn risk with machine learning, and surfaces the results in an executive Power BI dashboard.

**Stack:** SQL (SQLite) → Python (pandas, scikit-learn) → Power BI

---

## Business problem

Which customers are at risk of churning, how much revenue is at stake, and who should the retention team prioritize first?

This project answers that with three layers of analysis:
1. **Cohort retention** — how customer engagement decays over time, by acquisition month
2. **RFM segmentation** — rule-based customer segments from Recency, Frequency, Monetary behavior
3. **ML churn prediction** — a Random Forest classifier scoring every customer's probability of churning, validated against a leakage-free observation/outcome time split

---

## Dataset

[Online Retail II](https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci) (UCI/Kaggle) — ~1.07M transaction line items from a UK-based online retailer, Dec 2009–Dec 2011. Chosen for its realistic messiness (cancellations, missing customer IDs, negative quantities) — the kind of cleanup real analyst work involves.

After cleaning: **805,549 transactions**, **5,878 unique customers**.

---

## Pipeline

### 1. SQL — data modeling & feature prep (SQLite, `sql/`)

| File | Purpose |
|---|---|
| `01_cleaning.sql` | Staging table (`stg_events`): removes cancellations, null customer IDs, non-positive quantity/price |
| `02_dim_users.sql` | Customer dimension: first/last order date, lifetime orders, lifetime value |
| `03_user_purchase_gaps.sql` | Window functions (`LAG`, `ROW_NUMBER`) to compute days between consecutive orders per customer |
| `04_cohort_retention.sql` | CTE-based monthly cohort retention matrix |
| `05_rfm_segmentation.sql` | RFM scoring (`NTILE(5)`) and rule-based segment labels (Champions, Loyal Users, At Risk, Hibernating/Churned, etc.) |

### 2. Python — feature engineering & modeling (`python/`)

| File | Purpose |
|---|---|
| `01_load_data.py` | Sanity-check: loads SQL views into pandas, confirms row counts match SQL |
| `02_build_features.py` | Builds a leakage-free observation-window / outcome-window split (92-day outcome window) and per-customer behavioral features (tenure, recency, frequency, monetary, purchase gap stats) |
| `03_train_model.py` | Trains a Random Forest churn classifier (class-balanced, 75/25 stratified split), scores all customers, exports risk bands (Low/Medium/High) |
| `04_export_powerbi.py` | Exports the star-schema tables (fact + dimensions) as CSVs for Power BI |

**Key modeling decision:** churn is defined using a strict time split — features are computed only from the *observation window*, and the label (churned / not) comes from whether the customer had any activity in the following *outcome window*. This prevents the model from "seeing the future" during training.

**Model result:** Random Forest, ROC-AUC **0.80**, ~74% accuracy, 76%/78% precision/recall on the churned class.

### 3. Power BI — executive dashboard (`data/user_lifecycle_churn.pbix`)

**Page 1 — Executive Overview**
- KPI cards: Total Revenue, Total Customers, Churn Rate %, ARPU, High Risk Customers
- Cohort retention heatmap (% active users by month since acquisition)

**Page 2 — Churn Risk & Segmentation**
- Churn risk distribution (Low/Medium/High, from the ML model)
- RFM segment distribution (rule-based)
- Priority Retention List: high-risk customers ranked by a combined Priority Score (churn probability × lifetime value), so retention effort targets high-value at-risk customers first, not just statistically risky ones

---

## Key findings

- Retention drops sharply after month 0–1 across every cohort. Early, larger cohorts (Dec 2009–early 2010) stabilize in a 20–40% range for many months; smaller, later cohorts show noisier, generally lower retention (often single digits to ~15%) — though this is partly a sample-size effect, since those cohorts have fewer months of observed history
- ~31% of scored customers fall into the High Risk band
- The largest RFM segment is Hibernating/Churned (~1,750 customers) — most lapsed customers don't come back
- The highest-priority retention targets are high-value wholesale-style customers ($30K–$170K lifetime value) showing high churn probability (0.71–0.83) — a small group with outsized revenue impact

---

## How to reproduce

1. Import `data/online_retail_II.csv` into SQLite (`user_lifecycle_churn.db`) via DB Browser for SQLite
2. Run the SQL scripts in `sql/` in order (01 → 05)
3. Run the Python scripts in `python/` in order (01 → 04) inside the project's virtual environment
4. Open `data/user_lifecycle_churn.pbix` in Power BI Desktop, refresh data sources to point at the exported CSVs in `data/`

---

## Author

**Oliwia Tomiczek** — Data Analyst
[GitHub](https://github.com/12listopada)