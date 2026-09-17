-- DBT Model: Transform Green Taxi Trip Data
-- Adds calculated columns for CO2, speed, and time-based features

{{ config(
    materialized='table',
    unique_id='stg_green_taxi_transformed'
) }}

SELECT 
    gtc.VendorID,
    gtc.lpep_pickup_datetime,
    gtc.lpep_dropoff_datetime,
    gtc.passenger_count,
    gtc.trip_distance,
    gtc.RatecodeID,
    gtc.store_and_fwd_flag,
    gtc.PULocationID,
    gtc.DOLocationID,
    gtc.payment_type,
    gtc.fare_amount,
    gtc.extra,
    gtc.mta_tax,
    gtc.tip_amount,
    gtc.tolls_amount,
    gtc.total_amount,
    gtc.congestion_surcharge,
    gtc.ehail_fee,
    gtc.pickup_time,
    gtc.duration_seconds,
    -- Calculate CO2 emissions from trip distance and emissions lookup
    ROUND((gtc.trip_distance * ve.co2_grams_per_mile / 1000)::NUMERIC, 2) as trip_co2_kgs,
    -- Calculate average speed in miles per hour
    ROUND((gtc.trip_distance / (gtc.duration_seconds / 3600.0))::NUMERIC, 2) as avg_mph,
    -- Extract time-based features
    EXTRACT(HOUR FROM gtc.pickup_time) as hour_of_day,
    DAYNAME(gtc.pickup_time) as day_of_week,
    EXTRACT(WEEK FROM gtc.pickup_time) as week_of_year,
    EXTRACT(MONTH FROM gtc.pickup_time) as month_of_year

FROM {{ source('raw', 'green_taxi_cleaned') }} gtc
JOIN {{ source('raw', 'vehicle_emissions') }} ve 
    ON ve.vehicle_type = 'green_taxi'
