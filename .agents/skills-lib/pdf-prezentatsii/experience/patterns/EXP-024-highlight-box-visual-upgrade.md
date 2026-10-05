---
id: EXP-024
date: 2026-02-06
type: pattern
severity: medium
category: layout
projects: []
related: [EXP-012]
tags: [highlight-box, cards, gradient, icons, visual-upgrade]
status: verified
---

# EXP-024: Highlight Box → визуально богатые карточки-акценты

## Проблема

Стандартные `.hbox` (border-left + background) на светлой теме выглядят плоско и дёшево — как предупреждения в docs, а не как элемент дизайна. Особенно заметно когда:
- Рядом стоят карточки с тенями и border-radius
- Контент внутри важный (выводы, правила, инсайты)
- Слайд уже визуально насыщенный

## Решение

Заменять плоские `.hbox` на карточки с иконкой + gradient background + border:

### До (плоский hbox):
```html
<div class="hbox-p" style="font-size: 18px;">
  <strong>Почему дебаты лучше?</strong> Один агент находит...
</div>
```

### После (карточка с иконкой):
```html
<div class="card" style="padding: 24px 28px;
  background: linear-gradient(135deg, rgba(110,79,224,0.06) 0%, rgba(212,113,78,0.06) 100%);
  border: 2px solid var(--purple); border-radius: 18px;">
  <div style="display: flex; gap: 20px; align-items: flex-start;">
    <div style="width: 52px; height: 52px; background: var(--purple-light);
      border-radius: 14px; display: flex; align-items: center;
      justify-content: center; font-size: 26px; flex-shrink: 0;">🧠</div>
    <div>
      <div class="fw7 fs-20 mb-8" style="color: var(--purple);">Заголовок</div>
      <div class="fs-17" style="line-height: 1.6; color: var(--text-2);">
        Текст объяснения с <strong>акцентами</strong>.
      </div>
    </div>
  </div>
</div>
```

## Когда применять

- Ключевые выводы/инсайты на слайде (не предупреждения!)
- Рядом с визуально богатыми карточками (чтобы не выпадал из контекста)
- На светлых темах (на тёмных hbox с border-left нормально смотрится)

## Варианты по типу контента

### Инсайт / Вывод (purple/blue border)
- Иконка: 🧠 / 💡 / 🔬
- Gradient: purple → claude
- Заголовок: «Почему это работает», «Ключевой вывод»

### Предупреждение / Ограничение (amber border)
- Иконка: ⚠️ / 📢
- Gradient: amber → red
- Заголовок: «Ограничение», «Broadcast осторожно», «Золотое правило»

### Совет / Tip (green border)
- Иконка: 💡 / ✅
- Gradient: green → blue
- Заголовок: «Совет», «Количество teammates»

### Процесс / Цикл (purple border)
- Иконка: 🔄 / ⚙️
- Gradient: purple → green
- Заголовок: «Цикл одобрения», «Workflow»

### Результат / Итог (green border, inline — без заголовка)
- Иконка: ✅ / 🎯
- Border-left: 5px solid var(--green)
- Background: var(--green-light)
- Формат: icon + `<strong>Результат:</strong> текст...` (без отдельного заголовка)
```html
<div class="card" style="padding: 18px 24px; border-left: 5px solid var(--green); background: var(--green-light);">
  <div style="display: flex; align-items: center; gap: 14px;">
    <div style="font-size: 22px; flex-shrink: 0;">✅</div>
    <div style="font-size: 17px;"><strong>Результат:</strong> Полный ревью за 1 проход.</div>
  </div>
</div>
```

### Tip / Совет (green border, inline — без заголовка)
- Иконка: 💡
- Border-left: 5px solid var(--green)
- Background: var(--green-light)
- Формат: icon + `<strong>Label:</strong> текст...` (без отдельного заголовка)
```html
<div class="card" style="padding: 18px 24px; border-left: 5px solid var(--green); background: var(--green-light);">
  <div style="display: flex; align-items: center; gap: 14px;">
    <div style="font-size: 22px; flex-shrink: 0;">💡</div>
    <div style="font-size: 17px;"><strong>CLAUDE.md:</strong> Teammates читают его из рабочей директории.</div>
  </div>
</div>
```

### Правило выбора (два пути) — grid 1fr auto 1fr
```html
<div style="display: grid; grid-template-columns: 1fr auto 1fr; gap: 20px;">
  <div class="card" style="border: 2px solid var(--claude);">
    <div style="display: flex; gap: 18px;">
      <div class="icon">💬</div>
      <div>
        <div class="question">Нужна коммуникация?</div>
        <div class="answer" style="color: var(--claude);">→ Agent Teams</div>
      </div>
    </div>
  </div>
  <div class="or">ИЛИ</div>
  <div class="card" style="border: 2px solid var(--purple);">...</div>
</div>
```

## Два варианта замены

### Вариант A: Полная карточка (с заголовком)
- Icon (52×52px) + заголовок в цвет акцента + текст в text-2
- Для ключевых выводов, объяснений, предупреждений
- Используется когда есть 2+ строки текста и нужна иерархия

### Вариант B: Inline карточка (без заголовка)
- Icon (22px emoji) + `<strong>Label:</strong> текст` в одну строку
- border-left: 5px solid color + background: color-light
- Для результатов, советов, коротких фактов
- Занимает меньше места — подходит для плотных слайдов

**Правило:** Если hbox однострочный → Вариант B. Если 2+ строки → Вариант A.

## Процедура аудита hbox (ОБЯЗАТЕЛЬНАЯ!)

Перед заменой hbox на карточки:
1. `grep -n "hbox" presentation.html` — найти ВСЕ экземпляры
2. Составить список: слайд → содержимое → тип (A или B)
3. Заменить ВСЕ за один проход
4. Перепроверить: `grep -n "hbox" presentation.html` — должно быть 0 (или только допустимые)

**Допустимые hbox:** Внутри карточек сравнения (VS-layout), где border-left является частью дизайна секции.

## Когда НЕ применять

- На тёмных темах hbox с border-left нормально смотрится
- Внутри VS-layout / сравнительных секций (border-left = часть дизайна)

## Принципы

1. **Иконка** — визуальный якорь, глаз сразу находит блок
2. **Gradient background** — мягкий переход двух цветов, не плоский
3. **Border в цвет акцента** — выделяет блок среди обычных карточек
4. **Заголовок в цвет акцента** — типографическая иерархия
5. **Текст var(--text-2)** — вторичный цвет для тела, заголовок доминирует
6. **ВСЕ акцентные блоки единообразны** — на одной презентации все hbox заменены, не частично

## Дата и контекст

- **Сессия:** 2026-02-06 — Claude Agent Teams презентация (17 слайдов, светлая тема)
- **Фидбек #1:** "не нравится как комментарий оформлен визуально" → заменены 2 блока (слайды 12, 13)
- **Фидбек #2:** "исправь ещё 5 таких блоков" → заменены 5 блоков (слайды 04, 05, 06, 08, 09). Заявлено "7 из 7 — все hbox заменены"
- **Фидбек #3:** "тут тоже исправь" → найдены ЕЩЁ 2 hbox (слайды 11, 16), которые пропустили. Использован Вариант B (inline)
- **Критический урок:** Заявление "все заменены" оказалось ложным — не был сделан grep-аудит. **ВСЕГДА делай grep ДО и ПОСЛЕ замены!**
