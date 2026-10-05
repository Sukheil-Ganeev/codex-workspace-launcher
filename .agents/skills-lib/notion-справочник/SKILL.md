---
name: notion-справочник
description: "Production-ready руководство по Notion API для туристического бизнеса ОАЭ. Триггеры - notion api, notion база, notion crm, notion интеграция."
---
# Notion API Справочник

> **Version:** 1.0 | **Created:** 2026-02-15 | **Last updated:** 2026-02-15 | **Next review:** 2026-05-15
> **API Version:** 2025-09-03 | **Base URL:** `https://api.notion.com/v1`

---

## 01. Обзор платформы, тарифы, лимиты

Notion -- платформа продуктивности (заметки, базы данных, wiki, проекты, AI). 100 млн+ пользователей, более 50% Fortune 100. REST API открыт для всех планов, включая Free.

### Тарифы (актуально на февраль 2026)

| План | Цена/user/мес | AI | Гости | Блоки (команда) | История |
|------|--------------|-----|-------|-----------------|---------|
| **Free** | $0 | Нет | 10 | 1,000 (solo -- unlimited) | 7 дней |
| **Plus** | $10 | Нет | 100 | Unlimited | 30 дней |
| **Business** | $20 | Встроен | 250 | Unlimited | 90 дней |
| **Enterprise** | Custom | Встроен | Custom | Unlimited | Unlimited |

> AI add-on ($8/мес) **отменён** с мая 2025. AI встроен только в Business и Enterprise. На Plus AI не доступен.

### Лимиты API

| Лимит | Значение |
|-------|----------|
| Rate limit | 3 req/sec на интеграцию (~2,700/15 мин) |
| Payload | Max 1,000 block elements, 500 KB |
| Массив блоков | Max 100 элементов за запрос |
| Пагинация | Cursor-based, max 100 записей/страница |
| Rich text | Max 2,000 символов на элемент, max 100 элементов в массиве |
| Файл (upload) | До 5 GB (multi-part >20 MiB) |
| Free блоки (команда) | 1,000 блоков + 3 дня grace period |

### Версия API 2025-09-03

Ключевое изменение: **multi-source databases**. Database = контейнер, Data Source = схема свойств. Заголовок обязателен:
```
Notion-Version: 2025-09-03
```

---

## 02. Аутентификация

### Internal Integration (для одного workspace)

1. Создать на https://www.notion.so/profile/integrations
2. Скопировать токен (формат `ntn_***`, ранее `secret_***`)
3. Расшарить нужные страницы/БД с интеграцией (Share > Connections)

```javascript
const { Client } = require("@notionhq/client");
const notion = new Client({ auth: process.env.NOTION_TOKEN });
```

### Public Integration (OAuth 2.0)

Для приложений, работающих с чужими workspace. Flow:

1. Redirect на `GET https://api.notion.com/v1/oauth/authorize?client_id=...&response_type=code&owner=user&redirect_uri=...`
2. Обмен code на токен: `POST https://api.notion.com/v1/oauth/token` (Basic Auth: base64 client_id:client_secret)
3. Использование: `Authorization: Bearer {access_token}`
4. Отзыв: `POST https://api.notion.com/v1/oauth/revoke`

> Internal tokens не истекают. OAuth tokens можно отозвать.

### Обязательные заголовки

| Заголовок | Значение |
|-----------|----------|
| `Authorization` | `Bearer {token}` |
| `Notion-Version` | `2025-09-03` |
| `Content-Type` | `application/json` |

### Capabilities (права интеграции)

| Capability | Описание |
|-----------|----------|
| Read content | Чтение страниц, БД, блоков |
| Insert content | Создание страниц, блоков |
| Update content | Обновление страниц, блоков, БД |
| Read/Insert comments | Работа с комментариями (отключены по умолчанию!) |
| Read user info | Список пользователей workspace |

> Принцип минимальных привилегий: запрашивай только нужные capabilities.

---

## 03. Databases API

### Endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| `POST` | `/databases` | Создать БД |
| `GET` | `/databases/{id}` | Получить БД |
| `PATCH` | `/databases/{id}` | Обновить контейнер БД (title, icon, cover) |
| `POST` | `/databases/{id}/query` | Запросить записи (deprecated, используй Data Source) |

> В API v2025-09-03 свойства БД управляются через Data Source endpoints. `PATCH /databases/{id}` обновляет только контейнер.

### Типы свойств (Property Types)

| Тип | Описание | Ключ конфигурации |
|-----|----------|------------------|
| `title` | Название записи | `{}` |
| `rich_text` | Текст | `{}` |
| `number` | Число (форматы: dollar, euro, percent...) | `{ "format": "dollar" }` |
| `select` | Выбор одного значения | `{ "options": [...] }` |
| `multi_select` | Множественный выбор | `{ "options": [...] }` |
| `date` | Дата/период | `{}` |
| `people` | Пользователи | `{}` |
| `files` | Файлы | `{}` |
| `checkbox` | Чекбокс | `{}` |
| `url` / `email` / `phone_number` | Контактные данные | `{}` |
| `formula` | Вычисляемое свойство | `{ "expression": "..." }` |
| `relation` | Связь с другой БД | `{ "data_source_id": "UUID" }` |
| `rollup` | Агрегация через relation | `{ "function": "sum", ... }` |
| `status` | Статус (нельзя создать через API!) | -- |
| `unique_id` | Автоинкремент с префиксом | `{ "prefix": "BOOK" }` |
| `place` | Геолокация (lat, lng, address) | `{}` |
| `created_time` / `last_edited_time` | Автодаты | `{}` |

### Query (запрос записей)

```javascript
const results = await notion.databases.query({
  database_id: "...",
  filter: {
    and: [
      { property: "Status", status: { equals: "Confirmed" } },
      { property: "Date", date: { on_or_after: "2026-02-15" } }
    ]
  },
  sorts: [{ property: "Date", direction: "ascending" }],
  page_size: 50,
});
```

### Операторы фильтров

| Тип свойства | Операторы |
|-------------|-----------|
| text/title | `contains`, `does_not_contain`, `equals`, `starts_with`, `ends_with`, `is_empty` |
| number | `equals`, `greater_than`, `less_than`, `greater_than_or_equal_to`, `is_empty` |
| date | `equals`, `before`, `after`, `on_or_before`, `on_or_after`, `past_week`, `next_month`... |
| select/status | `equals`, `does_not_equal`, `is_empty` |
| multi_select | `contains`, `does_not_contain`, `is_empty` |
| relation | `contains`, `does_not_contain` (UUID), `is_empty` |
| checkbox | `equals` (boolean) |

---

## 04. Pages и Blocks API

### Pages

| Метод | URL | Описание |
|-------|-----|----------|
| `POST` | `/pages` | Создать страницу (child page или запись в БД) |
| `GET` | `/pages/{id}` | Получить страницу |
| `PATCH` | `/pages/{id}` | Обновить свойства, icon, cover, archive |

```javascript
// Создание записи в БД "Клиенты"
const page = await notion.pages.create({
  parent: { database_id: DB_CLIENTS },
  properties: {
    Name: { title: [{ text: { content: "Иван Петров" } }] },
    Phone: { phone_number: "+971501234567" },
    Source: { select: { name: "Telegram" } },
    Status: { status: { name: "Lead" } },
  },
});
```

> Свойства >25 ссылок (relation, people) не возвращаются полностью в Retrieve Page -- используй dedicated property endpoint.

### Blocks

| Метод | URL | Описание |
|-------|-----|----------|
| `GET` | `/blocks/{id}/children` | Получить дочерние блоки |
| `PATCH` | `/blocks/{id}/children` | Добавить блоки (max 100, 2 уровня вложенности) |
| `PATCH` | `/blocks/{id}` | Обновить блок |
| `DELETE` | `/blocks/{id}` | Удалить блок (в корзину, восстановимо) |

**Типы блоков:** `paragraph`, `heading_1/2/3`, `bulleted_list_item`, `numbered_list_item`, `to_do`, `toggle`, `quote`, `callout`, `code`, `image`, `video`, `audio`, `pdf`, `file`, `bookmark`, `embed`, `table`, `table_row`, `divider`, `column_list`, `column`, `synced_block`

