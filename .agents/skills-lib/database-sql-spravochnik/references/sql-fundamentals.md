# SQL Fundamentals - Основы SQL

**Версия:** 1.0.0
**Уровень:** Beginner
**Время:** 30 минут

---

## SELECT - Основной оператор

### Базовый синтаксис

```sql
SELECT column1, column2, ... FROM table_name;
```

**Пример:**
```sql
SELECT name, base_price, duration_hours FROM tours;
```

**Все колонки:**
```sql
SELECT * FROM tours;
```

**Поименованные результаты:**
```sql
SELECT
  name AS tour_name,
  base_price AS price_aed,
  duration_hours AS duration
FROM tours;
```

---

## WHERE - Фильтрация данных

### Операторы сравнения

```sql
-- Равно
SELECT * FROM tours WHERE base_price = 500;

-- Не равно
SELECT * FROM tours WHERE status != 'cancelled';

-- Больше, меньше
SELECT * FROM tours WHERE base_price > 1000;
SELECT * FROM tours WHERE duration_hours <= 4;
```

### Логические операторы

```sql
-- AND - все условия должны быть истинны
SELECT * FROM tours
WHERE base_price > 500 AND duration_hours >= 4;

-- OR - хотя бы одно условие истинно
SELECT * FROM tours
WHERE status = 'active' OR status = 'pending';

-- NOT - инверсия условия
SELECT * FROM tours WHERE NOT status = 'cancelled';
```

### IN и BETWEEN

```sql
-- IN - проверка принадлежности списку
SELECT * FROM tours
WHERE emirate IN ('Dubai', 'Abu Dhabi', 'Sharjah');

-- BETWEEN - диапазон значений
SELECT * FROM tours
WHERE base_price BETWEEN 500 AND 2000;
```

### NULL проверки

```sql
-- Есть значение
SELECT * FROM customers WHERE phone IS NOT NULL;

-- Нет значения
SELECT * FROM bookings WHERE notes IS NULL;
```

### LIKE - Поиск по шаблону

```sql
-- Содержит 'Safari'
SELECT * FROM tours WHERE name LIKE '%Safari%';

-- Начинается с 'Dune'
SELECT * FROM tours WHERE name LIKE 'Dune%';

-- Заканчивается на 'Experience'
SELECT * FROM tours WHERE name LIKE '%Experience';

-- Один символ вместо _ (5 букв, первая D)
SELECT * FROM tours WHERE name LIKE 'D____';
```

---

## ORDER BY - Сортировка

### Основная сортировка

```sql
-- По возрастанию (по умолчанию)
SELECT * FROM tours ORDER BY base_price ASC;

-- По убыванию
SELECT * FROM tours ORDER BY created_at DESC;
```

### Множественная сортировка

```sql
-- Сначала по цене, потом по времени
SELECT * FROM tours
ORDER BY base_price DESC, created_at ASC;
```

---

## DISTINCT - Уникальные значения

### Получить уникальные значения

```sql
-- Сколько разных эмиратов?
SELECT DISTINCT emirate FROM destinations;

-- Уникальные статусы бронирований
SELECT DISTINCT status FROM bookings;
```

### С COUNT

```sql
-- Уникальные страны клиентов
SELECT DISTINCT country FROM customers ORDER BY country;
```

---

## LIMIT и OFFSET - Пагинация

### Первые N результатов

```sql
-- Топ 5 самых дорогих туров
SELECT * FROM tours
ORDER BY base_price DESC
LIMIT 5;
```

### Пропустить строки (для пагинации)

```sql
-- Страница 1 (записи 0-9)
SELECT * FROM tours LIMIT 10 OFFSET 0;

-- Страница 2 (записи 10-19)
SELECT * FROM tours LIMIT 10 OFFSET 10;

-- Страница 3 (записи 20-29)
SELECT * FROM tours LIMIT 10 OFFSET 20;
```

**Расчёт OFFSET:** `(page_number - 1) * page_size`

---

## JOIN - Объединение таблиц

### INNER JOIN - только совпадающие

```sql
-- Получить туры с количеством бронирований
SELECT
  t.name,
  t.base_price,
  COUNT(b.id) AS booking_count
FROM tours t
INNER JOIN bookings b ON t.id = b.tour_id
GROUP BY t.id, t.name, t.base_price;
```

**Диаграмма:**
```
Tours:          Bookings:
┌─────┐         ┌────────┐
│ id  │ ◄─────► │tour_id │
└─────┘         └────────┘
  1  ────────► (1, 1)
  2  ────────► (2, 1)
               (2, 2)
  3  (нет)
```

### LEFT JOIN - все из левой таблицы

```sql
-- Все туры, даже без бронирований
SELECT
  t.name,
  COUNT(b.id) AS booking_count
FROM tours t
LEFT JOIN bookings b ON t.id = b.tour_id
GROUP BY t.id, t.name;
```

**Диаграмма:**
```
Tours:          Bookings:
1 ─────────────► (1, 1)
2 ─────────────► (2, 1), (2, 2)
3 ─────────────► NULL
```

### RIGHT JOIN - все из правой таблицы

```sql
-- Все бронирования, даже если тур удалён
SELECT b.id, t.name, b.participants
FROM tours t
RIGHT JOIN bookings b ON t.id = b.tour_id;
```

### FULL OUTER JOIN - всё из обеих таблиц

```sql
-- Туры И бронирования
SELECT t.name, b.id
FROM tours t
FULL OUTER JOIN bookings b ON t.id = b.tour_id;
```

### Множественные JOINs

```sql
-- Тур, клиент, платёж в одном запросе
SELECT
  t.name AS tour,
  c.first_name || ' ' || c.last_name AS customer,
  b.participants,
  p.amount,
  p.status
FROM bookings b
INNER JOIN tours t ON b.tour_id = t.id
INNER JOIN customers c ON b.customer_id = c.id
LEFT JOIN payments p ON b.id = p.booking_id;
```

---

## GROUP BY и HAVING - Агрегация

### GROUP BY - Группировка

```sql
-- Количество бронирований по турам
SELECT
  tour_id,
  COUNT(*) AS booking_count,
  SUM(participants) AS total_participants
FROM bookings
GROUP BY tour_id;
```

### Агрегирующие функции

```sql
-- Основные функции
SELECT
  COUNT(*) AS total_bookings,      -- Количество
  SUM(total_price) AS revenue,     -- Сумма
  AVG(total_price) AS avg_price,   -- Среднее
  MIN(total_price) AS min_price,   -- Минимум
  MAX(total_price) AS max_price    -- Максимум
FROM bookings;
```

### HAVING - Фильтр после группировки

```sql
-- Только туры с более чем 10 бронированиями
SELECT
  tour_id,
  COUNT(*) AS booking_count
FROM bookings
GROUP BY tour_id
HAVING COUNT(*) > 10
ORDER BY booking_count DESC;
```

**Различие WHERE vs HAVING:**
```sql
-- WHERE - до группировки (быстрее)
SELECT tour_id, COUNT(*)
FROM bookings
WHERE booking_date > CURRENT_DATE - INTERVAL '30 days'
GROUP BY tour_id;

-- HAVING - после группировки
SELECT tour_id, COUNT(*)
FROM bookings
GROUP BY tour_id
HAVING COUNT(*) > 5;
```

---

## Комплексные примеры для туризма

### Пример 1: Топ туры по выручке за месяц

```sql
SELECT
  t.id,
  t.name,
  COUNT(b.id) AS bookings,
  SUM(b.total_price) AS monthly_revenue,
  AVG(b.total_price) AS avg_booking_value
FROM tours t
INNER JOIN bookings b ON t.id = b.tour_id
WHERE b.booking_date >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY t.id, t.name
HAVING COUNT(b.id) > 0
ORDER BY monthly_revenue DESC
LIMIT 10;
```

### Пример 2: Активные клиенты в этом месяце

```sql
SELECT
  c.id,
  c.first_name || ' ' || c.last_name AS full_name,
  c.email,
  COUNT(b.id) AS bookings_this_month,
  SUM(b.total_price) AS spending
FROM customers c
INNER JOIN bookings b ON c.id = b.customer_id
WHERE b.booking_date >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY c.id, c.first_name, c.last_name, c.email
ORDER BY spending DESC;
```

### Пример 3: Проблемные туры (с отменами)

