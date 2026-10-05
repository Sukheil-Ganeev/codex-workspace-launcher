# NocoDB Справочник -- Опыт и критические уроки

> Заполняется при использовании скилла. Читать при активации!

---

## Критические уроки (топ-5)

### 1. Заголовок аутентификации: xc-token, НЕ xc-auth

API Token передается через заголовок `xc-token`. Заголовок `xc-auth` -- для deprecated JWT Auth Token. Путаница между ними -- самая частая ошибка.

### 2. Endpoint записей БЕЗ /meta/

Data API: `/api/v2/tables/{tableId}/records` -- БЕЗ `/meta/` в пути.
Meta API: `/api/v2/meta/...` -- отдельные endpoints для метаданных (таблицы, поля, views).

### 3. DATETIME_DIFF, не DATEDIFF

Правильное название функции: `DATETIME_DIFF(date1, date2, "days")`. Функции DATEDIFF не существует в NocoDB.

### 4. COUNTLINKS не существует

Для подсчета связанных записей: Links field (автоматический счетчик) или Rollup с функцией COUNT.

### 5. n8n: нет NocoDB Trigger Node

n8n имеет только NocoDB action node (CRUD). Для триггеров: NocoDB Webhook -> n8n Webhook trigger node, или Schedule trigger + NocoDB Get Many.

---

## Частые ошибки из исследований (2026-02-15)

| Ошибочное | Правильное |
|---|---|
| Лицензия AGPL-3.0 | Sustainable Use License (с января 2026) |
| Cloud $8/мес | Free $0, Plus $12/мес (год), Business $24/мес |
| `npx create-nocodb-app` | `npx nocodb` (create-nocodb-app устарел 3+ лет) |
| SDK аргумент 'v2' | SDK аргумент 'noco' (идентификатор workspace) |
| Webhook v3 с 0.250+ | Webhook v3 с 2025.06.0 |
| MCP Server с 2025.05.0 | MCP Server Desktop с 2025.09.0, OAuth с 2025.10.0 |
| Google Sheets прямой sync | Только через n8n/Zapier/Make (прямого sync нет) |
| Make.com нет модуля NocoDB | Make.com ИМЕЕТ нативный модуль (обновлен 2025.11.0) |

---

## Заметки

_Этот раздел заполняется при использовании скилла. Записывайте сюда найденные ошибки, улучшения и паттерны._
