# Bot Webhook - Telegram бот на Netlify

Serverless Telegram бот, работающий через webhook без собственного сервера.

## Описание

Этот пример показывает как запустить Telegram бота на Netlify используя Serverless Functions и Webhooks.

**Идеально для:** чат-ботов для бронирования, автоответчиков, уведомлений.

## Структура проекта

```
bot-webhook/
├── index.html                    # Простая страница (опционально)
├── netlify.toml                  # Конфигурация Netlify
└── netlify/functions/
    └── webhook.js                # Обработчик webhook от Telegram
```

## Шаг 1: Создайте Telegram бота

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям:
   - Введите название бота: `UAE Tours Bot`
   - Введите username: `uae_tours_bot`
4. Скопируйте токен бота (выглядит как `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Шаг 2: Создайте файлы проекта

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

### netlify/functions/webhook.js

Скопируйте содержимое из `templates/function-webhook.js`

### index.html (опционально)

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>UAE Tours Bot</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 600px;
      margin: 100px auto;
      text-align: center;
      padding: 20px;
    }
    .bot-link {
      display: inline-block;
      background: #0088cc;
      color: white;
      padding: 15px 30px;
      border-radius: 8px;
      text-decoration: none;
      font-size: 18px;
      margin-top: 20px;
    }
  </style>
</head>
<body>
  <h1>🤖 UAE Tours Bot</h1>
  <p>Бот для бронирования туров в ОАЭ</p>
  <a href="https://t.me/YOUR_BOT_USERNAME" class="bot-link">Открыть в Telegram</a>
</body>
</html>
```

## Шаг 3: Deploy на Netlify

### Через Git

```bash
git init
git add .
git commit -m "Initial commit"
# Загрузите на GitHub
```

В Netlify:
- `New site from Git`
- Выберите репозиторий
- Deploy

### Через CLI

```bash
netlify init
netlify deploy --prod
```

## Шаг 4: Настройте Environment Variables

В Netlify UI:

1. `Site settings` → `Environment variables`
2. Добавьте:
   - `BOT_TOKEN` = токен вашего бота

## Шаг 5: Установите Webhook

После деплоя, ваш webhook доступен по адресу:
```
https://your-site.netlify.app/.netlify/functions/webhook
```

Установите webhook командой:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -d "url=https://your-site.netlify.app/.netlify/functions/webhook"
```

Или откройте в браузере:
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://your-site.netlify.app/.netlify/functions/webhook
```

## Шаг 6: Проверка

1. Откройте вашего бота в Telegram
2. Отправьте `/start`
3. Бот должен ответить

## Проверка статуса webhook

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

## Расширение функционала

### Добавление команд

Отредактируйте `webhook.js`:

```javascript
if (text.startsWith('/start')) {
  await sendMessage(BOT_TOKEN, chatId,
    'Привет! 👋\n\nДоступные команды:\n/tours - Туры\n/prices - Цены\n/contact - Контакты'
  );
}
else if (text.startsWith('/tours')) {
  await sendMessage(BOT_TOKEN, chatId,
    '🏜️ Доступные туры:\n\n' +
    '1. Джип-сафари - 250 AED\n' +
    '2. Городской тур - 180 AED\n' +
    '3. Абу-Даби - 200 AED'
  );
}
```

### Интеграция с Google Sheets

Сохраняйте заявки в таблицу:

```javascript
async function saveToSheets(data) {
  // Используйте Google Sheets API
  // или webhook в Make.com/Zapier
}
```

### Отправка уведомлений администратору

```javascript
const ADMIN_CHAT_ID = process.env.ADMIN_CHAT_ID;

await sendMessage(BOT_TOKEN, ADMIN_CHAT_ID,
  `Новая заявка от ${firstName}:\n${text}`
);
```

## Troubleshooting

**Бот не отвечает:**
1. Проверьте логи в Netlify Functions
2. Проверьте webhook: `/getWebhookInfo`
3. Проверьте environment variables

**Ошибка "Webhook already set":**
- Удалите старый webhook: `/deleteWebhook`
- Установите новый

**Таймаут:**
- Telegram ждёт ответ в течение 60 секунд
- Если обработка долгая, сначала ответьте 200, потом обрабатывайте

## Полезные ссылки

- [Telegram Bot API Docs](https://core.telegram.org/bots/api)
- [Netlify Functions Docs](https://docs.netlify.com/functions/overview/)
