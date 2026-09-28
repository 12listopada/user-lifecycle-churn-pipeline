-- 05_rfm_segmentation.sql
-- RFM segmentation: Recency, Frequency, Monetary scored 1-5 via NTILE,
-- combined into a business-readable segment name.

DROP VIEW IF EXISTS vw_rfm;

CREATE VIEW vw_rfm AS
WITH snapshot AS (
    -- "today" = one day after the last event in the dataset
    SELECT DATE(MAX(event_ts), '+1 day') AS snapshot_date FROM stg_events
),
base AS (
    SELECT
        user_id,
        CAST(JULIANDAY((SELECT snapshot_date FROM snapshot)) - JULIANDAY(MAX(DATE(event_ts))) AS INTEGER) AS recency_days,
        COUNT(DISTINCT invoice_no) AS frequency,
        SUM(event_value) AS monetary
    FROM stg_events
    GROUP BY user_id
),
scored AS (
    SELECT
        user_id,
        recency_days,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,  -- lower recency = better
        NTILE(5) OVER (ORDER BY frequency ASC)     AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC)      AS m_score
    FROM base
)
SELECT
    user_id,
    recency_days,
    frequency,
    monetary,
    r_score, f_score, m_score,
    (r_score + f_score + m_score) AS rfm_total_score,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 4 AND f_score >= 3                  THEN 'Loyal Users'
        WHEN r_score >= 4 AND f_score <= 2                  THEN 'New / Promising'
        WHEN r_score = 3                                     THEN 'Needs Attention'
        WHEN r_score = 2 AND (f_score >= 3 OR m_score >= 3) THEN 'At Risk (High Value)'
        WHEN r_score <= 2                                     THEN 'Hibernating / Churned'
        ELSE 'Other'
    END AS rfm_segment
FROM scored;

SELECT rfm_segment, COUNT(*) AS users, ROUND(AVG(monetary), 2) AS avg_monetary
FROM vw_rfm
GROUP BY rfm_segment
ORDER BY users DESC;