```javascript
// Добавить контент на страницу
await notion.blocks.children.append({
  block_id: pageId,
  children: [
    { heading_2: { rich_text: [{ text: { content: "Desert Safari" } }] } },
    { paragraph: { rich_text: [{ text: { content: "Описание тура..." } }] } },
  ],
});
```

> Обновление блока **заменяет полное значение** поля. Нельзя частично обновить rich_text.

---

## 05. Формулы, Relations, Rollups

### Формулы 2.0

80+ функций, 7 типов данных (string, number, boolean, date, list, person, page).

**Ключевые категории функций:**

| Категория | Примеры |
|----------|---------|
| Строки | `substring`, `contains`, `lower`, `upper`, `split`, `join`, `format`, `link`, `style` |
| Числа | `round`, `ceil`, `floor`, `abs`, `min`, `max`, `sum`, `toNumber` |
| Даты | `now`, `today`, `dateAdd`, `dateSubtract`, `dateBetween`, `formatDate`, `parseDate` |
| Логика | `if`, `ifs`, `empty`, `and`, `or`, `not` |
| Списки | `map`, `filter`, `sort`, `find`, `every`, `some`, `unique`, `flat`, `length` |
| Regex | `test`, `match`, `replace`, `replaceAll` |
| Переменные | `let(var, value, expr)`, `lets(v1, val1, v2, val2, ..., expr)` |

**Формулы для туризма ОАЭ:**

```
// Прибыль
prop("Price AED") - prop("Cost Price")

// Конвертация в AED
if(prop("Currency") == "USD", prop("Amount") * 3.67,
if(prop("Currency") == "RUB", prop("Amount") * 0.04,
if(prop("Currency") == "KZT", prop("Amount") * 0.007,
prop("Amount"))))

// Сезонная цена (High: Oct-Mar, Low: Apr-Sep)
if(month(now()) >= 10 or month(now()) <= 3,
  prop("Price High Season"), prop("Price Regular"))

// Статус дедлайна
if(empty(prop("Date")), "No date",
  if(prop("Date") < now(), "Overdue",
    if(dateBetween(prop("Date"), now(), "days") <= 1, "Tomorrow", "Upcoming")))
```

### Relations

| Тип | Описание | API |
|-----|----------|-----|
| One-way (`single_property`) | Связь видна только в исходной БД | `{ "data_source_id": "UUID" }` |
| Two-way (`dual_property`) | Связь видна в обеих БД | Создает synced property |

> Обе БД **обязаны** быть расшарены с интеграцией.

### Rollups (24 функции)

**Универсальные:** `count`, `count_values`, `unique`, `empty`, `not_empty`, `percent_empty`, `percent_not_empty`, `show_original`, `show_unique`
**Числовые:** `sum`, `average`, `median`, `min`, `max`, `range`
**Даты:** `earliest_date`, `latest_date`, `date_range`
**Checkbox:** `checked`, `unchecked`, `percent_checked`, `percent_unchecked`, `count_per_group`, `percent_per_group`

---

## 06. Search, Users, Comments API

### Search API

```javascript
const results = await notion.search({
  query: "Desert Safari",
  filter: { property: "object", value: "page" }, // или "data_source"
  sort: { direction: "descending", timestamp: "last_edited_time" },
});
```

**Ограничения:** Ищет только по заголовкам. Асинхронная индексация (задержка для новых страниц). Не гарантирует полный список. Для поиска внутри БД -- используй Query Database.

### Users API

| Endpoint | Описание | Capability |
|----------|----------|-----------|
| `GET /users` | Список пользователей (без гостей) | Read user info |
| `GET /users/{id}` | Один пользователь | Read user info |
| `GET /users/me` | Текущий бот | Любой (всегда работает) |

### Comments API

```javascript
// Создать комментарий к странице
await notion.comments.create({
  parent: { page_id: "..." },
  rich_text: [{ text: { content: "Бронирование подтверждено!" } }],
});

// Получить комментарии
const comments = await notion.comments.list({ block_id: pageId });
```

