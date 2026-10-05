# Skill Integrations Reference

Связи с существующими скиллами для полных workflows. Этот документ показывает, как html-css-справочник интегрируется с другими скиллами для создания комплексных решений.

---

## 1. Интеграция с деплой скиллами

### netlify-deployment

**Workflow деплоя статического сайта:**

1. **Создание HTML/CSS/JS**
   - Используй html-css-справочник для создания layout, стилей и интерактивности
   - Оптимизируй CSS с помощью minification
   - Подготовь assets (изображения, шрифты)

2. **Деплой на Netlify**
   - Активируй скилл netlify-deployment
   - Подключи репозиторий или используй drag-and-drop
   - Настрой build settings (если используется препроцессор)

3. **Netlify Functions для serverless**
   ```javascript
   // netlify/functions/contact.js
   exports.handler = async (event) => {
     const { name, email, message } = JSON.parse(event.body);

     // Обработка формы
     return {
       statusCode: 200,
       body: JSON.stringify({ success: true })
     };
   };
   ```

**Пример интеграции:**
```html
<!-- Форма с Netlify Functions -->
<form id="contactForm">
  <input type="text" name="name" required>
  <input type="email" name="email" required>
  <textarea name="message" required></textarea>
  <button type="submit">Отправить</button>
</form>

<script>
document.getElementById('contactForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);

  const response = await fetch('/.netlify/functions/contact', {
    method: 'POST',
    body: JSON.stringify(Object.fromEntries(formData))
  });

  const result = await response.json();
  if (result.success) alert('Сообщение отправлено!');
});
</script>
```

### vercel-деплой

**Workflow с Vercel:**

1. **Подготовка проекта**
   - HTML/CSS/JS структура
   - vercel.json для конфигурации
   - API routes для серверной логики

2. **Деплой**
   - Используй vercel-деплой скилл
   - Автоматический CI/CD через Git
   - Preview deployments для каждого PR

**Когда использовать Netlify vs Vercel:**

| Критерий | Netlify | Vercel |
|----------|---------|--------|
| **Статический сайт** | ✅ Отлично | ✅ Отлично |
| **Serverless Functions** | Node.js, Go | Node.js, Go, Python, Ruby |
| **Edge Functions** | Deno | Edge Runtime (V8) |
| **Forms** | Встроенная обработка | Требует custom solution |
| **Identity** | Встроенная auth | Требует интеграцию |
| **Next.js** | Поддержка | Оптимизирован |
| **Цена** | Более щедрый free tier | Ограничения на serverless |

**Рекомендация:**
- **Netlify**: Простые сайты с формами, туристические landing pages
- **Vercel**: Next.js проекты, сложная серверная логика

---

## 2. Интеграция с API скиллами

### api-туризм-оаэ

**Использование данных из API скилла для создания динамических страниц:**

#### Прайс-листы из Google Sheets

