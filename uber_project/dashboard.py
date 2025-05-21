from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """
    Load delivery data from a parquet file.

    Args:
        path (str): File path to the parquet data.

    Returns:
        pd.DataFrame: Loaded delivery data.
    """
    df = pd.read_parquet(path)

    return df


def filter_data_by_date(df: pd.DataFrame, date_range: Tuple[str, str]) -> pd.DataFrame:
    """
    Filter dataframe based on a date range applied to the order request timestamp.

    Args:
        df (pd.DataFrame): Original dataframe.
        date_range (Tuple[str, str]): Tuple of start and end date strings (YYYY-MM-DD).

    Returns:
        pd.DataFrame: Filtered dataframe within the date range.
    """
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    mask = (df["eater_request_timestamp_local"] >= start_date) & (
        df["eater_request_timestamp_local"] <= end_date
    )
    return df.loc[mask]


def plot_atd_by_hour(df: pd.DataFrame) -> None:
    """
    Plot ATD distribution by order hour (0–23).
    """
    st.subheader("🕒 ATD by Order Hour")
    hourly_atd = df.groupby("order_hour")["ATD"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=hourly_atd, x="order_hour", y="ATD", marker="o", ax=ax)
    ax.set_ylabel("ATD (minutes)")
    ax.set_xlabel("Order Hour")
    ax.set_xticks(range(0, 24))
    st.pyplot(fig)


def plot_atd_by_dayofweek(df: pd.DataFrame) -> None:
    """
    Plot ATD distribution by day of week (Monday=0).
    """
    st.subheader("📅 ATD by Day of Week")
    dow_map = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    df["day_name"] = df["order_dayofweek"].apply(lambda x: dow_map[x])

    day_atd = df.groupby("day_name")["ATD"].mean().reindex(dow_map).reset_index()

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(data=day_atd, x="day_name", y="ATD", ax=ax, palette="Blues_d")
    ax.set_ylabel("ATD (minutes)")
    ax.set_xlabel("Day of Week")
    st.pyplot(fig)


