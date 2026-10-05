# Security & Backup - Безопасность и резервные копии

**Версия:** 1.0.0
**Уровень:** Advanced
**Время:** 40 минут

---

## SQL Injection - Защита

### Проблема: Прямая подстановка

```javascript
// УЯЗВИМО - SQL Injection!
const email = "'; DROP TABLE users; --";
const query = `SELECT * FROM customers WHERE email = '${email}'`;
// Результат: SELECT * FROM customers WHERE email = ''; DROP TABLE users; --'
```

### Решение 1: Prepared Statements

```javascript
// Node.js с pg
const result = await client.query(
  'SELECT * FROM customers WHERE email = $1',
  [email]  // Параметры отдельно
);

// Python с psycopg2
cursor.execute(
  'SELECT * FROM customers WHERE email = %s',
  (email,)
)

// Prisma (автоматически защищено)
const customer = await prisma.customer.findUnique({
  where: { email }
});
```

### Решение 2: Параметризация в Prisma

```javascript
// Всегда используйте $queryRaw с параметрами
const result = await prisma.$queryRaw`
  SELECT * FROM customers WHERE email = ${email}
`;

// НЕ используйте строковую интерполяцию
const badQuery = `SELECT * FROM customers WHERE email = '${email}'`;
```

---

## Роли и права доступа

### Создание ролей

```sql
-- Создать роль для приложения
CREATE ROLE app_user WITH PASSWORD 'secure_password';

-- Создать роль для администратора
CREATE ROLE admin_user WITH PASSWORD 'admin_password' SUPERUSER;

-- Создать роль для аналитики (только чтение)
CREATE ROLE analytics_user WITH PASSWORD 'analytics_password';
```

### Выдача прав

```sql
-- Права для приложения
GRANT CONNECT ON DATABASE tourism_db TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;

-- Чтение всех таблиц
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_user;

-- Изменение данных
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;

-- Использование последовательностей (для SERIAL)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Только чтение для аналитики
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_user;
```

### Сложные правила

```sql
-- Права по таблицам
GRANT SELECT, INSERT, UPDATE ON tours TO app_user;
GRANT SELECT, INSERT ON bookings TO app_user;
GRANT SELECT ON customers TO app_user;  -- Только чтение

-- Отозвать все права
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM app_user;

-- Проверить текущие права
SELECT grantee, privilege_type
FROM table_privileges
WHERE table_name = 'tours';
```

---

## Encryption - Шифрование

### Шифрование на уровне приложения

```javascript
const crypto = require('crypto');

// Шифровать чувствительные данные ПЕРЕД сохранением в БД
function encryptData(text, password) {
  const iv = crypto.randomBytes(16);
  const key = crypto.scryptSync(password, 'salt', 32);
  const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);

  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');

  return iv.toString('hex') + ':' + encrypted;
}

// Расшифровать при чтении
function decryptData(text, password) {
  const parts = text.split(':');
  const iv = Buffer.from(parts[0], 'hex');
  const key = crypto.scryptSync(password, 'salt', 32);
  const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);

  let decrypted = decipher.update(parts[1], 'hex', 'utf8');
  decrypted += decipher.final('utf8');

  return decrypted;
}

// Использование
const passport = '1234567890';
const encrypted = encryptData(passport, 'secret_key');
await prisma.customer.create({
  data: {
    passportNumber: encrypted
  }
});
```

### Шифрование на уровне БД (PostgreSQL)

```sql
-- Расширение pgcrypto
CREATE EXTENSION pgcrypto;

-- Хранить пароли хэшированными
INSERT INTO users (email, password_hash)
VALUES ('user@example.com', crypt('password', gen_salt('bf')));

-- Проверить пароль
SELECT * FROM users
WHERE email = 'user@example.com'
  AND password_hash = crypt('password', password_hash);
```

---

## Backup и восстановление

### Dump (экспорт полной БД)

```bash
# Текстовый формат (медленнее, но портативнее)
pg_dump -U postgres -h localhost tourism_db > backup.sql

# Бинарный формат (быстрее)
pg_dump -U postgres -h localhost -Fc tourism_db > backup.dump

# Только структура (без данных)
pg_dump -U postgres -h localhost -s tourism_db > structure.sql

# Только данные (без структуры)
pg_dump -U postgres -h localhost -a tourism_db > data.sql
```

### Restore (восстановление)

```bash
# Из текстового файла
psql -U postgres -h localhost -d tourism_db < backup.sql

# Из бинарного файла
pg_restore -U postgres -h localhost -d tourism_db backup.dump

# Восстановить в новую БД
createdb tourism_db_restored
pg_restore -U postgres -h localhost -d tourism_db_restored backup.dump
```

### Point-in-time recovery (PITR)

