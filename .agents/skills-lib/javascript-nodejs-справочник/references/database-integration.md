# Database Integration

Справочник по интеграции баз данных в Node.js приложениях. Покрывает PostgreSQL, Prisma ORM, управление подключениями, CRUD операции и миграции.

---

## 1. PostgreSQL с node-postgres

### Установка

```bash
npm install pg dotenv
```

### Базовое подключение

```javascript
const { Client } = require('pg');

const client = new Client({
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
});

client.connect();
```

### .env файл

```
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tourism_db
```

### Простой query

```javascript
async function getTours() {
  try {
    const result = await client.query('SELECT * FROM tours');
    console.log('Tours:', result.rows);
    return result.rows;
  } catch (error) {
    console.error('Database error:', error);
  }
}
```

### Query с параметрами (защита от SQL-injection)

```javascript
async function getTourById(tourId) {
  const query = 'SELECT * FROM tours WHERE id = $1';
  const result = await client.query(query, [tourId]);
  return result.rows[0];
}

// Использование
const tour = await getTourById(5);
```

---

## 2. Prisma ORM Setup

### Установка

```bash
npm install @prisma/client
npm install -D prisma
npx prisma init
```

### Структура проекта после init

```
project/
├── .env
├── prisma/
│   └── schema.prisma
├── node_modules/
└── src/
    └── index.js
```

### Конфигурация schema.prisma

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
  id          Int     @id @default(autoincrement())
  name        String
  description String?
  price       Float
  duration    Int     // в минутах
  city        String
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  bookings    Booking[]

  @@map("tours")
}

model Customer {
  id        Int     @id @default(autoincrement())
  name      String
  email     String  @unique
  phone     String
  country   String?
  bookings  Booking[]
  createdAt DateTime @default(now())

  @@map("customers")
}

model Booking {
  id          Int     @id @default(autoincrement())
  tourId      Int
  customerId  Int
  bookingDate DateTime @default(now())
  totalPrice  Float
  status      String  @default("pending") // pending, confirmed, completed
  notes       String?

  tour        Tour      @relation(fields: [tourId], references: [id])
  customer    Customer  @relation(fields: [customerId], references: [id])
  createdAt   DateTime  @default(now())
  updatedAt   DateTime  @updatedAt

  @@map("bookings")
}
```

### .env для Prisma

```
DATABASE_URL="postgresql://user:password@localhost:5432/tourism_db"
```

### Инициализация Prisma Client

```javascript
// src/prisma.js
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

module.exports = prisma;
```

---

## 3. Connection Pooling

### node-postgres с Pool

```javascript
const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
  max: 20,              // максимум подключений
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Обработка ошибок пула
pool.on('error', (err) => {
  console.error('Unexpected error on idle client', err);
});

module.exports = pool;
```

### Использование Pool

```javascript
const pool = require('./db');

async function getAllTours() {
  const client = await pool.connect();
  try {
    const result = await client.query('SELECT * FROM tours');
    return result.rows;
  } finally {
    client.release();
  }
}
```

### Prisma Connection Pooling

Prisma автоматически управляет connection pooling:

```prisma
// prisma/schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
  // Prisma использует свой пул по умолчанию
}
```

---

## 4. CRUD Operations

### С Prisma ORM (рекомендуется)

#### CREATE - Создание записи

```javascript
const prisma = require('./prisma');

async function createTour(data) {
  const tour = await prisma.tour.create({
    data: {
      name: data.name,
      description: data.description,
      price: data.price,
      duration: data.duration,
      city: data.city,
    },
  });
  return tour;
}

// Использование
const newTour = await createTour({
  name: 'Desert Safari Dubai',
  description: 'Evening desert safari with dinner',
  price: 89.99,
  duration: 240,
  city: 'Dubai',
});
```

#### READ - Чтение записей

```javascript
// Получить одну запись
async function getTourById(id) {
  const tour = await prisma.tour.findUnique({
    where: { id },
  });
  return tour;
}

