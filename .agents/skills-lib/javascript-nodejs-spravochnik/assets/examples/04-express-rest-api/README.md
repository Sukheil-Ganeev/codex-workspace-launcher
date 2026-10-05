# 04 - Express REST API

Полнофункциональный REST API с аутентификацией, валидацией и документацией.

## Кейсы использования

- Tours CRUD операции
- Users management
- Authentication & Authorization
- Pagination & filtering

## Установка

```bash
npm install
npm run dev
```

## API Endpoints

- GET /api/tours - Список туров
- POST /api/tours - Создать тур
- GET /api/tours/:id - Детали тура
- PUT /api/tours/:id - Обновить тур
- DELETE /api/tours/:id - Удалить тур
- POST /api/auth/login - Вход
- POST /api/auth/register - Регистрация

## Features

- ✅ JWT authentication
- ✅ Input validation (Joi)
- ✅ Error handling
- ✅ Pagination
- ✅ Filtering & sorting
- ✅ CORS security
- ✅ Rate limiting
