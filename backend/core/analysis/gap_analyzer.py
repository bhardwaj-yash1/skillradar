"""Semantic-ish gap analysis for resume skills versus market demand."""

from __future__ import annotations

from backend.core.extraction.normalizer import normalize_skill, normalize_skills
from backend.db.models import SkillFrequency


class GapAnalyzer:
    """Compare user skills to market demand and score the fit."""

    def similarity(self, candidate_skill: str, market_skill: str) -> float:
        """Return a normalized similarity score between two skills."""
        left = normalize_skill(candidate_skill)
        right = normalize_skill(market_skill)
        if not left or not right:
            return 0.0
        if left == right:
            return 1.0
        left_tokens = set(left.lower().split())
        right_tokens = set(right.lower().split())
        overlap = len(left_tokens & right_tokens)
        union = len(left_tokens | right_tokens)
        return round(overlap / union, 2) if union else 0.0

    def analyze(self, resume_skills: list[str], market_rows: list[SkillFrequency]) -> dict:
        """Build a structured gap analysis result."""
        normalized_resume = normalize_skills(resume_skills)
        strengths = []
        gaps = []
        weighted_total = 0.0
        weighted_hit = 0.0

        for row in sorted(market_rows, key=lambda item: item.frequency_pct, reverse=True):
            best_similarity = max(
                (self.similarity(skill, row.skill_name) for skill in normalized_resume),
                default=0.0,
            )
            weighted_total += row.frequency_pct
            if best_similarity >= 0.75:
                weighted_hit += row.frequency_pct
                status = "STRONG" if row.frequency_pct >= 25 else "PRESENT"
                strengths.append(
                    {
                        "skill_name": row.skill_name,
                        "category": row.category,
                        "market_frequency_pct": row.frequency_pct,
                        "similarity_score": best_similarity,
                        "status": status,
                        "reason": "Present in resume and aligns with market demand.",
                    }
                )
            else:
                status = "CRITICAL_GAP" if row.frequency_pct >= 40 else "RECOMMENDED_GAP"
                gaps.append(
                    {
                        "skill_name": row.skill_name,
                        "category": row.category,
                        "market_frequency_pct": row.frequency_pct,
                        "similarity_score": best_similarity,
                        "status": status,
                        "reason": "High demand skill is missing or only weakly represented.",
                    }
                )

        gap_score = round((weighted_hit / weighted_total) * 100, 2) if weighted_total else 0.0
        fit_label = "Excellent Fit" if gap_score >= 80 else "Good Fit" if gap_score >= 60 else "Needs Work"
        return {
            "gap_score": max(0.0, min(100.0, gap_score)),
            "fit_label": fit_label,
            "strengths": strengths,
            "gaps": gaps,
        }
