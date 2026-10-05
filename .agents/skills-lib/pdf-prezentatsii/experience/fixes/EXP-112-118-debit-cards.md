# EXP-112..118: Debit-Cards-Research (2026-02-18)

> Проект: Debit-Cards-Research -- исследовательская презентация
> Оригинальные номера пользователя: EXP-102..108 (перенумерованы из-за конфликта с EXP-102..111)

---

## EXP-112: inset highlight создаёт светлые артефакты (warning)

**Проблема:** `inset 0 1px 0 rgba(255,255,255,0.04)` в box-shadow создаёт видимые светлые квадратики в углах карточек на тёмном фоне.

**Причина:** Даже минимальный alpha (0.04) inset white highlight становится заметным артефактом на тёмных тонах из-за сложения с border-radius и другими слоями box-shadow.

**Решение:** НЕ использовать inset white highlight на тёмных темах. Если нужен верхний блик -- использовать gradient border-top или pseudo-element.

**Связано с:** EXP-092 (rgba на тёмном невидим), EXP-093 (backdrop-filter на однородном фоне).

---

## EXP-113: Slideshow mode для статических HTML-презентаций (pattern)

**Паттерн:** Статические HTML (сделанные для PDF-конвертации) можно превратить в интерактивные слайдшоу без переделки структуры.

**Реализация:**
```css
body.slideshow-mode .slide {
  display: none;
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  z-index: 10;
}
body.slideshow-mode .slide.active {
  display: flex;
}
```

**Print сохраняется:**
```css
@media print {
  .slide {
    display: flex !important;
    position: static !important;
    page-break-after: always;
  }
}
```

**JS:** IIFE, ~80 строк, keyboard nav + TOC + fullscreen. Не ломает PDF-конвертацию.

---

## EXP-114: Keyboard shortcuts стандарт для презентаций (pattern)

**Стандартный набор горячих клавиш:**

| Клавиша | Действие |
|---------|----------|
| Left / Up | Предыдущий слайд |
| Right / Down | Следующий слайд |
| T | Table of Contents (overlay toggle) |
| F | Fullscreen (document.documentElement.requestFullscreen) |
| Esc | Закрыть TOC |
| Home | Первый слайд |
| End | Последний слайд |
| Space | Следующий слайд |

**Важно:** При открытом TOC ставить `overflow: hidden` на body для блокировки прокрутки фонового контента.

---

## EXP-115: TOC overlay -- frosted glass design (pattern)

**Overlay:**
- Gradient bg (НЕ однородный rgba!) + `backdrop-filter: blur(30px) saturate(120%)`

**Panel:**
- Multi-stop gradient (4 точки, 0.85-0.9 opacity) + `blur(40px) saturate(150%)`
- SVG noise texture через `::before` (fractalNoise, opacity 0.03) для матовости

**Кнопка закрытия:**
- Крестик "X" выглядит неаккуратно -> заменить на pill-кнопку `ESC` (JetBrains Mono, 10px, uppercase)
- `h2` "Содержание" нужен `padding-right: 70px` чтобы не налезал на ESC кнопку

---

## EXP-116: "Убери свечения" != "Убери glassmorphism" (warning)

**Что пользователь имеет в виду "убери свечения":**
- Убрать `text-shadow` (glow эффекты на тексте)
- Уменьшить `.glow` opacity до 0.08
- Убрать color glow из `box-shadow` (оставить только `rgba(0,0,0,x)`)

**Что НЕ трогать:**
- `backdrop-filter` (blur, saturate)
- Gradient backgrounds на карточках
- Glass borders (rgba бордеры)
- Inset top line эффекты

**Правило:** Glass-эффекты (blur, saturate, gradient bg, inset top line) -- это НЕ свечения. Свечения = text-shadow glow + цветные box-shadow + radial glow overlays.

---

## EXP-117: Навигационные элементы -- glass style (pattern)

**#nav-arrows стиль:**
- `backdrop-filter: blur(16px) saturate(130%)`
- Полупрозрачный bg (gradient, не solid)

**Критично:**
- НЕ делать `opacity: 0.5-0.6` на навигационных кнопках -- пользователь не увидит
- Правильно: `opacity: 1`, но приглушённые цвета (accent с alpha 0.6-0.7)
- Hotkeys hint: `opacity: 0.4` -- достаточно тонкий, не мешает

---

## EXP-118: Скроллбар стилизация (pattern)

**WebKit (Chrome, Edge, Safari):**
```css
::-webkit-scrollbar { height: 4px; width: 4px; }
::-webkit-scrollbar-track { background: var(--bg-color); }
::-webkit-scrollbar-thumb { background: rgba(accent, 0.25); border-radius: 2px; }
```

**Firefox:**
```css
* { scrollbar-width: thin; scrollbar-color: rgba(accent, 0.25) var(--bg-color); }
```

**TOC panel:** Отдельные правила для вертикального скроллбара внутри панели.

**Comparison/dual-theme:** Gradient thumb (emerald -> cyan) для визуального разнообразия.

**Связано с:** EXP-109 (кастомный scrollbar обязателен, 6px).
