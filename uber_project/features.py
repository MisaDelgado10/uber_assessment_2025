import pandas as pd
import numpy as np

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds engineered features at the delivery level for Uber Eats data.

    Parameters:
        df (pd.DataFrame): Cleaned delivery-level data.

    Returns:
        pd.DataFrame: DataFrame with new features added.
    """

    df = df.copy()

    # --- Temporal features ---
    df["eater_request_timestamp_local"] = pd.to_datetime(df["eater_request_timestamp_local"])
    df["restaurant_offered_timestamp_local"] = pd.to_datetime(df["restaurant_offered_timestamp_local"])
    df["order_final_state_timestamp_local"] = pd.to_datetime(df["order_final_state_timestamp_local"])
    df["restaurant_offered_timestamp_local"] = pd.to_datetime(df["restaurant_offered_timestamp_local"])

    df["order_hour"] = df["eater_request_timestamp_local"].dt.hour
    df["order_dayofweek"] = df["eater_request_timestamp_local"].dt.dayofweek
    df["order_weekend"] = df["order_dayofweek"].isin([5, 6]).astype(int)

    df["order_time_of_day"] = pd.cut(
        df["order_hour"],
        bins=[-1, 5, 11, 17, 21, 24],
        labels=["night", "morning", "afternoon", "evening", "night"],
        ordered=False
    )

    df["delivery_duration_seconds"] = (
        df["order_final_state_timestamp_local"] - df["restaurant_offered_timestamp_local"]
    ).dt.total_seconds()

    df["preparation_time_minutes"] = (
        df["restaurant_offered_timestamp_local"] - df["eater_request_timestamp_local"]
    ).dt.total_seconds() / 60

    df["dispatch_delay_minutes"] = (
        df["restaurant_offered_timestamp_local"] - df["restaurant_offered_timestamp_local"]
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

    flow_map = {"Motorbike": 1, "Bicycle": 2, "Foot": 3}
    df["courier_flow_complexity_score"] = df["courier_flow"].map(flow_map).fillna(4)

    # --- Derived features ---
    df["is_peak_hour"] = df["order_hour"].between(12, 14) | df["order_hour"].between(18, 21)
    df["is_peak_hour"] = df["is_peak_hour"].astype(int)

    df["estimated_speed_kmh"] = (df["dropoff_distance"] / (df["ATD"] / 60)).replace([np.inf, -np.inf], np.nan)

    df["is_short_trip_long_time"] = (
        (df["dropoff_distance"] < 1) & (df["ATD"] > 40)
    ).astype(int)

    df["relative_prep_time"] = df["preparation_time_minutes"] / (df["ATD"] + 0.01)

    return df
