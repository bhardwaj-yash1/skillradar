"""Trend chart helpers."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


def render_trend_chart(points: list[dict], title: str) -> go.Figure:
    """Create a line chart with a simple moving average overlay."""
    frame = pd.DataFrame(points)
    if frame.empty:
        return go.Figure()
    frame["moving_average"] = frame["frequency_pct"].rolling(window=min(3, len(frame)), min_periods=1).mean()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=frame["week_start"],
            y=frame["frequency_pct"],
            mode="lines+markers",
            name="Frequency",
            line=dict(color="#0f766e", width=3),
            fill="tozeroy",
            fillcolor="rgba(15,118,110,0.12)",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=frame["week_start"],
            y=frame["moving_average"],
            mode="lines",
            name="Moving Avg",
            line=dict(color="#f97316", dash="dash"),
        )
    )
    fig.update_layout(title=title, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig
