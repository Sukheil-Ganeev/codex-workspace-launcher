# Troubleshooting: Notion API

> Данные актуальны на: 2026-02-15 | API Version: 2025-09-03

---

## Проблема 1: 401 Unauthorized

**Симптомы:** `{"code": "unauthorized", "status": 401}`
**Причина:** Неверный или отсутствующий токен, либо не указан `Notion-Version`.
**Решение:**
1. Проверь заголовок `Authorization: Bearer ntn_***` (не путай с `Token` или `ApiKey`)
2. Проверь заголовок `Notion-Version: 2025-09-03`
3. Убедись что токен не отозван (Settings > My Integrations)
4. Старые токены с `secret_` все ещё работают, но лучше обновить на `ntn_`

---

## Проблема 2: 403 Forbidden (restricted_resource)

**Симптомы:** `{"code": "restricted_resource", "status": 403}`
**Причина:** Интеграция не имеет нужных capabilities или не подключена к ресурсу.
**Решение:**
1. Проверь capabilities интеграции (My Integrations > Configuration)
2. Расшарь страницу/БД с интеграцией: Share > Connections > Add
3. Для comments -- включи Read/Insert comments capabilities (отключены по умолчанию!)
4. Для users -- включи Read user information

---

## Проблема 3: 404 Not Found (object_not_found)

**Симптомы:** `{"code": "object_not_found", "status": 404}`
**Причина:** Объект не существует, удалён, или нет доступа.
**Решение:**
1. Проверь правильность ID (32 hex символа, UUID формат)
2. Убедись что страница/БД расшарена с интеграцией
3. Проверь что объект не в корзине (`in_trash: true`)
4. Для relation -- обе связанные БД должны быть расшарены с интеграцией

---

## Проблема 4: 409 Conflict (conflict_error)

**Симптомы:** `{"code": "conflict_error", "status": 409}`
**Причина:** Одновременное редактирование одного объекта.
**Решение:**
1. Добавь retry с exponential backoff
2. Минимизируй параллельные запросы к одному ресурсу
3. Для batch-операций -- используй последовательное выполнение

---

## Проблема 5: 429 Rate Limited

**Симптомы:** `{"code": "rate_limited", "status": 429}`, заголовок `Retry-After: N`
**Причина:** Превышен лимит 3 req/sec.
**Решение:**
```javascript
// JS SDK: встроенный retry (maxRetries: 2)
const notion = new Client({
  auth: process.env.NOTION_TOKEN,
  retry: { maxRetries: 3 }, // увеличь при необходимости
});
```
```python
# Python: ручной retry
import time
while True:
    try:
        result = notion.databases.query(database_id="...")
        break
    except APIResponseError as e:
        if e.code == APIErrorCode.RateLimited:
            time.sleep(int(e.headers.get("Retry-After", 1)))
        else:
            raise
```

---

## Проблема 6: 400 Validation Error

**Симптомы:** `{"code": "validation_error", "status": 400, "message": "..."}`
**Причина:** Неверный формат данных в запросе.
**Частые ошибки:**
1. **Rich text > 2000 символов** -- разбей на несколько элементов
2. **Массив > 100 элементов** -- используй пагинацию для отправки
3. **Payload > 500KB** -- уменьши размер запроса
4. **Несуществующий property name** -- используй точное имя свойства (case-sensitive)
5. **Неверный тип значения** -- number требует число, не строку; select требует `{ "name": "..." }`

---

## Проблема 7: 502/503 Server Error

**Симптомы:** HTTP 502 Bad Gateway или 503 Service Unavailable
**Причина:** Сервер Notion временно недоступен.
**Решение:**
1. Подожди 30-60 секунд и повтори запрос
2. JS SDK автоматически повторяет (retry встроен)
3. Проверь статус Notion: https://status.notion.so/

---

## Проблема 8: Search не находит новые страницы

**Симптомы:** `POST /v1/search` возвращает пустые results для недавно созданных страниц.
**Причина:** Асинхронная индексация (задержка до нескольких минут).
**Решение:**
1. Для поиска по конкретной БД -- используй `POST /databases/{id}/query` (работает мгновенно)
2. Для гарантированного доступа -- обращайся по ID: `GET /pages/{id}`
3. Страницы, явно расшаренные с интеграцией, гарантированно появятся в search

---

## Проблема 9: Пустой результат query

**Симптомы:** `{ "results": [], "has_more": false }` при запросе к БД с данными.
**Причина:** Слишком строгий фильтр или неверное имя свойства.
**Решение:**
1. Убери filter и проверь что данные есть
2. Проверь точное имя свойства (case-sensitive: "Status" != "status")
3. Для date -- используй ISO 8601 формат: `"2026-02-15"`, не `"15.02.2026"`
4. Для select/status -- значение должно точно совпадать: `{ "equals": "Active" }`

---

## Проблема 10: MCP не подключается

**Симптомы:** Claude Code не видит Notion MCP tools.
**Решение:**
1. **Hosted MCP:** `claude mcp add --transport http notion https://mcp.notion.com/mcp` -- авторизуйся в браузере
2. **Open-Source:** Проверь `NOTION_TOKEN` в env, проверь что npx доступен
3. Перезапусти Claude Code/Desktop после изменения конфигурации
4. Проверь что интеграция подключена к нужным страницам в Notion

---

## Проблема 11: Webhook не приходит

**Симптомы:** Endpoint не получает POST от Notion.
**Причина:** URL не прошёл верификацию, endpoint недоступен, или подписка не активна.
**Решение:**
1. Проверь что URL -- HTTPS и публично доступен (не localhost)
2. Пройди верификацию: получи verification_token, введи в UI интеграции
3. Проверь что endpoint возвращает 200 OK
4. Проверь список подписок: My Integrations > Webhooks
5. Webhook payload НЕ содержит данных -- это только сигнал. Для данных делай follow-up API call

---

## Проблема 12: Формула возвращает ошибку

**Симптомы:** Свойство formula показывает ошибку в Notion UI.
**Причина:** Синтаксическая ошибка или несовместимость типов.
**Решение:**
1. Формулы 2.0 не совместимы с 1.0 -- `if()` вместо `if` и `.prop("Name")` vs `prop("Name")`
2. Через API expression возвращается во **внутреннем формате** (`{{notion:block_property:ID:...}}`), а не в читаемом
3. Формула может возвращать только ОДИН тип данных
4. Max глубина: 10 связанных таблиц

---

## Проблема 13: Relation не создаётся

**Симптомы:** Ошибка при создании relation property через API.
**Причина:** Связанная БД не расшарена с интеграцией.
**Решение:**
1. Расшарь ОБЕ базы данных с интеграцией
2. В API v2025-09-03 используй `data_source_id` (не `database_id`) для write operations
3. Для two-way relation: Notion автоматически создаст synced property в связанной БД

---

## Проблема 14: Pagination обрывается

**Симптомы:** Получены не все записи из БД.
**Причина:** Не обработан `has_more` / `next_cursor`.
**Решение:**
```javascript
// Правильная пагинация
const { collectPaginatedAPI } = require("@notionhq/client");
const allResults = await collectPaginatedAPI(notion.databases.query, {
  database_id: "...",
});
```
Или вручную:
```javascript
let cursor = undefined;
const all = [];
do {
  const res = await notion.databases.query({
    database_id: "...",
    start_cursor: cursor,
  });
  all.push(...res.results);
  cursor = res.has_more ? res.next_cursor : undefined;
} while (cursor);
```

---

## Проблема 15: SDK TypeError

**Симптомы:** `TypeError` при вызове SDK метода.
**Причина:** Несовместимая версия SDK с API version или неверные типы параметров.
**Решение:**
1. Обнови JS SDK: `npm update @notionhq/client` (текущая v5.9.0)
2. Обнови Python SDK: `pip install --upgrade notion-client` (текущая v2.7.0)
3. Используй type guards: `isFullPage(result)` перед обращением к `result.properties`
4. Проверь что `Notion-Version` соответствует версии SDK

---

## Проблема 16: Нет эндпоинта для шаринга страниц

**Симптомы:** Нужно расшарить страницу с пользователем через API.
**Причина:** API не имеет эндпоинта для управления sharing/permissions.
**Решение:**
Шаринг возможен только через UI Notion или SCIM API (Enterprise). Это архитектурное ограничение API. Workaround: создавай страницу в уже расшаренной БД -- она автоматически унаследует доступ.
