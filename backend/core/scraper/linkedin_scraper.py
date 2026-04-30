"""LinkedIn public jobs scraper implementation."""

from __future__ import annotations

import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from backend.core.scraper.base_scraper import BaseJobScraper, RawJobPosting


class LinkedInScraper(BaseJobScraper):
    """Scrapes LinkedIn's public jobs search pages."""

    BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    def get_source_name(self) -> str:
        return "linkedin"

    async def scrape(self, role: str, location: str, max_results: int) -> list[RawJobPosting]:
        params = {"keywords": role, "location": location, "start": 0}
        headers = {"User-Agent": UserAgent().random if self.settings.SCRAPE_USER_AGENT_ROTATE else "Mozilla/5.0"}
        postings: list[RawJobPosting] = []
        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True, headers=headers) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            cards = soup.select("li")
            for card in cards[:max_results]:
                anchor = card.select_one("a.base-card__full-link")
                title = card.select_one("h3")
                company = card.select_one("h4")
                location_node = card.select_one(".job-search-card__location")
                text = self._clean_text(card.get_text(" ", strip=True))
                exp_min, exp_max = self._extract_experience_range(text)
                external_id = card.get("data-entity-urn") or (anchor.get("href") if anchor else card.get_text())
                postings.append(
                    RawJobPosting(
                        external_id=external_id,
                        source=self.get_source_name(),
                        url=anchor.get("href") if anchor else "",
                        title=title.get_text(" ", strip=True) if title else role.title(),
                        company=company.get_text(" ", strip=True) if company else "Unknown Company",
                        location=location_node.get_text(" ", strip=True) if location_node else location,
                        raw_text=text,
                        experience_min=exp_min,
                        experience_max=exp_max,
                    )
                )
                await self._random_delay()
        except Exception as exc:  # pragma: no cover - network dependent
            self.logger.warning("linkedin_scrape_failed", role=role, location=location, error=str(exc))
        return postings
