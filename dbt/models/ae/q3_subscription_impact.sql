{{ config(materialized='view') }}

WITH subs AS (
    SELECT
        user_id,
        platform,
        CAST(subscription_date AS DATE) AS subscription_date
    FROM {{ ref('subscriptions') }}
    WHERE DATE_TRUNC('month', subscription_date) = DATE '2025-01-01'
),
events AS (
    SELECT
        user_id,
        created_at::DATE AS event_date,
        COUNTIF(completed) AS completed_activities
    FROM {{ ref('activity_events') }}
    WHERE event_type = 'activity_exit'
    GROUP BY 1, 2
),
joined AS (
    SELECT
        s.platform,
        s.user_id,
        e.event_date,
        e.completed_activities,
        DATE_DIFF('day', e.event_date, s.subscription_date) AS diff_days
    FROM subs s
    LEFT JOIN events e USING (user_id)
)
SELECT
    platform,
    ROUND(AVG(CASE WHEN diff_days BETWEEN -7 AND -1 THEN completed_activities END), 2) AS avg_completed_before,
    ROUND(AVG(CASE WHEN diff_days BETWEEN 1 AND 7 THEN completed_activities END), 2) AS avg_completed_after
FROM joined
GROUP BY platform
ORDER BY platform
