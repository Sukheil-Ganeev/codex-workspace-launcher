# ORM Integration - Интеграция с ORM

**Версия:** 1.0.0
**Уровень:** Intermediate
**Время:** 45 минут

---

## Prisma - Setup и конфигурация

### Инициализация проекта

```bash
npm init -y
npm install @prisma/client
npm install -D prisma

npx prisma init
```

### .env

```env
DATABASE_URL="postgresql://user:password@localhost:5432/tourism_db"
```

### prisma.schema

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
  id              Int       @id @default(autoincrement())
  name            String    @db.VarChar(255)
  description     String?
  basePrice       Decimal   @db.Decimal(10, 2)
  currency        String    @default("AED") @db.VarChar(3)
  durationHours   Int?
  maxParticipants Int?
  totalBookings   Int       @default(0)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt

  bookings        Booking[]
  reviews         Review[]
  schedules       Schedule[]
  expenses        Expense[]

  @@map("tours")
}

model Booking {
  id              Int       @id @default(autoincrement())
  tourId          Int
  customerId      Int
  bookingDate     DateTime  @db.Date
  participants    Int
  totalPrice      Decimal   @db.Decimal(10, 2)
  status          String    @default("pending") @db.VarChar(20)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt

  tour            Tour      @relation(fields: [tourId], references: [id])
  customer        Customer  @relation(fields: [customerId], references: [id])
  payments        Payment[]

  @@index([tourId])
  @@index([customerId])
  @@index([bookingDate])
  @@map("bookings")
}

model Customer {
  id              Int       @id @default(autoincrement())
  firstName       String?   @db.VarChar(100)
  lastName        String?   @db.VarChar(100)
  email           String    @unique @db.VarChar(255)
  phone           String?   @db.VarChar(20)
  country         String?   @db.VarChar(100)
  totalBookings   Int       @default(0)
  lifetimeValue   Decimal   @default(0) @db.Decimal(12, 2)
  createdAt       DateTime  @default(now())

  bookings        Booking[]

  @@index([email])
  @@map("customers")
}

model Payment {
  id              Int       @id @default(autoincrement())
  bookingId       Int
  amount          Decimal   @db.Decimal(12, 2)
  currency        String    @db.VarChar(3)
  method          String    @db.VarChar(50)
  status          String    @default("pending") @db.VarChar(20)
  transactionDate DateTime  @default(now())

  booking         Booking   @relation(fields: [bookingId], references: [id])

  @@index([bookingId])
  @@map("payments")
}

model Review {
  id              Int       @id @default(autoincrement())
  tourId          Int
  customerId      Int
  rating          Int
  comment         String?
  createdAt       DateTime  @default(now())

  tour            Tour      @relation(fields: [tourId], references: [id])

  @@index([tourId])
  @@map("reviews")
}

model Schedule {
  id              Int       @id @default(autoincrement())
  tourId          Int
  guideId         Int?
  scheduledDate   DateTime  @db.Date
  startTime       DateTime  @db.Time
  endTime         DateTime  @db.Time
  status          String    @default("available") @db.VarChar(20)

  tour            Tour      @relation(fields: [tourId], references: [id])

  @@index([tourId])
  @@index([scheduledDate])
  @@map("schedules")
}

model Expense {
  id              Int       @id @default(autoincrement())
  tourId          Int
  category        String    @db.VarChar(100)
  amount          Decimal   @db.Decimal(10, 2)
  expenseDate     DateTime  @db.Date
  description     String?

  tour            Tour      @relation(fields: [tourId], references: [id])

  @@index([tourId])
  @@map("expenses")
}
```

---

## Операции CRUD

### Create - Создание

```javascript
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// Простое создание
const tour = await prisma.tour.create({
  data: {
    name: 'Desert Safari',
    description: 'Amazing dune experience',
    basePrice: 500,
    durationHours: 4,
    maxParticipants: 6
  }
});

// С вложенными отношениями
const booking = await prisma.booking.create({
  data: {
    tourId: 1,
    customerId: 5,
    bookingDate: new Date('2026-02-15'),
    participants: 4,
    totalPrice: 2000,
    status: 'confirmed',
    // Создать вложенный платёж
    payments: {
      create: {
        amount: 2000,
        currency: 'AED',
        method: 'transfer',
        status: 'completed'
      }
    }
  },
  include: {
    payments: true
  }
});

// Массовое создание
const tours = await prisma.tour.createMany({
  data: [
    { name: 'Tour 1', basePrice: 500 },
    { name: 'Tour 2', basePrice: 600 }
  ]
});
```

### Read - Чтение

```javascript
// Получить один
const tour = await prisma.tour.findUnique({
  where: { id: 1 }
});

// Получить первый, совпадающий условию
const tour = await prisma.tour.findFirst({
  where: { status: 'active' }
});

// Получить все
const tours = await prisma.tour.findMany({
  where: {
    basePrice: { gte: 500 },
    maxParticipants: { gte: 4 }
  },
  orderBy: { basePrice: 'desc' },
  take: 10,  // LIMIT
  skip: 0    // OFFSET
});

// С включением вложений
const booking = await prisma.booking.findUnique({
  where: { id: 1 },
  include: {
    tour: true,
    customer: true,
    payments: true
  }
});

// С выборкой только нужных полей
const tours = await prisma.tour.findMany({
  select: {
    id: true,
    name: true,
    basePrice: true,
    // Не выбираем description для экономии памяти
    _count: {
      select: { bookings: true }
    }
  }
});
```

### Update - Обновление

```javascript
// Простое обновление
const tour = await prisma.tour.update({
  where: { id: 1 },
  data: {
    name: 'New Name',
    basePrice: 600
  }
});

