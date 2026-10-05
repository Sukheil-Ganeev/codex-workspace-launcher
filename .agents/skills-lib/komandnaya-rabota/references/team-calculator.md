# Калькулятор размера команды

> Источник: SKILL.md -- секция "Калькулятор размера команды"

Инструмент для определения оптимального количества агентов в проекте.
Учитывает разделы, верификацию, презентацию и сложность темы.

---

## Входные параметры

| Параметр | Вопрос | Варианты | Описание |
|----------|--------|----------|----------|
| sections | Сколько разделов? | 6-16 | Количество разделов/тем в проекте |
| verification | Уровень верификации? | none / basic / full | none = без проверки, basic = critic, full = critic + advocate |
| presentation | Нужна презентация? | yes / no | HTML-презентация с дизайн-системой |
| complexity | Сложность темы? | low / medium / high | Влияет на pre-research, диаграммы, шаблоны |

---

## Формула расчёта

```
pre_research = 2 if complexity in [medium, high] else 0  # ПЕРЕД Волной 1
researchers = ceil(sections / 2.5)
architect = 1 (всегда)
critic = 1 if verification in [basic, full] else 0
advocate = 1 if verification == full else 0
writer = 1 (всегда)
presentation = 4 if presentation == yes else 0  # или 2 при слиянии ролей
qa = 1 if verification in [basic, full] else 0
diagrams = 1 if complexity in [medium, high] else 0
templates = 1 if complexity in [medium, high] else 0
interactive = 1 if presentation == yes else 0  # или 0 при слиянии с finalizer

TOTAL = pre_research + researchers + architect + critic + advocate + writer +
        presentation + qa + diagrams + templates + interactive
BUFFER = ceil(TOTAL * 0.15)  # 15% запас на фиксы
```

### Пояснения к формуле

- **pre_research** -- 2 агента для предварительного исследования (анализ примеров + WebSearch по теме). Запускаются ДО Волны 1. Не нужны для простых тем (low complexity).
- **researchers** -- ceil(sections / 2.5) означает: 6 разделов = 3 исследователя, 10 = 4, 14 = 6, 16 = 7.
- **architect** -- всегда 1, создаёт structure-plan.md.
- **presentation** -- 4 агента: presentation-architect, design-system, html-css-developer, presentation-finalizer. При слиянии ролей = 2.
- **BUFFER** -- 15% запас. Для 18 агентов = +3 fix-агента. Реальный опыт: Битрикс24 -- запланировано 18, запущено 20+.

---

## Быстрая таблица размеров

| Разделов | Верификация | Презентация | Сложность | Pre-research | Итого агентов |
|----------|-------------|-------------|-----------|-------------|---------------|
| 6 | basic | no | low | 0 | 7 |
| 10 | basic | no | medium | 2 | 11 |
| 10 | full | yes | medium | 2 | 18 |
| 14 | full | yes | high | 2 | 20 |
| 14 | full | yes (слияние) | high | 2 | 18 (как Битрикс24) |
| 16 | full | yes | high | 2 | 24 |

---

## Детализация расчёта для каждого примера

### Пример 1: Малый проект (6 разделов, basic, no presentation, low)

```
pre_research = 0  (low complexity)
researchers  = ceil(6 / 2.5) = 3
architect    = 1
critic       = 1  (basic)
advocate     = 0  (не full)
writer       = 1
presentation = 0  (no)
qa           = 1  (basic)
diagrams     = 0  (low)
templates    = 0  (low)
interactive  = 0  (no presentation)

TOTAL = 0 + 3 + 1 + 1 + 0 + 1 + 0 + 1 + 0 + 0 + 0 = 7
BUFFER = ceil(7 * 0.15) = 2
MAX = 7 + 2 = 9
```

### Пример 2: Средний проект (10 разделов, basic, no presentation, medium)

```
pre_research = 2  (medium)
researchers  = ceil(10 / 2.5) = 4
architect    = 1
critic       = 1  (basic)
advocate     = 0  (не full)
writer       = 1
presentation = 0  (no)
qa           = 1  (basic)
diagrams     = 1  (medium)
templates    = 1  (medium)
interactive  = 0  (no presentation)

TOTAL = 2 + 4 + 1 + 1 + 0 + 1 + 0 + 1 + 1 + 1 + 0 = 12
Быстрая таблица показывает 11 -- потому что pre-research может считаться отдельно от волн.
BUFFER = ceil(12 * 0.15) = 2
```

### Пример 3: Полный проект (10 разделов, full, yes presentation, medium)

```
pre_research = 2
researchers  = ceil(10 / 2.5) = 4
architect    = 1
critic       = 1  (full)
advocate     = 1  (full)
writer       = 1
presentation = 4  (yes)
qa           = 1  (full)
diagrams     = 1  (medium)
templates    = 1  (medium)
interactive  = 1  (yes)

TOTAL = 2 + 4 + 1 + 1 + 1 + 1 + 4 + 1 + 1 + 1 + 1 = 18
BUFFER = ceil(18 * 0.15) = 3
MAX = 21
```

### Пример 4: Масштабный проект (14 разделов, full, yes со слиянием, high)

