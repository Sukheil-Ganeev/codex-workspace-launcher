# NocoDB -- Cheatsheet (Шпаргалка)

> ДАННЫЕ АКТУАЛЬНЫ НА: 2026-02-15

---

## API Endpoints (v2)

### Data API

| Метод | Endpoint | Описание |
|---|---|---|
| GET | `/api/v2/tables/{tableId}/records` | Список записей |
| POST | `/api/v2/tables/{tableId}/records` | Создать запись(и) |
| GET | `/api/v2/tables/{tableId}/records/{recordId}` | Одна запись |
| PATCH | `/api/v2/tables/{tableId}/records` | Обновить запись(и) |
| DELETE | `/api/v2/tables/{tableId}/records` | Удалить запись(и) |
| GET | `/api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}` | Связанные записи |
| POST | `/api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}` | Привязать записи |
| DELETE | `/api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}` | Отвязать записи |
| POST | `/api/v2/storage/upload` | Загрузить файл |

### Meta API

| Метод | Endpoint | Описание |
|---|---|---|
| GET | `/api/v2/meta/bases/{baseId}/tables` | Список таблиц |
| POST | `/api/v2/meta/bases/{baseId}/tables` | Создать таблицу |
| GET | `/api/v2/meta/tables/{tableId}` | Информация о таблице |
| POST | `/api/v2/meta/tables/{tableId}/columns` | Создать поле |
| PATCH | `/api/v2/meta/columns/{columnId}` | Обновить поле |
| DELETE | `/api/v2/meta/columns/{columnId}` | Удалить поле |
| GET | `/api/v2/meta/tables/{tableId}/hooks` | Список webhooks |
| POST | `/api/v2/meta/tables/{tableId}/hooks` | Создать webhook |

---

## Аутентификация

```bash
# Рекомендуется
-H 'xc-token: YOUR_API_TOKEN'

# Альтернативно (с v0.264.7+)
-H 'Authorization: Bearer YOUR_API_TOKEN'

# Deprecated (JWT)
-H 'xc-auth: YOUR_JWT_TOKEN'
```

---

## Параметры запросов

| Параметр | Алиас | Описание | По умолчанию |
|---|---|---|---|
| `limit` | `l` | Кол-во записей | 25 |
| `offset` | `o` | Смещение | 0 |
| `sort` | `s` | Сортировка (- = DESC) | - |
| `fields` | `f` | Конкретные поля | * |
| `where` | `w` | Фильтрация | - |
| `shuffle` | `r` | Случайный порядок | 0 |
| `viewId` | - | ID представления | - |

---

## Операторы фильтрации (where)

### Базовые

| Оператор | Описание | Пример |
|---|---|---|
| `eq` | Равно | `(Status,eq,Active)` |
| `neq` | Не равно | `(Status,neq,Archived)` |
| `gt` | Больше | `(Price,gt,100)` |
| `ge` / `gte` | Больше или равно | `(Price,ge,100)` |
| `lt` | Меньше | `(Price,lt,50)` |
| `le` / `lte` | Меньше или равно | `(Price,le,50)` |
| `like` | Содержит | `(Name,like,%Safari%)` |
| `nlike` | Не содержит | `(Name,nlike,%test%)` |
| `in` | В списке | `(Status,in,Active,Pending)` |
| `btw` | Между | `(Price,btw,10,100)` |

### Null/Empty

| Оператор | Описание |
|---|---|
| `is` | Является (null/true/false) |
| `isnot` | Не является |
| `null` / `notnull` | Null проверка |
| `empty` / `notempty` | Пустота |
| `blank` / `notblank` | Blank |
| `checked` / `notchecked` | Checkbox |

### Multi-value

| Оператор | Описание |
|---|---|
| `allof` | Содержит все |
| `anyof` | Содержит хотя бы одно |
| `nallof` | Не содержит все |
| `nanyof` | Не содержит ни одного |

### Логические

```
~and    # AND
~or     # OR
~not    # NOT

# Примеры
where=(Status,eq,Active)~and(Price,gt,100)
where=(Status,eq,Active)~or(Status,eq,Pending)
where=~not(Status,eq,Archived)
```

---

## Формулы

### Числовые

```
ABS(x)           ROUND(x, precision)    MOD(a, b)
ADD(a, b, ...)   ROUNDUP(x, p)          POWER(base, exp)
AVG(a, b, ...)   ROUNDDOWN(x, p)        SQRT(x)
MIN(a, b, ...)   CEILING(x)             EXP(x)
MAX(a, b, ...)   FLOOR(x)               LOG(base, x)
COUNT(a, b)      INT(x)                 VALUE(text)
COUNTA(a, b)     EVEN(x)                COUNTALL(a, b)
                 ODD(x)
```

### Строковые

```
CONCAT(a, b, ...)    TRIM(text)          SEARCH(text, str)
LEFT(text, n)        UPPER(text)         SUBSTR(text, pos, n)
RIGHT(text, n)       LOWER(text)         URL(text)
MID(text, pos, n)    LEN(text)           URLENCODE(text)
REPLACE(text,s,r)    REPEAT(text, n)     ISBLANK(text)
REGEX_EXTRACT(t,p)   REGEX_MATCH(t,p)    ISNOTBLANK(text)
REGEX_REPLACE(t,p,r)
```

### Дата

