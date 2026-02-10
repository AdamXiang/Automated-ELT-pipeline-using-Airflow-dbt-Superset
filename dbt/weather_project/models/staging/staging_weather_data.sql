{{ config(
    materialized='table',
    unique_key='id'
)}}

WITH source AS (
    SELECT *
    FROM {{ source('dev', 'raw_weather_date') }}
),
de_dup AS (
    SELECT
        *,
        row_number() OVER(PARTITION BY time ORDER BY inserted_at) AS rn
    FROM
        source
)
SELECT
    id, city, temperature, weather_descriptions,
    wind_speed,
    time AS weather_time_local,
    (inserted_at + (utc_offset || "hours")::interval) AS inserted_at_local
FROM
    de_dup
WHERE
    rn = 1