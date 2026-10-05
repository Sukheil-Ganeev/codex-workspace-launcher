# Static with Forms - Статичный сайт с формой обратной связи

Пример статичного сайта с формой, обрабатываемой через serverless функцию.

## Структура проекта

```
static-with-forms/
├── index.html           # Страница с формой
├── api/
│   └── submit-form.js   # API для обработки формы
├── vercel.json          # Конфигурация Vercel
└── README.md            # Документация
```

## Особенности

- Красивая responsive форма
- Client-side валидация
- Serverless обработка на backend
- Варианты интеграции (Telegram, Email, Database)
- Feedback пользователю (успех/ошибка)

## Деплой на Vercel

```bash
# Перейти в папку проекта
cd path/to/static-with-forms

# Залогиниться
vercel login

# Деплой
vercel --prod
```

## Интеграции

### Вариант 1: Отправка в Telegram

1. Создать бота через [@BotFather](https://t.me/BotFather)
2. Получить токен
3. Узнать Chat ID (отправить `/start` боту [@userinfobot](https://t.me/userinfobot))
4. Добавить переменные окружения:
   ```bash
   vercel env add TELEGRAM_BOT_TOKEN
   vercel env add TELEGRAM_CHAT_ID
   ```
5. Раскомментировать код в `api/submit-form.js` (секция "ВАРИАНТ 1")
6. Redeploy:
   ```bash
   vercel --prod
   ```

### Вариант 2: Отправка на Email (SendGrid)

1. Зарегистрироваться на [SendGrid](https://sendgrid.com/)
2. Получить API ключ
3. Установить зависимость:
   ```bash
   npm init -y
   npm install @sendgrid/mail
   ```
4. Добавить переменную окружения:
   ```bash
   vercel env add SENDGRID_API_KEY
   ```
5. Раскомментировать код в `api/submit-form.js` (секция "ВАРИАНТ 2")
6. Redeploy

### Вариант 3: Сохранение в MongoDB

1. Создать кластер на [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Получить connection string
3. Установить зависимость:
   ```bash
   npm install mongodb
   ```
4. Добавить переменную окружения:
   ```bash
   vercel env add MONGODB_URI
   ```
5. Раскомментировать код в `api/submit-form.js` (секция "ВАРИАНТ 3")
6. Redeploy

## Настройка формы

### Добавить новые поля

В `index.html`:

```html
<div class="form-group">
    <label for="phone">Телефон</label>
    <input type="tel" id="phone" name="phone" required>
</div>
```

В `api/submit-form.js`:

```javascript
const { name, email, message, phone } = req.body;

if (!name || !email || !message || !phone) {
    return res.status(400).json({ 
        error: 'Все поля обязательны' 
    });
}
```

### Изменить стили

В `<style>` секции `index.html` измените цвета:

```css
background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
```

### Добавить капчу (reCAPTCHA)

1. Зарегистрироваться на [Google reCAPTCHA](https://www.google.com/recaptcha)
2. Добавить скрипт в `<head>`:
   ```html
   <script src="https://www.google.com/recaptcha/api.js" async defer></script>
   ```
3. Добавить в форму:
   ```html
   <div class="g-recaptcha" data-sitekey="your-site-key"></div>
   ```
4. Валидировать на backend

## Тестирование

### Локальное тестирование

```bash
# Установить Vercel CLI
npm install -g vercel

# Запустить dev сервер
vercel dev

# Открыть http://localhost:3000
```

### Проверка формы

1. Заполнить все поля
2. Нажать "Отправить"
3. Проверить:
   - Сообщение об успехе
   - Логи: `vercel logs`
   - Telegram (если настроен)
   - Email (если настроен)

## Troubleshooting

**Проблема:** Форма не отправляется

**Решение:**
- Открыть DevTools (F12) → Console
- Проверить ошибки JavaScript
- Проверить Network tab (запрос к `/api/submit-form`)

---

**Проблема:** 500 Internal Server Error

**Решение:**
- Проверить логи: `vercel logs`
- Убедиться, что все переменные окружения добавлены
- Проверить синтаксис в `api/submit-form.js`

---

**Проблема:** CORS ошибки

**Решение:**
Добавить в `vercel.json`:

```json
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Access-Control-Allow-Origin", "value": "*" },
        { "key": "Access-Control-Allow-Methods", "value": "POST, OPTIONS" },
        { "key": "Access-Control-Allow-Headers", "value": "Content-Type" }
      ]
    }
  ]
}
```

---

**Проблема:** Сообщения не приходят в Telegram

**Решение:**
- Проверить TELEGRAM_BOT_TOKEN (правильный формат: `123456:ABC-DEF...`)
- Проверить TELEGRAM_CHAT_ID (число, например: `123456789`)
- Убедиться, что отправили `/start` боту
- Проверить логи: `vercel logs`

## Безопасность

### Rate Limiting

Добавить защиту от спама (пример с Upstash Redis):

```javascript
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(5, "1 h"),
});

export default async function handler(req, res) {
  const identifier = req.headers["x-forwarded-for"] || "anonymous";
  const { success } = await ratelimit.limit(identifier);
  
  if (!success) {
    return res.status(429).json({ error: "Слишком много запросов" });
  }
  
  // ... остальной код
}
```

### Валидация данных

Используйте библиотеки валидации:

```bash
npm install joi
```

```javascript
import Joi from 'joi';

const schema = Joi.object({
  name: Joi.string().min(2).max(50).required(),
  email: Joi.string().email().required(),
  message: Joi.string().min(10).max(1000).required()
});

const { error, value } = schema.validate(req.body);
if (error) {
  return res.status(400).json({ error: error.details[0].message });
}
```

## Полезные ссылки

- [Vercel Forms Guide](https://vercel.com/guides/deploying-react-forms-using-formspree-with-vercel)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [SendGrid Node.js](https://github.com/sendgrid/sendgrid-nodejs)
- [MongoDB Node.js Driver](https://www.mongodb.com/docs/drivers/node/current/)
