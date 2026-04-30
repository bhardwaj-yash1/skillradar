"""Helpers for weekly digest content."""

from __future__ import annotations


class DigestBuilder:
    """Create email-friendly market updates."""

    def build(self, role_filter: str, summary: dict, rising: list[dict], falling: list[dict]) -> str:
        """Return a simple HTML digest."""
        rising_html = "".join(
            f"<li>{item['skill_name']}: {item['velocity']:+.1f} pts</li>" for item in rising[:5]
        )
        falling_html = "".join(
            f"<li>{item['skill_name']}: {item['velocity']:+.1f} pts</li>" for item in falling[:5]
        )
        return f"""
        <h1>SkillRadar Weekly Update</h1>
        <p>Role filter: <strong>{role_filter}</strong></p>
        <p>Total postings this week: <strong>{summary.get('total_postings', 0)}</strong></p>
        <p>Top skill: <strong>{summary.get('top_skill') or 'N/A'}</strong></p>
        <h2>Rising Skills</h2>
        <ul>{rising_html}</ul>
        <h2>Declining Skills</h2>
        <ul>{falling_html}</ul>
        """
