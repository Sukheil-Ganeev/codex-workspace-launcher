"""
core/alerts.py — Alert helper for VIP-DXB-CatalogBot.

Sends Telegram notifications to all OWNER_IDS via Bot API (no aiogram dependency).
Used by all 7 platforms: Telegram, VK, Instagram, WhatsApp, Facebook, Viber, Mini App.

Alert levels:
  INFO     — log only, no Telegram message
  WARNING  — Telegram message, non-urgent
  CRITICAL — Telegram message, marked CRITICAL, requires action

Cooldown mechanism prevents alert storms (same alert type won't repeat for N seconds).
"""

import os
import time
import httpx
import structlog

logger = structlog.get_logger("alerts")

CATALOG_BOT_TOKEN = os.getenv("CATALOG_BOT_TOKEN", "")
OWNER_IDS = [int(x) for x in os.getenv("OWNER_IDS", "").split(",") if x.strip()]

# In-memory cooldown tracker: key = "platform:metric_name" → last_alert_timestamp
_alert_cooldowns: dict[str, float] = {}

# Default cooldowns (seconds) by level
_DEFAULT_COOLDOWN = {
    "WARNING": 600,    # 10 minutes
    "CRITICAL": 300,   # 5 minutes
}


async def send_alert(
    level: str,
    message: str,
    platform: str = "system",
    cooldown_seconds: int | None = None,
    cooldown_key: str | None = None,
) -> bool:
    """
    Send an alert to all OWNER_IDS via Telegram Bot API.

    Args:
        level:            "INFO" | "WARNING" | "CRITICAL"
        message:          Alert text (plain or HTML)
        platform:         Platform name for log context (telegram, instagram, db, ai, ...)
        cooldown_seconds: Override default cooldown. None = use level default.
        cooldown_key:     Deduplicate key. Defaults to f"{platform}:{message[:30]}"

    Returns:
        True if message was sent (or would be sent for INFO level).
        False if suppressed by cooldown.
    """
    # INFO — log only, never send Telegram
    if level == "INFO":
        logger.info("alert_info", platform=platform, message=message[:200])
        return True

    # Cooldown check
    key = cooldown_key or f"{platform}:{message[:40]}"
    now = time.time()
    cooldown = cooldown_seconds if cooldown_seconds is not None else _DEFAULT_COOLDOWN.get(level, 600)
    last_sent = _alert_cooldowns.get(key, 0.0)

    if now - last_sent < cooldown:
        logger.debug("alert_suppressed_cooldown",
                     key=key,
                     remaining_s=int(cooldown - (now - last_sent)))
        return False

    _alert_cooldowns[key] = now

    # Build Telegram message
    if level == "CRITICAL":
        text = f"🚨 <b>CRITICAL</b> [{platform}]\n{message}"
    else:
        text = f"⚠️ <b>WARNING</b> [{platform}]\n{message}"

    if not CATALOG_BOT_TOKEN or not OWNER_IDS:
        logger.warning("alert_no_token_or_owners", level=level, platform=platform)
        return False

    logger.warning("alert_sent", level=level, platform=platform, message=message[:200])

    async with httpx.AsyncClient(timeout=10.0) as client:
        for owner_id in OWNER_IDS:
            try:
                await client.post(
                    f"https://api.telegram.org/bot{CATALOG_BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": owner_id,
                        "text": text,
                        "parse_mode": "HTML",
                    },
                )
            except Exception as exc:
                # Never raise — alerts must not crash the main process
                logger.error("alert_send_failed", owner_id=owner_id, error=str(exc)[:100])

    return True


# ---------------------------------------------------------------------------
# Pre-built alert helpers for common VIP-DXB-CatalogBot scenarios
# ---------------------------------------------------------------------------

async def webhook_error_alert(platform: str, error_count: int, last_error: str) -> None:
    """
    Alert when webhook error rate crosses threshold (5 errors/min).
    Cooldown: 5 minutes.
    """
    if error_count >= 5:
        await send_alert(
            level="CRITICAL",
            platform=platform,
            message=f"webhook_errors: {error_count} ошибок за последнюю минуту\nПоследняя: {last_error[:200]}",
            cooldown_seconds=300,
            cooldown_key=f"{platform}:webhook_errors",
        )
    elif error_count >= 3:
        await send_alert(
            level="WARNING",
            platform=platform,
            message=f"webhook_errors: {error_count} ошибок за последнюю минуту",
            cooldown_seconds=300,
            cooldown_key=f"{platform}:webhook_errors_warn",
        )


async def db_pool_alert(used: int, max_size: int) -> None:
    """
    Alert when asyncpg connection pool utilization is high.
    WARNING > 80%, CRITICAL > 95%.
    Cooldown: 10 minutes.
    """
    if max_size == 0:
        return
    utilization = used / max_size

    if utilization > 0.95:
        await send_alert(
            level="CRITICAL",
            platform="db",
            message=f"pool_exhaustion: {used}/{max_size} соединений ({utilization:.0%})\nРиск TooManyConnectionsError",
            cooldown_seconds=300,
            cooldown_key="db:pool_critical",
        )
    elif utilization > 0.80:
        await send_alert(
            level="WARNING",
            platform="db",
            message=f"pool_high_utilization: {used}/{max_size} ({utilization:.0%})",
            cooldown_seconds=600,
            cooldown_key="db:pool_warning",
        )


async def ai_quota_alert(provider: str, retry_after: int | None = None) -> None:
    """
    Alert when AI provider returns 429 (quota exceeded).
    Cooldown: 30 minutes.
    """
    retry_msg = f", retry_after={retry_after}s" if retry_after else ""
    await send_alert(
        level="WARNING",
        platform="ai",
        message=f"quota_exceeded: {provider}{retry_msg}\nAI поиск переключится на fallback",
        cooldown_seconds=1800,
        cooldown_key=f"ai:quota_{provider}",
    )


async def health_check_fail_alert(platform: str, port: int, fail_count: int) -> None:
    """
    Alert after 3 consecutive health check failures.
    Cooldown: 5 minutes.
    """
    if fail_count >= 3:
        await send_alert(
            level="CRITICAL",
            platform=platform,
            message=f"health_check_failed: порт {port}, {fail_count} раза подряд\nПроверить: docker ps на tourist-bot",
            cooldown_seconds=300,
            cooldown_key=f"{platform}:health_fail",
        )
