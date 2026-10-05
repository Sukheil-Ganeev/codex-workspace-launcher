# Serverless API - API endpoints на Vercel

Пример serverless функций для создания API на Vercel.

## Структура проекта

```
serverless-api/
├── api/
│   ├── webhook.js       # Telegram webhook endpoint
│   └── hello.js         # Простой API endpoint
├── vercel.json          # Конфигурация Vercel
└── README.md            # Документация
```

## API Endpoints

### 1. `/api/hello` - Простой GET endpoint

**Использование:**

```bash
# Простой запрос
curl https://your-domain.vercel.app/api/hello

# С параметром name
curl https://your-domain.vercel.app/api/hello?name=Сухейль
```

**Ответ:**

```json
{
  "message": "Привет, Сухейль!",
  "timestamp": "2025-02-04T15:30:00.000Z",
  "method": "GET"
}
```

### 2. `/api/webhook` - Telegram webhook

**Настройка:**

1. Создать Telegram бота через [@BotFather](https://t.me/BotFather)
2. Получить токен
3. Добавить токен в Vercel Environment Variables:
   ```bash
   vercel env add TELEGRAM_BOT_TOKEN
   ```
4. Установить webhook:
   ```bash
   curl -X POST https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-domain.vercel.app/api/webhook"}'
   ```

**Использование:**

Бот будет автоматически получать обновления от Telegram.

## Деплой на Vercel

### 1. Через CLI

```bash
# Перейти в папку проекта
cd path/to/serverless-api

# Залогиниться
vercel login

# Деплой
vercel

# Production деплой
vercel --prod
```

### 2. Через GitHub

```bash
git init
git add .
git commit -m "Add serverless API"
git remote add origin your-repo-url
git push -u origin main
```

Затем на [vercel.com](https://vercel.com):
- New Project → Import Repository
- Deploy

## Environment Variables

Добавить переменные окружения:

```bash
# Через CLI
vercel env add TELEGRAM_BOT_TOKEN
vercel env add DATABASE_URL

# Или через Web Dashboard:
# Project Settings → Environment Variables
```

Использовать в коде:

```javascript
const token = process.env.TELEGRAM_BOT_TOKEN;
```

## Добавление новых endpoints

1. Создать файл в `api/`:
   ```bash
   touch api/users.js
   ```

2. Добавить код:
   ```javascript
   export default function handler(req, res) {
     res.status(200).json({ users: [] });
   }
   ```

3. Endpoint доступен по адресу:
   ```
   https://your-domain.vercel.app/api/users
   ```

## Поддерживаемые методы

```javascript
export default function handler(req, res) {
  if (req.method === 'GET') {
    // GET запрос
  } else if (req.method === 'POST') {
    // POST запрос
  } else if (req.method === 'PUT') {
    // PUT запрос
  } else if (req.method === 'DELETE') {
    // DELETE запрос
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}
```

## Работа с Body

```javascript
export default async function handler(req, res) {
  // JSON body (автоматический парсинг)
  const data = req.body;
  
  // Query параметры
  const { id } = req.query;
  
  // Headers
  const auth = req.headers.authorization;
  
  res.status(200).json({ received: data });
}
```

## Логирование

Логи доступны через:

```bash
# CLI
vercel logs

# Или в Web Dashboard:
# Project → Deployments → Deployment → Logs
```

## Limits

- **Execution timeout:** 10s (Hobby), 60s (Pro)
- **Payload size:** 5MB
- **Concurrent executions:** 1000 (Pro)

## Troubleshooting

**Проблема:** 404 на /api/endpoint

**Решение:** 
- Проверить, что файл находится в папке `api/`
- Проверить `vercel.json` конфигурацию
- Redeploy проект

---

**Проблема:** Environment variables не работают

**Решение:**
- Добавить через `vercel env add`
- Redeploy после добавления переменных
- Проверить название переменной (case-sensitive)

---

**Проблема:** Timeout ошибки

**Решение:**
- Оптимизировать код (убрать долгие операции)
- Использовать async/await правильно
- Рассмотреть переход на Pro план (60s timeout)

## Полезные ссылки

- [Vercel Serverless Functions](https://vercel.com/docs/concepts/functions/serverless-functions)
- [Node.js Runtime](https://vercel.com/docs/runtimes#official-runtimes/node-js)
- [Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
