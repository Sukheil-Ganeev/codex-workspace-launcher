---
name: nocodb-справочник
description: "Production-ready руководство по NocoDB API для туристического бизнеса ОАЭ. Триггеры - nocodb api, nocodb база, nocodb crm, nocodb docker."
---
# NocoDB -- Production-ready справочник

> Version: 1.0 | Created: 2026-02-15 | API: v2 (stable)

---

## 01. Обзор NocoDB

NocoDB -- open-source альтернатива Airtable, превращающая реляционную базу данных (PostgreSQL, MySQL, MariaDB, SQLite, SQL Server, Oracle) в spreadsheet-интерфейс с автоматически генерируемым REST API.

| Параметр | Значение |
|---|---|
| GitHub Stars | ~62,000+ |
| Версия | 0.301.2 (npm) / 2026.01.0 (changelog) |
| Лицензия | Sustainable Use License (с января 2026; ранее AGPL-3.0) |
| Стек | Node.js, Vue.js/Nuxt, PostgreSQL рекомендуется |
| API | REST API v2 (stable), v3 (beta, Cloud/Enterprise) |
| Типы полей | 35+ |
| MCP Server | Встроен с 2025.09.0 (Desktop), OAuth с 2025.10.0 (Web) |

**Лицензия:** С января 2026 NocoDB перешла с AGPL-3.0 на Sustainable Use License. Self-hosting бесплатен и без ограничений. Коммерческая перепродажа NocoDB как SaaS запрещена без лицензии.

### NocoDB vs Airtable

| Критерий | NocoDB | Airtable |
|---|---|---|
| Self-hosted | Да (Docker, npm) | Нет |
| Бесплатный план | 3 редактора, 1,000 записей | 5 пользователей, 1,000 записей/базу |
| Платный (от) | $12/мес (Plus, годовой) | $20/мес (Team) |
| Модель "Pay for 9" | Да -- после 9 пользователей все бесплатно | Строго per-seat |
| 100 пользователей/год | ~$2,592 (Plus) | ~$54,000 (Business) |
| Производительность | Миллионы строк (PostgreSQL) | Тормозит на >50K |
| Vendor lock-in | Нет (данные в вашей БД) | Да |

### NocoDB Cloud

| План | Цена | Записи | Хранилище | API/мес |
|---|---|---|---|---|
| **Free** | $0 | 1,000 | 1 ГБ | 1,000 |
| **Plus** | $12/мес (год) / $15/мес | 50,000 | 20 ГБ | 100,000 |
| **Business** | $24/мес (год) / $30/мес | 300,000 | 100 ГБ | 1,000,000 |
| **Enterprise** | от $1,000/мес | Unlimited | Unlimited | Unlimited |

"Pay for 9, get unlimited" -- максимальная оплата за 9 редакторов, далее бесплатно. Скидка 20% при годовой оплате.

### Ключевые концепции

- **Workspace** -- контейнер верхнего уровня
- **Base** -- основная единица: определяет структуру БД
- **Table** -- таблица данных (строки = records, столбцы = fields)
- **View** -- представление: Grid, Kanban, Gallery, Calendar, Form
- **Field** -- типизированный столбец (35+ типов)
- **Link** -- связи между таблицами

---

## 02. Установка и настройка

### Docker Compose с PostgreSQL (рекомендуемый)

```yaml
version: '3.8'
services:
  nocodb:
    image: nocodb/nocodb:latest
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      NC_DB: "pg://db:5432?u=nocodb&p=secure_password&d=nocodb"
      NC_AUTH_JWT_SECRET: "your-random-64-char-secret"
      NC_PUBLIC_URL: "https://nocodb.yourdomain.com"
      NC_REDIS_URL: "redis://redis:6379"
    volumes:
      - nc_data:/usr/app/data
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  db:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_DB: nocodb
      POSTGRES_USER: nocodb
      POSTGRES_PASSWORD: secure_password
    volumes:
      - pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U nocodb"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  nc_data:
  pg_data:
```

### Другие способы установки

| Метод | Команда/Действие | Production |
|---|---|---|
| **Docker (простой)** | `docker run -d -p 8080:8080 nocodb/nocodb:latest` | Нет |
| **Auto-Upstall** | `bash <(curl -sSL http://install.nocodb.com/noco.sh) <(mktemp)` | Да |
| **npm** | `npx nocodb` | Нет |
| **Railway** | One-click: railway.com/deploy/nocodb-starter-pack | Да |
| **NocoDB Cloud** | app.nocodb.com | Да |

**Устаревшее:** `npx create-nocodb-app` -- не обновлялся 3+ лет. Не использовать.

### Ключевые переменные окружения

| Переменная | Описание | По умолчанию |
|---|---|---|
| `NC_DB` | Строка подключения к мета-БД | SQLite |
| `NC_AUTH_JWT_SECRET` | Секрет для JWT (обязателен для production!) | Авто |
| `NC_PUBLIC_URL` | Публичный URL | Из запроса |
| `NC_REDIS_URL` | Redis для кэширования | Без кэша |
| `NC_INVITE_ONLY_SIGNUP` | Только по приглашению | false |
| `DB_QUERY_LIMIT_DEFAULT` | Лимит пагинации по умолчанию | 25 |
| `DB_QUERY_LIMIT_MAX` | Максимальный лимит пагинации | 1000 |

Формат `NC_DB`: `pg://host:5432?u=user&p=password&d=database` (PostgreSQL), `mysql2://host:3306?u=user&p=password&d=database` (MySQL).

### Первоначальная настройка

1. Открыть `http://localhost:8080`
2. Создать аккаунт суперадмина
3. Создать Base -> Tables -> Fields -> Links -> Views
4. Импорт данных: CSV, Excel, JSON, Airtable

---

## 03. API v2 -- Tables и Records

### Аутентификация

**API Token (рекомендуется):** заголовок `xc-token`

```bash
curl -X GET 'https://app.nocodb.com/api/v2/tables/{tableId}/records' \
  -H 'xc-token: YOUR_API_TOKEN'
```

Также поддерживается `Authorization: Bearer YOUR_API_TOKEN` (с v0.264.7+).

**Auth Token (deprecated):** заголовок `xc-auth`. JWT через `POST /api/v1/auth/user/signin`. Deprecated с v0.205.1.

Создание API Token: Settings -> Account Settings -> Tokens -> Add New API Token.

### Endpoints для записей (Data API v2)

| Метод | Endpoint | Описание |
|---|---|---|
| GET | `/api/v2/tables/{tableId}/records` | Список записей |
| POST | `/api/v2/tables/{tableId}/records` | Создать запись(и) |
| GET | `/api/v2/tables/{tableId}/records/{recordId}` | Одна запись |
| PATCH | `/api/v2/tables/{tableId}/records` | Обновить запись(и) |
| DELETE | `/api/v2/tables/{tableId}/records` | Удалить запись(и) |

### CRUD примеры

```bash
# Создать запись
curl -X POST "https://app.nocodb.com/api/v2/tables/${tableId}/records" \
  -H "xc-token: ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"Title": "Desert Safari", "Price": 150, "Status": "Active"}'

# Получить записи с фильтрами
curl -X GET "https://app.nocodb.com/api/v2/tables/${tableId}/records?where=(Status,eq,Active)&sort=-CreatedAt&limit=25&offset=0" \
  -H "xc-token: ${API_TOKEN}"

# Обновить запись
curl -X PATCH "https://app.nocodb.com/api/v2/tables/${tableId}/records" \
  -H "xc-token: ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"Id": 1, "Status": "Completed"}'

# Удалить записи (массив)
curl -X DELETE "https://app.nocodb.com/api/v2/tables/${tableId}/records" \
  -H "xc-token: ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '[{"Id": 1}, {"Id": 2}]'
```

Bulk-операции: передавайте массив объектов в POST/PATCH/DELETE для массового создания/обновления/удаления.

### Пагинация

```
GET /api/v2/tables/{tableId}/records?offset=0&limit=25
```

Ответ:
```json
{
  "list": [...],
  "pageInfo": {
    "totalRows": 150,
    "page": 1,
    "pageSize": 25,
    "isFirstPage": true,
    "isLastPage": false
  }
}
```

Параметры: `limit` (по умолчанию 25, макс. 1000), `offset` (по умолчанию 0). Альтернативно: `page` + `pageSize`.

### Фильтрация (where)

Синтаксис: `(FieldName,operator,value)`

```
# Одно условие
where=(Status,eq,Active)

# AND
where=(Status,eq,Active)~and(Price,gt,100)

# OR
where=(Status,eq,Active)~or(Status,eq,Pending)

# NOT
where=~not(Status,eq,Archived)
```

**Операторы:** eq, neq, gt, ge, lt, le, like, nlike, is, isnot, in, btw, nbtw, null, notnull, empty, notempty, blank, notblank, allof, anyof, nallof, nanyof, checked, notchecked.

**Date:** isWithin с суб-операторами: today, tomorrow, yesterday, oneWeekAgo, daysAgo, exactDate и др.

### Сортировка и выбор полей

```
sort=-CreatedAt,Priority    # DESC по CreatedAt, ASC по Priority
fields=Title,Status,Price   # только нужные поля
shuffle=1                   # случайный порядок
```

### Rate Limiting

5 запросов/сек на пользователя. При превышении: HTTP 429, ожидание 30 секунд.

---

## 04. Fields -- типы полей

NocoDB поддерживает 35+ типов полей. Основные категории:

### Сводная таблица типов

| Тип NocoDB | Категория | JSON формат | Пример |
|---|---|---|---|
| SingleLineText | Текст | `string` | `"Dubai City Tour"` |
| LongText | Текст | `string` | `"Описание..."` |
| Number | Число | `number` | `150` |
| Decimal | Число | `number` | `3.14` |
| Currency | Число | `number` | `299.99` |
| Percent | Число | `number` | `75` |
| SingleSelect | Выбор | `string` | `"Confirmed"` |
| MultiSelect | Выбор | `string[]` | `["VIP","Urgent"]` |
| Date | Дата | `string` | `"2026-02-15"` |
| DateTime | Дата | `string` | `"2026-02-15T10:00:00Z"` |
| Time | Дата | `string` | `"14:30:00"` |
| Duration | Дата | `number` | `3600` (секунды) |
| Checkbox | Boolean | `boolean` | `true` |
| Rating | Число | `number` | `4` |
| Email | Текст | `string` | `"user@mail.com"` |
| URL | Текст | `string` | `"https://..."` |
| PhoneNumber | Текст | `string` | `"+971501234567"` |
| Attachment | Медиа | `array` | `[{url, title, mimetype}]` |
| Links | Связи | `object/list` | `{Id:1, Title:"..."}` |
| Lookup | Связи | varies | Значение из связанной таблицы |
| Rollup | Связи | varies | Агрегация связанных записей |
| Formula | Вычисл. | varies | Результат формулы |
| User | Спец. | `object` | `{id, email, display_name}` |
| JSON | Спец. | `object/array` | `{"key": "value"}` |
| CreatedTime | Вычисл. | `string` | `"2026-02-15T..."` |
| LastModifiedTime | Вычисл. | `string` | `"2026-02-15T..."` |
| AutoNumber | Вычисл. | `number` | `1001` |
| QrCode | Спец. | Генерация | QR из строкового поля |
| Barcode | Спец. | Генерация | Штрих-код (CODE128, EAN и др.) |
| GeoData | Спец. | coordinates | Геоданные |
| Button | Спец. | - | Действие по клику |

### Управление полями через API

```bash
# Создание
POST /api/v2/meta/tables/{tableId}/columns
{"title": "Status", "uidt": "SingleSelect", "dtxp": "'Active','Inactive'"}

# Обновление
PATCH /api/v2/meta/columns/{columnId}
{"title": "New Name"}

# Удаление
DELETE /api/v2/meta/columns/{columnId}
```

