# Data Types & Constraints - Типы данных и ограничения

**Версия:** 1.0.0
**Уровень:** Intermediate
**Время:** 40 минут

---

## Числовые типы

### INTEGER семейство

```sql
-- SMALLINT (2 bytes): -32768 до 32767
CREATE TABLE test_small (id SMALLINT);

-- INTEGER (4 bytes): -2.1B до 2.1B - САМЫЙ ЧАСТЫЙ
CREATE TABLE guides (id INTEGER PRIMARY KEY);

-- BIGINT (8 bytes): -9.2E18 до 9.2E18
CREATE TABLE analytics (view_count BIGINT);

-- SERIAL - автоинкремент INTEGER
CREATE TABLE tours (id SERIAL PRIMARY KEY);

-- BIGSERIAL - автоинкремент BIGINT
CREATE TABLE events (id BIGSERIAL PRIMARY KEY);
```

### Числа с плавающей точкой

```sql
-- NUMERIC/DECIMAL - точные (рекомендуется для денег!)
CREATE TABLE payments (
  amount NUMERIC(10, 2)  -- 8 цифр до точки, 2 после
);

-- FLOAT4 - приблизительно (быстрее, но не для денег)
CREATE TABLE coordinates (latitude FLOAT4);

-- FLOAT8 - двойная точность (по умолчанию)
CREATE TABLE metrics (value FLOAT8);
```

**ВАЖНО:** Для денег ВСЕГДА используйте NUMERIC/DECIMAL!
```sql
-- ПРАВИЛЬНО
ALTER TABLE bookings ADD COLUMN total_price DECIMAL(10, 2);

-- НЕПРАВИЛЬНО (потеря точности)
ALTER TABLE bookings ADD COLUMN total_price FLOAT;
```

---

## Текстовые типы

### Строки различной длины

```sql
-- CHAR(n) - фиксированная длина, заполняется пробелами
CREATE TABLE countries (code CHAR(2));  -- 'US', 'RU'

-- VARCHAR(n) - переменная длина с лимитом (САМЫЙ ЧАСТЫЙ)
CREATE TABLE customers (
  email VARCHAR(255),
  phone VARCHAR(20),
  country VARCHAR(100)
);

-- TEXT - без лимита (для больших объёмов)
CREATE TABLE tours (
  description TEXT,
  terms_and_conditions TEXT
);

-- VARCHAR без лимита = TEXT
CREATE TABLE notes (comment VARCHAR);
```

**Выбор размера:**
```sql
-- Email - максимум ~254 символа
email VARCHAR(255)

-- Phone - обычно 15-20 символов (E.164)
phone VARCHAR(20)

-- Country - 50 символов достаточно
country VARCHAR(50)

-- Название тура - 255
name VARCHAR(255)

-- Произвольный текст
description TEXT
```

---

## Типы дат и времени

### Основные типы

```sql
-- DATE - только дата (4 bytes)
CREATE TABLE bookings (
  booking_date DATE
);

-- TIME - только время (8 bytes)
CREATE TABLE schedules (
  start_time TIME,
  end_time TIME
);

-- TIMESTAMP - дата и время (8 bytes, без TZ)
CREATE TABLE events (
  created_at TIMESTAMP
);

-- TIMESTAMPTZ - с часовым поясом (рекомендуется!)
CREATE TABLE payments (
  transaction_date TIMESTAMPTZ
);
```

**Лучшая практика:**
```sql
-- Используйте TIMESTAMPTZ для всех временных меток
CREATE TABLE tours (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### Работа с датами

```sql
-- Текущая дата/время
SELECT CURRENT_DATE;        -- '2026-02-04'
SELECT CURRENT_TIME;        -- '14:30:45.123456'
SELECT CURRENT_TIMESTAMP;   -- '2026-02-04 14:30:45.123456+00'

-- Интервалы
SELECT CURRENT_DATE - INTERVAL '30 days';
SELECT CURRENT_TIMESTAMP + INTERVAL '1 week';

-- Части даты
SELECT DATE_PART('year', CURRENT_DATE);    -- 2026
SELECT DATE_PART('month', CURRENT_DATE);   -- 2
SELECT EXTRACT(DAY FROM CURRENT_DATE);     -- 4

