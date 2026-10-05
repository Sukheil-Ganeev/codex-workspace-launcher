# Experience Index - Database SQL Справочник

**Версия:** 1.0.0
**Последнее обновление:** 2026-02-04
**Статус:** Production Ready

---

## Критические уроки (топ-5)

### 1. Всегда используйте Prepared Statements

**Проблема:** SQL Injection атаки - одна из самых серьёзных уязвимостей.

**Решение:** НИКОГДА не подставляйте значения напрямую в SQL:
```javascript
// НЕПРАВИЛЬНО - SQL Injection!
query = `SELECT * FROM users WHERE email = '${email}'`;

// ПРАВИЛЬНО - Prepared Statements
client.query('SELECT * FROM users WHERE email = $1', [email]);
```

**Почему важно:** Даже маленькая ошибка может привести к утечке данных всех клиентов.

---

### 2. Индексируйте ВСЕ foreign keys

**Проблема:** Запросы с JOINами становятся медленнее при росте данных.

**Решение:** Автоматически создавайте индексы:
```sql
-- Для каждого foreign key
CREATE INDEX idx_bookings_tour_id ON bookings(tour_id);
CREATE INDEX idx_bookings_customer_id ON bookings(customer_id);
```

**Результат:** Ускорение JOIN на 10-100x на больших таблицах (1M+ строк).

---

### 3. Всегда проверяйте EXPLAIN ANALYZE перед production

**Проблема:** Запрос быстрый на тесте, но медленный на 10M записей.

**Решение:** Анализируйте план до продакшена:
```sql
EXPLAIN ANALYZE
SELECT * FROM bookings
WHERE booking_date > CURRENT_DATE - INTERVAL '30 days'
AND status = 'confirmed';
```

**Ищите:**
- Seq Scan (= нужен индекс)
- N-ary Tree Scans (= query слишком сложный)
- Memory warnings (= увеличить work_mem)

---

### 4. Не блокируйте таблицу при обновлении

**Проблема:** `ALTER TABLE tours ADD COLUMN` заблокирует всё на несколько минут.

**Решение:** Используйте `CONCURRENTLY` для индексов:
```sql
-- ХОРОШО для большой таблицы
CREATE INDEX CONCURRENTLY idx_tours_created
ON tours(created_at);

-- Для ALTER используйте миграции с нулевым даунтаймом
```

**В production:** Каждая блокировка = потеря клиентов.

---

### 5. Connection pooling - ОБЯЗАТЕЛЕН

**Проблема:** Каждое подключение = 5-10 MB памяти. 1000 запросов = 5-10 GB утёка.

**Решение:** Используйте PgBouncer или встроенный pooling:
```javascript
// Node.js с pooling
const pool = new Pool({
  max: 20,                    // Max connections
  min: 5,                     // Min connections
  idleTimeoutMillis: 30000,   // Kill idle после 30s
  connectionTimeoutMillis: 2000,
});
```

**На production:** Настройте max_connections в PostgreSQL.

---

## Часто встречающиеся ошибки

### Ошибка: N+1 Query Problem
```javascript
// ПЛОХО: N запросов для N туров
const tours = await getTours();
for (const tour of tours) {
  const bookings = await getBookings(tour.id);  // N запросов!
}

// ХОРОШО: 1 запрос
const toursWithBookings = await prisma.tour.findMany({
  include: { bookings: true }  // 1 JOin вместо N запросов
});
```

### Ошибка: Неправильная типизация JSON
```sql
-- ПЛОХО: JSON как TEXT
SELECT json_data::text FROM tours;

-- ХОРОШО: JSONB для поиска и индексирования
SELECT details FROM tours
WHERE details @> '{"premium": true}'::jsonb;
```

### Ошибка: Забыли индексы на новые колонки
```sql
-- После ALTER TABLE, ВСЕГДА добавьте индекс:
ALTER TABLE bookings ADD COLUMN promo_code VARCHAR(50);
CREATE INDEX idx_bookings_promo ON bookings(promo_code);
```

---

## Паттерны, которые работают

