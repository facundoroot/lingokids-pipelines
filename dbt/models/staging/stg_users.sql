{{ config(materialized='view') }}

-- Temporal dependency: this model depends on the bronze_users Dagster asset
-- depends_on: {{ source('bronze', 'bronze_users') }}

WITH src AS (
    -- Read from bronze layer (merged files from Dagster)
    SELECT * FROM read_json_auto('data/bronze/bronze_users.json')
)
SELECT
    user_id,
    country_code,
    registration_at::TIMESTAMP AS registration_at,
    trial_start_at::TIMESTAMP AS trial_start_at,
    trial_end_at::TIMESTAMP AS trial_end_at,
    subscription_start_at::TIMESTAMP AS subscription_start_at,
    subscription_expire_at::TIMESTAMP AS subscription_expire_at
FROM src