-- Сравнения
WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '1 month'
WHERE DATE(created_at) = CURRENT_DATE
```

---

## JSON и JSONB типы

### JSON vs JSONB

```sql
-- JSON - хранит как текст, не индексируется
CREATE TABLE tours_json (
  id SERIAL,
  data JSON
);

-- JSONB - бинарный формат, индексируется (РЕКОМЕНДУЕТСЯ)
CREATE TABLE tours_jsonb (
  id SERIAL,
  details JSONB
);

-- Пример
INSERT INTO tours_jsonb VALUES (
  1,
  '{"rating": 4.5, "reviews": 123, "verified": true}'::jsonb
);
```

### JSONB операции

```sql
-- Поиск по ключу
SELECT * FROM tours WHERE details->>'rating' = '4.5';

-- Содержит ключ
SELECT * FROM tours WHERE details ? 'rating';

-- Поиск по вложенному значению
SELECT * FROM tours
WHERE details @> '{"verified": true}'::jsonb;

-- Получить все ключи
SELECT jsonb_object_keys(details) FROM tours;

-- Создать JSON объект
SELECT jsonb_build_object(
  'tour_id', 1,
  'price', 500,
  'currency', 'AED'
);
```

---

## Boolean тип

### Использование

```sql
-- BOOLEAN (1 byte на value, 1 bit на самом деле)
CREATE TABLE tours (
  id SERIAL,
  is_active BOOLEAN DEFAULT TRUE,
  is_premium BOOLEAN DEFAULT FALSE
);

-- Вставка
INSERT INTO tours (is_active, is_premium) VALUES (TRUE, FALSE);
INSERT INTO tours (is_active) VALUES ('yes');  -- Принимает много форматов
INSERT INTO tours (is_active) VALUES ('1');    -- Тоже работает

-- Фильтр
SELECT * FROM tours WHERE is_premium = TRUE;
SELECT * FROM tours WHERE is_active;           -- Сокращённый синтаксис
SELECT * FROM tours WHERE NOT is_active;
```

---

## Enum тип

### Определение и использование

```sql
-- Создание типа
CREATE TYPE booking_status AS ENUM (
  'pending',
  'confirmed',
  'cancelled',
  'completed'
);

-- Использование
CREATE TABLE bookings (
  id SERIAL PRIMARY KEY,
  status booking_status DEFAULT 'pending'
);

-- Фильтр
SELECT * FROM bookings WHERE status = 'confirmed';

-- Получить все значения (PostgreSQL трюк)
SELECT enum_range(NULL::booking_status);
```

**Преимущества:** Контроль типа, эффективное хранение.

---

## UUID тип

### Генерация и использование

```sql
-- Включить расширение
CREATE EXTENSION uuid-ossp;

-- Использование
CREATE TABLE customers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  external_id UUID UNIQUE
);

-- Вставка
INSERT INTO customers (external_id)
VALUES (uuid_generate_v4());

-- Фильтр
SELECT * FROM customers WHERE id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11';
```

---

## Array типы

### Работа с массивами

```sql
-- Определение
CREATE TABLE guides (
  id SERIAL,
  languages VARCHAR[] DEFAULT ARRAY[]::VARCHAR[],
  experience_years INTEGER[]
);

-- Вставка
INSERT INTO guides (languages) VALUES (ARRAY['English', 'Russian', 'Arabic']);

-- Доступ к элементу
SELECT languages[1] FROM guides;  -- 'English'

-- Длина массива
SELECT array_length(languages, 1) FROM guides;

-- Содержит элемент
SELECT * FROM guides WHERE 'Russian' = ANY(languages);

-- Все элементы содержат
SELECT * FROM guides WHERE languages @> ARRAY['English'];
```

---

## Constraints - Ограничения

### PRIMARY KEY

```sql
-- Уникален и не NULL
CREATE TABLE tours (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);

-- Составной ключ
CREATE TABLE booking_items (
  booking_id INTEGER NOT NULL,
  item_id INTEGER NOT NULL,
  PRIMARY KEY (booking_id, item_id)
);
```

### UNIQUE

```sql
-- Уникальное значение (NULL разрешены)
CREATE TABLE customers (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  passport_number VARCHAR(20) UNIQUE
);

