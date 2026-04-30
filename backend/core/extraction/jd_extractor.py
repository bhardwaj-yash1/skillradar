"""LLM-backed and heuristic job description extraction."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable

from backend.config import Settings
from backend.core.extraction.function_schemas import job_description_extraction_tool
from backend.core.llm.client import build_async_llm_client
from backend.core.extraction.normalizer import CANONICAL_SKILLS, infer_category, normalize_skill
from backend.utils.logging_config import get_logger

KNOWN_ALIASES = sorted(CANONICAL_SKILLS.keys(), key=len, reverse=True)
OPTIONAL_SKILL_HINTS = (
    "nice to have",
    "good to have",
    "preferred",
    "plus",
    "bonus",
    "exposure to",
    "familiarity with",
)
REQUIRED_SKILL_HINTS = (
    "must have",
    "required",
    "strong experience in",
    "hands-on experience in",
    "proficient in",
    "expertise in",
    "experience with",
)
DOMAIN_HINTS = {
    "nlp": "natural_language_processing",
    "language model": "generative_ai",
    "llm": "generative_ai",
    "rag": "generative_ai",
    "computer vision": "computer_vision",
    "vision": "computer_vision",
    "recommendation": "recommendation_systems",
    "recommender": "recommendation_systems",
    "mlops": "mlops",
    "data pipeline": "data_engineering",
    "etl": "data_engineering",
}


class JobDescriptionExtractor:
    """Extract structured skill data from job description text."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)
        self.client = build_async_llm_client(settings) if settings.llm_enabled else None

    async def extract(self, raw_text: str) -> dict:
        """Extract normalized skills and metadata from a JD."""
        try:
            if self.settings.llm_enabled and self.client is not None:
                return await self._extract_with_openai(raw_text)
        except Exception as exc:  # pragma: no cover - graceful runtime fallback
            self.logger.warning(
                "llm_extraction_failed",
                provider=self.settings.LLM_PROVIDER,
                model=self.settings.llm_model,
                error=str(exc),
            )
        return self._extract_heuristically(raw_text)

    async def _extract_with_openai(self, raw_text: str) -> dict:
        response = await self.client.chat.completions.create(
            model=self.settings.llm_model,
            temperature=self.settings.safe_temperature,
            max_tokens=self.settings.LLM_MAX_TOKENS,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract structured hiring requirements from the job description. "
                        "Prefer concise, canonical skill names."
                    ),
                },
                {"role": "user", "content": raw_text[:12000]},
            ],
            tools=[job_description_extraction_tool()],
            tool_choice={"type": "function", "function": {"name": "extract_job_requirements"}},
        )
        arguments = response.choices[0].message.tool_calls[0].function.arguments
        payload = json.loads(arguments)
        payload["skills"] = self._normalize_skill_payload(payload.get("skills", []))
        return payload

    def _extract_heuristically(self, raw_text: str) -> dict:
        lowered = raw_text.lower()
        found = []
        sentences = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+|\n+", lowered) if segment.strip()]
        for alias in KNOWN_ALIASES:
            for match in re.finditer(r"\b" + re.escape(alias) + r"\b", lowered):
                canonical = normalize_skill(alias)
                context = next((sentence for sentence in sentences if alias in sentence), lowered)
                found.append(
                    {
                        "name": canonical,
                        "category": infer_category(canonical),
                        "is_required": self._classify_requirement(context),
                        "confidence": self._heuristic_confidence(alias, context),
                    }
                )
        normalized = self._normalize_skill_payload(found)
        return {
            "skills": normalized,
            "role_category": self._infer_role(raw_text),
            "experience_level": self._infer_experience_level(raw_text),
            "domain": self._infer_domain(raw_text),
        }

    def _normalize_skill_payload(self, skills: Iterable[dict]) -> list[dict]:
        deduped: list[dict] = []
        seen: set[str] = set()
        for skill in skills:
            name = normalize_skill(skill.get("name"))
            if not name or name in seen:
                continue
            deduped.append(
                {
                    "name": name,
                    "category": skill.get("category") or infer_category(name),
                    "is_required": bool(skill.get("is_required", True)),
                    "confidence": max(0.0, min(1.0, float(skill.get("confidence", 0.75)))),
                }
            )
            seen.add(name)
        return deduped

    def _infer_role(self, raw_text: str) -> str:
        lowered = raw_text.lower()
        if "data scientist" in lowered:
            return "data_scientist"
        if "llm" in lowered or "language model" in lowered:
            return "llm_engineer"
        if "machine learning engineer" in lowered or "ml engineer" in lowered:
            return "ml_engineer"
        return "ai_engineer"

    def _infer_experience_level(self, raw_text: str) -> str:
        lowered = raw_text.lower()
        if re.search(r"\b0[- ]?2 years|\bfresher\b", lowered):
            return "entry"
        if re.search(r"\b3[- ]?5 years|\bmid\b", lowered):
            return "mid"
        if re.search(r"\b6\+ years|\bsenior\b", lowered):
            return "senior"
        return "mid"

    def _classify_requirement(self, context: str) -> bool:
        """Infer whether a skill is required or optional from nearby context."""
        if any(hint in context for hint in OPTIONAL_SKILL_HINTS):
            return False
        if any(hint in context for hint in REQUIRED_SKILL_HINTS):
            return True
        return True

    def _heuristic_confidence(self, alias: str, context: str) -> float:
        """Assign a simple heuristic confidence score for fallback extraction."""
        confidence = 0.78
        if alias in {"pytorch", "tensorflow", "langchain", "kubernetes", "fastapi"}:
            confidence += 0.07
        if any(hint in context for hint in REQUIRED_SKILL_HINTS):
            confidence += 0.08
        if any(hint in context for hint in OPTIONAL_SKILL_HINTS):
            confidence -= 0.08
        return round(max(0.55, min(0.95, confidence)), 2)

    def _infer_domain(self, raw_text: str) -> str:
        """Infer a broad market domain from the full job description."""
        lowered = raw_text.lower()
        for hint, domain in DOMAIN_HINTS.items():
            if hint in lowered:
                return domain
        return "ai_ml"
