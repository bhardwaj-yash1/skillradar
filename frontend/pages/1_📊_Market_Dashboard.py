"""Market dashboard page."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from components.skill_heatmap import render_skill_heatmap
from utils.api_client import api_client
from utils.ui import describe_role, humanize_role, infer_data_mode

st.set_page_config(page_title="Market Dashboard", page_icon="📊", layout="wide")
st.title("Market Dashboard")
st.caption("Explore a recruiter-friendly snapshot of how AI and data roles are trending across the current market dataset.")

try:
    role_options = api_client.get("/skills/roles", params={"limit": 10})
    scrape_status = api_client.get("/scrape/status")
except Exception as exc:
    st.error(f"Backend unavailable: {exc}")
    st.stop()

role_lookup = {item["role_key"]: item for item in role_options}
selectable_roles = ["all"] + [item["role_key"] for item in role_options]
selected_role = st.selectbox("Role view", selectable_roles, format_func=humanize_role)

try:
    summary = api_client.get("/skills/summary", params={"role_filter": selected_role})
    top_skills = api_client.get("/skills/top", params={"role_filter": selected_role, "limit": 12})
    trending = api_client.get("/skills/trending", params={"role_filter": selected_role})
    heatmap = api_client.get("/skills/heatmap", params={"role_filter": selected_role})
except Exception as exc:
    st.error(f"Unable to load market analytics: {exc}")
    st.stop()

data_mode, data_message = infer_data_mode(scrape_status.get("posting_counts", {}))
banner_left, banner_right = st.columns([1.1, 2.4])
banner_left.info(f"Dataset: {data_mode}")
banner_right.caption(data_message)

selected_role_meta = role_lookup.get(selected_role)
if selected_role_meta:
    st.info(
        f"**{selected_role_meta['label']}** | {describe_role(selected_role)} "
        f"| Latest tracked postings: {selected_role_meta['latest_postings']} "
        f"| Week-over-week change: {selected_role_meta['week_over_week_change_pct']:+.1f}% "
        f"| Top requested skill: {selected_role_meta['top_skill'] or 'N/A'}"
    )
else:
    st.info("Use the role selector to move between the overall market view and the 10 most active tracked roles.")

metric_cols = st.columns(5)
metric_cols[0].metric("Tracked postings", summary["total_postings"])
metric_cols[1].metric("Unique tracked skills", summary["unique_skills"])
metric_cols[2].metric("Most requested skill", summary["top_skill"] or "N/A")
metric_cols[3].metric("Fastest rising skill", summary["fastest_rising"] or "N/A")
metric_cols[4].metric("Latest snapshot week", summary["data_freshness_week"] or "N/A")

top_frame = pd.DataFrame(top_skills)
row_left, row_right = st.columns((1.1, 0.9))

if not top_frame.empty:
    with row_left:
        fig = px.bar(
            top_frame.sort_values("frequency_pct"),
            x="frequency_pct",
            y="skill_name",
            orientation="h",
            color="category",
            title=f"Top Skills Recruiters Keep Asking For: {humanize_role(selected_role)}",
            labels={"frequency_pct": "Share of postings (%)", "skill_name": "Skill"},
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(margin=dict(l=20, r=20, t=60, b=20), legend_title_text="Category")
        st.plotly_chart(fig, use_container_width=True)

velocity_rows = trending["rising"][:8] + trending["falling"][:4]
velocity_frame = pd.DataFrame(velocity_rows)
if not velocity_frame.empty:
    velocity_frame["direction"] = velocity_frame["velocity"].apply(lambda value: "Rising" if value >= 0 else "Cooling")
    with row_right:
        fig = px.bar(
            velocity_frame.sort_values("velocity"),
            x="velocity",
            y="skill_name",
            orientation="h",
            color="direction",
            color_discrete_map={"Rising": "#15803d", "Cooling": "#dc2626"},
            title="Momentum This Quarter",
            labels={"velocity": "12-week change (percentage points)", "skill_name": "Skill"},
        )
        fig.update_layout(margin=dict(l=20, r=20, t=60, b=20), legend_title_text="Direction")
        st.plotly_chart(fig, use_container_width=True)

if not top_frame.empty and heatmap.get("matrix"):
    focus_skills = top_frame.head(5)["skill_name"].tolist()
    weeks = heatmap["weeks"]
    trend_rows = []
    for skill_name, values in zip(heatmap["skills"], heatmap["matrix"], strict=False):
        if skill_name not in focus_skills:
            continue
        for week, value in zip(weeks, values, strict=False):
            trend_rows.append({"week_start": week, "frequency_pct": value, "skill_name": skill_name})

    focus_frame = pd.DataFrame(trend_rows)
    if not focus_frame.empty:
        st.plotly_chart(
            px.line(
                focus_frame,
                x="week_start",
                y="frequency_pct",
                color="skill_name",
                markers=True,
                title="How The Top Skills Moved Over 12 Weeks",
                labels={"week_start": "Week", "frequency_pct": "Share of postings (%)", "skill_name": "Skill"},
            ),
            use_container_width=True,
        )

st.caption(
    "Heatmap guide: darker cells mean that skill showed up in a larger share of tracked postings during that week."
)
st.plotly_chart(render_skill_heatmap(heatmap), use_container_width=True)
