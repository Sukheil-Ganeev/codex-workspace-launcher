# EXP-CMD-034: Spy-Bot Refactoring Pipeline

**Дата:** 2026-02-18
**Категория:** pattern
**Severity:** critical
**Теги:** refactoring-pipeline, security-wave, wiring-агент, haiku-gate, pytest, bot-refactoring, 7-файлов-лимит

## Контекст

Полный рефакторинг Telegram spy-bot:
- aiogram 2 → 3 (polling → dispatcher)
- sync SQLite → async aiosqlite
- Dual AI backend (Gemini → Groq fallback)
- Хардкод-токены → .env + config.py

## Результаты

| Параметр | Значение |
|----------|----------|
| Волн | 5 + 3 gate-проверки |
| Агентов | 13 (impl) + 3 (gate на haiku) |
| Тестов | 98 |
| Падений | 0 |
| Retry | 0 |
| Время | ~90 мин wall-clock |
| Тип агентов | Обычные субагенты, run_in_background: true, bypassPermissions |

## Тайминги по волнам

| Волна | Агенты | Время | Bottleneck |
|-------|--------|-------|------------|
| Wave 0 (security) | 1 | 55 сек | - |
| Wave 1 (core) | 3 параллельно | ~140 сек | database (async migration) |
| Wave 2 (logic) | 5 параллельно | ~280 сек | handlers (7 файлов!) |
| Wave 3 (wiring) | 1 | ~170 сек | чтение + фиксы импортов |
| Wave 4 (tests) | 2 параллельно | ~310 сек | core tests (72 теста) |
| Wave 5 (polish) | 1 | ~330 сек | удаление + README + проверки |

## Ключевые уроки

### 1. Wiring-агент КРИТИЧЕН -- не просто "склей файлы"
Wave 3 (wiring) обнаружил и исправил:
- Дублирующий callback handler в export.py (конфликт с start.py)
- `bot["db"]` vs `dp["db"]` — нужно на ОБА объекта
- Отсутствующие `__init__.py`

**Правило:** Давай wiring-агенту полный доступ ко ВСЕМ файлам предыдущих волн. Wiring = интеграционное тестирование на уровне импортов.

### 2. Security wave ПЕРВОЙ — всегда
Wave 0 (55 сек) удаляет хардкод-токены, создаёт `.env` + `config.py` ПЕРЕД запуском любых других волн.

Без этого: если агенты Wave 1+ прочитают `config_old.py`, реальные API-ключи попадут в контекст агентов.

**Правило:** Для рефакторинга с секретами — Wave 0 = security. Минимальная стоимость, критический результат.

### 3. Реальный pytest > Gate-проверки через Grep
Gate-проверки (Explore + Grep) проверяют наличие файлов и классов, но НЕ проверяют что код РАБОТАЕТ.

Только pytest с реальным запуском проверяет:
- Правильность импортов
- Совместимость сигнатур
- Runtime-ошибки
- Интеграцию между модулями

98 тестов за ~310 сек — отличная инвестиция.

**Правило:** Gate = необходимый минимум (быстрая проверка между волнами). pytest = полная верификация (Wave 4).

### 4. Gate на haiku = экономия токенов
Quality Gates запускались на модели haiku — достаточно для:
- Grep по файлам
- ls проверка наличия
- Простая валидация структуры

**Правило:** Gate-проверки не требуют полноценной модели. haiku экономит токены без потери качества.

### 5. Handlers-агент на 7 файлов — предел
T2.2 (handlers) создал 7 файлов и занял 280 сек — самый долгий в Wave 2.

**Правило:** max 7 файлов на impl-агента. 10+ → разделять на 2 агента. Подтверждение лимита из EXP-CMD-032 для impl-агентов (не только тестовых).

## Паттерн: Refactoring Wave Pipeline

```
Wave 0: Security (1 агент)
  └── Удаление хардкод-токенов, .env + config.py

Gate 0→1: haiku

Wave 1: Core (параллельно)
  ├── database (async migration)
  ├── ai_client (dual backend)
  └── utils / config

Gate 1→2: haiku

Wave 2: Logic (параллельно)
  ├── handlers (max 7 файлов!)
  ├── keyboards
  ├── states / FSM
  ├── middleware
  └── export / специфичные модули

Gate 2→3: haiku

Wave 3: Wiring (1 агент, ПОЛНЫЙ ДОСТУП)
  └── main.py + __init__.py + фиксы импортов

Wave 4: Tests (параллельно)
  ├── core tests
  └── handler tests

Wave 5: Polish (1 агент)
  └── Удаление старых файлов, README, проверки
```

## Связанные записи

- **EXP-CMD-029:** Code Project Wave A/B/C/D (ContentFactory)
- **EXP-CMD-030:** Один файл = один агент + wiring отдельно
- **EXP-CMD-032:** Тестовый агент = верификатор (max 7 файлов)
- **EXP-CMD-033:** Graceful degradation как стандарт
