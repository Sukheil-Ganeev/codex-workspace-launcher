# Database Scripts Reference - Полная Справка

## Справочная таблица всех 12 скриптов

| Скрипт | Назначение | Основная команда |
|--------|-----------|------------------|
| migrate.js | Управление миграциями | `node migrate.js up` |
| seed.js | Генерация тестовых данных | `node seed.js --count 100` |
| backup.js | Резервное копирование | `node backup.js create` |
| restore.js | Восстановление из backup | `node restore.js restore --file backup.dump --force` |
| schema-validator.js | Валидация схемы БД | `node schema-validator.js` |
| performance-analyzer.js | Анализ производительности | `node performance-analyzer.js` |
| connection-monitor.js | Мониторинг соединений | `node connection-monitor.js --watch` |
| health-checker.js | Проверка здоровья БД | `node health-checker.js` |
| schema-diff.js | Сравнение схем БД | `node schema-diff.js --source db1 --target db2` |
| test-factory.js | Фабрика тестовых данных | `node test-factory.js create --table users --count 100` |
| replication-setup.js | Настройка репликации | `node replication-setup.js setup --role primary` |
| query-builder.js | Интерактивный конструктор запросов | `node query-builder.js` |

---

## migrate.js - Управление Миграциями

### Описание
Выполняет SQL миграции из директории `migrations/` с отслеживанием в таблице `schema_migrations`.

### Основные команды

```bash
# Показать статус миграций
node migrate.js status

# Запустить все оставшиеся миграции
node migrate.js up

# Откатить последнюю миграцию
node migrate.js down

# Откатить несколько миграций
node migrate.js down 3

# Создать новую миграцию
node migrate.js create create_users_table
node migrate.js create add_email_index
```

### Структура миграции

Миграции должны находиться в папке `migrations/` с именем: `TIMESTAMP_description.sql`

```sql
-- migrations/1704067200000_create_users.sql

BEGIN;

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

COMMIT;
```

### Параметры

- `--dir` - Путь к директории миграций (по умолчанию: ./migrations)

### Вывод

```
→ 1704067200000_create_users_table.sql (245ms)
→ 1704067300000_add_email_index.sql (120ms)
Total: 5 | Executed: 5 | Pending: 0
```

---

## seed.js - Генерация Тестовых Данных

### Описание
Генерирует реалистичные тестовые данные для разработки и тестирования.

### Основные команды

```bash
# Заполнить 100 записей (по умолчанию)
node seed.js

# Заполнить 500 записей
node seed.js --count 500

# Очистить и заново заполнить
node seed.js --count 1000 --clear

# Использовать кастомный файл seed
node seed.js --seed-file custom-seeds.js
```

### Параметры

- `--count` - Количество записей (по умолчанию: 100)
- `--clear` - Очистить таблицы перед заполнением
- `--seed-file` - Кастомный файл с генератором

### Особенности

- Автоматическое определение таблиц
- Умная генерация значений (email, phone, uuid)
- Батч-вставка (по 100 записей)
- Прогресс-индикатор
- Обработка constraints

### Генерируемые типы данных

```
- UUID / UUID v4
- Email: user.lastname.1@test.com
- Phone: +1XXXXXXXXXX
- Names: John, Jane (случайные)
- Dates: Past/Future dates
- Boolean: random true/false
- Numbers: 0-1000
- Text: sample sentences
- JSON: objects
```

---

## backup.js - Резервное Копирование

### Описание
Создает резервные копии БД с помощью `pg_dump` с поддержкой различных форматов.

### Основные команды

```bash
# Создать резервную копию
node backup.js create

# Создать с кастомными параметрами
node backup.js create --format plain --compression 9 --output custom_backup.sql

# Показать список всех резервных копий
node backup.js list

# Удалить старые резервные копии (оставить 5 последних)
node backup.js cleanup 5

# Очистить все резервные копии
node backup.js cleanup 0
```

### Параметры

- `--format` - Формат: `custom` (default), `tar`, `plain`
- `--compression` - Уровень сжатия: 0-9 (default: 6)
- `--output` - Путь для сохранения
- Действия: `create`, `list`, `cleanup`

### Форматы

