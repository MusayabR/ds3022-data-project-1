-- DBT Model: Transform Yellow Taxi Trip Data
-- Adds calculated columns for CO2, speed, and time-based features

{{ config(
    materialized='table',
    unique_id='stg_yellow_taxi_transformed'
) }}

SELECT 
    ytc.VendorID,
    ytc.tpep_pickup_datetime,
    ytc.tpep_dropoff_datetime,
    ytc.passenger_count,
    ytc.trip_distance,
    ytc.RatecodeID,
    ytc.store_and_fwd_flag,
    ytc.PULocationID,
    ytc.DOLocationID,
    ytc.payment_type,
    ytc.fare_amount,
    ytc.extra,
    ytc.mta_tax,
    ytc.tip_amount,
    ytc.tolls_amount,
    ytc.total_amount,
    ytc.congestion_surcharge,
    ytc.airport_fee,
    ytc.pickup_time,
    ytc.duration_seconds,
    -- Calculate CO2 emissions from trip distance and emissions lookup
    ROUND((ytc.trip_distance * ve.co2_grams_per_mile / 1000)::NUMERIC, 2) as trip_co2_kgs,
    -- Calculate average speed in miles per hour
    ROUND((ytc.trip_distance / (ytc.duration_seconds / 3600.0))::NUMERIC, 2) as avg_mph,
    -- Extract time-based features
    EXTRACT(HOUR FROM ytc.pickup_time) as hour_of_day,
    DAYNAME(ytc.pickup_time) as day_of_week,
    EXTRACT(WEEK FROM ytc.pickup_time) as week_of_year,
    EXTRACT(MONTH FROM ytc.pickup_time) as month_of_year

FROM {{ source('raw', 'yellow_taxi_cleaned') }} ytc
JOIN {{ source('raw', 'vehicle_emissions') }} ve 
    ON ve.vehicle_type = 'yellow_taxi'
