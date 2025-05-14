WITH delivery_base AS (
  SELECT
    edmjm.jobuuid,
    edmjm.cityid,
    edmjm.datestr,
    edmjm.pickupdistance / 1000.0 AS pickup_distance_km,
    edmjm.traveldistance / 1000.0 AS travel_distance_km,
    edmjm.estimated_delivery_time,
    edmjm.delivery_status,
    edmjm.isfinalplan
  FROM delivery_matching.eats_dispatch_metrics_job_message edmjm
  WHERE edmjm.isfinalplan = true
    AND edmjm.delivery_status = 'completed'
),

trip_details AS (
  SELECT
    lt.delivery_trip_uuid,
    lt.workflow_uuid,
    lt.driver_uuid,
    lt.courier_flow,
    lt.restaurant_offered_timestamp_utc,
    lt.order_final_state_timestamp_local,
    lt.eater_request_timestamp_local,
    lt.geo_archetype,
    lt.merchant_surface,
    lt.total_distance_travelled
  FROM tmp.lea_trips_scope_atd_consolidation_v2 lt
),

city_info AS (
  SELECT
    dc.city_id,
    dc.city_name,
    dc.country_name,
    dc.mega_region,
    dc.currency_code,
    dc.population_size AS city_population,
    dc.average_income,
    csr.region,
    csr.territory,
    csr.population_size AS region_population,
    csr.market_demand
  FROM dwh.dim_city dc
  LEFT JOIN kirby_external_data.cities_strategy_region csr
    ON dc.city_id = csr.city_id
)

-- Unión final
SELECT 
  ci.territory, 
  ci.country_name, 
  td.workflow_uuid,
  td.driver_uuid,
  td.delivery_trip_uuid,
  td.courier_flow,
  td.restaurant_offered_timestamp_utc,
  td.order_final_state_timestamp_local,
  td.eater_request_timestamp_local,
  td.geo_archetype, 
  td.merchant_surface,
  db.pickup_distance_km,
  db.travel_distance_km as dropoff_distance_km,
  EXTRACT(EPOCH FROM (td.order_final_state_timestamp_local - td.eater_request_timestamp_local)) / 60 AS atd
FROM delivery_base db
LEFT JOIN trip_details td
  ON db.jobuuid = td.delivery_trip_uuid
LEFT JOIN city_info ci
  ON db.cityid = ci.city_id;
