# Indexes & Performance - Индексы и производительность

**Версия:** 1.0.0
**Уровень:** Intermediate
**Время:** 45 минут

---

## Типы индексов

### B-tree (по умолчанию)

```sql
-- Самый универсальный, работает для всех операций сравнения
CREATE INDEX idx_tours_name ON tours(name);
CREATE INDEX idx_bookings_date ON bookings(booking_date);
CREATE INDEX idx_customers_email ON customers(email);

-- Для равенства и диапазонов
CREATE INDEX idx_tours_price ON tours(base_price);
```

### Hash индекс

```sql
-- Только для равенства (=), не для диапазонов
CREATE INDEX idx_customers_email_hash ON customers USING HASH(email);
```

### GIST и GiST

```sql
-- Для текстового поиска и геоданных
CREATE INDEX idx_tours_description ON tours USING GIST(
  to_tsvector('russian', description)
);
```

### BRIN (Block Range Index)

```sql
-- Для очень больших таблиц с упорядоченными данными
CREATE INDEX idx_bookings_date_brin ON bookings USING BRIN(booking_date);
-- Занимает 1/1000 от памяти B-tree!
```

---

## Стратегии индексирования

### Правило 1: Индексируйте Foreign Keys

```sql
-- ОБЯЗАТЕЛЬНО для JOINов
CREATE INDEX idx_bookings_tour_id ON bookings(tour_id);
CREATE INDEX idx_bookings_customer_id ON bookings(customer_id);
CREATE INDEX idx_payments_booking_id ON payments(booking_id);

-- До: 500ms на JOIN
-- После: 5ms на JOIN (100x ускорение)
```

### Правило 2: Индексируйте WHERE колонки

```sql
-- Если часто фильтруете:
WHERE status = 'confirmed'
CREATE INDEX idx_bookings_status ON bookings(status);

-- Если часто по дате:
WHERE booking_date > CURRENT_DATE - INTERVAL '30 days'
CREATE INDEX idx_bookings_date ON bookings(booking_date);
```

### Правило 3: Составные индексы для частых комбинаций

```sql
-- Часто запрашиваете: tour_id И booking_date
CREATE INDEX idx_bookings_tour_date
ON bookings(tour_id, booking_date);

-- Вместо двух отдельных индексов:
-- CREATE INDEX idx_tour ON bookings(tour_id);
-- CREATE INDEX idx_date ON bookings(booking_date);
```

**Порядок в составном индексе важен:**
```sql
-- Хорошо для: WHERE tour_id = X AND date > Y
CREATE INDEX idx_tour_date ON bookings(tour_id, booking_date DESC);

-- Плохо для: WHERE tour_id = X AND date > Y (но хорошо для дате отдельно)
CREATE INDEX idx_date_tour ON bookings(booking_date, tour_id);
```

### Правило 4: Partial индекс для фильтров

```sql
-- Если часто ищете только активные туры
CREATE INDEX idx_tours_active ON tours(id)
WHERE status = 'active';

-- Использует 1/10 памяти полного индекса
-- Но работает только для WHERE status = 'active'
```

---

## EXPLAIN и анализ запросов

### EXPLAIN - план выполнения

```sql
EXPLAIN
SELECT * FROM bookings WHERE customer_id = 123;
```

**Вывод:**
```
Index Scan using idx_bookings_customer_id on bookings (cost=0.29..8.30 rows=12 width=32)
  Index Cond: (customer_id = 123)
```

### EXPLAIN ANALYZE - реальное выполнение

```sql
EXPLAIN ANALYZE
SELECT * FROM bookings WHERE customer_id = 123;
```

**Вывод:**
```
Index Scan using idx_bookings_customer_id on bookings (cost=0.29..8.30 rows=12 width=32)
  (actual time=0.015..0.045 rows=12 loops=1)
Planning Time: 0.123 ms
Execution Time: 0.067 ms
```

### Что ищут в плане

```
1. Seq Scan = ПЛОХО (читает всё)
   → Добавьте индекс

2. Index Scan = ХОРОШО (читает по индексу)

3. Bitmap Index Scan = ХОРОШО (для multiple indxes)

4. cost=X..Y = ожидаемая стоимость в page fetches
   → Чем меньше, тем лучше

5. rows=X = ожидаемое количество строк
   → Если actual отличается на 100x - есть проблема

6. loops=X = сколько раз выполнилось
   → Цикл в запросе?
```

---

## Оптимизация запросов

### Проблема: N+1 Query

```javascript
// МЕДЛЕННО: N+1 запрос
const tours = await getTours();
for (const tour of tours) {
  tour.bookings = await getBookings(tour.id);  // N дополнительных запросов
}

// БЫСТРО: 1 запрос
const tours = await prisma.tour.findMany({
  include: { bookings: true }  // 1 JOIN вместо N
});
```

### Проблема: Неиспользуемые колонки

```sql
-- МЕДЛЕННО: берет все колонки
SELECT * FROM bookings;

-- БЫСТРО: только нужные колонки
SELECT id, tour_id, customer_id, participants FROM bookings;

-- Особенно если есть TEXT:
SELECT * FROM tours;  -- description TEXT может быть 10KB
SELECT id, name, base_price FROM tours;  -- Только что нужно
```

