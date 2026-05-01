"""SkillRadar Streamlit home page."""

from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="SkillRadar", page_icon="📡", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --ink-strong: #14213d;
        --ink-soft: #415a77;
        --panel: rgba(255, 252, 245, 0.88);
        --panel-strong: rgba(255, 255, 255, 0.96);
        --accent: #0f766e;
        --accent-soft: #d9f3ef;
        --gold: #f0b429;
        --line: rgba(20, 33, 61, 0.10);
        --shadow: 0 28px 80px rgba(20, 33, 61, 0.12);
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(240, 180, 41, 0.20), transparent 26%),
            radial-gradient(circle at 80% 20%, rgba(15, 118, 110, 0.16), transparent 24%),
            linear-gradient(160deg, #f7f3ea 0%, #eef6f5 52%, #f8fafc 100%);
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    .hero-shell {
        position: relative;
        overflow: hidden;
        padding: 3.25rem;
        border-radius: 30px;
        background:
            linear-gradient(135deg, rgba(255,255,255,0.98), rgba(246,250,252,0.92)),
            radial-gradient(circle at top right, rgba(240,180,41,0.16), transparent 30%);
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
    }

    .hero-shell::after {
        content: "";
        position: absolute;
        inset: auto -6% -22% auto;
        width: 280px;
        height: 280px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(15,118,110,0.18), rgba(15,118,110,0));
        pointer-events: none;
    }

    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.85rem;
        border-radius: 999px;
        background: rgba(15, 118, 110, 0.08);
        color: var(--accent);
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .hero-title {
        margin: 1rem 0 0.85rem;
        color: var(--ink-strong);
        font-size: clamp(2.8rem, 5vw, 4.6rem);
        line-height: 0.98;
        font-weight: 800;
        letter-spacing: -0.05em;
    }

    .hero-copy {
        max-width: 720px;
        margin: 0;
        color: var(--ink-soft);
        font-size: 1.15rem;
        line-height: 1.75;
    }

    .hero-band {
        display: grid;
        grid-template-columns: 1.4fr 0.9fr;
        gap: 1.2rem;
        margin-top: 2rem;
    }

    .mini-panel {
        padding: 1.2rem 1.25rem;
        border-radius: 22px;
        background: rgba(255,255,255,0.82);
        border: 1px solid rgba(20, 33, 61, 0.08);
    }

    .mini-panel h3 {
        margin: 0 0 0.7rem;
        color: var(--ink-strong);
        font-size: 1.05rem;
    }

    .mini-panel p,
    .mini-panel li {
        color: var(--ink-soft);
        font-size: 0.98rem;
        line-height: 1.6;
    }

    .mini-panel ul {
        margin: 0;
        padding-left: 1.1rem;
    }

    .stat-card {
        padding: 1.35rem 1.2rem;
        border-radius: 24px;
        background: var(--panel-strong);
        border: 1px solid var(--line);
        box-shadow: 0 14px 40px rgba(20, 33, 61, 0.08);
        min-height: 172px;
    }

    .stat-label {
        color: var(--ink-soft);
        font-size: 0.88rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .stat-value {
        margin-top: 0.9rem;
        color: var(--ink-strong);
        font-size: 2.4rem;
        line-height: 1;
        font-weight: 800;
        letter-spacing: -0.05em;
    }

    .stat-detail {
        margin-top: 0.85rem;
        color: var(--accent);
        font-size: 1rem;
        font-weight: 700;
    }

    .next-step {
        margin-top: 1.2rem;
        padding: 1.15rem 1.3rem;
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(217,243,239,0.95), rgba(227,241,255,0.95));
        border: 1px solid rgba(15, 118, 110, 0.14);
        color: var(--ink-strong);
        font-size: 1rem;
        line-height: 1.65;
        font-weight: 600;
    }

    @media (max-width: 900px) {
        .hero-shell {
            padding: 2rem 1.35rem;
        }

        .hero-band {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero-shell">
      <div class="eyebrow">AI Job Signal Layer</div>
      <h1 class="hero-title">SkillRadar</h1>
      <p class="hero-copy">
        Track what the AI and ML job market is actually asking for, compare that signal to your
        current skill stack, and turn gaps into a realistic learning roadmap before your next application cycle.
      </p>
      <div class="hero-band">
        <div class="mini-panel">
          <h3>What You Can Do Here</h3>
          <ul>
            <li>Monitor rising tools, frameworks, and role-specific demand.</li>
            <li>Analyze your resume or pasted skills against current market expectations.</li>
            <li>Generate a focused roadmap instead of guessing what to learn next.</li>
          </ul>
        </div>
        <div class="mini-panel">
          <h3>Best Starting Flow</h3>
          <p>Start with <strong>Resume Analyzer</strong> to see your fit score first, then open <strong>Market Dashboard</strong> and <strong>Skill Explorer</strong> to understand the market behind that result.</p>
        </div>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

cards = [
    ("Market View", "Live trends", "Skills and momentum"),
    ("Resume Fit", "0-100", "Gap score"),
    ("Roadmaps", "4-26 weeks", "Personalized plans"),
]

columns = st.columns(3)
for column, (label, value, detail) in zip(columns, cards, strict=True):
    with column:
        st.markdown(
            f"""
            <div class="stat-card">
              <div class="stat-label">{label}</div>
              <div class="stat-value">{value}</div>
              <div class="stat-detail">{detail}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <div class="next-step">
      Use the sidebar to start with Resume Analyzer, inspect the market benchmark behind your score,
      and generate a learning roadmap that matches current hiring demand.
    </div>
    """,
    unsafe_allow_html=True,
)
