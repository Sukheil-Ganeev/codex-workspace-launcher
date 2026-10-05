# Advanced Queries - Продвинутые запросы

**Версия:** 1.0.0
**Уровень:** Advanced
**Время:** 50 минут

---

## Window Functions

### ROW_NUMBER - Нумерация

```sql
-- Ранжировать туры по цене
SELECT
  id, name, base_price,
  ROW_NUMBER() OVER (ORDER BY base_price DESC) as price_rank
FROM tours;

-- Результат:
-- id  name            price   rank
-- 1   Premium Safari  2500    1
-- 2   Dune Adventure  1500    2
-- 3   City Tour       500     3
```

### RANK vs DENSE_RANK

```sql
-- RANK - с пропусками при ничьих
SELECT
  name, base_price,
  RANK() OVER (ORDER BY base_price DESC) as rank
FROM tours;
-- Price 1000: rank 1
-- Price 1000: rank 1
-- Price 500:  rank 3 (пропуск)

-- DENSE_RANK - без пропусков
SELECT
  name, base_price,
  DENSE_RANK() OVER (ORDER BY base_price DESC) as rank
FROM tours;
-- Price 1000: rank 1
-- Price 1000: rank 1
-- Price 500:  rank 2 (без пропуска)
```

### Running totals и cumulative sums

```sql
-- Накопительная сумма доходов
SELECT
  booking_date,
  total_price,
  SUM(total_price) OVER (
    ORDER BY booking_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) as running_total
FROM bookings
ORDER BY booking_date;

-- booking_date  price  running_total
-- 2026-01-01    500    500
-- 2026-01-02    300    800
-- 2026-01-03    200    1000
```

### PARTITION BY - Группировка в функциях

```sql
-- Средняя цена бронирования ПО ТУРАМ
SELECT
  tour_id,
  booking_date,
  total_price,
  AVG(total_price) OVER (PARTITION BY tour_id) as tour_avg_price,
  AVG(total_price) OVER () as overall_avg_price
FROM bookings;

-- tour_id  date        price   tour_avg   overall_avg
-- 1        2026-01-01  500     750        800
-- 1        2026-01-02  1000    750        800
-- 2        2026-01-03  600     600        800
```

### LAG и LEAD - Предыдущие/следующие значения

```sql
-- Найти день-в-день прирост бронирований
SELECT
  booking_date,
  COUNT(*) as bookings_today,
  LAG(COUNT(*)) OVER (ORDER BY booking_date) as bookings_yesterday,
  COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY booking_date) as daily_growth
FROM bookings
GROUP BY booking_date
ORDER BY booking_date;
```

---

## Common Table Expressions (CTE)

### Базовый CTE

```sql
-- Определить временную таблицу
WITH tour_stats AS (
  SELECT
    tour_id,
    COUNT(*) as total_bookings,
    SUM(total_price) as revenue
  FROM bookings
  GROUP BY tour_id
)
SELECT * FROM tour_stats WHERE total_bookings > 10;
```

### Множественные CTE

```sql
WITH
-- Первый CTE
recent_bookings AS (
  SELECT * FROM bookings
  WHERE booking_date >= CURRENT_DATE - INTERVAL '30 days'
),
-- Второй CTE
booking_stats AS (
  SELECT
    tour_id,
    COUNT(*) as count,
    SUM(total_price) as revenue
  FROM recent_bookings
  GROUP BY tour_id
)
SELECT t.name, bs.count, bs.revenue
FROM tours t
JOIN booking_stats bs ON t.id = bs.tour_id
ORDER BY bs.revenue DESC;
```

### Рекурсивный CTE

```sql
-- Вся иерархия категорий
WITH RECURSIVE category_tree AS (
  -- Base case: корневые категории
  SELECT id, name, parent_id, 0 as level
  FROM categories
  WHERE parent_id IS NULL

  UNION ALL

  -- Рекурсивная часть: дочерние категории
  SELECT c.id, c.name, c.parent_id, ct.level + 1
  FROM categories c
  JOIN category_tree ct ON c.parent_id = ct.id
  WHERE ct.level < 10  -- Безопасность от бесконечной рекурсии
)
SELECT * FROM category_tree ORDER BY level, name;
```

---

## Subqueries - Подзапросы

### Скалярный подзапрос

```sql
-- Получить туры с выше средней ценой
SELECT name, base_price,
  (SELECT AVG(base_price) FROM tours) as avg_price
FROM tours
WHERE base_price > (SELECT AVG(base_price) FROM tours);
```

### IN с подзапросом

```sql
-- Туры с бронированиями
SELECT * FROM tours
WHERE id IN (
  SELECT DISTINCT tour_id FROM bookings
);

-- Туры БЕЗ бронирований (медленно, см. антипаттерны)
SELECT * FROM tours
WHERE id NOT IN (
  SELECT tour_id FROM bookings WHERE tour_id IS NOT NULL
);
```

### EXISTS

```sql
-- Туры, у которых есть положительные отзывы (быстро!)
SELECT * FROM tours t
WHERE EXISTS (
  SELECT 1 FROM reviews
  WHERE tour_id = t.id AND rating >= 4
);
```

### Коррелирующий подзапрос

```sql
-- Для каждого тура: его цена и средняя цена в категории
SELECT
  name, base_price,
  (SELECT AVG(base_price)
   FROM tours t2
   WHERE t2.category = t1.category) as category_avg
FROM tours t1;
```

