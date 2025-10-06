{{ config(materialized='view') }}

SELECT
    a.price_tier,
    COUNT(e.event_id) AS session_count,
    ROUND(AVG(e.duration_seconds), 2) AS avg_duration_seconds
FROM {{ ref('activity_events') }} AS e
JOIN {{ ref('activities') }} AS a
  ON e.activity_id = a.activity_id
WHERE e.event_type = 'activity_exit'
GROUP BY a.price_tier
ORDER BY a.price_tier
