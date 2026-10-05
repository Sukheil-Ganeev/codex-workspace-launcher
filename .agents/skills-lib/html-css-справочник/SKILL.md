---
name: html-css-справочник
description: "Use when creating web pages, landing pages, price lists, booking forms, or integrating with APIs (Google Maps/Sheets) - covers HTML5, CSS3, responsive design, animations, and JavaScript integrations"
---
# HTML & CSS Справочник для Веб-разработки

> **Назначение:** Полное руководство по созданию современных веб-страниц для туристического бизнеса. HTML5 semantic elements, CSS3 animations, JavaScript integrations, API работа.

**Версия:** 1.0
**Дата:** 2026-02-04

---

## 1. Введение и философия

### Что такое современный веб-стек

Современная веб-разработка — это не просто HTML и CSS. Это полноценный стек технологий:

**HTML5** — структура и семантика
- Semantic elements для SEO (`<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<footer>`)
- Forms с встроенной валидацией (`type="email"`, `required`, `pattern`)
- HTML5 APIs (Geolocation, Local Storage, Canvas)
- Accessibility через ARIA attributes

**CSS3** — дизайн и анимации
- Grid и Flexbox для современных layouts
- Custom properties (CSS variables) для динамического стилинга
- Animations и transitions для плавности
- Responsive design через media queries
- Transform и backdrop-filter для эффектов

**JavaScript** — интерактивность
- DOM manipulation для динамического контента
- Event handling для пользовательских действий
- Fetch API для работы с backend
- Интеграция с внешними сервисами (Google Maps, Sheets, Telegram)
- LocalStorage для сохранения данных клиента

### Почему это важно для туристического бизнеса

В туризме скорость = деньги. Клиент находит ваш сайт в Google, и у вас есть **3 секунды**, чтобы его зацепить.

**Веб-страницы решают задачи:**
- ✅ Лендинг тура → привлекает клиентов из поиска
- ✅ Прайс-лист с автообновлением → всегда актуальные цены
- ✅ Форма бронирования → заявки прямо в Telegram
- ✅ Калькулятор стоимости → клиент сам считает цену
- ✅ Карта маршрута → наглядная визуализация тура
- ✅ Галерея фотографий → показывает качество услуг
- ✅ Отзывы клиентов → повышает доверие

**Ключевые метрики:**
- **Загрузка < 3 секунды** (клиенты нетерпеливы, 53% уходят при долгой загрузке)
- **Мобильный фокус** (80% трафика с телефонов)
- **SEO оптимизация** (попадание в топ Google для "экскурсии дубай")
- **Конверсия в заявки** (чёткие CTA кнопки типа "Забронировать")

### Ключевые возможности этого скилла

**Что вы получаете:**

1. **Готовые шаблоны** (`assets/templates/`)
   - 10 HTML/CSS шаблонов для копирования
   - Лендинги, формы, калькуляторы, галереи
   - Плейсхолдеры для быстрой замены контента

2. **Рабочие примеры** (`assets/examples/`)
   - 9 полных production-ready примеров
   - Реальные кейсы туристического бизнеса
   - С комментариями и README

3. **Production скрипты** (`scripts/`)
   - 8 инструментов автоматизации
   - Валидация, минификация, деплой
   - Готовы к использованию

4. **Детальные справочники** (`references/`)
   - 7 модульных гайдов
   - HTML5, CSS3, Responsive, JS, API, Performance
   - С примерами кода

5. **Интеграции** (`references/skill-integrations.md`)
   - Связь с другими вашими скиллами
   - Готовые workflows для бизнеса
   - Netlify, Google APIs, Telegram боты

**Кому полезен:** турагентам (лендинги), владельцам бизнеса (прайсы), менеджерам (заявки), всем кто хочет создать сайт без найма разработчиков.

---

## 2. Quick Start Guide

### Три сценария для быстрого старта

Выберите ваш сценарий и следуйте инструкциям.

#### Сценарий A: Простой лендинг за 15 минут ⚡

**Задача:** Создать одностраничный лендинг тура для быстрой проверки идеи.

**Шаги:**

1. **Скопируйте шаблон:**
   ```bash
   cp assets/templates/landing-page.html my-tour.html
   cp assets/templates/base-styles.css my-styles.css
   ```

2. **Замените плейсхолдеры в HTML:**
   ```html
   <!-- Было: -->
   <h1>[НАЗВАНИЕ ТУРА]</h1>
   <p>[ОПИСАНИЕ]</p>
   <span class="price">[ЦЕНА]</span>

   <!-- Стало: -->
   <h1>Экскурсия в Дубай: Бурдж Халифа + Дубай Молл</h1>
   <p>Полнодневная экскурсия с русскоговорящим гидом,
      включая билеты на смотровую площадку 124 этажа</p>
   <span class="price">150 AED</span>
   ```

3. **Откройте в браузере:**
   ```bash
   # Способ 1: Простое открытие
   open my-tour.html  # Mac
   start my-tour.html  # Windows

   # Способ 2: Dev server с live reload
   node scripts/dev-server.js
   # Открывается на http://localhost:8080
   ```

4. **Деплой на Netlify:**
   - Перетащите файл на https://app.netlify.com/drop
   - Получите живой URL за 30 секунд
   - Пример: `https://random-name-123.netlify.app`

**Результат:** Работающий лендинг за 15 минут.

**Смотрите полный пример:** `assets/examples/tour-landing/`

---

#### Сценарий B: Интерактивный калькулятор за 30 минут 🧮

**Задача:** Калькулятор стоимости тура с live расчётом.

**Шаги:**

1. **Скопируйте пример:**
   ```bash
   cp -r assets/examples/calculator/ my-calculator/
   cd my-calculator/
   ```

