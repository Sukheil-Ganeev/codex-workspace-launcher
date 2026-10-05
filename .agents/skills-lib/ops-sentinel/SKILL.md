---
name: ops-sentinel
description: "Каждый деплой виден, каждый сбой алертится, каждый инцидент решён по runbook. Объединяет monitoring, security audit и incident response. Используй при деплое нового бота, настройке алертов, добавлении health checks, реакции на инцидент или post-deploy verification. Режимы: setup, deploy-verify, alert-design, incident, full."
license: Apache-2.0
metadata:
---
# Skill: ops-sentinel

**Каждый деплой виден. Каждый сбой алертится. Каждый инцидент решён по runbook.**

---

## Overview

VIP-DXB-CatalogBot — 7 ботов в продакшне на GCP VM `tourist-bot` (zone: `europe-west3-b`). Без мониторинга — слепые. При сбое непонятно где искать: в Telegram? В DB? В Meta API? На самой VM?

**Ops-sentinel = видимость + реакция.**

```
Видимость:  structured logs → health checks → метрики
Реакция:    алерты → runbook → устранение за минуты, не часы
```

Скилл закрывает три пробела, которые оставались при раздельном использовании monitoring-observability и integration-guardian:

1. **Нет единого "deploy → verify → alert" pipeline** — знали как мониторить ИЛИ как проверять безопасность, но не было сквозного чеклиста после каждого push
2. **Нет post-deploy smoke test** — GitHub Actions зелёный, но боты реально работают?
3. **Guardian audit и observability setup смотрели на одно** (что может упасть), но с разных сторон и не были связаны

---

## When to Use

Активируй ops-sentinel когда:

- **Деплоишь новый бот** — mode `full`, получаешь setup + verify + alerts + runbook за один проход
- **Делаешь `git push origin main`** — mode `deploy-verify`, убеждаешься что всё поднялось
- **Добавляешь health check** к новому FastAPI webhook-серверу — mode `setup`
- **Настраиваешь алерты** для нового уровня ошибок или нового порога — mode `alert-design`
- **Что-то сломалось в production** — mode `incident`, получаешь нужный runbook с командами
- **Добавляешь Phase 22+ бот** — mode `full`, он включает security audit из guardian

---

## Modes

### Mode: `setup`

**Настроить structured logging + health check endpoints для всех 7 ботов.**

**Промт:**
```
ops-sentinel: setup / target: "Max Bot (порт 8085)"
```

**Что делает:**
1. Добавляет JSON structlog конфиг (`core/logging_config.py`) с PII-фильтром
2. Добавляет FastAPI `/health` endpoint с реальной DB-проверкой (`SELECT 1`)
3. Добавляет `healthcheck` в `docker-compose.prod.yml` для этого сервиса
4. Логирует correlation_id для трассировки через Omni Inbox

**Вывод:**
- `core/logging_config.py` — единая конфигурация для всех платформ
- `/health` endpoint в `app.py` нового бота
- Блок `healthcheck` для docker-compose

**Формат лога:**
```json
{"timestamp": "2026-03-12T10:00:00Z", "platform": "max_bot", "event": "message_received",
 "level": "info", "user_id": -4001, "correlation_id": "a1b2c3d4"}
```

**Шаблоны:** `assets/templates/health-endpoint.py`, `assets/templates/structlog-setup.py`

**После setup — предлагает:** `alert-design` для нового бота.

---

### Mode: `deploy-verify`

**Post-deploy smoke test. Объединяет guardian security audit + observability health checks.**

**Промт:**
```
ops-sentinel: deploy-verify / after: "Phase 22 Max Bot push to main"
```

**Что делает:**
1. **Security layer** (из integration-guardian `audit`):
   - Проверяет что секреты в `.env`, не в коде
   - Проверяет HMAC на всех `/webhook/*` endpoints нового бота
   - Проверяет нет CVE-блокеров в новых зависимостях
2. **Functional layer** (из monitoring-observability `health`):
   - GitHub Actions workflow завершён зелёным?
   - `docker ps` — все контейнеры Up?
   - Health endpoints отвечают для всех 7 ботов?
   - Первые 5 минут логов чистые?
