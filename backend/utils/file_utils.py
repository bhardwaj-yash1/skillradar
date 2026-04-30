"""File helpers for uploads and parsing."""

from __future__ import annotations

from pathlib import Path


def ensure_directory(path: str | Path) -> Path:
    """Create a directory if missing and return the path."""
    resolved = Path(path)
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def validate_file_size(size_bytes: int, max_size_mb: int) -> None:
    """Raise ValueError when file size exceeds the configured limit."""
    max_bytes = max_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise ValueError(f"File exceeds maximum size of {max_size_mb} MB")
