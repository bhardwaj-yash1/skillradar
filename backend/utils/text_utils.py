"""Text processing utilities."""

from __future__ import annotations

import re
from html import unescape

from bs4 import BeautifulSoup

WHITESPACE_RE = re.compile(r"\s+")


def strip_html(text: str) -> str:
    """Remove HTML tags and normalize whitespace."""
    if not text:
        return ""
    plain = BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
    plain = unescape(plain).encode("utf-8", errors="ignore").decode("utf-8")
    return normalize_whitespace(plain)


def normalize_whitespace(text: str) -> str:
    """Collapse repeated whitespace."""
    return WHITESPACE_RE.sub(" ", text or "").strip()
