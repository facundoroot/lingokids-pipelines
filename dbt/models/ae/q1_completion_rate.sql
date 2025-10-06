{{ config(materialized='view') }}

SELECT
    a.theme,
    ROUND(100.0 * SUM(CASE WHEN e.completed THEN 1 ELSE 0 END) / COUNT(e.event_id), 2) AS completion_rate_pct
FROM {{ ref('activity_events') }} AS e
JOIN {{ ref('activities') }} AS a
  ON e.activity_id = a.activity_id
WHERE e.event_type = 'activity_exit'
GROUP BY a.theme
ORDER BY completion_rate_pct DESC
