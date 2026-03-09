# =========================================================
# PEREN AI – Digital Twin Dashboard (Simple + Single Timeline)
# 3 indicators on ONE chart - exactly like your image
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# Page config
# ---------------------------------------------------------
st.set_page_config(layout="wide")
st.title("PEREN AI – Digital Twin Dashboard")

# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------
df = pd.read_csv("final_digital_twin.csv")

df["datetime"] = pd.to_datetime(df["datetime"])
df = df.sort_values(["user_id", "datetime"])

# ---------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------
st.sidebar.header("Filters")
users = df["user_id"].unique()
selected_user = st.sidebar.selectbox("User", users)

user_df = df[df["user_id"] == selected_user].copy()
user_df = user_df.sort_values("datetime")

latest = user_df.iloc[-1]

# =========================================================
# USER PROFILE
# =========================================================
st.subheader("User Profile")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Sex", latest["sex"])
c2.metric("Chronological Age", latest["age"])

delta_age = latest["body_age"] - latest["age"]

c3.metric(
    "Body Age",
    latest["body_age"],
    delta=delta_age,
    delta_color="inverse"
)

c4.metric(
    "Last Assessment",
    latest["datetime"].strftime("%Y-%m-%d")
)

st.divider()

# =========================================================
# KPI INDICATORS
# =========================================================
st.subheader("Health Indicators (vs previous assessment)")

k1, k2, k3 = st.columns(3)

k1.metric(
    "Body Age",
    latest["body_age"],
    delta=latest["body_age_change"],
    delta_color="inverse"
)

k2.metric(
    "Work Load",
    latest["work_load"],
    delta=latest["work_load_change"]
)

k3.metric(
    "Body Toxins",
    latest["body_toxin"],
    delta=latest["body_toxin_change"]
)

st.divider()

# =========================================================
# STATES
# =========================================================
st.subheader("Current Body States")

s1, s2, s3 = st.columns(3)

s1.metric("Body Age State", latest["body_age_state"])
s2.metric("Workload State", latest["workload_state"])
s3.metric("Toxins State", latest["body_toxins_state"])

st.divider()

# =========================================================
# SINGLE TIMELINE CHART (exactly like your image)
# =========================================================
st.subheader("Longitudinal Performance Timeline")

fig = px.line(
    user_df,
    x="datetime",
    y=["body_age", "work_load", "body_toxin"],
    labels={"value": "Score", "datetime": "Date", "variable": "Metric"},
    color_discrete_map={
        "body_age": "#FFD700",      # yellow
        "work_load": "#00FF9D",     # green
        "body_toxin": "#00CCFF"     # cyan
    }
)

fig.update_layout(
    template="plotly_dark",
    height=500,
    legend_title="Metrics",
    xaxis_title="Date",
    yaxis_title="Score",
    legend=dict(orientation="v", yanchor="top", xanchor="right", x=1.05)
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# =========================================================
# RAW TABLE
# =========================================================
st.subheader("Assessment History")
st.dataframe(user_df)