```sql
SELECT
  t.name,
  COUNT(b.id) AS total_bookings,
  COUNT(CASE WHEN b.status = 'cancelled' THEN 1 END) AS cancelled,
  ROUND(
    100.0 * COUNT(CASE WHEN b.status = 'cancelled' THEN 1 END) /
    COUNT(b.id),
    2
  ) AS cancellation_rate
FROM tours t
LEFT JOIN bookings b ON t.id = b.tour_id
GROUP BY t.id, t.name
HAVING COUNT(CASE WHEN b.status = 'cancelled' THEN 1 END) > 0
ORDER BY cancellation_rate DESC;
```

### Пример 4: Месячный доход по направлениям

```sql
SELECT
  d.emirate,
  DATE_TRUNC('month', b.booking_date)::DATE AS month,
  COUNT(b.id) AS bookings,
  SUM(b.total_price) AS revenue,
  AVG(b.participants) AS avg_group_size
FROM bookings b
INNER JOIN tours t ON b.tour_id = t.id
INNER JOIN destinations d ON t.id = d.id
WHERE b.booking_date >= CURRENT_DATE - INTERVAL '3 months'
GROUP BY d.emirate, DATE_TRUNC('month', b.booking_date)
ORDER BY month DESC, revenue DESC;
```

---

## Оптимизация базовых запросов

### Проблема: Медленный SELECT

```sql
-- МЕДЛЕННО: нет индекса
SELECT * FROM bookings WHERE customer_id = 123;

-- Добавьте индекс
CREATE INDEX idx_bookings_customer ON bookings(customer_id);
```

### Проблема: Много данных

```sql
-- МЕДЛЕННО: всё в памяти
SELECT * FROM bookings WHERE status = 'confirmed';

-- ХОРОШО: с LIMIT
SELECT * FROM bookings WHERE status = 'confirmed' LIMIT 1000;
```

### Проблема: Дублирующиеся результаты

```sql
-- МЕДЛЕННО: без DISTINCT может быть дублирование
SELECT customer_id FROM bookings JOIN payments ...

-- ХОРОШО: только уникальные
SELECT DISTINCT customer_id FROM bookings;
```

---

## Практические упражнения

### Упр 1: Найти все туры длительностью 4+ часов
```sql
SELECT name, duration_hours, base_price FROM tours
WHERE duration_hours >= 4
ORDER BY duration_hours DESC;
```

### Упр 2: Клиенты из России или Казахстана
```sql
SELECT first_name, last_name, email, country FROM customers
WHERE country IN ('Russia', 'Kazakhstan')
ORDER BY country, last_name;
```

### Упр 3: Бронирования из последнего месяца
```sql
SELECT id, tour_id, customer_id, total_price FROM bookings
WHERE booking_date >= CURRENT_DATE - INTERVAL '1 month'
ORDER BY booking_date DESC;
```

### Упр 4: Туры без рецензий
```sql
SELECT t.id, t.name FROM tours t
LEFT JOIN reviews r ON t.id = r.tour_id
WHERE r.id IS NULL;
```

### Упр 5: Среднее количество участников по турам
```sql
SELECT
  tour_id,
  AVG(participants) AS avg_participants
FROM bookings
GROUP BY tour_id
ORDER BY avg_participants DESC;
```

---

## Шпаргалка операторов

| Оператор | Описание | Пример |
|----------|---------|--------|
| = | Равно | WHERE price = 500 |
| != или <> | Не равно | WHERE status != 'cancelled' |
| > | Больше | WHERE price > 1000 |
| < | Меньше | WHERE date < '2026-01-01' |
| >= | Больше или равно | WHERE age >= 18 |
| <= | Меньше или равно | WHERE price <= 500 |
| BETWEEN | Диапазон | WHERE price BETWEEN 100 AND 1000 |
| IN | Список | WHERE status IN ('active', 'pending') |
| LIKE | Шаблон | WHERE name LIKE '%Safari%' |
| IS NULL | Пустое значение | WHERE notes IS NULL |
| IS NOT NULL | Не пустое | WHERE phone IS NOT NULL |
| AND | И | WHERE price > 500 AND status = 'active' |
| OR | Или | WHERE status = 'active' OR status = 'pending' |
| NOT | Инверсия | WHERE NOT status = 'cancelled' |

---

**Последнее обновление:** 2026-02-04
