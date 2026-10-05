# FAQ: Notion API Справочник

> Данные актуальны на: 2026-02-15 | API Version: 2025-09-03

---

## Q1: Какой тариф Notion нужен для API?

Любой, включая Free. API доступен на всех планах. Rate limit одинаковый для всех -- 3 req/sec.

## Q2: Нужно ли платить за API отдельно?

Нет. Notion API входит в стоимость плана. Отдельной тарификации за API-запросы нет.

## Q3: Какую версию API использовать?

`2025-09-03` -- последняя актуальная. Указывается в заголовке `Notion-Version: 2025-09-03`. Эта версия ввела multi-source databases (breaking change).

## Q4: Чем Internal Integration отличается от Public?

| | Internal | Public (OAuth) |
|-|----------|---------------|
| Workspace | Только один | Любой (через OAuth) |
| Токен | Создаётся сразу | Получается через OAuth flow |
| Истекает? | Нет | Можно отозвать |
| Для кого | Свои автоматизации | Приложения для других пользователей |

Для бизнеса Сухейля достаточно Internal Integration.

## Q5: Как создать Internal Integration?

1. Перейди на https://www.notion.so/profile/integrations
2. "New integration" -> задай название, выбери workspace
3. Выбери capabilities (Read/Insert/Update content)
4. Скопируй токен (`ntn_***`)
5. В Notion расшарь нужные страницы/БД: Share -> Connections -> выбери интеграцию

## Q6: Почему интеграция не видит мою базу данных?

Страницы и БД должны быть **явно расшарены** с интеграцией. Создание интеграции не даёт автоматический доступ ко всему workspace. Расшарь через Share -> Connections.

## Q7: Как получить database_id?

**Из URL:** `https://www.notion.so/workspace/abc123def456...?v=...` -- часть после workspace/ и до `?` -- это ID.
**Из Search API:** `POST /v1/search` с filter `{ "property": "object", "value": "data_source" }`.
**Формат:** UUID (32 hex символа с дефисами или без).

## Q8: Максимум properties в базе данных?

Официального лимита на количество properties не документировано. Практически -- десятки свойств работают нормально. Ограничения: нельзя создать status через API, select options нельзя обновить через API.

## Q9: Можно ли создать view через API?

Нет. Views (Table, Board, Calendar, Gallery, Timeline, List) создаются только через UI Notion. API работает с данными, не с представлениями.

## Q10: Формат даты в API?

ISO 8601: `2026-02-15` (дата), `2026-02-15T10:00:00.000Z` (дата+время), `2026-02-15T10:00:00.000+04:00` (с timezone). Для диапазона: `{ "start": "...", "end": "..." }`.

## Q11: Можно ли загрузить файл через API?

Да, с помощью multi-part upload (файлы >20 MiB загружаются частями по 5-20 MiB). Через обычный API -- только external URL (`{ "type": "external", "external": { "url": "..." } }`). Через MCP -- загрузка файлов пока не поддерживается.

## Q12: Как подключить Notion MCP к Claude Code?

```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
```
Авторизация через OAuth -- всплывёт окно браузера для подтверждения доступа.

## Q13: Какие операции доступны через MCP?

16 tools: search, fetch страниц, create/update pages, move/duplicate pages, create database, update data source, query data sources, query database view, comments (create/get), teams, users. НЕ доступно: удаление БД, загрузка файлов, webhook-подписки, block-level комментарии.

## Q14: MCP бесплатный?

Да. Лимиты MCP = лимиты API (3 req/sec, 180 req/min).

## Q15: Как построить CRM в Notion?

1. Создай 4+ базы: Clients, Bookings, Products, Suppliers
2. Свяжи через Relations: Client -> Bookings -> Products
3. Добавь Rollups: Total Revenue (sum), Count Bookings, Last Booking
4. Настрой Views: Pipeline (Board), Calendar, Today (filtered Table)
5. Добавь Automations: Status changed -> Slack notification
6. Интегрируй Zapier/Make для внешних сервисов (Google Forms, WhatsApp)

## Q16: Можно ли принимать оплату через Notion?

Нет. Notion не имеет встроенной обработки платежей. Используй Notion для **трекинга** оплат (свойства Payment Status, Payment Method, Amount) и внешние сервисы для приёма (банк, Kaspi, Sber, крипто).

## Q17: Как интегрировать с WhatsApp?

Через сторонние платформы:
- **n8n** (self-hosted, бесплатно): Webhook Trigger -> Notion Create Database Item
- **Zapier:** WhatsApp Business trigger -> Notion action
- **Make.com:** WhatsApp module -> Notion module
- **Onlizer:** Прямая двусторонняя синхронизация Notion + WhatsApp Business

## Q18: Что такое Data Source в API v2025-09-03?

С версии 2025-09-03 Database = контейнер (title, icon, cover), Data Source = схема свойств + данные. Одна БД может иметь несколько data sources. В запросах на запись используй `data_source_id` вместо `database_id`. В ответах (read) возвращаются оба ID.

## Q19: Webhook или Polling -- что выбрать?

| Критерий | Webhook | Polling |
|----------|---------|---------|
| Задержка | < 1 мин | >= 2 мин |
| Надёжность | At-most-once | Гарантированная |
| Нагрузка API | Минимальная | Постоянная |
| Требования | HTTPS endpoint | Любой скрипт |

**Рекомендация:** Webhooks для production + Polling как fallback.

## Q20: Почему Search API не находит мою новую страницу?

Индексация асинхронная -- новые или недавно расшаренные страницы могут появиться в результатах с задержкой (до нескольких минут). Для поиска внутри конкретной БД используй `POST /databases/{id}/query` -- он работает сразу.
