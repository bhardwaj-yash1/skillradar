"""Resume parsing and skill extraction."""

from __future__ import annotations

import io
import re
from pathlib import Path

from docx import Document
from pdfminer.high_level import extract_text

from backend.config import Settings
from backend.core.extraction.normalizer import CANONICAL_SKILLS, normalize_skills
from backend.utils.file_utils import ensure_directory, validate_file_size
from backend.utils.logging_config import get_logger

SKILL_PATTERNS = sorted(CANONICAL_SKILLS.keys(), key=len, reverse=True)


class ResumeParser:
    """Extract text and normalized skills from uploaded resumes."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)
        ensure_directory(settings.UPLOAD_DIR)

    def parse_bytes(self, filename: str, content: bytes) -> dict:
        """Parse uploaded bytes into text and normalized skills."""
        validate_file_size(len(content), self.settings.MAX_RESUME_SIZE_MB)
        suffix = Path(filename).suffix.lower()
        if suffix == ".pdf":
            try:
                text = extract_text(io.BytesIO(content))
            except Exception:
                text = content.decode("utf-8", errors="ignore")
        elif suffix == ".docx":
            document = Document(io.BytesIO(content))
            text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        else:
            raise ValueError("Unsupported resume format. Only PDF and DOCX are accepted.")
        skills = self.extract_skills_from_text(text)
        return {"text": text, "skills": skills}

    def extract_skills_from_text(self, text: str) -> list[str]:
        """Find skill mentions in plain text."""
        lowered = text.lower()
        found: list[tuple[int, str]] = []
        for pattern in SKILL_PATTERNS:
            regex = r"\b" + re.escape(pattern) + r"\b"
            match = re.search(regex, lowered)
            if match:
                found.append((match.start(), pattern))
        ordered = [pattern for _, pattern in sorted(found, key=lambda item: item[0])]
        return normalize_skills(ordered)
