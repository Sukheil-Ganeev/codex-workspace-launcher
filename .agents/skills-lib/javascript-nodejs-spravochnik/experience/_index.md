# Опыт использования скилла: JavaScript & Node.js Production Справочник

**Дата создания:** 2026-02-04
**Последнее обновление:** 2026-02-04

---

## Критические уроки (топ-5)

### 1. Всегда используйте environment variables для секретов

**Проблема:** API keys и database URLs в коде
**Решение:** Всегда использовать .env файлы и process.env
**Файл:** Все templates и examples
**Важность:** 🔴 Критично для security

```javascript
// Никогда
const STRIPE_KEY = 'sk_live_123456789';

// Всегда
const STRIPE_KEY = process.env.STRIPE_SECRET_KEY;
```

### 2. Обрабатывайте Promise rejections глобально

**Проблема:** Необработанные async ошибки крашат приложение
**Решение:** Добавить global handlers для unhandledRejection
**Файл:** error-handling.md, express-server-template.js
**Важность:** 🔴 Критично для stability

```javascript
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection:', reason);
  process.exit(1);
});
```

### 3. Используйте connection pooling для database

**Проблема:** Connection leaks при работе с PostgreSQL
**Решение:** Всегда используйте pool.connect() с try/finally
**Файл:** database-integration.md
**Важность:** 🟡 Важно для performance

```javascript
const client = await pool.connect();
try {
  const result = await client.query('SELECT * FROM tours');
  return result.rows;
} finally {
  client.release(); // Обязательно!
}
```

### 4. Rate limiting обязателен для публичных API

**Проблема:** API уязвим к DDoS атакам
**Решение:** express-rate-limit для всех публичных endpoints
**Файл:** express-api.md, rest-api-route.js
**Важность:** 🔴 Критично для security

```javascript
const rateLimit = require('express-rate-limit');
app.use('/api/', rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));
```

### 5. Валидация входных данных перед обработкой

**Проблема:** Невалидные данные попадают в БД и ломают логику
**Решение:** express-validator для всех POST/PUT endpoints
**Файл:** express-api.md, booking-form-handler example
**Важность:** 🔴 Критично для data integrity

```javascript
const { body, validationResult } = require('express-validator');

app.post('/api/bookings', [
  body('email').isEmail(),
  body('date').isISO8601()
], (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  // Process...
});
```

---

## Статистика использования

- **Скилл активирован:** 0 раз (создан 2026-02-04)
- **Templates скопированы:** 0
- **Examples использованы:** 0
- **Записей в experience:** 0

---

## Как записывать опыт

### Категории

1. **fixes/** - Исправленные ошибки
   - Формат: `YYYY-MM-DD-краткое-описание.md`
   - Содержание: Проблема → Причина → Решение → Код

2. **improvements/** - Найденные улучшения
   - Формат: `YYYY-MM-DD-что-улучшено.md`
   - Содержание: Было → Стало → Почему лучше

3. **patterns/** - Повторяющиеся паттерны
   - Формат: `название-паттерна.md`
   - Содержание: Описание → Когда использовать → Пример кода

4. **warnings/** - Что НЕ делать
   - Формат: `что-не-делать.md`
   - Содержание: Антипаттерн → Почему плохо → Правильный способ

### Пример записи

```markdown
# 2026-02-04: SQL injection в booking API

## Проблема
API endpoint /api/bookings принимал user input напрямую в SQL query

## Причина
Использовали string concatenation вместо параметризованных запросов

## Решение
Переписали на prepared statements с placeholders

## Код

До:
const query = `SELECT * FROM bookings WHERE user_id = ${userId}`;

После:
const query = 'SELECT * FROM bookings WHERE user_id = $1';
const result = await pool.query(query, [userId]);

## Урок
Всегда используйте параметризованные запросы для защиты от SQL injection
```

---

## Связанные ресурсы

- SKILL.md - Главный файл справочника
- references/ - Детальные модули
- assets/templates/ - Шаблоны с best practices
- assets/examples/ - Рабочие примеры

---

**Следующее обновление:** После первого месяца использования
