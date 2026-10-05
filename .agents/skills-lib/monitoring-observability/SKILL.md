---
name: monitoring-observability
description: "Production monitoring и observability для Python ботов. Structured logging, health checks, Grafana дашборды, алерты. Используй при настройке мониторинга нового бота, отладке production-проблем, настройке алертов или создании runbook для инцидентов."
license: Apache-2.0
metadata:
---
# Skill: monitoring-observability

Production monitoring и observability для Python-ботов на базе VIP-DXB-CatalogBot.

---

## Overview

Observability строится на трёх уровнях:

```
Logs      → ЧТО произошло         (structlog / loguru → файлы / stdout)
Metrics   → СКОЛЬКО РАЗ и КОГДА   (Prometheus / Grafana)
Traces    → ПОЧЕМУ МЕДЛЕННО        (OpenTelemetry / Jaeger)
```

Для VIP-DXB-CatalogBot минимальный production-стек:
- **Logs** — structlog с JSON-форматом, ротация файлов
- **Health checks** — FastAPI `/health` на каждом webhook-сервере
- **Alerts** — Telegram-уведомления через Bot API (уже в проекте OWNER_IDS)
- **Metrics** — опционально Prometheus + Grafana на GCP VM

---

## When to Use

Активируй этот скилл когда:

- Настраиваешь мониторинг нового бота или платформы
- Бот перестал отвечать в production и нужен runbook
- Нужно добавить health check endpoints к webhook-серверам
- Настраиваешь алерты при превышении порогов ошибок
- Создаёшь Grafana дашборд для бизнес-метрик (бронирования, конверсия)
- Дебажишь медленные запросы к PostgreSQL
- Нужна трассировка запроса через несколько платформ (Omni Inbox)

---

## Modes

### Mode: setup

Настройка structured logging для Python бота.

**Пакеты:**
```
structlog>=24.0.0
python-json-logger>=2.0.0
```

**Базовая конфигурация structlog для VIP-DXB:**
```python
# core/logging_config.py
import logging
import structlog
import sys

def configure_logging(log_level: str = "INFO", json_output: bool = True):
    """
    Настраивает structlog для всех платформ VIP-DXB-CatalogBot.
    Формат: [platform] event: details
    """
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
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
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))

# Использование в main.py каждого бота:
# from core.logging_config import configure_logging
# configure_logging(json_output=True)
```

**Логгер в модуле:**
```python
import structlog
logger = structlog.get_logger(__name__)

# Формат проекта: [platform] event: details
await logger.ainfo("message_received",
    platform="instagram",
    user_id=-42,
    msg_id="abc123",
    text_length=len(text)
)
```

---

### Mode: health

Health check endpoints для всех 7 ботов VIP-DXB.

**FastAPI health endpoint (для IG/WA/FB/Viber/MiniApp):**
```python
# Добавить в каждый app.py
from fastapi import APIRouter
from data.database import db
import time

health_router = APIRouter()
_start_time = time.time()

@health_router.get("/health")
async def health_check():
    """
    Проверяет: процесс жив, DB доступна, время работы.
    Возвращает 200 OK или 503 если DB недоступна.
    """
    checks = {}

    # 1. DB check
    try:
        await db.fetchval("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)[:100]}"

    # 2. Uptime
    checks["uptime_seconds"] = int(time.time() - _start_time)

    # 3. Platform-specific
    checks["platform"] = "instagram"  # менять на платформу
    checks["status"] = "ok" if checks["database"] == "ok" else "degraded"

    status_code = 200 if checks["status"] == "ok" else 503
    return JSONResponse(content=checks, status_code=status_code)

# В app.py:
# app.include_router(health_router)
```

**Порты health endpoints:**
| Платформа     | URL                          |
|--------------|------------------------------|
| Instagram DM | http://localhost:8081/health  |
| WhatsApp     | http://localhost:8082/health  |
| Facebook     | http://localhost:8083/health  |
| Viber        | http://localhost:8084/health  |
| Mini App     | http://localhost:8080/health  |
| Telegram     | (long poll — нет HTTP)        |
| VK Bot       | (long poll — нет HTTP)        |

