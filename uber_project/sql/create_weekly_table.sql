CREATE TABLE IF NOT EXISTS AA_tables.weekly_delivery_metrics (
  week_start_date DATE,
  week_year TEXT, 
  territory TEXT,
  country_name TEXT,
  workflow_uuid TEXT,
  driver_uuid TEXT,
  delivery_trip_uuid TEXT,
  courier_flow TEXT,
  restaurant_offered_timestamp_utc TIMESTAMP,
  order_final_state_timestamp_local TIMESTAMP,
  eater_request_timestamp_local TIMESTAMP,
  geo_archetype TEXT,
  merchant_surface TEXT,
  pickup_distance_km FLOAT,
  dropoff_distance_km FLOAT,
  atd FLOAT
);
