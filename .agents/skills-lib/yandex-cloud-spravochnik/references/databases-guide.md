# Managed Databases Guide

## Обзор сервисов

### PostgreSQL
- **Версии:** 12-16
- **Use case:** OLTP, booking системы, транзакции
- **HA:** Multi-master репликация
- **Цена:** от ~8,000₽/месяц (s2.micro)

### MySQL
- **Версии:** 5.7, 8.0
- **Use case:** Web приложения, legacy системы
- **HA:** Master-slave репликация

### MongoDB
- **Версии:** 4.4-7.0
- **Use case:** Document storage, flexible schema
- **Sharding:** Да

### ClickHouse
- **Use case:** OLAP, аналитика, big data
- **Performance:** Миллионы строк/секунду
- **Compression:** 10-20x сжатие

### YDB
- **Type:** Distributed SQL/NoSQL
- **Use case:** High-load OLTP, IoT
- **Serverless:** Да (pay-per-request)

---

## PostgreSQL: Подробное руководство

### Создание кластера

```bash
yc managed-postgresql cluster create \
  --name tourism-db \
  --environment production \
  --network-name default \
  --host zone-id=ru-central1-a,subnet-id=$SUBNET_ID \
  --postgresql-version 15 \
  --resource-preset s2.small \
  --disk-type network-ssd \
  --disk-size 100 \
  --user name=admin,password=SecurePass123 \
  --database name=tourism,owner=admin \
  --backup-window-start time=03:00,tz=UTC \
  --datalens-access \
  --websql-access
```

### Connection String

```bash
# Host
HOST=$(yc managed-postgresql hosts list --cluster-name tourism-db --format json | jq -r '.[0].name')

# Connection strings
echo "psql: postgresql://admin:SecurePass123@$HOST:6432/tourism?sslmode=require"
echo "JDBC: jdbc:postgresql://$HOST:6432/tourism?ssl=true&sslmode=require"
```

### Schema для туризма

```sql
-- tours table
CREATE TABLE tours (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price_aed DECIMAL(10,2) NOT NULL,
    price_usd DECIMAL(10,2),
    duration_hours INTEGER,
    max_capacity INTEGER,
    category VARCHAR(50),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tours_active ON tours(active);
CREATE INDEX idx_tours_category ON tours(category);

-- bookings table
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    tour_id INTEGER REFERENCES tours(id),
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(20),
    booking_date DATE NOT NULL,
    participants INTEGER DEFAULT 1,
    total_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'AED',
    status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bookings_tour_id ON bookings(tour_id);
CREATE INDEX idx_bookings_date ON bookings(booking_date);
CREATE INDEX idx_bookings_status ON bookings(status);

-- payments table
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER REFERENCES bookings(id),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    transaction_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- customers table (для CRM)
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    country VARCHAR(50),
    total_bookings INTEGER DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0,
    first_booking_date DATE,
    last_booking_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Backup и restore

```bash
# Manual backup
yc managed-postgresql cluster backup tourism-db

# List backups
yc managed-postgresql backup list --cluster-id <CLUSTER_ID>

# Restore from backup
yc managed-postgresql cluster restore \
  --backup-id <BACKUP_ID> \
  --name tourism-db-restored \
  --environment production \
  --network-name default
```

### Connection pooling (Odyssey)

```python
# Python с connection pool
import psycopg2
from psycopg2 import pool

# Создать connection pool
connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=20,
    host=HOST,
    port=6432,  # Odyssey pooler
    database='tourism',
    user='admin',
    password='SecurePass123',
    sslmode='require'
)

# Получить connection
conn = connection_pool.getconn()
cursor = conn.cursor()

# Query
cursor.execute("SELECT * FROM tours WHERE active = true")
tours = cursor.fetchall()

# Вернуть connection в pool
connection_pool.putconn(conn)
```

---

## ClickHouse: Аналитика

### Создание кластера

```bash
yc clickhouse cluster create \
  --name analytics-db \
  --environment production \
  --network-name default \
  --clickhouse-resource-preset s2.small \
  --clickhouse-disk-size 100 \
  --clickhouse-disk-type network-ssd \
  --user name=admin,password=SecurePass123 \
  --database name=analytics \
  --host type=clickhouse,zone-id=ru-central1-a,subnet-id=$SUBNET_ID
