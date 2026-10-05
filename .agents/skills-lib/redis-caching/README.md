# redis-caching

Redis caching patterns для Python ботов и FastAPI.

## Файлы

- `SKILL.md` — основной скилл: обзор, режимы, паттерны, TTL стратегии, Docker Compose, типичные ошибки, quick reference
- `references/patterns-cookbook.md` — практические рецепты: connection pool, cache-aside декоратор, FSM session в Redis, webhook idempotency, cache invalidation при изменении каталога

## Когда использовать

- Оптимизация горячих callback-путей (тапы кнопок меню)
- Хранение FSM-состояний Instagram/WhatsApp/Facebook/Viber (замена in-memory)
- Дедупликация Meta webhook по `message.mid`
- Кэширование каталога (285 блоков) с инвалидацией из owner panel
- Rate limiting across multiple FastAPI workers