**Ограничения:** Нельзя редактировать/удалять/resolve комментарии через API. Max 3 вложения на комментарий. Capabilities отключены по умолчанию.

---

## 07. Notion SDK (JS/Python)

### JavaScript (@notionhq/client v5.9.0)

```bash
npm install @notionhq/client
```

| Фича | Значение |
|------|----------|
| Node.js | >= 18 |
| TypeScript | >= 5.9 |
| Retry | Встроенный (maxRetries: 2, exponential backoff) |
| Timeout | 60s (настраивается) |
| Namespaces | `databases`, `pages`, `blocks`, `users`, `search`, `comments`, `dataSources` |

```javascript
import { Client, isFullPage, collectPaginatedAPI } from "@notionhq/client";

const notion = new Client({ auth: process.env.NOTION_TOKEN });

// Автопагинация
const allPages = await collectPaginatedAPI(notion.databases.query, {
  database_id: "...",
});

// Error handling
import { isNotionClientError, APIErrorCode } from "@notionhq/client";
try {
  await notion.pages.retrieve({ page_id: "..." });
} catch (e) {
  if (isNotionClientError(e) && e.code === APIErrorCode.ObjectNotFound) {
    console.log("Страница не найдена или нет доступа");
  }
}
```

### Python (notion-client v2.7.0)

```bash
pip install notion-client
```

```python
from notion_client import Client, AsyncClient
from notion_client.helpers import collect_paginated_api

notion = Client(auth=os.environ["NOTION_TOKEN"])

# Автопагинация
all_pages = collect_paginated_api(notion.databases.query, database_id="...")

# Error handling
from notion_client import APIResponseError, APIErrorCode
try:
    notion.pages.retrieve(page_id="...")
except APIResponseError as e:
    if e.code == APIErrorCode.ObjectNotFound:
        print("Не найдено")
```

**Отличия от JS SDK:** Нет встроенного retry (реализуй вручную). Sync Client + AsyncClient. Нет namespace `dataSources`.

---

## 08. Webhooks и автоматизация

### API Webhooks (с сентября 2025)

Настройка: My Integrations > Webhooks > Create subscription. Нужен публичный HTTPS endpoint.

**Event types (23 типа):**

| Группа | События |
|--------|---------|
| Page (8) | `created`, `content_updated`, `properties_updated`, `moved`, `deleted`, `undeleted`, `locked`, `unlocked` |
| Data Source (6) | `created`, `content_updated`, `schema_updated`, `moved`, `deleted`, `undeleted` |
| Database (6) | `created`, `moved`, `deleted`, `undeleted` + deprecated: `content_updated`, `schema_updated` |
| Comment (3) | `created`, `updated`, `deleted` |

**Верификация подписи (HMAC-SHA256):**
```javascript
const crypto = require("crypto");
const hmac = crypto.createHmac("sha256", WEBHOOK_SECRET);
hmac.update(rawBody);
const expected = `sha256=${hmac.digest("hex")}`;
const isValid = crypto.timingSafeEqual(
  Buffer.from(req.headers["x-notion-signature"]),
  Buffer.from(expected)
);
```

> Payload НЕ содержит данные изменений -- только сигнал. Нужен follow-up запрос к API.
> Доставка: at-most-once, до 8 retry за ~24 часа, агрегация быстрых изменений.

### Webhook Actions (UI, с декабря 2025)

Доступны на платных планах (Plus+). Настраиваются в Database Automations (значок молнии). Max 5 webhook actions на автоматизацию. Только POST.

### Database Automations (no-code)

Триггеры: Page added, Property edited, Scheduled (Plus+).
Действия: Edit property, Send Slack notification (Plus+), Add page (Plus+), Send webhook (Plus+).

### Polling как fallback

```python
results = notion.databases.query(
  database_id=DB_ID,
  filter={"timestamp": "last_edited_time",
          "last_edited_time": {"after": last_check_iso}},
)
```

Интервал >= 2 мин. Гарантирует захват всех изменений (в отличие от webhooks).