**Telegram / VK polling check (через watchdog):**
```python
# В bot/main.py — проверка что polling активен
import asyncio
_last_poll_time = 0.0

async def polling_watchdog():
    """Алертит если polling завис > 60 секунд."""
    while True:
        await asyncio.sleep(30)
        elapsed = time.time() - _last_poll_time
        if elapsed > 60 and _last_poll_time > 0:
            await notify_owner(f"[telegram] polling_stalled: {elapsed:.0f}s без событий")
```

---

### Mode: dashboard

Grafana дашборд для бизнес-метрик VIP-DXB-CatalogBot.

**Ключевые панели дашборда:**

1. **Bookings per hour** — новые бронирования по часам
2. **Platform breakdown** — Telegram / VK / Instagram / WhatsApp / Facebook / Viber
3. **Webhook latency** — p50 / p95 / p99 для каждого сервера
4. **DB pool utilization** — использование asyncpg connection pool
5. **AI search cost** — токены и стоимость Gemini / OpenAI
6. **Error rate** — ошибки по платформам

**Prometheus metrics endpoint (добавить в каждый FastAPI app):**
```python
# pip install prometheus-client
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
import time

# Метрики
bookings_total = Counter(
    "vip_dxb_bookings_total",
    "Total bookings created",
    ["platform", "form_type"]
)
webhook_latency = Histogram(
    "vip_dxb_webhook_duration_seconds",
    "Webhook request duration",
    ["platform", "event_type"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)
db_pool_size = Gauge(
    "vip_dxb_db_pool_size",
    "Current DB connection pool size"
)
errors_total = Counter(
    "vip_dxb_errors_total",
    "Total errors",
    ["platform", "error_type"]
)

# Middleware для замера latency
@app.middleware("http")
async def track_latency(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    webhook_latency.labels(
        platform="instagram",
        event_type=request.url.path
    ).observe(duration)
    return response

# Metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

**Grafana datasource конфиг (prometheus.yml на GCP VM):**
```yaml
scrape_configs:
  - job_name: 'vip-dxb-instagram'
    static_configs:
      - targets: ['localhost:8081']
  - job_name: 'vip-dxb-whatsapp'
    static_configs:
      - targets: ['localhost:8082']
  - job_name: 'vip-dxb-facebook'
    static_configs:
      - targets: ['localhost:8083']
  - job_name: 'vip-dxb-viber'
    static_configs:
      - targets: ['localhost:8084']
  - job_name: 'vip-dxb-miniapp'
    static_configs:
      - targets: ['localhost:8080']
```

---

### Mode: alerts

Правила алертов с Telegram-уведомлениями через Bot API.

**Alert helper (core/alerts.py):**
```python
# core/alerts.py
import httpx
import os
import asyncio
from typing import Optional

CATALOG_BOT_TOKEN = os.getenv("CATALOG_BOT_TOKEN", "")
OWNER_IDS = [int(x) for x in os.getenv("OWNER_IDS", "").split(",") if x.strip()]

async def notify_owner(message: str, parse_mode: str = "HTML") -> None:
    """
    Отправляет alert всем OWNER_IDS через Telegram Bot API.
    Используется для production-алертов из всех платформ.
    """
    if not CATALOG_BOT_TOKEN or not OWNER_IDS:
        return
    async with httpx.AsyncClient(timeout=10.0) as client:
        for owner_id in OWNER_IDS:
            try:
                await client.post(
                    f"https://api.telegram.org/bot{CATALOG_BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": owner_id,
                        "text": f"🚨 <b>ALERT</b>\n{message}",
                        "parse_mode": parse_mode,
                    }
                )
            except Exception:
                pass  # Alert не должен ронять основной процесс

async def alert_if_threshold(
    metric_name: str,
    current_value: float,
    threshold: float,
    platform: str = "unknown",
    cooldown_seconds: int = 300
) -> None:
    """Алертит если метрика превысила порог. Cooldown предотвращает спам."""
    # Реализация cooldown через простой dict в памяти
    key = f"{platform}:{metric_name}"
    last_alert = _alert_cooldowns.get(key, 0)
    if time.time() - last_alert < cooldown_seconds:
        return
    if current_value >= threshold:
        _alert_cooldowns[key] = time.time()
        await notify_owner(
            f"[{platform}] {metric_name}: {current_value:.1f} >= порога {threshold:.1f}"
        )

