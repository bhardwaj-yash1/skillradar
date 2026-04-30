"""HTTP client helpers for the Streamlit app."""

from __future__ import annotations

import os
from typing import Any

import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_PREFIX = "/api/v1"


class APIClient:
    """Tiny wrapper around the SkillRadar backend API."""

    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url.rstrip("/")

    def _url(self, path: str) -> str:
        return f"{self.base_url}{API_PREFIX}{path}"

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        response = httpx.get(self._url(path), params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()

    def post(self, path: str, json: dict[str, Any] | None = None, files: dict | None = None, data: dict | None = None) -> Any:
        response = httpx.post(self._url(path), json=json, files=files, data=data, timeout=60.0)
        response.raise_for_status()
        return response.json()


api_client = APIClient()
