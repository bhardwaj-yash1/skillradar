"""Base scraper abstractions."""

from __future__ import annotations

import asyncio
import random
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import uuid4

from backend.config import Settings
from backend.utils.logging_config import get_logger
from backend.utils.text_utils import strip_html

EXPERIENCE_RANGE_RE = re.compile(r"(?P<min>\d+)\s*[-to]+\s*(?P<max>\d+)\s+years?", re.IGNORECASE)
EXPERIENCE_PLUS_RE = re.compile(r"(?P<min>\d+)\s*\+\s*years?", re.IGNORECASE)
EXPERIENCE_SINGLE_RE = re.compile(r"(?P<value>\d+)\s+years?", re.IGNORECASE)


@dataclass
class RawJobPosting:
    """Raw scraper output before persistence."""

    external_id: str
    source: str
    url: str
    title: str
    company: str
    location: str
    raw_text: str
    experience_min: int | None = None
    experience_max: int | None = None


class BaseJobScraper(ABC):
    """Abstract base for all job scrapers."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)
        self._session_id = str(uuid4())

    @abstractmethod
    async def scrape(self, role: str, location: str, max_results: int) -> list[RawJobPosting]:
        """Return scraped job postings without raising on partial failures."""

    @abstractmethod
    def get_source_name(self) -> str:
        """Return the source identifier string."""

    async def _random_delay(self) -> None:
        delay = random.uniform(
            self.settings.SCRAPE_DELAY_MIN_SECONDS,
            self.settings.SCRAPE_DELAY_MAX_SECONDS,
        )
        await asyncio.sleep(delay)

    def _clean_text(self, text: str) -> str:
        """Normalize HTML-rich text into plain text."""
        return strip_html(text)

    def _extract_experience_range(self, text: str) -> tuple[int | None, int | None]:
        """Extract min and max years of experience from free text."""
        lowered = text.lower()
        if "fresher" in lowered:
            return 0, 0
        if match := EXPERIENCE_RANGE_RE.search(lowered):
            return int(match.group("min")), int(match.group("max"))
        if match := EXPERIENCE_PLUS_RE.search(lowered):
            return int(match.group("min")), None
        if match := EXPERIENCE_SINGLE_RE.search(lowered):
            value = int(match.group("value"))
            return value, value
        return None, None
