"""Learning roadmap page."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.api_client import api_client
from utils.ui import humanize_role

st.set_page_config(page_title="Learning Roadmap", page_icon="🗺️", layout="wide")
st.title("Learning Roadmap")
st.caption("Turn the benchmark gaps from your analysis into a phased study plan you can actually execute.")

roadmap = st.session_state.get("roadmap")
analysis_id = st.session_state.get("analysis_id")

if roadmap is None and analysis_id:
    roadmap = api_client.post(f"/roadmap/{analysis_id}?total_weeks=12")
    st.session_state["roadmap"] = roadmap

if roadmap is None:
    st.info("Generate a roadmap from the Resume Analyzer page first.")
    st.stop()

st.subheader(f"{humanize_role(roadmap['target_role'])} | {roadmap['total_weeks']} weeks")

if not roadmap["phases"]:
    st.success(
        "This profile already covers the tracked market benchmark unusually well. Use the Resume Analyzer again with a different role or a shorter, more realistic skill list to generate a sharper roadmap."
    )
    st.stop()

timeline_rows = []
for phase in roadmap["phases"]:
    start_week = int(phase["week_range"].split()[1].split("-")[0])
    end_week = int(phase["week_range"].split("-")[-1])
    for skill in phase["skills"]:
        timeline_rows.append(
            {
                "Skill": skill["skill_name"],
                "Start": start_week,
                "Finish": end_week,
                "Category": skill["category"],
                "Phase": phase["phase_title"],
            }
        )

frame = pd.DataFrame(timeline_rows)
if not frame.empty:
    fig = px.timeline(
        frame,
        x_start="Start",
        x_end="Finish",
        y="Skill",
        color="Phase",
        title="Execution Timeline",
        hover_data={"Category": True, "Start": True, "Finish": True},
    )
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig, use_container_width=True)

for phase in roadmap["phases"]:
    with st.expander(f"{phase['phase_title']} | {phase['week_range']}", expanded=True):
        for skill in phase["skills"]:
            st.markdown(
                f"**{skill['skill_name']}** | {skill['category'].title()} | {skill['market_frequency_pct']:.1f}% of tracked postings"
            )
            st.caption(skill["why_important"])
            st.markdown(f"Free resource: [{skill['free_resource']['title']}]({skill['free_resource']['url']})")
            st.markdown(f"Paid resource: [{skill['paid_resource']['title']}]({skill['paid_resource']['url']})")
            st.markdown(f"Project proof idea: {skill['project_idea']}")
            st.divider()

st.subheader("Weekly Updates")
email = st.text_input("Email address")
if st.button("Subscribe", use_container_width=True) and email:
    result = api_client.post("/notifications/subscribe", json={"email": email, "role_filter": "all"})
    st.success(f"Subscribed {result['email']}")
