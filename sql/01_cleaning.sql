-- 01_cleaning.sql
-- Cleans the raw Online Retail II data and builds a staging table of
-- user events (staging layer for downstream cohort/RFM/churn analysis)

DROP TABLE IF EXISTS stg_events;

CREATE TABLE stg_events AS
SELECT
    Invoice                        AS invoice_no,
    StockCode                      AS item_code,
    Description                    AS item_name,
    Quantity                       AS quantity,
    InvoiceDate                    AS event_ts,
    Price                          AS unit_price,
    CAST("Customer ID" AS INTEGER) AS user_id,
    Country                        AS country,
    ROUND(Quantity * Price, 2)     AS event_value
FROM online_retail_II
WHERE Invoice NOT LIKE 'C%'      -- remove cancellations
  AND "Customer ID" IS NOT NULL  -- remove events with no attributed user
  AND Quantity > 0               -- remove invalid/negative quantities
  AND Price > 0;                 -- remove invalid/zero prices

SELECT COUNT(*) AS rows_after_cleaning FROM stg_events;
SELECT COUNT(DISTINCT user_id) AS unique_users FROM