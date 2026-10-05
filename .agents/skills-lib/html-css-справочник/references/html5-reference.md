# HTML5 Reference

Полный справочник по HTML5 для создания современных туристических сайтов и landing pages.

---

## 1. Semantic HTML5 Elements

HTML5 предоставляет семантические теги, которые делают структуру страницы понятной для браузеров, поисковых систем и вспомогательных технологий.

### Основные семантические теги

**`<header>`** — Шапка сайта или секции
```html
<header>
  <nav>
    <a href="#tours">Tours</a>
    <a href="#yachts">Yachts</a>
    <a href="#cars">Cars</a>
  </nav>
</header>
```

**`<nav>`** — Навигационное меню
```html
<nav>
  <ul>
    <li><a href="#desert-safari">Desert Safari</a></li>
    <li><a href="#city-tours">City Tours</a></li>
    <li><a href="#water-sports">Water Sports</a></li>
  </ul>
</nav>
```

**`<main>`** — Основной контент страницы (один на документ)
```html
<main>
  <section id="hero">...</section>
  <section id="tours">...</section>
  <section id="booking">...</section>
</main>
```

**`<article>`** — Независимый, завершённый контент (статья, карточка тура)
```html
<article class="tour-card">
  <h2>Burj Khalifa Tour</h2>
  <p>Visit the world's tallest building...</p>
  <a href="#book">Book Now</a>
</article>
```

**`<section>`** — Тематическая группировка контента
```html
<section id="tours">
  <h2>Our Tours</h2>
  <article>Tour 1</article>
  <article>Tour 2</article>
</section>
```

**`<aside>`** — Боковая информация, связанная с основным контентом
```html
<aside class="promo">
  <h3>Special Offer!</h3>
  <p>Book 3 tours and get 20% off</p>
</aside>
```

**`<footer>`** — Подвал сайта или секции
```html
<footer>
  <p>&copy; 2026 Dubai Tours by Suhail</p>
  <address>Tecom, Barsha Heights, Dubai</address>
</footer>
```

### Преимущества семантической разметки

1. **SEO оптимизация** — поисковые системы лучше понимают структуру
2. **Accessibility** — screen readers корректно читают контент
3. **Поддержка** — код легче читать и поддерживать
4. **Стандарты** — соответствие современным веб-стандартам

### Пример структуры landing page

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dubai Tours & Excursions</title>
</head>
<body>
  <header>
    <nav>...</nav>
  </header>

  <main>
    <section id="hero">...</section>
    <section id="tours">...</section>
    <section id="booking">...</section>
  </main>

  <footer>...</footer>
</body>
</html>
```

---

## 2. Forms & Validation

HTML5 упрощает создание форм и добавляет встроенную валидацию без JavaScript.

### HTML5 Input Types

**Базовые типы:**
- `text` — обычный текст
- `email` — автоматическая валидация email
- `tel` — телефонный номер (мобильная клавиатура)
- `url` — веб-адрес с валидацией
- `password` — скрытый ввод пароля

**Числовые и временные типы:**
- `number` — числовой ввод с стрелками
- `range` — слайдер для выбора значения
- `date` — календарь для выбора даты
- `time` — выбор времени
- `datetime-local` — дата и время

**Другие типы:**
- `color` — выбор цвета
- `search` — поле поиска
- `file` — загрузка файлов

### Атрибуты валидации

**`required`** — обязательное поле
```html
<input type="text" name="name" required>
```

**`pattern`** — регулярное выражение для валидации
```html
<input type="tel" pattern="[0-9]{10}" placeholder="0501234567">
```

**`min` и `max`** — минимальное и максимальное значение
```html
<input type="number" min="1" max="10" name="guests">
<input type="date" min="2026-02-04" max="2026-12-31">
```

**`minlength` и `maxlength`** — длина текста
```html
<input type="text" minlength="3" maxlength="50" name="name">
```

**`placeholder`** — подсказка внутри поля
```html
<input type="email" placeholder="your@email.com">
```

**`autocomplete`** — автозаполнение браузера
```html
<input type="email" autocomplete="email">
<input type="tel" autocomplete="tel">
```

### Примеры форм бронирования

**Простая форма контакта:**
```html
<form action="/submit" method="POST">
  <label for="name">Your Name:</label>
  <input type="text" id="name" name="name" required minlength="2">

  <label for="email">Email:</label>
  <input type="email" id="email" name="email" required>

  <label for="phone">Phone:</label>
  <input type="tel" id="phone" name="phone" pattern="[0-9]{10}" placeholder="0501234567">

  <button type="submit">Send</button>