-- Составной UNIQUE
CREATE TABLE schedules (
  tour_id INTEGER NOT NULL,
  date DATE NOT NULL,
  UNIQUE (tour_id, date)
);
```

### NOT NULL

```sql
-- Значение обязательно
CREATE TABLE bookings (
  id SERIAL PRIMARY KEY,
  tour_id INTEGER NOT NULL,
  customer_id INTEGER NOT NULL,
  participants INTEGER NOT NULL
);
```

### DEFAULT

```sql
-- Значение по умолчанию
CREATE TABLE tours (
  id SERIAL PRIMARY KEY,
  currency VARCHAR(3) DEFAULT 'AED',
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- С функцией
CREATE TABLE bookings (
  id SERIAL PRIMARY KEY,
  confirmation_code VARCHAR(20) DEFAULT 'BOOKING-' || CURRENT_TIMESTAMP::TEXT
);
```

### CHECK

```sql
-- Проверка условия
CREATE TABLE tours (
  id SERIAL PRIMARY KEY,
  base_price DECIMAL(10, 2) CHECK (base_price > 0),
  discount_percent DECIMAL(5, 2) CHECK (discount_percent BETWEEN 0 AND 100),
  duration_hours INTEGER CHECK (duration_hours > 0)
);

-- Составной CHECK
CREATE TABLE bookings (
  id SERIAL PRIMARY KEY,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  CHECK (end_date >= start_date)
);
```

### FOREIGN KEY

```sql
-- Связь с другой таблицей
CREATE TABLE bookings (
  id SERIAL PRIMARY KEY,
  tour_id INTEGER NOT NULL REFERENCES tours(id),
  customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE
);

-- С явным именем
ALTER TABLE bookings
ADD CONSTRAINT fk_bookings_tour
FOREIGN KEY (tour_id) REFERENCES tours(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;
```

**ON DELETE/UPDATE параметры:**
- `CASCADE` - удалить/обновить зависимые
- `RESTRICT` - запретить удаление (по умолчанию)
- `SET NULL` - установить NULL
- `SET DEFAULT` - установить значение по умолчанию

---

## Примеры для туризма

### Правильная схема тура

```sql
CREATE TABLE tours (
  id SERIAL PRIMARY KEY,

  -- Текст
  name VARCHAR(255) NOT NULL,
  description TEXT,

  -- Числа (денежные)
  base_price DECIMAL(10, 2) NOT NULL CHECK (base_price > 0),
  currency VARCHAR(3) DEFAULT 'AED',

  -- Числа (обычные)
  duration_hours INTEGER CHECK (duration_hours > 0),
  max_participants INTEGER CHECK (max_participants > 0),

  -- Статусы
  status VARCHAR(20) DEFAULT 'active',

  -- Даты
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

  -- Булевы
  is_premium BOOLEAN DEFAULT FALSE,
  is_seasonal BOOLEAN DEFAULT FALSE,

  -- JSON для гибкости
  metadata JSONB
);
```

### Правильная схема бронирования

```sql
CREATE TABLE bookings (
  id SERIAL PRIMARY KEY,

  tour_id INTEGER NOT NULL REFERENCES tours(id),
  customer_id INTEGER NOT NULL REFERENCES customers(id),

  -- Дата
  booking_date DATE NOT NULL,

  -- Числа
  participants INTEGER NOT NULL CHECK (participants > 0),
  total_price DECIMAL(10, 2) NOT NULL CHECK (total_price >= 0),

  -- Статус
  status booking_status DEFAULT 'pending',

  -- Временные метки
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

---

## Миграция типов

### Изменение типа колонки

```sql
-- Правильно: через промежуточный тип
ALTER TABLE tours
ALTER COLUMN description TYPE TEXT USING description::TEXT;

-- Если невозможно конвертировать
ALTER TABLE tours
ADD COLUMN new_price DECIMAL(12, 2);

UPDATE tours SET new_price = base_price::NUMERIC;
ALTER TABLE tours DROP COLUMN base_price;
ALTER TABLE tours RENAME COLUMN new_price TO base_price;
```

---

**Последнее обновление:** 2026-02-04
