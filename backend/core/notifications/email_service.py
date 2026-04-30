"""Resend-backed email delivery service."""

from __future__ import annotations

try:
    import resend
except Exception:  # pragma: no cover - optional dependency during tests
    resend = None

from backend.config import Settings
from backend.utils.logging_config import get_logger


class EmailService:
    """Send transactional and digest emails through Resend."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)

    async def send_email(self, to_email: str, subject: str, html: str) -> bool:
        """Send an email or no-op when disabled."""
        if not self.settings.RESEND_API_KEY:
            self.logger.debug("email_disabled_missing_api_key")
            return True
        if resend is None:  # pragma: no cover
            self.logger.warning("resend_library_unavailable")
            return False
        resend.api_key = self.settings.RESEND_API_KEY
        resend.Emails.send(
            {
                "from": self.settings.EMAIL_FROM,
                "to": [to_email],
                "subject": subject,
                "html": html,
            }
        )
        return True
