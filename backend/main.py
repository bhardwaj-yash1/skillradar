"""FastAPI application entry point."""
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.v1.endpoints.scrape import set_scheduler_service
from backend.api.v1.router import api_router
from backend.config import get_settings
from backend.core.scheduler.job_scheduler import JobSchedulerService
from backend.db.database import init_db
from backend.utils.file_utils import ensure_directory
from backend.utils.logging_config import configure_logging, get_logger

settings = get_settings()
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application startup and shutdown."""
    ensure_directory(settings.UPLOAD_DIR)
    await init_db()
    scheduler_service = JobSchedulerService(settings)
    scheduler_service.start()
    set_scheduler_service(scheduler_service)
    logger.info("app_started")
    try:
        yield
    finally:
        await scheduler_service.shutdown()
        logger.info("app_stopped")


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def root_health() -> dict:
    """Container health endpoint."""
    return {"status": "ok"}