// Условное обновление (всё или ничего)
const result = await prisma.tour.updateMany({
  where: { status: 'active' },
  data: { totalBookings: { increment: 1 } }
});

// Upsert - обновить или создать
const tour = await prisma.tour.upsert({
  where: { id: 999 },
  update: { basePrice: 700 },
  create: {
    name: 'New Tour',
    basePrice: 700
  }
});
```

### Delete - Удаление

```javascript
// Простое удаление
const tour = await prisma.tour.delete({
  where: { id: 1 }
});

// Массовое удаление
const result = await prisma.tour.deleteMany({
  where: { status: 'inactive' }
});
```

---

## Миграции

### Создание миграции

```bash
# Изменить schema.prisma, потом:
npx prisma migrate dev --name initial_schema

# Ввести имя миграции
```

### Просмотр статуса

```bash
npx prisma migrate status
```

### Развёртывание миграции

```bash
# Production
npx prisma migrate deploy

# Rollback (локально)
npx prisma migrate resolve --rolled-back <migration_name>
```

### Prisma Studio

```bash
# Интерактивный браузер БД
npx prisma studio
```

---

## Raw queries

### Когда нужны raw queries

```javascript
// Сложный запрос с window functions
const stats = await prisma.$queryRaw`
  SELECT
    tour_id,
    COUNT(*) as bookings,
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) as rank
  FROM bookings
  GROUP BY tour_id
`;

// Параметризованный запрос
const tours = await prisma.$queryRaw`
  SELECT * FROM tours
  WHERE base_price > ${minPrice}
  AND max_participants >= ${minParticipants}
`;
```

### Безопасность параметров

```javascript
// ПРАВИЛЬНО - SQL injection защита
const result = await prisma.$queryRaw`
  SELECT * FROM customers WHERE email = ${email}
`;

// НЕПРАВИЛЬНО - уязвимо
const result = await prisma.$executeRaw(
  `SELECT * FROM customers WHERE email = '${email}'`
);
```

---

## Оптимизация запросов в Prisma

### Избегать N+1

```javascript
// МЕДЛЕННО - N+1 запрос
const tours = await prisma.tour.findMany();
for (const tour of tours) {
  const bookings = await prisma.booking.findMany({
    where: { tourId: tour.id }
  });
  tour.bookings = bookings;
}

// БЫСТРО - 1 запрос
const tours = await prisma.tour.findMany({
  include: { bookings: true }
});

// Ещё лучше - только счётчик
const tours = await prisma.tour.findMany({
  select: {
    id: true,
    name: true,
    _count: { select: { bookings: true } }
  }
});
```

### Bulk операции

```javascript
// МЕДЛЕННО - 1000 INSERT запросов
for (const booking of bookings) {
  await prisma.booking.create({ data: booking });
}

// БЫСТРО - 1 запрос
await prisma.booking.createMany({
  data: bookings,
  skipDuplicates: true
});
```

### Conditional includes

```javascript
// Динамическое include
const includePayments = needsPayments ? { payments: true } : false;

const booking = await prisma.booking.findUnique({
  where: { id: 1 },
  include: {
    tour: true,
    customer: true,
    ...(includePayments && { payments: true })
  }
});
```

---

## Seeding - Заполнение тестовыми данными

### prisma/seed.ts

```typescript
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  // Очистить существующие данные
  await prisma.booking.deleteMany();
  await prisma.review.deleteMany();
  await prisma.tour.deleteMany();
  await prisma.customer.deleteMany();

  // Создать туры
  const tour1 = await prisma.tour.create({
    data: {
      name: 'Desert Safari',
      basePrice: 500,
      durationHours: 4,
      maxParticipants: 6
    }
  });

  // Создать клиентов
  const customer1 = await prisma.customer.create({
    data: {
      firstName: 'Ahmed',
      lastName: 'Al Mansouri',
      email: 'ahmed@example.com',
      country: 'UAE'
    }
  });

  // Создать бронирование
  const booking = await prisma.booking.create({
    data: {
      tourId: tour1.id,
      customerId: customer1.id,
      bookingDate: new Date('2026-02-15'),
      participants: 4,
      totalPrice: 2000,
      status: 'confirmed'
    }
  });

  console.log('Seeding completed', { tour1, customer1, booking });
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
```

### package.json

```json
{
  "scripts": {
    "prisma:seed": "ts-node prisma/seed.ts"
  }
}
```

---

## Error handling

### Уникальные нарушения

```javascript
try {
  await prisma.customer.create({
    data: {
      email: 'duplicate@example.com'
    }
  });
} catch (error) {
  if (error.code === 'P2002') {
    console.log('Email already exists');
  }
}
```

### Foreign key нарушения

```javascript
try {
  await prisma.booking.create({
    data: {
      tourId: 999999,  // Несуществующий тур
      customerId: 1,
      bookingDate: new Date(),
      participants: 2,
      totalPrice: 1000
    }
  });
} catch (error) {
  if (error.code === 'P2003') {
    console.log('Tour does not exist');
  }
}
```

---

## Production practices

1. **Используйте connection pooling** - PgBouncer или встроенный
2. **Кэшируйте часто запрашиваемые данные** - Redis
3. **Оптимизируйте N+1** - всегда проверяйте queries в DevTools
4. **Используйте миграции** - никогда не меняйте БД вручную
5. **Логируйте slow queries** - Prisma логирует по умолчанию

---

**Последнее обновление:** 2026-02-04