2. **Настройте цены в `prices.json`:**
   ```json
   {
     "tours": [
       {
         "id": "dubai-city",
         "name": "Дубай Сити",
         "price": 150,
         "category": "city-tour"
       },
       {
         "id": "abu-dhabi",
         "name": "Абу-Даби",
         "price": 200,
         "category": "city-tour"
       },
       {
         "id": "desert-safari",
         "name": "Сафари в пустыне",
         "price": 180,
         "category": "adventure"
       }
     ],
     "kids_discount": 0.5,
     "group_discount": {
       "10": 0.1,
       "20": 0.15,
       "30": 0.2
     }
   }
   ```

3. **Откройте `index.html` в браузере**
   - Калькулятор работает без backend
   - Сохраняет выбор в localStorage
   - Live обновление при изменении параметров

4. **Кастомизируйте дизайн в `styles.css`:**
   ```css
   :root {
     --primary-color: #ff6600;  /* Ваш бренд цвет */
     --secondary-color: #333;
     --accent-color: #00d4ff;
   }
   ```

**Функционал калькулятора:**
- Выбор тура из списка
- Количество взрослых и детей
- Автоматический расчёт скидок
- Итоговая стоимость в реальном времени
- Кнопка "Забронировать" с предзаполненными данными

**Результат:** Интерактивный калькулятор за 30 минут.

**Документация:** `assets/examples/calculator/README.md`

---

#### Сценарий C: Интеграция с Google Sheets API за 1 час 📊

**Задача:** Прайс-лист с автообновлением из Google Sheets.

**Шаги:**

1. **Скопируйте пример:**
   ```bash
   cp -r assets/examples/price-list/ my-price-list/
   cd my-price-list/
   ```

2. **Создайте Google Sheet с прайсом:**
   - Откройте https://sheets.google.com
   - Создайте таблицу со структурой:

   | Tour Name | Emirate | Category | Adult Price | Child Price | Duration |
   |-----------|---------|----------|-------------|-------------|----------|
   | Dubai City Tour | Dubai | City Tour | 150 | 75 | Half Day |
   | Abu Dhabi Tour | Abu Dhabi | City Tour | 200 | 100 | Full Day |
   | Desert Safari | Dubai | Adventure | 180 | 90 | Evening |

   - **Сделайте публичным:** File → Share → Anyone with link can view

3. **Получите API key:** Google Cloud Console -> Create credentials -> API key. Enable Google Sheets API.

4. **Настройте config:** Скопируйте `config.example.js` -> `config.js`, укажите `apiKey`, `sheetId` (из URL таблицы), `range` и `updateInterval`.

5. **Запустите:** `node ../scripts/dev-server.js` -> http://localhost:8080

6. **Деплой:** `node ../scripts/deploy-helper.js --platform netlify`

**Результат:** Прайс-лист обновляется каждые 5 минут автоматически из Google Sheets.

**Преимущества:**
- ✅ Менеджеры обновляют цены в знакомой Google Sheets
- ✅ Сайт всегда показывает актуальные данные
- ✅ Нет необходимости редактировать код
- ✅ История изменений в Google Sheets

**Детали интеграции:** `references/api-integrations.md`

**Связь с другим скиллом:** `api-туризм-оаэ`

---

## 3. Навигация по модулям

Этот скилл разделён на модули для быстрого доступа к нужной информации.

### References (справочники)

| Модуль | Когда читать | Ключевые темы | Размер |
|--------|--------------|---------------|--------|
| **html5-reference.md** | Создаёте структуру страницы | Semantic HTML, Forms, Accessibility, HTML5 APIs | ~800 слов |
| **css3-reference.md** | Оформляете дизайн | Grid, Flexbox, Animations, Custom Properties, Transform | ~1000 слов |
| **responsive-design.md** | Адаптируете под мобильные | Media queries, Mobile-first, Touch-friendly UI | ~600 слов |
| **javascript-integration.md** | Добавляете интерактивность | DOM, Events, Fetch API, Form Validation | ~700 слов |
| **api-integrations.md** | Интегрируете внешние сервисы | Google Maps, Sheets API, Webhooks, Telegram | ~800 слов |
| **performance-optimization.md** | Оптимизируете для production | Minify, Cache, Images, Core Web Vitals, Lighthouse | ~600 слов |
| **skill-integrations.md** | Связываете с другими скиллами | Workflows, netlify-deployment, api-туризм-оаэ | ~1000 слов |
| **workflow-code-examples.md** | Код для workflows | Прайс-лист API, Booking webhook, Invoice HTML | ~600 слов |
| **common-mistakes.md** | Подробные примеры ошибок 7-10 | Grid/Flexbox, console.log, Loading, Performance | ~400 слов |

### Как пользоваться этим справочником

**Последовательность для новичка:**
1. Прочитайте **Quick Start Guide** (раздел 2) → выберите сценарий
2. Начните с готового примера из `assets/examples/`
3. При возникновении вопроса → откройте нужный reference
4. Кастомизируйте через `assets/templates/`
5. Автоматизируйте через `scripts/`

**Последовательность для опытного:**
1. Откройте нужный reference напрямую
2. Скопируйте нужный паттерн из examples
3. Запустите нужный скрипт из scripts/
4. Интегрируйте с другими скиллами через workflows

**Система поиска:**
- **По задаче:** "Нужна форма" → `contact-form.html` template → `javascript-integration.md` для валидации
- **По технологии:** "Использую Grid" → `css3-reference.md` → секция Grid
- **По проблеме:** "Медленно грузится" → `performance-optimization.md` → секция Images

---

## 4. Templates & Examples

### Templates (assets/templates/) — Шаблоны для копирования

**10 готовых шаблонов:**

