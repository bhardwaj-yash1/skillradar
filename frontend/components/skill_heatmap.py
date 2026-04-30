"""Heatmap rendering component."""

from __future__ import annotations

import plotly.graph_objects as go


def render_skill_heatmap(payload: dict) -> go.Figure:
    """Create a skills-by-week heatmap figure."""
    fig = go.Figure(
        data=go.Heatmap(
            z=payload.get("matrix", []),
            x=payload.get("weeks", []),
            y=payload.get("skills", []),
            colorscale=[[0, "#f7f4ea"], [0.5, "#7aa37a"], [1, "#16302b"]],
            hovertemplate="Skill: %{y}<br>Week: %{x}<br>Demand share: %{z:.1f}%<extra></extra>",
            colorbar=dict(title="Demand %"),
        )
    )
    fig.update_layout(
        title="Tracked Skill Demand By Week",
        xaxis_title="Week",
        yaxis_title="Skill",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig
