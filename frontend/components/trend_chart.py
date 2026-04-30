"""Trend chart helpers."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


def render_trend_chart(
    points: list[dict],
    title: str,
    comparison_points: list[dict] | None = None,
    primary_label: str = "Selected Role",
    comparison_label: str = "All Roles",
) -> go.Figure:
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
            name=primary_label,
            line=dict(color="#0f766e", width=3),
            hovertemplate="%{x}<br>Demand share: %{y:.1f}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=frame["week_start"],
            y=frame["moving_average"],
            mode="lines",
            name="3-Week Avg",
            line=dict(color="#f97316", dash="dash"),
            hovertemplate="%{x}<br>3-week avg: %{y:.1f}%<extra></extra>",
        )
    )

    if comparison_points:
        comparison_frame = pd.DataFrame(comparison_points)
        if not comparison_frame.empty:
            fig.add_trace(
                go.Scatter(
                    x=comparison_frame["week_start"],
                    y=comparison_frame["frequency_pct"],
                    mode="lines",
                    name=comparison_label,
                    line=dict(color="#64748b", width=2, dash="dot"),
                    hovertemplate="%{x}<br>Overall market: %{y:.1f}%<extra></extra>",
                )
            )

    fig.update_layout(
        title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Week",
        yaxis_title="Share of tracked postings (%)",
        legend_title_text="Series",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig
