# meta-messenger-bot-справочник

Production-ready руководство по Meta Messenger Platform для создания ботов Instagram DM и Facebook Messenger.

## Структура

```
meta-messenger-bot-справочник/
├── SKILL.md              # Основной справочник (объединённый IG + FB)
├── README.md             # Этот файл
├── references/
│   ├── faq.md            # Часто задаваемые вопросы
│   └── cheatsheet.md     # Шпаргалка по API endpoints и лимитам
└── experience/
    └── _index.md         # Журнал опыта реализации
```

## Что покрывает

- Общая архитектура Meta Messenger Platform (один App, два канала)
- Webhook setup (верификация, X-Hub-Signature-256, retry policy)
- Send API (текст, вложения, шаблоны)
- Общие элементы: Quick Replies, Generic Template, Ice Breakers, Persistent Menu
- Instagram-only: Private Replies, Story Mentions, модерация комментариев
- Facebook-only: Button/Receipt/Airline Templates, OTN, Recurring Notifications, wit.ai NLP, Handover Protocol, WebView
- FSM (конечный автомат диалога)
- Rate limits (IG vs FB)
- Деплой: Node.js, Python FastAPI, AWS Lambda
- **Production patterns** (Section 12): реальные паттерны из VIP-DXB CatalogBot (Phase 20)
  - Multi-platform architecture (TG + VK + IG + WA + FB, shared SQLite WAL)
  - messaging_type, Sender Actions, Get Started, User Profile API
  - Synthetic user_id, form_type by platform, Telegram manager notifications
  - FastAPI webhook pattern, HMAC-SHA256 (shared META_APP_SECRET)
  - Carousel pagination, booking FSM, gotchas & best practices

## Происхождение

Создан путём объединения двух скиллов:
- `instagram-bot-справочник` (DEPRECATED)
- `facebook-messenger-bot-справочник` (DEPRECATED)

## API версия

Graph API **v22.0** (2025-2026)

## Для кого

Туристический бизнес в ОАЭ (Сухейль) — автоматизация DM-продаж экскурсий, билетов, яхт, трансферов.
