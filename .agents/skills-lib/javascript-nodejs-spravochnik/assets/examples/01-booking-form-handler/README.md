# 01 - Booking Form Handler

Полнофункциональный обработчик форм бронирования с валидацией, сохранением в базу данных и отправкой уведомлений.

## Использование

Идеален для туристических операторов, экскурсионных компаний и агентств ОАЭ, которым нужна автоматизация приёма и обработки бронирований.

### Кейс использования

- Приём заявок на экскурсии (сафари, городские туры)
- Сохранение данных клиента в базу
- Автоматическая отправка подтверждения по email
- Логирование и аналитика

## Установка

```bash
npm install
```

## Environment Variables

```bash
cp .env.example .env
# Настроить:
# - DATABASE_URL
# - SENDGRID_API_KEY (или SMTP параметры)
# - SECRET_KEY для CSRF
```

## Запуск

### Разработка
```bash
npm run dev
```

### Production
```bash
npm start
```

## API Endpoints

### POST /bookings
Создать новое бронирование

**Request:**
```json
{
  "customerName": "Ahmed Al-Mansouri",
  "email": "ahmed@example.com",
  "phone": "+971501234567",
  "tourType": "desert-safari",
  "date": "2026-02-15",
  "adults": 2,
  "children": 1,
  "specialRequests": "Vegetarian meals needed"
}
```

**Response (201):**
```json
{
  "id": "bk_123456",
  "status": "confirmed",
  "confirmationCode": "DBX-2026-001",
  "createdAt": "2026-02-04T10:30:00Z"
}
```

### GET /bookings/:id
Получить детали бронирования

### PUT /bookings/:id
Обновить статус бронирования

### GET /bookings
Список всех бронирований (с фильтрацией по дате, статусу)

## Testing

```bash
npm test
```

## Features

- ✅ Валидация данных на frontend и backend
- ✅ CSRF защита
- ✅ Сохранение в PostgreSQL/MongoDB
- ✅ Email уведомления
- ✅ Логирование событий
- ✅ Rate limiting
- ✅ Unit и Integration тесты

## Структура

```
├── index.js              # Основной Express сервер
├── routes/
│   └── bookings.js       # REST endpoints для бронирований
├── models/
│   └── Booking.js        # Database model
├── middleware/
│   ├── validation.js     # Валидация данных
│   ├── auth.js          # CSRF protection
│   └── errorHandler.js  # Обработка ошибок
├── services/
│   ├── bookingService.js # Бизнес логика
│   └── emailService.js   # Отправка писем
└── utils/
    ├── logger.js         # Логирование
    └── database.js       # Подключение к БД
```

## Production Checklist

- [ ] Настроен SSL/TLS
- [ ] Переменные окружения защищены
- [ ] Database backup настроен
- [ ] Email сервис готов
- [ ] Rate limiting включён
- [ ] Логи собираются (Sentry, CloudWatch, etc.)
- [ ] Monitoring настроен
- [ ] API документация готова

## Дополнительные ресурсы

- [Express documentation](https://expressjs.com)
- [Database connection pooling](https://www.postgresql.org/docs/current/runtime-config-connection.html)
- [Email best practices](https://sendgrid.com/blog/email-best-practices/)