| Файл | Назначение | Когда использовать | Размер |
|------|------------|-------------------|--------|
| `landing-page.html` | Базовый лендинг | Одностраничный сайт тура | ~200 строк |
| `tour-card.html` | Карточка тура | Сетка предложений на главной | ~80 строк |
| `contact-form.html` | Контактная форма | Сбор заявок клиентов | ~150 строк |
| `price-calculator.html` | Калькулятор | Live расчёт стоимости | ~250 строк |
| `booking-form.html` | Форма бронирования | Выбор дат, количества людей | ~300 строк |
| `gallery.html` | Галерея изображений | Фотографии тура с lightbox | ~120 строк |
| `google-maps-integration.html` | Карта маршрута | Визуализация точек тура | ~180 строк |
| `sheets-api-integration.html` | Прайс с API | Автообновление цен из Google Sheets | ~220 строк |
| `base-styles.css` | Базовые стили | CSS variables, reset, typography | ~400 строк |
| `responsive-grid.css` | Адаптивная сетка | Grid layout для любых блоков | ~200 строк |

**Все шаблоны содержат:**
- ✅ Плейсхолдеры `[ТЕКСТ]` для быстрой замены
- ✅ Подробные комментарии с инструкциями
- ✅ HTML5 semantic structure
- ✅ CSS variables для кастомизации цветов/шрифтов
- ✅ Responsive design из коробки (mobile-first)
- ✅ Accessibility (ARIA labels, semantic elements)

**Как использовать шаблоны:**
```bash
# 1. Скопируйте нужный шаблон
cp assets/templates/landing-page.html my-page.html

# 2. Замените плейсхолдеры (найдите все [ТЕКСТ])
# В VS Code: Ctrl+H → Find: \[.*?\] → Replace all

# 3. Свяжите со стилями
<link rel="stylesheet" href="assets/templates/base-styles.css">

# 4. Кастомизируйте CSS variables
:root {
  --primary-color: #ff6600;  /* Ваш бренд */
  --font-main: 'Inter', sans-serif;
}
```

---

### Examples (assets/examples/) — Полные рабочие примеры

**9 production-ready примеров:**

| Пример | Описание | Технологии | README | Строк кода |
|--------|----------|------------|--------|-----------|
| **tour-landing/** | Лендинг "Экскурсия в Абу-Даби" | HTML, CSS, JS, Smooth scroll | ✅ | ~500 |
| **price-list/** | Прайс-лист с Google Sheets API | HTML, CSS, JS, Fetch API | ✅ | ~600 |
| **booking-system/** | Multi-step форма бронирования | HTML, CSS, JS, Webhook | ✅ | ~800 |
| **tour-cards/** | Сетка карточек с фильтрами | HTML, CSS, JS, JSON data | ✅ | ~450 |
| **gallery/** | Lightbox галерея | HTML, CSS, JS, Lazy load | ✅ | ~400 |
| **calculator/** | Калькулятор стоимости | HTML, CSS, JS, LocalStorage | ✅ | ~550 |
| **maps-route/** | Маршрут с Google Maps | HTML, CSS, JS, Maps API | ✅ | ~650 |
| **contact-form/** | Форма с Netlify Function | HTML, CSS, JS, Serverless | ✅ | ~350 |
| **integrated-workflow/** | Полная интеграция всех скиллов | HTML, CSS, JS, API, Netlify | ✅ | ~1200 |

**Каждый пример содержит:**
- ✅ Реальный контент (не Lorem Ipsum)
- ✅ Готовый к запуску код (открыть и работает)
- ✅ README с инструкциями
- ✅ Комментарии в коде на русском
- ✅ Структура файлов: `index.html`, `styles.css`, `script.js`
- ✅ Конфигурация (где нужно API keys)

**Структура примера:**
```
tour-landing/
├── index.html          # Главная страница
├── styles.css          # Стили
├── script.js           # Интерактивность
├── images/             # Изображения (если есть)
│   ├── hero.jpg
│   └── gallery/
├── config.example.js   # Пример конфигурации (для API)
└── README.md           # Инструкции
```

**Как запустить пример:**
```bash
# 1. Перейдите в папку
cd assets/examples/tour-landing/

# 2. Откройте в браузере
open index.html

# ИЛИ запустите dev server
node ../../scripts/dev-server.js

# 3. Для примеров с API - настройте config
cp config.example.js config.js
# Отредактируйте API keys в config.js
```

---

## 5. Scripts & Automation

### Production-ready инструменты (scripts/)

**8 скриптов для полного цикла разработки:**

#### 1. validate.js — Валидация кода (~300 строк)

```bash
# Валидация всех файлов в папке
node scripts/validate.js src/

# Валидация конкретного HTML
node scripts/validate.js --html index.html

# Строгая валидация CSS
node scripts/validate.js --css styles.css --strict

# Валидация доступности
node scripts/validate.js --a11y index.html
```

**Проверяет:**
- ✅ **HTML:** DOCTYPE, meta viewport, semantic tags, alt текст, heading hierarchy
- ✅ **CSS:** синтаксис, vendor prefixes, unused rules, !important usage
- ✅ **JS:** ESLint правила, console.log в production, var вместо let/const
- ✅ **Accessibility:** ARIA labels, contrast ratios, keyboard navigation
- ✅ **Performance:** image sizes > 1MB, CSS/JS file sizes, blocking scripts

**Вывод:**
```
✅ HTML valid (15 elements checked)
⚠️  CSS warning: Missing vendor prefix for 'appearance' (line 45)
❌ JS error: console.log found in production code (line 120)
⚠️  A11y warning: Image missing alt text (line 67)
❌ Performance: Image too large - hero.jpg (2.5 MB > 1 MB limit)

Summary: 2 errors, 2 warnings, 1 passed
```

---

#### 2. minify.js — Минификация (~200 строк)

```bash
# Минификация всей папки
node scripts/minify.js --input src/ --output dist/

# Минификация конкретного CSS
node scripts/minify.js --css styles.css --output styles.min.css

# Минификация JS с source maps
node scripts/minify.js --js script.js --output script.min.js --sourcemap
```

**Результаты минификации:**
- CSS: 45 KB → 12 KB (73% reduction)
- JS: 120 KB → 38 KB (68% reduction)
- HTML: 20 KB → 15 KB (25% reduction)

**Что делает:**
- Удаляет пробелы, переносы строк, комментарии
- Сокращает имена переменных (в JS)
- Объединяет CSS правила
- Удаляет неиспользуемый CSS

---

#### 3. template-gen.js — Генератор страниц (~400 строк)

```bash
node scripts/template-gen.js

# Интерактивный prompt:
? Choose template: Landing Page
? Tour name: Экскурсия в Дубай
? Price: 150 AED
? Description: Полнодневная экскурсия...
? Include booking form? Yes
? Include Google Maps? Yes

✅ Generated: output/dubai-tour/
   ├── index.html
   ├── styles.css
   └── script.js
```

**Импортирует данные из:**
- `создание-карточек-каталога` (структура туров)
- `uae-tourism-calculator` (цены и скидки)
- `форматирование-турпродуктов` (описания)

**Возможности:**
- Генерация на основе JSON данных
- Множественная генерация (batch mode)
- Кастомные шаблоны

---

#### 4. dev-server.js — Dev режим (~250 строк)

```bash
node scripts/dev-server.js

# Опции:
node scripts/dev-server.js --port 3000
node scripts/dev-server.js --https  # Для geolocation API
node scripts/dev-server.js --proxy https://api.example.com  # CORS proxy
```

**Запускается на:**
```
🚀 Dev server running at:
   Local:   http://localhost:8080
   Network: http://192.168.1.10:8080
```

**Возможности:**
- ✅ Live reload при изменениях файлов
- ✅ CORS proxy для API запросов
- ✅ HTTPS для geolocation/camera APIs
- ✅ Автооткрытие браузера
- ✅ Error overlay для быстрого дебага

---

#### 5. build.js — Production build (~500 строк)

```bash
# Production build со всеми оптимизациями
node scripts/build.js --env production

# Development build (без минификации)
node scripts/build.js --env development

# Build с анализом bundle size
node scripts/build.js --analyze
```

**Выполняет последовательно:**
1. ✅ SASS → CSS компиляция
2. ✅ Autoprefixer (vendor prefixes)
3. ✅ CSS минификация
4. ✅ JS транспиляция (Babel)
5. ✅ JS минификация (Terser)
6. ✅ HTML минификация
7. ✅ Image optimization
8. ✅ Bundling (объединение файлов)

**Результат:**
```
dist/
├── index.html          # Минифицирован
├── styles.min.css      # 12 KB (было 45 KB)
├── script.min.js       # 38 KB (было 120 KB)
└── assets/
    └── images/         # Оптимизированы
```

---

#### 6. autoprefixer.js — Vendor prefixes (~150 строк)

```bash
node scripts/autoprefixer.js styles.css
```

**Преобразует:**
```css
/* Входной CSS */
.element {
  display: flex;
  user-select: none;
}

