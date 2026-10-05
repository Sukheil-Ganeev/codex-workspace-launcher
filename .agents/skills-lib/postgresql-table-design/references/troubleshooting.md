# Troubleshooting — postgresql-table-design

## Проблема 1: Медленные запросы по FK без индекса
**Симптом:** JOIN между таблицами занимает секунды, DELETE из родительской таблицы блокирует надолго, EXPLAIN показывает Seq Scan на дочерней таблице.
**Решение:**
```sql
-- Найти FK без индексов
SELECT c.conrelid::regclass AS table_name,
       c.conname AS fk_name,
       a.attname AS column_name
FROM pg_constraint c
JOIN pg_attribute a ON a.attnum = ANY(c.conkey) AND a.attrelid = c.conrelid
WHERE c.contype = 'f'
  AND NOT EXISTS (
    SELECT 1 FROM pg_index i
    WHERE i.indrelid = c.conrelid
      AND a.attnum = ANY(i.indkey)
  );

-- Создать недостающие индексы
CREATE INDEX CONCURRENTLY idx_orders_user_id ON orders(user_id);
```

## Проблема 2: Bloat таблицы — размер растёт, данных не прибавилось
**Симптом:** `pg_total_relation_size()` растёт, хотя количество строк стабильно. Запросы замедляются.
**Решение:** Проверить работу autovacuum:
```sql
SELECT relname, n_dead_tup, last_autovacuum, last_autoanalyze
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```
Если autovacuum отстаёт — настроить агрессивнее для hot-таблиц:
```sql
ALTER TABLE orders SET (
  autovacuum_vacuum_scale_factor = 0.05,  -- вместо 0.2
  autovacuum_analyze_scale_factor = 0.02
);
```
Для экстренных случаев: `VACUUM FULL` (блокирует таблицу!) или `pg_repack` (без блокировки).

## Проблема 3: Вставка VARCHAR больше лимита — ошибка вместо обрезки
**Симптом:** `ERROR: value too long for type character varying(100)` — PostgreSQL не обрезает молча.
**Решение:** Это by design — PostgreSQL строгий. Варианты:
1. Увеличить лимит или перейти на TEXT + CHECK
2. Обрезать на уровне приложения перед вставкой
3. Использовать триггер (не рекомендуется — скрывает проблему)
```sql
-- Миграция на TEXT + CHECK
ALTER TABLE users ALTER COLUMN name TYPE TEXT;
ALTER TABLE users ADD CONSTRAINT users_name_length CHECK (LENGTH(name) <= 255);
```

## Проблема 4: Дыры в sequence (1, 2, 5, 6...)
**Симптом:** Identity/serial колонка имеет пропуски в нумерации. Бизнес-пользователи паникуют.
**Решение:** Это нормальное поведение! Gaps появляются при: rollback транзакций, crash recovery, конкурентных вставках. **НЕ пытайтесь** делать ID последовательными — это разрушит конкурентность. Если нужна последовательная нумерация (номера счетов), используйте отдельную логику:
```sql
-- Отдельная таблица-счётчик с FOR UPDATE
SELECT nextval FROM invoice_counter WHERE type = 'invoice' FOR UPDATE;
```

## Проблема 5: Запрос с LIKE '%text%' игнорирует индекс
**Симптом:** EXPLAIN показывает Seq Scan даже при наличии B-tree индекса на колонке. Поиск по подстроке медленный.
**Решение:** B-tree не поддерживает leading wildcard (`%text%`). Варианты:
```sql
-- 1. Trigram индекс (pg_trgm)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_products_name_trgm ON products USING GIN (name gin_trgm_ops);
-- Теперь LIKE '%text%' и ILIKE работают с индексом

-- 2. Full-text search (для естественного языка)
ALTER TABLE products ADD COLUMN search_vector TSVECTOR
  GENERATED ALWAYS AS (to_tsvector('russian', name || ' ' || description)) STORED;
CREATE INDEX idx_products_fts ON products USING GIN (search_vector);
```

## Проблема 6: Deadlock при конкурентных UPDATE
**Симптом:** `ERROR: deadlock detected` — два процесса обновляют одни и те же строки в разном порядке.
**Решение:** Всегда обновлять строки в одинаковом порядке (например, по ID). Использовать `SELECT ... FOR UPDATE` с явным ORDER BY. Уменьшить длительность транзакций. Для массовых обновлений — batching:
```sql
-- Вместо одного большого UPDATE
UPDATE accounts SET balance = balance - 100 WHERE id IN (SELECT id FROM ... ORDER BY id FOR UPDATE);
```