```html
<!-- Динамическая таблица цен -->
<div id="priceList"></div>

<script>
async function loadPrices() {
  // API из скилла api-туризм-оаэ
  const response = await fetch('https://api.example.com/prices');
  const prices = await response.json();

  const html = `
    <table class="price-table">
      <thead>
        <tr>
          <th>Экскурсия</th>
          <th>Цена</th>
          <th>Длительность</th>
        </tr>
      </thead>
      <tbody>
        ${prices.map(item => `
          <tr>
            <td>${item.name}</td>
            <td>${item.price} AED</td>
            <td>${item.duration}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;

  document.getElementById('priceList').innerHTML = html;
}

loadPrices();
</script>

<style>
.price-table {
  width: 100%;
  border-collapse: collapse;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.price-table th {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px;
  text-align: left;
}

.price-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #eee;
}

.price-table tr:hover {
  background-color: #f8f9fa;
}
</style>
```

#### Карты маршрутов

```html
<!-- Интерактивная карта экскурсий -->
<div id="tourMap"></div>

<script>
async function loadTourMap() {
  const response = await fetch('https://api.example.com/tours/routes');
  const routes = await response.json();

  // Используй Google Maps API или Mapbox
  const map = new google.maps.Map(document.getElementById('tourMap'), {
    center: { lat: 25.2048, lng: 55.2708 }, // Dubai
    zoom: 11
  });

  routes.forEach(route => {
    new google.maps.Marker({
      position: { lat: route.lat, lng: route.lng },
      map: map,
      title: route.name
    });
  });
}
</script>
```

#### Webhooks для бронирований

```html
<!-- Форма бронирования с webhook -->
<form id="bookingForm">
  <input type="text" name="name" placeholder="Имя" required>
  <input type="email" name="email" placeholder="Email" required>
  <input type="tel" name="phone" placeholder="Телефон" required>
  <select name="tour" required>
    <option value="">Выберите экскурсию</option>
    <option value="desert-safari">Desert Safari</option>
    <option value="city-tour">City Tour</option>
  </select>
  <input type="date" name="date" required>
  <button type="submit">Забронировать</button>
</form>

<script>
document.getElementById('bookingForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);

  const response = await fetch('https://api.example.com/webhook/booking', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(Object.fromEntries(formData))
  });

  if (response.ok) {
    alert('Бронирование отправлено! Мы свяжемся с вами в ближайшее время.');
    e.target.reset();
  }
});
</script>
```

---

## 3. Интеграция с контент-скиллами

### форматирование-турпродуктов

**Workflow создания каталога экскурсий:**

1. **Получить форматированный контент**
   - Активируй скилл форматирование-турпродуктов
   - Получи структурированные описания экскурсий

2. **Вставить в HTML шаблон**
   ```html
   <article class="tour-card">
     <img src="tour-image.jpg" alt="Desert Safari">
     <div class="tour-content">
       <h2>Desert Safari</h2>
       <!-- Контент из скилла форматирование-турпродуктов -->
       <div class="tour-description">
         <h3>Что включено:</h3>
         <ul>
           <li>Трансфер из отеля</li>
           <li>Катание по дюнам</li>
           <li>Ужин BBQ</li>
           <li>Шоу программа</li>
         </ul>
       </div>
       <div class="tour-price">
         <span class="price">250 AED</span>
         <button class="btn-book">Забронировать</button>
       </div>
     </div>
   </article>
   ```

3. **Стилизовать с помощью CSS**
   ```css
   .tour-card {
     background: white;
     border-radius: 12px;
     overflow: hidden;
     box-shadow: 0 4px 12px rgba(0,0,0,0.1);
     transition: transform 0.3s ease;
   }

   .tour-card:hover {
     transform: translateY(-5px);
     box-shadow: 0 8px 24px rgba(0,0,0,0.15);
   }

   .tour-card img {
     width: 100%;
     height: 240px;
     object-fit: cover;
   }

   .tour-content {
     padding: 20px;
   }

   .tour-price {
     display: flex;
     justify-content: space-between;
     align-items: center;
     margin-top: 20px;
     padding-top: 20px;
     border-top: 1px solid #eee;
   }

   .price {
     font-size: 24px;
     font-weight: bold;
     color: #667eea;
   }
   ```

### создание-карточек-каталога

**Создание полноценного каталога на сайте:**

```html
<!-- Grid layout для каталога -->
<div class="catalog-grid">
  <!-- Карточки генерируются из скилла создание-карточек-каталога -->
</div>

<style>
.catalog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

@media (max-width: 768px) {
  .catalog-grid {
    grid-template-columns: 1fr;
  }
}
</style>
```

---

## 4. Интеграция с бизнес-скиллами

### обработка-запросов-турагентов

**Создание форм для запросов с автоматической обработкой:**

```html
<form id="agentRequestForm" class="agent-form">
  <h2>Запрос для турагентов</h2>

  <input type="text" name="agency" placeholder="Название агентства" required>
  <input type="email" name="email" placeholder="Email" required>
  <textarea name="request" placeholder="Ваш запрос" rows="5" required></textarea>

  <button type="submit" class="btn-submit">Отправить запрос</button>
</form>

<script>
document.getElementById('agentRequestForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);

  // Webhook из скилла обработка-запросов-турагентов
  await fetch('https://api.example.com/webhook/agent-request', {
    method: 'POST',
    body: JSON.stringify(Object.fromEntries(formData))
  });
});
</script>
```

### генератор-инвойсов

**HTML инвойсы для печати и PDF:**

```html
<!DOCTYPE html>
<html>
<head>
  <title>Invoice</title>
  <style>
    @media print {
      .no-print { display: none; }
    }

    .invoice {
      max-width: 800px;
      margin: 0 auto;
      padding: 40px;
      font-family: Arial, sans-serif;
    }

    .invoice-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 40px;
    }

    .invoice-table {
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
    }

    .invoice-table th,
    .invoice-table td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #ddd;
    }

    .invoice-total {
      text-align: right;
      font-size: 20px;
      font-weight: bold;
      margin-top: 20px;
    }
  </style>
</head>
<body>
  <div class="invoice">
    <!-- Контент генерируется скиллом генератор-инвойсов -->
    <div class="invoice-header">
      <div class="company-info">
        <h1>VIP Dubai Tours</h1>
        <p>Tecom, Barsha Heights, Dubai</p>
      </div>
      <div class="invoice-info">
        <p><strong>Invoice #:</strong> 12345</p>
        <p><strong>Date:</strong> 2026-02-04</p>
      </div>
    </div>

    <table class="invoice-table">
      <thead>
        <tr>
          <th>Service</th>
          <th>Quantity</th>
          <th>Price</th>
          <th>Total</th>
        </tr>
      </thead>
      <tbody id="invoiceItems"></tbody>
    </table>

    <div class="invoice-total">
      Total: <span id="totalAmount"></span> AED
    </div>

    <button onclick="window.print()" class="no-print">Print / Save as PDF</button>
  </div>
</body>
</html>
```

### банковские-реквизиты

**Интеграция реквизитов на страницу оплаты:**

```html
<div class="payment-methods">
  <h3>Способы оплаты</h3>

  <div class="payment-option">
    <h4>AED (Местный счёт)</h4>
    <!-- Реквизиты из скилла банковские-реквизиты -->
    <p><strong>Bank:</strong> Emirates NBD</p>
    <p><strong>Account:</strong> XXXX-XXXX-XXXX</p>
    <p><strong>IBAN:</strong> AE07XXXXXXXXXXXX</p>
  </div>

  <div class="payment-option">
    <h4>KZT (Kaspi)</h4>
    <p><strong>Номер:</strong> +7 XXX XXX XXXX</p>
  </div>

  <div class="payment-option">
    <h4>RUB (Сбербанк)</h4>
    <p><strong>Карта:</strong> XXXX XXXX XXXX XXXX</p>
  </div>

  <div class="payment-option">
    <h4>Криптовалюта</h4>
    <p><strong>USDT (TRC20):</strong> TXxxxxxxxxxx</p>
  </div>
</div>

<style>
.payment-methods {
  max-width: 600px;
  margin: 40px auto;
  padding: 30px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.payment-option {
  padding: 15px;
  margin: 15px 0;
  border-left: 4px solid #667eea;
  background-color: #f8f9fa;
}
</style>
```

### vip-dxb-rus-telegram-bot

**Web-версии для контента бота:**

```html
<!-- Мини-приложение для Telegram Web App -->
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    body {
      margin: 0;
      padding: 20px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--tg-theme-bg-color);
      color: var(--tg-theme-text-color);
    }

    .tour-list {
      display: flex;
      flex-direction: column;
      gap: 15px;
    }

    .tour-item {
      padding: 15px;
      background: var(--tg-theme-secondary-bg-color);
      border-radius: 12px;
      cursor: pointer;
    }

    .tour-item:active {
      opacity: 0.7;
    }
  </style>
</head>
<body>
  <div class="tour-list" id="tourList"></div>

  <script>
    // Интеграция с Telegram Web App
    const tg = window.Telegram.WebApp;
    tg.expand();

    // Загрузка туров
    async function loadTours() {
      const response = await fetch('https://api.example.com/tours');
      const tours = await response.json();

      const html = tours.map(tour => `
        <div class="tour-item" onclick="selectTour(${tour.id})">
          <h3>${tour.name}</h3>
          <p>${tour.price} AED</p>
        </div>
      `).join('');

      document.getElementById('tourList').innerHTML = html;
    }

    function selectTour(id) {
      tg.sendData(JSON.stringify({ tourId: id }));
      tg.close();
    }

    loadTours();
  </script>
</body>
</html>
```

---

## Заключение

Эти интеграции показывают, как html-css-справочник работает в связке с другими скиллами для создания полноценных решений. Комбинируй скиллы для достижения максимальной эффективности.

**Следующие шаги:**
1. Изучи документацию связанных скиллов
2. Тестируй интеграции на реальных проектах
3. Документируй новые найденные паттерны интеграции
