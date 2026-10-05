# facebook-messenger-bot-справочник

Production-ready руководство по Facebook Messenger Platform для создания ботов.

## Структура

```
facebook-messenger-bot-справочник/
├── SKILL.md                    # Основной справочник (~4800 слов)
├── README.md                   # Этот файл
└── references/
    ├── faq.md                  # Часто задаваемые вопросы (20 вопросов)
    ├── troubleshooting.md      # Решение проблем (15 проблем)
    └── cheatsheet.md           # Шпаргалка (все API на одном листе)
```

## Что внутри

### SKILL.md — 20 разделов

1. Quick Start — создание бота за 15 минут
2. Архитектура — Send/Receive API, Graph API v22.0
3. Аутентификация — Page Access Token, App Secret, permissions
4. Получение сообщений — Webhook events, X-Hub-Signature-256
5. Отправка сообщений — Send API, Sender Actions, messaging_type
6. Шаблоны — Generic, Button, Receipt, Media, Airline (Boarding Pass + Itinerary)
7. Кнопки — URL, Postback, Call, Login/Logout, WebView
8. Quick Replies — быстрые ответы (до 13), email/phone
9. Persistent Menu — постоянное меню (3 уровня)
10. Get Started — приветственный экран, Greeting
11. Ice Breakers — FAQ на стартовом экране (до 4)
12. Handover Protocol — передача live-оператору
13. One-Time Notification — разовое уведомление вне 24ч
14. Recurring Notifications — подписка на рассылки
15. Webhooks — настройка, безопасность, retry policy
16. Состояния диалога — FSM, интеграция wit.ai
17. Rate Limits — лимиты API и 24-Hour Messaging Policy
18. Примеры для туризма ОАЭ — каталог, чек, FAQ
19. Деплой — Node.js, Python, Serverless
20. Библиотеки — Bottender, Botpress, pymessenger

### Ключевые фичи для туризма

- **Airline Templates** — посадочные талоны и маршруты прямо в Messenger
- **Receipt Template** — чеки бронирования с деталями заказа
- **Generic Template** — карусель экскурсий с картинками и кнопками
- **Quick Replies** — быстрый FAQ для туристов
- **Handover Protocol** — бот + живой оператор в одном диалоге

## Использование

Активировать при задачах:
- Создание Facebook Messenger бота
- Настройка webhook для Messenger
- Отправка шаблонов (карусель, чек, посадочный талон)
- Интеграция бота с живым оператором
- Настройка OTN / Recurring Notifications

## Актуальность

- Graph API v22.0 (2025-2026)
- Учтена deprecation Messaging Events API (сентябрь 2025)
- Broadcast API заменён на Recurring Notifications
