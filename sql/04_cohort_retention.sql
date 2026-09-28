-- 04_cohort_retention.sql
-- Assigns each user to an acquisition cohort (month of first purchase)
-- and builds a monthly retention matrix (cohort heatmap data).

DROP VIEW IF EXISTS vw_user_cohort;

CREATE VIEW vw_user_cohort AS
SELECT
    user_id,
    strftime('%Y-%m', first_event_date) AS cohort_month
FROM dim_users;

DROP VIEW IF EXISTS vw_cohort_retention;

CREATE VIEW vw_cohort_retention AS
WITH cohort_size AS (
    SELECT cohort_month, COUNT(*) AS cohort_users
    FROM vw_user_cohort
    GROUP BY cohort_month
),
user_activity_months AS (
    -- distinct (user, month) pairs where the user had at least one purchase
    SELECT DISTINCT
        e.user_id,
        strftime('%Y-%m', e.event_ts) AS activity_month
    FROM stg_events e
),
joined AS (
    SELECT
        c.cohort_month,
        a.activity_month,
        -- month_index = how many months after acquisition this activity happened
        (CAST(strftime('%Y', a.activity_month || '-01') AS INTEGER) * 12
            + CAST(strftime('%m', a.activity_month || '-01') AS INTEGER))
        -
        (CAST(strftime('%Y', c.cohort_month || '-01') AS INTEGER) * 12
            + CAST(strftime('%m', c.cohort_month || '-01') AS INTEGER)) AS month_index,
        a.user_id
    FROM vw_user_cohort c
    JOIN user_activity_months a ON a.user_id = c.user_id
)
SELECT
    j.cohort_month,
    j.month_index,
    COUNT(DISTINCT j.user_id) AS active_users,
    s.cohort_users,
    ROUND(100.0 * COUNT(DISTINCT j.user_id) / s.cohort_users, 1) AS retention_pct
FROM joined j
JOIN cohort_size s ON s.cohort_month = j.cohort_month
GROUP BY j.cohort_month, j.month_index
ORDER BY j.cohort_month, j.month_index;

SELECT * FROM vw_cohort_retention LIMIT 20;