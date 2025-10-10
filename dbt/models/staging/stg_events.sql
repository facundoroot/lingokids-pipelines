{{ config(materialized='view') }}

-- Temporal dependency: this model depends on the bronze_events Dagster asset
-- depends_on: {{ source('bronze', 'bronze_events') }}

WITH src AS (
    -- Read from bronze layer (merged files from Dagster)
    SELECT * FROM read_json_auto('data/bronze/bronze_events.json')
)
SELECT
    event_id,
    user_id,
    occurred_at::TIMESTAMP AS occurred_at,

    -- Flatten nested data
    data->>'activity_id' AS activity_id,
    data->>'source' AS source,
    TRY_CAST(data->>'duration' AS DOUBLE) AS duration_seconds,
    (data->>'completed')::BOOLEAN AS completed_flag,
    data->>'collection_id' AS collection_id,
    TRY_CAST(data->>'loading_time' AS DOUBLE) AS loading_time_seconds,

    -- Flatten nested context
    context->'device'->>'brand' AS device_name,
    context->'os'->>'name' AS os_name,
    context->'os'->>'version' AS os_version,
    context->'app'->>'version' AS app_version,

    name AS event_name
FROM src
WHERE name = 'activity_exit'

