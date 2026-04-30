"""Semantic-ish gap analysis for resume skills versus market demand."""

from __future__ import annotations

from backend.core.extraction.normalizer import normalize_skill, normalize_skills
from backend.db.models import SkillFrequency

RELATED_SKILL_HINTS = {
    "Natural Language Processing": {"Transformers", "Large Language Models", "Prompt Engineering"},
    "Large Language Models": {"Prompt Engineering", "Retrieval-Augmented Generation", "Vector Databases"},
    "PyTorch": {"Transformers", "Fine-Tuning", "Computer Vision"},
    "TensorFlow": {"Computer Vision", "MLOps"},
    "Docker": {"Kubernetes", "MLOps"},
    "Kubernetes": {"Docker", "MLOps"},
    "Retrieval-Augmented Generation": {"Vector Databases", "Large Language Models"},
    "Prompt Engineering": {"Large Language Models", "Retrieval-Augmented Generation"},
}


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
        exact_matches = 0
        adjacent_matches = 0

        for row in sorted(market_rows, key=lambda item: item.frequency_pct, reverse=True):
            best_similarity = max(
                (self.similarity(skill, row.skill_name) for skill in normalized_resume),
                default=0.0,
            )
            adjacency_score = self._adjacency_score(row.skill_name, normalized_resume)
            weighted_total += row.frequency_pct
            if best_similarity >= 0.95:
                exact_matches += 1
                weighted_hit += row.frequency_pct
                status = "STRONG" if row.frequency_pct >= 25 else "PRESENT"
                strengths.append(
                    {
                        "skill_name": row.skill_name,
                        "category": row.category,
                        "market_frequency_pct": row.frequency_pct,
                        "similarity_score": best_similarity,
                        "status": status,
                        "reason": "Strong direct match between your resume and current market demand.",
                    }
                )
            elif best_similarity >= 0.55 or adjacency_score >= 0.6:
                adjacent_matches += 1
                weighted_hit += row.frequency_pct * 0.65
                strengths.append(
                    {
                        "skill_name": row.skill_name,
                        "category": row.category,
                        "market_frequency_pct": row.frequency_pct,
                        "similarity_score": max(best_similarity, adjacency_score),
                        "status": "ADJACENT",
                        "reason": "You have nearby or transferable experience, but this skill is not yet a full direct match.",
                    }
                )
            else:
                status = "CRITICAL_GAP" if row.frequency_pct >= 40 else "RECOMMENDED_GAP"
                gaps.append(
                    {
                        "skill_name": row.skill_name,
                        "category": row.category,
                        "market_frequency_pct": row.frequency_pct,
                        "similarity_score": max(best_similarity, adjacency_score),
                        "status": status,
                        "reason": "This skill is underrepresented in your current profile relative to market demand.",
                    }
                )

        gap_score = round((weighted_hit / weighted_total) * 100, 2) if weighted_total else 0.0
        fit_label = (
            "Excellent Fit"
            if gap_score >= 80
            else "Good Fit"
            if gap_score >= 60
            else "Emerging Fit"
            if gap_score >= 40
            else "Needs Work"
        )
        return {
            "gap_score": max(0.0, min(100.0, gap_score)),
            "fit_label": fit_label,
            "strengths": sorted(strengths, key=lambda item: item["market_frequency_pct"], reverse=True),
            "gaps": sorted(gaps, key=lambda item: item["market_frequency_pct"], reverse=True),
            "summary": {
                "resume_skill_count": len(normalized_resume),
                "market_skill_count": len(market_rows),
                "exact_matches": exact_matches,
                "adjacent_matches": adjacent_matches,
                "critical_gaps": len([item for item in gaps if item["status"] == "CRITICAL_GAP"]),
            },
        }

    def _adjacency_score(self, market_skill: str, resume_skills: list[str]) -> float:
        """Estimate whether the resume contains related skills that partially cover the market skill."""
        related = RELATED_SKILL_HINTS.get(normalize_skill(market_skill), set())
        if not related:
            return 0.0
        normalized_resume = {normalize_skill(skill) for skill in resume_skills}
        overlap = len(related & normalized_resume)
        if overlap == 0:
            return 0.0
        return round(min(0.85, 0.45 + (overlap * 0.2)), 2)
