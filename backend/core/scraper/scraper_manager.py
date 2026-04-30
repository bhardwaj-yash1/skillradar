"""Scrape orchestration for all sources."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import Settings
from backend.core.extraction.jd_extractor import JobDescriptionExtractor
from backend.core.scraper.base_scraper import RawJobPosting
from backend.core.scraper.indeed_scraper import IndeedScraper
from backend.core.scraper.linkedin_scraper import LinkedInScraper
from backend.core.scraper.naukri_scraper import NaukriScraper
from backend.db import crud
from backend.db.models import CompanyTier
from backend.utils.logging_config import get_logger

COMPANY_TIERS = {
    "google": CompanyTier.TIER1_MNC,
    "microsoft": CompanyTier.TIER1_MNC,
    "amazon": CompanyTier.TIER1_MNC,
    "meta": CompanyTier.TIER1_MNC,
    "tcs": CompanyTier.TIER2_MNC,
    "infosys": CompanyTier.TIER2_MNC,
    "wipro": CompanyTier.TIER2_MNC,
    "hcl": CompanyTier.TIER2_MNC,
}

SAMPLE_POSTINGS = [
    RawJobPosting(
        external_id="sample-ml-001",
        source="indeed",
        url="https://example.com/jobs/sample-ml-001",
        title="Machine Learning Engineer",
        company="Google",
        location="Bengaluru",
        raw_text=(
            "Build ML systems with Python, PyTorch, Docker, Kubernetes, AWS, NLP, and FastAPI. "
            "3-5 years experience required."
        ),
        experience_min=3,
        experience_max=5,
    ),
    RawJobPosting(
        external_id="sample-ai-002",
        source="linkedin",
        url="https://example.com/jobs/sample-ai-002",
        title="LLM Engineer",
        company="TCS",
        location="Remote",
        raw_text=(
            "Develop RAG pipelines with LangChain, Python, SQL, Transformers, Hugging Face, and Docker. "
            "5+ years experience."
        ),
        experience_min=5,
        experience_max=None,
    ),
]


class ScraperManager:
    """Run scrapers, deduplicate data, and trigger skill extraction."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)
        self.scrapers = {
            "naukri": NaukriScraper(settings),
            "indeed": IndeedScraper(settings),
            "linkedin": LinkedInScraper(settings),
        }
        self.extractor = JobDescriptionExtractor(settings)

    async def scrape_sources(
        self,
        role: str,
        location: str,
        max_results: int,
        sources: list[str] | None = None,
    ) -> list[RawJobPosting]:
        """Collect postings across requested sources."""
        requested = sources or list(self.scrapers.keys())
        postings: list[RawJobPosting] = []
        for source in requested:
            scraper = self.scrapers.get(source)
            if scraper is None:
                continue
            postings.extend(await scraper.scrape(role, location, max_results))
        if not postings:
            postings = SAMPLE_POSTINGS[: max_results or len(SAMPLE_POSTINGS)]
            self.logger.info("using_sample_postings", count=len(postings))
        return postings

    async def run_scrape_pipeline(
        self,
        db: AsyncSession,
        role: str,
        location: str,
        max_results: int,
        sources: list[str] | None = None,
    ) -> dict[str, int]:
        """Scrape postings, store new items, and extract skills."""
        postings = await self.scrape_sources(role, location, max_results, sources)
        new_postings = 0
        extracted_skill_count = 0

        for posting in postings:
            existing = await crud.get_job_posting_by_external_id(db, posting.external_id, posting.source)
            if existing:
                continue
            created = await crud.create_job_posting(
                db,
                {
                    "external_id": posting.external_id,
                    "source": posting.source,
                    "url": posting.url,
                    "title": posting.title,
                    "company": posting.company,
                    "company_tier": self.classify_company_tier(posting.company),
                    "location": posting.location,
                    "experience_min": posting.experience_min,
                    "experience_max": posting.experience_max,
                    "raw_text": posting.raw_text,
                    "scraped_at": datetime.now(timezone.utc),
                },
            )
            new_postings += 1
            payload = await self.extractor.extract(posting.raw_text)
            skill_rows = [
                {
                    "job_posting_id": created.id,
                    "skill_name": skill["name"],
                    "skill_raw": skill["name"],
                    "category": skill["category"],
                    "is_required": skill["is_required"],
                    "extraction_confidence": skill["confidence"],
                }
                for skill in payload.get("skills", [])
            ]
            if skill_rows:
                extracted_skill_count += await crud.bulk_create_skills(db, skill_rows)
            await crud.mark_posting_processed(db, created.id, datetime.now(timezone.utc))

        return {
            "scraped": len(postings),
            "new_postings": new_postings,
            "extracted_skills": extracted_skill_count,
        }

    def classify_company_tier(self, company_name: str) -> CompanyTier:
        """Classify a company into a coarse tier bucket."""
        lowered = company_name.lower()
        for company, tier in COMPANY_TIERS.items():
            if company in lowered:
                return tier
        if any(keyword in lowered for keyword in ("labs", "ai", "technologies", "startup")):
            return CompanyTier.STARTUP_FUNDED
        return CompanyTier.UNKNOWN
