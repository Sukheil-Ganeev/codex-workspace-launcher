# Database Utility Scripts

Полный набор из 12 production-ready скриптов для управления PostgreSQL базами данных.

## Требования

- Node.js 14+
- PostgreSQL 12+
- Пакеты: `pg`

## Установка

```bash
npm install pg
```

## Конфигурация

Создайте `.env` файл в корне проекта:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myDatabase
DB_USER=postgres
DB_PASSWORD=password
DB_SSL=false
DB_TIMEOUT=30000
BACKUP_DIR=./backups
LOG_LEVEL=info
```

Или используйте переменные окружения.

## 12 Основных Скриптов

### 1. migrate.js - Migration Runner

Запускает SQL миграции из директории `migrations/`.

```bash
# Показать статус миграций
node scripts/migrate.js status

# Запустить все миграции
node scripts/migrate.js up

# Откатить последнюю миграцию
node scripts/migrate.js down

# Создать новую миграцию
node scripts/migrate.js create create_users_table
```

**Возможности:**
- Отслеживание выполненных миграций в таблице `schema_migrations`
- Транзакционное выполнение
- Откаты

---

### 2. seed.js - Test Data Generator

Генерирует реалистичные тестовые данные.

```bash
# Заполнить 100 записей
node scripts/seed.js --count 100

# Очистить и заново заполнить
node scripts/seed.js --count 50 --clear

# Сгенерировать пользователей и товары
node scripts/seed.js --count 1000
```

**Возможности:**
- Поддержка встроенного генератора данных
- Батч-вставка для производительности
- Прогресс-индикатор
- Указание количества записей

---

### 3. backup.js - Automated Backup

Создание резервных копий базы данных с pg_dump.

```bash
# Создать резервную копию
node scripts/backup.js create

# Создать с пользовательским форматом
node scripts/backup.js create --format plain --compression 9

# Показать список всех резервных копий
node scripts/backup.js list

# Удалить старые резервные копии (оставить последние 5)
node scripts/backup.js cleanup 5
```

**Форматы:**
- `custom` - Кастомный формат PostgreSQL (по умолчанию)
- `tar` - TAR архив
- `plain` - SQL текст

**Возможности:**
- Сжатие (0-9)
- Верификация резервной копии
- Автоудаление старых копий
- Размер в MB

---

### 4. restore.js - Database Restore

Восстановление базы данных из резервной копии.

```bash
# Восстановить базу данных
node scripts/restore.js restore --file backups/backup_2024-01-15.dump --force

# Очистить перед восстановлением
node scripts/restore.js restore --file backup.dump --clean --force

# Показать содержимое резервной копии
node scripts/restore.js list --file backup.dump

# Протестировать восстановление
node scripts/restore.js test --file backup.dump
```

**Опции:**
- `--clean` - Удалить существующие объекты
- `--drop-schema` - Удалить все схемы
- `--force` - Пропустить подтверждение
- `--verbose` - Подробный вывод

---

### 5. schema-validator.js - Schema Validation

Валидация структуры базы данных.

```bash
# Проверить схему
node scripts/schema-validator.js

# Строгий режим (выход с кодом ошибки)
node scripts/schema-validator.js --strict

# Список всех таблиц
node scripts/schema-validator.js | grep TABLE
```

**Проверяет:**
- Таблицы и их колонки
- Ограничения (constraints)
- Индексы
- Типы данных
- Связи (foreign keys)

---

### 6. performance-analyzer.js - Slow Query Analyzer

Анализирует производительность и выявляет медленные запросы.

```bash
# Анализировать производительность
node scripts/performance-analyzer.js

# Анализировать запросы медленнее 500ms
node scripts/performance-analyzer.js --min-time 500

# Показать топ 20 медленных запросов
node scripts/performance-analyzer.js --limit 20

# Сбросить статистику
node scripts/performance-analyzer.js reset
```

**Требует расширения:** `CREATE EXTENSION pg_stat_statements;`

**Анализирует:**
- Медленные запросы
- Использование индексов
- Статистика таблиц
- Временные тренды

---

### 7. connection-monitor.js - Connection Pool Monitor

Мониторинг состояния пула соединений в реальном времени.

```bash
# Показать текущее состояние
node scripts/connection-monitor.js

# Мониторить в реальном времени (обновление каждые 5 сек)
node scripts/connection-monitor.js --watch --interval 5000

# Завершить долгие запросы (> 300 сек)
node scripts/connection-monitor.js kill-long 300
```

**Отображает:**
- Текущие соединения
- Активные соединения
- Очередь ожидания
- Utilization percentage
- График тренда

---

### 8. health-checker.js - DB Health Check

Комплексная проверка здоровья базы данных.

```bash
# Полная проверка
node scripts/health-checker.js

# Проверить конкретные компоненты
node scripts/health-checker.js --checks connection,tables,indexes

# Выход с кодом ошибки при проблемах
node scripts/health-checker.js --exit-code
```

**Проверяет:**
1. Соединение
2. Целостность БД
3. Таблицы
4. Индексы
5. Ограничения
6. Блокировки
7. Фрагментация
8. Репликация

---

### 9. schema-diff.js - Schema Diff Tool

Сравнение схемы между двумя базами данных.

```bash
# Сравнить две БД
node scripts/schema-diff.js --source db1 --target db2

