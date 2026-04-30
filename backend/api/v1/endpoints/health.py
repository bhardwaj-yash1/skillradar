"""Health and readiness endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def healthcheck() -> dict:
    """Simple liveness endpoint."""
    return {"status": "ok"}
