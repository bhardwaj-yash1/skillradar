"""Trend and dashboard analytics."""

from __future__ import annotations

from collections import defaultdict

from backend.db.models import SkillFrequency


class TrendAnalyzer:
    """Compute dashboard-friendly views from weekly skill frequencies."""

    def top_skills(self, rows: list[SkillFrequency], limit: int = 20) -> list[SkillFrequency]:
        """Return rows sorted by frequency descending."""
        return sorted(rows, key=lambda row: (-row.frequency_pct, -row.count))[:limit]

    def compute_velocity(self, rows: list[SkillFrequency]) -> dict[str, float]:
        """Compute simple first-to-last velocity per skill."""
        grouped: dict[str, list[SkillFrequency]] = defaultdict(list)
        for row in sorted(rows, key=lambda row: (row.skill_name, row.week_start)):
            grouped[row.skill_name].append(row)
        return {
            skill: round(points[-1].frequency_pct - points[0].frequency_pct, 2)
            for skill, points in grouped.items()
            if len(points) >= 2
        }

    def heatmap(self, rows: list[SkillFrequency], top_n: int = 20) -> dict:
        """Return a dense skills-by-week matrix."""
        ordered = self.top_skills(rows, limit=top_n)
        skills = []
        for row in ordered:
            if row.skill_name not in skills:
                skills.append(row.skill_name)
        weeks = sorted({row.week_start.isoformat() for row in rows})
        matrix: list[list[float]] = []
        for skill in skills:
            row_values = []
            for week in weeks:
                match = next(
                    (item.frequency_pct for item in rows if item.skill_name == skill and item.week_start.isoformat() == week),
                    0.0,
                )
                row_values.append(round(match, 2))
            matrix.append(row_values)
        return {"skills": skills, "weeks": weeks, "matrix": matrix}

    def market_summary(self, rows: list[SkillFrequency]) -> dict:
        """Compute summary cards for the dashboard."""
        if not rows:
            return {
                "total_postings": 0,
                "unique_skills": 0,
                "top_skill": None,
                "fastest_rising": None,
                "data_freshness_week": None,
            }
        latest_week = max(row.week_start for row in rows)
        latest_rows = [row for row in rows if row.week_start == latest_week]
        velocities = self.compute_velocity(rows)
        top_skill = self.top_skills(latest_rows, limit=1)[0].skill_name if latest_rows else None
        fastest = max(velocities, key=velocities.get) if velocities else None
        return {
            "total_postings": max((row.total_postings for row in latest_rows), default=0),
            "unique_skills": len({row.skill_name for row in latest_rows}),
            "top_skill": top_skill,
            "fastest_rising": fastest,
            "data_freshness_week": latest_week.isoformat(),
        }
