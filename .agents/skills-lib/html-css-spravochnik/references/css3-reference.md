# CSS3 Reference

Практический справочник по современным возможностям CSS3 для создания туристических сайтов и лендингов.

---

## 1. Layout Systems (Grid & Flexbox)

### CSS Grid - Основа для страниц туров

**Адаптивная сетка туров:**
```css
.tour-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
}

/* Для больших экранов - 3 колонки */
@media (min-width: 1200px) {
  .tour-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Для планшетов - 2 колонки */
@media (min-width: 768px) and (max-width: 1199px) {
  .tour-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

**Layout главной страницы:**
```css
.main-layout {
  display: grid;
  grid-template-areas:
    "header header header"
    "sidebar content content"
    "footer footer footer";
  grid-template-columns: 250px 1fr 1fr;
  grid-template-rows: auto 1fr auto;
  min-height: 100vh;
}

.header { grid-area: header; }
.sidebar { grid-area: sidebar; }
.content { grid-area: content; }
.footer { grid-area: footer; }
```

### Flexbox - Для навигации и карточек

**Навигационное меню:**
```css
.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  background: white;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.nav-links {
  display: flex;
  gap: 30px;
  list-style: none;
}

.nav-links a {
  text-decoration: none;
  color: #333;
  font-weight: 500;
  transition: color 0.3s;
}

.nav-links a:hover {
  color: #0066cc;
}
```

**Карточка тура с Flexbox:**
```css
.tour-card {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.tour-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.tour-card-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.tour-card-content {
  padding: 20px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.tour-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 15px;
  border-top: 1px solid #eee;
}
```

**Центрирование элементов:**
```css
/* Метод 1: Flexbox */
.center-flex {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

/* Метод 2: Grid */
.center-grid {
  display: grid;
  place-items: center;
  height: 100vh;
}
```

---

## 2. CSS Custom Properties (Variables)

### Система переменных для брендинга

**Основные цвета и размеры:**
```css
:root {
  /* Брендовые цвета */
  --primary-color: #0066cc;
  --secondary-color: #ff6b35;
  --success-color: #28a745;
  --warning-color: #ffc107;
  --danger-color: #dc3545;

  /* Нейтральные цвета */
  --text-dark: #333333;
  --text-light: #666666;
  --bg-light: #f8f9fa;
  --border-color: #e0e0e0;

  /* Отступы */
  --spacing-xs: 5px;
  --spacing-sm: 10px;
  --spacing-md: 20px;
  --spacing-lg: 40px;
  --spacing-xl: 60px;

  /* Радиусы скругления */
  --border-radius-sm: 4px;
  --border-radius-md: 8px;
  --border-radius-lg: 12px;
  --border-radius-round: 50%;

  /* Тени */
  --shadow-sm: 0 2px 4px rgba(0,0,0,0.1);
  --shadow-md: 0 4px 15px rgba(0,0,0,0.1);
  --shadow-lg: 0 8px 30px rgba(0,0,0,0.15);

  /* Шрифты */
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-heading: 'Montserrat', sans-serif;
}
```

**Использование переменных:**
```css
.button {
  background: var(--primary-color);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-sm);
  font-family: var(--font-primary);
  transition: all 0.3s ease;
}

.button:hover {
  background: color-mix(in srgb, var(--primary-color) 80%, black);
  box-shadow: var(--shadow-md);
}

.price-tag {
  color: var(--secondary-color);
  font-size: calc(var(--spacing-md) * 1.2);
  font-weight: 700;
}
```

**Темная тема (пример):**
```css
[data-theme="dark"] {
  --primary-color: #4d94ff;
  --text-dark: #f0f0f0;
  --text-light: #cccccc;
  --bg-light: #1a1a1a;
  --border-color: #333333;
}
```

---

## 3. Animations & Transitions

### Плавные переходы для интерактивности

**Hover эффекты для карточек:**
```css
.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

/* Эффект увеличения изображения */
.card-image-wrapper {
  overflow: hidden;
  border-radius: 12px 12px 0 0;
}

.card-image {
  transition: transform 0.5s ease;
}

.card:hover .card-image {
  transform: scale(1.1);
}
```

**Анимации для загрузки страницы:**
```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

/* Применение анимаций */
.hero-title {
  animation: fadeIn 0.8s ease-out;
}

.tour-card {
  animation: fadeIn 0.6s ease-out;
  animation-fill-mode: both;
}

.tour-card:nth-child(1) { animation-delay: 0.1s; }
.tour-card:nth-child(2) { animation-delay: 0.2s; }
.tour-card:nth-child(3) { animation-delay: 0.3s; }

.cta-button {
  animation: pulse 2s infinite;
}
```

**Спиннер загрузки:**
```css
@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0,0,0,0.1);
  border-left-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