---

## 05. Views -- представления

### Типы Views

| Тип | Назначение | Пример для туризма |
|---|---|---|
| **Grid** | Табличный вид (по умолчанию) | Все экскурсии с ценами |
| **Gallery** | Карточки с фото | Каталог достопримечательностей |
| **Kanban** | Доски по статусам | Бронирования: New -> Paid -> Done |
| **Form** | Формы ввода | Заявка от клиента |
| **Calendar** | Календарь | Расписание трансферов |

Данные общие для всех views одной таблицы. Конфигурация (фильтры, сортировка, скрытые поля) -- независимая для каждого view.

### Form View (подробно)

- **Conditional Fields** -- динамическое скрытие/показ полей
- **Pre-filling** -- 3 режима: Default (редактируемый), Hide (скрытый), Read-only
- **Survey Mode** -- пошаговый опрос
- **Redirect URL** -- перенаправление после отправки (поддерживает `{record_id}`)
- **Валидация** (Cloud): лимит символов, min/max, regex, типы файлов

### Shared Views

Публичные ссылки для views без авторизации:
- Custom URL
- Защита паролем
- Toggle "Allow Download"
- RTL и Themes для форм
- Embed через iframe:

```html
<iframe src="https://app.nocodb.com/#/nc/view/YOUR_SHARED_VIEW_ID" width="100%" height="600"></iframe>
```

### View API

Данные через view: `GET /api/v2/tables/{tableId}/records?viewId={viewId}`

Meta API для управления views (Cloud/Enterprise): `GET/POST/PATCH/DELETE /api/v2/meta/tables/{tableId}/views`

---

## 06. Формулы

### Основные функции

**Числовые (22):** ABS, ADD, AVG, CEILING, COUNT, COUNTA, COUNTALL, EVEN, EXP, FLOOR, INT, LOG, MAX, MIN, MOD, ODD, POWER, ROUND, ROUNDDOWN, ROUNDUP, SQRT, VALUE

**Строковые (19):** CONCAT, LEFT, LEN, LOWER, MID, REGEX_EXTRACT, REGEX_MATCH, REGEX_REPLACE, REPEAT, REPLACE, RIGHT, SEARCH, SUBSTR, TRIM, UPPER, URL, URLENCODE, ISBLANK, ISNOTBLANK

**Дата (9):** NOW, DATEADD, DATETIME_DIFF, WEEKDAY, DATESTR, DAY, MONTH, YEAR, HOUR

**Условные (4):** IF, SWITCH, AND, OR

**Общие:** RECORD_ID

### Готовые формулы для туризма ОАЭ

```
# Прибыль (AED)
{Цена продажи} - {Себестоимость}

# Маржа (%)
IF({Цена продажи} > 0,
   ROUND(({Цена продажи} - {Себестоимость}) / {Цена продажи} * 100, 1),
   0)

# Дней до экскурсии
IF({Дата} >= NOW(), DATETIME_DIFF({Дата}, NOW(), "days"), "Прошло")

# Статус оплаты
IF({Статус} = "Оплачено", "Оплачен",
IF({Статус} = "Завершено", "Оплачен", "Не оплачен"))

# Полное имя клиента
CONCAT({Имя}, " ", {Фамилия})

# Дедлайн (за 2 дня до тура)
DATEADD({Дата}, -2, "days")

# Конвертация валют -> AED
IF({Валюта оплаты} = "RUB", {Сумма} * 0.04,
IF({Валюта оплаты} = "KZT", {Сумма} * 0.0072,
IF({Валюта оплаты} = "USD", {Сумма} * 3.67,
{Сумма})))

# Сезонная цена (High: Oct-Mar, Low: Apr-Sep)
IF(OR(MONTH(NOW()) >= 10, MONTH(NOW()) <= 3),
   {Сезон High}, {Сезон Low})

# Скидка
IF({Сумма} >= 1000, {Сумма} * 0.9,
IF({Сумма} >= 500, {Сумма} * 0.95, {Сумма}))
```