/* Выходной CSS */
.element {
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-user-select: none;
     -moz-user-select: none;
      -ms-user-select: none;
          user-select: none;
}
```

---

#### 7. image-optimizer.js — Сжатие изображений (~350 строк)

```bash
# Оптимизация всех изображений в папке
node scripts/image-optimizer.js images/

# С конверсией в WebP
node scripts/image-optimizer.js images/ --webp

# Указать качество
node scripts/image-optimizer.js images/ --quality 80
```

**Результаты:**
- JPEG: 5 MB → 800 KB (84% reduction)
- PNG: 2 MB → 400 KB (80% reduction)
- Генерация WebP: дополнительно -30% размера

**Создаёт структуру:**
```
images/
├── hero.jpg              # Оригинал 5 MB
├── hero-optimized.jpg    # 800 KB
└── hero.webp             # 560 KB
```

---

#### 8. deploy-helper.js — Деплой на Netlify/Vercel (~400 строк)

```bash
# Деплой на Netlify
node scripts/deploy-helper.js --platform netlify

# Деплой на Vercel
node scripts/deploy-helper.js --platform vercel

# С автоматическим build
node scripts/deploy-helper.js --platform netlify --build
```

**Выполняет:**
1. Production build
2. Валидация файлов
3. Создание `netlify.toml` / `vercel.json`
4. Push в Git
5. Деплой через CLI

**Интеграция со скиллом:** `netlify-deployment`

---

**Полная документация всех скриптов:** `scripts/README.md`

**Установка зависимостей:**
```bash
cd scripts/
npm install
```

---

## 6. Типичные ошибки

### Топ-10 ошибок при создании веб-страниц

#### Ошибка 1: Забыли viewport meta tag

**Проблема:**
```html
<head>
  <meta charset="UTF-8">
  <title>Мой сайт</title>
  <!-- Забыли viewport! -->
</head>
```

**Симптом:** Сайт не responsive, мелкий текст на мобильных, пользователи зумят.

**Решение:**
```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Мой сайт</title>
</head>
```

**Почему критично:** Без viewport браузер рендерит как desktop (980px ширина), игнорируя media queries.

---

#### Ошибка 2: Inline styles вместо классов

**Проблема:**
```html
<div style="color: red; font-size: 20px; margin: 10px;">Тур №1</div>
<div style="color: red; font-size: 20px; margin: 10px;">Тур №2</div>
<div style="color: red; font-size: 20px; margin: 10px;">Тур №3</div>
<!-- Повторение стилей 50 раз! -->
```

**Решение:**
```html
<div class="tour-item">Тур №1</div>
<div class="tour-item">Тур №2</div>
<div class="tour-item">Тур №3</div>