---

## Full-Text Search

### Базовый поиск

```sql
-- Включить русский язык
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Найти туры содержащие "сафари"
SELECT id, name, description,
  ts_rank(
    to_tsvector('russian', description),
    plainto_tsquery('russian', 'сафари')
  ) as rank
FROM tours
WHERE to_tsvector('russian', description) @@
      plainto_tsquery('russian', 'сафари')
ORDER BY rank DESC;
```

### Индексирование для поиска

```sql
-- Full-text индекс для быстрого поиска
CREATE INDEX idx_tours_search ON tours USING GIST(
  to_tsvector('russian', name || ' ' || COALESCE(description, ''))
);

-- Теперь этот запрос будет быстрым
SELECT * FROM tours
WHERE to_tsvector('russian', name || ' ' || description) @@
      plainto_tsquery('russian', 'сафари')
LIMIT 10;
```

---

## JSON операции

### Базовые операции

```sql
-- Получить поле из JSON
SELECT id, details->>'price' as price FROM tours;

-- Массив в JSON
SELECT * FROM tours
WHERE details @> '{"premium": true}'::jsonb;

-- Получить все ключи
SELECT jsonb_object_keys(details) FROM tours;
```

### Построение JSON

```sql
-- Создать JSON объект
SELECT jsonb_build_object(
  'id', id,
  'name', name,
  'price', base_price,
  'includes', jsonb_build_array('guide', 'transport', 'meals')
) as tour_json
FROM tours LIMIT 1;
```

### JSON агрегирование

```sql
-- Собрать все отзывы тура в JSON массив
SELECT
  tour_id,
  jsonb_agg(
    jsonb_build_object(
      'customer', customer_name,
      'rating', rating,
      'comment', comment
    )
  ) as reviews
FROM reviews
GROUP BY tour_id;
```

---

## Примеры комплексных запросов для туризма

### Пример 1: VIP клиенты с анализом

```sql
WITH customer_lifetime AS (
  SELECT
    c.id,
    c.first_name || ' ' || c.last_name as full_name,
    c.email,
    COUNT(b.id) as total_bookings,
    SUM(b.total_price) as lifetime_value,
    MAX(b.booking_date) as last_booking,
    AVG(r.rating) as avg_rating
  FROM customers c
  LEFT JOIN bookings b ON c.id = b.customer_id
  LEFT JOIN reviews r ON b.tour_id = r.tour_id
  GROUP BY c.id, c.first_name, c.last_name, c.email
)
SELECT
  *,
  CASE
    WHEN lifetime_value > 5000 AND total_bookings > 5 THEN 'VIP_PLATINUM'
    WHEN lifetime_value > 2000 THEN 'VIP_GOLD'
    WHEN lifetime_value > 500 THEN 'VIP_SILVER'
    ELSE 'REGULAR'
  END as tier
FROM customer_lifetime
WHERE lifetime_value > 500
ORDER BY lifetime_value DESC;
```

### Пример 2: Сезонный анализ

```sql
WITH monthly_stats AS (
  SELECT
    EXTRACT(YEAR FROM b.booking_date)::INT as year,
    EXTRACT(MONTH FROM b.booking_date)::INT as month,
    t.id,
    t.name,
    COUNT(b.id) as bookings,
    SUM(b.total_price) as revenue,
    AVG(b.participants) as avg_group_size
  FROM bookings b
  JOIN tours t ON b.tour_id = t.id
  GROUP BY year, month, t.id, t.name
)
SELECT
  year, month, name,
  bookings,
  revenue,
  avg_group_size,
  LAG(revenue) OVER (PARTITION BY name ORDER BY year, month) as prev_month_revenue,
  ROUND(
    100.0 * (revenue - LAG(revenue) OVER (PARTITION BY name ORDER BY year, month)) /
    LAG(revenue) OVER (PARTITION BY name ORDER BY year, month),
    2
  ) as yoy_growth_percent
FROM monthly_stats
ORDER BY year DESC, month DESC, revenue DESC;
```

### Пример 3: Рекомендации туров

```sql
WITH user_tours AS (
  SELECT DISTINCT tour_id FROM bookings WHERE customer_id = 123
),
similar_customers AS (
  SELECT DISTINCT b.customer_id
  FROM bookings b
  WHERE b.tour_id IN (SELECT tour_id FROM user_tours)
    AND b.customer_id != 123
  GROUP BY b.customer_id
  HAVING COUNT(*) >= 2  -- Минимум 2 общих тура
)
SELECT
  t.id, t.name, t.base_price,
  COUNT(*) as times_booked_by_similar
FROM tours t
JOIN bookings b ON t.id = b.tour_id
WHERE b.customer_id IN (SELECT customer_id FROM similar_customers)
  AND t.id NOT IN (SELECT tour_id FROM user_tours)
GROUP BY t.id, t.name, t.base_price
ORDER BY times_booked_by_similar DESC
LIMIT 10;
```

---

## Performance tips для advanced queries

1. **CTE материализуются** - используйте LATERAL для прямой функции
2. **Window functions дешёвые** - часто быстрее чем subqueries
3. **Индексируйте подзапросы** - если IN (SELECT...) используется часто
4. **Избегайте коррелирующих подзапросов** - медленные для больших таблиц
5. **Тестируйте EXPLAIN ANALYZE** - перед production

---

**Последнее обновление:** 2026-02-04
