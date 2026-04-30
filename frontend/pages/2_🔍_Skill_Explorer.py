"""Skill explorer page."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from components.trend_chart import render_trend_chart
from utils.api_client import api_client
from utils.ui import describe_role, humanize_role, infer_data_mode

st.set_page_config(page_title="Skill Explorer", page_icon="🔍", layout="wide")
st.title("Skill Explorer")
st.caption("Inspect one skill at a time and compare its demand inside a role against the broader market.")

try:
    role_options = api_client.get("/skills/roles", params={"limit": 10})
    scrape_status = api_client.get("/scrape/status")
except Exception as exc:
    st.error(f"Backend unavailable: {exc}")
    st.stop()

role_lookup = {item["role_key"]: item for item in role_options}
role_keys = [item["role_key"] for item in role_options]
selected_role = st.selectbox("Role benchmark", role_keys, format_func=humanize_role)

try:
    top_skills = api_client.get("/skills/top", params={"role_filter": selected_role, "limit": 25})
except Exception as exc:
    st.error(f"Unable to load skill list: {exc}")
    st.stop()

skill_options = [item["skill_name"] for item in top_skills]
if not skill_options:
    st.warning("No skills are available for this role yet.")
    st.stop()

data_mode, data_message = infer_data_mode(scrape_status.get("posting_counts", {}))
banner_left, banner_right = st.columns([1.1, 2.4])
banner_left.info(f"Dataset: {data_mode}")
banner_right.caption(data_message)

role_meta = role_lookup[selected_role]
st.info(
    f"**{role_meta['label']}** | {describe_role(selected_role)} "
    f"| Tracked postings: {role_meta['latest_postings']} "
    f"| This week's leading skill: {role_meta['top_skill'] or 'N/A'}"
)

selected_skill = st.selectbox(
    "Skill to inspect",
    skill_options,
    help="Type to search. The list is limited to the most visible skills for the selected role.",
)

try:
    role_trend = api_client.get(f"/skills/trend/{selected_skill}", params={"role_filter": selected_role, "weeks": 12})
    overall_trend = api_client.get(f"/skills/trend/{selected_skill}", params={"role_filter": "all", "weeks": 12})
except Exception as exc:
    st.error(f"Unable to load trend data: {exc}")
    st.stop()

st.plotly_chart(
    render_trend_chart(
        role_trend["points"],
        title=f"{selected_skill} Demand Trend",
        comparison_points=overall_trend["points"],
        primary_label=humanize_role(selected_role),
        comparison_label="Overall Market",
    ),
    use_container_width=True,
)

if role_trend["points"]:
    current = role_trend["points"][-1]["frequency_pct"]
    overall_current = overall_trend["points"][-1]["frequency_pct"] if overall_trend["points"] else 0.0
    peak = max(role_trend["points"], key=lambda point: point["frequency_pct"])
    velocity = current - role_trend["points"][0]["frequency_pct"]
    selected_row = next((item for item in top_skills if item["skill_name"] == selected_skill), None)
    skill_rank = skill_options.index(selected_skill) + 1 if selected_skill in skill_options else None

    stats = st.columns(5)
    stats[0].metric("Current role demand", f"{current:.1f}%")
    stats[1].metric("Overall market demand", f"{overall_current:.1f}%")
    stats[2].metric("12-week change", f"{velocity:+.1f} pts")
    stats[3].metric("Peak week", peak["week_start"])
    stats[4].metric("Role rank", f"#{skill_rank}" if skill_rank is not None else "N/A")

    if selected_row:
        st.caption(
            f"{selected_skill} currently sits inside the **top {skill_rank}** skills for {humanize_role(selected_role)} "
            f"under the **{selected_row['category']}** category."
        )

benchmark_frame = pd.DataFrame(top_skills[:10])
if not benchmark_frame.empty:
    benchmark_frame["highlight"] = benchmark_frame["skill_name"].apply(
        lambda name: "Selected Skill" if name == selected_skill else "Other Top Skill"
    )
    fig = px.bar(
        benchmark_frame.sort_values("frequency_pct"),
        x="frequency_pct",
        y="skill_name",
        orientation="h",
        color="highlight",
        color_discrete_map={"Selected Skill": "#0f766e", "Other Top Skill": "#cbd5e1"},
        title=f"Where {selected_skill} Sits Inside {humanize_role(selected_role)}",
        labels={"frequency_pct": "Share of postings (%)", "skill_name": "Skill"},
    )
    fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig, use_container_width=True)

st.caption(
    "How to read this page: the solid line shows demand inside the selected role, the dotted line shows the overall market, and the bar chart shows whether the skill is a headline requirement or a supporting one."
)