</form>
```

**Форма бронирования тура:**
```html
<form class="booking-form">
  <h2>Book Desert Safari</h2>

  <input type="text" name="name" required placeholder="Full Name">

  <input type="email" name="email" required placeholder="Email">

  <input type="tel" name="phone" required placeholder="Phone Number">

  <label for="tour-date">Tour Date:</label>
  <input type="date" id="tour-date" name="date" min="2026-02-04" required>

  <label for="guests">Number of Guests:</label>
  <input type="number" id="guests" name="guests" min="1" max="15" value="2" required>

  <label for="hotel">Hotel Name:</label>
  <input type="text" id="hotel" name="hotel">

  <label for="notes">Special Requests:</label>
  <textarea id="notes" name="notes" rows="4"></textarea>

  <button type="submit">Book Now</button>
</form>
```

**Калькулятор цены с range:**
```html
<form class="price-calculator">
  <label for="guests-range">Number of Guests: <span id="guests-value">2</span></label>
  <input type="range" id="guests-range" min="1" max="15" value="2"
         oninput="document.getElementById('guests-value').textContent = this.value">

  <label for="tour-type">Tour Type:</label>
  <select id="tour-type" name="tour-type">
    <option value="morning">Morning Safari - $50</option>
    <option value="evening">Evening Safari - $60</option>
    <option value="overnight">Overnight Safari - $120</option>
  </select>

  <p class="total-price">Total: <strong>$100</strong></p>
</form>
```

### CSS для стилизации форм

```css
input, select, textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #007bff;
}

input:invalid {
  border-color: #dc3545;
}

input:valid {
  border-color: #28a745;
}
```

---

## 3. HTML5 APIs

Современные браузерные API для интерактивных функций.

### Geolocation API

Определение местоположения пользователя для расчёта расстояния до офиса или достопримечательностей.

```html
<button onclick="getLocation()">Find Nearest Office</button>
<p id="location"></p>

<script>
function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition);
  } else {
    document.getElementById("location").textContent =
      "Geolocation not supported";
  }
}

function showPosition(position) {
  const lat = position.coords.latitude;
  const lon = position.coords.longitude;

  // Координаты офиса в Tecom, Dubai
  const officeLat = 25.0937;
  const officeLon = 55.1724;

  const distance = calculateDistance(lat, lon, officeLat, officeLon);
  document.getElementById("location").textContent =
    `You are ${distance.toFixed(2)} km from our office`;
}

function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // радиус Земли в км
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}
</script>
```

### LocalStorage API

Сохранение настроек калькулятора или выбранного языка.

```html
<script>
// Сохранение данных
localStorage.setItem('preferredCurrency', 'AED');
localStorage.setItem('lastTourSearch', 'Desert Safari');

// Чтение данных
const currency = localStorage.getItem('preferredCurrency'); // 'AED'

// Удаление данных
localStorage.removeItem('lastTourSearch');

// Очистка всего хранилища
localStorage.clear();

// Сохранение объектов (через JSON)
const settings = {
  language: 'en',
  currency: 'AED',
  notifications: true
};
localStorage.setItem('userSettings', JSON.stringify(settings));

// Чтение объектов
const savedSettings = JSON.parse(localStorage.getItem('userSettings'));
</script>
```

**Пример: Сохранение выбора языка**
```html
<select id="language" onchange="saveLanguage()">
  <option value="en">English</option>
  <option value="ru">Русский</option>
  <option value="ar">العربية</option>
</select>

<script>
// Загрузка сохранённого языка при загрузке страницы
window.onload = function() {
  const savedLang = localStorage.getItem('language') || 'en';
  document.getElementById('language').value = savedLang;
};