```
NOW()                              # Текущая дата/время
DATEADD(date, value, unit)         # Добавить к дате
DATETIME_DIFF(date1, date2, unit)  # Разница дат (НЕ DATEDIFF!)
WEEKDAY(date, [startDay])          # День недели (0-6)
DATESTR(date)                      # Дата -> строка 'YYYY-MM-DD'
DAY(date)                          # День (1-31)
MONTH(date)                        # Месяц (1-12)
YEAR(date)                         # Год
HOUR(datetime)                     # Час (0-23)
```

Units для DATEADD/DATETIME_DIFF: `"second"`, `"minute"`, `"hour"`, `"day"`, `"week"`, `"month"`, `"year"`

### Условные

```
IF(condition, then, else)
SWITCH(expr, pattern1, value1, pattern2, value2, ..., default)
AND(expr1, expr2, ...)
OR(expr1, expr2, ...)
```

### Общие

```
RECORD_ID()    # Уникальный ID записи
```

---

## Docker команды

```bash
# Запуск
docker compose up -d

# Остановка
docker compose down

# Логи
docker logs nocodb -f
docker logs nocodb --tail 100

# Статус
docker compose ps

# Обновление
docker compose pull && docker compose up -d

# Бэкап PostgreSQL
docker exec nocodb-db pg_dump -U nocodb nocodb | gzip > backup.sql.gz

# Восстановление
gunzip -c backup.sql.gz | docker exec -i nocodb-db psql -U nocodb nocodb

# Бэкап volumes
docker run --rm -v nocodb_nc_data:/src:ro -v $(pwd):/bk alpine tar czf /bk/data.tar.gz -C /src .
```

---

## Переменные окружения

### Обязательные (production)

```env
NC_DB=pg://db:5432?u=nocodb&p=password&d=nocodb
NC_AUTH_JWT_SECRET=random-64-char-secret
NC_PUBLIC_URL=https://nocodb.yourdomain.com
NC_REDIS_URL=redis://redis:6379
```

### Безопасность

```env
NC_INVITE_ONLY_SIGNUP=true
NC_ALLOW_LOCAL_HOOKS=false
NC_SECURE_ATTACHMENTS=true
NC_CONNECTION_ENCRYPT_KEY=random-32-char
NC_SANITIZE_COLUMN_NAME=true
```

### Лимиты

```env
DB_QUERY_LIMIT_DEFAULT=25
DB_QUERY_LIMIT_MAX=1000
NC_ATTACHMENT_FIELD_SIZE=20971520
NC_MAX_ATTACHMENTS_ALLOWED=10
```

---

## HTTP коды ответов

| Код | Описание | Действие |
|---|---|---|
| 200 | OK | Успешный GET/PATCH/DELETE |
| 201 | Created | Успешный POST |
| 400 | Bad Request | Проверить тело запроса |
| 401 | Unauthorized | Проверить xc-token |
| 403 | Forbidden | Нет прав доступа |
| 404 | Not Found | Проверить tableId/recordId |
| 429 | Too Many Requests | Ждать 30 сек, rate limit |
| 500 | Server Error | Проверить логи NocoDB |

---

## Типы полей (uidt для API)

```
SingleLineText    LongText         Number
Decimal           Currency         Percent
Email             URL              PhoneNumber
Date              DateTime         Time
Duration          Year             SingleSelect
MultiSelect       Checkbox         Rating
Attachment        LinkToAnotherRecord  Links
Lookup            Rollup           Formula
Count             CreatedTime      LastModifiedTime
CreatedBy         LastModifiedBy   AutoNumber
Barcode           QrCode           GeoData
Geometry          Button           JSON
User
```

---

## ID форматы

| ID | Префикс | Пример |
|---|---|---|
| Workspace | `w` | `w1234abc` |
| Base | `p` | `p5678def` |
| Table | `m` | `m9012ghi` |
| View | `v` | `vw3456jkl` |
| Field | `c` | `c7890mno` |
| Record | число | `1`, `2`, `3` |

---

## Быстрые рецепты

### Получить все записи (пагинация)

```python
import requests

all_records = []
offset = 0
limit = 100

while True:
    r = requests.get(f"{BASE}/api/v2/tables/{TID}/records",
                     headers={"xc-token": TOKEN},
                     params={"limit": limit, "offset": offset})
    data = r.json()
    all_records.extend(data["list"])
    if data["pageInfo"]["isLastPage"]:
        break
    offset += limit
```

### Фильтрация по дате (сегодня)

```
?where=(Date,eq,today)
```

### Bulk создание с curl

```bash
curl -X POST "${BASE}/api/v2/tables/${TID}/records" \
  -H "xc-token: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '[
    {"Title": "Safari 1", "Price": 150},
    {"Title": "Safari 2", "Price": 200},
    {"Title": "City Tour", "Price": 100}
  ]'
```

---

## Ссылки

| Ресурс | URL |
|---|---|
| Документация | https://nocodb.com/docs |
| API v2 | https://nocodb.com/apis/v2/data |
| API v3 (beta) | https://nocodb.com/apis/v3/data |
| GitHub | https://github.com/nocodb/nocodb |
| Cloud | https://app.nocodb.com |
| Pricing | https://nocodb.com/pricing |
| ENV Variables | https://nocodb.com/docs/self-hosting/environment-variables |
| Changelog | https://nocodb.com/docs/changelog |
| n8n NocoDB | https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.nocodb/ |
| Make.com | https://www.make.com/en/integrations/nocodb |
| Zapier | https://zapier.com/apps/nocodb/integrations |
