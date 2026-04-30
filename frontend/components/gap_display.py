"""Gap analysis rendering helpers."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_gap_gauge(score: float, label: str) -> go.Figure:
    """Render a fit-score gauge chart."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "/100"},
            title={"text": label},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#0f766e"},
                "steps": [
                    {"range": [0, 40], "color": "#fee2e2"},
                    {"range": [40, 70], "color": "#fef3c7"},
                    {"range": [70, 100], "color": "#dcfce7"},
                ],
            },
        )
    )
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def render_gap_scatter(strengths: list[dict], gaps: list[dict]) -> go.Figure:
    """Render the gap quadrant chart."""
    rows = strengths + gaps
    frame = pd.DataFrame(rows)
    if frame.empty:
        return go.Figure()
    colors = {
        "STRONG": "#15803d",
        "PRESENT": "#65a30d",
        "ADJACENT": "#0f766e",
        "CRITICAL_GAP": "#dc2626",
        "RECOMMENDED_GAP": "#f59e0b",
    }
    fig = go.Figure()
    for status, subset in frame.groupby("status"):
        fig.add_trace(
            go.Scatter(
                x=subset["market_frequency_pct"],
                y=subset["similarity_score"],
                mode="markers+text",
                text=subset["skill_name"],
                textposition="top center",
                name=status,
                marker=dict(size=14, color=colors.get(status, "#64748b")),
            )
        )
    fig.add_vline(x=30, line_dash="dash", line_color="#94a3b8")
    fig.add_hline(y=0.75, line_dash="dash", line_color="#94a3b8")
    fig.update_layout(
        title="Skill Gap Quadrant",
        xaxis_title="Market Frequency %",
        yaxis_title="Similarity Score",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_skill_lists(strengths: list[dict], gaps: list[dict]) -> None:
    """Render strengths and gaps side by side."""
    left, right = st.columns(2)
    with left:
        st.subheader("Your Strengths")
        for item in strengths:
            st.markdown(
                f"- **{item['skill_name']}** · {item['status']} · {item['market_frequency_pct']:.1f}% market demand"
            )
            st.caption(item["reason"])
    with right:
        st.subheader("Skills To Learn")
        for item in gaps:
            st.markdown(f"- **{item['skill_name']}** · {item['status']} · {item['market_frequency_pct']:.1f}%")
            st.caption(item["reason"])
