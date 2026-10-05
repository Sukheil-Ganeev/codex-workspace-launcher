# Transactions & Locking - Транзакции и блокировки

**Версия:** 1.0.0
**Уровень:** Advanced
**Время:** 40 минут

---

## ACID свойства

### Atomicity (Атомарность)

```sql
-- Либо всё, либо ничего
BEGIN;
  UPDATE tours SET total_bookings = total_bookings + 1 WHERE id = 1;
  INSERT INTO bookings (...) VALUES (...);
COMMIT;
-- Если ошибка - оба отката

-- Если один успел, второй нет - откат всего
ROLLBACK;
```

### Consistency (Согласованность)

```sql
-- Все constraint соблюдены
ALTER TABLE bookings
ADD CONSTRAINT fk_tour
FOREIGN KEY (tour_id) REFERENCES tours(id);

-- Нельзя добавить booking с несуществующим tour_id
INSERT INTO bookings (tour_id, ...) VALUES (999999, ...);
-- ERROR: foreign key violation
```

### Isolation (Изоляция)

```sql
-- Транзакция A не видит незафиксированные изменения от B
-- Connection A:
BEGIN;
UPDATE tours SET views = views + 1 WHERE id = 1;
-- SELECT вернёт новое значение в A
-- Но другие не видят до COMMIT

COMMIT;  -- Теперь видят все
```

### Durability (Долговечность)

```sql
-- После COMMIT данные в безопасности
BEGIN;
  UPDATE customers SET email = 'new@example.com' WHERE id = 1;
COMMIT;
-- Даже если серверная ошибка - данные сохранены на диск
```

---

## Базовые операции

### BEGIN и COMMIT

```sql
-- Начать транзакцию
BEGIN;

-- Операции
UPDATE tours SET name = 'New Name' WHERE id = 1;
INSERT INTO bookings (...) VALUES (...);

-- Применить всё
COMMIT;

-- Или отменить
ROLLBACK;
```

### SAVEPOINT - точки восстановления

```sql
BEGIN;
  UPDATE tours SET status = 'inactive' WHERE id = 1;

  SAVEPOINT sp1;

  UPDATE bookings SET status = 'cancelled' WHERE tour_id = 1;
  -- Ошибка! Откатываемся только к sp1

  ROLLBACK TO sp1;

  -- tours уже обновлён, bookings откачен
COMMIT;
```

---

## Уровни изоляции

### READ UNCOMMITTED

```sql
-- Самый слабый уровень (РЕДКО ИСПОЛЬЗУЕТСЯ)
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

-- Может прочитать незафиксированные изменения (Dirty Read)
```

### READ COMMITTED (по умолчанию)

```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Читает только зафиксированные данные
-- Может быть Phantom Read

BEGIN;
SELECT COUNT(*) FROM bookings WHERE status = 'pending';  -- 5
-- Connection B добавляет ещё одну
SELECT COUNT(*) FROM bookings WHERE status = 'pending';  -- 6!
COMMIT;
```

### REPEATABLE READ

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Снимок данных на начало транзакции
BEGIN;
SELECT COUNT(*) FROM bookings WHERE status = 'pending';  -- 5
-- Connection B добавляет ещё одну (видно в её транзакции)
SELECT COUNT(*) FROM bookings WHERE status = 'pending';  -- Всё ещё 5
COMMIT;
```

### SERIALIZABLE

```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Полная изоляция, как если бы транзакции выполнялись по очереди
-- САМЫЙ БЕЗОПАСНЫЙ но самый МЕДЛЕННЫЙ
```

**Практика:**
```sql
-- Туристический бизнес: READ COMMITTED достаточно
-- Используйте READ COMMITTED (по умолчанию)

-- Для финансовых операций: SERIALIZABLE
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
  -- Платёж
COMMIT;
```

---

## Блокировки

### Типы блокировок

```sql
-- Читать (может быть несколько)
SELECT ... FROM bookings WHERE id = 1;

-- Писать (исключительная, одна на таблицу)
UPDATE bookings SET status = 'confirmed' WHERE id = 1;
DELETE FROM bookings WHERE id = 1;
INSERT INTO bookings (...);

-- Явная блокировка (pessimistic locking)
BEGIN;
SELECT * FROM bookings WHERE id = 1 FOR UPDATE;
-- Никто больше не может обновить эту строку
UPDATE bookings SET total_price = 2000 WHERE id = 1;
COMMIT;
```

### FOR UPDATE vs FOR SHARE

```sql
-- Исключительная блокировка (для обновления)
BEGIN;
SELECT * FROM tours WHERE id = 1 FOR UPDATE;
UPDATE tours SET total_bookings = total_bookings + 1 WHERE id = 1;
COMMIT;