| Формат | Размер | Скорость | Использование |
|--------|--------|----------|---------------|
| custom | Маленький | Быстро | Восстановление парт |
| tar | Средний | Нормально | Переносимость |
| plain | Большой | Медленно | Редактирование |

### Вывод

```
Starting backup of myapp...
Format: custom | Compression: 6
✓ Backup completed in 12.34s
File: ./backups/backup_2024-01-15_1704067200000.dump
Size: 45.67 MB
```

---

## restore.js - Восстановление БД

### Описание
Восстанавливает БД из резервной копии, созданной `pg_dump`.

### Основные команды

```bash
# Восстановить базу данных
node restore.js restore --file backups/backup_2024-01-15.dump --force

# Очистить перед восстановлением
node restore.js restore --file backup.dump --clean --force

# Показать содержимое резервной копии
node restore.js list --file backup.dump

# Тестировать восстановление (создать тестовую БД)
node restore.js test --file backup.dump
```

### Параметры

- `--file` - Путь к резервной копии (обязательный)
- `--format` - Формат (auto-detect по умолчанию)
- `--clean` - Удалить существующие объекты
- `--drop-schema` - Удалить все схемы перед восстановлением
- `--force` - Пропустить подтверждение
- `--verbose` - Подробный вывод

### Действия

```bash
node restore.js restore ...  # Восстановить
node restore.js list ...     # Показать содержимое
node restore.js test ...     # Протестировать
```

### Предупреждения

```
⚠ WARNING: This will restore the database from backup
⚠ Database: myapp
⚠ Backup: backups/backup_2024-01-15.dump
✗ Add --force flag to proceed with restore
```

---

## schema-validator.js - Валидация Схемы

### Описание
Проверяет целостность и корректность схемы БД.

### Основные команды

```bash
# Полная проверка схемы
node schema-validator.js

# Строгий режим (выход с кодом ошибки)
node schema-validator.js --strict

# С кастомным файлом схемы
node schema-validator.js --schema-file expected-schema.json
```

### Параметры

- `--schema-file` - Файл с ожидаемой схемой
- `--strict` - Выход с кодом 1 при обнаружении ошибок

### Проверяемые элементы

1. **Таблицы** - Наличие, имена, типы колонок
2. **Constraints** - PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK
3. **Индексы** - Наличие, определение
4. **Типы данных** - Корректность, nullable флаги
5. **Связи** - Foreign key relationships

### Вывод

```
Validating tables...
✓ Found 8 table(s)
  - users
  - profiles
  - posts
  ...

Validating constraints...
✓ Found constraints:
  - PRIMARY KEY: 8
  - FOREIGN KEY: 3
  - UNIQUE: 2

Total issues: 0
```

---

## performance-analyzer.js - Анализ Производительности

### Описание
Анализирует медленные запросы и метрики производительности БД.

### Основные команды

```bash
# Полный анализ производительности
node performance-analyzer.js

# Показать топ 20 медленных запросов
node performance-analyzer.js --limit 20

# Показать только запросы медленнее 500ms
node performance-analyzer.js --min-time 500

# Сбросить статистику
node performance-analyzer.js reset
```

### Параметры

- `--limit` - Максимум запросов в отчете (default: 10)
- `--min-time` - Минимальное время в ms (default: 100)
- Действия: `analyze`, `reset`

### Требования

Требуется расширение PostgreSQL (один раз):

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

### Анализируемые метрики

1. **Медленные запросы** - топ запросов по времени
2. **Паттерны** - статистика по типам запросов
3. **Использование индексов** - неиспользуемые индексы
4. **Статистика таблиц** - размер, количество операций

### Вывод

```
Top 10 Slow Queries (min 100ms):
1. SELECT * FROM orders WHERE status = 'pending'
   Calls: 1523
   Total: 45234.50ms | Mean: 29.72ms | Max: 120ms
   Std Dev: 15.34ms
```

---

## connection-monitor.js - Мониторинг Соединений

### Описание
Отслеживает состояние пула соединений БД в реальном времени.

### Основные команды

```bash
# Показать текущее состояние пула
node connection-monitor.js

# Мониторить в реальном времени (обновление каждые 5 сек)
node connection-monitor.js --watch --interval 5000

# Завершить запросы, выполняющиеся дольше 300 секунд
node connection-monitor.js kill-long 300
```

### Параметры

