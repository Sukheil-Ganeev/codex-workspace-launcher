# NocoDB Справочник

Production-ready руководство по NocoDB API для туристического бизнеса ОАЭ.

## Структура

```
nocodb-справочник/
├── SKILL.md              # Основной справочник (12 разделов)
├── README.md             # Этот файл
├── references/
│   ├── faq.md            # Часто задаваемые вопросы (15+)
│   ├── troubleshooting.md # Решение проблем (15+)
│   └── cheatsheet.md     # Шпаргалка (endpoints, формулы, команды)
└── experience/
    └── _index.md         # Критические уроки (заполняется при использовании)
```

## Разделы SKILL.md

| # | Раздел | Содержание |
|---|--------|-----------|
| 01 | Обзор NocoDB | Архитектура, лицензия, NocoDB vs Airtable, Cloud pricing |
| 02 | Установка | Docker Compose, npm, Railway, Cloud, ENV |
| 03 | API v2 -- Records | CRUD, пагинация, фильтрация, сортировка, rate limit |
| 04 | Fields | 35+ типов полей, JSON форматы, API управления |
| 05 | Views | Grid, Gallery, Kanban, Form, Calendar, Shared Views |
| 06 | Формулы | 55+ функций, готовые формулы для туризма ОАЭ |
| 07 | Links, Lookups, Rollups | Связи, подстановки, агрегации, Links API |
| 08 | Webhooks v3 | Триггеры, payload, Handlebars, автоматизации |
| 09 | SDK и аутентификация | nocodb-sdk, Python, xc-token, MCP Server |
| 10 | Интеграции | n8n, Zapier, Make.com, Telegram, Google Sheets |
| 11 | Self-hosted | Бэкап, обновление, безопасность, деплой |
| 12 | CRM для туризма ОАЭ | 4 таблицы, views, формулы, автоматизация |

## Ключевые факты

- **API:** v2 (stable), аутентификация через `xc-token`
- **Лицензия:** Sustainable Use License (с января 2026)
- **Cloud:** Free $0 | Plus $12/мес | Business $24/мес | Enterprise от $1000/мес
- **Rate Limit:** 5 req/sec, HTTP 429
- **Рекомендуемая БД:** PostgreSQL
- **Лучшая интеграция:** n8n (self-hosted)
- **MCP Server:** с 2025.09.0 (Desktop), 2025.10.0 (OAuth)

## Триггеры активации

- `nocodb api` -- работа с NocoDB API
- `nocodb база` -- создание/управление базами
- `nocodb crm` -- CRM на NocoDB
- `nocodb docker` -- установка и деплой
- `nocodb интеграция` -- n8n/Zapier/Make + NocoDB
- `nocodb формулы` -- формулы и связи
- `nocodb self-hosted` -- бэкап, миграции

## Версия

- **Version:** 1.0
- **Created:** 2026-02-15
- **Данные актуальны на:** 2026-02-15
