---
name: database-sql-spravochnik
description: "Используй когда пользователь спрашивает о SQL, базах данных, PostgreSQL. При запросе о схемах БД, запросах, ORM, Prisma, оптимизации SQL для туристических систем. Активируй при вопросах о проектировании таблиц, индексах, миграциях."
---
# Database & SQL Справочник

**Версия:** 1.0.0
**Последнее обновление:** 2026-02-04
**Статус:** Production Ready
**Целевая аудитория:** Backend-разработчики, туристические системы

---

## 1. Overview

Полный справочник SQL и баз данных для туристического бизнеса, сфокусированный на PostgreSQL. Охватывает всё от базовых концепций до продвинутых техник оптимизации.

**Что входит:**
- 13 готовых schemas для туризма
- Примеры запросов для реальных сценариев
- Интеграция с PostgreSQL, ORM (Prisma)
- Best practices и паттерны
- Полный lifecycle управления данными

**Основные кейсы:**
- Управление экскурсиями и ценообразованием
- Системы бронирования
- Аналитика продаж
- Клиентские базы
- Управление яхтами и автомобилями

---

## 2. Quick Start

### Подключение к PostgreSQL

**Установка драйвера:**
```bash
# Node.js
npm install pg

# Python
pip install psycopg2-binary
```

**Подключение в Node.js:**
```javascript
const { Client } = require('pg');

const client = new Client({
  user: 'your_user',
  password: 'your_password',
  host: 'localhost',
  port: 5432,
  database: 'tourism_db'
});

await client.connect();
const res = await client.query('SELECT * FROM tours LIMIT 5');
console.log(res.rows);
await client.end();
```

**Подключение в Python:**
```python
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    database='tourism_db',
    user='your_user',
    password='your_password'
)
cursor = conn.cursor()
cursor.execute('SELECT * FROM tours LIMIT 5')
rows = cursor.fetchall()
cursor.close()
conn.close()
```

**Базовая проверка:**
```sql
SELECT version();
SELECT current_user, current_database();
```

---

## 3. Schemas для Туризма (Обзор 13)

### 3.1 Tours Schema
Основная таблица экскурсий с информацией о названии, описании, ценах и расписании.