3. **Business layer**:
   - Тестовое сообщение/бронирование прошло?
   - Telegram notify менеджеру пришёл?

**Вывод:**
```
deploy-verify: Phase 22 Max Bot
[OK]  GitHub Actions: green (run #142)
[OK]  docker ps: 8 контейнеров Up
[OK]  health: instagram:8081 ok, whatsapp:8082 ok, ...
[WARN] max_bot:8085 — /health возвращает 503 (DB check failed)
→ переход к incident: db-pool-exhausted
```

**Если найдена проблема:** автоматически предлагает нужный `incident` runbook.

**Чеклист:** `assets/checklists/post-deploy-verify.md`

---

### Mode: `alert-design`

**Создать правила алертов через Telegram Bot API notify.**

**Промт:**
```
ops-sentinel: alert-design / bot: "Max Bot"
```

**Что делает:**
1. Генерирует правила в `core/alerts.py` для нового бота
2. Добавляет конкретные пороги под тип бота (webhook/polling)
3. Настраивает cooldown чтобы не спамить OWNER_IDS
4. Связывает CVE-алерты из guardian deps с alert rules (если найдены критические CVE)

**Пороги (стандартные для VIP-DXB-CatalogBot):**

| Событие | Порог | Cooldown | Уровень |
|---------|-------|----------|---------|
| Webhook ошибки | 5 за 1 мин | 5 мин | CRITICAL |
| DB pool | > 80% | 10 мин | WARNING |
| DB pool | > 95% | 5 мин | CRITICAL |
| AI quota (Gemini) | HTTP 429 | 30 мин | WARNING |
| AI quota + OpenAI 429 | оба недоступны | 5 мин | CRITICAL |
| Health check fail | 3 подряд | 5 мин | CRITICAL |
| FSM зависшие сессии | > 30 мин неактивны | 15 мин | WARNING |
| Slow DB query | > 3 сек | 2 мин | WARNING |

**Уровни алертов:**
- `INFO` — логируется, не отправляется в Telegram
- `WARNING` — Telegram сообщение, но не срочно
- `CRITICAL` — Telegram сообщение с пометкой CRITICAL, ждёт реакции

**Шаблон:** `assets/templates/alert-rules.py`

**Synergy:** если guardian `deps` нашёл critical CVE → автоматически добавляется как security alert в alert-design.

---

### Mode: `incident`

**Активировать runbook по типу инцидента.**

**Промт:**
```
ops-sentinel: incident / type: "webhook-dead" / platform: "instagram"
```

**Что делает:**
Выдаёт пошаговый runbook с готовыми SSH-командами для конкретного типа инцидента.

**Типы инцидентов:**

| Тип | Симптом | Runbook |
|-----|---------|---------|
| `bot-down` | Telegram/VK не отвечает | RB-01 |
| `webhook-dead` | IG/WA/FB/Viber не получают события | RB-02 |
| `db-pool-exhausted` | asyncpg pool заполнен, бронирования не сохраняются | RB-03 |
| `ai-quota-exceeded` | Gemini/OpenAI 429, AI поиск не работает | RB-04 |
| `gcp-vm-unreachable` | SSH не работает, все боты упали | RB-05 |

**Полные runbooks:** `references/runbook-advanced.md`

**Быстрые команды диагностики (применимы к любому типу):**
```bash
# Статус всех контейнеров на tourist-bot
gcloud compute ssh tourist-bot --zone=europe-west3-b -- \
  'docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml ps'

# Health checks всех webhook-ботов
gcloud compute ssh tourist-bot --zone=europe-west3-b -- \
  'for port in 8080 8081 8082 8083 8084; do echo "=== Port $port ==="; curl -s localhost:$port/health; echo; done'

# Последние ошибки по всем контейнерам
gcloud compute ssh tourist-bot --zone=europe-west3-b -- \
  'docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml logs --tail=50 2>&1 | grep -i error'
```

**Synergy:** если `deploy-verify` обнаружил проблему — автоматически переходит к `incident` с нужным runbook.

---

### Mode: `full`

**Полный ops setup для нового бота с нуля.**

**Промт:**
```
ops-sentinel: full / new-bot: "Max Bot" / port: 8085
```

**Что делает:** выполняет setup → alert-design → deploy-verify последовательно.

