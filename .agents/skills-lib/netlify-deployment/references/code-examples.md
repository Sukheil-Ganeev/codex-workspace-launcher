# Примеры кода для Netlify

> Перенесено из SKILL.md — развёрнутые примеры кода для всех бизнес-кейсов.

---

## Netlify Drop: примеры HTML

### Прайс-лист HTML

```html
<!-- index.html -->
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Экскурсии Дубай — Прайс 2026</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <h1>Экскурсии по Дубаю</h1>
  <table>
    <tr>
      <th>Название</th>
      <th>Цена (AED)</th>
    </tr>
    <tr>
      <td>Джип-сафари</td>
      <td>150</td>
    </tr>
    <tr>
      <td>Бурдж Халифа</td>
      <td>120</td>
    </tr>
  </table>
</body>
</html>
```

**Деплой:**
- Папка: `price-list/` (с `index.html` и `style.css`)
- Drop → https://dxb-tours-price.netlify.app
- Время: 30 секунд

### Защищённый dashboard

```html
<!-- dashboard.html → переименовать в index.html -->
<!DOCTYPE html>
<html lang="ru">
<head>
  <title>Dashboard — Бронирования</title>
</head>
<body>
  <h1>Сегодняшние бронирования</h1>
  <ul id="bookings"></ul>

  <script>
    // Данные загружаются из локального JSON или API
    fetch('bookings.json')
      .then(r => r.json())
      .then(data => {
        const list = document.getElementById('bookings');
        data.forEach(b => {
          list.innerHTML += `<li>${b.name} — ${b.tour} — ${b.date}</li>`;
        });
      });
  </script>
</body>
</html>
```

```json
// bookings.json
[
  {"name": "Иван", "tour": "Джип-сафари", "date": "2026-02-05"},
  {"name": "Мария", "tour": "Бурдж Халифа", "date": "2026-02-06"}
]
```

**Деплой:**
- Папка: `dashboard/` (с `index.html` и `bookings.json`)
- Drop → https://team-dashboard.netlify.app
- **Сразу:** Site Settings → Password Protection → `team2024`

### Обновление Drop сайта

**Сценарий:** Добавили новую экскурсию в прайс-лист

1. Обновили `index.html` локально:
```html
<tr>
  <td>Абу-Даби тур</td>
  <td>200</td>
</tr>
```

2. Netlify Dashboard → Deploys → "Drag and drop"
3. Перетащили папку `price-list/` снова
4. URL остался прежним: `https://dxb-tours-price.netlify.app`
5. Контент обновился за 10 секунд

### Когда использовать Drop: полный список сценариев

**Идеальные сценарии:**

1. **Срочное демо клиенту** — за 2 минуты: обновили дизайн → Drop → отправили URL
2. **Тестирование на реальных устройствах** — проверить адаптивность на iPhone (localhost не открыть на телефоне)
3. **Одноразовые лендинги** — акция на экскурсию на 3 дня, потом можно удалить
4. **Internal tools без чувствительных данных** — калькулятор комиссий, инструкция для гидов, расписание экскурсий

**С password protection:**
5. **Internal dashboards** — сводка бронирований, финансовый отчёт, admin панель

**НЕ использовать Drop для:**
1. Production сайтов (если обновляете регулярно → GitHub Integration)
2. Проектов с build процессом (React, Vue — используйте GitHub/CLI)
3. Сайтов с Serverless Functions (Drop не поддерживает)
4. Когда нужна история деплоев (Drop не хранит предыдущие версии)

---

## React прайс-лист (GitHub Integration)

### Шаг 1: Создайте React проект

```bash
cd /d/Downloads
npx create-react-app price-list
cd price-list
```

### Шаг 2: Добавьте код прайс-листа

```javascript
// src/App.js
import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [prices, setPrices] = useState([]);

  useEffect(() => {
    // В production: fetch из Google Sheets API
    // Сейчас: mock data
    setPrices([
      { name: 'Джип-сафари', price: 150 },
      { name: 'Бурдж Халифа', price: 120 },
      { name: 'Абу-Даби тур', price: 200 },
    ]);
  }, []);

  return (
    <div className="App">
      <h1>Экскурсии по Дубаю</h1>
      <table>
        <thead>
          <tr>
            <th>Название</th>
            <th>Цена (AED)</th>
          </tr>
        </thead>
        <tbody>
          {prices.map((item, i) => (
            <tr key={i}>
              <td>{item.name}</td>
              <td>{item.price}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
```