// Получить все записи
async function getAllTours() {
  const tours = await prisma.tour.findMany({
    orderBy: { createdAt: 'desc' },
  });
  return tours;
}

// С фильтрацией
async function getToursByCity(city) {
  const tours = await prisma.tour.findMany({
    where: { city },
    take: 10,
  });
  return tours;
}

// С relations (связанные данные)
async function getBookingWithDetails(bookingId) {
  const booking = await prisma.booking.findUnique({
    where: { id: bookingId },
    include: {
      tour: true,
      customer: true,
    },
  });
  return booking;
}
```

#### UPDATE - Обновление записи

```javascript
async function updateTour(id, data) {
  const tour = await prisma.tour.update({
    where: { id },
    data: {
      name: data.name,
      price: data.price,
      // только передаваемые поля обновляются
    },
  });
  return tour;
}

// Использование
await updateTour(5, {
  name: 'Updated Safari Experience',
  price: 99.99,
});
```

#### DELETE - Удаление записи

```javascript
async function deleteTour(id) {
  const tour = await prisma.tour.delete({
    where: { id },
  });
  return tour;
}

// Мягкое удаление (обновление статуса)
async function softDeleteBooking(id) {
  const booking = await prisma.booking.update({
    where: { id },
    data: { status: 'cancelled' },
  });
  return booking;
}
```

---

## 5. Transactions

### Prisma Transactions

```javascript
async function createBookingWithTourCheck(tourId, customerId, totalPrice) {
  // Транзакция: либо все выполнится, либо откатится всё
  const result = await prisma.$transaction(async (prisma) => {
    // Проверка тура
    const tour = await prisma.tour.findUnique({
      where: { id: tourId },
    });

    if (!tour) {
      throw new Error('Tour not found');
    }

    // Проверка клиента
    const customer = await prisma.customer.findUnique({
      where: { id: customerId },
    });

    if (!customer) {
      throw new Error('Customer not found');
    }

    // Создание бронирования
    const booking = await prisma.booking.create({
      data: {
        tourId,
        customerId,
        totalPrice,
        status: 'confirmed',
      },
    });

    // Обновление тура (например, уменьшение свободных мест)
    await prisma.tour.update({
      where: { id: tourId },
      data: { availableSeats: { decrement: 1 } },
    });

    return booking;
  });

  return result;
}

// Использование
try {
  const booking = await createBookingWithTourCheck(1, 5, 89.99);
  console.log('Booking created:', booking);
} catch (error) {
  console.error('Transaction failed:', error.message);
}
```

### node-postgres Transactions

```javascript
const pool = require('./db');

async function transferBalance(fromCustomerId, toCustomerId, amount) {
  const client = await pool.connect();

  try {
    await client.query('BEGIN');

    // Вычитание из первого аккаунта
    await client.query(
      'UPDATE customers SET balance = balance - $1 WHERE id = $2',
      [amount, fromCustomerId]
    );

    // Добавление ко второму аккаунту
    await client.query(
      'UPDATE customers SET balance = balance + $1 WHERE id = $2',
      [amount, toCustomerId]
    );

    await client.query('COMMIT');
    console.log('Transfer completed');
  } catch (error) {
    await client.query('ROLLBACK');
    console.error('Transaction failed:', error);
  } finally {
    client.release();
  }
}
```

---

## 6. Migrations

### Prisma Migrations

```bash
# Создать миграцию после изменения schema.prisma
npx prisma migrate dev --name add_bookings_table

# Выполнить миграции в production
npx prisma migrate deploy

# Просмотр истории миграций
npx prisma migrate status

# Откат последней миграции (dev только)
npx prisma migrate resolve --rolled-back migration_name
```

### Структура миграций

```
prisma/migrations/
├── migration_lock.toml
├── 20240204100000_init/
│   └── migration.sql
├── 20240204110000_add_bookings_table/
│   └── migration.sql
└── 20240204120000_add_customer_phone/
    └── migration.sql
