# EXP-136: Researcher -> Presenter pipeline для больших презентаций

> Дата: 2026-02-20
> Проект: Telegram Business + Connected Bot v2.0
> Категория: pattern

## Проблема

При создании презентации из множества исходных файлов (>200KB суммарно), один агент не может одновременно:
1. Прочитать все источники
2. Выделить ключевые данные
3. Создать HTML с премиальным дизайном

Контекстное окно заполняется источниками, и на дизайн не остаётся места.

## Решение: Двухфазный pipeline

### Фаза 1: Researcher (субагент в фоне)

**Вход:** plan.md + все исходные файлы (SKILL.md, FAQ, источники, данные)
**Выход:** `content_brief.md` — исчерпывающий бриф со ВСЕМИ данными

```
content_brief.md содержит:
- Структура слайдов (номера, заголовки)
- ВСЕ цифры, метрики, проценты
- ВСЕ списки фич и преимуществ
- ВСЕ технические детали
- Цитаты и формулировки
- Категоризация контента по слайдам
```

**Правило:** Researcher должен быть ИЗБЫТОЧНЫМ — лучше включить лишние данные, чем потерять важные. Presenter сам выберет что использовать.

### Фаза 2: Presenter (субагент в фоне)

**Вход:** plan.md + content_brief.md (НЕ оригинальные источники!)
**Выход:** presentation.html (полный HTML с CSS и JS)

Presenter работает из content_brief только — чистый контекст, 100% фокус на дизайне.

### Полный pipeline

```
plan.md + sources/
    |
    v
[Researcher Agent] ---> content_brief.md
    |
    v
[Presenter Agent] ---> presentation_EN.html
    |                   presentation_RU.html (параллельно)
    v
[Playwright PDF] ---> presentation_EN.pdf
                      presentation_RU.pdf
```

## Параллельные агенты для мультиязычности

```
content_brief.md
    |
    +---> [Presenter EN] ---> presentation_EN.html (background)
    |
    +---> [Presenter RU] ---> presentation_RU.html (background)
```

Оба агента работают одновременно как background субагенты (НЕ тиммейты). Каждый получает одинаковый plan.md + content_brief.md, но с инструкцией на конкретный язык.

## Когда использовать

| Ситуация | Pipeline |
|----------|----------|
| Источники < 50KB | Один агент всё делает |
| Источники 50-200KB | Можно один агент, но лучше pipeline |
| Источники > 200KB | ОБЯЗАТЕЛЬНО pipeline |
| 2+ языка | ОБЯЗАТЕЛЬНО параллельные агенты |

## Отличие от EXP-132 (5 агентов)

EXP-132 описывает 5-агентный pipeline для максимального качества (Content Architect + CSS Architect -> HTML Builder -> Static + QA). Текущий EXP-136 — **облегчённый 2-агентный pipeline**: Researcher -> Presenter. Подходит когда:
- Нужна скорость (2 агента вместо 5)
- CSS дизайн-система уже выбрана (не нужен CSS Architect)
- Не нужна static-версия (только HTML + PDF)

## Связанные записи

- EXP-077 -- Team parallel design
- EXP-132 -- Presentation pipeline 5 агентов 3 волны