```

### Analytics schema

```sql
-- bookings_analytics (MergeTree для аналитики)
CREATE TABLE analytics.bookings_analytics (
    date Date,
    tour_id UInt32,
    tour_name String,
    participants UInt16,
    amount Decimal(10,2),
    currency String,
    payment_method String,
    customer_country String
) ENGINE = MergeTree()
ORDER BY (date, tour_id);

-- Агрегированные метрики
CREATE TABLE analytics.daily_metrics (
    date Date,
    total_bookings UInt32,
    total_revenue Decimal(12,2),
    avg_booking_value Decimal(10,2),
    unique_customers UInt32
) ENGINE = SummingMergeTree()
ORDER BY date;
```

### Analytics queries

```sql
-- Топ туров по выручке за месяц
SELECT
    tour_name,
    COUNT(*) as bookings_count,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_price
FROM bookings_analytics
WHERE date >= today() - INTERVAL 30 DAY
GROUP BY tour_name
ORDER BY total_revenue DESC
LIMIT 10;

-- Динамика бронирований по дням
SELECT
    date,
    COUNT(*) as bookings,
    SUM(amount) as revenue
FROM bookings_analytics
WHERE date >= today() - INTERVAL 90 DAY
GROUP BY date
ORDER BY date;

-- Конверсия по странам
SELECT
    customer_country,
    COUNT(*) as bookings,
    SUM(amount) as revenue,
    AVG(participants) as avg_group_size
FROM bookings_analytics
WHERE date >= today() - INTERVAL 30 DAY
GROUP BY customer_country
ORDER BY revenue DESC;
```

---

## YDB: Serverless база

### Создание database

```bash
yc ydb database create \
  --name tourism-serverless \
  --serverless
```

### Table schema (Document API)

```python
import ydb

# Инициализация
driver = ydb.Driver(
    endpoint='grpcs://ydb.serverless.yandexcloud.net:2135',
    database='/ru-central1/.../tourism-serverless'
)

# Создать таблицу
session = driver.table_client.session().create()

session.create_table(
    '/ru-central1/.../tourism-serverless/tours',
    ydb.TableDescription()
        .with_column(ydb.Column('tour_id', ydb.OptionalType(ydb.PrimitiveType.Uint64)))
        .with_column(ydb.Column('name', ydb.OptionalType(ydb.PrimitiveType.Utf8)))
        .with_column(ydb.Column('price', ydb.OptionalType(ydb.PrimitiveType.Double)))
        .with_primary_key('tour_id')
)
```

**Use case:** High-load системы (>10k RPS), IoT данные, real-time аналитика

---

## Сравнение БД для туризма

| Задача | Рекомендация | Почему |
|--------|--------------|--------|
| Booking система | PostgreSQL | ACID, transactions, relations |
| Аналитика | ClickHouse | Fast aggregations, compression |
| Session storage | YDB | Low latency, serverless |
| User profiles | MongoDB | Flexible schema |
| Кеш | Redis | In-memory, fast |

---

## Pricing (2026)

### PostgreSQL (s2.small: 4 vCPU, 16GB RAM)

- Compute: ~16,000₽/месяц
- Storage (SSD): 100GB × 8₽ = 800₽
- Backup: 100GB × 2₽ = 200₽
- **Итого:** ~17,000₽/месяц

### ClickHouse (s2.small)

- Compute: ~16,000₽/месяц
- Storage: 100GB × 8₽ = 800₽
- **Итого:** ~16,800₽/месяц

### YDB Serverless

- Storage: 1₽/GB/месяц
- Operations: 2₽/1M read units, 8₽/1M write units
- **Пример:** 10GB + 10M reads + 1M writes = 10 + 20 + 8 = ~38₽/месяц

---

**См. также:**
- `assets/templates/booking-system-schema.sql` - полная схема
- `assets/examples/booking-api-nodejs/` - REST API
- `tourism-business-cases.md` - кейс #1 (booking система)