**Важно:** Функция называется `DATETIME_DIFF`, не DATEDIFF. Функции `COUNTLINKS` не существует -- для подсчета связей используйте Links field (автосчетчик) или Rollup с COUNT.

---

## 07. Links, Lookups, Rollups

### Links (связи между таблицами)

| Тип | Код | Описание |
|---|---|---|
| Has-Many | `hm` | Один-ко-многим (автоматически создает обратное Belongs-to) |
| Many-to-Many | `mm` | Многие-ко-многим (junction table автоматически) |
| One-to-One | `oo` | Один-к-одному |

Self-referencing links поддерживаются (Employee -> Manager, Category -> Parent).

Связи только между таблицами **одной базы**.

### Links API

```bash
# Получить связанные записи
GET /api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}

# Привязать записи
POST /api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}
Body: [{"Id": 1}, {"Id": 2}]

# Отвязать записи
DELETE /api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}
Body: [{"Id": 1}]
```

### Lookup

Подтягивает значение поля из связанной таблицы. Read-only. Обновляется в реальном времени.

Создание: выбрать Link field -> выбрать поле для отображения из связанной таблицы.

### Rollup

Агрегирует данные из связанных записей.

| Функция | Описание |
|---|---|
| count | Количество записей |
| sum | Сумма |
| avg | Среднее |
| min | Минимум |
| max | Максимум |
| countDistinct | Уникальных записей |
| sumDistinct | Сумма уникальных |
| avgDistinct | Среднее уникальных |

**Conditional Rollup** (Cloud Plus / Enterprise): фильтрация связанных записей перед агрегацией.

### Подсчет связей

Links field автоматически показывает количество связанных записей. Для подсчета с условиями -- используйте Rollup с COUNT.

---

## 08. Webhooks v3 и автоматизация

### Webhooks v3 (с NocoDB 2025.06.0)

**Триггеры:**
- **Record:** Send Me Everything, After Insert, After Update, After Delete
- **View / Field:** Enterprise
- **Button / Manual Trigger**

Unified events: After Insert срабатывает и при single, и при bulk операциях.

**Field-Level Triggers** (платные планы): webhook срабатывает только при изменении конкретных полей.

### Payload (v3)

```json
{
  "type": "records.after.update",
  "id": "unique-event-id",
  "version": "v3",
  "data": {
    "table_id": "tbl_xxxxx",
    "table_name": "Bookings",
    "rows": [{"Id": 1, "Status": "Confirmed"}],
    "previous_rows": [{"Id": 1, "Status": "New"}]
  }
}
```

**Кастомизация через Handlebars:**
```handlebars
{{ json event }}
{{ event.data.rows.[0].Title }}
{{ event.type }}
{{ event.data.table_name }}
```

### Условные webhooks

Webhook срабатывает только когда условие переходит из false в true. Поддерживаются AND/OR условия.

### Примеры автоматизаций для туризма

1. **Новое бронирование -> Telegram:** NocoDB Webhook -> n8n Webhook trigger -> Telegram Bot
2. **Статус "Confirmed" -> Email:** NocoDB Webhook (field-level: Status) -> n8n -> Send Email
3. **Ежедневный отчет:** n8n Schedule (08:00) -> NocoDB API (дата = сегодня) -> Telegram
4. **Напоминание клиенту:** n8n Schedule -> NocoDB API (дата = завтра) -> WhatsApp/Telegram

### Встроенные Workflows (beta)

NocoDB Cloud (Team+) и Enterprise: встроенные Workflows с triggers (record created/updated), actions (create record, send email/Slack), flow logic (if/else). Beta-статус.

---

## 09. SDK и аутентификация

### nocodb-sdk (npm)

```bash
npm i nocodb-sdk
```