def plot_atd_by_part_of_day(df: pd.DataFrame) -> None:
    """
    Plot ATD distribution by part of the day.
    """
    st.subheader("📅 ATD by part of the day")

    day_atd = df.groupby("order_time_of_day")["ATD"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(data=day_atd, x="order_time_of_day", y="ATD", ax=ax, palette="Blues_d")
    ax.set_ylabel("ATD (minutes)")
    ax.set_xlabel("Part of the Day")
    st.pyplot(fig)


def plot_atd_by_date_peak(df: pd.DataFrame) -> None:
    """
    Plot average ATD by peak hour).
    """
    st.subheader("📅 ATD by peak hour")

    day_atd = df.groupby("is_peak_hour")["ATD"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(data=day_atd, x="is_peak_hour", y="ATD", ax=ax, palette="Blues_d")
    ax.set_ylabel("ATD (minutes)")
    ax.set_xlabel("is peak hour")
    st.pyplot(fig)


def plot_atd_by_weekend(df: pd.DataFrame) -> None:
    """
    Plot average ATD by weekend.
    """
    st.subheader("📅 ATD by weekend")

    weekend_atd = df.groupby("order_weekend")["ATD"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(data=weekend_atd, x="order_weekend", y="ATD", ax=ax, palette="Blues_d")
    ax.set_ylabel("ATD (minutes)")
    ax.set_xlabel("is placed on weekend")
    st.pyplot(fig)


def main() -> None:
    """
    Main function to run the Streamlit dashboard.
    """
    st.set_page_config(page_title="Uber Eats Delivery ATD Dashboard", layout="wide")

    st.title("🚴‍♂️ Uber Eats Delivery Performance Dashboard")
    st.markdown(
        """
        This dashboard provides insights on Actual Time to Delivery (ATD) and related operational metrics.
        Use the filters on the sidebar to explore data by date and category.
        """
    )

    # Load data
    data_path = (
        "../data/processed/BC_A&A_with_ATD_processed.parquet"  # Update this path to your file
    )
    df = load_data(data_path)
    df["eater_request_timestamp_local"] = pd.to_datetime(df["eater_request_timestamp_local"])

    # Sidebar filters
    st.sidebar.header("Filters")
    min_date = df["eater_request_timestamp_local"].min().date()
    max_date = df["eater_request_timestamp_local"].max().date()
    date_range = st.sidebar.date_input(
        "Select date range", [min_date, max_date], min_value=min_date, max_value=max_date
    )
    view_by = st.sidebar.radio("Time aggregation", ["Weekly", "Daily"], horizontal=True)

    filtered_df = filter_data_by_date(df, (str(date_range[0]), str(date_range[1])))

    # KPI Section
    st.subheader("Key Performance Indicators (KPIs)")
    col1, col2, col3, col4, col5 = st.columns(5)

    avg_atd = filtered_df["ATD"].mean()
    total_orders = len(filtered_df)
    unique_couriers = (
        filtered_df["driver_uuid"].nunique() if "driver_uuid" in filtered_df.columns else "N/A"
    )
    long_delivery_pct = (filtered_df["long_delivery_flag"].sum() / total_orders) * 100
    avg_distance = filtered_df["total_distance_km"].mean()

    col1.metric("Average ATD (min)", f"{avg_atd:.2f}" if pd.notnull(avg_atd) else "N/A")
    col2.metric("Total Orders", f"{total_orders}")
    col3.metric("Unique Couriers", f"{unique_couriers}")
    col4.metric("Long  Deliveries > 10 km", f"{long_delivery_pct:.1f}%")
    col5.metric(
        "Avg Total Distance (km)", f"{avg_distance:.2f}" if pd.notnull(avg_distance) else "N/A"
    )

    st.markdown("---")

    # Time Aggregation
    st.subheader("Average ATD Over Time")

    if view_by == "Weekly":
        filtered_df["period"] = (
            filtered_df["eater_request_timestamp_local"]
            .dt.to_period("W")
            .apply(lambda r: r.start_time)
        )
    else:
        filtered_df["period"] = filtered_df["eater_request_timestamp_local"].dt.date

    time_trend = filtered_df.groupby("period")["ATD"].mean().reset_index()

    fig_time = px.line(
        time_trend,
        x="period",
        y="ATD",
        title=f"{view_by} Average ATD",
        labels={"period": view_by, "ATD": "Avg ATD (min)"},
        markers=True,
    )
    st.plotly_chart(fig_time, use_container_width=True)

    st.markdown("---")

    # Trends by Category
    st.subheader("ATD Trends by Category")

    categories = ["territory", "courier_flow", "geo_archetype", "merchant_surface"]
    available_categories = [cat for cat in categories if cat in filtered_df.columns]
    selected_category = st.selectbox(
        "Select category to analyze ATD over time", available_categories
    )

    if selected_category:
        cat_trend = filtered_df.groupby([selected_category, "period"])["ATD"].mean().reset_index()

        fig_cat = px.line(
            cat_trend,
            x="period",
            y="ATD",
            color=selected_category,
            title=f"{view_by} Average ATD by {selected_category.capitalize()}",
            labels={
                "period": view_by,
                "ATD": "Avg ATD (min)",
                selected_category: selected_category.capitalize(),
            },
            markers=True,
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    st.markdown("---")
    st.header("Historical variables")

    # Distribution of ATD
    st.subheader("Distribution of ATD")

    atd_min = float(filtered_df["ATD"].min())
    atd_max = float(filtered_df["ATD"].quantile(0.99))  # Avoid outliers
    atd_range = st.slider(
        "Select ATD range for histogram (minutes)", atd_min, atd_max, (atd_min, atd_max)
    )

    hist_data = filtered_df[
        (filtered_df["ATD"] >= atd_range[0]) & (filtered_df["ATD"] <= atd_range[1])
    ]

    fig_hist = px.histogram(
        hist_data,
        x="ATD",
        nbins=50,
        title="Distribution of Actual Time to Delivery (ATD)",
        labels={"ATD": "ATD (minutes)"},
        opacity=0.75,
        marginal="box",
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("---")

    # Scatter plots
    st.subheader("🧭 Relationships between ATD and Distance / Time Features")

    for x_col, label in [
        ("pickup_distance", "Pickup Distance (km)"),
        ("dropoff_distance", "Dropoff Distance (km)"),
        ("total_distance_km", "Total Distance (km)"),
        ("preparation_time_minutes", "Preparation Time (min)"),
    ]:
        fig, ax = plt.subplots(figsize=(10, 5))
        sample = filtered_df[[x_col, "ATD"]].dropna().sample(n=min(5000, len(filtered_df)))
        sns.scatterplot(x=x_col, y="ATD", data=sample, alpha=0.4, ax=ax)
        sns.regplot(x=x_col, y="ATD", data=sample, scatter=False, ax=ax, color="red")
        ax.set_title(f"ATD vs {label}")
        ax.set_xlabel(label)
        ax.set_ylabel("ATD (minutes)")
        st.pyplot(fig)

    st.divider()

    plot_atd_by_hour(filtered_df)
    plot_atd_by_dayofweek(filtered_df)
    plot_atd_by_part_of_day(filtered_df)
    plot_atd_by_date_peak(filtered_df)
    plot_atd_by_weekend(filtered_df)


if __name__ == "__main__":
    main()