**Последовательность:**

```
Шаг 1: setup
  └── structlog JSON logging для Max Bot
  └── /health endpoint (DB check + uptime + platform)
  └── docker-compose healthcheck блок
  └── correlation_id для трассировки

Шаг 2: alert-design
  └── core/alerts.py правила для Max Bot (порт 8085)
  └── Webhook error threshold → CRITICAL alert
  └── Health check 3x fail → CRITICAL alert
  └── CVE алерты если найдены deps-ом

Шаг 3: deploy-verify (после деплоя)
  └── Security: HMAC на /webhook/max, секреты в .env
  └── Functional: docker ps, health:8085, первые 5 мин логов
  └── Business: тестовый сценарий прошёл

Шаг 4: runbook в references/runbook-advanced.md
  └── Добавить RB-06: Max Bot специфичные инциденты
```

**Вывод:** готовый к production бот с полной ops-инфраструктурой за один проход.

---

## Internal Service Monitoring

Некоторые сервисы VIP-DXB-CatalogBot живут внутри Telegram polling-процесса и не имеют HTTP-портов: lead scoring, AI copilot, concierge. Для них нужны другие паттерны мониторинга.

### 1. Сервисы без HTTP-портов — structured metrics из кода

```python
# Pattern: emit structured metrics from internal services
import structlog
logger = structlog.get_logger()

async def calculate_lead_score(user_id: int) -> int:
    start = time.monotonic()
    try:
        score = await _compute(user_id)
        logger.info("lead_score_calculated",
            user_id=user_id, score=score,
            duration_ms=int((time.monotonic() - start) * 1000))
        return score
    except Exception:
        logger.exception("lead_score_failed", user_id=user_id)
        raise
```

### 2. AI cost tracking — токены и стоимость per-request

```python
# Pattern: track AI usage per provider
COST_PER_1K = {"gemini-2.5-flash-lite": 0.00005, "gpt-4o-mini": 0.00015}

async def track_ai_usage(model: str, input_tokens: int, output_tokens: int):
    total_tokens = input_tokens + output_tokens
    cost = (total_tokens / 1000) * COST_PER_1K.get(model, 0.0001)
    logger.info("ai_usage",
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=round(cost, 6))
```

### 3. Correlation ID tracing — трассировка через платформы

```python
# Pattern: bind correlation_id at webhook entry
import uuid
import structlog

async def process_webhook(data: dict):
    correlation_id = str(uuid.uuid4())[:8]
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    try:
        await route_event(data)
    finally:
        structlog.contextvars.clear_contextvars()
```

### 4. Алерты для AI и внутренних сервисов

| Метрика | Порог | Cooldown | Уровень |
|---------|-------|----------|---------|
| AI copilot latency p95 | > 5s | 10 мин | WARNING |
| AI daily cost | > $5 | 24h | WARNING |
| AI оба провайдера недоступны | consecutive failures | 5 мин | CRITICAL |
| AI token budget exceeded | per user per day | 1h | INFO |
| Lead score calculation failed | per batch | 5 мин | WARNING |
| Internal service exception rate | > 5/min | 5 мин | CRITICAL |

### 5. Runbook RB-10: Internal Service Degradation

```
Симптомы: Copilot возвращает "unavailable", scores устарели, concierge зависает
Диагностика:
  docker logs catalog-telegram-vk-prod --tail=50 | grep "ERROR\|exception\|failed"
  docker logs catalog-telegram-vk-prod | grep "ai_usage" | tail -5
  docker logs catalog-telegram-vk-prod | grep "lead_score" | tail -5
Исправление A: Restart Telegram контейнера (clears in-memory state)
Исправление B: Проверить AI API keys и квоты
Исправление C: Проверить PostgreSQL pool (internal services разделяют pool)
Превентивно: Structured logging + alert on exception rate
```

---

## Synergy Rules

Правила автоматических переходов между режимами:

| Триггер | Автоматическое действие |
|---------|------------------------|
| `deploy-verify` нашёл проблему | → `incident` с нужным runbook |
| guardian `deps` нашёл critical CVE | → добавляется как security alert в `alert-design` |
| `setup` завершён | → предлагает `alert-design` для нового бота |
| `full` запущен | → setup → alert-design → deploy-verify последовательно |
| `alert-design` создал WARNING | → проверить `incident` runbook для этого типа |
| Новый платформенный бот | → всегда использовать `full` |