```javascript
import { Api } from 'nocodb-sdk';

const api = new Api({
  baseURL: 'https://app.nocodb.com',
  headers: { 'xc-token': 'YOUR_API_TOKEN' }
});

// CRUD
const records = await api.dbTableRow.list('noco', 'baseName', 'tableName', {
  limit: 25, offset: 0, where: '(Status,eq,Active)'
});
await api.dbTableRow.create('noco', 'baseName', 'tableName', { Title: 'New' });
await api.dbTableRow.update('noco', 'baseName', 'tableName', rowId, { Status: 'Done' });
await api.dbTableRow.delete('noco', 'baseName', 'tableName', rowId);
```

**Важно:** Первый аргумент `"noco"` -- идентификатор workspace/org, НЕ версия API.

### Python (requests)

```python
import requests

BASE_URL = "https://app.nocodb.com"
headers = {"xc-token": "YOUR_API_TOKEN", "Content-Type": "application/json"}

# Чтение
r = requests.get(f"{BASE_URL}/api/v2/tables/{TABLE_ID}/records",
                 headers=headers, params={"limit": 25})
records = r.json()

# Создание
requests.post(f"{BASE_URL}/api/v2/tables/{TABLE_ID}/records",
              headers=headers, json={"Title": "Safari", "Price": 150})
```

Официального Python SDK нет. Неофициальные: `nocodb` (PyPI), `python-nocodb` (GitHub).

### Аутентификация

| Метод | Заголовок | Статус |
|---|---|---|
| API Token | `xc-token: TOKEN` | Рекомендуется |
| API Token | `Authorization: Bearer TOKEN` | С v0.264.7+ |
| Auth Token (JWT) | `xc-auth: JWT` | Deprecated с v0.205.1 |

API Token: не истекает, привязан к пользователю, создается в Settings -> Tokens.

### MCP Server

**Desktop (2025.09.0):** NocoDB Settings -> Model Context Protocol -> New MCP Endpoint. Подключение через Claude Desktop, Cursor, Windsurf.

```json
{
  "mcpServers": {
    "NocoDB MCP": {
      "command": "npx",
      "args": ["mcp-remote", "https://domain.com/mcp/<id>", "--header", "xc-mcp-token: <token>"]
    }
  }
}
```

**OAuth Web (2025.10.0):** Для Claude Web, ChatGPT. OAuth через браузер.

MCP работает только с записями (records). Метаданные (таблицы, поля) не поддерживаются.

---

## 10. Интеграции

### n8n (лучшая интеграция)

- **Тип:** Нативный NocoDB node (CRUD: Get, Get Many, Create, Update, Delete)
- **Trigger:** Отдельного NocoDB Trigger node НЕТ. Используйте: NocoDB Webhook -> n8n Webhook trigger, или Schedule trigger + NocoDB node
- **Self-hosted:** n8n и NocoDB на одном сервере в одной Docker-сети

### Zapier

- **Тип:** Нативное приложение
- **Trigger:** New or Updated Record
- **Actions:** Create, Update, Delete, Search Records
- Самый простой в настройке

### Make.com (Integromat)

- **Тип:** Нативный модуль NocoDB (обновлен с v3 APIs в 2025.11.0)
- **Triggers:** Watch Records, Watch Responses
- **Actions:** CRUD + Upsert + Bulk (Create/Update/Delete) + Make an API Call
- Самый богатый набор модулей

### Сравнительная таблица

| Функция | n8n | Zapier | Make.com |
|---|---|---|---|
| Self-hosted | Да | Нет | Нет |
| Trigger | Webhook/Schedule | New/Updated Record | Watch Records |
| Bulk ops | Через API | Update Multiple | Create/Update/Delete Bulk |
| Upsert | Нет | Нет | Да |
| Стоимость | Free (self-hosted) | от $20/мес | от $9/мес |

### Google Sheets

Прямого sync в NocoDB нет. Интеграция через n8n, Zapier или Make.com:
- NocoDB -> Sheets: NocoDB node -> Google Sheets node
- Sheets -> NocoDB: Google Sheets Trigger -> NocoDB Create Record

### Telegram Bot

