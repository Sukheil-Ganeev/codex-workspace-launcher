# Responsive Design Reference

Адаптивный дизайн критически важен для туристических сайтов — более 80% ваших клиентов бронируют туры и экскурсии со смартфонов прямо на месте в Дубае.

---

## 1. Mobile-First Approach

### Философия mobile-first

**Почему mobile-first?**
- 80% туристов в ОАЭ используют мобильные устройства для поиска экскурсий
- Туристы принимают решения "на ходу" — между достопримечательностями
- Проще добавлять функции для больших экранов, чем убирать для маленьких
- Google индексирует mobile-версию в первую очередь

**Принципы:**
1. Начинайте дизайн с экрана 320px (iPhone SE)
2. Базовые стили пишите БЕЗ media queries
3. Media queries используйте только для усложнения на больших экранах
4. Приоритет контенту, а не декорациям

### Пример структуры CSS

```css
/* Базовые стили (mobile) — БЕЗ media query */
.tour-card {
  width: 100%;
  padding: 15px;
  margin-bottom: 20px;
  font-size: 16px;
}

.tour-title {
  font-size: 20px;
  line-height: 1.3;
}

.tour-image {
  width: 100%;
  height: auto;
}

/* Tablet — добавляем сетку */
@media (min-width: 768px) {
  .tour-card {
    width: calc(50% - 20px);
    display: inline-block;
    vertical-align: top;
  }

  .tour-title {
    font-size: 22px;
  }
}

/* Desktop — 3 колонки + больше пространства */
@media (min-width: 1200px) {
  .tour-card {
    width: calc(33.333% - 30px);
    padding: 25px;
  }

  .tour-title {
    font-size: 24px;
  }
}
```

**Практический пример для кнопки "Забронировать":**

```css
/* Mobile: на всю ширину экрана */
.booking-button {
  width: 100%;
  padding: 18px;
  font-size: 18px;
  background: #ff6600;
  border: none;
  border-radius: 8px;
}

/* Desktop: фиксированная ширина */
@media (min-width: 768px) {
  .booking-button {
    width: auto;
    min-width: 250px;
    padding: 15px 40px;
  }
}
```

---

## 2. Breakpoints для туризма

### Рекомендуемые breakpoints

**Статистика по устройствам туристов в ОАЭ:**
- Mobile (320-767px): ~70% трафика
- Tablet (768-1199px): ~15% трафика
- Desktop (1200px+): ~15% трафика

### Стандартная структура

```css
/* Mobile (default) — основная аудитория */
.container {
  padding: 10px;
  max-width: 100%;
}

.tour-grid {
  display: block; /* Один тур на строку */
}

.price {
  font-size: 24px;
  font-weight: bold;
}

/* Tablet (768px) — планшеты и большие телефоны */
@media (min-width: 768px) {
  .container {
    padding: 20px;
    max-width: 750px;
    margin: 0 auto;
  }

  .tour-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
  }

  .tour-grid > * {
    flex: 0 0 calc(50% - 10px); /* 2 колонки */
  }
}

/* Desktop (1200px) — компьютеры и большие ноутбуки */
@media (min-width: 1200px) {
  .container {
    padding: 40px;
    max-width: 1200px;
  }

  .tour-grid > * {
    flex: 0 0 calc(33.333% - 14px); /* 3 колонки */
  }

  .price {
    font-size: 28px;
  }
}
```

**Не используйте промежуточные breakpoints без необходимости** — 3 точки достаточно для 95% случаев.

---

## 3. Responsive Images

### Picture element для туристических фото

```html
<picture>
  <!-- Desktop: высокое качество для больших экранов -->
  <source
    media="(min-width: 1200px)"
    srcset="burj-khalifa-large.jpg">

  <!-- Tablet: средний размер -->
  <source
    media="(min-width: 768px)"
    srcset="burj-khalifa-medium.jpg">

  <!-- Mobile: оптимизированное изображение (fallback) -->
  <img
    src="burj-khalifa-small.jpg"
    alt="Burj Khalifa Tour"
    loading="lazy">
</picture>
```

### srcset и sizes для галерей

