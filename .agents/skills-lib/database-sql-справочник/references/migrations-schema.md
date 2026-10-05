# Migrations & Schema - Миграции и управление схемой

**Версия:** 1.0.0
**Уровень:** Intermediate
**Время:** 40 минут

---

## Версионирование БД

### Проблема без миграций

```
Production БД:      Dev БД:         Локальная БД:
Users               Users v1        Users v2
Posts               Comments        Orders
                                    OrderItems
ХАОС!
```

### Решение: Миграции

```
Migration 001: CREATE TABLE users
Migration 002: CREATE TABLE posts
Migration 003: ALTER TABLE posts ADD COLUMN tags
Migration 004: CREATE INDEX idx_posts_date
...
```

**Все БД проходят одинаковый путь: 001 → 002 → 003 → 004 → ...**

---

## Prisma Migrations

### Workflow

```bash
# 1. Изменить prisma/schema.prisma
# 2. Создать миграцию
npx prisma migrate dev --name add_tours_table

# 3. Prisma:
#    - Создаст SQL миграцию
#    - Применит к dev БД
#    - Обновит prisma client

# 4. SQL миграция в prisma/migrations/20260204123456_add_tours_table/migration.sql
```

### Пример миграции

```prisma
// schema.prisma БЫЛО:
model Customer {
  id    Int     @id @default(autoincrement())
  email String  @unique
}

// schema.prisma СТАЛО:
model Customer {
  id        Int     @id @default(autoincrement())
  email     String  @unique
  phone     String?  // Новое поле
  country   String?  // Новое поле
  createdAt DateTime @default(now())  // Новое поле
}
```

```bash
npx prisma migrate dev --name add_customer_fields
```

**Сгенерируется:**
```sql
ALTER TABLE "Customer" ADD COLUMN "phone" TEXT;
ALTER TABLE "Customer" ADD COLUMN "country" TEXT;
ALTER TABLE "Customer" ADD COLUMN "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;
```

### Просмотр миграций

```bash
# Статус
npx prisma migrate status

# История
ls prisma/migrations/
```

---

## Flyway - Альтернатива для raw SQL

### Структура проекта

```
project/
├── flyway/
│   ├── V1__Initial_schema.sql
│   ├── V2__Add_tours_table.sql
│   ├── V3__Add_indexes.sql
│   └── U3__Add_indexes.sql (Undo)
└── ...
```

### SQL миграции

```sql
-- V1__Initial_schema.sql
CREATE TABLE customers (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tours (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  base_price DECIMAL(10, 2) NOT NULL
);

-- V2__Add_bookings_table.sql
CREATE TABLE bookings (
  id SERIAL PRIMARY KEY,
  tour_id INTEGER NOT NULL REFERENCES tours(id),
  customer_id INTEGER NOT NULL REFERENCES customers(id),
  booking_date DATE NOT NULL
);

-- V3__Add_payment_method.sql
ALTER TABLE bookings ADD COLUMN payment_method VARCHAR(50);
```

### Использование Flyway

```bash
# Применить миграции
flyway migrate

# Статус
flyway info

# Откатить на версию
flyway undo
```

---

## Zero-downtime миграции

### Проблема: ALTER TABLE блокирует

```sql
-- ПЛОХО: Блокирует таблицу на 5 минут (если 1M строк)
ALTER TABLE tours ADD COLUMN is_premium BOOLEAN DEFAULT FALSE;
```

### Решение 1: Новая колонка с nullable

```sql
-- Шаг 1: Добавить колонку (быстро, нет блокировки)
ALTER TABLE tours ADD COLUMN is_premium BOOLEAN;

-- Шаг 2: Заполнить данные батчами (без блокировки)
UPDATE tours SET is_premium = FALSE WHERE is_premium IS NULL LIMIT 10000;
-- Повторить пока есть NULL

-- Шаг 3: Добавить DEFAULT и NOT NULL (быстро)
ALTER TABLE tours ALTER COLUMN is_premium SET DEFAULT FALSE;
ALTER TABLE tours ALTER COLUMN is_premium SET NOT NULL;
```

### Решение 2: Индекс CONCURRENTLY

```sql
-- ПЛОХО: Блокирует таблицу
CREATE INDEX idx_tours_active ON tours(is_active);

-- ХОРОШО: Без блокировки (медленнее)
CREATE INDEX CONCURRENTLY idx_tours_active ON tours(is_active);
```

### Решение 3: Переименование без downtime