function saveLanguage() {
  const lang = document.getElementById('language').value;
  localStorage.setItem('language', lang);
  // Здесь можно добавить логику смены языка сайта
}
</script>
```

### Canvas API

Рисование интерактивных карт, графиков цен, визуализаций.

```html
<canvas id="priceChart" width="400" height="200"></canvas>

<script>
const canvas = document.getElementById('priceChart');
const ctx = canvas.getContext('2d');

// Рисование графика цен по месяцам
const prices = [50, 55, 60, 70, 80, 90, 95, 90, 80, 70, 60, 55];
const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// Фон
ctx.fillStyle = '#f8f9fa';
ctx.fillRect(0, 0, 400, 200);

// Линия графика
ctx.strokeStyle = '#007bff';
ctx.lineWidth = 2;
ctx.beginPath();

prices.forEach((price, index) => {
  const x = (index / 11) * 350 + 25;
  const y = 180 - (price / 100) * 150;

  if (index === 0) {
    ctx.moveTo(x, y);
  } else {
    ctx.lineTo(x, y);
  }
});

ctx.stroke();

// Подписи месяцев
ctx.fillStyle = '#333';
ctx.font = '10px Arial';
months.forEach((month, index) => {
  const x = (index / 11) * 350 + 20;
  ctx.fillText(month, x, 195);
});
</script>
```

---

## 4. Best Practices

### Обязательные элементы HTML5 документа

**DOCTYPE** — объявление типа документа (всегда первая строка)
```html
<!DOCTYPE html>
```

**Meta viewport** — адаптивность для мобильных устройств
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

**Lang атрибут** — язык контента для accessibility и SEO
```html
<html lang="en">
<html lang="ru">
<html lang="ar">
```

**Charset** — кодировка символов (UTF-8 для поддержки всех языков)
```html
<meta charset="UTF-8">
```

### Accessibility (Доступность)

**Alt текст для изображений** — описание для screen readers и SEO
```html
<img src="burj-khalifa.jpg" alt="Burj Khalifa at sunset in Dubai">
```

**ARIA labels** — метки для интерактивных элементов
```html
<button aria-label="Close menu">✕</button>
<nav aria-label="Main navigation">...</nav>
<input type="search" aria-label="Search tours">
```

**Keyboard navigation** — доступность через Tab
```html
<a href="#main" class="skip-link">Skip to main content</a>
```

### Правильная вложенность тегов

**Правильно:**
```html
<article>
  <h2>Tour Title</h2>
  <p>Description</p>
  <a href="#">Book</a>
</article>
```

**Неправильно:**
```html
<article>
  <h2>Tour Title
  <p>Description</h2>
  </article></p>
```

### SEO оптимизация

**Title и meta description:**
```html
<title>Dubai Tours & Excursions | Book Desert Safari, City Tours</title>
<meta name="description" content="Book best Dubai tours with Suhail:
      desert safari, city tours, yacht rentals. Official tickets,
      best prices, Russian-speaking guides.">
```

**Open Graph для социальных сетей:**
```html
<meta property="og:title" content="Dubai Tours by Suhail">
<meta property="og:description" content="Best tours in Dubai and UAE">
<meta property="og:image" content="https://example.com/dubai-tour.jpg">
<meta property="og:url" content="https://example.com">
```

### Минимальный шаблон HTML5

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Page description for SEO">
  <title>Page Title</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header>
    <nav aria-label="Main navigation">
      <!-- Navigation links -->
    </nav>
  </header>

  <main>
    <section>
      <!-- Main content -->
    </section>
  </main>

  <footer>
    <p>&copy; 2026 Your Company</p>
  </footer>

  <script src="script.js"></script>
</body>
</html>
```

---

## Полезные ссылки

- [MDN HTML5 Reference](https://developer.mozilla.org/en-US/docs/Web/HTML)
- [HTML5 Validator](https://validator.w3.org/)
- [Can I Use](https://caniuse.com/) — проверка поддержки HTML5 функций браузерами
