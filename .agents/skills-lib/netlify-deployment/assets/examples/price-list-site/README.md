# Price List Site - Прайс-лист с Google Sheets

Статичный сайт с прайс-листом, загружаемым из Google Sheets через Serverless Function.

## Описание

Этот пример показывает как создать сайт с динамическим прайс-листом, который автоматически обновляется при изменении Google таблицы.

**Идеально для:** туристических компаний, которые часто обновляют цены на туры.

## Структура проекта

```
price-list-site/
├── index.html                    # Главная страница с прайс-листом
├── netlify.toml                  # Конфигурация Netlify
└── netlify/functions/
    └── get-prices.js             # Функция для получения данных из Google Sheets
```

## Шаг 1: Создайте Google Sheet

1. Создайте новую Google таблицу
2. Название листа: `Prices`
3. Структура таблицы:

| Название | Описание | Цена | Валюта |
|----------|----------|------|--------|
| Джип-сафари | Утреннее сафари | 250 | AED |
| Бурдж Халифа | 124 этаж | 149 | AED |
| Городской тур | Обзорная экскурсия | 180 | AED |

4. Сделайте таблицу публичной:
   - `File` → `Share` → `Get link`
   - Выберите `Anyone with the link can view`

5. Скопируйте ID таблицы из URL:
   ```
   https://docs.google.com/spreadsheets/d/ЭТОТ_ID_ЗДЕСЬ/edit
   ```

## Шаг 2: Получите Google API Key

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите `Google Sheets API`:
   - `APIs & Services` → `Library` → Найдите `Google Sheets API` → `Enable`
4. Создайте API ключ:
   - `APIs & Services` → `Credentials` → `Create Credentials` → `API Key`
5. Скопируйте ключ

## Шаг 3: Создайте файлы проекта

### index.html

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Прайс-лист | Туры в ОАЭ</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 800px;
      margin: 50px auto;
      padding: 20px;
      background: #f5f5f5;
    }
    h1 { color: #333; }
    .loading { text-align: center; padding: 40px; }
    .error { background: #ffebee; padding: 20px; border-radius: 8px; color: #c62828; }
    .prices { display: grid; gap: 20px; }
    .price-card {
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .price-card h3 { margin-top: 0; color: #1976d2; }
    .price-card .price {
      font-size: 24px;
      font-weight: bold;
      color: #4caf50;
      margin-top: 10px;
    }
  </style>
</head>
<body>
  <h1>🏜️ Туры в ОАЭ - Прайс-лист</h1>

  <div id="content">
    <div class="loading">Загрузка прайс-листа...</div>
  </div>

  <script>
    async function loadPrices() {
      try {
        const response = await fetch('/.netlify/functions/get-prices');
        const result = await response.json();

        if (result.success) {
          displayPrices(result.data);
        } else {
          showError('Ошибка загрузки: ' + result.message);
        }
      } catch (error) {
        showError('Не удалось загрузить прайс-лист: ' + error.message);
      }
    }

    function displayPrices(items) {
      const html = `
        <div class="prices">
          ${items.map(item => `
            <div class="price-card">
              <h3>${item.Название}</h3>
              <p>${item.Описание}</p>
              <div class="price">${item.Цена} ${item.Валюта}</div>
            </div>
          `).join('')}
        </div>
      `;
      document.getElementById('content').innerHTML = html;
    }

    function showError(message) {
      document.getElementById('content').innerHTML = `
        <div class="error">${message}</div>
      `;
    }

    // Загрузка при открытии страницы
    loadPrices();
  </script>
</body>
</html>
```

### netlify.toml

```toml
[build]
  publish = "."
  functions = "netlify/functions"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

### netlify/functions/get-prices.js

Скопируйте содержимое из `templates/function-api-sheets.js`

## Шаг 4: Deploy на Netlify

### Через Git (рекомендуется)

1. Создайте Git репозиторий:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. Загрузите на GitHub

3. В Netlify:
   - `New site from Git`
   - Выберите ваш репозиторий
   - Deploy

### Через Netlify CLI

```bash
npm install -g netlify-cli
netlify login
netlify init
netlify deploy --prod
```

## Шаг 5: Настройте Environment Variables

В Netlify UI:

1. `Site settings` → `Environment variables` → `Add a variable`
2. Добавьте:
   - `GOOGLE_API_KEY` = ваш API ключ
   - `SHEET_ID` = ID вашей таблицы

## Шаг 6: Проверка

Откройте ваш сайт: `https://your-site.netlify.app`

Прайс-лист должен загрузиться автоматически из Google Sheets.

## Обновление цен

Просто измените данные в Google таблице - сайт будет показывать актуальные цены без редеплоя!

## Расширения

- Добавьте фильтрацию по категориям
- Добавьте кнопку "Забронировать"
- Интегрируйте с формой заявки
- Добавьте кэширование (в function или через Netlify Edge)

## Troubleshooting

**Ошибка "Google API error":**
- Проверьте что Google Sheets API включен
- Проверьте что таблица публичная
- Проверьте правильность SHEET_ID

**Данные не загружаются:**
- Откройте Netlify Functions logs
- Проверьте что environment variables добавлены