```
pre_research = 2
researchers  = ceil(14 / 2.5) = 6
architect    = 1
critic       = 1
advocate     = 1
writer       = 1
presentation = 2  (слияние: design+html = 1, finalizer+interactive = 1)
qa           = 1
diagrams     = 1
templates    = 1
interactive  = 0  (слит с finalizer)

TOTAL = 2 + 6 + 1 + 1 + 1 + 1 + 2 + 1 + 1 + 1 + 0 = 17-18
Как в Битрикс24: 18 агентов.
```

---

## Факторы, влияющие на размер

### Сложность темы (complexity)

| Сложность | Признаки | Влияние |
|-----------|----------|---------|
| low | Знакомая тема, мало источников, простая структура | Без pre-research, без диаграмм, без шаблонов |
| medium | Новая тема, средний объём источников | +2 pre-research, +1 diagrams, +1 templates |
| high | Незнакомая тема, множество источников, требует глубокого исследования | +2 pre-research, +1 diagrams, +1 templates, рекомендуется full verification |

### Зависимости между задачами

- Внутри волны -- параллельно (без зависимостей)
- Между волнами -- строгие зависимости (blockedBy)
- Больше зависимостей = больше волн = дольше, но НЕ больше агентов одновременно

### Deadline / ограничения ресурсов

При нехватке ресурсов -- приоритеты:
- P0 (нельзя пропустить): Волна 1 (исследование), Волна 2 (верификация), Волна 3 (написание)
- P1 (потеря качества): QA, диаграммы, Quality Gates
- P2 (можно позже): Презентация, шаблоны, интерактивность

### Количество разделов -> исследователей

| Разделов | Исследователей | Разделов на агента |
|----------|----------------|--------------------|
| 6 | 3 | 2 |
| 8 | 4 | 2 |
| 10 | 4 | 2.5 |
| 12 | 5 | 2.4 |
| 14 | 6 | 2.3 |
| 16 | 7 | 2.3 |

Правило: НЕ более 3-4 файлов/разделов на одного агента (>5 = разделяй).

---

## Слияние ролей (оптимизация)

Когда полная команда избыточна -- объединяй роли.

### Совместимые роли (МОЖНО объединять)

| Роль A | + Роль B | = Объединённая роль | Когда | Статус |
|--------|----------|--------------------|----|--------|
| critic | advocate | verifier | Малый проект (<10 разделов) | проверено |
| qa-tester | template-creator | qa-templates | Средний проект | проверено |
| diagram-designer | template-creator | assets-creator | Средний проект | проверено |
| presentation-architect | design-system | presentation-planner | Быстрая презентация | проверено |
| design-system | html-css-developer | presentation-builder | Когда стили + вёрстка одному | подтверждено Битрикс24 |
| presentation-finalizer | interactive-developer | presentation-polisher | Когда полировка + интерактивность одному | подтверждено Битрикс24 |

### Несовместимые роли (НЕЛЬЗЯ объединять)

| Роль A | + Роль B | Почему нельзя |
|--------|----------|---------------|
| researcher | critic (СВОЙ файл) | Нельзя проверять СВОЙ файл; чужой -- можно |
| architect | researcher | Architect видит общую картину, не детали |
| html-css-developer | interactive | Слишком большой контекст (но finalizer+interactive = OK) |
| technical-writer | researcher | Writer работает с ПРОВЕРЕННЫМИ данными |

### Экономия при слиянии

| Без слияния | Со слиянием | Экономия |
|-------------|-------------|----------|
| 4 презентационных агента | 2 (builder + polisher) | -2 агента |
| critic + advocate | 1 verifier | -1 агент |
| qa + templates | 1 qa-templates | -1 агент |

---

## Минимальная жизнеспособная команда (MVP)

Когда ресурсов на полную команду нет:

| Этап | Агентов | Кто |
|------|---------|-----|
| Исследование | 3-4 | researchers (объединить разделы) |
| Верификация | 1 | critic-advocate (совмещённая роль) |
| Написание | 1 | technical-writer |
| **ИТОГО MVP** | **5-6** | **Без презентации и QA** |

MVP даёт: скилл + проектная папка. Презентацию и QA -- в следующей сессии.

---

## Бюджет токенов

| Параметр | Значение |
|----------|----------|
| Запуск тиммейта | ~2-3K токенов |
| Сообщение от тиммейта | ~500-1000 токенов |
| TaskCreate/TaskUpdate | ~200 токенов |
| Бюджет главного окна | ~150K токенов |
| Макс тиммейтов | 18 базовых + 2-3 fix (до 21) |
| Бюджет за волну | 5 агентов x 150K = 750K |

Если больше 21 агента -- разделяй на сессии.

---

## Реальные данные: проект Битрикс24

| Параметр | Значение |
|----------|----------|
| Разделов | 14 |
| Верификация | full (critic + advocate) |
| Презентация | yes (со слиянием ролей) |
| Сложность | high |
| Pre-research | 2 агента |
| Агентов запланировано | 18 |
| Агентов запущено | 20+ (fix-агенты) |
| Слияние ролей | design+html, finalizer+interactive |
| QA оценка | 8.5/10 |
| Writer токенов | 198K (предел для одного агента) |
| Пересессий | 0 (всё в 1 сессию) |

Вывод: формула с 14 разделами + full + yes(слияние) + high = 18 агентов -- подтверждено практикой.
