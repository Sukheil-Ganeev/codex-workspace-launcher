# viber-bot-справочник

Production-ready руководство по Viber Bot API для туристического бизнеса ОАЭ.

## Структура

```
viber-bot-справочник/
├── SKILL.md              # Основной справочник (16 разделов)
├── README.md             # Этот файл
└── references/
    ├── faq.md            # Часто задаваемые вопросы
    ├── troubleshooting.md # Решение проблем
    └── cheatsheet.md     # Шпаргалка по API
```

## Что внутри SKILL.md

1. **Quick Start** — регистрация, токен, webhook, первое сообщение
2. **Архитектура** — REST API, webhook-only (нет long poll!)
3. **Аутентификация** — X-Viber-Auth-Token, HMAC SHA256
4. **Webhook** — set_webhook, callback types, структуры событий
5. **Отправка сообщений** — send_message, 9 типов (text, picture, video, file, contact, location, sticker, URL, rich_media)
6. **Клавиатуры** — keyboard object, кнопки, ActionType/ActionBody, HTML-текст
7. **Rich Media (карусели)** — карточки с изображениями, описанием и кнопками
8. **Broadcast** — рассылка подписчикам, лимиты (300/запрос, 500 req/10s)
9. **Conversation Started** — welcome message, deep links с контекстом
10. **User Details** — get_user_details, get_online
11. **Состояния диалога** — tracking_data (уникальная фича Viber для FSM!)
12. **Account Info** — get_account_info
13. **Rate Limits** — лимиты API и коммерческая модель
14. **Примеры для туризма ОАЭ** — каталог экскурсий, бронирование, welcome
15. **Деплой** — Node.js, Python, Serverless (AWS Lambda)
16. **Библиотеки** — viber-bot (Node.js), viberbot (Python)

## Ключевые особенности Viber Bot API

- **Только webhook** — нет long polling (в отличие от Telegram)
- **tracking_data** — встроенный механизм состояний (FSM без БД)
- **Rich Media** — нативные карусели для каталогов
- **Коммерческая модель** — с 05.02.2024 боты только на коммерческих условиях
- **10,000 бесплатных bot-initiated сообщений/месяц**
- **HTML в кнопках** — поддержка `<b>`, `<i>`, `<font>`, `<br>`

## Применение для туризма ОАЭ

- Каталог экскурсий через Rich Media карусели
- Бронирование через FSM (tracking_data)
- Рассылки акций через broadcast
- Welcome message с определением языка (ru/en)
- Deep links для маркетинговых кампаний
