# API Proxy Example - Проксирование внешнего API

Пример проксирования внешних API через Netlify для обхода CORS и скрытия ключей.

## Описание

Показывает как безопасно использовать внешние API (Google Maps, Currency API, Weather API) без раскрытия API ключей клиенту.

**Идеально для:** интеграций с внешними сервисами, скрытия API ключей, обхода CORS.

## Структура проекта

```
api-proxy-example/
├── index.html                    # Демо страница
├── netlify.toml                  # Конфигурация с redirects
└── netlify/functions/
    ├── currency.js               # Прокси для валют
    ├── weather.js                # Прокси для погоды
    └── maps.js                   # Прокси для карт
```

## Кейсы использования

1. **Currency API** - получение курсов валют
2. **Weather API** - погода в Дубае
3. **Maps API** - геокодинг адресов

## Пример 1: Currency API Proxy

### netlify/functions/currency.js

```javascript
// Прокси для получения курсов валют
// Использует API: exchangerate-api.com

exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  try {
    // API ключ хранится в environment variables
    const apiKey = process.env.CURRENCY_API_KEY;

    // Параметры из query string
    const { from = 'AED', to = 'USD' } = event.queryStringParameters || {};

    // Запрос к внешнему API
    const url = `https://v6.exchangerate-api.com/v6/${apiKey}/pair/${from}/${to}`;

    const response = await fetch(url);
    const data = await response.json();

    if (data.result === 'success') {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          success: true,
          from: from,
          to: to,
          rate: data.conversion_rate,
          timestamp: new Date().toISOString()
        })
      };
    } else {
      throw new Error('API Error');
    }

  } catch (error) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        success: false,
        error: error.message
      })
    };
  }
};
```

## Пример 2: Weather API Proxy

### netlify/functions/weather.js

```javascript
// Прокси для получения погоды
// Использует API: openweathermap.org

exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  try {
    const apiKey = process.env.WEATHER_API_KEY;
    const city = event.queryStringParameters?.city || 'Dubai';

    const url = `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric&lang=ru`;

    const response = await fetch(url);
    const data = await response.json();

    if (response.ok) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          success: true,
          city: data.name,
          temperature: data.main.temp,
          description: data.weather[0].description,
          humidity: data.main.humidity,
          windSpeed: data.wind.speed
        })
      };
    } else {
      throw new Error('Weather API Error');
    }

  } catch (error) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        success: false,
        error: error.message
      })
    };
  }
};
```

## Пример 3: Google Maps Geocoding Proxy

### netlify/functions/maps.js

```javascript
// Прокси для геокодинга адресов
// Использует API: Google Maps Geocoding

exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  try {
    const apiKey = process.env.GOOGLE_MAPS_API_KEY;
    const address = event.queryStringParameters?.address;

    if (!address) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Address parameter required' })
      };
    }

    const url = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(address)}&key=${apiKey}`;

    const response = await fetch(url);
    const data = await response.json();

    if (data.status === 'OK') {
      const result = data.results[0];
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          success: true,
          formattedAddress: result.formatted_address,
          location: result.geometry.location,
          placeId: result.place_id
        })
      };
    } else {
      throw new Error('Geocoding failed: ' + data.status);
    }

  } catch (error) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        success: false,
        error: error.message
      })
    };
  }
};
```

## Демо страница

