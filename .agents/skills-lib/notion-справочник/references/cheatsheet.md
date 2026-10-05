# Cheatsheet: Notion API

> Данные актуальны на: 2026-02-15 | API Version: 2025-09-03 | Base URL: `https://api.notion.com/v1`

---

## Все Endpoints

### Databases

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/databases` | Создать БД |
| `GET` | `/databases/{id}` | Получить БД |
| `PATCH` | `/databases/{id}` | Обновить контейнер БД |
| `POST` | `/databases/{id}/query` | Запросить записи (deprecated -> Data Source) |

### Pages

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/pages` | Создать страницу |
| `GET` | `/pages/{id}` | Получить страницу |
| `PATCH` | `/pages/{id}` | Обновить свойства |
| `GET` | `/pages/{id}/properties/{property_id}` | Получить конкретное свойство |

### Blocks

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/blocks/{id}` | Получить блок |
| `PATCH` | `/blocks/{id}` | Обновить блок |
| `DELETE` | `/blocks/{id}` | Удалить блок (в корзину) |
| `GET` | `/blocks/{id}/children` | Получить дочерние блоки |
| `PATCH` | `/blocks/{id}/children` | Добавить дочерние блоки |

### Search / Users / Comments

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/search` | Поиск по заголовкам |
| `GET` | `/users` | Список пользователей |
| `GET` | `/users/{id}` | Один пользователь |
| `GET` | `/users/me` | Текущий бот |
| `POST` | `/comments` | Создать комментарий |
| `GET` | `/comments?block_id={id}` | Получить комментарии |

### OAuth

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/oauth/authorize` | Начать OAuth flow |
| `POST` | `/oauth/token` | Обменять code на token |
| `POST` | `/oauth/revoke` | Отозвать token |

---

## Обязательные заголовки

```
Authorization: Bearer ntn_***
Notion-Version: 2025-09-03
Content-Type: application/json
```

---

## HTTP коды ответов

| Код | Имя | Описание | Действие |
|-----|-----|----------|----------|
| 200 | OK | Успех | -- |
| 400 | validation_error | Неверный формат запроса | Проверь payload |
| 401 | unauthorized | Неверный токен | Проверь Authorization + Notion-Version |
| 403 | restricted_resource | Нет прав | Проверь capabilities и sharing |
| 404 | object_not_found | Не найдено или нет доступа | Проверь ID и sharing |
| 409 | conflict_error | Конфликт | Retry с backoff |
| 429 | rate_limited | Превышен лимит | Жди Retry-After |
| 500 | internal_server_error | Ошибка сервера | Retry |
| 502 | -- | Bad Gateway | Retry через 30s |
| 503 | service_unavailable | Сервис недоступен | Retry через 30s |

---

## Лимиты

| Лимит | Значение |
|-------|----------|
| Rate limit | 3 req/sec (~180/мин, ~2,700/15 мин) |
| Payload | 1,000 block elements, 500 KB |
| Массив блоков | 100 элементов |
| Вложенность (append) | 2 уровня |
| page_size | Max 100 |
| Rich text content | 2,000 символов |
| Rich text массив | 100 элементов |
| URL | 2,000 символов |
| Email/Phone | 200 символов |
| Relations | 100 страниц |
| Multi-select | 100 опций |
| People | 100 пользователей |
| Файл upload | До 5 GB (multi-part > 20 MiB) |
| Имя файла | 900 байт |
| filter_properties | 100 ID |
| Комментарий: вложения | 3 файла |
| Formula depth | 10 таблиц |
| Free блоки (команда) | 1,000 + 3 дня grace |

---

## Property Types -- JSON формат значений

### При записи (Create/Update Page)

```json
// title
"Name": { "title": [{ "text": { "content": "Desert Safari" } }] }

// rich_text
"Description": { "rich_text": [{ "text": { "content": "Описание тура" } }] }

// number
"Price": { "number": 150 }

// select
"Category": { "select": { "name": "Excursion" } }

// multi_select
"Tags": { "multi_select": [{ "name": "VIP" }, { "name": "Desert" }] }

// date (одиночная)
"Date": { "date": { "start": "2026-03-15" } }

// date (диапазон)
"Period": { "date": { "start": "2026-03-15", "end": "2026-03-20" } }

// checkbox
"Paid": { "checkbox": true }

// url
"Website": { "url": "https://example.com" }

// email
"Email": { "email": "client@example.com" }

// phone_number
"Phone": { "phone_number": "+971501234567" }

// people
"Agent": { "people": [{ "id": "user-uuid" }] }

// relation
"Client": { "relation": [{ "id": "page-uuid" }] }

// files (external)
"Photo": { "files": [{ "name": "tour.jpg", "external": { "url": "https://..." } }] }

// status
"Status": { "status": { "name": "Active" } }
```

---

## Block Types -- JSON формат

```json
// Параграф
{ "type": "paragraph", "paragraph": { "rich_text": [{ "text": { "content": "Текст" } }] } }

// Заголовок
{ "type": "heading_2", "heading_2": { "rich_text": [{ "text": { "content": "Заголовок" } }] } }

// Список
{ "type": "bulleted_list_item", "bulleted_list_item": { "rich_text": [{ "text": { "content": "Пункт" } }] } }

// Чекбокс
{ "type": "to_do", "to_do": { "rich_text": [{ "text": { "content": "Задача" } }], "checked": false } }

// Код
{ "type": "code", "code": { "rich_text": [{ "text": { "content": "console.log('hi')" } }], "language": "javascript" } }

// Callout
{ "type": "callout", "callout": { "rich_text": [{ "text": { "content": "Важно!" } }], "icon": { "emoji": "\u26a0\ufe0f" } } }

// Изображение (external)
{ "type": "image", "image": { "type": "external", "external": { "url": "https://..." } } }