```sql
CREATE TABLE tours (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  base_price DECIMAL(10, 2),
  currency VARCHAR(3) DEFAULT 'AED',
  duration_hours INT,
  max_participants INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 Bookings Schema
Система бронирования с отслеживанием статуса и клиентов.

```sql
CREATE TABLE bookings (
  id SERIAL PRIMARY KEY,
  tour_id INT REFERENCES tours(id),
  customer_id INT REFERENCES customers(id),
  booking_date DATE NOT NULL,
  participants INT NOT NULL,
  total_price DECIMAL(10, 2),
  status VARCHAR(20) DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.3 Customers Schema
Клиентская база с контактной информацией и историей.

```sql
CREATE TABLE customers (
  id SERIAL PRIMARY KEY,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  email VARCHAR(255) UNIQUE,
  phone VARCHAR(20),
  country VARCHAR(100),
  total_bookings INT DEFAULT 0,
  lifetime_value DECIMAL(12, 2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.4 Vehicles Schema
Управление парком яхт и автомобилей.

```sql
CREATE TABLE vehicles (
  id SERIAL PRIMARY KEY,
  type VARCHAR(50), -- 'yacht', 'car'
  model VARCHAR(100),
  capacity INT,
  hourly_rate DECIMAL(10, 2),
  daily_rate DECIMAL(10, 2),
  status VARCHAR(20) DEFAULT 'available',
  last_maintenance TIMESTAMP
);
```

### 3.5 Payments Schema
История платежей и транзакций.

```sql
CREATE TABLE payments (
  id SERIAL PRIMARY KEY,
  booking_id INT REFERENCES bookings(id),
  amount DECIMAL(12, 2),
  currency VARCHAR(3),
  method VARCHAR(50), -- 'cash', 'transfer', 'card'
  status VARCHAR(20) DEFAULT 'pending',
  transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.6 Reviews Schema
Отзывы и рейтинги туров.

```sql
CREATE TABLE reviews (
  id SERIAL PRIMARY KEY,
  tour_id INT REFERENCES tours(id),
  customer_id INT REFERENCES customers(id),
  rating INT CHECK (rating >= 1 AND rating <= 5),
  comment TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.7 Pricing Schema
Динамическое ценообразование и скидки.

```sql
CREATE TABLE pricing_rules (
  id SERIAL PRIMARY KEY,
  tour_id INT REFERENCES tours(id),
  min_participants INT,
  max_participants INT,
  discount_percent DECIMAL(5, 2),
  valid_from DATE,
  valid_to DATE
);
```

### 3.8 Guides Schema
Управление гидами и их рабочими графиками.

```sql
CREATE TABLE guides (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  languages VARCHAR(255),
  rating DECIMAL(3, 2),
  hourly_rate DECIMAL(10, 2),
  available_from TIME,
  available_to TIME
);
```

### 3.9 Schedules Schema
Расписание туров и доступность.

```sql
CREATE TABLE schedules (
  id SERIAL PRIMARY KEY,
  tour_id INT REFERENCES tours(id),
  guide_id INT REFERENCES guides(id),
  scheduled_date DATE NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  status VARCHAR(20) DEFAULT 'available'
);
```

### 3.10 Expenses Schema
Управление расходами и себестоимостью.

```sql
CREATE TABLE expenses (
  id SERIAL PRIMARY KEY,
  tour_id INT REFERENCES tours(id),
  category VARCHAR(100),
  amount DECIMAL(10, 2),
  expense_date DATE,
  description TEXT
);
```

### 3.11 Promotions Schema
Специальные предложения и коды.

```sql
CREATE TABLE promotions (
  id SERIAL PRIMARY KEY,
  code VARCHAR(50) UNIQUE,
  discount_percent DECIMAL(5, 2),
  discount_fixed DECIMAL(10, 2),
  max_uses INT,
  current_uses INT DEFAULT 0,
  valid_from DATE,
  valid_to DATE
);
```

### 3.12 Destinations Schema
Направления и расположение туров.

```sql
CREATE TABLE destinations (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  emirate VARCHAR(100),
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  highlights TEXT
);
```

### 3.13 Analytics Schema
Агрегированные данные для отчётов.

```sql
CREATE TABLE daily_stats (
  id SERIAL PRIMARY KEY,
  date DATE NOT NULL UNIQUE,
  tours_count INT,
  bookings_count INT,
  revenue DECIMAL(12, 2),
  avg_rating DECIMAL(3, 2)
);
```

---

## 4. SQL Fundamentals

### SELECT & WHERE
```sql
-- Базовый SELECT
SELECT id, name, base_price FROM tours;

-- С условиями
SELECT * FROM tours WHERE base_price > 500 AND duration_hours >= 4;

-- DISTINCT значения
SELECT DISTINCT emirate FROM destinations;

-- LIMIT и OFFSET
SELECT * FROM tours ORDER BY base_price DESC LIMIT 10 OFFSET 5;
```

### JOIN операции
```sql
-- INNER JOIN: только совпадающие записи
SELECT t.name, COUNT(b.id) as booking_count
FROM tours t
INNER JOIN bookings b ON t.id = b.tour_id
GROUP BY t.id, t.name;

-- LEFT JOIN: все туры, даже без бронирований
SELECT t.name, COUNT(b.id) as booking_count
FROM tours t
LEFT JOIN bookings b ON t.id = b.tour_id
GROUP BY t.id, t.name;

-- Multiple JOINs
SELECT
  t.name as tour_name,
  c.first_name || ' ' || c.last_name as customer,
  b.participants,
  p.amount
FROM bookings b
INNER JOIN tours t ON b.tour_id = t.id
INNER JOIN customers c ON b.customer_id = c.id
LEFT JOIN payments p ON b.id = p.booking_id;
```

### Агрегация данных
```sql
-- COUNT, SUM, AVG
SELECT
  tour_id,
  COUNT(*) as total_bookings,
  SUM(participants) as total_participants,
  AVG(total_price) as avg_price
FROM bookings
GROUP BY tour_id
HAVING COUNT(*) > 5;

-- GROUP BY с фильтром
SELECT
  DATE(booking_date) as date,
  COUNT(*) as bookings,
  SUM(total_price) as daily_revenue
FROM bookings
WHERE booking_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(booking_date)
ORDER BY date DESC;
```

### Сортировка и ограничения
```sql
-- ORDER BY multiple columns
SELECT * FROM tours
ORDER BY base_price DESC, created_at ASC;

-- TOP N
SELECT name, base_price FROM tours
ORDER BY base_price DESC
LIMIT 5;
```

---

## 5. Advanced Features

### Window Functions
```sql
-- ROW_NUMBER для ранжирования
SELECT
  id, name, base_price,
  ROW_NUMBER() OVER (ORDER BY base_price DESC) as price_rank,
  RANK() OVER (ORDER BY base_price DESC) as price_dense_rank
FROM tours;

-- Running totals
SELECT
  booking_date,
  total_price,
  SUM(total_price) OVER (
    ORDER BY booking_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) as running_total
FROM bookings
ORDER BY booking_date;

-- Partition для груп по категориям
SELECT
  tour_id,
  booking_date,
  participants,
  AVG(participants) OVER (PARTITION BY tour_id) as avg_per_tour
FROM bookings;
```

### CTE (Common Table Expressions)
```sql
-- Рекурсивные запросы и подзапросы
WITH booking_stats AS (
  SELECT
    tour_id,
    COUNT(*) as total_bookings,
    SUM(participants) as total_participants
  FROM bookings
  WHERE booking_date >= CURRENT_DATE - INTERVAL '90 days'
  GROUP BY tour_id
),
top_tours AS (
  SELECT tour_id FROM booking_stats
  WHERE total_bookings > 10
  ORDER BY total_bookings DESC
  LIMIT 5
)
SELECT t.name, bs.total_bookings, bs.total_participants
FROM top_tours tt
JOIN tours t ON tt.tour_id = t.id
JOIN booking_stats bs ON tt.tour_id = bs.tour_id;
```

### JSON операции
```sql
-- Работа с JSON данными
SELECT
  id,
  name,
  jsonb_build_object(
    'price', base_price,
    'duration', duration_hours,
    'capacity', max_participants
  ) as tour_details
FROM tours;

-- Распаковка JSON
SELECT
  id,
  name,
  details->>'price' as price,
  (details->>'duration')::INT as duration_hours
FROM tours
WHERE details->>'price' IS NOT NULL;
```

### Full-Text Search
```sql
-- Полнотекстовый поиск
SELECT
  id, name, description,
  ts_rank(to_tsvector('russian', description),
          plainto_tsquery('russian', 'сафари')) as rank
FROM tours
WHERE to_tsvector('russian', description) @@ plainto_tsquery('russian', 'сафари')
ORDER BY rank DESC;
```

---

## 6. ORM Integration (Prisma)

### Schema в Prisma
```prisma
// prisma/schema.prisma

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model Tour {
  id              Int      @id @default(autoincrement())
  name            String   @db.VarChar(255)
  description     String?
  basePrice       Decimal  @db.Decimal(10, 2)
  currency        String   @default("AED") @db.VarChar(3)
  durationHours   Int?
  maxParticipants Int?
  bookings        Booking[]
  createdAt       DateTime @default(now())

  @@map("tours")
}

model Booking {
  id            Int      @id @default(autoincrement())
  tourId        Int
  tour          Tour     @relation(fields: [tourId], references: [id])
  customerId    Int
  customer      Customer @relation(fields: [customerId], references: [id])
  bookingDate   DateTime @db.Date
  participants  Int
  totalPrice    Decimal  @db.Decimal(10, 2)
  status        String   @default("pending") @db.VarChar(20)
  payments      Payment[]
  createdAt     DateTime @default(now())

  @@map("bookings")
}

model Customer {
  id             Int       @id @default(autoincrement())
  firstName      String?   @db.VarChar(100)
  lastName       String?   @db.VarChar(100)
  email          String    @unique @db.VarChar(255)
  phone          String?   @db.VarChar(20)
  country        String?   @db.VarChar(100)
  totalBookings  Int       @default(0)
  lifetimeValue  Decimal   @default(0) @db.Decimal(12, 2)
  bookings       Booking[]
  createdAt      DateTime  @default(now())

  @@map("customers")
}

model Payment {
  id              Int      @id @default(autoincrement())
  bookingId       Int
  booking         Booking  @relation(fields: [bookingId], references: [id])
  amount          Decimal  @db.Decimal(12, 2)
  currency        String   @db.VarChar(3)
  method          String   @db.VarChar(50)
  status          String   @default("pending") @db.VarChar(20)
  transactionDate DateTime @default(now())

  @@map("payments")
}
```

### Примеры операций
```javascript
// Создание бронирования
const booking = await prisma.booking.create({
  data: {
    tourId: 1,
    customerId: 5,
    bookingDate: new Date(),
    participants: 4,
    totalPrice: 2000,
    status: 'confirmed'
  },
  include: {
    tour: true,
    customer: true
  }
});

// Получение с связанными данными
const tourStats = await prisma.tour.findUnique({
  where: { id: 1 },
  include: {
    _count: {
      select: { bookings: true }
    }
  }
});

// Агрегированный запрос
const stats = await prisma.booking.aggregate({
  where: { bookingDate: { gte: new Date('2026-01-01') } },
  _count: true,
  _sum: { totalPrice: true },
  _avg: { participants: true }
});
```

---

## 7. Best Practices

### Индексирование
```sql
-- Основные индексы
CREATE INDEX idx_bookings_tour ON bookings(tour_id);
CREATE INDEX idx_bookings_customer ON bookings(customer_id);
CREATE INDEX idx_bookings_date ON bookings(booking_date);
CREATE INDEX idx_customers_email ON customers(email);

-- Составной индекс
CREATE INDEX idx_bookings_tour_date ON bookings(tour_id, booking_date);

-- Уникальный индекс
CREATE UNIQUE INDEX idx_promotions_code ON promotions(code);
```

### Нормализация данных
- 1NF: Атомарные значения (нет повторяющихся групп)
- 2NF: Зависит от полного первичного ключа
- 3NF: Нет транзитивных зависимостей

### Безопасность
```sql
-- Prepared Statements (всегда используйте!)
-- Node.js
const result = await client.query(
  'SELECT * FROM tours WHERE id = $1',
  [tourId]
);

-- Роли и права доступа
CREATE ROLE app_user WITH PASSWORD 'secure_password';
GRANT SELECT, INSERT, UPDATE ON tours TO app_user;
GRANT SELECT ON customers TO app_user;
```

### Транзакции
```sql
BEGIN;
  UPDATE tours SET total_bookings = total_bookings + 1 WHERE id = 1;
  INSERT INTO bookings (tour_id, customer_id, ...) VALUES (...);
COMMIT;

-- С обработкой ошибок
BEGIN;
  SAVEPOINT sp1;
  -- operations
  ROLLBACK TO sp1;
COMMIT;
```

---

## 8. Common Patterns для Туризма

### Расчёт цены с скидками
```sql
SELECT
  b.id as booking_id,
  t.name as tour_name,
  b.participants,
  t.base_price,
  (b.participants * t.base_price) as gross_price,
  COALESCE(pr.discount_percent, 0) as discount_percent,
  ((b.participants * t.base_price) *
   (100 - COALESCE(pr.discount_percent, 0)) / 100) as final_price
FROM bookings b
JOIN tours t ON b.tour_id = t.id
LEFT JOIN pricing_rules pr ON
  t.id = pr.tour_id AND
  b.participants BETWEEN pr.min_participants AND pr.max_participants
WHERE b.status = 'confirmed';
```

### Доступность гидов
```sql
SELECT
  g.id,
  g.name,
  COUNT(s.id) as scheduled_tours
FROM guides g
LEFT JOIN schedules s ON g.id = s.guide_id
  AND s.scheduled_date = CURRENT_DATE
  AND s.status = 'confirmed'
GROUP BY g.id, g.name
HAVING COUNT(s.id) < 3;  -- Максимум 3 тура в день
```

### Отчёт по продажам
```sql
SELECT
  DATE_TRUNC('week', b.booking_date)::DATE as week,
  COUNT(*) as bookings_count,
  SUM(b.total_price) as weekly_revenue,
  AVG(b.participants) as avg_participants,
  COUNT(DISTINCT b.customer_id) as unique_customers
FROM bookings b
WHERE b.booking_date >= CURRENT_DATE - INTERVAL '3 months'
GROUP BY DATE_TRUNC('week', b.booking_date)
ORDER BY week DESC;
```

### Клиенты VIP
```sql
WITH customer_stats AS (
  SELECT
    c.id,
    c.first_name,
    c.email,
    COUNT(b.id) as total_bookings,
    SUM(b.total_price) as lifetime_value,
    AVG(r.rating) as avg_rating
  FROM customers c
  LEFT JOIN bookings b ON c.id = b.customer_id
  LEFT JOIN reviews r ON b.tour_id = r.tour_id
    AND c.id = r.customer_id
  GROUP BY c.id
)
SELECT
  id, first_name, email,
  total_bookings, lifetime_value,
  CASE
    WHEN lifetime_value > 5000 AND total_bookings > 5 THEN 'VIP_GOLD'
    WHEN lifetime_value > 2000 THEN 'VIP_SILVER'
    ELSE 'REGULAR'
  END as customer_tier
FROM customer_stats
ORDER BY lifetime_value DESC;
```

---

## 9. Troubleshooting

### Медленные запросы
```sql
-- EXPLAIN ANALYZE для анализа
EXPLAIN ANALYZE
SELECT * FROM bookings WHERE booking_date > CURRENT_DATE - INTERVAL '30 days';

-- Добавьте индексы если нужно
CREATE INDEX idx_bookings_date ON bookings(booking_date);
```

### Блокировки
```sql
-- Найти активные транзакции
SELECT
  pid, usename, application_name, state,
  query, query_start
FROM pg_stat_activity
WHERE state != 'idle';

-- Отменить зависшую транзакцию
SELECT pg_terminate_backend(pid);
```

### Утечки подключений
```sql
-- Проверить количество подключений
SELECT COUNT(*) FROM pg_stat_activity;

-- Максимум подключений
SHOW max_connections;

-- Убить неиспользуемые
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND query_start < CURRENT_TIMESTAMP - INTERVAL '1 hour';
```

---

**Дальнейшее обучение:**
- Смотрите `/references/` для подробных модулей
- Используйте примеры из `/assets/examples/`
- Проверьте `/experience/_index.md` для критических уроков
