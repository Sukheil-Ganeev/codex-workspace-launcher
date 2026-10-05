# Каталог API для Make.com

## Бесплатные API (No Auth)

### AlAdhan — Время намаза
```
URL: https://api.aladhan.com/v1/timingsByCity?city=Dubai&country=UAE&method=8
Auth: No Auth
Лимит: Без ограничений

Response:
{{data.timings.Fajr}}      — Фаджр
{{data.timings.Sunrise}}   — Восход
{{data.timings.Dhuhr}}     — Зухр
{{data.timings.Asr}}       — Аср
{{data.timings.Maghrib}}   — Магриб
{{data.timings.Isha}}      — Иша
{{data.date.readable}}     — Дата
```

### ExchangeRate-API — Курсы валют
```
URL: https://api.exchangerate-api.com/v4/latest/USD
Auth: No Auth
Лимит: 1500 запросов/месяц

Response:
{{rates.RUB}}   — Рубль
{{rates.AED}}   — Дирхам
{{rates.EUR}}   — Евро
{{rates.KZT}}   — Тенге
{{time_last_updated}}  — Время обновления
```

### Open-Meteo — Погода
```
URL: https://api.open-meteo.com/v1/forecast?latitude=25.2&longitude=55.27&current_weather=true
Auth: No Auth
Лимит: 10000 запросов/день

Response:
{{current_weather.temperature}}     — Температура °C
{{current_weather.windspeed}}       — Скорость ветра км/ч
{{current_weather.weathercode}}     — Код погоды
```

---

## API с ключом (API Key)

### OpenWeather — Погода
```
URL: https://api.openweathermap.org/data/2.5/weather?q=Dubai&appid=YOUR_KEY&units=metric&lang=ru
Auth: API Key в URL (appid=)
Лимит: 1000 запросов/день (free)
Получить ключ: https://openweathermap.org/api

Response:
{{main.temp}}              — Температура °C
{{main.humidity}}          — Влажность %
{{weather[0].description}} — Описание на русском
{{wind.speed}}             — Скорость ветра м/с
```

### Google Geocoding — Координаты
```
URL: https://maps.googleapis.com/maps/api/geocode/json?address=Dubai&key=YOUR_KEY
Auth: API Key в URL (key=)
Лимит: 200$/месяц бесплатно
Получить ключ: https://console.cloud.google.com

Response:
{{results[0].geometry.location.lat}}  — Широта
{{results[0].geometry.location.lng}}  — Долгота
{{results[0].formatted_address}}      — Полный адрес
```

---

## API с Bearer Token

### Notion API
```
URL: https://api.notion.com/v1/databases/{database_id}/query
Auth: Bearer Token
Headers:
  Authorization: Bearer secret_YOUR_TOKEN
  Notion-Version: 2022-06-28
  Content-Type: application/json

Получить токен: Notion → Settings → Integrations → New integration
```

---

## Универсальный шаблон подключения нового API

### 1. Найди документацию
- Обычно: `docs.servicename.com` или `servicename.com/api`

### 2. Определи тип авторизации
| Тип | Как передать в Make.com |
|-----|------------------------|
| No Auth | Просто URL |
| API Key в URL | `?key=YOUR_KEY` или `?appid=YOUR_KEY` |
| API Key в Header | Headers → `X-API-Key: YOUR_KEY` |
| Bearer Token | Headers → `Authorization: Bearer YOUR_TOKEN` |

### 3. Собери URL
```
Базовый: https://api.service.com/v1/endpoint
+ Параметры: ?param1=value1&param2=value2
= Полный: https://api.service.com/v1/endpoint?param1=value1&param2=value2
```

### 4. Протестируй
- Открой URL в браузере (для No Auth / API Key в URL)
- Или используй Postman / curl

### 5. Запиши маппинг
```
{{data}}           — весь объект data
{{data.field}}     — поле field внутри data
{{data[0].field}}  — первый элемент массива, поле field
{{results[0].name}} — типичный паттерн для списков
```

---

## Частые ошибки API

| Ошибка | Причина | Решение |
|--------|---------|---------|
| 401 Unauthorized | Неправильный ключ | Проверь API key |
| 403 Forbidden | Ключ не активирован | Активируй billing |
| 429 Too Many Requests | Превышен лимит | Добавь Sleep между запросами |
| 404 Not Found | Неправильный endpoint | Проверь URL в документации |
| CORS error | API не для браузера | Используй HTTP модуль Make |