NocoDB Webhook -> n8n Webhook trigger -> Telegram node. Настройка:
1. Создать бота через @BotFather
2. В n8n: Webhook trigger + IF (фильтр) + Telegram node
3. В NocoDB: Webhook -> POST -> URL вебхука n8n

---

## 11. Self-hosted -- бэкап и обслуживание

### Бэкап PostgreSQL

```bash
# Бэкап (сжатый)
docker exec nocodb-db pg_dump -U nocodb nocodb | gzip > nocodb-$(date +%Y%m%d).sql.gz

# Восстановление
gunzip -c nocodb-backup.sql.gz | docker exec -i nocodb-db psql -U nocodb nocodb
```

### Бэкап Docker volumes

```bash
docker run --rm \
  -v nocodb_nc_data:/source:ro \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/nocodb-data-$(date +%Y%m%d).tar.gz -C /source .
```

### Автоматизация через cron

```bash
# /etc/cron.d/nocodb-backup
0 3 * * * root docker exec nocodb-db pg_dump -U nocodb nocodb | gzip > /backups/nocodb-db-$(date +\%Y\%m\%d).sql.gz
0 5 * * * root find /backups -name "nocodb-*" -mtime +30 -delete
```

### Обновление версий

```bash
# 1. Бэкап!
docker exec nocodb-db pg_dump -U nocodb nocodb > pre-upgrade.sql

# 2. Обновить
docker compose pull && docker compose up -d

# 3. Проверить
docker logs nocodb -f
```

Рекомендуется фиксировать версию: `nocodb/nocodb:0.301.2` вместо `latest`.

### Безопасность production

- HTTPS через Traefik/Nginx (reverse proxy)
- Firewall: только 22, 80, 443
- `NC_INVITE_ONLY_SIGNUP=true`
- `NC_ALLOW_LOCAL_HOOKS=false`
- `NC_SECURE_ATTACHMENTS=true`
- Секреты в `.env` файле (chmod 600), не в docker-compose.yml
- Log rotation: `logging: { driver: json-file, options: { max-size: "10m", max-file: "3" } }`

### Деплой на хостингах

| Сценарий | Рекомендация | Цена |
|---|---|---|
| Быстрый старт | Railway (1-click) | от $5/мес |
| Малый бизнес | Railway или Render | от $25/мес |
| GDPR / полный контроль | Hetzner VPS + Docker | от ~$4-5/мес |
| Большая команда | Hetzner Dedicated + Redis | от ~$20/мес |

### Масштабирование

- Redis для кэширования (обязателен для 10+ пользователей)
- Кластерный режим (с v1.6.0): несколько инстансов NocoDB + Redis PubSub
- S3/Minio для вложений + CDN

---

## 12. CRM на NocoDB для туризма ОАЭ

### Структура CRM (4 таблицы)

#### Clients (Клиенты)

| Поле | Тип | Описание |
|---|---|---|
| ФИО | SingleLineText | Полное имя |
| Телефон | PhoneNumber | Номер телефона |
| Email | Email | Email-адрес |
| Telegram | SingleLineText | @username |
| WhatsApp | PhoneNumber | WhatsApp |
| Страна | SingleSelect | Казахстан, Россия, Узбекистан, ОАЭ, Другое |
| Источник | SingleSelect | Instagram, WhatsApp, Telegram, Referral, Walk-in |
| VIP | Checkbox | VIP-статус |
| Бронирования | Links (HasMany) | -> Bookings |

#### Bookings (Бронирования)

| Поле | Тип | Описание |
|---|---|---|
| Клиент | Links (BelongsTo) | -> Clients |
| Дата | Date | Дата экскурсии |
| Продукт | Links (BelongsTo) | -> Products |
| Статус | SingleSelect | Заявка, Подтверждено, Оплачено, Завершено, Отменено, Возврат |
| Количество | Number | Кол-во человек |
| Цена продажи | Currency (AED) | Цена для клиента |
| Себестоимость | Currency (AED) | Закупочная цена |
| Валюта оплаты | SingleSelect | AED, USD, RUB, KZT, Crypto |
| Способ оплаты | SingleSelect | Cash, Bank Transfer, Kaspi, Sber, Crypto |
| Агент | SingleSelect | Сухейль, Марсель, Муфамад |
| Поставщик | Links (BelongsTo) | -> Suppliers |
| Прибыль | Formula | `{Цена продажи} - {Себестоимость}` |
| Маржа (%) | Formula | `ROUND(...)` |