```

**Плавное появление меню:**
```css
.dropdown-menu {
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: opacity 0.3s, transform 0.3s, visibility 0.3s;
}

.dropdown:hover .dropdown-menu {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}
```

---

## 4. Advanced Selectors

### Интерактивные состояния

**Псевдоклассы для форм:**
```css
/* Состояния input полей */
input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(0,102,204,0.1);
}

input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
  opacity: 0.6;
}

input:valid {
  border-color: var(--success-color);
}

input:invalid:not(:placeholder-shown) {
  border-color: var(--danger-color);
}

/* Кастомный чекбокс */
input[type="checkbox"]:checked + label::before {
  background: var(--primary-color);
  border-color: var(--primary-color);
}
```

**Структурные селекторы:**
```css
/* Первый и последний элементы */
.tour-list li:first-child {
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.tour-list li:last-child {
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
}

/* Чередующиеся цвета строк */
.price-table tr:nth-child(odd) {
  background: #f8f9fa;
}

.price-table tr:nth-child(even) {
  background: white;
}

/* Каждый третий элемент */
.tour-card:nth-child(3n) {
  border-right: none;
}

/* Все кроме первого */
.breadcrumb-item:not(:first-child)::before {
  content: "›";
  margin: 0 10px;
  color: #999;
}
```

**Атрибутные селекторы:**
```css
/* Внешние ссылки */
a[href^="http"]::after {
  content: " ↗";
  font-size: 0.8em;
}

/* Ссылки на PDF */
a[href$=".pdf"]::before {
  content: "📄 ";
}

/* Телефонные ссылки */
a[href^="tel:"] {
  color: var(--success-color);
  font-weight: 600;
}

/* Email ссылки */
a[href^="mailto:"] {
  color: var(--primary-color);
  text-decoration: underline;
}

/* Атрибуты data */
[data-status="available"] {
  color: var(--success-color);
}

[data-status="sold-out"] {
  color: var(--danger-color);
  text-decoration: line-through;
}
```

**Псевдоэлементы ::before и ::after:**
```css
/* Декоративные элементы */
.section-title::before {
  content: "";
  display: block;
  width: 60px;
  height: 4px;
  background: var(--primary-color);
  margin-bottom: 15px;
}

/* Иконки без изображений */
.location::before {
  content: "📍";
  margin-right: 8px;
}

.price::before {
  content: "AED ";
  font-weight: normal;
  opacity: 0.7;
}

/* Декоративная рамка */
.featured-tour {
  position: relative;
}

.featured-tour::after {
  content: "Популярно";
  position: absolute;
  top: 10px;
  right: 10px;
  background: var(--secondary-color);
  color: white;
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

/* Clearfix хак */
.clearfix::after {
  content: "";
  display: table;
  clear: both;
}
```

**Комбинированные селекторы:**
```css
/* Все параграфы внутри .content кроме первого */
.content p:not(:first-child) {
  margin-top: 15px;
}

/* Последний элемент определенного типа */
.tour-features li:last-of-type {
  margin-bottom: 0;
}

/* Hover на родителе меняет дочерний элемент */
.card:hover .card-title {
  color: var(--primary-color);
}

/* Соседние элементы */
h2 + p {
  font-size: 1.1em;
  color: var(--text-light);
}

/* Все следующие элементы */
.active ~ .tab-content {
  display: block;
}
```

---

## Полезные комбинации для туристических сайтов

**Адаптивная галерея с hover эффектами:**
```css
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.gallery-item {
  position: relative;
  overflow: hidden;
  border-radius: var(--border-radius-md);
  aspect-ratio: 4/3;
}

.gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.gallery-item:hover img {
  transform: scale(1.15);
}

.gallery-item::after {
  content: attr(data-caption);
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0,0,0,0.8));
  color: white;
  padding: 40px 20px 15px;
  transform: translateY(100%);
  transition: transform 0.3s ease;
}

.gallery-item:hover::after {
  transform: translateY(0);
}
```

**Карточка цены с анимацией:**
```css
.price-card {
  display: flex;
  flex-direction: column;
  padding: var(--spacing-lg);
  background: white;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  transition: all 0.3s ease;
}

.price-card:hover {
  border-color: var(--primary-color);
  transform: scale(1.05);
  box-shadow: var(--shadow-lg);
}

.price-card.featured {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-md);
}

.price-card.featured::before {
  content: "Лучший выбор";
  position: absolute;
  top: -15px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--primary-color);
  color: white;
  padding: 5px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}
```

