{{ config(materialized='view') }}

-- Temporal dependency: this model depends on the bronze_activities Dagster asset
-- depends_on: {{ source('bronze', 'bronze_activities') }}

WITH src AS (
    -- Read from bronze layer (merged files from Dagster)
    SELECT * FROM read_json_auto('data/bronze/bronze_activities.json')
)
SELECT
    activity_id,
    name AS activity_name,
    type AS activity_type,
    subtype AS activity_subtype
FROM src