### Шаг 3-6: Тест и деплой

```bash
# Тест локально
npm start

# Push в GitHub
git add .
git commit -m "Initial price list"
gh repo create price-list --public --source=. --push

# Обновление цен
nano src/App.js  # 150 → 160
git add .
git commit -m "Update safari price"
git push
# Netlify автоматически rebuild через минуту
```

**Build settings для Netlify:** Build command: `npm run build`, Publish directory: `build`

---

## Serverless Functions

### Telegram Webhook обработка

```javascript
// netlify/functions/telegram-webhook.js
exports.handler = async (event, context) => {
  // Telegram отправляет POST запрос
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  // Parse тело запроса
  const body = JSON.parse(event.body);
  const message = body.message;

  console.log('New message:', message.text);
  console.log('From:', message.from.username);

  // Обработка команд
  if (message.text === '/start') {
    await sendTelegramMessage(message.chat.id, 'Добро пожаловать!');
  }

  return {
    statusCode: 200,
    body: JSON.stringify({ ok: true }),
  };
};

async function sendTelegramMessage(chatId, text) {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const url = `https://api.telegram.org/bot${token}/sendMessage`;

  await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: chatId, text: text }),
  });
}
```

**Настройка Telegram webhook:**

```bash
curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
  -d url=https://your-site.netlify.app/.netlify/functions/telegram-webhook
```

### Google Sheets API интеграция

```javascript
// netlify/functions/fetch-prices.js
const fetch = require('node-fetch');

exports.handler = async (event, context) => {
  const apiKey = process.env.GOOGLE_SHEETS_API_KEY;
  const spreadsheetId = process.env.SPREADSHEET_ID;
  const range = 'Prices!A2:C'; // Столбцы: Name, Price AED, Price USD

  const url = `https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}/values/${range}?key=${apiKey}`;

  try {
    const response = await fetch(url);
    const data = await response.json();

    if (!data.values) {
      return {
        statusCode: 404,
        body: JSON.stringify({ error: 'No data found' }),
      };
    }

    const prices = data.values.map(row => ({
      name: row[0],
      priceAED: parseFloat(row[1]),
      priceUSD: parseFloat(row[2]),
    }));

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=21600', // 6 часов cache
      },
      body: JSON.stringify(prices),
    };
  } catch (error) {
    console.error('Error fetching Google Sheets:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal Server Error' }),
    };
  }
};
```

**Scheduled обновление:**
- Netlify не поддерживает scheduled functions из коробки
- Используйте **Cron-job.org** (бесплатный сервис): GET каждые 6 часов
- Или **Build Hook**: Site Settings → Build hooks → Cron-job.org вызывает hook → rebuild

### Форма заявки на экскурсию (Function)

```javascript
// netlify/functions/submit-booking.js
const fetch = require('node-fetch');

exports.handler = async (event, context) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  const data = JSON.parse(event.body);
  const { name, phone, tour, date } = data;

  // Валидация
  if (!name || !phone || !tour) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Missing required fields' }),
    };
  }

  // Отправить в Telegram
  const chatId = process.env.TELEGRAM_CHAT_ID;
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const message = `
Новая заявка!

Имя: ${name}
Телефон: ${phone}
Экскурсия: ${tour}
Дата: ${date || 'Не указана'}
  `.trim();

  const telegramUrl = `https://api.telegram.org/bot${token}/sendMessage`;
  await fetch(telegramUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: chatId,
      text: message,
    }),
  });

  return {
    statusCode: 200,
    body: JSON.stringify({ success: true, message: 'Заявка принята' }),
  };
};
```

**Frontend вызов:**

```javascript
// script.js
document.getElementById('booking-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const formData = {
    name: e.target.name.value,
    phone: e.target.phone.value,
    tour: e.target.tour.value,
    date: e.target.date.value,
  };

  const response = await fetch('/.netlify/functions/submit-booking', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData),
  });

  if (response.ok) {
    alert('Заявка отправлена! Мы свяжемся с вами.');
  } else {
    alert('Ошибка. Попробуйте позже.');
  }
});
```

### Проверка доступности дат

```javascript
// netlify/functions/check-availability.js
exports.handler = async (event, context) => {
  const { tour, date } = event.queryStringParameters;

  // В production: проверяем в базе данных или Google Calendar API
  const bookedDates = {
    'safari': ['2026-02-05', '2026-02-10'],
    'burj-khalifa': ['2026-02-07'],
  };

  const isAvailable = !bookedDates[tour]?.includes(date);

  return {
    statusCode: 200,
    body: JSON.stringify({
      tour,
      date,
      available: isAvailable,
    }),
  };
};
```

### Email уведомления (SendGrid)

```javascript
// netlify/functions/send-email.js
const sgMail = require('@sendgrid/mail');