#### Products (Продукты/Услуги)

| Поле | Тип | Описание |
|---|---|---|
| Название | SingleLineText | Название услуги |
| Категория | SingleSelect | Экскурсия, Билет, Яхта, Авто, Трансфер, МВУ |
| Эмират | SingleSelect | Dubai, Abu Dhabi, Sharjah, RAK |
| Цена (AED) | Currency | Базовая цена |
| Себестоимость | Currency | Закупочная |
| Сезон High (Oct-Mar) | Currency | Цена в высокий сезон |
| Сезон Low (Apr-Sep) | Currency | Цена в низкий сезон |
| Фото | Attachment | Фотографии |
| Активен | Checkbox | В продаже |
| Бронирования | Links (HasMany) | -> Bookings |

#### Suppliers (Поставщики)

| Поле | Тип | Описание |
|---|---|---|
| Компания | SingleLineText | Название компании |
| Контакт | SingleLineText | Имя менеджера |
| Телефон | PhoneNumber | Телефон |
| WhatsApp | PhoneNumber | WhatsApp |
| Тип услуг | MultiSelect | Экскурсии, Билеты, Яхты, Авто, Трансферы |
| Комиссия (%) | Number | Размер комиссии |
| Рейтинг | Rating (1-5) | Оценка качества |
| Бронирования | Links (HasMany) | -> Bookings |

### Связи между таблицами

```
Clients ─── 1:N ──── Bookings
                        |
Products ── 1:N ────────|
                        |
Suppliers ─ 1:N ────────'
```

Lookup-поля: в Bookings -- `Клиент.Телефон`, `Продукт.Категория`.
Rollup-поля: в Clients -- `COUNT(Бронирования)`, `SUM(Бронирования.Цена)`, `AVG(Бронирования.Цена)`.

### Views для CRM

| View | Тип | Назначение |
|---|---|---|
| Pipeline | Kanban (по Статус) | Ежедневная работа агентов |
| Расписание | Calendar (по Дата) | Планирование дня |
| Каталог | Gallery (по Фото) | Показ клиентам |
| Заявка | Form (публичная) | Сбор заявок через WhatsApp/Telegram |
| Мои заявки | Grid (фильтр Агент) | Персональный вид |
| Сегодня | Grid (фильтр Дата=today) | Текущие заказы |
| Неоплаченные | Grid (фильтр Статус) | Контроль оплаты |

### Мультивалютность

| Валюта | Способ | Курс к AED |
|---|---|---|
| AED | Наличные, банк | 1.00 |
| USD | Наличные | 3.67 |
| RUB | Сбер, карты | ~0.04 |
| KZT | Kaspi | ~0.0072 |
| Crypto | Кошелек | По курсу |

Для актуальных курсов: n8n Schedule -> ExchangeRate API -> обновление таблицы курсов NocoDB.

### Сезонность ОАЭ

| Сезон | Месяцы | Цены |
|---|---|---|
| High Season | Октябрь -- Март | +20-50% |
| Low Season | Апрель -- Сентябрь | Скидки 10-30% |
| Пиковые даты | Новый год, Eid | Максимальные |

Formula автоматически выбирает сезонную цену по текущему месяцу.

### Автоматизация CRM

```
NocoDB Webhook (новая заявка)
    |
    v
n8n (self-hosted)
    |
    |-- Фильтр (Статус = "Заявка")
    |-- Форматирование
    v
Telegram Bot -> Группа "Новые заявки"
```

Сообщение:
```
Новая заявка!
Клиент: {ФИО}
Телефон: {Телефон}
Продукт: {Продукт}
Дата: {Дата}
Кол-во: {Количество}
Агент: {Агент}
```
