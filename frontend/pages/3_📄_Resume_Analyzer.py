"""Resume analyzer page."""

from __future__ import annotations

import uuid

import streamlit as st

from components.gap_display import render_gap_gauge, render_gap_scatter, render_skill_lists
from utils.api_client import api_client

st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="wide")
st.title("Resume Analyzer")

session_id = st.session_state.setdefault("session_id", str(uuid.uuid4()))
tab_upload, tab_manual = st.tabs(["Upload Resume", "Enter Skills Manually"])

analysis = None

with tab_upload:
    uploaded = st.file_uploader("Upload your resume", type=["pdf", "docx"])
    upload_role = st.selectbox("Target role", ["ml_engineer", "llm_engineer", "data_scientist"], key="upload_role")
    if st.button("Analyze Resume", use_container_width=True) and uploaded is not None:
        analysis = api_client.post(
            "/analyze/resume",
            files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")},
            data={"session_id": session_id, "target_role": upload_role},
        )

with tab_manual:
    manual_skills = st.text_area("Enter your skills", placeholder="Python, PyTorch, Docker")
    manual_role = st.selectbox("Target role", ["ml_engineer", "llm_engineer", "data_scientist"], key="manual_role")
    if st.button("Analyze Skills", use_container_width=True):
        skills = [item.strip() for item in manual_skills.replace("\n", ",").split(",") if item.strip()]
        analysis = api_client.post(
            "/analyze/skills",
            json={"session_id": session_id, "target_role": manual_role, "skills": skills},
        )

if analysis:
    st.session_state["analysis_id"] = analysis["analysis_id"]
    st.session_state["gap_result"] = analysis

gap_result = st.session_state.get("gap_result")
if gap_result:
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
