{{ config(
    materialized='table',
    unique_key='id'
) }}

SELECT
    city,
    temperature,
    weather_descriptions,
    wind_speed,
    weather_time_local
FROM
    {{ ref('staging_weather_data') }}