```sql
-- ПЛОХО: Переименование требует EXCLUSIVE lock
ALTER TABLE old_tours RENAME TO tours;

-- ХОРОШО: Переименование через миграцию с временем
-- 1. Создать новую таблицу
-- 2. Переключить представления
-- 3. Удалить старую таблицу
```

### Решение 4: Изменение типа данных

```sql
-- ПЛОХО: Прямое изменение типа может быть медленно
ALTER TABLE tours ALTER COLUMN base_price TYPE NUMERIC(12, 2);

-- ХОРОШО: Через промежуточную колонку
ALTER TABLE tours ADD COLUMN base_price_new NUMERIC(12, 2);
UPDATE tours SET base_price_new = base_price::NUMERIC(12, 2);
ALTER TABLE tours DROP COLUMN base_price;
ALTER TABLE tours RENAME COLUMN base_price_new TO base_price;
```

---

## Откатывание миграций

### Prisma rollback

```bash
# Откатить последнюю миграцию
npx prisma migrate resolve --rolled-back migration_name

# Затем пересоздать нужную миграцию
npx prisma migrate dev --name fixed_migration
```

### Flyway undo

```bash
# Требует V и U версий
# V1__Create.sql + U1__Create.sql

flyway undo  # Откатит последнюю миграцию
```

---

## Тестирование миграций

### Локальное тестирование

```bash
# Создать тестовую БД
createdb tourism_db_test

# Применить миграции
npx prisma migrate deploy --preview-feature
psql -d tourism_db_test -f prisma/migrations/*/migration.sql

# Проверить структуру
\d tourism_db_test
```

### Валидация миграции

```sql
-- Проверить что индексы созданы
SELECT indexname FROM pg_indexes
WHERE tablename = 'tours';

-- Проверить constraints
SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'tours';

-- Проверить данные после миграции
SELECT COUNT(*) FROM tours;
SELECT COUNT(*) FROM bookings WHERE tour_id IS NULL;
```

---

## Примеры для туризма

### Сценарий 1: Добавление нового поля

```prisma
// schema.prisma
model Tour {
  ...
  // Было только basePrice

  // Добавляем динамическое ценообразование
  minPrice    Decimal?  @db.Decimal(10, 2)
  maxPrice    Decimal?  @db.Decimal(10, 2)
}
```

```bash
npx prisma migrate dev --name add_price_range
```

**Миграция:**
```sql
ALTER TABLE "tours" ADD COLUMN "minPrice" DECIMAL(10,2),
ADD COLUMN "maxPrice" DECIMAL(10,2);

-- Заполнить данные
UPDATE "tours" SET
  "minPrice" = CASE
    WHEN "basePrice" > 1000 THEN "basePrice" * 0.9
    ELSE "basePrice" * 0.8
  END,
  "maxPrice" = "basePrice" * 1.2;
```

### Сценарий 2: Переход на новую таблицу платежей

```sql
-- V5__Refactor_payments.sql

-- 1. Создать новую таблицу с нормализацией
CREATE TABLE payment_methods (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO payment_methods (name)
SELECT DISTINCT payment_method FROM payments;

-- 2. Добавить foreign key
ALTER TABLE payments
ADD COLUMN payment_method_id INTEGER
REFERENCES payment_methods(id);

-- 3. Заполнить данные
UPDATE payments p
SET payment_method_id = (
  SELECT id FROM payment_methods pm
  WHERE pm.name = p.payment_method
);

-- 4. Удалить старую колонку
ALTER TABLE payments DROP COLUMN payment_method;
ALTER TABLE payments ALTER COLUMN payment_method_id SET NOT NULL;
```

### Сценарий 3: История версий БД

```bash
# Посмотреть что изменилось
git log --oneline prisma/migrations/

# Сравнить две версии
git diff HEAD~5 prisma/schema.prisma

# Откатить миграцию, если ошибка
npx prisma migrate resolve --rolled-back add_wrong_field
```

---

## Best practices

1. **Миграции должны быть идемпотентны** - безопасно запускать несколько раз
2. **Одна миграция = одно изменение** - разделяйте логику
3. **Тестируйте миграции локально** - перед production
4. **Версионируйте миграции в git** - все должны использовать один путь
5. **Откатывайте данные перед структурными изменениями** - если надо
6. **Используйте CONCURRENTLY для индексов** - на больших таблицах
7. **Документируйте причину миграции** - в комментариях

---

**Последнее обновление:** 2026-02-04