### Проблема: Функции в WHERE

```sql
-- МЕДЛЕННО: индекс не используется
SELECT * FROM bookings
WHERE EXTRACT(MONTH FROM booking_date) = 2;

-- БЫСТРО: используется индекс
SELECT * FROM bookings
WHERE booking_date >= '2026-02-01'
  AND booking_date < '2026-03-01';
```

### Проблема: NOT IN на большом наборе

```sql
-- МЕДЛЕННО: проверяет все значения
SELECT * FROM tours
WHERE id NOT IN (
  SELECT tour_id FROM bookings WHERE status = 'cancelled'
);

-- БЫСТРО: LEFT JOIN с NULL проверкой
SELECT DISTINCT t.*
FROM tours t
LEFT JOIN bookings b ON t.id = b.tour_id AND b.status = 'cancelled'
WHERE b.tour_id IS NULL;
```

---

## Maintenance операции

### VACUUM - очистка мёртвых строк

```sql
-- Полная очистка таблицы
VACUUM FULL tours;

-- Автоматическое (по умолчанию)
VACUUM ANALYZE;

-- Без блокировки
VACUUM ANALYZE CONCURRENTLY;
```

**Когда:** После массового DELETE или UPDATE.

### ANALYZE - обновление статистики

```sql
-- Обновить статистику для лучшего плана
ANALYZE tours;

-- Для всех таблиц
ANALYZE;
```

### Переиндексирование

```sql
-- Пересчитать индекс
REINDEX INDEX idx_bookings_date;

-- Всех индексов таблицы
REINDEX TABLE bookings;

-- Без блокировки (медленнее)
REINDEX TABLE CONCURRENTLY bookings;
```

---

## Connection pooling

### Проблема утечки соединений

```
Каждое соединение PostgreSQL = 5-10 MB памяти
1000 соединений = 5-10 GB памяти = краш
```

### PgBouncer конфиг

```ini
[databases]
tourism_db = host=localhost port=5432 dbname=tourism_db

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
min_pool_size = 10
```

### Node.js с pooling

```javascript
const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'tourism_db',
  user: 'app_user',
  password: 'secret',
  max: 20,                      // Maximum connections
  min: 5,                       // Minimum connections
  idleTimeoutMillis: 30000,     // Close idle after 30s
  connectionTimeoutMillis: 2000 // Timeout for new connection
});

// Используйте pool, а не Client
const result = await pool.query('SELECT * FROM tours');
```

---

## Примеры оптимизации для туризма

### Сценарий 1: Список туров с рейтингом

```sql
-- МЕДЛЕННО: N+1 запрос
SELECT * FROM tours;  -- Получить все туры
-- Потом для каждого:
SELECT AVG(rating) FROM reviews WHERE tour_id = X;

-- БЫСТРО: 1 запрос с агрегацией
SELECT
  t.id, t.name, t.base_price,
  COUNT(r.id) as review_count,
  COALESCE(AVG(r.rating), 0) as avg_rating
FROM tours t
LEFT JOIN reviews r ON t.id = r.tour_id
GROUP BY t.id, t.name, t.base_price;

-- Индекс для reviews
CREATE INDEX idx_reviews_tour ON reviews(tour_id);
```

### Сценарий 2: Dashboard с KPI

```sql
-- Материализованное представление для ночного расчёта
CREATE MATERIALIZED VIEW tour_kpi AS
SELECT
  tour_id,
  COUNT(*) as total_bookings,
  SUM(participants) as total_participants,
  SUM(total_price) as revenue,
  AVG(total_price) as avg_booking_value,
  MAX(booking_date) as last_booking
FROM bookings
GROUP BY tour_id;

-- Индекс для быстрого поиска
CREATE INDEX idx_tour_kpi_revenue ON tour_kpi(revenue DESC);

-- Обновлять ночью
REFRESH MATERIALIZED VIEW CONCURRENTLY tour_kpi;
```

### Сценарий 3: Поиск доступных туров

```sql
-- Составной индекс для частого фильтра
CREATE INDEX idx_tours_search
ON tours(emirate, base_price, is_active)
WHERE is_active = true;

-- Быстрый поиск
SELECT * FROM tours
WHERE emirate = 'Dubai'
  AND base_price BETWEEN 500 AND 2000
  AND is_active = true
ORDER BY base_price;
```

---

## Чек-лист производительности

- [ ] Все foreign keys индексированы
- [ ] WHERE колонки имеют индексы
- [ ] Нет Seq Scan в частых запросах
- [ ] EXPLAIN ANALYZE показывает reasonable rows/actual
- [ ] Connection pool настроен (20-30 connections)
- [ ] VACUUM ANALYZE запускается еженедельно
- [ ] Нет N+1 запросов (проверить в ORM)
- [ ] Выбираются только нужные колонки
- [ ] Функции не используются в WHERE
- [ ] Статистика актуальна (pg_stat_statements)

---

**Последнее обновление:** 2026-02-04