- `--watch` - Режим реального времени
- `--interval` - Интервал обновления в ms (default: 5000)
- Действия: `monitor`, `kill-long`

### Отображаемая информация

```
Total Connections:  15/20
Idle Connections:   8
Active Connections: 7
Waiting Requests:   2

Utilization:        75.0%

Active Connections (5):
  PID 12345: psql [active] (45s)
  PID 12346: node-app [active] (2s)
  ...
```

### График тренда

```
Connection Trend (last 60 samples):
▄▆█████▅▃▄███████▄▅▂▃▅
Legend: _ = idle, █ = full utilization
```

---

## health-checker.js - Проверка Здоровья БД

### Описание
Проводит комплексную диагностику здоровья БД.

### Основные команды

```bash
# Полная проверка здоровья
node health-checker.js

# Проверить конкретные компоненты
node health-checker.js --checks connection,tables,indexes

# Выход с кодом ошибки при проблемах (для CI/CD)
node health-checker.js --exit-code
```

### Параметры

- `--checks` - Список проверок (разделённые запятой)
- `--exit-code` - Выход с кодом 1 при ошибках

### Проводимые проверки

1. **Connection** - Соединение с БД
2. **Database** - Целостность БД, размер, соединения
3. **Tables** - Наличие таблиц, фрагментация
4. **Indexes** - Наличие и валидность индексов
5. **Constraints** - PRIMARY KEY, FOREIGN KEY, UNIQUE
6. **Locks** - Активные блокировки
7. **Bloat** - Фрагментация (bloat)
8. **Replication** - Статус репликации

### Вывод

```
Health Check Summary
✓ All 8 check(s) passed!

Status: HEALTHY
```

---

## schema-diff.js - Сравнение Схем

### Описание
Сравнивает схему между двумя БД и генерирует миграции.

### Основные команды

```bash
# Сравнить две БД
node schema-diff.js --source production --target development

# Генерировать SQL миграции
node schema-diff.js --source prod_db --target dev_db --output migration.sql

# Вывести различия в JSON
node schema-diff.js --source db1 --target db2 --output-format json
```

### Параметры

- `--source` - Исходная БД (обязательный)
- `--target` - Целевая БД (обязательный)
- `--output` - Файл для сохранения миграции
- `--output-format` - Формат: `text`, `sql`, `json`

### Выявляемые различия

1. **Таблицы** - Отсутствующие, лишние
2. **Колонки** - Добавленные, удалённые, изменённые
3. **Типы данных** - Несовпадения типов
4. **Индексы** - Отсутствующие или лишние
5. **Constraints** - Различия в ограничениях

### Вывод

```
Schema Differences Found:

Table Differences:
  Only in source: old_table
  Only in target: new_table

Columns Added (in target):
  users.phone [character varying]
  users.verified [boolean]

Columns Changed:
  users.email
    From: character varying(100)
    To:   character varying(255)
```

---

## test-factory.js - Фабрика Тестовых Данных

### Описание
Производство тестовых данных с корректными типами и связями.

### Основные команды

```bash
# Создать данные для всех таблиц
node test-factory.js create

# Создать для конкретной таблицы (1000 записей)
node test-factory.js create --table users --count 1000

# Показать доступные таблицы
node test-factory.js list

# Очистить таблицу
node test-factory.js truncate --table users
```

### Параметры

- `--count` - Количество записей (default: 10)
- `--table` - Конкретная таблица
- `--relate` - Создать связанные данные
- Действия: `create`, `list`, `truncate`

### Генерация значений по типам

```
UUID           → xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
Email          → firstname.lastname.N@test.com
Phone          → +1XXXXXXXXXX
Username       → testusername_N
Boolean        → true/false (случайно)
Integer        → 0-10000
Decimal        → 0.00-999.99
Timestamp      → случайная дата за последний год
Date           → YYYY-MM-DD
Text/Varchar   → Умные значения по названию столбца
JSON/JSONB     → Валидные JSON объекты
```

### Интеллектуальная генерация

```javascript
// По названию столбца определяется тип значения:
- email      → test.user.1@test.com
- name       → Test User 1
- phone      → +15551234567
- address    → 1 Test Street
- created_at → timestamp за последний год
- user_id    → UUID (если есть FK)
```

---

## replication-setup.js - Настройка Репликации

