import pandas as pd
import numpy as np
from datetime import timedelta

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds engineered features at the delivery level for Uber Eats data,
    including weather features (rain and temperature) aggregated por mes y territorio.

    Parameters:
        df (pd.DataFrame): Cleaned delivery-level data.

    Returns:
        pd.DataFrame: DataFrame with new features added.
    """

    df = df.copy()

    # --- Leer datasets de clima ---
    # Reemplaza estos paths con los correctos
    rain = pd.read_csv('../data/external/weather/rain.csv')          # columnas: territory, year_month, rain
    temp_mean = pd.read_csv('../data/external/weather/temp_mean.csv') # columnas: territory, year_month, temp

    # --- Convert timestamps ---
    df["eater_request_timestamp_local"] = pd.to_datetime(df["eater_request_timestamp_local"])
    df["restaurant_offered_timestamp_local"] = pd.to_datetime(df["restaurant_offered_timestamp_local"])
    df["order_final_state_timestamp_local"] = pd.to_datetime(df["order_final_state_timestamp_local"])

    # --- Temporal features ---
    df["order_hour"] = df["eater_request_timestamp_local"].dt.hour
    df["order_dayofweek"] = df["eater_request_timestamp_local"].dt.dayofweek
    df["order_weekend"] = df["order_dayofweek"].isin([5, 6]).astype(int)

    df["order_time_of_day"] = pd.cut(
        df["order_hour"],
        bins=[-1, 5, 11, 17, 21, 24],
        labels=["night", "morning", "afternoon", "evening", "night"],
        ordered=False
    )

    df["order_time_of_day_encoded"] = df["order_time_of_day"].astype("category").cat.codes

    df["delivery_duration_minutes"] = (
        df["order_final_state_timestamp_local"] - df["restaurant_offered_timestamp_local"]
    ).dt.total_seconds() / 60

    df["preparation_time_minutes"] = (
        df["restaurant_offered_timestamp_local"] - df["eater_request_timestamp_local"]
    ).dt.total_seconds() / 60

    df["delivery_hour"] = df["order_final_state_timestamp_local"].dt.hour

    # --- Distance-based features ---
    df["pickup_distance"] = pd.to_numeric(df["pickup_distance"], errors="coerce")
    df["dropoff_distance"] = pd.to_numeric(df["dropoff_distance"], errors="coerce")

    df["total_distance_km"] = df["pickup_distance"] + df["dropoff_distance"]
    df["distance_ratio"] = df["pickup_distance"] / (df["dropoff_distance"] + 0.01)
    df["long_delivery_flag"] = (df["dropoff_distance"] > 10).astype(int)

    # --- Operational / logistic features ---
    df["courier_flow_encoded"] = df["courier_flow"].astype("category").cat.codes
    df["geo_archetype_encoded"] = df["geo_archetype"].astype("category").cat.codes
    df["merchant_surface_encoded"] = df["merchant_surface"].astype("category").cat.codes
    df["territory_encoded"] = df["territory"].astype("category").cat.codes

    # Courier flow complexity (lower is faster)
    courier_complexity_map = {
        "Motorbike": 1,
        "UberEats": 1,
        "Logistics": 2,
        "UberX": 2,
        "Fleet": 2,
        "SUV": 3,
        "Onboarder": 3
    }
    df["courier_flow_complexity_score"] = df["courier_flow"].map(courier_complexity_map).fillna(4)

    # --- Derived features ---
    df["is_peak_hour"] = df["order_hour"].between(12, 14) | df["order_hour"].between(18, 21)
    df["is_peak_hour"] = df["is_peak_hour"].astype(int)

    df["estimated_speed_kmh"] = (
        df["dropoff_distance"] / (df["ATD"] / 60)
    ).replace([np.inf, -np.inf], np.nan)

    df["is_short_trip_long_time"] = (
        (df["dropoff_distance"] < 1) & (df["ATD"] > 40)
    ).astype(int)

    df["relative_prep_time"] = df["preparation_time_minutes"] / (df["ATD"] + 0.01)

    # Traffic-related signals
    df["is_high_traffic_suspected"] = (
        (df["total_distance_km"] < 3) & (df["ATD"] > 45)
    ).astype(int)

    df["speed_below_threshold"] = (
        df["estimated_speed_kmh"] < 10
    ).astype(int)

    # --- Extraer año y mes para join con datos de clima ---
    df['year_month'] = df['restaurant_offered_timestamp_local'].dt.to_period('M').astype(str)

    # --- Merge con datos de lluvia ---
    df = df.merge(rain, how='left', on=['territory', 'year_month'])

    # --- Merge con datos de temperatura ---
    df = df.merge(temp_mean, how='left', on=['territory', 'year_month'])

    # --- Opcional: eliminar columna auxiliar ---
    df.drop(columns=['year_month'], inplace=True)

    return df