<style>
.tour-item {
  color: red;
  font-size: 20px;
  margin: 10px;
}
</style>
```

**Почему:** Переиспользование, легче менять (одно место вместо 50), меньше кода.

---

#### Ошибка 3: Нет alt текста у изображений

**Проблема:**
```html
<img src="tour.jpg">
<img src="hotel.jpg">
```

**Решение:**
```html
<img src="tour.jpg" alt="Экскурсия в Абу-Даби с посещением мечети шейха Зайда">
<img src="hotel.jpg" alt="Номер люкс в отеле Burj Al Arab с видом на море">
```

**Почему критично:**
- **SEO:** Google индексирует alt текст
- **Accessibility:** Screen readers читают для слабовидящих
- **Fallback:** Если изображение не загрузилось, показывается alt текст

---

#### Ошибка 4: CORS ошибки при API запросах

**Проблема:**
```javascript
// В консоли браузера:
Access to fetch at 'https://sheets.googleapis.com/...' from origin
'http://localhost:8080' has been blocked by CORS policy
```

**Причина:** Запрос с localhost на внешний API без правильных заголовков.

**Решение 1 - API key (для Google APIs):**
```javascript
const url = `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}?key=${apiKey}`;
fetch(url)
  .then(res => res.json())
  .then(data => console.log(data));
```

**Решение 2 - CORS proxy через Netlify Functions:**
```javascript
// netlify/functions/proxy.js
exports.handler = async (event) => {
  const response = await fetch(EXTERNAL_API_URL);
  return {
    statusCode: 200,
    body: JSON.stringify(await response.json())
  };
};
```

**Детали:** `references/api-integrations.md`

---

#### Ошибка 5: Не тестировали на мобильных

**Проблема:** Сайт отлично выглядит на desktop, сломан на телефоне.

**Почему происходит:**
- Кнопки слишком маленькие (< 44x44px)
- Текст нечитаемый (< 16px)
- Элементы наезжают друг на друга
- Горизонтальный скролл

**Решение:**
```bash
# Chrome DevTools
# 1. Откройте сайт
# 2. Нажмите Ctrl+Shift+M (Toggle device toolbar)
# 3. Выберите iPhone 12 Pro / Galaxy S21
# 4. Тестируйте все страницы
```

**Mobile-first подход:**
```css
/* Сначала стили для мобильных */
.tour-card {
  width: 100%;
  padding: 1rem;
}

/* Затем адаптация для desktop */
@media (min-width: 768px) {
  .tour-card {
    width: 50%;
    padding: 2rem;
  }
}
```

**Гайд:** `references/responsive-design.md`

---

#### Ошибка 6: Большие изображения без оптимизации

**Проблема:**
- Загружаете 5 MB JPEG с камеры телефона
- Сайт грузится 10 секунд на 3G
- Клиент уходит

**Решение:**
```bash
# Автоматическая оптимизация
node scripts/image-optimizer.js images/

# Результат:
# hero.jpg: 5 MB → 800 KB (84% reduction)
# + hero.webp: 560 KB (WebP формат)
```

**В HTML используйте современный формат:**
```html
<picture>
  <source srcset="hero.webp" type="image/webp">
  <img src="hero.jpg" alt="Дубай" loading="lazy">
</picture>
```

**Lazy loading:** атрибут `loading="lazy"` загружает изображения только при прокрутке к ним.

---

#### Ошибки 7-10: Grid/Flexbox, console.log, Loading states, Performance

**Ошибка 7:** Layouts через `float` вместо Grid/Flexbox. Используйте `display: flex` для одномерных и `display: grid` для двумерных layouts.

**Ошибка 8:** console.log в production. Используйте `validate.js --js` для автоматической проверки или обёртку с флагом DEBUG.

**Ошибка 9:** Нет loading состояний у кнопок. Добавляйте `disabled`, текст "Отправка..." и CSS-анимацию спиннера при отправке форм.

**Ошибка 10:** Игнорирование Performance. Lighthouse audit в Chrome DevTools, цель: score > 90.

**Подробные примеры кода для ошибок 7-10:** `references/common-mistakes.md`

---

## 7. Best Practices для туризма

### 4 правила успешного туристического сайта

#### 1. Быстрая загрузка (< 3 секунды)

**Почему критично:**
- 53% пользователей покидают сайт, если он грузится > 3 секунд
- Google ранжирует быстрые сайты выше в результатах поиска
- Мобильный 3G интернет медленный (типичная скорость туристов в роуминге)

**Как достичь:**

✅ **Оптимизируйте изображения:**
```bash
node scripts/image-optimizer.js images/ --webp --quality 80
```

✅ **Минифицируйте CSS/JS:**
```bash
node scripts/minify.js --input src/ --output dist/
```

✅ **Используйте CDN:** Netlify/Vercel автоматически раздают файлы через CDN

✅ **Lazy load для изображений:**
```html
<img src="tour.jpg" alt="Тур" loading="lazy">
```

✅ **Проверяйте Lighthouse score:**
- Chrome DevTools → Lighthouse
- Цель: Performance > 90

**Инструменты:**
- https://pagespeed.web.dev/ (Google PageSpeed Insights)
- https://www.webpagetest.org/ (детальный анализ)

---

#### 2. Мобильный фокус (80% трафика)

**Mobile-first подход:**
1. Дизайн **сначала** для телефонов (самый сложный случай)
2. **Затем** адаптация для планшетов
3. **Затем** адаптация для desktop

**Ключевые требования:**

✅ **Viewport meta tag:**
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

✅ **Touch-friendly кнопки (min 44x44px):**
```css
.cta-button {
  min-width: 44px;
  min-height: 44px;
  padding: 1rem 2rem; /* Комфортно для пальца */
}
```

✅ **Readable текст (min 16px):**
```css
body {
  font-size: 16px; /* Не мельче! */
  line-height: 1.6;
}
```

✅ **Swipeable галереи:**
```html
<!-- Используйте Swiper.js для touch-friendly слайдера -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css">
<script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
```

**Тестирование:**
- Chrome DevTools (Ctrl+Shift+M) → выберите iPhone/Android
- Реальные устройства (попросите друзей протестировать)
- BrowserStack для тестирования на разных устройствах

**Статистика по устройствам туристов:**
- 📱 Мобильные: 80% трафика
- 💻 Desktop: 15% трафика
- 📱 Планшеты: 5% трафика

**Гайд:** `references/responsive-design.md`

---

#### 3. Чёткие CTA (Call-to-Action)

**Принцип:** Пользователь должен понять **что делать** за 3 секунды.

**Хорошие CTA:**
- ✅ **"Забронировать тур"** (конкретное действие)
- ✅ **"Рассчитать стоимость"** (понятная выгода)
- ✅ **"Связаться в WhatsApp"** (удобный канал)
- ✅ **"Узнать расписание"** (чёткая цель)

**Плохие CTA:**
- ❌ **"Узнать больше"** (слишком абстрактно)
- ❌ **"Кликните здесь"** (не понятно зачем)
- ❌ **"Далее"** (куда далее?)
- ❌ **"Подробнее"** (о чём?)

**Дизайн кнопок:**
```css
.cta-button {
  /* Контрастный яркий цвет */
  background: #ff6600;
  color: white;

  /* Крупный текст */
  font-size: 1.2rem;
  font-weight: 600;

  /* Достаточный padding */
  padding: 1rem 2rem;

  /* Rounded corners (современно) */
  border-radius: 8px;

  /* Тень для глубины */
  box-shadow: 0 4px 12px rgba(255, 102, 0, 0.3);

  /* Плавный hover */
  transition: transform 0.2s, box-shadow 0.2s;
}

