# performance-layer

Супер-скилл: горячие пути быстрые, webhook без дублей, каталог в памяти.

Объединяет `redis-caching`, `database-sql-справочник` и `integration-guardian` (webhook режим) в единый workflow.

## Когда использовать

- Callback кнопок меню дают видимую задержку
- FSM webhook-ботов (IG/WA/FB/Viber) теряется при деплое
- Одно сообщение клиента создаёт несколько бронирований
- Добавляешь Redis в проект с нуля
- Нужны метрики: cache hit rate, DLQ items, p95 latency

## Режимы

| Режим | Промт | Результат |
|-------|-------|-----------|
| `benchmark` | `performance-layer: benchmark / target: "callback меню"` | Таблица задержек + рекомендации |
| `cache-design` | `performance-layer: cache-design / what: "285 блоков"` | TTL таблица + инвалидация |
| `session-store` | `performance-layer: session-store / platforms: "IG, WA"` | RedisFSMManager drop-in |
| `webhook-dedup` | `performance-layer: webhook-dedup / platform: "instagram"` | Idempotency middleware |
| `monitoring` | `performance-layer: monitoring / scope: "все боты"` | Метрики + alerts |

## Файлы

```
SKILL.md                              — основная документация (500+ строк)
references/
  cache-strategies.md                 — L1+L2+L3 архитектура, invalidation, stampede
  redis-patterns.md                   — все паттерны: pool, @cached, FSM, lock, dedup
assets/
  templates/
    redis-fsm-manager.py              — RedisFSMManager drop-in замена core/fsm.py
    idempotency-middleware.py         — FastAPI middleware для webhook dedup
    cache-decorator.py                — @cached + async_lru_cache + batch operations
  docker/
    redis-compose.yml                 — Redis для docker-compose.prod.yml
```

## Источники

Объединяет знания из:
- `redis-caching/SKILL.md` + `references/patterns-cookbook.md`
- `integration-guardian/SKILL.md` (секция webhook)
- `database-sql-справочник` (indexing, optimization)