_alert_cooldowns: dict = {}
```

**Правила алертов для VIP-DXB:**

| Событие | Порог | Cooldown | Пример сообщения |
|---------|-------|----------|-----------------|
| Webhook ошибки | 5 за 1 мин | 5 мин | `[instagram] webhook_errors: 7 за последнюю минуту` |
| DB pool exhausted | pool_size >= 90% | 10 мин | `[db] pool_exhaustion: 18/20 connections` |
| Booking форма зависла | FSM > 30 мин | 15 мин | `[whatsapp] fsm_stale: user=-1042, state=WAITING_DATE, age=32min` |
| AI quota exceeded | HTTP 429 | 30 мин | `[ai] quota_exceeded: gemini-2.5-flash-lite, retry_after=60s` |
| VM недоступна | health check fail 3x | 5 мин | `[system] health_check_failed: instagram 3 раза подряд` |

**Мониторинг webhook ошибок:**
```python
# В обработчике webhook FastAPI:
_error_window: list[float] = []
ERROR_THRESHOLD = 5
ERROR_WINDOW_SECONDS = 60

async def track_webhook_error(platform: str, error: Exception):
    now = time.time()
    _error_window.append(now)
    # Чистим старые
    cutoff = now - ERROR_WINDOW_SECONDS
    while _error_window and _error_window[0] < cutoff:
        _error_window.pop(0)

    errors_in_window = len(_error_window)
    if errors_in_window >= ERROR_THRESHOLD:
        await notify_owner(
            f"[{platform}] webhook_errors: {errors_in_window} ошибок за {ERROR_WINDOW_SECONDS}s\n"
            f"Последняя: {type(error).__name__}: {str(error)[:200]}"
        )
```

---

### Mode: runbook

Шаблон runbook для производственных инцидентов. Полные шаблоны в `references/runbook-templates.md`.

**Структура runbook:**
```
## Инцидент: [название]
### Симптомы
### Диагностика (команды)
### Устранение
### Профилактика
```

**Быстрые диагностические команды для GCP VM tourist-bot:**
```bash
# Статус всех контейнеров
ssh tourist-bot 'docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml ps'

# Логи конкретного контейнера
ssh tourist-bot 'docker logs catalog-bot-instagram --tail=100'

# DB connections
ssh tourist-bot 'docker exec catalog-bot-postgres psql -U postgres -c "SELECT count(*), state FROM pg_stat_activity GROUP BY state"'

# Health checks
for port in 8080 8081 8082 8083 8084; do
  curl -s http://tourist-bot:$port/health | python3 -m json.tool
done
```

---

## Logging Patterns

### Формат проекта

Уже принятый в VIP-DXB-CatalogBot формат:
```
[platform] event: details
```

Примеры:
```
[telegram] booking_started: user=123456789, block_id=42, form_type=GT
[instagram] message_received: user=-42, msg_id=abc123, text_length=15
[whatsapp] fsm_transition: user=-1042, from=WAITING_NAME, to=WAITING_DATE
[omni] message_normalized: platform=viber, synthetic_id=-3001, event=text
[db] query_slow: table=bookings, duration=2.3s, query=get_bookings_by_date
[ai] search_completed: model=gemini-2.5-flash-lite, tokens=342, duration=0.8s
```

### Correlation ID

Для трассировки запроса через Omni Inbox (все 7 платформ):
```python
import uuid
import structlog

# В начале каждого входящего события
correlation_id = str(uuid.uuid4())[:8]

# Привязать к контексту
structlog.contextvars.bind_contextvars(
    correlation_id=correlation_id,
    platform="instagram",
    user_id=synthetic_id,
)

# Все последующие логи автоматически включат correlation_id
logger.info("booking_created", block_id=42)
# → {"correlation_id": "a1b2c3d4", "platform": "instagram", "event": "booking_created", ...}