---

## 09. Notion MCP Server

### Два варианта

| | Hosted MCP (рекомендуемый) | Open-Source MCP |
|-|---------------------------|----------------|
| URL | `https://mcp.notion.com/mcp` | npm `@notionhq/notion-mcp-server` |
| Auth | OAuth 2.1 (one-click) | Bearer Token |
| Формат | Notion-Flavored Markdown (token-efficient) | JSON |
| Статус | Активно поддерживается | **Not actively maintained** |

### Настройка в Claude Code

```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
```

### Настройка Open-Source (claude_desktop_config.json)

```json
{
  "mcpServers": {
    "notionApi": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": { "NOTION_TOKEN": "ntn_****" }
    }
  }
}
```

### Hosted MCP Tools (16)

`notion-search`, `notion-fetch`, `notion-create-pages`, `notion-update-page`, `notion-move-pages`, `notion-duplicate-page`, `notion-create-database`, `notion-update-data-source`, `notion-query-data-sources`, `notion-query-database-view`, `notion-create-comment`, `notion-get-comments`, `notion-get-teams`, `notion-get-users`, `notion-get-user`, `notion-get-self`

### Ограничения MCP vs прямой API

Через MCP нельзя: удалять БД, загружать файлы, создавать block-level комментарии, управлять webhook-подписками.

> **Предупреждение:** OAuth через MCP даёт AI-агенту те же права, что у пользователя. Non-zero risk к данным workspace.

---

## 10. Интеграции (Zapier, Make, n8n)

### Сравнение платформ

| | Zapier | Make.com | n8n |
|-|--------|---------|-----|
| Notion triggers | 6 (все Instant) | 1 (Watch, polling) | 2 (polling) + Webhook node |
| Notion actions | 27 | 4 + Make an API Call | 14 |
| Приложения | 8,000+ | 1,500+ | 400+ (+ custom nodes) |
| Self-hosted | Нет | Нет | Да (бесплатно) |
| Бесплатный план | 100 tasks/мес | 1,000 ops/мес | Unlimited (self-hosted) |
| Для туризма | Лучший выбор для быстрого старта | Сложные сценарии | Полный контроль |

### Сценарии для туризма ОАЭ

| Сценарий | Платформа | Trigger -> Action |
|----------|----------|-------------------|
| Google Form -> CRM | Zapier/Make | Form submission -> Create Database Item |
| Новый заказ -> Slack | Zapier | New Data Source Item -> Send Slack Message |
| Booking -> Google Calendar | Zapier/Make | New Item -> Create Calendar Event |
| WhatsApp -> Notion | n8n/Zapier | Webhook -> Create Database Item |
| Ежедневный отчёт | Make/n8n | Schedule -> Query Notion -> Email/Slack |

### Slack + Notion (нативно)

`/notion create` в Slack, link previews с AI-summary, автоматизации Database -> Slack channel.

### Google Calendar

Notion Calendar (нативное приложение) для двусторонней синхронизации. Для одностороннего -- Zapier/Make.

---

## 11. Permissions, Sharing, Team Spaces

### Уровни доступа (5)

| Уровень | Страницы | БД | Описание |
|---------|----------|-----|----------|
| Full access | Да | Да | Всё, включая share и delete |
| Can edit | Да | Да | Редактирование контента и структуры |
| Can edit content | Нет | Да | Только записи, без изменения views/свойств БД |
| Can comment | Да | Да | Только комментарии |
| Can view | Да | Да | Только просмотр |

### Teamspaces

| Тип | Видимость | Доступность |
|-----|-----------|-------------|
| Open | Все видят, все могут присоединиться | Все планы |
| Closed | Видно что существует, вход по приглашению | Все планы |
| Private | Невидим для не-членов | Business+ |

### Гости

Бесплатны на всех планах. Лимиты: Free 10, Plus 100, Business 250, Enterprise custom. Видят только расшаренные страницы.

### API Permissions

