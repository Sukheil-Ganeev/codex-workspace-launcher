"""
core/logging_config.py — Structured JSON logging for all 7 VIP-DXB-CatalogBot platforms.

Features:
- JSON output (Docker-friendly: stdout → docker logs → jq)
- PII sanitization (phone numbers, passport numbers, card numbers)
- Correlation ID for tracing requests across Omni Inbox platforms
- Platform field in every log record
- Slow query detection hook

Usage in each bot's main.py / app.py:
    from core.logging_config import configure_logging, get_logger
    configure_logging(platform="instagram", json_output=True)
    logger = get_logger(__name__)

Log format (JSON):
    {
        "timestamp": "2026-03-12T10:00:00Z",
        "platform": "instagram",
        "event": "message_received",
        "level": "info",
        "user_id": -42,
        "correlation_id": "a1b2c3d4",
        "details": "..."
    }

Log filtering with jq on tourist-bot:
    docker logs catalog-bot-instagram --tail=200 2>&1 | jq 'select(.level == "error")'
    docker logs catalog-bot-telegram --since=1h 2>&1 | jq 'select(.event == "booking_created")'
    docker logs catalog-bot-telegram --since=1h 2>&1 | jq 'select(.event == "slow_query")'
"""

import re
import sys
import uuid
import logging
import structlog
from typing import Any

# --- PII sanitization patterns ---
_PHONE_RE = re.compile(r'\+?\d[\d\s\-\(\)]{7,}\d')
_PASSPORT_RE = re.compile(r'[A-Z]{1,2}\d{6,9}', re.IGNORECASE)
_CARD_RE = re.compile(r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b')


def sanitize_log(text: str, max_len: int = 500) -> str:
    """
    Mask PII (phones, passports, card numbers) in text before logging.
    Always apply to user-submitted input.
    """
    if not isinstance(text, str):
        return str(text)[:max_len]
    text = _PHONE_RE.sub('[PHONE]', text)
    text = _PASSPORT_RE.sub('[PASSPORT]', text)
    text = _CARD_RE.sub('[CARD]', text)
    return text[:max_len]


def _pii_processor(logger: Any, method: str, event_dict: dict) -> dict:
    """
    structlog processor: sanitize PII in 'text', 'message', 'user_input' fields.
    Added automatically by configure_logging().
    """
    for field in ("text", "message", "user_input", "query"):
        if field in event_dict and isinstance(event_dict[field], str):
            event_dict[field] = sanitize_log(event_dict[field])
    return event_dict


def configure_logging(
    platform: str = "unknown",
    log_level: str = "INFO",
    json_output: bool = True,
) -> None:
    """
    Configure structlog for a VIP-DXB-CatalogBot platform.

    Call once at bot startup, before any loggers are created.

    Args:
        platform:    Platform name added to every log record (telegram, instagram, etc.)
        log_level:   Logging level string (DEBUG/INFO/WARNING/ERROR)
        json_output: True = JSON (production/Docker), False = colored console (dev)
    """
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        _pii_processor,
        # Add platform to every record
        lambda _, __, ed: {**ed, "platform": ed.get("platform", platform)},
    ]

    if json_output:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
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
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structlog logger for a module.
    Use instead of logging.getLogger() for structured output.

    Example:
        logger = get_logger(__name__)
        logger.info("booking_created", block_id=42, user_id=123)
    """
    return structlog.get_logger(name)


# --- Correlation ID helpers (for Omni Inbox cross-platform tracing) ---

def bind_correlation_id(platform: str, user_id: int | None = None) -> str:
    """
    Generate a short correlation ID and bind it to the current async context.
    All subsequent log calls in this request will include correlation_id automatically.

    Returns the correlation_id string for passing to downstream calls.

    Example (in a webhook handler):
        corr_id = bind_correlation_id("instagram", synthetic_id)
        # ... process the event ...
        clear_correlation_id()
    """
    correlation_id = str(uuid.uuid4())[:8]
    structlog.contextvars.bind_contextvars(
        correlation_id=correlation_id,
        platform=platform,
        **({"user_id": user_id} if user_id is not None else {}),
    )
    return correlation_id


def clear_correlation_id() -> None:
    """Clear correlation context after request is complete."""
    structlog.contextvars.clear_contextvars()
