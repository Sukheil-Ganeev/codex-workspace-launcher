# API Integrations Reference

## 1. Google Maps Integration

### Подготовка

**Получение API key:**
1. Перейти на [Google Cloud Console](https://console.cloud.google.com/)
2. Создать проект или выбрать существующий
3. Включить Maps JavaScript API
4. Создать API key в разделе Credentials
5. Ограничить key по HTTP referrers (домен вашего сайта)

**Подключение библиотеки:**
```html
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap" async defer></script>
<div id="map" style="height: 500px; width: 100%;"></div>
```

### Базовая карта

```javascript
function initMap() {
  // Координаты Дубая
  const dubai = { lat: 25.2048, lng: 55.2708 };

  const map = new google.maps.Map(document.getElementById('map'), {
    center: dubai,
    zoom: 12,
    mapTypeControl: true,
    streetViewControl: false
  });

  // Добавление маркера
  const marker = new google.maps.Marker({
    position: dubai,
    map: map,
    title: 'Dubai Office',
    animation: google.maps.Animation.DROP
  });

  // Info window при клике
  const infowindow = new google.maps.InfoWindow({
    content: '<h3>Our Office</h3><p>Tecom, Barsha Heights</p>'
  });

  marker.addListener('click', () => {
    infowindow.open(map, marker);
  });
}
```

### Directions API (построение маршрута)

```javascript
function displayRoute(start, end) {
  const directionsService = new google.maps.DirectionsService();
  const directionsRenderer = new google.maps.DirectionsRenderer();

  directionsRenderer.setMap(map);

  const request = {
    origin: start,
    destination: end,
    travelMode: 'DRIVING'
  };

  directionsService.route(request, (result, status) => {
    if (status === 'OK') {
      directionsRenderer.setDirections(result);

      // Вывод расстояния и времени
      const route = result.routes[0].legs[0];
      console.log(`Distance: ${route.distance.text}`);
      console.log(`Duration: ${route.duration.text}`);
    }
  });
}

// Пример использования
displayRoute('Dubai Marina', 'Burj Khalifa');
```

### Множественные маркеры (точки тура)

```javascript
const tourPoints = [
  { lat: 25.2048, lng: 55.2708, title: 'Burj Khalifa' },
  { lat: 25.1972, lng: 55.2744, title: 'Dubai Mall' },
  { lat: 25.0760, lng: 55.1324, title: 'Dubai Marina' },
  { lat: 24.4539, lng: 54.3773, title: 'Sheikh Zayed Mosque' }
];

function addMultipleMarkers(map, points) {
  const bounds = new google.maps.LatLngBounds();

  points.forEach((point, index) => {
    const marker = new google.maps.Marker({
      position: { lat: point.lat, lng: point.lng },
      map: map,
      title: point.title,
      label: (index + 1).toString()
    });

    bounds.extend(marker.position);
  });

  // Автоматическая подгонка zoom под все маркеры
  map.fitBounds(bounds);
}
```

### Ограничение по региону (только ОАЭ)

```javascript
const uaeCenter = { lat: 24.4667, lng: 54.3667 };

const map = new google.maps.Map(document.getElementById('map'), {
  center: uaeCenter,
  zoom: 8,
  restriction: {
    latLngBounds: {
      north: 26.0,
      south: 22.5,
      west: 51.5,
      east: 56.5
    },
    strictBounds: true
  }
});
```

## 2. Google Sheets API

### Подготовка

**Создание и настройка Sheet:**
1. Создать Google Sheet с прайс-листом
2. Структура: `Название | Категория | Цена | Валюта | Описание`
3. Перейти в Tools → Share → Get link → "Anyone with the link can view"
4. Скопировать SHEET_ID из URL: `docs.google.com/spreadsheets/d/{SHEET_ID}/edit`

**Получение API key:**
1. Google Cloud Console → Credentials → Create API Key
2. Включить Google Sheets API
3. Ограничить key по HTTP referrers

### Fetch данных из Sheet

```javascript
const API_KEY = 'YOUR_API_KEY';
const SHEET_ID = 'YOUR_SHEET_ID';
const RANGE = 'Sheet1!A2:E'; // Начиная со второй строки (без заголовков)

async function fetchPrices() {
  const url = `https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values/${RANGE}?key=${API_KEY}`;

  try {
    const response = await fetch(url);
    const data = await response.json();

    // data.values - массив массивов
    // [[Название, Категория, Цена, Валюта, Описание], ...]
    return data.values;
  } catch (error) {
    console.error('Error fetching prices:', error);
    return [];
  }
}

// Использование
async function displayPrices() {
  const prices = await fetchPrices();
  const container = document.getElementById('prices');

  prices.forEach(row => {
    const [name, category, price, currency, description] = row;

    container.innerHTML += `
      <div class="price-card">
        <h3>${name}</h3>
        <span class="category">${category}</span>
        <p class="price">${price} ${currency}</p>
        <p>${description}</p>
      </div>
    `;
  });
}
```

### Автообновление каждые 5 минут

```javascript
let pricesCache = [];
let lastFetch = 0;
const CACHE_TIME = 5 * 60 * 1000; // 5 минут в миллисекундах

async function getPrices() {
  const now = Date.now();

  // Если кэш свежий - вернуть из кэша
  if (pricesCache.length > 0 && (now - lastFetch) < CACHE_TIME) {
    console.log('Using cached data');
    return pricesCache;
  }

  // Иначе - загрузить свежие данные
  console.log('Fetching fresh data');
  pricesCache = await fetchPrices();
  lastFetch = now;

  return pricesCache;
}

// Автоматическое обновление
setInterval(async () => {
  const prices = await fetchPrices();
  pricesCache = prices;
  lastFetch = Date.now();
  displayPrices(); // Перерисовать цены на странице
}, CACHE_TIME);
```

### Фильтрация данных на клиенте

```javascript
async function filterPricesByCategory(category) {
  const prices = await getPrices();

  return prices.filter(row => {
    const [name, rowCategory] = row;
    return rowCategory.toLowerCase() === category.toLowerCase();
  });
}

// Пример: получить только экскурсии
const tours = await filterPricesByCategory('Excursions');
```

## 3. Webhooks

### Отправка данных в Telegram Bot

```javascript
async function sendToTelegram(message) {
  const BOT_TOKEN = 'YOUR_BOT_TOKEN';
  const CHAT_ID = 'YOUR_CHAT_ID';

  const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;

  try {
    await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: CHAT_ID,
        text: message,
        parse_mode: 'HTML'
      })
    });
  } catch (error) {
    console.error('Telegram send error:', error);
  }
}

// Отправка заявки из формы
async function sendBooking(formData) {
  const message = `
<b>🎫 Новая заявка</b>

<b>Имя:</b> ${formData.name}
<b>Email:</b> ${formData.email}
<b>Тур:</b> ${formData.tour}
<b>Дата:</b> ${formData.date}
<b>Количество:</b> ${formData.guests}
  `;

  await sendToTelegram(message);
}
```

### Generic Webhook (отправка в backend)

```javascript
async function sendWebhook(endpoint, data) {
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_TOKEN' // если требуется
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Webhook error:', error);
    throw error;
  }
}

// Использование
const bookingData = {
  customer: 'John Doe',
  tour: 'Desert Safari',
  date: '2026-03-15',
  guests: 2
};

await sendWebhook('https://your-api.com/bookings', bookingData);
```

### Netlify Functions (serverless webhook)

**Файл:** `netlify/functions/submit-booking.js`

```javascript
exports.handler = async (event, context) => {
  // Только POST запросы
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  const data = JSON.parse(event.body);

  // Отправка в Telegram
  const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
  const CHAT_ID = process.env.TELEGRAM_CHAT_ID;

  await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: CHAT_ID,
      text: `New booking: ${data.name} - ${data.tour}`
    })
  });

  return {
    statusCode: 200,
    body: JSON.stringify({ success: true })
  };
};
```

**Вызов со страницы:**
```javascript
async function submitBooking(formData) {
  await fetch('/.netlify/functions/submit-booking', {
    method: 'POST',
    body: JSON.stringify(formData)
  });
}
```

## Best Practices

1. **Безопасность API keys:**
   - Никогда не коммитить ключи в Git
   - Использовать environment variables для serverless functions
   - Ограничивать API keys по доменам и IP

2. **Кэширование:**
   - Минимизировать количество запросов к API
   - Использовать localStorage для долгосрочного кэша
   - Реализовать стратегию stale-while-revalidate

3. **Обработка ошибок:**
   - Всегда оборачивать API calls в try-catch
   - Показывать пользователю понятные сообщения об ошибках
   - Реализовать retry logic для критичных запросов

4. **Performance:**
   - Использовать lazy loading для карт
   - Минимизировать размер payload в webhooks
   - Debounce для частых API calls (поиск, фильтры)