- Интеграция видит ТОЛЬКО страницы/БД, явно расшаренные с ней
- Связанные через Relation БД тоже должны быть расшарены
- **API не имеет эндпоинта для шаринга страниц** -- шаринг только через UI
- Granular DB permissions (Business+): разные права на уровне строк по Person/Created by
- `is_locked` блокирует UI-редактирование, но API продолжает работать

### Безопасность

AES-256 (at rest), TLS 1.2+ (in transit). SOC 2/3, ISO 27001, HIPAA (Enterprise+BAA), GDPR. SAML SSO, SCIM, Audit Log -- Enterprise.

---

## 12. CRM/Wiki для туризма ОАЭ

### Структура CRM (7 связанных баз)

```
Clients <-> Bookings <-> Products
                |            |
            Suppliers    Suppliers
```

**Распределение по братьям:**
- **Сухейль:** Экскурсии (City Tour, Desert Safari, Abu Dhabi Tour), Билеты (Burj Khalifa, Dubai Frame, Aquaventure)
- **Марсель:** Car Rental (Luxury/Sport/Business/Economy), Transfers, МВУ
- **Муфамад:** Paramount Yachts (300+ яхт), Water Activities, Catering

### Clients DB -- ключевые свойства

`Name` (title), `Phone`, `Email`, `WhatsApp` (URL: wa.me/номер), `Telegram` (URL), `Country` (select), `Source` (select: Instagram/Telegram/Referral/Walk-in), `Status` (status: Lead/Active/VIP), `Bookings` (relation), `Total Revenue` (rollup: sum), `Agent` (person: Сухейль/Марсель/Муфамад)

### Bookings DB -- ключевые свойства

`Booking Name` (title), `Client` (relation), `Product` (relation), `Date`, `Status` (status: Inquiry/Confirmed/Paid/Completed/Cancelled), `Price AED` (number), `Client Currency` (select: AED/USD/RUB/KZT/Crypto), `Payment Method` (select: Cash AED/Sber RUB/Kaspi KZT/Crypto), `Pax` (number), `Pickup Location`, `Cost Price` (number), `Profit` (formula), `Booking ID` (unique_id: prefix "BOOK")

### Products DB -- ключевые свойства

`Product Name` (title), `Category` (select: Excursion/Park Ticket/Yacht/Car Rental/Transfer/MVU), `Responsible` (person), `Price Regular AED`, `Price High Season AED`, `Cost Price`, `Place` (place -- геолокация точки в Дубае), `Status` (Active/Paused), `Total Sold` (rollup: count)

### Мультивалютность (AED, USD, RUB, KZT)

```
// Формула Amount AED
if(prop("Client Currency") == "USD", prop("Amount") * 3.67,
if(prop("Client Currency") == "RUB", prop("Amount") * 0.04,
if(prop("Client Currency") == "KZT", prop("Amount") * 0.007,
prop("Amount"))))
```

### Рекомендуемые Views

| View | Тип | База | Назначение |
|------|-----|------|-----------|
| Pipeline | Board (Kanban) | Bookings | По статусу: Inquiry -> Confirmed -> Paid -> Completed |
| Calendar | Calendar | Bookings | По датам экскурсий |
| Gallery | Gallery | Products | Каталог с фото и ценами |
| Today | Table (filter) | Bookings | Date = Today |
| Unpaid | Board | Bookings | Payment Status != Paid |
| By Agent | Board | Bookings | Группировка по ответственному |

### Автоматизация для туризма

1. **Новый заказ -> Slack:** Database Automation: Status changed -> Send Slack notification
2. **Google Form -> CRM:** Zapier: Form submission -> Create Database Item в Bookings
3. **WhatsApp -> Notion:** n8n: Webhook -> Create record в Clients
4. **Напоминание клиенту:** Zapier: Schedule -> Filter (Date = Tomorrow) -> Send WhatsApp

### Wiki для команды

Структура в Teamspace: Прайсы (linked databases с фильтрами по категориям), Инструкции (как оформить бронирование, принять оплату), Скрипты продаж (приветствие, upsell, обработка возражений), Шаблоны ответов (подтверждение, напоминание, запрос отзыва), Чек-листы (утренний, подготовка к экскурсии, закрытие дня).
