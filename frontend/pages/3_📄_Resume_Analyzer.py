"""Resume analyzer page."""

from __future__ import annotations

import uuid

import streamlit as st

from components.gap_display import render_gap_gauge, render_gap_scatter, render_skill_lists
from utils.api_client import api_client
from utils.ui import humanize_role

st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="wide")
st.title("Resume Analyzer")
st.caption("Compare your current profile against the market and see what to strengthen next.")

session_id = st.session_state.setdefault("session_id", str(uuid.uuid4()))
tab_upload, tab_manual = st.tabs(["Upload Resume", "Enter Skills Manually"])
role_options = ["ml_engineer", "llm_engineer", "data_scientist"]

analysis = None

with tab_upload:
    uploaded = st.file_uploader("Upload your resume", type=["pdf", "docx"])
    upload_role = st.selectbox(
        "Target role",
        role_options,
        key="upload_role",
        format_func=humanize_role,
    )
    st.caption("Best for testing the end-to-end resume parsing flow.")
    if st.button("Analyze Resume", use_container_width=True) and uploaded is not None:
        analysis = api_client.post(
            "/analyze/resume",
            files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")},
            data={"session_id": session_id, "target_role": upload_role},
        )

with tab_manual:
    manual_skills = st.text_area("Enter your skills", placeholder="Python, PyTorch, Docker")
    manual_role = st.selectbox(
        "Target role",
        role_options,
        key="manual_role",
        format_func=humanize_role,
    )
    st.caption("Fastest demo flow if you want to test the analysis without uploading a file.")
    if st.button("Analyze Skills", use_container_width=True):
        skills = [item.strip() for item in manual_skills.replace("\n", ",").split(",") if item.strip()]
        if not skills:
            st.warning("Add at least one skill before running manual analysis.")
            st.stop()
        analysis = api_client.post(
            "/analyze/skills",
            json={"session_id": session_id, "target_role": manual_role, "skills": skills},
        )

if analysis:
    st.session_state["analysis_id"] = analysis["analysis_id"]
    st.session_state["gap_result"] = analysis

gap_result = st.session_state.get("gap_result")
if gap_result:
    st.success(
        f"Analysis ready for {humanize_role(gap_result['target_role'])}. "
        f"Detected {len(gap_result['extracted_skills'])} normalized skills."
    )
    summary = gap_result["summary"]
    summary_cards = st.columns(4)
    summary_cards[0].metric("Fit score", f"{gap_result['gap_score']:.0f}/100")
    summary_cards[1].metric("Exact matches", summary["exact_matches"])
    summary_cards[2].metric("Adjacent matches", summary["adjacent_matches"])
    summary_cards[3].metric("Critical gaps", summary["critical_gaps"])
    st.plotly_chart(render_gap_gauge(gap_result["gap_score"], gap_result["fit_label"]), use_container_width=True)
    render_skill_lists(gap_result["strengths"], gap_result["gaps"])
    st.plotly_chart(
        render_gap_scatter(gap_result["strengths"], gap_result["gaps"]),
        use_container_width=True,
    )
    weeks = st.slider("Weeks available", min_value=4, max_value=26, value=12)
    if st.button("Generate My Learning Roadmap", use_container_width=True):
        roadmap = api_client.post(f"/roadmap/{gap_result['analysis_id']}?total_weeks={weeks}")
        st.session_state["roadmap"] = roadmap
        st.switch_page("pages/4_🗺️_Learning_Roadmap.py")
