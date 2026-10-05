# x-twitter-bot-справочник

Production-ready руководство по X (Twitter) Bot API v2 для автоматизации и создания ботов.

## Структура

```
x-twitter-bot-справочник/
├── SKILL.md              # Основной справочник (~4800 слов)
├── README.md             # Этот файл
└── references/
    ├── faq.md            # 15 часто задаваемых вопросов
    ├── troubleshooting.md # 15 проблем и решений
    └── cheatsheet.md     # Шпаргалка: endpoints, операторы, лимиты
```

## Что покрывает

- **Quick Start** — регистрация, ключи, первый пост за 10 минут
- **Архитектура API v2** — REST + Streaming, тарифы Free/Basic/Pro/Enterprise
- **Аутентификация** — OAuth 2.0 App-only, PKCE, OAuth 1.0a, управление токенами
- **Автопостинг** — текст, медиа, треды, планировщик
- **Filtered Stream** — правила, операторы, reconnect, реалтайм
- **Search API** — recent search, full-archive, tweet counts
- **DM-автоматизация** — отправка/получение DM, Welcome Message, FAQ-бот
- **Мониторинг** — mentions timeline, keyword tracking
- **Likes, Retweets, Replies** — автоматизация реакций
- **Webhooks** — Account Activity API, CRC, polling-альтернатива
- **FSM для DM-ботов** — состояния диалога, бронирование через DM
- **Rate Limits** — детальные лимиты по endpoint и тарифу
- **Примеры для туризма ОАЭ** — автопостинг акций, мониторинг #Dubai, DM-бот
- **Деплой** — Python, Node.js, Serverless, Docker
- **Библиотеки** — tweepy, twitter-api-v2, twikit

## Когда использовать

- Создание бота для X/Twitter
- Автоматизация постинга
- Мониторинг упоминаний и ключевых слов
- DM-автоматизация для клиентского сервиса
- Интеграция X API v2 в существующие системы

## Актуальность

Данные актуальны на 2025-2026. Учтены:
- Pay-Per-Use пилот (декабрь 2025)
- Media Upload v2 endpoints (январь 2025)
- Текущие тарифы и лимиты

## Связанные справочники

- `x-twitter-справочник` — платформа X как маркетинговый канал (не бот)
- `telegram-bot-справочник` — боты для Telegram
- `whatsapp-bot-справочник` — боты для WhatsApp
- `instagram-bot-справочник` — боты для Instagram