### index.html

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>API Proxy Demo</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 800px;
      margin: 50px auto;
      padding: 20px;
      background: #f5f5f5;
    }
    .api-card {
      background: white;
      padding: 30px;
      margin-bottom: 20px;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    button {
      background: #667eea;
      color: white;
      border: none;
      padding: 12px 24px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 16px;
    }
    button:hover {
      background: #5568d3;
    }
    .result {
      margin-top: 20px;
      padding: 20px;
      background: #f8f9fa;
      border-radius: 8px;
      font-family: monospace;
      white-space: pre-wrap;
    }
    input {
      padding: 10px;
      border: 2px solid #e0e0e0;
      border-radius: 6px;
      font-size: 16px;
      width: 200px;
      margin-right: 10px;
    }
  </style>
</head>
<body>
  <h1>🔗 API Proxy Examples</h1>

  <!-- Currency API -->
  <div class="api-card">
    <h2>💱 Currency Converter</h2>
    <p>Получение курса валют через прокси</p>
    <select id="currencyFrom">
      <option value="AED">AED</option>
      <option value="USD">USD</option>
      <option value="EUR">EUR</option>
      <option value="RUB">RUB</option>
    </select>
    <span> → </span>
    <select id="currencyTo">
      <option value="USD">USD</option>
      <option value="AED">AED</option>
      <option value="EUR">EUR</option>
      <option value="RUB">RUB</option>
    </select>
    <button onclick="getCurrency()">Получить курс</button>
    <div id="currencyResult" class="result" style="display:none;"></div>
  </div>

  <!-- Weather API -->
  <div class="api-card">
    <h2>🌤️ Weather</h2>
    <p>Получение погоды через прокси</p>
    <input type="text" id="city" value="Dubai" placeholder="Город">
    <button onclick="getWeather()">Получить погоду</button>
    <div id="weatherResult" class="result" style="display:none;"></div>
  </div>

  <!-- Maps API -->
  <div class="api-card">
    <h2>📍 Geocoding</h2>
    <p>Геокодинг адреса через прокси</p>
    <input type="text" id="address" value="Burj Khalifa, Dubai" placeholder="Адрес">
    <button onclick="geocodeAddress()">Найти координаты</button>
    <div id="mapsResult" class="result" style="display:none;"></div>
  </div>

  <script>
    async function getCurrency() {
      const from = document.getElementById('currencyFrom').value;
      const to = document.getElementById('currencyTo').value;

      try {
        const response = await fetch(`/.netlify/functions/currency?from=${from}&to=${to}`);
        const data = await response.json();

        const resultDiv = document.getElementById('currencyResult');
        resultDiv.style.display = 'block';

        if (data.success) {
          resultDiv.textContent = `1 ${data.from} = ${data.rate.toFixed(4)} ${data.to}`;
        } else {
          resultDiv.textContent = 'Ошибка: ' + data.error;
        }
      } catch (error) {
        alert('Ошибка: ' + error.message);
      }
    }

    async function getWeather() {
      const city = document.getElementById('city').value;

      try {
        const response = await fetch(`/.netlify/functions/weather?city=${encodeURIComponent(city)}`);
        const data = await response.json();

        const resultDiv = document.getElementById('weatherResult');
        resultDiv.style.display = 'block';

        if (data.success) {
          resultDiv.textContent = `${data.city}
Температура: ${data.temperature}°C
Описание: ${data.description}
Влажность: ${data.humidity}%
Ветер: ${data.windSpeed} м/с`;
        } else {
          resultDiv.textContent = 'Ошибка: ' + data.error;
        }
      } catch (error) {
        alert('Ошибка: ' + error.message);
      }
    }

    async function geocodeAddress() {
      const address = document.getElementById('address').value;

      try {
        const response = await fetch(`/.netlify/functions/maps?address=${encodeURIComponent(address)}`);
        const data = await response.json();

        const resultDiv = document.getElementById('mapsResult');
        resultDiv.style.display = 'block';

        if (data.success) {
          resultDiv.textContent = `Адрес: ${data.formattedAddress}
Координаты:
  Широта: ${data.location.lat}
  Долгота: ${data.location.lng}
Place ID: ${data.placeId}`;
        } else {
          resultDiv.textContent = 'Ошибка: ' + data.error;
        }
      } catch (error) {
        alert('Ошибка: ' + error.message);
      }
    }
  </script>
</body>
</html>
```

## netlify.toml

```toml
[build]
  publish = "."
  functions = "netlify/functions"

# Проксирование на functions
[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

## Настройка Environment Variables

В Netlify UI добавьте:

```
CURRENCY_API_KEY=your_exchangerate_api_key
WEATHER_API_KEY=your_openweather_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

## Получение API ключей

### Currency API
1. Зарегистрируйтесь на [exchangerate-api.com](https://www.exchangerate-api.com/)
2. Free plan: 1500 запросов/месяц

### Weather API
1. Зарегистрируйтесь на [openweathermap.org](https://openweathermap.org/api)
2. Free plan: 1000 запросов/день

### Google Maps API
1. [Google Cloud Console](https://console.cloud.google.com/)
2. Включите Geocoding API
3. Создайте API Key

## Deploy

```bash
git init
git add .
git commit -m "Initial commit"
# Push на GitHub и deploy через Netlify
```

Добавьте Environment Variables в Netlify UI.

## Преимущества прокси

1. **Безопасность:** API ключи не видны клиенту
2. **CORS:** Обход CORS ограничений
3. **Кэширование:** Можно добавить кэш в function
4. **Лимиты:** Контроль rate limiting на своей стороне
5. **Трансформация:** Модификация ответов API

## Расширения

### Добавление кэширования

```javascript
const cache = {};

exports.handler = async (event, context) => {
  const cacheKey = JSON.stringify(event.queryStringParameters);

  if (cache[cacheKey]) {
    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: cache[cacheKey]
    };
  }

  // Запрос к API...
  const result = JSON.stringify(data);
  cache[cacheKey] = result;

  return { statusCode: 200, body: result };
};
```

### Rate limiting

```javascript
const rateLimits = {};

function checkRateLimit(ip) {
  const now = Date.now();
  const limit = rateLimits[ip] || { count: 0, reset: now + 60000 };

  if (now > limit.reset) {
    rateLimits[ip] = { count: 1, reset: now + 60000 };
    return true;
  }

  if (limit.count >= 10) {
    return false;
  }

  limit.count++;
  return true;
}
```

## Troubleshooting

**403 Forbidden:**
- Проверьте API ключи
- Проверьте квоты API

**CORS ошибки:**
- Добавьте CORS headers во всех функциях
- Обработайте OPTIONS запросы

**Таймауты:**
- Netlify Functions timeout: 10 секунд (free), 26 секунд (pro)
- Оптимизируйте запросы или используйте background functions
