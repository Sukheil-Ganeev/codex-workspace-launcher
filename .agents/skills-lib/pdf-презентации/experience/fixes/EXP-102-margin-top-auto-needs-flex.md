---
id: EXP-102
date: 2026-02-13
type: fix
severity: medium
category: layout
projects: [telegram-bot, whatsapp-bot, vk-bot]
related: [EXP-096, EXP-022]
tags: [margin-top-auto, flex, card, layout, push-down]
status: verified
---

# EXP-102: margin-top: auto не работает без flex на родителе

## Проблема

Плашки типа "Для: Production" внизу карточки используют `margin-top: auto` для прижатия к низу. Но `margin-top: auto` равен 0 в обычном block flow -- работает только внутри flex-контейнера.

## Контекст

- Часто встречается на карточках с разной высотой контента
- Нижний элемент (тег, бейдж, статус) должен быть прижат к низу карточки
- Без flex родитель не распределяет свободное пространство

## Решение

**Добавить `display: flex; flex-direction: column` на родительскую карточку:**

```css
/* Карточка как flex-column контейнер */
.card {
    display: flex;
    flex-direction: column;
}

/* Контент растягивается */
.card-body {
    flex: 1;
}

/* Плашка прижата к низу */
.card-footer,
.card .tag-row {
    margin-top: auto;
}
```

```css
/* НЕПРАВИЛЬНО -- margin-top: auto без flex */
.card {
    display: block; /* или без display вообще */
}
.card .badge {
    margin-top: auto; /* = 0, не работает */
}
```

## Урок

**`margin-top: auto` для push-to-bottom работает ТОЛЬКО внутри flex-контейнера.** Альтернативы в block flow: `position: absolute; bottom: 0` (требует relative родителя и фиксированный padding-bottom) или CSS Grid с `align-self: end`.