# Очистить после завершения
structlog.contextvars.clear_contextvars()
```

### PII Sanitization

Убрать персональные данные из логов:
```python
import re

_PHONE_RE = re.compile(r'\+?\d[\d\s\-]{7,}\d')
_PASSPORT_RE = re.compile(r'[A-Z]{2}\d{6,9}', re.IGNORECASE)

def sanitize_log(text: str) -> str:
    """Маскирует телефоны и паспорта в тексте для логирования."""
    text = _PHONE_RE.sub('[PHONE]', text)
    text = _PASSPORT_RE.sub('[PASSPORT]', text)
    return text

# Использование при логировании пользовательского ввода:
logger.info("user_input_received",
    text=sanitize_log(user_text[:200]),  # ограничение длины
    platform="whatsapp"
)
```

### PostgreSQL Slow Query Logging

```python
# В data/database.py — обёртка для slow query detection
import time
import structlog

_SLOW_QUERY_THRESHOLD = 1.0  # секунды

async def _execute_with_timing(self, query: str, *args):
    start = time.monotonic()
    try:
        result = await self._pool.fetchval(query, *args)
        return result
    finally:
        duration = time.monotonic() - start
        if duration > _SLOW_QUERY_THRESHOLD:
            structlog.get_logger("db").warning(
                "slow_query",
                duration=round(duration, 3),
                query=query[:200],
            )