-- Совместная блокировка (для чтения с последующим обновлением)
BEGIN;
SELECT * FROM tours WHERE id = 1 FOR SHARE;
SELECT * FROM bookings WHERE tour_id = 1 FOR SHARE;
-- Другие тоже могут прочитать FOR SHARE
-- Но не могут UPDATE
COMMIT;
```

---

## Deadlocks

### Что такое deadlock

```
Transaction A:
  BEGIN;
  UPDATE tours SET views = views + 1 WHERE id = 1;
  UPDATE bookings SET status = 'confirmed' WHERE tour_id = 1;

Transaction B:
  BEGIN;
  UPDATE bookings SET status = 'cancelled' WHERE tour_id = 1;
  UPDATE tours SET views = views - 1 WHERE id = 1;

DEADLOCK! Ждут друг друга в цикле
```

### Решение: Сортируйте обновления

```sql
-- ПРАВИЛЬНО: всегда одинаковый порядок
BEGIN;
  UPDATE tours SET views = views + 1 WHERE id = 1;
  UPDATE bookings SET status = 'confirmed' WHERE tour_id = 1;
COMMIT;

BEGIN;
  UPDATE tours SET views = views - 1 WHERE id = 1;
  UPDATE bookings SET status = 'cancelled' WHERE tour_id = 1;
COMMIT;

-- Теперь deadlock невозможен
```

### Обработка deadlock в коде

```javascript
async function updateBookingWithRetry(id, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      await db.query('BEGIN');
      await db.query(
        'UPDATE bookings SET status = $1 WHERE id = $2',
        ['confirmed', id]
      );
      await db.query('COMMIT');
      return;
    } catch (error) {
      if (error.code === '40P01') {  // Deadlock detected
        await db.query('ROLLBACK');
        // Exponential backoff
        await new Promise(resolve =>
          setTimeout(resolve, Math.random() * Math.pow(2, attempt) * 100)
        );
        if (attempt === maxRetries - 1) throw error;
      } else {
        throw error;
      }
    }
  }
}
```

---

## Row-level locking

### Optimistic locking с версией

```sql
-- Добавить версию
CREATE TABLE bookings (
  id SERIAL PRIMARY KEY,
  tour_id INTEGER NOT NULL,
  customer_id INTEGER NOT NULL,
  status VARCHAR(20),
  version INTEGER DEFAULT 1,
  ...
);

-- Обновить, проверяя версию
UPDATE bookings
SET status = 'confirmed', version = version + 1
WHERE id = 123 AND version = 1;

-- Если вернул 0 rows - конфликт версий
```

### Optimistic locking в Prisma

```prisma
model Booking {
  id        Int     @id @default(autoincrement())
  status    String  @default("pending")
  version   Int     @default(1)
}
```

```javascript
// Обновить с проверкой версии
await prisma.booking.updateMany({
  where: {
    id: 123,
    version: 1  // Проверим версию
  },
  data: {
    status: 'confirmed',
    version: { increment: 1 }
  }
});
```

---

## Примеры для туризма

### Сценарий 1: Безопасное увеличение счётчика

```sql
-- НЕПРАВИЛЬНО: потеря данных при concurrent access
UPDATE tours SET total_views = total_views + 1 WHERE id = 1;

-- ПРАВИЛЬНО: с FOR UPDATE
BEGIN;
SELECT id, total_views FROM tours WHERE id = 1 FOR UPDATE;
UPDATE tours SET total_views = total_views + 1 WHERE id = 1;
COMMIT;
```

### Сценарий 2: Перевод денег между аккаунтами

```sql
-- ПРАВИЛЬНО: атомарная операция
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
  -- Списать со счёта A
  UPDATE customer_balance SET balance = balance - 100
  WHERE customer_id = 1;

  -- Начислить на счёт B
  UPDATE customer_balance SET balance = balance + 100
  WHERE customer_id = 2;

  -- Логировать операцию
  INSERT INTO transactions VALUES (...);

COMMIT;
-- Всё либо выполнится, либо откатится полностью
```

### Сценарий 3: Последовательность номеров

```sql
-- Таблица для счётчиков
CREATE TABLE sequences (
  name VARCHAR(50) PRIMARY KEY,
  current_value BIGINT,
  lock_key CHAR(1)
);

-- Получить следующий номер бронирования
BEGIN;
SELECT current_value FROM sequences
WHERE name = 'booking_number'
FOR UPDATE;  -- Блокируем строку

UPDATE sequences
SET current_value = current_value + 1
WHERE name = 'booking_number'
RETURNING current_value;

COMMIT;
```

---

## Best practices

1. **Минимизируйте размер транзакции** - меньше вероятность deadlock
2. **Фиксируйте порядок обновлений** - избегайте циклических зависимостей
3. **Используйте FOR UPDATE для критичных операций** - гарантирует безопасность
4. **Используйте REPEATABLE READ для аналитики** - стабильный снимок
5. **Обрабатывайте deadlock в коде** - retry с exponential backoff
6. **Логируйте большие транзакции** - ищите узкие места

---

**Последнее обновление:** 2026-02-04
