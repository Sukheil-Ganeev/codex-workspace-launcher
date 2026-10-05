# 04-fullstack-booking-uae -- Booking API для туризма ОАЭ

Полноценный API для бронирования экскурсий и билетов в парки по ОАЭ.
Стек: Node.js 22 + PostgreSQL 17 + Redis 7.

## Быстрый запуск

```bash
# 1. Скопируй переменные окружения
cp .env.example .env

# 2. Запусти стек
docker compose up -d --wait

# 3. Проверь работу
curl http://localhost:3000/health
```

## API эндпоинты

```bash
# Список всех туров
curl http://localhost:3000/api/tours

# Фильтрация по категории
curl http://localhost:3000/api/tours?category=adventure

# Фильтрация по эмирату
curl http://localhost:3000/api/tours?emirate=Dubai

# Детали тура
curl http://localhost:3000/api/tours/1

# Создание бронирования
curl -X POST http://localhost:3000/api/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "tour_id": 1,
    "customer_name": "Иван Петров",
    "customer_phone": "+79001234567",
    "guests": 2,
    "date": "2026-03-15"
  }'

# Список бронирований
curl http://localhost:3000/api/bookings
```

## Остановка

```bash
docker compose down -v   # остановка + удаление данных
docker compose down      # остановка, данные сохраняются
```

## Структура

```
04-fullstack-booking-uae/
  compose.yml       # Docker Compose стек (app + db + redis)
  Dockerfile         # Multi-stage Node.js (builder + production)
  app.js             # Express.js API (туры, бронирования)
  package.json       # Зависимости
  .env.example       # Шаблон переменных окружения
  README.md          # Документация
```
