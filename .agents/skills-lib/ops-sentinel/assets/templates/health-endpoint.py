"""
Health endpoint template for VIP-DXB-CatalogBot webhook bots.
Applies to: instagram_bot, whatsapp_bot, facebook_bot, viber_bot, miniapp.

Usage: Copy this into the app.py of your bot and add to the FastAPI app:
    app.include_router(health_router)

The endpoint checks:
- DB connection (SELECT 1 via asyncpg pool)
- Core tables are reachable
- Uptime and version
Returns 200 OK when healthy, 503 when DB is unavailable.
"""

import time
from fastapi import APIRouter
from fastapi.responses import JSONResponse

# Import the shared CatalogDB instance
from data.database import db

health_router = APIRouter()
_start_time = time.time()

# Set this to the name of your platform
PLATFORM_NAME = "instagram"  # change to: whatsapp, facebook, viber, miniapp


@health_router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Checks:
    1. Process is alive (this endpoint responding proves it)
    2. DB connection via asyncpg pool (SELECT 1)
    3. Core tables accessible (blocks table count)

    Returns:
        200 OK  — all checks passed
        503     — DB unavailable or critical check failed
    """
    checks: dict = {}
    overall_ok = True

    # --- Check 1: DB connection ---
    try:
        result = await db.fetchval("SELECT 1")
        if result == 1:
            checks["database"] = "ok"
        else:
            checks["database"] = "error: unexpected result"
            overall_ok = False
    except Exception as exc:
        checks["database"] = f"error: {str(exc)[:120]}"
        overall_ok = False

    # --- Check 2: Core table accessible ---
    if overall_ok:
        try:
            count = await db.fetchval("SELECT COUNT(*) FROM blocks WHERE is_active = TRUE")
            checks["catalog_blocks"] = int(count) if count is not None else 0
        except Exception as exc:
            checks["catalog_blocks"] = f"error: {str(exc)[:80]}"
            # Non-critical — don't flip overall_ok

    # --- Check 3: DB pool stats (if pool available) ---
    try:
        if hasattr(db, "_pool") and db._pool is not None:
            pool = db._pool
            pool_used = pool.get_size() - pool.get_idle_size()
            pool_max = pool.get_max_size()
            checks["db_pool"] = f"{pool_used}/{pool_max}"
            # Warn if pool is nearly full (but don't fail health check)
            if pool_max > 0 and pool_used / pool_max > 0.8:
                checks["db_pool_warning"] = "utilization > 80%"
    except Exception:
        pass  # Pool stats are optional; don't break health check

    # --- Uptime ---
    checks["uptime_seconds"] = int(time.time() - _start_time)
    checks["platform"] = PLATFORM_NAME
    checks["status"] = "ok" if overall_ok else "degraded"

    status_code = 200 if overall_ok else 503
    return JSONResponse(content=checks, status_code=status_code)


# --- How to add to your app.py ---
#
# from .health import health_router   (or inline in app.py)
# app.include_router(health_router)
#
# After that, the endpoint is available at:
#   http://localhost:808X/health
#
# Docker Compose healthcheck block (add to your service in docker-compose.prod.yml):
#
# healthcheck:
#   test: ["CMD", "curl", "-f", "http://localhost:8081/health"]
#   interval: 30s
#   timeout: 10s
#   retries: 3
#   start_period: 15s
#
# Adjust port (8081 for instagram, 8082 for whatsapp, 8083 for facebook, 8084 for viber, 8080 for miniapp)
