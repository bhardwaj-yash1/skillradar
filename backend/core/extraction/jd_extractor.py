"""LLM-backed and heuristic job description extraction."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable

from backend.config import Settings
from backend.core.extraction.function_schemas import job_description_extraction_tool
from backend.core.llm.client import build_async_llm_client
from backend.core.extraction.normalizer import infer_category, normalize_skill
from backend.utils.logging_config import get_logger

KNOWN_ALIASES = [
    "python",
    "pytorch",
    "tensorflow",
    "fastapi",
    "langchain",
    "docker",
    "kubernetes",
    "sql",
    "aws",
    "azure",
    "gcp",
    "nlp",
    "rag",
    "transformers",
    "huggingface",
    "computer vision",
    "mlops",
    "scikit learn",
    "sklearn",
    "pandas",
    "numpy",
]


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
        for alias in KNOWN_ALIASES:
            if alias in lowered:
                canonical = normalize_skill(alias)
                found.append(
                    {
                        "name": canonical,
                        "category": infer_category(canonical),
                        "is_required": True,
                        "confidence": 0.8,
                    }
                )
        normalized = self._normalize_skill_payload(found)
        return {
            "skills": normalized,
            "role_category": self._infer_role(raw_text),
            "experience_level": self._infer_experience_level(raw_text),
            "domain": "ai_ml",
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
                    "confidence": float(skill.get("confidence", 0.75)),
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
