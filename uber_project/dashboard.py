import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style('whitegrid')

@st.cache_data
def load_data(path):
    df = pd.read_parquet(path)
    df['order_final_state_timestamp_local'] = pd.to_datetime(df['order_final_state_timestamp_local'])
    df['order_week'] = df['order_final_state_timestamp_local'].dt.isocalendar().week
    return df

def main():
    st.title("🚀 Food Delivery Dashboard - Insights on Actual Time of Delivery (ATD)")

    # Load data
    data_path = '../data/processed/BC_A&A_with_ATD_processed.parquet'
    df = load_data(data_path)

    # Sidebar filters
    st.sidebar.header("Filters")

    weeks = sorted(df['order_week'].unique())
    selected_weeks = st.sidebar.multiselect("Select week(s)", options=weeks, default=weeks)

    territories = sorted(df['territory'].unique())
    selected_territories = st.sidebar.multiselect("Select territory(ies)", options=territories, default=territories)

    courier_flows = sorted(df['courier_flow'].unique())
    selected_couriers = st.sidebar.multiselect("Select courier flow(s)", options=courier_flows, default=courier_flows)

    # Filter data
    df_filtered = df[
        (df['order_week'].isin(selected_weeks)) &
        (df['territory'].isin(selected_territories)) &
        (df['courier_flow'].isin(selected_couriers))
    ]

    st.markdown(f"### Showing data for {len(df_filtered)} deliveries")

    # Summary KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg ATD (min)", f"{df_filtered['ATD'].mean():.2f}")
    with col2:
        st.metric("Median ATD (min)", f"{df_filtered['ATD'].median():.2f}")
    with col3:
        long_deliv_pct = 100 * df_filtered['long_delivery_flag'].mean()
        st.metric("Long Delivery % (> threshold)", f"{long_deliv_pct:.2f}%")
    with col4:
        st.metric("Avg Preparation Time (min)", f"{df_filtered['preparation_time_minutes'].mean():.2f}")

    st.markdown("---")

    # Distribution of ATD
    st.subheader("Distribution of Actual Time of Delivery (ATD)")
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(df_filtered['ATD'], bins=50, kde=True, color='blue', ax=ax)
    ax.set_xlabel("ATD (minutes)")
    st.pyplot(fig)

    st.markdown("---")

    # Boxplots of ATD by categorical variables
    st.subheader("ATD by Territory, Courier Flow and Geo Archetype")

    cat_vars = ['territory', 'courier_flow', 'geo_archetype']

    for var in cat_vars:
        fig, ax = plt.subplots(figsize=(12, 5))
        sns.boxplot(x=var, y='ATD', data=df_filtered, ax=ax)
        ax.set_title(f"ATD distribution by {var.capitalize()}")
        ax.set_xlabel(var.capitalize())
        ax.set_ylabel("ATD (minutes)")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    st.markdown("---")

    # Scatter plots and correlation insights
    st.subheader("Relationships between ATD and Distances / Times")

    # Scatter with pickup_distance
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(x='pickup_distance', y='ATD', data=df_filtered.sample(5000), alpha=0.4, ax=ax)
    sns.regplot(x='pickup_distance', y='ATD', data=df_filtered.sample(5000), scatter=False, ax=ax, color='red')
    ax.set_title("ATD vs Pickup Distance (km)")
    st.pyplot(fig)

    # Scatter with dropoff_distance
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(x='dropoff_distance', y='ATD', data=df_filtered.sample(5000), alpha=0.4, ax=ax)
    sns.regplot(x='dropoff_distance', y='ATD', data=df_filtered.sample(5000), scatter=False, ax=ax, color='red')
    ax.set_title("ATD vs Dropoff Distance (km)")
    st.pyplot(fig)

    # Scatter with preparation_time_minutes
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(x='preparation_time_minutes', y='ATD', data=df_filtered.sample(5000), alpha=0.4, ax=ax)
    sns.regplot(x='preparation_time_minutes', y='ATD', data=df_filtered.sample(5000), scatter=False, ax=ax, color='red')
    ax.set_title("ATD vs Preparation Time (minutes)")
    st.pyplot(fig)

    st.markdown("---")

    # Correlation heatmap of numeric features
    st.subheader("Correlation Heatmap")

    numeric_cols = [
        'pickup_distance', 'dropoff_distance', 'ATD', 'preparation_time_minutes',
        'dispatch_delay_minutes', 'delivery_duration_seconds', 'total_distance_km',
        'distance_ratio', 'courier_flow_complexity_score', 'estimated_speed_kmh',
        'relative_prep_time'
    ]
    corr = df_filtered[numeric_cols].corr()

    fig, ax = plt.subplots(figsize=(10, 7))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', ax=ax)
    st.pyplot(fig)

    st.markdown("---")

    # Distribution by day of week and peak hours
    st.subheader("ATD by Day of Week and Peak Hours")

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.boxplot(x='order_dayofweek', y='ATD', hue='is_peak_hour', data=df_filtered, ax=ax)
    ax.set_xlabel("Day of Week (0=Mon, 6=Sun)")
    ax.set_ylabel("ATD (minutes)")
    ax.set_title("ATD Distribution by Day of Week and Peak Hour")
    st.pyplot(fig)

if __name__ == "__main__":
    main()