.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 102, 0, 0.4);
}
```

**Размещение CTA:**
- Above the fold (видно без прокрутки)
- После каждого значимого блока
- В конце страницы (для тех, кто дочитал)

**Пример структуры лендинга:**
```html
<section class="hero">
  <h1>Экскурсия в Абу-Даби</h1>
  <p>Однодневный тур с посещением мечети шейха Зайда</p>
  <a href="#booking" class="cta-button">Забронировать за 200 AED</a>
</section>

<section class="features">
  <!-- Преимущества тура -->
  <a href="#booking" class="cta-button">Рассчитать стоимость</a>
</section>

<section class="reviews">
  <!-- Отзывы клиентов -->
  <a href="https://wa.me/971..." class="cta-button">Связаться в WhatsApp</a>
</section>
```

---

#### 4. Доверие (отзывы, сертификаты, контакты)

**Проблема:** Турист в интернете не видит вас лично. Как вызвать доверие?

**Элементы доверия:**

✅ **Реальные фото туров (не стоки)**
```html
<!-- Плохо: стоковое фото -->
<img src="shutterstock-dubai-generic.jpg">

<!-- Хорошо: реальное фото вашего тура -->
<img src="our-tour-group-at-burj-khalifa.jpg"
     alt="Наша группа на 124 этаже Бурдж Халифа, 15 января 2026">
```

✅ **Отзывы клиентов с именами и фото**
```html
<div class="review">
  <img src="client-anna.jpg" alt="Анна">
  <blockquote>
    "Отличная экскурсия! Гид Сухейль очень интересно рассказывал
    про историю Дубая. Рекомендую!"
  </blockquote>
  <cite>Анна, Москва • Январь 2026</cite>
  <div class="rating">⭐⭐⭐⭐⭐</div>
</div>
```

✅ **Сертификаты и лицензии**
```html
<section class="trust">
  <h2>Мы — лицензированный туроператор</h2>
  <div class="certificates">
    <img src="license-dtcm.jpg" alt="Лицензия DTCM Дубай">
    <img src="certificate-tourism-uae.jpg" alt="Сертификат Ministry of Tourism UAE">
  </div>
</section>
```

✅ **Видимые контакты (WhatsApp, телефон, офис)**
```html
<section class="contacts">
  <h2>Свяжитесь с нами</h2>

  <div class="contact-item">
    <i class="fab fa-whatsapp"></i>
    <a href="https://wa.me/971501234567">+971 50 123 4567</a>
  </div>

  <div class="contact-item">
    <i class="fas fa-phone"></i>
    <a href="tel:+971501234567">+971 50 123 4567</a>
  </div>

  <div class="contact-item">
    <i class="fas fa-map-marker-alt"></i>
    <p>Офис: Dubai, Tecom (Barsha Heights),
       возле метро Dubai Internet City</p>
  </div>

  <div class="contact-item">
    <i class="fab fa-instagram"></i>
    <a href="https://instagram.com/your_tours">@your_tours</a>
    <span>5000+ подписчиков</span>
  </div>
</section>
```

✅ **Социальные proof (Instagram, отзывы Google)**
```html
<section class="social-proof">
  <h2>Нам доверяют 5000+ туристов</h2>

  <div class="stats">
    <div class="stat">
      <span class="number">5000+</span>
      <span class="label">Довольных клиентов</span>
    </div>
    <div class="stat">
      <span class="number">4.9</span>
      <span class="label">Рейтинг Google (120 отзывов)</span>
    </div>
    <div class="stat">
      <span class="number">8</span>
      <span class="label">Лет на рынке</span>
    </div>
  </div>

  <a href="https://g.page/r/..." class="google-reviews">
    Читать отзывы на Google
  </a>
</section>
```

✅ **Гарантии и политика возврата**
```html
<section class="guarantees">
  <h3>Наши гарантии</h3>
  <ul>
    <li>✅ Возврат 100% при отмене за 24 часа</li>
    <li>✅ Страховка для всех пассажиров</li>
    <li>✅ Лицензированные гиды</li>
    <li>✅ Новые комфортабельные автомобили</li>
  </ul>
