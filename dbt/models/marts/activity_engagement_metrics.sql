{{
  config(
    materialized='incremental',
    unique_key=['date', 'country_code', 'os_name', 'app_version', 'subscription_status', 'activity_type'],
    on_schema_change='sync_all_columns',
    incremental_strategy='delete+insert'
  )
}}

-- ===============================================================
-- Purpose:
--   Aggregates event-level data into daily engagement KPIs:
--   - number of activities played
--   - total time spent
--   - completion rate
--   Broken down by country, OS, app version, subscription
--   status, and activity type.
--
-- Incremental logic:
--   Rebuild only recent days (last 3) to capture late-arriving
--   events, leaving older dates untouched.
-- ===============================================================

WITH base AS (
    SELECT
        date,
        country_code,
        os_name,
        app_version,
        subscription_status,
        activity_type,
        COUNT(event_id) AS activities_played,
        SUM(duration_seconds) AS total_time_spent,
        ROUND(AVG(CASE WHEN completed_flag THEN 1 ELSE 0 END), 3) AS completion_rate
    FROM {{ ref('intermediate_activity_events_enriched') }}
    GROUP BY
        1,2,3,4,5,6
)

SELECT *
FROM base

-- ===============================================================
-- Incremental filter:
--   When running incrementally, refresh only the last 3 days.
--   This allows you to capture late-arriving events without
--   rewriting the entire table.
-- ===============================================================
{% if is_incremental() %}
  WHERE date >= (SELECT max(date) - INTERVAL '3 day' FROM {{ this }})
{% endif %}