```

---

## Metrics

### Что измерять в VIP-DXB-CatalogBot

**Бизнес-метрики:**
| Метрика | Тип | Как собирать |
|---------|-----|-------------|
| bookings_per_hour | Counter | При создании bookings записи |
| bookings_by_platform | Counter + label | form_type = GT/IG_GT/WA_GT/FB_GT/VB_GT |
| search_queries_total | Counter | В bot/handlers/search.py |
| ai_search_tokens | Histogram | В core/services/ai_assistant.py |
| promo_codes_used | Counter | При применении промокода |

**Технические метрики:**
| Метрика | Тип | Порог для алерта |
|---------|-----|-----------------|
| webhook_latency_p95 | Histogram | > 2.0s |
| webhook_errors_per_min | Counter | > 5 |
| db_pool_active_connections | Gauge | > 80% pool_size |
| fsm_sessions_active | Gauge | > 1000 |
| ai_search_cost_per_hour | Counter | > $0.50 |

**Webhook latency цели:**
- p50: < 200ms
- p95: < 1s
- p99: < 2s
- Timeout SLA: < 5s (Meta webhook retry)

### AI Search Cost Tracking

```python
# В core/services/ai_adapter.py — после каждого AI вызова
async def _track_ai_cost(self, model: str, input_tokens: int, output_tokens: int):
    """Логирует стоимость AI запроса."""
    # Ориентировочные цены (проверяй актуальные)
    pricing = {
        "gemini-2.5-flash-lite": {"input": 0.000075, "output": 0.0003},  # per 1K tokens
        "gemini-2.5-flash": {"input": 0.00015, "output": 0.0006},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    }
    rates = pricing.get(model, {"input": 0.001, "output": 0.001})
    cost = (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1000

    structlog.get_logger("ai").info("request_completed",
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=round(cost, 6),
    )
```

### DB Pool Monitoring

```python
# В data/database.py — периодическая проверка pool
async def log_pool_stats(self):
    """Логирует статистику connection pool каждые 60 секунд."""
    if not self._pool:
        return
    stats = {
        "min_size": self._pool.get_min_size(),
        "max_size": self._pool.get_max_size(),
        "free": self._pool.get_idle_size(),
        "used": self._pool.get_size() - self._pool.get_idle_size(),
    }
    structlog.get_logger("db").info("pool_stats", **stats)

    # Алерт если pool почти заполнен
    utilization = stats["used"] / stats["max_size"] if stats["max_size"] > 0 else 0
    if utilization > 0.8:
        from core.alerts import notify_owner
        await notify_owner(
            f"[db] pool_high_utilization: {stats['used']}/{stats['max_size']} "
            f"({utilization:.0%})"
        )
```

---

## Common Mistakes

### 1. Логировать PII в production
**Проблема:** телефоны, паспорта, имена клиентов попадают в логи.
**Решение:** всегда применять `sanitize_log()` перед логированием пользовательского ввода.

### 2. Алерт-шторм без cooldown
**Проблема:** при массовой ошибке 100+ алертов за секунду заспамят владельца.
**Решение:** использовать `alert_if_threshold()` с cooldown. Минимум 5 минут.

### 3. Блокирующий logging в async handler
**Проблема:** `logging.info()` в async коде может блокировать event loop при записи в файл.
**Решение:** structlog с `asyncio`-совместимым handler или `logger.ainfo()`.

### 4. Health check без реальной DB проверки
**Проблема:** `/health` возвращает 200 даже когда DB недоступна.
**Решение:** в health check всегда делать `SELECT 1` к реальному pool.

### 5. Метрики только в памяти
**Проблема:** при рестарте контейнера все счётчики сбрасываются.
**Решение:** для критичных бизнес-метрик (bookings) — считать из DB, не из памяти.

### 6. Один лог-файл на все платформы
**Проблема:** невозможно фильтровать по платформе при дебаге.
**Решение:** использовать структурированные поля `platform=` в каждой записи и фильтровать через jq.

### 7. Игнорировать Meta webhook timeout
**Проблема:** Meta (Instagram/WhatsApp/Facebook) ждёт ответ 5 секунд, иначе retry.
**Решение:** webhook handler должен отвечать 200 немедленно, обработку делать фоново.

---

## Quick Reference

### Команды для дебага на GCP VM

```bash
# Войти на VM
gcloud compute ssh tourist-bot --zone=europe-west3-b

# Статус всех контейнеров
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml ps

# Логи с фильтром по платформе (structlog JSON)
docker logs catalog-bot-instagram --tail=200 2>&1 | python3 -m json.tool | grep '"platform": "instagram"'

# Или через jq (если установлен)
docker logs catalog-bot-instagram --tail=200 2>&1 | jq 'select(.platform == "instagram" and .level == "error")'

# Перезапустить конкретный сервис
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml restart instagram

# DB — активные запросы
docker exec catalog-bot-postgres psql -U postgres -c \
  "SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state \
   FROM pg_stat_activity WHERE (now() - pg_stat_activity.query_start) > interval '5 seconds';"

# Проверить health all webhooks
for port in 8080 8081 8082 8083 8084; do echo "Port $port:"; curl -s localhost:$port/health; echo; done
```

### structlog фильтрация

```bash
# Все ошибки за последний час
docker logs catalog-bot-telegram --since=1h 2>&1 | jq 'select(.level == "error")'

# Медленные запросы к DB
docker logs catalog-bot-telegram --since=1h 2>&1 | jq 'select(.event == "slow_query")'

# AI search запросы
docker logs catalog-bot-telegram --since=1h 2>&1 | jq 'select(.event == "request_completed") | {model, cost_usd, input_tokens}'

# Бронирования за день
docker logs catalog-bot-telegram --since=24h 2>&1 | jq 'select(.event == "booking_created")' | wc -l
```

### Добавление нового алерта — чеклист

- [ ] Определить метрику и порог
- [ ] Выбрать cooldown (минимум 5 мин)
- [ ] Использовать `notify_owner()` из `core/alerts.py`
- [ ] Проверить что алерт не блокирует основной поток
- [ ] Добавить в runbook-templates.md описание и шаги устранения
- [ ] Протестировать в dev перед деплоем

### Новый бот — чеклист мониторинга

- [ ] `configure_logging()` вызван при старте
- [ ] `/health` endpoint добавлен и проверяет DB
- [ ] Все webhook ошибки логируются с platform + error_type
- [ ] FSM-переходы логируются (from_state → to_state)
- [ ] Уведомление менеджеру при новом бронировании логируется
- [ ] Добавлен в prometheus.yml scrape_configs (если используется)
- [ ] Добавлен в runbook-templates.md
