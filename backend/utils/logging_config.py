"""Structured logging helpers."""

from __future__ import annotations

import contextvars
import logging
import sys
from typing import Any

import structlog

from backend.config import get_settings

scrape_session_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "scrape_session_id",
    default=None,
)


def _add_callsite(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Expose common callsite attributes on every event."""
    event_dict["module"] = event_dict.pop("module", None)
    event_dict["function"] = event_dict.pop("func_name", None)
    return event_dict


def _inject_scrape_session(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Attach scrape session ID when present."""
    session_id = scrape_session_id.get()
    if session_id:
        event_dict["scrape_session_id"] = session_id
    return event_dict


def configure_logging() -> None:
    """Configure stdlib logging and structlog."""
    settings = get_settings()
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.MODULE,
                structlog.processors.CallsiteParameter.FUNC_NAME,
            }
        ),
        timestamper,
        _add_callsite,
        _inject_scrape_session,
    ]

    renderer: structlog.types.Processor
    if settings.DEBUG:
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a configured structlog logger."""
    return structlog.get_logger(name)