```html
<!-- Пример для карточки экскурсии -->
<img
  src="desert-safari-400.jpg"
  srcset="desert-safari-400.jpg 400w,
          desert-safari-800.jpg 800w,
          desert-safari-1200.jpg 1200w"
  sizes="(max-width: 767px) 100vw,
         (max-width: 1199px) 50vw,
         400px"
  alt="Desert Safari Dubai">
```

**Расшифровка:**
- `400w, 800w, 1200w` — доступные размеры изображений
- `100vw` — на mobile занимает 100% ширины экрана
- `50vw` — на tablet занимает 50% (2 колонки)
- `400px` — на desktop фиксированная ширина

### Оптимизация для скорости

```css
/* Lazy loading для изображений ниже fold */
img[loading="lazy"] {
  opacity: 0;
  transition: opacity 0.3s;
}

img[loading="lazy"].loaded {
  opacity: 1;
}

/* Aspect ratio для предотвращения layout shift */
.tour-image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 66.67%; /* 3:2 aspect ratio */
  overflow: hidden;
}

.tour-image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```

---

## 4. Touch-Friendly Design

### Минимальные размеры для касаний

**Apple и Google рекомендуют:**
- Минимальный размер: **44x44px** (iOS) или **48x48dp** (Android)
- Оптимальный размер: **48-56px** для важных кнопок

```css
/* Кнопка "Забронировать" */
.book-button {
  min-width: 120px;
  min-height: 48px;
  padding: 12px 24px;
  font-size: 16px;

  /* Легче попасть пальцем */
  margin: 10px 0;
}

/* Ссылки в тексте */
a {
  display: inline-block;
  padding: 8px 4px; /* Увеличиваем зону клика */
  margin: -8px -4px; /* Компенсируем визуально */
}

/* Иконки навигации */
.nav-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

### Отступы между элементами

```css
/* Минимальные отступы между кликабельными элементами */
.button-group button {
  margin: 8px; /* Минимум 8px между кнопками */
}

/* Форма бронирования */
.booking-form input,
.booking-form select {
  height: 48px;
  margin-bottom: 16px; /* Достаточно места между полями */
  font-size: 16px; /* Предотвращает зум в iOS */
}
```

### Swipe gestures для галерей

```css
/* CSS для swipe-галереи */
.tour-gallery {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch; /* Плавная прокрутка iOS */
  gap: 10px;
  padding: 10px;
}

.tour-gallery img {
  scroll-snap-align: start;
  flex-shrink: 0;
  width: 85vw;
  height: 60vw;
  object-fit: cover;
  border-radius: 12px;
}

/* Скрываем scrollbar */
.tour-gallery::-webkit-scrollbar {
  display: none;
}
```

### Hover states для desktop + active для mobile

```css
.tour-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

/* Desktop: hover */
@media (min-width: 1200px) {
  .tour-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
  }
}

/* Mobile: active (при нажатии) */
@media (max-width: 1199px) {
  .tour-card:active {
    transform: scale(0.98);
  }
}
```

### Крупные формы для туристов

```css
/* Форма бронирования экскурсии */
.booking-form {
  padding: 20px;
}

.booking-form input,
.booking-form select,
.booking-form textarea {
  width: 100%;
  height: 56px; /* Больше стандартных 48px */
  padding: 0 16px;
  font-size: 16px; /* Предотвращает автозум в Safari iOS */
  border: 2px solid #ddd;
  border-radius: 8px;
  margin-bottom: 16px;
}

.booking-form textarea {
  height: 120px;
  padding: 16px;
  resize: vertical;
}

/* Важно: font-size: 16px предотвращает зум при фокусе в iOS */
```

---

## Практические советы для туризма

1. **Тестируйте на реальных устройствах** — девайсы туристов разные
2. **Приоритет скорости** — туристы часто на медленном роуминге
3. **Упрощайте навигацию** — турист на жаре и спешит
4. **Кнопки видны без прокрутки** — "Забронировать" должна быть доступна
5. **Цены крупно и четко** — главная информация для принятия решения

**Инструменты для тестирования:**
- Chrome DevTools (F12 → Toggle device toolbar)
- Реальные устройства (iPhone, Samsung Galaxy)
- BrowserStack для проверки на разных экранах
