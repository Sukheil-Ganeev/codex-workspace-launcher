# Workflow Code Examples

Подробные примеры кода для workflow-интеграций из SKILL.md (раздел 9).

---

## Workflow 2: Прайс-лист с автообновлением — Код интеграции

```javascript
// В price-list/script.js
const CONFIG = {
  apiKey: 'AIzaSyC...',
  sheetId: '1Abc...xyz',
  range: 'Прайс!A2:F100'
};

async function fetchPrices() {
  const url = `https://sheets.googleapis.com/v4/spreadsheets/${CONFIG.sheetId}/values/${CONFIG.range}?key=${CONFIG.apiKey}`;

  const response = await fetch(url);
  const data = await response.json();

  return data.values.map(row => ({
    name: row[0],
    emirate: row[1],
    category: row[2],
    adultPrice: parseFloat(row[3]),
    childPrice: parseFloat(row[4]),
    duration: row[5]
  }));
}

async function renderPriceTable() {
  const prices = await fetchPrices();

  const tbody = document.querySelector('#price-table tbody');
  tbody.innerHTML = prices.map(tour => `
    <tr>
      <td>${tour.name}</td>
      <td>${tour.emirate}</td>
      <td>${tour.adultPrice} AED</td>
      <td>${tour.childPrice} AED</td>
      <td>${tour.duration}</td>
      <td><button onclick="book('${tour.name}')">Забронировать</button></td>
    </tr>
  `).join('');
}

// Автообновление каждые 5 минут
renderPriceTable();
setInterval(renderPriceTable, 5 * 60 * 1000);
```

---

## Workflow 3: Букинг-система — Netlify Function для webhook

```javascript
// netlify/functions/submit-booking.js
const fetch = require('node-fetch');

exports.handler = async (event) => {
  // Получаем данные из формы
  const booking = JSON.parse(event.body);

  // Форматируем сообщение для Telegram
  const message = `
🎫 *Новая заявка на бронирование*

📍 *Тур:* ${booking.tourName}
📅 *Дата:* ${booking.date}
👥 *Количество:* ${booking.adults} взрослых, ${booking.children} детей
💰 *Стоимость:* ${booking.totalPrice} AED

👤 *Контакты клиента:*
Имя: ${booking.name}
Телефон: ${booking.phone}
Email: ${booking.email}

📝 *Комментарий:*
${booking.comment || 'Нет комментария'}
  `.trim();

  // Отправка в Telegram
  const telegramUrl = `https://api.telegram.org/bot${process.env.BOT_TOKEN}/sendMessage`;

  await fetch(telegramUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: process.env.CHAT_ID,
      text: message,
      parse_mode: 'Markdown'
    })
  });

  return {
    statusCode: 200,
    body: JSON.stringify({
      success: true,
      message: 'Booking received'
    })
  };
};
```

**Environment variables (Netlify):**
```bash
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
CHAT_ID=-1001234567890
```

---

## Workflow 4: Инвойсы — HTML шаблон + Print Styles

### HTML шаблон инвойса

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Invoice #12345</title>
  <style>
    /* Стили для экрана */
    body {
      font-family: 'Inter', sans-serif;
      max-width: 800px;
      margin: 0 auto;
      padding: 2rem;
    }

    /* Стили для печати */
    @media print {
      .no-print { display: none; }
      body { margin: 0; padding: 1cm; }
      .invoice {
        width: 21cm;
        height: 29.7cm;
        page-break-after: avoid;
      }
    }
  </style>
</head>
<body>
  <div class="invoice">
    <header>
      <h1>Invoice #12345</h1>
      <p>Date: 2026-02-04</p>
    </header>

    <section class="company-info">
      <h2>From:</h2>
      <p>VIP Dubai Tours</p>
      <p>Dubai, Tecom, Barsha Heights</p>
      <p>Phone: +971 50 123 4567</p>
    </section>

    <section class="client-info">
      <h2>To:</h2>
      <p id="client-name">Client Name</p>
      <p id="client-email">client@example.com</p>
    </section>

    <table class="items">
      <thead>
        <tr>
          <th>Description</th>
          <th>Quantity</th>
          <th>Price</th>
          <th>Total</th>
        </tr>
      </thead>
      <tbody id="invoice-items">
        <!-- Динамически заполняется из JSON -->
      </tbody>
    </table>

    <div class="total">
      <strong>Total: <span id="total-amount">0</span> AED</strong>
    </div>

    <button class="no-print" onclick="window.print()">Print / Save PDF</button>
  </div>

  <script>
    // Загружаем данные инвойса из JSON
    async function loadInvoice() {
      const invoiceData = await fetch('/api/invoice/12345').then(r => r.json());

      document.getElementById('client-name').textContent = invoiceData.client.name;
      document.getElementById('client-email').textContent = invoiceData.client.email;

      const tbody = document.getElementById('invoice-items');
      tbody.innerHTML = invoiceData.items.map(item => `
        <tr>
          <td>${item.description}</td>
          <td>${item.quantity}</td>
          <td>${item.price} AED</td>
          <td>${item.quantity * item.price} AED</td>
        </tr>
      `).join('');

      document.getElementById('total-amount').textContent = invoiceData.total;
    }

    loadInvoice();
  </script>
</body>
</html>
```

### Print styles для A4 формата

```css
@media print {
  /* Убираем элементы управления */
  .no-print {
    display: none !important;
  }

  /* A4 размер */
  @page {
    size: A4;
    margin: 1cm;
  }

  /* Инвойс на всю страницу */
  .invoice {
    width: 21cm;
    height: 29.7cm;
    margin: 0;
    padding: 0;
  }

  /* Избегаем разрывов внутри блоков */
  table, section {
    page-break-inside: avoid;
  }

  /* Чёрно-белая печать */
  body {
    color: #000;
    background: #fff;
  }
}
```