```sql
-- Включить архивирование логов
-- postgresql.conf:
-- wal_level = replica
-- archive_mode = on
-- archive_command = 'cp %p /backup/wal_archive/%f'

-- Восстановить в точку времени
-- recovery.conf:
-- restore_command = 'cp /backup/wal_archive/%f %p'
-- recovery_target_time = '2026-02-04 14:30:00 UTC'
```

### Автоматический backup

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DB_NAME="tourism_db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Ежедневный backup
pg_dump -U postgres -Fc $DB_NAME > $BACKUP_DIR/backup_$TIMESTAMP.dump

# Удалить старые backups (старше 30 дней)
find $BACKUP_DIR -name "backup_*.dump" -mtime +30 -delete

echo "Backup completed: backup_$TIMESTAMP.dump"
```

```bash
# Добавить в crontab
0 2 * * * /path/to/backup.sh  # Ежедневно в 2:00 AM
```

---

## WAL (Write-Ahead Logging)

### Как работает WAL

```
1. Запрос пришёл
2. Записан в WAL (на диск)
3. Применён к данным (в памяти)
4. Checkpoint: данные записаны на диск
5. WAL файл можно архивировать
```

### Настройка WAL

```sql
-- postgresql.conf
wal_level = replica              -- Для PITR и streaming replication
max_wal_senders = 3              -- Максимум replication соединений
wal_keep_size = 1GB              -- Держать 1GB WAL файлов
archive_mode = on                -- Архивирование
archive_command = 'cp %p /backup/wal_archive/%f'
```

### Проверка WAL

```bash
# Список WAL файлов
pg_ls_waldir

# Размер WAL архива
du -sh /backup/wal_archive/
```

---

## Примеры для туризма

### Сценарий 1: Защита паспортных данных

```javascript
// Шифровать паспорта перед сохранением
const encryptedPassport = encryptData(
  customer.passportNumber,
  process.env.ENCRYPTION_KEY
);

await prisma.customer.update({
  where: { id: customerId },
  data: { passportNumber: encryptedPassport }
});

// При выводе - расшифровать
const customer = await prisma.customer.findUnique({ where: { id } });
const decryptedPassport = decryptData(
  customer.passportNumber,
  process.env.ENCRYPTION_KEY
);
```

### Сценарий 2: Регулярные backup

```bash
#!/bin/bash
# daily-backup.sh

BACKUP_DIR="/backups/tourism_db"
DB="tourism_db"
USER="backup_user"
HOST="db.tourism.com"

mkdir -p $BACKUP_DIR

# Полный backup каждый день
pg_dump -U $USER -h $HOST -Fc $DB > \
  $BACKUP_DIR/full_$(date +%A).dump

# Инкрементальный через WAL (автоматический)
# Настроить в postgresql.conf

# Тестировать восстановление раз в неделю
if [ $(date +%u) -eq 1 ]; then
  pg_restore -U $USER -d test_tourism_db \
    $BACKUP_DIR/full_Monday.dump && \
  echo "Restore test passed" || \
  echo "Restore test FAILED - ALERT!"
fi
```

### Сценарий 3: Audit log

```sql
-- Таблица для логирования всех изменений
CREATE TABLE audit_log (
  id SERIAL PRIMARY KEY,
  table_name VARCHAR(100),
  operation VARCHAR(10),  -- INSERT, UPDATE, DELETE
  record_id INTEGER,
  old_values JSONB,
  new_values JSONB,
  user_name VARCHAR(100),
  timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Trigger для логирования
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    INSERT INTO audit_log
      (table_name, operation, record_id, old_values, user_name)
    VALUES
      (TG_TABLE_NAME, TG_OP, OLD.id, to_jsonb(OLD), current_user);
  ELSIF TG_OP = 'UPDATE' THEN
    INSERT INTO audit_log
      (table_name, operation, record_id, old_values, new_values, user_name)
    VALUES
      (TG_TABLE_NAME, TG_OP, NEW.id, to_jsonb(OLD), to_jsonb(NEW), current_user);
  ELSIF TG_OP = 'INSERT' THEN
    INSERT INTO audit_log
      (table_name, operation, record_id, new_values, user_name)
    VALUES
      (TG_TABLE_NAME, TG_OP, NEW.id, to_jsonb(NEW), current_user);
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Применить к таблицам
CREATE TRIGGER audit_bookings
AFTER INSERT OR UPDATE OR DELETE ON bookings
FOR EACH ROW EXECUTE FUNCTION audit_trigger();
```

---

## Чек-лист безопасности

- [ ] Используются prepared statements везде
- [ ] Пароли хранятся хэшированные (bcrypt, scrypt)
- [ ] Чувствительные данные шифруются
- [ ] Роли создана и права ограничены
- [ ] Backup запускается ежедневно
- [ ] Restore регулярно тестируется
- [ ] WAL archiving включён
- [ ] Audit log ведётся для критичных операций
- [ ] Доступ к БД логируется (pg_log)
- [ ] Регулярные patching PostgreSQL

---

**Последнее обновление:** 2026-02-04
