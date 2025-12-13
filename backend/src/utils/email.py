"""Simple email helper used for development/logging."""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str, cc: Optional[str] = None) -> None:
    """Log the email details (simulated send) and optionally mirror to cc."""
    log_message = (
        f"Simulated email -> To: {to}, Subject: {subject}\n"
        f"Body:\n{body}"
    )
    if cc:
        log_message += f"\nCC: {cc}"
    logger.info(log_message)

