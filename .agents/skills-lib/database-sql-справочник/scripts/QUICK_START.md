# Database Scripts - Быстрый Старт

## Установка и Настройка (5 минут)

### 1. Установка зависимостей
```bash
cd scripts
npm install
```

### 2. Создайте `.env` файл
```bash
cat > .env << EOF
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_USER=postgres
DB_PASSWORD=your_password
BACKUP_DIR=./backups
LOG_LEVEL=info
EOF
```

### 3. Проверьте соединение
```bash
node health-checker.js
```

---

## Первые 10 Команд

### Работа с миграциями

```bash
# 1. Создать миграцию
node migrate.js create create_users_table

# 2. Посмотреть статус
node migrate.js status

# 3. Запустить миграции
node migrate.js up
```

### Тестовые данные

```bash
# 4. Заполнить данными (100 записей)
node seed.js --count 100

# 5. Заполнить конкретную таблицу (1000 записей)
node test-factory.js create --table users --count 1000
```

### Резервные копии

```bash
# 6. Создать резервную копию
node backup.js create

# 7. Показать список резервных копий
node backup.js list

# 8. Восстановить базу
node restore.js restore --file backups/backup_2024-01-15.dump --force
```

### Мониторинг

```bash
# 9. Проверка здоровья базы
node health-checker.js

# 10. Анализ производительности
node performance-analyzer.js
```

---

## Типичные Задачи

### Задача 1: Подготовка к разработке

```bash
# Очистить старые данные
node test-factory.js truncate --table users

# Заполнить новыми данными
node seed.js --count 50

# Проверить все ОК
node health-checker.js
```

### Задача 2: Развертывание на production

```bash
# 1. Проверить схему совместима
node schema-validator.js --strict

# 2. Запустить миграции
node migrate.js up

# 3. Создать резервную копию
node backup.js create

# 4. Проверить здоровье
node health-checker.js --exit-code
```

### Задача 3: Анализ проблем производительности

```bash
# 1. Мониторить соединения
node connection-monitor.js --watch &

# 2. Анализировать медленные запросы
node performance-analyzer.js --limit 10 --min-time 100

# 3. Проверить фрагментацию
node health-checker.js --checks bloat
```

### Задача 4: Миграция между БД

```bash
# На prod сервере
node backup.js create

# На dev сервере - сравнить схемы
node schema-diff.js --source prod_db --target dev_db

# Применить различия
node schema-diff.js --source prod_db --target dev_db --output migration.sql
psql -d dev_db -f migration.sql
```

### Задача 5: Интерактивное исследование данных

```bash
# Запустить интерактивный конструктор
node query-builder.js --table users

# В REPL:
sql> SELECT * FROM users LIMIT 5;
sql> UPDATE users SET active = true WHERE id = 1;
sql> help
```

---

## Шпаргалка по Флагам

### migrate.js
```bash
node migrate.js status              # Статус миграций
node migrate.js up                  # Запустить все
node migrate.js down                # Откатить одну
node migrate.js create users_table  # Создать миграцию
```

### seed.js
```bash
node seed.js --count 50             # Генерировать 50 записей
node seed.js --count 100 --clear    # Очистить и заново заполнить
```

### backup.js
```bash
node backup.js create               # Создать backup
node backup.js list                 # Показать backups
node backup.js cleanup 5            # Оставить только 5 последних
```

### health-checker.js
```bash
node health-checker.js              # Все проверки
node health-checker.js --checks connection,tables  # Выборочные
node health-checker.js --exit-code  # Выход с кодом ошибки
```

### performance-analyzer.js
```bash
node performance-analyzer.js        # Анализ
node performance-analyzer.js --limit 20    # Топ 20
node performance-analyzer.js --min-time 500 # Только > 500ms
```

### test-factory.js
```bash
node test-factory.js create         # Все таблицы
node test-factory.js create --table users --count 1000  # Конкретная таблица
node test-factory.js list           # Доступные таблицы
node test-factory.js truncate --table users  # Очистить
```

---

## Переменные Окружения

Установить для всех скриптов:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=myapp
export DB_USER=postgres
export DB_PASSWORD=password
export BACKUP_DIR=./backups
export LOG_LEVEL=info
```

Или через `.env` файл (автоматически загружается).

---

## Примеры цветовых выводов

```
✓ Success messages (зелёный)
✗ Error messages (красный)
⚠ Warnings (жёлтый)
ℹ Info (голубой)
```

---

## Troubleshooting

### Ошибка: "Database connection failed"
```bash
# Проверить параметры
echo $DB_HOST $DB_PORT $DB_NAME
cat .env

# Проверить доступность
pg_isready -h localhost -p 5432
```

### Ошибка: "ENOENT: no such file or directory"
```bash
# Создать недостающие директории
mkdir -p migrations backups
```

### Ошибка при restore
```bash
# Использовать --force флаг
node restore.js restore --file backup.dump --clean --force
```

### pg_stat_statements не найден
```bash
# Установить расширение (один раз)
psql -d myapp -c "CREATE EXTENSION pg_stat_statements;"
```

---

## Полезные SQL команды для проверки

```sql
-- Размер БД
SELECT pg_size_pretty(pg_database_size(current_database()));

-- Активные соединения
SELECT count(*) FROM pg_stat_activity;

-- Медленные запросы
SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 5;

-- Таблицы по размеру
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Размер индексов
SELECT indexname, pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## Автоматизация (Cron)

### Ежедневная резервная копия
```bash
# Добавить в crontab
0 2 * * * cd /path/to/scripts && node backup.js create >> backup.log 2>&1
```

### Еженедельная проверка здоровья
```bash
# Добавить в crontab
0 3 * * 0 cd /path/to/scripts && node health-checker.js >> health.log 2>&1
```

### Ежемесячная очистка резервных копий
```bash
# Добавить в crontab
0 4 1 * * cd /path/to/scripts && node backup.js cleanup 10 >> cleanup.log 2>&1
```

---

## Интеграция с CI/CD

### GitHub Actions пример
```yaml
- name: Database Health Check
  run: |
    cd scripts
    npm install
    node health-checker.js --exit-code

- name: Run Migrations
  run: |
    cd scripts
    node migrate.js up

- name: Backup Database
  run: |
    cd scripts
    node backup.js create
```

---

## Дополнительные ресурсы

- PostgreSQL документация: https://www.postgresql.org/docs/
- pg module: https://node-postgres.com/
- Best practices: https://wiki.postgresql.org/wiki/Useful_PostgreSQL_Documentation
