"""Naukri scraper implementation."""

from __future__ import annotations

import json
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from slugify import slugify

from backend.core.scraper.base_scraper import BaseJobScraper, RawJobPosting


class NaukriScraper(BaseJobScraper):
    """Scrapes public Naukri result pages."""

    BASE_URL = "https://www.naukri.com"

    def get_source_name(self) -> str:
        return "naukri"

    async def scrape(self, role: str, location: str, max_results: int) -> list[RawJobPosting]:
        url = (
            f"{self.BASE_URL}/{slugify(role)}-jobs-in-{slugify(location)}"
            "?jobAge=7&k={role}&l={location}"
        ).format(role=quote_plus(role), location=quote_plus(location))
        headers = {"User-Agent": UserAgent().random if self.settings.SCRAPE_USER_AGENT_ROTATE else "Mozilla/5.0"}
        postings: list[RawJobPosting] = []
        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True, headers=headers) as client:
                response = await client.get(url)
                response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            script = soup.find("script", {"id": "__NEXT_DATA__"})
            if not script or not script.string:
                return postings
            data = json.loads(script.string)
            items = (
                data.get("props", {})
                .get("pageProps", {})
                .get("jobsData", {})
                .get("jobDetails", [])
            )
            for item in items[:max_results]:
                text = self._clean_text(item.get("jobDescription", ""))
                exp_min, exp_max = self._extract_experience_range(
                    f"{item.get('experienceText', '')} {text}"
                )
                postings.append(
                    RawJobPosting(
                        external_id=str(item.get("jobId") or item.get("jdURL") or item.get("title")),
                        source=self.get_source_name(),
                        url=item.get("jdURL", ""),
                        title=item.get("title", "Unknown Role"),
                        company=item.get("companyName", "Unknown Company"),
                        location=item.get("placeholders", [{}])[0].get("label", location),
                        raw_text=text,
                        experience_min=exp_min,
                        experience_max=exp_max,
                    )
                )
                await self._random_delay()
        except Exception as exc:  # pragma: no cover - network dependent
            self.logger.warning("naukri_scrape_failed", role=role, location=location, error=str(exc))
        return postings