### Паттерн 1: Мягкое удаление
```sql
-- Вместо DELETE, добавьте deleted_at
ALTER TABLE tours ADD COLUMN deleted_at TIMESTAMP NULL;

-- При выборе:
SELECT * FROM tours WHERE deleted_at IS NULL;

-- Восстановление просто:
UPDATE tours SET deleted_at = NULL WHERE id = 123;
```

**Преимущества:** Логирование, восстановление, compliance.

### Паттерн 2: Временные срезы (Temporal Tables)
```sql
-- Отслеживайте все изменения
CREATE TABLE tours_history (
  id INT,
  name VARCHAR(255),
  base_price DECIMAL(10,2),
  changed_at TIMESTAMP,
  changed_by VARCHAR(100)
);

-- При каждом UPDATE:
BEFORE UPDATE ON tours
  INSERT INTO tours_history VALUES (old.*, now(), current_user);
```

### Паттерн 3: Денормализация для аналитики
```sql
-- Вместо сложного JOIN каждый раз:
-- Создайте materialized view
CREATE MATERIALIZED VIEW tour_analytics AS
SELECT
  t.id, t.name,
  COUNT(b.id) as bookings_count,
  SUM(b.total_price) as revenue,
  AVG(r.rating) as avg_rating
FROM tours t
LEFT JOIN bookings b ON t.id = b.tour_id
LEFT JOIN reviews r ON t.id = r.tour_id
GROUP BY t.id;

-- Обновляйте по расписанию:
REFRESH MATERIALIZED VIEW CONCURRENTLY tour_analytics;
```

---

## Туристический бизнес - специфические советы

### Совет 1: Сезонность
```sql
-- Добавьте season_id для анализа
ALTER TABLE bookings ADD COLUMN season VARCHAR(20);

-- Индекс для быстрого фильтра
CREATE INDEX idx_bookings_season ON bookings(season, booking_date);
```

### Совет 2: Multi-currency
```sql
-- Храните цену и валюту отдельно
ALTER TABLE bookings
  ADD COLUMN currency VARCHAR(3) DEFAULT 'AED';

-- Индекс для каждой валюты отдельно
CREATE INDEX idx_bookings_aed ON bookings(currency, total_price)
WHERE currency = 'AED';
```

### Совет 3: VIP клиенты
```sql
-- Создайте segment для VIP
ALTER TABLE customers ADD COLUMN segment VARCHAR(50);

-- Быстрый поиск VIP
CREATE INDEX idx_vip ON customers(segment) WHERE segment = 'VIP';
```

---

## Что НЕ делать

1. **Не используйте DELETE без WHERE** - потеряете все данные
2. **Не делайте SELECT *** на больших таблицах - изберёте сеть
3. **Не мигрируйте на production в пик-часы
4. **Не забывайте про ROLLBACK в транзакциях
5. **Не работайте под root пользователем БД

---

## Улучшения, которые нашлись

### Улучшение 1: Batch операции вместо одиночных
```javascript
// МЕДЛЕННО: 1000 INSERT операций
for (const booking of bookings) {
  await insertBooking(booking);
}

// БЫСТРО: 1 batch insert
await prisma.booking.createMany({
  data: bookings,
  skipDuplicates: true
});
```

**Ускорение:** 50-100x для больших наборов.

### Улучшение 2: Кэширование часто запрашиваемых данных
```javascript
// Redis cache для tours
const getTourCached = async (id) => {
  const cached = await redis.get(`tour:${id}`);
  if (cached) return JSON.parse(cached);

  const tour = await db.tours.findUnique({ where: { id } });
  await redis.setex(`tour:${id}`, 3600, JSON.stringify(tour));
  return tour;
};
```

**Результат:** Ускорение 1000x, снизить нагрузку на БД.

---

## Что читать дальше

1. **PostgreSQL документация** - для глубокого понимания
2. **SKILL.md** - основной справочник
3. **references/** - детальные модули по темам

---

## Как добавить новый урок

При нахождении:
- Исправленной ошибки → `experience/fixes/`
- Нового паттерна → `experience/patterns/`
- Предупреждения → `experience/warnings/`

**Команда:**
```
"Запиши это в опыт скилла"
```

---

**Последнее обновление:** 2026-02-04
**Статус:** Active, постоянное улучшение
