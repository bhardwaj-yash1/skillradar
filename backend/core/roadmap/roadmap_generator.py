"""Roadmap generation helpers."""

from __future__ import annotations

from math import ceil


RESOURCE_MAP = {
    "framework": (
        {"title": "Official Framework Docs", "url": "https://pytorch.org/tutorials/", "provider": "Docs"},
        {"title": "DeepLearning.AI Specializations", "url": "https://www.deeplearning.ai/", "provider": "DeepLearning.AI"},
    ),
    "language": (
        {"title": "Python Tutorial", "url": "https://docs.python.org/3/tutorial/", "provider": "Python"},
        {"title": "Educative Learning Path", "url": "https://www.educative.io/", "provider": "Educative"},
    ),
    "tool": (
        {"title": "Hands-on Product Docs", "url": "https://docs.docker.com/get-started/", "provider": "Docs"},
        {"title": "KodeKloud Labs", "url": "https://kodekloud.com/", "provider": "KodeKloud"},
    ),
    "cloud": (
        {"title": "Cloud Skills Boost", "url": "https://www.cloudskillsboost.google/", "provider": "Google"},
        {"title": "A Cloud Guru", "url": "https://www.pluralsight.com/cloud-guru", "provider": "A Cloud Guru"},
    ),
}

PHASE_TITLES = [
    "Foundation And Core Coverage",
    "Production Workflow Skills",
    "Portfolio And Interview Proof",
]


class RoadmapGenerator:
    """Create a phased learning roadmap from a gap analysis."""

    def generate(
        self,
        analysis_id: str,
        target_role: str,
        gaps: list[dict],
        strengths: list[dict] | None = None,
        total_weeks: int = 12,
    ) -> dict:
        """Generate a deterministic roadmap grouped into practical phases."""
        strengths = strengths or []
        actionable = [gap for gap in gaps if gap["status"] in {"CRITICAL_GAP", "RECOMMENDED_GAP"}][:6]

        if not actionable:
            actionable = [
                {
                    "skill_name": item["skill_name"],
                    "category": item["category"],
                    "market_frequency_pct": item["market_frequency_pct"],
                    "status": "BRIDGE_GAP",
                    "reason": item["reason"],
                }
                for item in strengths
                if item["status"] == "ADJACENT"
            ][:4]

        if not actionable:
            actionable = [
                {
                    "skill_name": item["skill_name"],
                    "category": item["category"],
                    "market_frequency_pct": item["market_frequency_pct"],
                    "status": "ADVANCE_STRENGTH",
                    "reason": item["reason"],
                }
                for item in strengths[:3]
            ]

        if not actionable:
            return {"analysis_id": analysis_id, "target_role": target_role, "total_weeks": total_weeks, "phases": []}

        phase_count = min(3, max(1, len(actionable)))
        skills_per_phase = ceil(len(actionable) / phase_count)
        weeks_per_phase = max(1, ceil(total_weeks / phase_count))

        phases = []
        phase_start_week = 1
        for phase_index in range(phase_count):
            phase_end_week = min(total_weeks, phase_start_week + weeks_per_phase - 1)
            phase_skills = actionable[phase_index * skills_per_phase : (phase_index + 1) * skills_per_phase]
            if not phase_skills:
                break

            rendered_skills = []
            for gap in phase_skills:
                free_resource, paid_resource = RESOURCE_MAP.get(
                    gap["category"],
                    (
                        {
                            "title": "Community Tutorials",
                            "url": "https://www.youtube.com/results?search_query=" + gap["skill_name"],
                            "provider": "YouTube",
                        },
                        {
                            "title": "Structured Course",
                            "url": "https://www.coursera.org/search?query=" + gap["skill_name"],
                            "provider": "Coursera",
                        },
                    ),
                )
                rendered_skills.append(
                    {
                        "skill_name": gap["skill_name"],
                        "category": gap["category"],
                        "market_frequency_pct": gap["market_frequency_pct"],
                        "estimated_weeks": phase_end_week - phase_start_week + 1,
                        "free_resource": free_resource,
                        "paid_resource": paid_resource,
                        "project_idea": self._project_idea(target_role, gap["skill_name"], phase_index),
                        "why_important": self._why_important(gap),
                    }
                )

            phases.append(
                {
                    "phase_title": f"Phase {phase_index + 1}: {PHASE_TITLES[phase_index]}",
                    "week_range": f"Weeks {phase_start_week}-{phase_end_week}",
                    "skills": rendered_skills,
                }
            )
            phase_start_week = phase_end_week + 1
            if phase_start_week > total_weeks:
                break

        return {"analysis_id": analysis_id, "target_role": target_role, "total_weeks": total_weeks, "phases": phases}

    def _project_idea(self, target_role: str, skill_name: str, phase_index: int) -> str:
        """Generate a project suggestion that feels realistic for hiring loops."""
        role_label = target_role.replace("_", " ")
        if phase_index == 0:
            return f"Ship a focused {role_label} mini-project that proves hands-on use of {skill_name}."
        if phase_index == 1:
            return f"Integrate {skill_name} into a production-style pipeline with tests, metrics, and deployment notes."
        return f"Create a recruiter-ready capstone that highlights {skill_name} in a portfolio case study or demo."

    def _why_important(self, gap: dict) -> str:
        """Explain the market signal behind the step."""
        if gap["status"] == "BRIDGE_GAP":
            return "This is close to your current experience, so converting it into direct evidence is high leverage."
        if gap["status"] == "ADVANCE_STRENGTH":
            return "You already have a base here, so the roadmap focuses on turning it into interview-ready proof."
        return f"{gap['skill_name']} appears in {gap['market_frequency_pct']:.1f}% of current postings and is a meaningful market gap."
