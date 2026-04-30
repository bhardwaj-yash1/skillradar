"""Subscription endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.schemas.notifications import (
    SubscriptionCreateRequest,
    SubscriptionResponse,
    UnsubscribeResponse,
)
from backend.db import crud
from backend.dependencies import get_db

router = APIRouter()


@router.post("/subscribe", response_model=SubscriptionResponse, status_code=201)
async def subscribe(
    payload: SubscriptionCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> SubscriptionResponse:
    """Create or reactivate an email subscription."""
    existing = await crud.get_subscription_by_email(db, str(payload.email))
    if existing and existing.is_active:
        raise HTTPException(status_code=409, detail="subscription_exists")
    subscription = await crud.create_subscription(db, str(payload.email), payload.name, payload.role_filter)
    return SubscriptionResponse(
        email=subscription.email,
        role_filter=subscription.role_filter,
        is_active=subscription.is_active,
        unsubscribe_token=subscription.unsubscribe_token,
    )


@router.post("/unsubscribe/{token}", response_model=UnsubscribeResponse)
async def unsubscribe(token: str, db: AsyncSession = Depends(get_db)) -> UnsubscribeResponse:
    """Deactivate a subscription by token."""
    success = await crud.deactivate_subscription(db, token)
    return UnsubscribeResponse(success=success)