```

### Пример миграции SQL

```sql
-- prisma/migrations/20240204110000_add_bookings_table/migration.sql

CREATE TABLE "bookings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "tourId" INTEGER NOT NULL,
    "customerId" INTEGER NOT NULL,
    "bookingDate" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "totalPrice" DOUBLE PRECISION NOT NULL,
    "status" VARCHAR(255) NOT NULL DEFAULT 'pending',
    "notes" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "bookings_tourId_fkey"
      FOREIGN KEY ("tourId") REFERENCES "tours"("id") ON DELETE RESTRICT,
    CONSTRAINT "bookings_customerId_fkey"
      FOREIGN KEY ("customerId") REFERENCES "customers"("id") ON DELETE RESTRICT
);

CREATE INDEX "bookings_tourId_idx" ON "bookings"("tourId");
CREATE INDEX "bookings_customerId_idx" ON "bookings"("customerId");
```

---

## 7. Best Practices

### Error Handling

```javascript
async function safeQueryTour(id) {
  try {
    const tour = await prisma.tour.findUnique({
      where: { id },
    });

    if (!tour) {
      throw new Error(`Tour ${id} not found`);
    }

    return tour;
  } catch (error) {
    if (error.code === 'P2025') {
      console.error('Record not found');
    } else if (error.code === 'P2002') {
      console.error('Unique constraint violation');
    } else {
      console.error('Database error:', error.message);
    }
    throw error;
  }
}
```

### Использование Indexes

```prisma
// schema.prisma
model Tour {
  id          Int     @id @default(autoincrement())
  name        String  @db.VarChar(255)
  city        String  @index  // Index для быстрого поиска по городу
  price       Float
  createdAt   DateTime @default(now())

  @@index([city, price])  // Составной индекс
  @@unique([name, city])  // Уникальное ограничение
  @@map("tours")
}
```

### Batch Operations

```javascript
// Создание нескольких записей за раз
async function createMultipleTours(toursData) {
  const tours = await prisma.tour.createMany({
    data: toursData,
    skipDuplicates: true,
  });
  return tours;
}

// Использование
await createMultipleTours([
  { name: 'Safari', price: 89, duration: 240, city: 'Dubai' },
  { name: 'Beach Day', price: 59, duration: 480, city: 'Dubai' },
  { name: 'City Tour', price: 49, duration: 180, city: 'Abu Dhabi' },
]);
```

### Pagination

```javascript
async function getPaginatedTours(page = 1, pageSize = 10) {
  const skip = (page - 1) * pageSize;

  const [tours, total] = await Promise.all([
    prisma.tour.findMany({
      skip,
      take: pageSize,
      orderBy: { createdAt: 'desc' },
    }),
    prisma.tour.count(),
  ]);

  return {
    tours,
    pagination: {
      page,
      pageSize,
      total,
      pages: Math.ceil(total / pageSize),
    },
  };
}
```

### Disconnect на выходе

```javascript
process.on('SIGINT', async () => {
  await prisma.$disconnect();
  process.exit(0);
});
```

---

## Быстрая справка

| Операция | node-postgres | Prisma |
|----------|---------------|--------|
| Подключение | `new Client()` | `new PrismaClient()` |
| Query | `client.query(sql, params)` | `prisma.model.findMany()` |
| Insert | Написать INSERT SQL | `prisma.model.create()` |
| Update | Написать UPDATE SQL | `prisma.model.update()` |
| Delete | Написать DELETE SQL | `prisma.model.delete()` |
| Pool | `new Pool()` | Автоматический |
| Миграции | Вручную через SQL | `prisma migrate` |

---

**Дата создания:** февраль 2025
**Версии:** PostgreSQL 13+, Prisma 5+, pg 8+