# Генерировать SQL миграции
node scripts/schema-diff.js --source db1 --target db2 --output migration.sql

# Показать различия в JSON формате
node scripts/schema-diff.js --source db1 --target db2 --output-format json
```

**Выявляет:**
- Отсутствующие таблицы
- Различия в колонках
- Изменения типов данных
- Отсутствующие индексы
- Различия в ограничениях

---

### 10. test-factory.js - Test Data Factory

Фабрика для создания тестовых данных с правильными связями.

```bash
# Создать тестовые данные для всех таблиц
node scripts/test-factory.js create --count 10

# Создать данные для конкретной таблицы
node scripts/test-factory.js create --table users --count 100

# Показать доступные таблицы
node scripts/test-factory.js list

# Очистить таблицу
node scripts/test-factory.js truncate --table users
```

**Особенности:**
- Автоматическое определение типов данных
- Умная генерация значений (email, phone, uuid и т.д.)
- Соблюдение constraints
- Батч-вставка

---

### 11. replication-setup.js - Replication Helper

Помощник для настройки репликации PostgreSQL.

```bash
# Настроить PRIMARY сервер
node scripts/replication-setup.js setup --role primary

# Настроить REPLICA сервер
node scripts/replication-setup.js setup --role replica --replica-host primary.example.com

# Создать слот репликации
node scripts/replication-setup.js setup --role primary --slot-name my_slot

# Тестировать соединение
node scripts/replication-setup.js test --replica-host primary.example.com

# Удалить слот репликации
node scripts/replication-setup.js drop-slot --slot-name my_slot
```

**Функции:**
- Проверка WAL level
- Создание слотов репликации
- Информация об LSN
- Информация о репликах
- Комманды для pg_basebackup

---

### 12. query-builder.js - Interactive Query Builder

Интерактивный конструктор SQL запросов в REPL.

```bash
# Запустить интерактивный режим
node scripts/query-builder.js

# Выбрать таблицу по умолчанию
node scripts/query-builder.js --table users

# Использовать шаблон SELECT
node scripts/query-builder.js --template select
```

**Команды в REPL:**
- `help` - Справка
- `list` - Показать таблицы
- `describe` - Описание таблицы
- `template` - Шаблоны запросов
- `show` - Показать текущий запрос
- `run` или `execute` - Выполнить запрос
- `clear` - Очистить запрос
- `exit` или `quit` - Выход

---

## Примеры Использования

### Полный цикл разработки

```bash
# 1. Создать миграцию
node scripts/migrate.js create add_users_table

# 2. Запустить миграции
node scripts/migrate.js up

# 3. Проверить схему
node scripts/schema-validator.js

# 4. Заполнить тестовыми данными
node scripts/seed.js --count 100

# 5. Проверить здоровье БД
node scripts/health-checker.js

# 6. Создать резервную копию
node scripts/backup.js create
```

### Анализ производительности

```bash
# 1. Запустить анализ
node scripts/performance-analyzer.js --limit 20 --min-time 100

# 2. Мониторить соединения
node scripts/connection-monitor.js --watch

# 3. Проверить здоровье БД
node scripts/health-checker.js --checks bloat,locks
```

### Миграция между средами

```bash
# На production
node scripts/backup.js create

# На development
node scripts/schema-diff.js --source prod_db --target dev_db

# Сравнить схемы
node scripts/schema-diff.js --source prod_db --target dev_db --output migration.sql

# Применить миграции
psql -d dev_db -f migration.sql
```

## Структура Проекта

```
scripts/
├── config.js              # Конфигурация
├── logger.js              # Логирование
├── db.js                  # Менеджер соединений
├── migrate.js             # Миграции
├── seed.js                # Генератор данных
├── backup.js              # Резервные копии
├── restore.js             # Восстановление
├── schema-validator.js    # Валидация схемы
├── performance-analyzer.js # Анализ производительности
├── connection-monitor.js  # Мониторинг соединений
├── health-checker.js      # Проверка здоровья
├── schema-diff.js         # Сравнение схем
├── test-factory.js        # Фабрика тестовых данных
├── replication-setup.js   # Настройка репликации
├── query-builder.js       # Интерактивный конструктор
└── README.md              # Эта документация
```

## Переменные Окружения

| Переменная | По умолчанию | Описание |
|------------|--------------|---------|
| DB_HOST | localhost | Хост БД |
| DB_PORT | 5432 | Порт БД |
| DB_NAME | postgres | Имя БД |
| DB_USER | postgres | Пользователь |
| DB_PASSWORD | postgres | Пароль |
| DB_SSL | false | SSL соединение |
| DB_TIMEOUT | 30000 | Timeout в ms |
| BACKUP_DIR | ./backups | Директория резервных копий |
| LOG_LEVEL | info | Уровень логирования |

## Error Handling

Все скрипты имеют:
- ✓ Обработку ошибок БД
- ✓ Транзакционность (где нужно)
- ✓ Graceful shutdown
- ✓ Exit codes для CI/CD

## Performance Tips

1. **Миграции:** Используйте батч-операции для больших данных
2. **Seed:** Отключите индексы при заполнении больших объемов
3. **Backup:** Используйте `--compression 9` для сжатия
4. **Monitor:** Используйте `--interval 1000` для частого обновления
5. **Query:** Оптимизируйте запросы перед массовым выполнением

## Лицензия

MIT