### Описание
Помощник для настройки и управления PostgreSQL репликацией.

### Основные команды

```bash
# Настроить PRIMARY сервер
node replication-setup.js setup --role primary

# Настроить REPLICA сервер
node replication-setup.js setup --role replica --replica-host prod.example.com

# Создать слот репликации
node replication-setup.js setup --role primary --slot-name my_repl_slot

# Показать статус репликации
node replication-setup.js status

# Тестировать соединение с replica
node replication-setup.js test --replica-host prod.example.com

# Удалить слот репликации
node replication-setup.js drop-slot --slot-name my_repl_slot
```

### Параметры

- `--role` - `primary` или `replica` (обязательный)
- `--slot-name` - Имя слота репликации (default: replication_slot)
- `--replica-host` - Хост replica сервера
- `--wal-level` - Уровень WAL (default: replica)

### Действия

```bash
setup                 # Настроить сервер
drop-slot             # Удалить слот
test                  # Тестировать соединение
```

### Информация для Primary

```
Setting up PRIMARY server...

Current WAL level: replica
Creating replication slot: replication_slot...
✓ Slot created

Base Backup Command (run on replica):
pg_basebackup -h primary.com -p 5432 -U postgres -D /var/lib/postgresql/14/main -Fp -Xs -Pv
```

---

## query-builder.js - Интерактивный Конструктор Запросов

### Описание
REPL интерфейс для построения и выполнения SQL запросов.

### Основные команды

```bash
# Запустить интерактивный режим
node query-builder.js

# С предвыбранной таблицей
node query-builder.js --table users

# С шаблоном SELECT
node query-builder.js --template select
```

### Команды в REPL

```
sql> help                    # Справка
sql> list                    # Показать таблицы
sql> describe                # Описание текущей таблицы
sql> template                # Шаблоны запросов
sql> show                    # Показать текущий запрос
sql> run                     # Выполнить запрос
sql> execute                 # Выполнить запрос
sql> clear                   # Очистить запрос
sql> exit                    # Выход
```

### Примеры использования

```sql
sql> SELECT * FROM users LIMIT 5;
✓ Query executed in 45ms

  id                   | email           | username   | created_at
  --------------------|-----------------|------------|---------------------
  123e4567-e89b-12d3- | john@example.com| johndoe    | 2024-01-15 10:30:45
  ...

Rows affected: 5

sql> INSERT INTO users (email, username) VALUES ('jane@example.com', 'jane');
✓ Query executed in 12ms
Rows affected: 1

sql> UPDATE users SET email = 'newemail@test.com' WHERE id = 1;
✓ Query executed in 8ms
Rows affected: 1
```

### Встроенные шаблоны

```
select   → SELECT column FROM table WHERE condition
insert   → INSERT INTO table (col1, col2) VALUES (val1, val2)
update   → UPDATE table SET column = value WHERE condition
delete   → DELETE FROM table WHERE condition
join     → SELECT * FROM table1 JOIN table2 ON condition
aggregate→ SELECT COUNT(*) FROM table GROUP BY column
```

---

## Утилиты и Модули

### config.js
Централизованная конфигурация всех скриптов.

```javascript
// Используется автоматически
require('./config');
// config.dbConfig - конфиг БД
// config.logLevel - уровень логирования
// config.backupDir - директория резервных копий
```

### logger.js
Логирование с цветным выводом.

```javascript
logger.success('Operation completed');  // Зелёный
logger.error('Error occurred', err);    // Красный
logger.warn('Warning message');         // Жёлтый
logger.info('Information');             // Голубой
logger.progress(50, 100, 'label');      // Прогресс-бар
```

### db.js
Менеджер соединений с пулингом.

```javascript
await db.connect();                    // Подключиться
const result = await db.query(sql);    // Выполнить запрос
await db.transaction(callback);        // Транзакция
await db.disconnect();                 // Отключиться
```

---

## Интеграция с CI/CD

### GitHub Actions

```yaml
- name: Health Check
  run: |
    cd scripts
    npm install
    node health-checker.js --exit-code

- name: Run Migrations
  run: node scripts/migrate.js up

- name: Backup Database
  run: node scripts/backup.js create
```

### GitLab CI

```yaml
db-health:
  script:
    - cd scripts
    - npm install
    - node health-checker.js --exit-code
```

