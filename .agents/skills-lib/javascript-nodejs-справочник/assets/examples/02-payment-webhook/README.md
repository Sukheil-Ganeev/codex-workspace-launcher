# 02 - Payment Webhook Handler

Secure webhook processor для платёжных систем (Stripe, PayPal, 2Checkout) с верификацией и логированием.

## Кейсы использования

- Обработка платежей за экскурсии и туры
- Синхронизация статуса платежей с базой данных
- Отправка уведомлений клиентам
- Безопасная верификация webhook подписей

## Установка

```bash
npm install
```

## API Endpoints

### POST /webhooks/stripe
Обработать Stripe webhook

### POST /webhooks/paypal
Обработать PayPal webhook

### GET /webhook-status
Статус последних webhooks

## Features

- ✅ Signature verification
- ✅ Idempotency (повторные запросы игнорируются)
- ✅ Retry logic
- ✅ Database sync
- ✅ Email notifications
- ✅ Logging & monitoring

## Production Setup

Использовать инструменты мониторинга:
- Sentry для ошибок
- DataDog для метрик
- CloudWatch для логов
