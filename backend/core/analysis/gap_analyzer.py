"""Role-aware gap analysis for resume skills versus market demand."""

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
    "Apache Spark": {"PySpark", "Databricks", "SQL"},
    "Airflow": {"dbt", "SQL", "Data Pipelines"},
    "MLOps": {"Docker", "Kubernetes", "MLflow"},
}

ROLE_CORE_SKILLS = {
    "ai_engineer": {"Python", "Large Language Models", "Prompt Engineering", "FastAPI", "Docker"},
    "ml_engineer": {"Python", "PyTorch", "Scikit-learn", "Docker", "MLflow"},
    "llm_engineer": {"Python", "Large Language Models", "Prompt Engineering", "LangChain", "Vector Databases"},
    "data_scientist": {"Python", "SQL", "Scikit-learn", "Pandas", "Experimentation"},
    "mlops_engineer": {"Docker", "Kubernetes", "MLflow", "CI/CD", "AWS"},
    "data_engineer": {"Python", "SQL", "Apache Spark", "Airflow", "dbt"},
    "analytics_engineer": {"SQL", "dbt", "BI Reporting", "Data Modeling", "Python"},
    "computer_vision_engineer": {"Python", "PyTorch", "Computer Vision", "OpenCV", "MLOps"},
    "nlp_engineer": {"Python", "Natural Language Processing", "Transformers", "Prompt Engineering", "Large Language Models"},
    "applied_scientist": {"Python", "Experimentation", "Scikit-learn", "PyTorch", "SQL"},
}


class GapAnalyzer:
    """Compare user skills to a role-specific market benchmark and score the fit."""

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

    def analyze(self, resume_skills: list[str], market_rows: list[SkillFrequency], target_role: str = "all") -> dict:
        """Build a structured gap analysis result."""
        normalized_resume = normalize_skills(resume_skills)
        resume_set = set(normalized_resume)
        strengths: list[dict] = []
        gaps: list[dict] = []
        weighted_total = 0.0
        weighted_hit = 0.0
        exact_matches = 0
        adjacent_matches = 0
        exact_core_matches = 0
        adjacent_core_matches = 0
        matched_categories: set[str] = set()

        sorted_rows = sorted(market_rows, key=lambda item: item.frequency_pct, reverse=True)
        top_market_skills = {row.skill_name for row in sorted_rows[:6]}
        core_skills = ROLE_CORE_SKILLS.get(target_role, set()) | top_market_skills

        for row in sorted_rows:
            normalized_market_skill = normalize_skill(row.skill_name)
            best_similarity = max(
                (self.similarity(skill, row.skill_name) for skill in normalized_resume),
                default=0.0,
            )
            adjacency_score = self._adjacency_score(row.skill_name, normalized_resume)
            is_core_skill = normalized_market_skill in {normalize_skill(skill) for skill in core_skills}
            importance_weight = row.frequency_pct * (1.3 if is_core_skill else 1.0)
            weighted_total += importance_weight

            if best_similarity >= 0.95:
                exact_matches += 1
                if is_core_skill:
                    exact_core_matches += 1
                weighted_hit += importance_weight
                matched_categories.add(row.category)
                status = "STRONG" if row.frequency_pct >= 25 else "PRESENT"
                strengths.append(
                    {
                        "skill_name": row.skill_name,
                        "category": row.category,
                        "market_frequency_pct": row.frequency_pct,
                        "similarity_score": best_similarity,
                        "status": status,
                        "reason": self._strength_reason(row.skill_name, row.frequency_pct, is_core_skill, direct=True),
                    }
                )
            elif best_similarity >= 0.55 or adjacency_score >= 0.6:
                adjacent_matches += 1
                if is_core_skill:
                    adjacent_core_matches += 1
                weighted_hit += importance_weight * 0.65
                matched_categories.add(row.category)
                strengths.append(
                    {
                        "skill_name": row.skill_name,
                        "category": row.category,
                        "market_frequency_pct": row.frequency_pct,
                        "similarity_score": max(best_similarity, adjacency_score),
                        "status": "ADJACENT",
                        "reason": self._strength_reason(row.skill_name, row.frequency_pct, is_core_skill, direct=False),
                    }
                )
            else:
                status = "CRITICAL_GAP" if is_core_skill or row.frequency_pct >= 40 else "RECOMMENDED_GAP"
                gaps.append(
                    {
                        "skill_name": row.skill_name,
                        "category": row.category,
                        "market_frequency_pct": row.frequency_pct,
                        "similarity_score": max(best_similarity, adjacency_score),
                        "status": status,
                        "reason": self._gap_reason(row.skill_name, row.frequency_pct, is_core_skill),
                    }
                )

        raw_skill_coverage = round((weighted_hit / weighted_total) * 100, 2) if weighted_total else 0.0
        normalized_core_skills = {normalize_skill(skill) for skill in core_skills if normalize_skill(skill)}
        core_coverage_pct = (
            round(((exact_core_matches + (adjacent_core_matches * 0.6)) / len(normalized_core_skills)) * 100, 2)
            if normalized_core_skills
            else 0.0
        )
        market_categories = {row.category for row in sorted_rows}
        category_coverage_pct = (
            round((len(matched_categories) / len(market_categories)) * 100, 2) if market_categories else 0.0
        )
        gap_score = round(
            min(
                100.0,
                (raw_skill_coverage * 0.72) + (core_coverage_pct * 0.2) + (category_coverage_pct * 0.08),
            ),
            2,
        )

        fit_label = (
            "Interview Ready"
            if gap_score >= 82
            else "Strong Match"
            if gap_score >= 68
            else "Promising Fit"
            if gap_score >= 50
            else "Needs Work"
        )
        return {
            "gap_score": max(0.0, min(100.0, gap_score)),
            "fit_label": fit_label,
            "strengths": sorted(strengths, key=lambda item: item["market_frequency_pct"], reverse=True),
            "gaps": sorted(gaps, key=lambda item: item["market_frequency_pct"], reverse=True),
            "summary": {
                "resume_skill_count": len(resume_set),
                "market_skill_count": len(sorted_rows),
                "exact_matches": exact_matches,
                "adjacent_matches": adjacent_matches,
                "critical_gaps": len([item for item in gaps if item["status"] == "CRITICAL_GAP"]),
                "core_skill_coverage_pct": core_coverage_pct,
                "category_coverage_pct": category_coverage_pct,
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

    def _strength_reason(self, skill_name: str, frequency_pct: float, is_core_skill: bool, direct: bool) -> str:
        """Explain why a skill counts as a strength."""
        if direct and is_core_skill:
            return f"{skill_name} is a core hiring signal and already appears directly in your profile."
        if direct:
            return f"{skill_name} is showing up in {frequency_pct:.1f}% of postings and you already match it directly."
        if is_core_skill:
            return f"{skill_name} is a core benchmark skill; your adjacent experience is helpful but still needs direct evidence."
        return f"You have transferable evidence near {skill_name}, but recruiters would still expect a clearer direct signal."

    def _gap_reason(self, skill_name: str, frequency_pct: float, is_core_skill: bool) -> str:
        """Explain why a skill is treated as a gap."""
        if is_core_skill:
            return f"{skill_name} is a core benchmark for this role and is missing from your current profile."
        return f"{skill_name} appears in {frequency_pct:.1f}% of current postings and would materially improve role coverage."