### Jenkins

```groovy
stage('Database') {
  steps {
    sh 'cd scripts && npm install && node health-checker.js --exit-code'
    sh 'cd scripts && node migrate.js up'
  }
}
```

---

## Оптимизация и Best Practices

### Миграции

```bash
# Всегда проверяйте статус перед запуском
node migrate.js status

# Тестируйте миграции на staging
node migrate.js up  # на staging

# Создавайте откаты (down миграции)
# Используйте транзакции (BEGIN; ... COMMIT;)
```

### Резервные копии

```bash
# Частые резервные копии для production
0 * * * * node backup.js create  # Каждый час

# Очищайте старые копии
0 2 * * * node backup.js cleanup 30  # Оставить 30

# Тестируйте восстановление регулярно
node restore.js test --file backup.dump
```

### Мониторинг

```bash
# Постоянный мониторинг в production
node connection-monitor.js --watch &

# Еженедельная проверка здоровья
0 3 * * 0 node health-checker.js --exit-code

# Анализ производительности
0 * * * * node performance-analyzer.js > perf_report.txt
```

### Тестирование

```bash
# Перед каждым тестовым прогоном
node test-factory.js truncate --table users
node test-factory.js create --table users --count 100

# Проверьте целостность схемы
node schema-validator.js --strict
```

---

## Примеры реальных сценариев

### Сценарий 1: Развертывание на production

```bash
#!/bin/bash
set -e

cd scripts

# 1. Проверить здоровье
echo "Checking database health..."
node health-checker.js --exit-code

# 2. Создать резервную копию
echo "Creating backup..."
node backup.js create

# 3. Запустить миграции
echo "Running migrations..."
node migrate.js up

# 4. Валидировать схему
echo "Validating schema..."
node schema-validator.js --strict

# 5. Проверить снова
echo "Final health check..."
node health-checker.js --exit-code

echo "✓ Deployment successful!"
```

### Сценарий 2: Диагностика проблем производительности

```bash
#!/bin/bash

cd scripts

echo "=== Performance Diagnosis ==="

# 1. Анализировать медленные запросы
echo "1. Analyzing slow queries..."
node performance-analyzer.js --limit 20

# 2. Мониторить соединения
echo "2. Connection status..."
node connection-monitor.js

# 3. Проверить индексы
echo "3. Checking indexes..."
node health-checker.js --checks indexes

echo "=== End of report ==="
```

### Сценарий 3: Синхронизация между средами

```bash
#!/bin/bash

# На production
echo "Creating production backup..."
cd /prod/scripts && node backup.js create

# На development
echo "Downloading backup and restoring..."
scp user@prod:/prod/scripts/backups/latest.dump ./

cd /dev/scripts
node restore.js restore --file latest.dump --force

# Проверить
node schema-validator.js
node health-checker.js
```

---

## Troubleshooting

### Проблема: "Database connection failed"

**Решение:**
```bash
# 1. Проверить конфиг
cat .env

# 2. Проверить доступность
pg_isready -h localhost -p 5432

# 3. Проверить учётные данные
psql -h localhost -U postgres -d postgres
```

### Проблема: "Extension pg_stat_statements not found"

**Решение:**
```sql
-- На целевой БД (один раз)
CREATE EXTENSION pg_stat_statements;

-- Убедиться
SELECT * FROM pg_extension WHERE extname = 'pg_stat_statements';
```

### Проблема: "Restore failed"

**Решение:**
```bash
# Использовать флаги очистки
node restore.js restore --file backup.dump --clean --force

# Или с более агрессивным подходом
node restore.js restore --file backup.dump --drop-schema --force
```

### Проблема: "Миграция не запускается"

**Решение:**
```bash
# 1. Проверить статус
node migrate.js status

# 2. Проверить формат файла (должен быть в папке migrations/)
ls -la migrations/

# 3. Проверить права доступа
chmod +x migrations/*.sql
```

---

## Лицензия и Поддержка

Все скрипты предоставляются as-is. Для поддержки смотрите документацию PostgreSQL и ng-postgres.

**Рекомендуемые ресурсы:**
- PostgreSQL Docs: https://www.postgresql.org/docs/
- pg Node.js: https://node-postgres.com/
- Best Practices: https://wiki.postgresql.org/