exports.handler = async (event, context) => {
  sgMail.setApiKey(process.env.SENDGRID_API_KEY);

  const { to, subject, text } = JSON.parse(event.body);

  const msg = {
    to: to,
    from: process.env.FROM_EMAIL,
    subject: subject,
    text: text,
  };

  try {
    await sgMail.send(msg);
    return {
      statusCode: 200,
      body: JSON.stringify({ success: true }),
    };
  } catch (error) {
    console.error('SendGrid error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message }),
    };
  }
};
```

**Dependencies:** `package.json`:
```json
{
  "dependencies": {
    "@sendgrid/mail": "^7.7.0"
  }
}
```

---

## Netlify Forms: Полная форма заявки

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Забронировать экскурсию</title>
  <style>
    form { max-width: 500px; margin: 50px auto; }
    label { display: block; margin: 10px 0 5px; }
    input, select, textarea { width: 100%; padding: 8px; }
    button { margin-top: 20px; padding: 10px 20px; }
  </style>
</head>
<body>
  <h1>Забронировать экскурсию</h1>

  <form name="booking" method="POST" netlify netlify-honeypot="bot-field" action="/thank-you">
    <!-- Скрытые поля для Netlify -->
    <input type="hidden" name="form-name" value="booking" />
    <p style="display:none">
      <label>Don't fill: <input name="bot-field" /></label>
    </p>

    <!-- Видимые поля -->
    <label>
      Ваше имя *
      <input type="text" name="name" required />
    </label>

    <label>
      Телефон *
      <input type="tel" name="phone" required />
    </label>

    <label>
      Email
      <input type="email" name="email" />
    </label>

    <label>
      Экскурсия *
      <select name="tour" required>
        <option value="">Выберите...</option>
        <option value="safari">Джип-сафари</option>
        <option value="burj-khalifa">Бурдж Халифа</option>
        <option value="abu-dhabi">Абу-Даби тур</option>
      </select>
    </label>

    <label>
      Желаемая дата
      <input type="date" name="date" />
    </label>

    <label>
      Количество человек *
      <input type="number" name="people" min="1" max="20" required />
    </label>

    <label>
      Комментарий
      <textarea name="message" rows="4"></textarea>
    </label>

    <button type="submit">Отправить заявку</button>
  </form>
</body>
</html>
```

**Thank you page:**

```html
<!-- thank-you.html -->
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Спасибо!</title>
</head>
<body>
  <h1>Заявка принята!</h1>
  <p>Мы свяжемся с вами в ближайшее время.</p>
  <a href="/">Вернуться на главную</a>
</body>
</html>
```

### AJAX форма (без перезагрузки)

```html
<form name="contact" netlify netlify-honeypot="bot-field">
  <input type="hidden" name="form-name" value="contact" />
  <p style="display:none">
    <label>Don't fill this out: <input name="bot-field" /></label>
  </p>
  <input type="text" name="name" />
  <button type="submit">Отправить</button>
</form>

<script>
  document.querySelector('form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);

    const response = await fetch('/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams(formData).toString(),
    });

    if (response.ok) {
      alert('Заявка отправлена!');
      e.target.reset();
    } else {
      alert('Ошибка. Попробуйте позже.');
    }
  });
</script>
```

### Form Notification → Telegram (webhook)

```javascript
// netlify/functions/form-handler.js
exports.handler = async (event, context) => {
  const data = JSON.parse(event.body);

  console.log('New form submission:', data);

  const message = `
Новая заявка:
Имя: ${data.data.name}
Email: ${data.data.email}
  `;

  await fetch(`https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: process.env.TELEGRAM_CHAT_ID,
      text: message,
    }),
  });

  return { statusCode: 200, body: 'OK' };
};
```

---

## Netlify dev для Serverless Functions: полный пример

**Сценарий:** Разрабатываете прайс-лист с Serverless Function для фетчинга Google Sheets.

**Структура проекта:**

```
price-list/
├── index.html
├── script.js
└── netlify/
    └── functions/
        └── fetch-prices.js
