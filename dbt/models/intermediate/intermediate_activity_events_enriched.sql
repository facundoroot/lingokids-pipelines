{{
  config(
    materialized='incremental',
    unique_key='event_id',
    on_schema_change='sync_all_columns',
    incremental_strategy='delete+insert'
  )
}}

-- ===============================================================
-- Purpose:
--   This model enriches the raw event data by joining user and
--   activity metadata and computing the user's subscription
--   status at the time of each event.
--
-- Incremental logic:
--   On first run → full historical load.
--   On subsequent runs → only load events newer than the
--   latest event currently in this table.
-- ===============================================================

WITH events AS (
    SELECT * FROM {{ ref('stg_events') }}
),

users AS (
    SELECT * FROM {{ ref('stg_users') }}
),

activities AS (
    SELECT * FROM {{ ref('stg_activities') }}
),

joined AS (
    SELECT
        e.event_id,
        e.user_id,
        e.activity_id,
        e.occurred_at,
        e.duration_seconds,
        e.completed_flag,
        e.os_name,
        e.app_version,
        a.activity_name,
        a.activity_type,
        a.activity_subtype,
        u.country_code,

        CASE
            WHEN e.occurred_at BETWEEN u.subscription_start_at AND u.subscription_expire_at THEN 'subscribed'
            WHEN e.occurred_at BETWEEN u.trial_start_at AND u.trial_end_at THEN 'trial'
            WHEN e.occurred_at < u.trial_start_at THEN 'free'
            WHEN u.trial_start_at IS NULL THEN 'free'  -- Never had a trial
            ELSE 'lapsed'
        END AS subscription_status

    FROM events e
    LEFT JOIN users u USING (user_id)
    LEFT JOIN activities a USING (activity_id)
)

SELECT
    *,
    DATE(occurred_at) AS date
FROM joined

-- ===============================================================
-- Incremental filter: process only new events that are later
-- than the last recorded event in this table.
-- ===============================================================
{% if is_incremental() %}
  WHERE occurred_at > (SELECT max(occurred_at) FROM {{ this }})
{% endif %}

