# PAT-025: UX-полировка Telegram-бота — параллельные субагенты

**Дата:** 2026-02-23
**Проект:** VIP-DXB-CatalogBot
**Severity:** high
**Times applied:** 1

## Контекст
UX-полировка CRM Telegram-бота (aiogram 3, SQLite). 25+ файлов, P1/P2/P3 задачи — от Unicode escapes до i18n и formatter module.

## Уроки

### 1. Variable shadowing при импорте formatter helpers
**Тип:** warning
При импорте `price()` из formatter.py — локальные переменные `price = block.price_adult` затеняют функцию. Решение: переименовать локальные (`block_price`, `custom_price`).

### 2. DefaultBotProperties наследуется всеми методами
**Тип:** pattern
`DefaultBotProperties(parse_mode=ParseMode.HTML)` в aiogram 3 применяется ко ВСЕМ методам бота (send_message, edit_text, answer). Явный parse_mode нужен только при переопределении.

### 3. Safe HTML truncation — обязательна для Telegram
**Тип:** fix
Наивная обрезка `text[:N]` разрезает HTML-теги пополам, ломая parse_mode=HTML. Stack-based подход: отслеживать открытые теги, обрезать только текст, закрывать все теги.

### 4. asyncio.to_thread() для sync file I/O в async
**Тип:** fix (MANDATORY по триггеру #20)
fpdf2 `report.output(filepath)` блокирует event loop. `await asyncio.to_thread()` перемещает в ThreadPoolExecutor.

### 5. Direct SQL bypass (db._db.execute) — анти-паттерн
**Тип:** warning
Обход CatalogDB API делает код невидимым для grep по методам и непокрытым тестами. Всегда создавать API-метод.

### 6. Параллельные субагенты для независимых задач — 6x ускорение
**Тип:** pattern
6 независимых P1 задач запущены параллельно. Все завершились без конфликтов. Ключ: каждый агент работает с ОТДЕЛЬНЫМИ файлами.

### 7. i18n: проверять существующие ключи перед добавлением
**Тип:** pattern
Агент добавил ключи search.* в локали, но они уже существовали от предыдущего агента. Проверка дедупликации обязательна.

## Результат
- 25+ файлов изменено
- 702 passed, 0 регрессий
- 10 субагентов параллельно, 0 конфликтов
