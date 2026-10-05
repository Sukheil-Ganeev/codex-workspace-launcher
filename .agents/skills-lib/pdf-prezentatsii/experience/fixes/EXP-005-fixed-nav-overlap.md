---
id: EXP-005
date: 2026-02-05
type: fix
severity: high
category: layout
projects: []
related: [EXP-022]
tags: [navigation, fixed, overlap, padding, z-index]
status: verified
---

# Fix: Fixed Navigation Overlap

**ID:** EXP-005
**Дата:** 2026-02-05
**Контекст:** MCP Presentation - навигация перекрывает первую секцию

## Проблема

Fixed navigation bar перекрывает контент первой секции после hero.

**Симптомы:**
- Navigation bar накладывается поверх карточек/контента
- Первые элементы секции частично скрыты под nav
- Визуально видно на скриншоте: nav перекрывает "Реальное время" и "Автоматизация"

**Причина:**
```css
/* Navigation */
.nav {
    position: fixed;  /* Всегда сверху */
    top: 0;
    z-index: 1000;    /* Поверх всего */
    height: 64px;
}

/* Hero section */
.hero {
    padding: 120px 32px 80px;  /* Верхний отступ компенсирует nav */
}

/* Первая секция */
.section {
    padding: 120px 32px;  /* НЕ достаточно! */
}
```

**Расчет проблемы:**
- Nav height: 64px
- Section padding-top: 120px
- Контент начинается на: 120px от верха секции
- Но nav занимает первые 64px экрана
- **Недостаток:** 64px контента перекрыто

## Решение

Добавить дополнительный `padding-top` для **первой** секции:

```css
/* Fix: First section after hero needs extra top padding to avoid nav overlap */
.section:first-of-type {
    padding-top: 180px;  /* 120px (стандарт) + 60px (компенсация nav) */
}
```

**Почему 180px:**
- Стандартный padding: 120px
- Nav height: 64px
- Плюс небольшой зазор: ~4px
- Итого: 120 + 60 = 180px

## Диагностика

**Как обнаружить:**
1. Открыть HTML в браузере
2. Прокрутить к первой секции после hero
3. Проверить: перекрывает ли nav контент?

**Команда для поиска:**
```bash
grep -n "position: fixed" file.html  # Найти fixed элементы
grep -n "\.section {" file.html      # Найти секции
```

**Визуальная проверка:**
- Открыть DevTools (F12)
- Выделить `.section:first-of-type`
- Проверить `padding-top`
- Сравнить с высотой `.nav`

## Верификация фикса

**До фикса:**
- Nav перекрывает карточки
- Первые 60-70px контента не видны

**После фикса:**
- Контент начинается ниже nav
- Все карточки полностью видны
- Визуальный зазор между nav и контентом

**Проверка в коде:**
```bash
grep -A 3 "section:first-of-type" file.html
# Должно показать: padding-top: 180px
```

## Когда применять

**Всегда при:**
- Fixed header/navigation (`position: fixed; top: 0`)
- Презентации с full-height hero секцией
- Landing pages с sticky nav

**Не нужно если:**
- Navigation не fixed (position: static/relative)
- Hero секция уже имеет достаточный padding
- Нет hero секции (первая секция = обычная)

## Альтернативные решения

### Вариант 1: CSS Variable (более гибко)
```css
:root {
    --nav-height: 64px;
}

.section:first-of-type {
    padding-top: calc(120px + var(--nav-height));
}
```

### Вариант 2: Scroll Padding (современный)
```css
html {
    scroll-padding-top: 64px;
}
```
**Примечание:** Работает только для якорных ссылок, не решает визуальное перекрытие.

### Вариант 3: Margin-top (не рекомендуется)
```css
.section:first-of-type {
    margin-top: 64px;
}
```
**Проблема:** Может создать пустое пространство, нарушить layout.

## Связанные уроки

- `_index.md` — урок #10
- `patterns/css-compactification.md` — общая компактификация padding

## Важные замечания

1. **Проверяйте высоту nav:** Если nav имеет другую высоту (не 64px), скорректируйте padding-top
2. **Responsive design:** На мобильных nav может быть другой высоты
3. **Sticky vs Fixed:** Для `position: sticky` та же проблема
4. **Z-index конфликты:** Убедитесь что nav имеет достаточный z-index

## Код-пример (полный)

```css
/* Navigation */
.nav {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 64px;
    background: rgba(10, 10, 11, 0.85);
    backdrop-filter: blur(20px);
    z-index: 1000;
}

/* Sections */
.section {
    padding: 120px 32px;
    max-width: 1400px;
    margin: 0 auto;
}

/* Fix: First section needs extra padding */
.section:first-of-type {
    padding-top: 180px; /* 120px standard + 60px nav compensation */
}
```

## Тестирование

**Ручное тестирование:**
1. Открыть презентацию в браузере
2. Прокрутить к первой секции
3. Проверить визуально - nav не должен перекрывать контент

**Автоматическое (Playwright):**
```python
# Проверить что первый элемент секции не перекрыт nav
section_top = page.query_selector('.section:first-of-type .card').bounding_box()['y']
nav_bottom = page.query_selector('.nav').bounding_box()['height']

assert section_top > nav_bottom, f"Контент перекрыт: {section_top} <= {nav_bottom}"
```
