"""Skill explorer page."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from components.trend_chart import render_trend_chart
from utils.api_client import api_client
from utils.ui import infer_data_mode

st.set_page_config(page_title="Skill Explorer", page_icon="🔍", layout="wide")
st.title("Skill Explorer")
st.caption("Pick one skill to inspect how demand changes over time in the current dataset.")

top_skills = api_client.get("/skills/top", params={"role_filter": "all", "limit": 100})
scrape_status = api_client.get("/scrape/status")
skill_options = [item["skill_name"] for item in top_skills]
data_mode, data_message = infer_data_mode(scrape_status.get("posting_counts", {}))

banner_left, banner_right = st.columns([1.2, 2.2])
banner_left.info(f"Dataset: {data_mode}")
banner_right.caption(data_message)

selected_skill = st.selectbox(
    "Choose a skill",
    skill_options,
    help="This dropdown is searchable, so you can type directly into it to find a skill faster.",
)

trend = api_client.get(f"/skills/trend/{selected_skill}", params={"role_filter": "all", "weeks": 12})
st.plotly_chart(render_trend_chart(trend["points"], f"{selected_skill} Trend"), use_container_width=True)

if trend["points"]:
    current = trend["points"][-1]["frequency_pct"]
    peak = max(trend["points"], key=lambda point: point["frequency_pct"])
    velocity = current - trend["points"][0]["frequency_pct"]
    stats = st.columns(4)
    stats[0].metric("Current frequency", f"{current:.1f}%")
    stats[1].metric("Peak week", peak["week_start"])
    stats[2].metric("Peak frequency", f"{peak['frequency_pct']:.1f}%")
    stats[3].metric("12-week change", f"{velocity:+.1f} pts")

frame = pd.DataFrame(top_skills)
if not frame.empty:
    fig = px.treemap(
        frame,
        path=[px.Constant("skills"), "category", "skill_name"],
        values="frequency_pct",
        color="frequency_pct",
        color_continuous_scale="Tealgrn",
        title="Skill Category Explorer",
    )
    st.plotly_chart(fig, use_container_width=True)
