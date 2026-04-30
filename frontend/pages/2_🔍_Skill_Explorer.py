"""Skill explorer page."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from components.trend_chart import render_trend_chart
from utils.api_client import api_client

st.set_page_config(page_title="Skill Explorer", page_icon="🔍", layout="wide")
st.title("Skill Explorer")

top_skills = api_client.get("/skills/top", params={"role_filter": "all", "limit": 100})
skill_options = [item["skill_name"] for item in top_skills]
search = st.text_input("Search skills")
filtered = [skill for skill in skill_options if search.lower() in skill.lower()]
selected_skill = st.selectbox("Select a skill", filtered or skill_options)

trend = api_client.get(f"/skills/trend/{selected_skill}", params={"role_filter": "all", "weeks": 12})
st.plotly_chart(render_trend_chart(trend["points"], f"{selected_skill} Trend"), use_container_width=True)

if trend["points"]:
    current = trend["points"][-1]["frequency_pct"]
    peak = max(trend["points"], key=lambda point: point["frequency_pct"])
    st.columns(4)[0].metric("Current frequency", f"{current:.1f}%")
    st.columns(4)[1].metric("Peak week", peak["week_start"])
    st.columns(4)[2].metric("Peak frequency", f"{peak['frequency_pct']:.1f}%")
    st.columns(4)[3].metric("Data points", len(trend["points"]))

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
