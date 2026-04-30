"""Roadmap generation helpers."""

from __future__ import annotations

from math import ceil


RESOURCE_MAP = {
    "framework": (
        {"title": "Official Docs", "url": "https://pytorch.org/tutorials/", "provider": "Docs"},
        {"title": "DeepLearning.AI", "url": "https://www.deeplearning.ai/", "provider": "DeepLearning.AI"},
    ),
    "language": (
        {"title": "Python Docs", "url": "https://docs.python.org/3/tutorial/", "provider": "Python"},
        {"title": "Educative", "url": "https://www.educative.io/", "provider": "Educative"},
    ),
    "tool": (
        {"title": "Hands-on Guide", "url": "https://docs.docker.com/get-started/", "provider": "Docker"},
        {"title": "KodeKloud", "url": "https://kodekloud.com/", "provider": "KodeKloud"},
    ),
    "cloud": (
        {"title": "Cloud Skills Boost", "url": "https://www.cloudskillsboost.google/", "provider": "Google"},
        {"title": "A Cloud Guru", "url": "https://www.pluralsight.com/cloud-guru", "provider": "A Cloud Guru"},
    ),
}


class RoadmapGenerator:
    """Create a phased learning roadmap from a gap analysis."""

    def generate(self, analysis_id: str, target_role: str, gaps: list[dict], total_weeks: int = 12) -> dict:
        """Generate a deterministic roadmap grouped into phases."""
        actionable = [gap for gap in gaps if gap["status"] in {"CRITICAL_GAP", "RECOMMENDED_GAP"}]
        if not actionable:
            return {"analysis_id": analysis_id, "target_role": target_role, "total_weeks": total_weeks, "phases": []}

        per_skill_weeks = max(1, ceil(total_weeks / max(1, len(actionable))))
        phases = []
        cursor = 1
        for index, gap in enumerate(actionable, start=1):
            end_week = min(total_weeks, cursor + per_skill_weeks - 1)
            free_resource, paid_resource = RESOURCE_MAP.get(
                gap["category"],
                (
                    {"title": "Community Tutorials", "url": "https://www.youtube.com/results?search_query=" + gap["skill_name"], "provider": "YouTube"},
                    {"title": "Structured Course", "url": "https://www.coursera.org/search?query=" + gap["skill_name"], "provider": "Coursera"},
                ),
            )
            phases.append(
                {
                    "phase_title": f"Phase {index}: Master {gap['skill_name']}",
                    "week_range": f"Weeks {cursor}-{end_week}",
                    "skills": [
                        {
                            "skill_name": gap["skill_name"],
                            "category": gap["category"],
                            "market_frequency_pct": gap["market_frequency_pct"],
                            "estimated_weeks": end_week - cursor + 1,
                            "free_resource": free_resource,
                            "paid_resource": paid_resource,
                            "project_idea": f"Build a mini {target_role.replace('_', ' ')} project using {gap['skill_name']}.",
                            "why_important": f"{gap['skill_name']} appears in {gap['market_frequency_pct']:.1f}% of current postings.",
                        }
                    ],
                }
            )
            cursor = end_week + 1
            if cursor > total_weeks:
                break
        return {"analysis_id": analysis_id, "target_role": target_role, "total_weeks": total_weeks, "phases": phases}