**Ключевая связь deploy-verify + incident:**
Если `deploy-verify` показал `[WARN]` или `[FAIL]` — не останавливаться. Немедленно идти в `incident` с типом проблемы. Разрыва между обнаружением и устранением быть не должно.

**Ключевая связь guardian + alert-design:**
CVE из `integration-guardian deps` — это не просто обновление зависимостей. Критическая CVE должна стать security alert в `core/alerts.py`, чтобы при повторном деплое без исправления сигналить.

---

## Platform Map

Все 7 ботов VIP-DXB-CatalogBot — точки мониторинга:

| Бот | Порт | Тип | Health URL | Контейнер |
|-----|------|-----|-----------|-----------|
| Telegram | — | Long Poll | polling watchdog | catalog-bot-telegram |
| VK | — | Long Poll | polling watchdog | catalog-bot-vk |
| Instagram | 8081 | Webhook | http://localhost:8081/health | catalog-bot-instagram |
| WhatsApp | 8082 | Webhook | http://localhost:8082/health | catalog-bot-whatsapp |
| Facebook | 8083 | Webhook | http://localhost:8083/health | catalog-bot-facebook |
| Viber | 8084 | Webhook | http://localhost:8084/health | catalog-bot-viber |
| Mini App | 8080 | HTTP | http://localhost:8080/health | catalog-bot-miniapp |

**Проверить все сразу (на tourist-bot):**
```bash
for port in 8080 8081 8082 8083 8084; do
  result=$(curl -s -o /dev/null -w "%{http_code}" localhost:$port/health)
  echo "Port $port: $result"
done
```

**Long Poll боты (нет HTTP):**
```bash
# Telegram — проверить что контейнер жив и polling активен
docker logs catalog-bot-telegram --tail=20 | grep -E "polling|started|error"

# VK — проверить polling loop
docker logs catalog-bot-vk --tail=20 | grep -E "polling|longpoll|error"
```

---

## Quick Reference

| Режим | Когда | Промт | Результат |
|-------|-------|-------|-----------|
| `setup` | Новый бот/платформа | `setup / target: "Max Bot (8085)"` | structlog + /health + docker healthcheck |
| `deploy-verify` | После каждого git push | `deploy-verify / after: "Phase 22"` | Чеклист OK/WARN/FAIL + переход к incident |
| `alert-design` | Новые алерты/пороги | `alert-design / bot: "Max Bot"` | core/alerts.py правила + cooldown |
| `incident` | Что-то сломалось | `incident / type: "bot-down"` | Runbook с SSH командами |
| `full` | Новый бот с нуля | `full / new-bot: "Max Bot" / port: 8085` | setup + alerts + verify + runbook |

---

## Common Mistakes

### 1. Health check без реальной DB-проверки
**Проблема:** `/health` возвращает 200 даже когда asyncpg pool недоступен.
**Решение:** всегда делать `await db.fetchval("SELECT 1")` внутри health endpoint. Если ошибка — 503.

### 2. Алерт-шторм без cooldown
**Проблема:** при массовой ошибке 100+ алертов за секунду залит Telegram владельца.
**Решение:** использовать `alert_if_threshold()` с cooldown. Минимум 5 минут на тип ошибки.

### 3. deploy-verify = только GitHub Actions зелёный
**Проблема:** workflow зелёный, но контейнер поднялся в degrade-режиме (DB недоступна).
**Решение:** всегда проверять health endpoints и первые 5 минут логов — не только статус CI.

### 4. Incident без runbook → угадывание команд
**Проблема:** при сбое в панике набираешь команды наугад, теряешь 20-30 минут.
**Решение:** `incident / type: "..."` сразу даёт готовый набор команд из `references/runbook-advanced.md`.

### 5. Новый бот без `full` → пропущенные проверки
**Проблема:** добавили Max Bot, настроили webhook, задеплоили — но нет ни health check, ни алертов, ни runbook.
**Решение:** каждый новый бот начинается с `ops-sentinel: full`. Не "потом добавим мониторинг".