```

**Serverless Function:**

```javascript
// netlify/functions/fetch-prices.js
exports.handler = async (event, context) => {
  // В production: fetch Google Sheets API
  const prices = [
    { name: 'Джип-сафари', price: 150 },
    { name: 'Бурдж Халифа', price: 120 },
  ];

  return {
    statusCode: 200,
    body: JSON.stringify(prices),
  };
};
```

**Frontend:**

```javascript
// script.js
fetch('/.netlify/functions/fetch-prices')
  .then(r => r.json())
  .then(data => {
    console.log(data);
    // Рендерим таблицу
  });
```

**Локальная разработка:**

```bash
cd /d/Downloads/price-list
netlify dev
```

Netlify запустит:
- Static server: `http://localhost:8888`
- Functions: `http://localhost:8888/.netlify/functions/fetch-prices`

Откройте `http://localhost:8888` → function работает локально!

**Debugging:**
- Логи function выводятся в терминал
- Изменения в `fetch-prices.js` → hot reload

---

## Preview Deployments с CLI

**Сценарий:** Хотите показать клиенту изменения до merge в main.

**Шаги:**

1. **Создайте feature branch:**
```bash
git checkout -b feature/new-hero
```

2. **Сделайте изменения:**
```bash
nano src/Hero.js
git add .
git commit -m "New hero design"
```

3. **Deploy preview:**
```bash
netlify deploy
```

Получите URL:
```
Draft URL: https://abc123--my-project.netlify.app
```

4. **Отправьте клиенту URL**

5. **Клиент одобрил → deploy в production:**
```bash
git checkout main
git merge feature/new-hero
netlify deploy --prod
```

Или просто `git push` (если настроен GitHub Integration).

---

## Практический пример: Google Sheets Прайс-лист с Environment Variables

**Цель:** Автообновление прайс-листа из Google Sheets.

**Шаг 1: Получите API key**
- Google Cloud Console → API & Services → Credentials
- Create Credentials → API key
- Restrict key → Google Sheets API
- Скопируйте key: `AIzaSyD...`

**Шаг 2: Добавьте в Netlify**
- Site Settings → Environment variables → Add variable
- Key: `GOOGLE_SHEETS_API_KEY`, Value: `AIzaSyD...`
- Scopes: Production

**Шаг 3: Serverless Function** (см. Google Sheets API интеграция выше)

**Шаг 4: Frontend**

```javascript
// script.js
fetch('/.netlify/functions/fetch-prices')
  .then(r => r.json())
  .then(prices => {
    const table = document.getElementById('price-table');
    prices.forEach(p => {
      table.innerHTML += `<tr><td>${p.name}</td><td>${p.price}</td></tr>`;
    });
  });
```

**Результат:**
- Google Sheets обновили → перезагрузили страницу → новые цены
- API key в безопасности (только в Serverless Function)

---

## CORS решение через Serverless Function

```javascript
// netlify/functions/proxy.js
const fetch = require('node-fetch');

exports.handler = async (event) => {
  const response = await fetch('https://api.example.com/data');
  const data = await response.json();

  return {
    statusCode: 200,
    body: JSON.stringify(data),
  };
};
```

```javascript
// Frontend
fetch('/.netlify/functions/proxy')
  .then(r => r.json())
  .then(data => console.log(data));
```

---

## Event и Context объекты (Serverless Functions)

**Event object:**

```javascript
{
  httpMethod: 'POST',
  headers: { 'content-type': 'application/json', ... },
  queryStringParameters: { key: 'value' },
  body: '{"name":"John"}',
  path: '/.netlify/functions/hello',
  isBase64Encoded: false,
}
```

**Доступ:**
- `event.httpMethod` — GET, POST, etc
- `event.headers` — HTTP headers
- `event.queryStringParameters` — query params (?key=value)
- `event.body` — request body (строка, нужен JSON.parse)

**Context object:**

```javascript
{
  callbackWaitsForEmptyEventLoop: true,
  functionName: 'hello',
  functionVersion: '$LATEST',
  clientContext: { ... },
}
```

Обычно не используется (для продвинутых сценариев).
