"""Schemas for subscription endpoints."""

from __future__ import annotations

from pydantic import BaseModel


class SubscriptionCreateRequest(BaseModel):
    """Create or update a subscription."""

    email: str
    name: str | None = None
    role_filter: str = "all"


class SubscriptionResponse(BaseModel):
    """Serialized subscription response."""

    email: str
    role_filter: str
    is_active: bool
    unsubscribe_token: str


class UnsubscribeResponse(BaseModel):
    """One-click unsubscribe outcome."""

    success: bool
