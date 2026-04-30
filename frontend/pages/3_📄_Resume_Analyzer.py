"""Resume analyzer page."""

from __future__ import annotations

import uuid

import streamlit as st

from components.gap_display import render_gap_gauge, render_gap_scatter, render_skill_lists
from utils.api_client import api_client
from utils.ui import describe_role, humanize_role

st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="wide")
st.title("Resume Analyzer")
st.caption(
    "Benchmark a resume against the selected role's latest market snapshot using direct matches, transferable skills, core-skill coverage, and category coverage."
)

try:
    role_options = api_client.get("/skills/roles", params={"limit": 10})
except Exception as exc:
    st.error(f"Backend unavailable: {exc}")
    st.stop()

role_keys = [item["role_key"] for item in role_options]
role_lookup = {item["role_key"]: item for item in role_options}
session_id = st.session_state.setdefault("session_id", str(uuid.uuid4()))
tab_upload, tab_manual = st.tabs(["Upload Resume", "Enter Skills Manually"])

analysis = None

with tab_upload:
    uploaded = st.file_uploader("Upload your resume", type=["pdf", "docx"])
    upload_role = st.selectbox("Target role", role_keys, key="upload_role", format_func=humanize_role)
    st.caption(describe_role(upload_role))
    st.caption("Best for testing the full parsing flow with a realistic recruiter benchmark.")
    if st.button("Analyze Resume", use_container_width=True) and uploaded is not None:
        analysis = api_client.post(
            "/analyze/resume",
            files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")},
            data={"session_id": session_id, "target_role": upload_role},
        )

with tab_manual:
    manual_skills = st.text_area(
        "Enter your skills",
        placeholder="Python, PyTorch, SQL, Docker, AWS",
    )
    manual_role = st.selectbox("Target role", role_keys, key="manual_role", format_func=humanize_role)
    st.caption(describe_role(manual_role))
    st.caption("Fastest way to sanity-check the scoring logic without uploading a document.")
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
    role_meta = role_lookup.get(gap_result["target_role"])
    st.success(
        f"Analysis ready for {humanize_role(gap_result['target_role'])}. "
        f"Detected {len(gap_result['extracted_skills'])} normalized skills."
    )
    if role_meta:
        st.info(
            f"Benchmark role: **{role_meta['label']}** | Tracked postings: {role_meta['latest_postings']} "
            f"| Leading benchmark skill: {role_meta['top_skill'] or 'N/A'}"
        )

    summary = gap_result["summary"]
    summary_cards = st.columns(5)
    summary_cards[0].metric("Fit score", f"{gap_result['gap_score']:.0f}/100")
    summary_cards[1].metric("Exact matches", summary["exact_matches"])
    summary_cards[2].metric("Adjacent matches", summary["adjacent_matches"])
    summary_cards[3].metric("Core skill coverage", f"{summary['core_skill_coverage_pct']:.0f}%")
    summary_cards[4].metric("Critical gaps", summary["critical_gaps"])
    st.caption(
        f"Category coverage: {summary['category_coverage_pct']:.0f}% of the tracked benchmark categories. "
        "Scores reward direct proof, partial credit for adjacent skills, and heavier weighting on core hiring signals."
    )

    st.plotly_chart(render_gap_gauge(gap_result["gap_score"], gap_result["fit_label"]), use_container_width=True)
    render_skill_lists(gap_result["strengths"], gap_result["gaps"])
    st.plotly_chart(
        render_gap_scatter(gap_result["strengths"], gap_result["gaps"]),
        use_container_width=True,
    )
    weeks = st.slider("Weeks available for upskilling", min_value=4, max_value=26, value=12)
    if st.button("Generate My Learning Roadmap", use_container_width=True):
        roadmap = api_client.post(f"/roadmap/{gap_result['analysis_id']}?total_weeks={weeks}")
        st.session_state["roadmap"] = roadmap
        st.switch_page("pages/4_🗺️_Learning_Roadmap.py")
