# Metrics Catalog — VIP-DXB-CatalogBot

Что измерять, как собирать и какие пороги для алертов.
Все метрики привязаны к конкретным точкам в коде.

---

## Бизнес-метрики

### Bookings per Hour

**Что:** количество новых бронирований в час.

| Состояние | Диапазон | Действие |
|-----------|----------|---------|
| Normal | 5–20 | Ничего |
| Low alert | < 1 за 2 часа (рабочее время) | WARNING: возможно бот не работает |
| High alert | > 50 | WARNING: подозрение на тест-спам или DDoS |

**Где собирать:** в `data/database.py` метод `create_booking()` — инкрементировать Counter при успешной записи.

```python
# Пример: structlog при создании бронирования
logger.info("booking_created",
    platform=form_type,
    block_id=block_id,
    user_id=user_id,
)
```

**Как считать в реальном времени:**
```bash
docker logs catalog-bot-telegram --since=1h 2>&1 | grep '"event": "booking_created"' | wc -l
```

---

### Platform Breakdown

**Что:** распределение бронирований по платформам.

| form_type | Платформа |
|-----------|-----------|
| GT / PT / buggy / rent | Telegram |
| GT (с VK offset) | VK |
| IG_GT | Instagram |
| WA_GT | WhatsApp |
| FB_GT | Facebook |
| VB_GT | Viber |
| webapp | Mini App |

**Как использовать:** если одна платформа показывает 0 бронирований больше 4 часов в рабочее время → проверить health endpoint этой платформы.

---

### Search Queries

**Что:** количество поисковых запросов в час (regular + AI).

| Состояние | Диапазон |
|-----------|----------|
| Normal | 10–100 |
| AI search % | Обычно 20–40% от total |
| Alert | 0 за 1 час в рабочее время |

**Где:** `bot/handlers/search.py` — логировать при каждом вызове `search_blocks()` и `ai_assistant`.

---

## Технические метрики — Webhook

### Webhook Latency (p50/p95/p99)

**Что:** время ответа webhook endpoint от получения события до отправки 200 OK.

| Уровень | p50 | p95 | p99 |
|---------|-----|-----|-----|
| Target | < 100ms | < 500ms | < 1s |
| Warning | — | > 1s | > 2s |
| Critical | — | > 3s | > 5s |

**Почему важно:** Meta (IG/WA/FB) ждёт ответ 5 секунд. Если медленнее — начнёт retry, потом отключит webhook.

**Как собирать:** middleware в FastAPI app.py:
```python
@app.middleware("http")
async def track_request_time(request: Request, call_next):
    start = time.monotonic()
    response = await call_next(request)
    duration = time.monotonic() - start
    if duration > 3.0:
        logger.warning("slow_webhook", path=request.url.path, duration_s=round(duration, 3))
    return response
```

---

### Webhook Error Rate

**Что:** количество ошибок при обработке webhook-событий за 1 минуту.

| Состояние | Значение |
|-----------|----------|
| Normal | 0–2 |
| Warning | 3–4 |
| Critical | >= 5 |

**Cooldown для алерта:** 5 минут (избежать алерт-шторма при кратковременном всплеске).

**Где:** в обработчиках событий в `handlers/common.py` каждого webhook-бота.

---

## Технические метрики — Database

### DB Pool Utilization

**Что:** процент используемых соединений asyncpg connection pool.

| Состояние | % от max_size |
|-----------|--------------|
| Normal | 0–60% |
| Warning | 61–80% |
| Critical | > 80% |

**Формула:** `utilization = used_connections / max_size * 100`

**Как мониторить:**
```python
# В data/database.py — периодически вызывать
async def get_pool_utilization(self) -> float:
    if not self._pool:
        return 0.0
    used = self._pool.get_size() - self._pool.get_idle_size()
    return used / self._pool.get_max_size()
```

**Алерт при WARNING:** "DB pool 75% — проверить нет ли зависших запросов"
**Алерт при CRITICAL:** "DB pool 85% — риск TooManyConnectionsError"

---

### Slow Query Detection

**Что:** запросы к PostgreSQL, выполняющиеся дольше порога.

| Порог | Действие |
|-------|---------|
| > 1 сек | WARNING лог |
| > 3 сек | WARNING алерт в Telegram |
| > 10 сек | CRITICAL алерт + принудительный TERMINATE |