</section>
```

**Полный пример блока доверия:**
```html
<section class="trust-section">
  <h2>Почему нам доверяют</h2>

  <div class="trust-grid">
    <div class="trust-item">
      <img src="icon-experience.svg" alt="">
      <h3>8 лет опыта</h3>
      <p>Работаем с 2018 года, провели более 10,000 экскурсий</p>
    </div>

    <div class="trust-item">
      <img src="icon-license.svg" alt="">
      <h3>Официальная лицензия</h3>
      <p>DTCM License №12345, Ministry of Tourism certified</p>
    </div>

    <div class="trust-item">
      <img src="icon-reviews.svg" alt="">
      <h3>4.9/5 рейтинг</h3>
      <p>120+ отзывов на Google, 5000+ на Instagram</p>
    </div>

    <div class="trust-item">
      <img src="icon-support.svg" alt="">
      <h3>24/7 поддержка</h3>
      <p>Всегда на связи в WhatsApp и по телефону</p>
    </div>
  </div>
</section>
```

---

## 8. Дополнительные ресурсы

### Полезные ссылки

**Документация:**
- [MDN Web Docs](https://developer.mozilla.org/) — Полная документация HTML/CSS/JS (лучший источник)
- [Can I Use](https://caniuse.com/) — Проверка поддержки браузерами (перед использованием новых фич)
- [CSS-Tricks](https://css-tricks.com/) — Гайды, трюки и best practices CSS
- [Web.dev](https://web.dev/) — Гайды от Google по modern web development

**Инструменты тестирования:**
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) — Аудит performance, accessibility, SEO
- [PageSpeed Insights](https://pagespeed.web.dev/) — Рекомендации оптимизации от Google
- [WebPageTest](https://www.webpagetest.org/) — Детальное тестирование скорости загрузки
- [WAVE](https://wave.webaim.org/) — Accessibility checker

**Дизайн ресурсы:**
- [Google Fonts](https://fonts.google.com/) — Бесплатные шрифты для веба
- [Font Awesome](https://fontawesome.com/) — 2000+ бесплатных иконок
- [Unsplash](https://unsplash.com/) — Бесплатные фото высокого качества (если нет своих)
- [Coolors](https://coolors.co/) — Генератор цветовых палитр

**Вдохновение:**
- [Awwwards](https://www.awwwards.com/) — Лучшие веб-дизайны
- [Dribbble](https://dribbble.com/tags/landing-page) — UI/UX вдохновение
- [Land-book](https://land-book.com/) — Коллекция лендингов

---

### Рекомендуемые VS Code Extensions

**Must-have (установите обязательно):**
- **Live Server** (`ritwickdey.LiveServer`) -- Live reload, запуск: Right-click на HTML -> Open with Live Server
- **Prettier** (`esbenp.prettier-vscode`) -- автоформатирование, настройка: Format On Save
- **HTML CSS Support** (`ecmel.vscode-html-css`) -- автодополнение классов
- **Path Intellisense** (`christian-kohler.path-intellisense`) -- автодополнение путей

**Полезные (опционально):**
- **Auto Rename Tag** (`formulahendry.auto-rename-tag`) -- автоматически меняет закрывающий тег
- **CSS Peek** (`pranaygp.vscode-css-peek`) -- быстрый просмотр CSS классов
- **IntelliSense for CSS** (`zignd.html-css-class-completion`) -- умное автодополнение CSS
- **Image preview** (`kisstkondoros.vscode-gutter-preview`) -- превью изображений в коде
- **Color Highlight** (`naumovs.color-highlight`) -- подсветка цветов в CSS

---

### CDN для быстрого старта

**Fonts (Google Fonts):** Подключить через `fonts.googleapis.com`, рекомендуемый шрифт: `Inter` (wght 400-700). Добавить `rel="preconnect"`.

**Icons (Font Awesome 6.4):** CDN `cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css`. Использование: `<i class="fas fa-phone"></i>`, `<i class="fab fa-whatsapp"></i>`.

**Библиотеки (CDN):**
- **Swiper** (touch-friendly слайдеры): `cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js`
- **AOS** (scroll animations): `unpkg.com/aos@2.3.1/dist/aos.js`
- **Lightbox2** (галереи с zoom): `cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.3/js/lightbox.min.js`

CDN удобно для прототипов; для production используйте локальные файлы.

---

## 9. Связанные скиллы и workflows

Этот справочник работает в связке с другими вашими скиллами для создания полного production workflow.

### Workflow 1: Создание лендинга тура (от идеи до production)

```
1. форматирование-турпродуктов
   ↓ (создаёте контент для WhatsApp/Telegram)
   ↓ выход: структурированное описание тура

2. html-css-справочник 👈 ВЫ ЗДЕСЬ
   ↓ (преобразуете контент в веб-страницу)
   ↓ используете: assets/examples/tour-landing/
   ↓ добавляете: contact-form, price-calculator
   ↓ выход: готовая HTML/CSS/JS страница

3. git-github-справочник
   ↓ (версионирование кода)
   ↓ git init, commit, push в репозиторий

4. netlify-deployment ИЛИ vercel-деплой
   ↓ (деплой на production)
   ↓ выход: живой URL типа https://your-tour.netlify.app

✅ Результат: Живой лендинг с формой заявок
```

**Пример команд:**
```bash
# Шаг 1: Создаём страницу из шаблона
cp -r C:/Users/londo/.claude/skills/html-css-справочник/assets/examples/tour-landing/ D:/Downloads/my-tour/
cd D:/Downloads/my-tour/

# Шаг 2: Редактируем контент
# (импортируем описание из форматирование-турпродуктов)
# Редактируем index.html, меняем [ПЛЕЙСХОЛДЕРЫ]

# Шаг 3: Git workflow
git init
git add .
git commit -m "Initial tour landing: Dubai City Tour"
git branch -M main
git remote add origin https://github.com/username/my-tour.git
git push -u origin main

