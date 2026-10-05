# api-туризм-оаэ Skill

## Описание

Скилл для работы с API в туристическом бизнесе ОАЭ. Покрывает интеграцию REST API, Webhooks, GraphQL, WebSocket для автоматизации бронирований, платежей и уведомлений.

## Структура

```
api-туризм-оаэ/
├── SKILL.md                    # Основной файл (~5000 слов)
├── README.md                   # Этот файл
│
├── references/
│   ├── faq.md                  # Часто задаваемые вопросы
│   ├── troubleshooting.md      # Решение проблем
│   ├── cheatsheet.md           # Быстрая справка
│   └── glossary.md             # Глоссарий терминов
│
├── assets/templates/
│   ├── rest_endpoint.py        # Шаблон REST endpoint (FastAPI)
│   ├── webhook_receiver.py     # Шаблон webhook receiver
│   ├── graphql_query.js        # Шаблон GraphQL query
│   ├── websocket_client.js     # Шаблон WebSocket client
│   ├── auth_api_key.py         # Шаблон аутентификации API Key
│   └── auth_oauth2.py          # Шаблон OAuth2
│
├── assets/examples/
│   ├── whatsapp_autoconfirm.py # Полный пример автоподтверждения
│   ├── stripe_payment_flow.py  # Полный пример оплаты
│   ├── booking_search.py       # Полный пример поиска туров
│   └── google_maps_route.py    # Полный пример маршрута
│
└── scripts/
    ├── test_api_connection.py  # Скрипт проверки подключения
    ├── validate_webhook.py     # Скрипт валидации webhook
    └── rate_limit_checker.py   # Проверка rate limits
```

## Триггеры использования

Claude автоматически использует этот скилл при запросах:

- "интегрируй API", "подключи Stripe"
- "настрой WhatsApp Business API"
- "webhook для платежей"
- "автоматизируй бронирование"
- "отправь сообщение в WhatsApp через API"

## Связанный справочник

Детальная документация: `D:/Downloads/API_СПРАВОЧНИК/`

## Быстрый старт

### Отправка WhatsApp сообщения

```python
# Используй шаблон
from assets.templates.auth_api_key import make_authenticated_request

# Или полный пример
python assets/examples/whatsapp_autoconfirm.py
```

### Webhook для Stripe

```bash
# Запуск сервера
cd assets/templates
uvicorn webhook_receiver:app --reload --port 8000

# Endpoint: http://localhost:8000/webhooks/stripe
```

### Тестирование API

```bash
python scripts/test_api_connection.py https://api.stripe.com/v1/charges sk_test_xxx
```

## Версия

- **Создано:** 2026-02-03
- **Версия:** 1.0.0
- **Автор:** Claude Code для Сухейля
