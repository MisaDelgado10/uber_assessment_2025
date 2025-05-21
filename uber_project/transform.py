import pandas as pd


def transform_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Do transformation on main features

    Parameters:
        df (pd.DataFrame): Cleaned delivery-level data.

    Returns:
        pd.DataFrame: DataFrame with features transformed.
    """

    df = df.copy()

    # --- Drop missing and 0 values in essential columns ---
    df = df[(df["ATD"] > 0) & (df["ATD"].notnull())]

    # Winsorizing for outliers in ATD and distances (1% y 99%)
    for col in ["ATD", "pickup_distance", "dropoff_distance", "total_distance_km"]:
        if col in df.columns:
            lower = df[col].quantile(0.01)
            upper = df[col].quantile(0.99)
            df[col] = df[col].clip(lower, upper)

    df = df.drop_duplicates()

    return df
