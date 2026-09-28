-- 02_dim_users.sql
-- Builds a one-row-per-user dimension with first/last activity dates.
-- Foundation for cohort assignment and retention analysis.

DROP TABLE IF EXISTS dim_users;

CREATE TABLE dim_users AS
SELECT
    user_id,
    MIN(DATE(event_ts))              AS first_event_date,
    MAX(DATE(event_ts))              AS last_event_date,
    COUNT(DISTINCT invoice_no)       AS lifetime_orders,
    SUM(event_value)                 AS lifetime_value
FROM stg_events
GROUP BY user_id;

SELECT COUNT(*) AS total_users FROM dim_users;
SELECT * FROM dim_users LIMIT 10;