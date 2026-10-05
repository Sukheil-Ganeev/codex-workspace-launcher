# Cheatsheet — postgresql-table-design

## Типы данных (быстрый выбор)
| Для чего | Тип | НЕ использовать |
|----------|-----|-----------------|
| ID (по умолчанию) | `BIGINT GENERATED ALWAYS AS IDENTITY` | `SERIAL` (устаревший) |
| ID (распределённый) | `UUID` (uuidv7 на PG18+) | `VARCHAR` для ID |
| Целые числа | `BIGINT` / `INTEGER` | `SMALLINT` (без причины) |
| Дробные (точные) | `NUMERIC(p,s)` | `FLOAT` / `REAL` |
| Дробные (приблизит.) | `DOUBLE PRECISION` | `REAL` (без причины) |
| Деньги | `NUMERIC(12,2)` | `MONEY`, `FLOAT` |
| Строки | `TEXT` | `VARCHAR(n)`, `CHAR(n)` |
| Бинарные данные | `BYTEA` | `TEXT` + base64 |
| Дата и время | `TIMESTAMPTZ` | `TIMESTAMP` (без tz) |
| Только дата | `DATE` | `TEXT` для дат |
| Длительность | `INTERVAL` | `INTEGER` (секунды) |
| Булево | `BOOLEAN NOT NULL` | `INTEGER` (0/1) |
| Перечисления (фикс.) | `CREATE TYPE ... AS ENUM` | `VARCHAR` без CHECK |
| Перечисления (динам.) | `TEXT + CHECK` или lookup table | `ENUM` (сложно менять) |
| JSON-данные | `JSONB` | `JSON` (без причины) |
| IP-адреса | `INET` | `TEXT` |
| Массивы/теги | `TEXT[]` + GIN индекс | Junction table для тегов |
| Диапазоны | `daterange`, `numrange` | Два поля start/end |

## Шаблон таблицы
```sql
CREATE TABLE orders (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users(id),
    status      TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','confirmed','cancelled','completed')),
    total       NUMERIC(12,2) NOT NULL CHECK (total >= 0),
    currency    TEXT NOT NULL DEFAULT 'AED' CHECK (currency ~ '^[A-Z]{3}$'),
    notes       TEXT,
    metadata    JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- FK индекс (PostgreSQL НЕ создаёт автоматически!)
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Частые фильтры
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- JSONB (если нужен поиск по ключам)
CREATE INDEX idx_orders_metadata ON orders USING GIN(metadata);
```

## Типы индексов
| Тип | Когда использовать | Операторы |
|-----|-------------------|-----------|
| B-tree (default) | =, <, >, BETWEEN, ORDER BY | Сравнения |
| GIN | JSONB, массивы, полнотекст, триграммы | @>, <@, &&, @@ |
| GiST | Геометрия, range-типы, nearest-neighbor | &&, @>, <<, >> |
| BRIN | Очень большие таблицы с natural ordering | =, <, > (блочные) |
| Hash | Только equality (редко нужен) | = |

## Constraints
```sql
-- Primary Key
id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY

-- Foreign Key
user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE

-- Unique
UNIQUE(email)
UNIQUE(user_id, slug)  -- составной

-- Unique с NULLs (PG15+)
UNIQUE NULLS NOT DISTINCT (email)

-- Check
CHECK (price >= 0)
CHECK (status IN ('active','inactive'))
CHECK (end_date > start_date)
CHECK (LENGTH(name) <= 255)

-- Exclusion (для диапазонов)
EXCLUDE USING GIST (room WITH =, during WITH &&)
```

## Полезные паттерны
```sql
-- Soft delete
deleted_at TIMESTAMPTZ DEFAULT NULL
-- + partial index
CREATE INDEX idx_active_users ON users(email) WHERE deleted_at IS NULL;

-- Автообновление updated_at (триггер)
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Partial index (только активные)
CREATE INDEX idx_active_orders ON orders(created_at) WHERE status = 'pending';

-- Covering index (index-only scan)
CREATE INDEX idx_users_email_name ON users(email) INCLUDE (name);
```

## Диагностика
```sql
-- Размер таблиц
SELECT relname, pg_size_pretty(pg_total_relation_size(oid))
FROM pg_class WHERE relkind = 'r' ORDER BY pg_total_relation_size(oid) DESC LIMIT 10;

-- Неиспользуемые индексы
SELECT indexrelname, idx_scan FROM pg_stat_user_indexes WHERE idx_scan = 0;

-- Dead tuples (нужен vacuum?)
SELECT relname, n_dead_tup, last_autovacuum FROM pg_stat_user_tables ORDER BY n_dead_tup DESC;

-- Медленные запросы
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;

-- FK без индексов
SELECT c.conrelid::regclass, a.attname
FROM pg_constraint c
JOIN pg_attribute a ON a.attnum = ANY(c.conkey) AND a.attrelid = c.conrelid
WHERE c.contype = 'f'
AND NOT EXISTS (SELECT 1 FROM pg_index i WHERE i.indrelid = c.conrelid AND a.attnum = ANY(i.indkey));
```