// Таблица
{ "type": "table", "table": { "table_width": 3, "has_column_header": true, "children": [/* table_row */] } }

// Divider
{ "type": "divider", "divider": {} }
```

---

## Filter операторы

### По типу свойства

| Тип | Операторы |
|-----|-----------|
| **text/title** | `equals`, `does_not_equal`, `contains`, `does_not_contain`, `starts_with`, `ends_with`, `is_empty`, `is_not_empty` |
| **number** | `equals`, `does_not_equal`, `greater_than`, `less_than`, `greater_than_or_equal_to`, `less_than_or_equal_to`, `is_empty`, `is_not_empty` |
| **checkbox** | `equals`, `does_not_equal` (boolean) |
| **select/status** | `equals`, `does_not_equal`, `is_empty`, `is_not_empty` |
| **multi_select** | `contains`, `does_not_contain`, `is_empty`, `is_not_empty` |
| **date** | `equals`, `before`, `after`, `on_or_before`, `on_or_after`, `is_empty`, `is_not_empty`, `past_week`, `past_month`, `past_year`, `next_week`, `next_month`, `next_year`, `this_week` |
| **people/relation** | `contains`, `does_not_contain` (UUID), `is_empty`, `is_not_empty` |
| **files** | `is_empty`, `is_not_empty` |
| **unique_id** | `equals`, `does_not_equal`, `greater_than`, `less_than`, `greater_than_or_equal_to`, `less_than_or_equal_to` |

### Compound фильтры

```json
{ "and": [{ "property": "Status", "status": { "equals": "Active" } }, { "property": "Price", "number": { "greater_than": 100 } }] }
{ "or": [{ "property": "Agent", "people": { "contains": "user-1" } }, { "property": "Agent", "people": { "contains": "user-2" } }] }
```

---

## Sort формат

```json
// По свойству
{ "property": "Date", "direction": "ascending" }
{ "property": "Price", "direction": "descending" }

// По timestamp
{ "timestamp": "created_time", "direction": "descending" }
{ "timestamp": "last_edited_time", "direction": "ascending" }
```

---

## Rollup функции (24)

| Категория | Функции |
|----------|---------|
| Универсальные | `count`, `count_values`, `unique`, `empty`, `not_empty`, `percent_empty`, `percent_not_empty`, `show_original`, `show_unique` |
| Числовые | `sum`, `average`, `median`, `min`, `max`, `range` |
| Даты | `earliest_date`, `latest_date`, `date_range` |
| Checkbox | `checked`, `unchecked`, `percent_checked`, `percent_unchecked` |
| Группировки | `count_per_group`, `percent_per_group` |

---

## Формулы 2.0 -- ключевые функции

| Категория | Функции |
|----------|---------|
| Строки | `substring`, `contains`, `lower`, `upper`, `split`, `join`, `trim`, `length`, `format`, `link`, `style`, `repeat` |
| Числа | `round`, `ceil`, `floor`, `abs`, `min`, `max`, `sum`, `mean`, `median`, `toNumber`, `pow`, `sqrt`, `mod` |
| Даты | `now`, `today`, `dateAdd`, `dateSubtract`, `dateBetween`, `formatDate`, `parseDate`, `dateRange`, `year`, `month`, `date`, `day`, `hour`, `minute` |
| Логика | `if`, `ifs`, `empty`, `and`, `or`, `not`, `equal`, `unequal` |
| Списки | `map`, `filter`, `sort`, `reverse`, `unique`, `find`, `findIndex`, `some`, `every`, `flat`, `concat`, `slice`, `at`, `first`, `last`, `includes`, `length` |
| Regex | `test`, `match`, `replace`, `replaceAll` |
| Переменные | `let`, `lets` |
| Люди | `name`, `email`, `id` |

---

## MCP Tools (Hosted -- 16)

| Tool | Описание |
|------|----------|
| `notion-search` | Поиск по workspace |
| `notion-fetch` | Получить страницу по URL |
| `notion-create-pages` | Создать страницы |
| `notion-update-page` | Обновить страницу |
| `notion-move-pages` | Переместить страницы |
| `notion-duplicate-page` | Дублировать страницу |
| `notion-create-database` | Создать БД |
| `notion-update-data-source` | Обновить data source |
| `notion-query-data-sources` | Запросить data sources |
| `notion-query-database-view` | Запросить через view (Business+) |
| `notion-create-comment` | Создать комментарий |
| `notion-get-comments` | Получить комментарии |
| `notion-get-teams` | Список teamspaces |
| `notion-get-users` | Список пользователей |
| `notion-get-user` | Один пользователь |
| `notion-get-self` | Текущий бот |

---

## Webhook Event Types (23)

| Группа | Events |
|--------|--------|
| Page | `page.created`, `page.content_updated`, `page.properties_updated`, `page.moved`, `page.deleted`, `page.undeleted`, `page.locked`, `page.unlocked` |
| Data Source | `data_source.created`, `data_source.content_updated`, `data_source.schema_updated`, `data_source.moved`, `data_source.deleted`, `data_source.undeleted` |
| Database | `database.created`, `database.moved`, `database.deleted`, `database.undeleted`, ~~`database.content_updated`~~, ~~`database.schema_updated`~~ (deprecated) |
| Comment | `comment.created`, `comment.updated`, `comment.deleted` |

---

## Тарифы (февраль 2026)

| План | Цена | AI | Гости | Блоки (команда) |
|------|------|----|-------|----------------|
| Free | $0 | Нет | 10 | 1,000 |
| Plus | $10/user/мес | Нет | 100 | Unlimited |
| Business | $20/user/мес | Да | 250 | Unlimited |
| Enterprise | Custom | Да | Custom | Unlimited |
