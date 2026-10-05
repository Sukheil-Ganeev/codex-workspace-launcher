# Шпаргалка командной работы
> Актуально на: 2026-02-15

## Быстрый старт (7 шагов)

1. TeamCreate → team_name
2. Создать папки (mkdir)
3. TaskCreate x N (все задачи)
4. TaskUpdate addBlockedBy (зависимости)
5. Task x N (запуск Волны 1)
6. Мониторинг → Shutdown → Следующая волна
7. TeamDelete после всех shutdown

## Размеры команд

| Проект | Агентов | Волн |
|--------|---------|------|
| Малый | 3-5 | 2-3 |
| Средний | 8-12 | 3-4 |
| Полный | 18+ | 5 |

## Параметры запуска агента

subagent_type: "general-purpose"
team_name: "проект"
mode: "bypassPermissions"
run_in_background: true
name: "роль"

## Зависимости (пример)

Волна 1: tasks 1-7 → нет blockedBy
Волна 2: task 8 → blockedBy [1-7], task 9 → blockedBy [8]
Волна 3: task 10 → blockedBy [9]

## Золотые правила (топ-5)

1. Главное окно = диспетчер
2. Верификация обязательна (< 6 файлов = 1 verifier, >= 6 = critic + advocate) [ОБНОВЛЕНО по Ревизии 8]
3. Shutdown после Quality Gate, не после волны [ОБНОВЛЕНО по Ревизии 9]
4. Задачи Волны 1 — сразу, Волны 2-5 — уточнить после architect [ОБНОВЛЕНО по Ревизии 7]
5. Детальные промпты

## Auto-scaling Calculator

### Входные данные

| Параметр | Вопрос | Варианты |
|----------|--------|----------|
| sections | Сколько разделов? | 6-16 |
| verification | Уровень верификации? | none / basic / full |
| presentation | Нужна презентация? | yes / no |
| complexity | Сложность темы? | low / medium / high |

### Формула

researchers = ceil(sections / 2.5)
architect = 1 (всегда)
critic = 1 if verification in [basic, full] else 0
advocate = 1 if verification == full else 0
writer = 1 (всегда)
presentation = 4 if presentation == yes else 0
qa = 1 if verification in [basic, full] else 0
diagrams = 1 if complexity in [medium, high] else 0
templates = 1 if complexity in [medium, high] else 0
interactive = 1 if presentation == yes else 0

TOTAL = researchers + architect + critic + advocate + writer + presentation + qa + diagrams + templates + interactive
BUFFER = ceil(TOTAL * 0.15)  # 15% запас на фиксы

### Быстрая таблица

| Разделов | Верификация | Презентация | Итого агентов |
|----------|-------------|-------------|---------------|
| 6 | basic | no | 7 |
| 10 | basic | no | 9 |
| 10 | full | yes | 16 |
| 14 | full | yes | 18 |
| 16 | full | yes | 22 |

## Priority System

### Уровни приоритета

P0 — НЕЛЬЗЯ ПРОПУСТИТЬ:
  - Волна 1 (исследование) — без данных нет проекта
  - Волна 2 (верификация) — без проверки данные ненадёжны
  - Волна 3 (написание) — это основной результат

P1 — ПРОПУСТИТЬ = ПОТЕРЯ КАЧЕСТВА:
  - QA-тестер — ошибки останутся
  - Diagram-designer — нет визуализации
  - Quality Gates — возможны сбои

P2 — МОЖНО СДЕЛАТЬ ПОЗЖЕ (в другой сессии):
  - Презентация (Волна 4) — можно добавить потом
  - Template-creator — шаблоны не критичны
  - Interactive-developer — интерактивность = бонус

### Минимальная жизнеспособная команда (MVP)

| Этап | Агентов | Кто |
|------|---------|-----|
| Исследование | 3-4 | researchers (объединить разделы) |
| Верификация | 1 | critic-advocate (совмещённая роль) |
| Написание | 1 | technical-writer |
| **ИТОГО MVP** | **5-6** | **Без презентации и QA** |

### Решение по ходу

Если после Волны 2 контекст > 60%:
  → Запусти technical-writer
  → Сгенерируй файл продолжения
  → Презентацию и улучшения — в новой сессии

Если после Волны 3 контекст > 60%:
  → Сгенерируй файл продолжения
  → Всё остальное — в новой сессии

## Retry Budget

Исследователь: 3 попытки
Critic/Advocate: 2 попытки
Writer: 2 попытки
Presentation: 3 попытки
QA/Diagrams: 2 попытки
