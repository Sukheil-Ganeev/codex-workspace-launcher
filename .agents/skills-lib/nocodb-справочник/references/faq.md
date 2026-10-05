# NocoDB -- FAQ (Часто задаваемые вопросы)

> ДАННЫЕ АКТУАЛЬНЫ НА: 2026-02-15

---

### 1. Как получить API Token?

Settings -> Account Settings -> Tokens -> Add New API Token. Токен не истекает. Передавать в заголовке `xc-token: YOUR_TOKEN`.

### 2. Какой заголовок использовать для аутентификации?

`xc-token: YOUR_API_TOKEN` (рекомендуется) или `Authorization: Bearer YOUR_API_TOKEN` (с v0.264.7+). Заголовок `xc-auth` -- deprecated (для JWT Auth Token).

### 3. Чем отличается xc-token от xc-auth?

- `xc-token` -- для API Token (не истекает, рекомендуется)
- `xc-auth` -- для JWT Auth Token (deprecated с v0.205.1, истекает через 10ч)

### 4. Какой URL для API записей?

`/api/v2/tables/{tableId}/records` -- Data API. БЕЗ `/meta/` в пути. Meta API (`/api/v2/meta/...`) -- отдельные endpoints для метаданных.

### 5. Какой лимит записей через API?

По умолчанию `DB_QUERY_LIMIT_DEFAULT=25`. Максимум `DB_QUERY_LIMIT_MAX=1000`. Передавайте `?limit=100&offset=0`.

### 6. Как фильтровать записи через API?

Параметр `where` с синтаксисом `(FieldName,operator,value)`:
```
?where=(Status,eq,Active)~and(Price,gt,100)
```
Операторы: eq, neq, gt, ge, lt, le, like, in, btw, is, isnot, null, notnull.

### 7. NocoDB бесплатный?

Self-hosted -- полностью бесплатный (Sustainable Use License). Cloud: Free план -- $0 (3 редактора, 1000 записей). Платные: от $12/мес (Plus).

### 8. NocoDB vs Airtable -- что выбрать?

NocoDB: self-hosted, дешевле (модель "Pay for 9"), миллионы строк, нет vendor lock-in. Airtable: более развитый UI, больше готовых интеграций, но дороже и нет self-hosted.

### 9. Какую БД использовать?

PostgreSQL рекомендуется для production. SQLite -- только для тестов. MySQL допустим, но PostgreSQL лучше поддерживается.

### 10. Как настроить webhook?

Таблица -> Details -> Webhooks -> Add New Webhook. Выбрать trigger (After Insert/Update/Delete), указать URL, метод, headers. Webhook v3 с NocoDB 2025.06.0.

### 11. Как подключить Telegram бота?

NocoDB Webhook -> n8n Webhook trigger -> Telegram Bot node. n8n отдельного NocoDB Trigger node НЕ имеет, используйте Webhook trigger.

### 12. Как импортировать из Excel/CSV?

Контекстное меню таблицы -> Upload -> CSV/Excel. Автоматический маппинг по именам полей. Или создать новую таблицу из файла.

### 13. Как импортировать из Airtable?

Base -> ... -> Import from Airtable. Нужен Airtable Personal Access Token (scope: data.records:read). Формулы НЕ переносятся.

### 14. Есть ли Google Sheets sync?

Прямого sync нет. Интеграция через n8n, Zapier или Make.com в обе стороны.

### 15. Как сделать бэкап?

PostgreSQL: `docker exec nocodb-db pg_dump -U nocodb nocodb | gzip > backup.sql.gz`. Volumes: tar архивация. Автоматизация через cron (ежедневно в 3:00).

### 16. Какая лицензия у NocoDB?

С января 2026 -- Sustainable Use License (ранее AGPL-3.0). Бесплатное использование и self-hosting. Запрещена коммерческая перепродажа как SaaS.

### 17. Что такое "Pay for 9"?

Модель оплаты NocoDB Cloud: оплата максимум за 9 editor seats, далее все дополнительные пользователи бесплатно. Скидка 20% при годовой оплате.

### 18. Как поменять тип поля?

Нажать на заголовок поля -> Edit field -> изменить тип. Некоторые конвертации могут привести к потере данных (например, Text -> Number).

### 19. Как настроить права доступа?

Workspace level: Owner, Creator, Editor, Commenter, Viewer. View level: Collaborative, Locked, Personal. API Token наследует права пользователя.

### 20. Как работает MCP Server?

Встроен с 2025.09.0 (Desktop: Claude, Cursor) и 2025.10.0 (OAuth: ChatGPT, Claude Web). Работает только с records. Настройка: NocoDB Settings -> Model Context Protocol.

### 21. Есть ли SDK для Python?

Официального нет. Используйте `requests` напрямую или неофициальные: `nocodb` (PyPI), `python-nocodb` (GitHub).

### 22. Как подсчитать связанные записи?

Links field автоматически показывает количество. Для подсчета с условиями -- Rollup с COUNT. Функции COUNTLINKS НЕ существует.

### 23. Какая формула для разницы дат?

`DATETIME_DIFF(date1, date2, "days")`. Не DATEDIFF. Units: "days", "hours", "minutes", "months", "years".

### 24. Можно ли использовать API v3?

API v3 в beta (с 2025.06.0). Доступен для Cloud/Enterprise. Ключевое улучшение: inline linked records в ответах. Для production рекомендуется v2.

### 25. Как обновить NocoDB?

```bash
docker exec nocodb-db pg_dump -U nocodb nocodb > pre-upgrade.sql  # бэкап!
docker compose pull && docker compose up -d
```
Рекомендуется фиксировать версию вместо `latest`.
