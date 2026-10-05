# EXP-137: Horizontal scrollbar от glow blobs

> Дата: 2026-02-20
> Проект: Telegram Business + Connected Bot v2.0
> Категория: fix

## Проблема

Ambient glow blobs (position: absolute, filter: blur(150px), ширина 600-800px) выходят за границы viewport, вызывая горизонтальный scrollbar. Особенно заметно на блобах с left: -200px или right: -200px.

```css
/* Проблемный элемент */
.bg-glow {
    position: absolute;
    width: 700px;
    height: 700px;
    border-radius: 50%;
    filter: blur(150px);
    opacity: 0.15;
    left: -200px;  /* Выход за viewport! */
    top: -150px;
}
```

**Результат:** горизонтальный scrollbar на всей странице, ломает layout.

## Решение

Добавить overflow ограничения в БАЗОВЫЙ CSS (не как фикс потом!):

```css
html, body {
    overflow-x: hidden;  /* Скрыть горизонтальный overflow от glow */
}

.slide {
    overflow: hidden;     /* Каждый слайд тоже ограничивает overflow */
    position: relative;   /* Для position:absolute дочерних элементов */
}
```

## ВАЖНО

1. **Ставить В БАЗОВЫЙ CSS** — с самого начала, не добавлять как фикс позже
2. `overflow-x: hidden` на html+body убирает горизонтальный scroll
3. `overflow: hidden` на .slide изолирует glow внутри каждого слайда
4. НЕ влияет на вертикальный scroll (страница прокручивается нормально)
5. НЕ влияет на PDF (page-break работает как обычно)

## Чеклист для новых презентаций с glow

- [ ] `html, body { overflow-x: hidden; }` в базовом CSS
- [ ] `.slide { overflow: hidden; position: relative; }`
- [ ] Glow blobs: `position: absolute; z-index: 0;`
- [ ] Контент: `position: relative; z-index: 1;`

## Связанные записи

- EXP-126 -- filter:blur() раздувает PDF (для static-версии убирать blur)
- EXP-091 -- .slide > * ломает position:absolute декоров
- EXP-095 -- bg-glow opacity 0.30+ для видимости
