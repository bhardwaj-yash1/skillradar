"""API router composition."""

from fastapi import APIRouter

from backend.api.v1.endpoints import analyze, health, notifications, roadmap, scrape, skills

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(scrape.router, prefix="/scrape", tags=["scrape"])
api_router.include_router(skills.router, prefix="/skills", tags=["skills"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(roadmap.router, prefix="/roadmap", tags=["roadmap"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