# Шаг 4: Deploy
# Используем netlify-deployment скилл
# Или через CLI:
netlify deploy --prod
# Получаем URL: https://dubai-city-tour.netlify.app
```

**Время выполнения:** 1-2 часа от идеи до живого сайта.

---

### Workflow 2: Прайс-лист с автообновлением

```
1. создание-карточек-каталога
   ↓ (структурируете данные туров)
   ↓ выход: Excel/JSON с данными туров

2. html-css-справочник 👈 ВЫ ЗДЕСЬ
   ↓ используете: assets/examples/price-list/
   ↓ + assets/templates/sheets-api-integration.html
   ↓ создаёте интерфейс прайс-листа
   ↓ выход: веб-страница с прайсом

3. api-туризм-оаэ
   ↓ (настраиваете Google Sheets API)
   ↓ создаёте Google Sheet с прайсом
   ↓ выход: API endpoint для получения данных

4. netlify-deployment
   ↓ (деплой + serverless function для API)
   ↓ выход: живой прайс-лист

✅ Результат: Прайс-лист обновляется автоматически при изменении Google Sheet
```

**Ключевая идея:** Fetch API подтягивает данные из Google Sheets по API key + sheetId, рендерит таблицу и обновляет каждые 5 минут через `setInterval`.

**Полный код интеграции:** `references/workflow-code-examples.md` (секция Workflow 2)

**Время выполнения:** 2-3 часа setup, затем автоматическое обновление.

---

### Workflow 3: Букинг-система с Telegram уведомлениями

```
1. обработка-запросов-турагентов
   ↓ (понимаете структуру запроса клиента)
   ↓ выход: формат данных для бронирования

2. html-css-справочник 👈 ВЫ ЗДЕСЬ
   ↓ используете: assets/examples/booking-system/
   ↓ создаёте multi-step форму бронирования
   ↓ выход: интерактивная форма с валидацией

3. api-туризм-оаэ
   ↓ (webhook для отправки в Telegram)
   ↓ настраиваете Telegram Bot API
   ↓ выход: Netlify Function для отправки

4. vip-dxb-rus-telegram-bot
   ↓ (бот получает заявки и уведомляет агентов)
   ↓ выход: уведомления в Telegram канал

5. vercel-деплой ИЛИ netlify-deployment
   ↓ (деплой формы + serverless функций)
   ↓ выход: живая букинг-форма

✅ Результат: Заявки автоматически попадают в Telegram с полными данными
```

**Ключевая идея:** Netlify Function (`submit-booking.js`) принимает данные формы, форматирует Markdown-сообщение и отправляет через Telegram Bot API (`sendMessage`). Env vars: `BOT_TOKEN`, `CHAT_ID`.

**Полный код Netlify Function:** `references/workflow-code-examples.md` (секция Workflow 3)

**Время выполнения:** 3-4 часа setup, затем автоматическая работа.

---

### Workflow 4: Генерация и отображение инвойсов

```
1. генератор-инвойсов
   ↓ (создаёте данные инвойса: тур, цена, клиент)
   ↓ выход: JSON с данными инвойса

2. html-css-справочник 👈 ВЫ ЗДЕСЬ
   ↓ создаёте HTML-версию инвойса для веба
   ↓ используете CSS для печати (print styles)
   ↓ выход: красивый веб-инвойс

3. pdf-презентации
   ↓ (конвертация HTML → PDF для отправки клиенту)
   ↓ используете Puppeteer/Chrome headless
   ↓ выход: PDF файл инвойса

✅ Результат: Инвойс доступен онлайн + PDF версия для отправки
```

**Ключевая идея:** HTML-инвойс с `@media print` стилями для A4 формата. JS загружает данные из API и рендерит таблицу позиций. Кнопка `window.print()` для сохранения в PDF. Print styles: `@page { size: A4; margin: 1cm; }`, `page-break-inside: avoid`.

**Полный HTML шаблон + print styles:** `references/workflow-code-examples.md` (секция Workflow 4)

**Время выполнения:** 2 часа setup, затем автоматическая генерация.

---

**Подробная документация всех интеграций:** `references/skill-integrations.md`

**Связанные скиллы:**
- `netlify-deployment` — деплой сайтов
- `vercel-деплой` — альтернатива Netlify
- `api-туризм-оаэ` — работа с Google APIs
- `форматирование-турпродуктов` — создание контента
- `создание-карточек-каталога` — структурирование туров
- `генератор-инвойсов` — создание счетов
- `pdf-презентации` — конвертация в PDF
- `vip-dxb-rus-telegram-bot` — уведомления в Telegram
- `git-github-справочник` — версионирование кода

---

## Заключение

Этот справочник — ваш полный гайд по созданию современных веб-страниц для туристического бизнеса.

**Что вы теперь умеете:**
- ✅ Создавать лендинги туров за 15 минут
- ✅ Интегрировать Google Sheets API для прайсов
- ✅ Настраивать формы бронирования с Telegram уведомлениями
- ✅ Оптимизировать сайты для мобильных (80% трафика)
- ✅ Деплоить на Netlify/Vercel
- ✅ Автоматизировать через скрипты

**Следующие шаги:**
1. Выберите Quick Start сценарий (раздел 2)
2. Скопируйте нужный пример из `assets/examples/`
3. Кастомизируйте под свой бизнес
4. Деплойте на production
5. Интегрируйте с другими скиллами

**Помните:** Начинайте с простого. Лучше запустить простой лендинг сегодня, чем идеальный сайт через месяц.

**Вопросы?** Читайте детальные references в папке `references/` или смотрите рабочие примеры в `assets/examples/`.

---

**Версия:** 1.0
**Последнее обновление:** 2026-02-04
**Автор:** Сухейль, VIP Dubai Tours
**Скилл:** html-css-справочник
