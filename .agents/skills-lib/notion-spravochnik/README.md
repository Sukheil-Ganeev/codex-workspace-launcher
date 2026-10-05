# Notion API Справочник

Production-ready руководство по Notion API для туристического бизнеса ОАЭ.

## Быстрый старт

1. Создай интеграцию: https://www.notion.so/profile/integrations
2. Скопируй токен (`ntn_***`)
3. Расшарь нужные страницы/БД с интеграцией
4. Подключи MCP: `claude mcp add --transport http notion https://mcp.notion.com/mcp`

## Структура файлов

```
notion-справочник/
├── SKILL.md                    # Основной справочник (~5000 слов, 12 разделов)
├── README.md                   # Этот файл
├── references/
│   ├── faq.md                  # 15+ часто задаваемых вопросов
│   ├── troubleshooting.md      # 15+ типичных проблем и решений
│   └── cheatsheet.md           # Endpoints, лимиты, коды, property types
└── experience/
    └── _index.md               # Критические уроки (заполняется при использовании)
```

## Навигация по разделам SKILL.md

| # | Раздел | Что найти |
|---|--------|-----------|
| 01 | Обзор, тарифы, лимиты | Цены, API rate limits, версия API |
| 02 | Аутентификация | Internal token, OAuth 2.0, заголовки |
| 03 | Databases API | Endpoints, property types, фильтры, сортировка |
| 04 | Pages и Blocks API | CRUD страниц, типы блоков, rich text |
| 05 | Формулы, Relations, Rollups | 80+ функций, связи, агрегации, формулы для туризма |
| 06 | Search, Users, Comments | Поиск, пользователи, комментарии |
| 07 | SDK (JS/Python) | @notionhq/client, notion-client, примеры кода |
| 08 | Webhooks | 23 event types, подпись, automations, polling |
| 09 | MCP Server | Hosted MCP, Open-Source MCP, настройка Claude |
| 10 | Интеграции | Zapier, Make, n8n, Slack, Google Calendar |
| 11 | Permissions | 5 уровней доступа, Teamspaces, гости, безопасность |
| 12 | CRM/Wiki для туризма ОАЭ | Структура БД, формулы, views, автоматизация |

## Триггеры активации

- `notion api` -- общая работа с Notion API
- `notion база` -- создание/управление базами данных
- `notion crm` -- CRM в Notion для туристического бизнеса
- `notion mcp` -- MCP Server для Claude
- `notion интеграция` -- Zapier/Make/n8n + Notion
- `notion формулы` -- формулы 2.0, relations, rollups

## Актуальность данных

- **API Version:** 2025-09-03
- **Цены:** Февраль 2026 (notion.com/pricing)
- **SDK:** JS v5.9.0, Python v2.7.0
- **MCP:** Hosted (рекомендуемый), Open-Source (not actively maintained)

## Контекст бизнеса

Справочник заточен под семейный туристический бизнес в Дубае:
- **Сухейль** -- экскурсии и билеты
- **Марсель** -- аренда автомобилей и трансферы
- **Муфамад** -- Paramount Yachts (300+ яхт)

Валюты: AED (основная), USD, RUB, KZT, Crypto
Клиенты: туристы из СНГ
Мессенджеры: WhatsApp, Telegram
