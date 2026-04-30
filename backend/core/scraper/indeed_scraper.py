"""Indeed scraper implementation."""

from __future__ import annotations

import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from backend.core.scraper.base_scraper import BaseJobScraper, RawJobPosting


class IndeedScraper(BaseJobScraper):
    """Scrapes public Indeed search result pages."""

    BASE_URL = "https://in.indeed.com/jobs"

    def get_source_name(self) -> str:
        return "indeed"

    async def scrape(self, role: str, location: str, max_results: int) -> list[RawJobPosting]:
        params = {"q": role, "l": location, "fromage": "7"}
        headers = {"User-Agent": UserAgent().random if self.settings.SCRAPE_USER_AGENT_ROTATE else "Mozilla/5.0"}
        postings: list[RawJobPosting] = []
        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True, headers=headers) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            cards = soup.select("div.job_seen_beacon")
            for card in cards[:max_results]:
                anchor = card.select_one("h2 a")
                title = anchor.get_text(" ", strip=True) if anchor else "Unknown Role"
                href = anchor.get("href") if anchor else ""
                company = card.select_one("[data-testid='company-name']")
                location_node = card.select_one("[data-testid='text-location']")
                snippet = card.select_one("[data-testid='job-snippet']")
                text = self._clean_text(snippet.get_text(" ", strip=True) if snippet else "")
                exp_min, exp_max = self._extract_experience_range(text)
                external_id = card.get("data-jk") or href or title
                postings.append(
                    RawJobPosting(
                        external_id=external_id,
                        source=self.get_source_name(),
                        url=f"https://in.indeed.com{href}" if href and href.startswith("/") else href,
                        title=title,
                        company=company.get_text(" ", strip=True) if company else "Unknown Company",
                        location=location_node.get_text(" ", strip=True) if location_node else location,
                        raw_text=text,
                        experience_min=exp_min,
                        experience_max=exp_max,
                    )
                )
                await self._random_delay()
        except Exception as exc:  # pragma: no cover - network dependent
            self.logger.warning("indeed_scrape_failed", role=role, location=location, error=str(exc))
        return postings
