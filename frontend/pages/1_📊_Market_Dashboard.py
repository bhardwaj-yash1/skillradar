"""Market dashboard page."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from components.skill_heatmap import render_skill_heatmap
from utils.api_client import api_client

st.set_page_config(page_title="Market Dashboard", page_icon="📊", layout="wide")
st.title("Market Dashboard")

role_filter = st.selectbox("Role filter", ["all"], index=0)

try:
    summary = api_client.get("/skills/summary", params={"role_filter": role_filter})
    top_skills = api_client.get("/skills/top", params={"role_filter": role_filter, "limit": 20})
    trending = api_client.get("/skills/trending", params={"role_filter": role_filter})
    heatmap = api_client.get("/skills/heatmap", params={"role_filter": role_filter})
except Exception as exc:
    st.error(f"Backend unavailable: {exc}")
    st.stop()

metric_cols = st.columns(5)
metric_cols[0].metric("Total postings", summary["total_postings"])
metric_cols[1].metric("Unique skills", summary["unique_skills"])
metric_cols[2].metric("Top skill", summary["top_skill"] or "N/A")
metric_cols[3].metric("Fastest rising", summary["fastest_rising"] or "N/A")
metric_cols[4].metric("Data freshness", summary["data_freshness_week"] or "N/A")

row1_left, row1_right = st.columns(2)
top_frame = pd.DataFrame(top_skills)
if not top_frame.empty:
    with row1_left:
        fig = px.bar(
            top_frame.sort_values("frequency_pct"),
            x="frequency_pct",
            y="skill_name",
            orientation="h",
            color="category",
            title="Top 20 Skills",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        st.plotly_chart(fig, use_container_width=True)

velocity_rows = trending["rising"][:10] + trending["falling"][:5]
velocity_frame = pd.DataFrame(velocity_rows)
if not velocity_frame.empty:
    velocity_frame["direction"] = velocity_frame["velocity"].apply(lambda value: "Rising" if value >= 0 else "Falling")
    with row1_right:
        fig = px.bar(
            velocity_frame.sort_values("velocity"),
            x="velocity",
            y="skill_name",
            orientation="h",
            color="direction",
            color_discrete_map={"Rising": "#15803d", "Falling": "#dc2626"},
            title="Trending Velocity",
        )
        st.plotly_chart(fig, use_container_width=True)

st.plotly_chart(render_skill_heatmap(heatmap), use_container_width=True)