**Где:** обёртка в `data/database.py` (см. monitoring-observability SKILL.md → PostgreSQL Slow Query Logging).

---

### DB Connection State

**Нормальные состояния** (из `pg_stat_activity`):

| state | Что значит |
|-------|-----------|
| `active` | Запрос выполняется |
| `idle` | Соединение открыто, запроса нет |
| `idle in transaction` | Транзакция открыта, но запроса нет (опасно!) |

**Алерт:** если `idle in transaction` > 5 минут → CRITICAL (транзакция зависла, держит блокировки).

---

## Технические метрики — AI

### AI Token Usage

**Что:** процент использования дневного лимита токенов.

| Состояние | % от дневного лимита |
|-----------|---------------------|
| Normal | 0–70% |
| Warning | 71–85% |
| Critical | > 85% (риск quota exceeded до конца дня) |

**Как оценить лимит:** Google AI free tier — ~1M токенов/день для Gemini 2.5 Flash-Lite.

**Алерт:** "AI quota 87% использована — риск отключения AI поиска сегодня"

---

### AI Cost per Hour

**Что:** стоимость AI-запросов в USD за текущий час.

| Состояние | USD/час |
|-----------|---------|
| Normal | < $0.10 |
| Warning | $0.10–$0.50 |
| Critical | > $0.50 |

**Как считать:**
```bash
docker logs catalog-bot-telegram --since=1h 2>&1 | \
  python3 -c "
import sys, json
costs = []
for line in sys.stdin:
    try:
        d = json.loads(line)
        if 'cost_usd' in d:
            costs.append(float(d['cost_usd']))
    except: pass
print(f'Last hour AI cost: \${sum(costs):.4f}')
"
```

---

### AI Fallback Rate

**Что:** процент запросов, где Gemini не ответил и включился OpenAI fallback.

| Состояние | % fallback |
|-----------|-----------|
| Normal | 0–5% |
| Warning | 5–20% (Gemini нестабилен) |
| Critical | > 20% (Gemini недоступен) |

---

## Технические метрики — FSM

### Stale FSM Sessions

**Что:** FSM-сессии пользователей, которые не продвигались больше 30 минут (застрявшие формы).

| Состояние | Количество |
|-----------|-----------|
| Normal | 0–10 |
| Warning | > 20 |
| Alert action | Логировать user_id + state для ручной проверки |

**Почему важно:** stale sessions занимают память и могут указывать на UX-проблему (пользователи бросают форму на конкретном шаге).

---

## Технические метрики — System

### Container Memory Usage

**Как проверить:**
```bash
gcloud compute ssh tourist-bot --zone=europe-west3-b -- 'docker stats --no-stream'
```

| Контейнер | Warning | Critical |
|-----------|---------|---------|
| catalog-bot-telegram | > 512 MB | > 1 GB |
| catalog-bot-vk | > 256 MB | > 512 MB |
| catalog-bot-postgres | > 1 GB | > 2 GB |
| Webhook боты (каждый) | > 256 MB | > 512 MB |

### Disk Usage on tourist-bot

```bash
gcloud compute ssh tourist-bot --zone=europe-west3-b -- 'df -h /'
```

| Состояние | % диска |
|-----------|---------|
| Normal | 0–70% |
| Warning | 71–85% |
| Critical | > 85% (риск краша Docker при сборке) |

**Действие при Critical:** `docker system prune -f` (удалить неиспользуемые образы и контейнеры).

---

## Сводная таблица алертов

| Метрика | Warning | Critical | Cooldown |
|---------|---------|---------|---------|
| Webhook errors/min | 3 | 5 | 5 мин |
| Webhook latency p95 | > 1s | > 3s | 2 мин |
| DB pool utilization | > 80% | > 95% | 10 мин |
| Slow query | > 1s лог | > 3s алерт | 2 мин |
| AI cost/hour | > $0.10 | > $0.50 | 30 мин |
| AI quota % | > 85% | 429 response | 30 мин |
| Bookings/2h рабочий день | < 1 | — | 60 мин |
| Container memory | > 512 MB | > 1 GB | 15 мин |
| Disk % | > 80% | > 90% | 60 мин |
| Health check fails | — | 3 подряд | 5 мин |
