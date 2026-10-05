# Пример: Serverless API

Пример создания serverless функций на Vercel для API endpoints и webhooks.

## Структура проекта

```
serverless-api/
├── api/
│   ├── hello.js      # Простой API endpoint
│   └── webhook.js    # Telegram webhook handler
├── vercel.json       # Конфигурация
└── README.md         # Эта инструкция
```

## API Endpoints

### 1. /api/hello

Простой endpoint для тестирования.

**Использование:**
```bash
# GET запрос
curl https://ВАШ_ДОМЕН.vercel.app/api/hello

# С параметром name
curl https://ВАШ_ДОМЕН.vercel.app/api/hello?name=Сухейль
```

**Ответ:**
```json
{
  "message": "Привет, Сухейль!",
  "method": "GET",
  "timestamp": "2026-02-04T12:00:00.000Z",
  "environment": "production"
}
```

### 2. /api/webhook

Обработчик для Telegram webhook.

**Настройка webhook:**
```bash
# Установите webhook для вашего бота
curl -X POST https://api.telegram.org/botВАШ_ТОКЕН/setWebhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://ВАШ_ДОМЕН.vercel.app/api/webhook"}'
```

## Как развернуть

### 1. Установите переменные окружения

```bash
# Добавьте токен бота (для webhook.js)
vercel env add TELEGRAM_BOT_TOKEN

# Введите значение токена
# Выберите среды: Production, Preview, Development
```

### 2. Разверните проект

```bash
cd C:/Users/londo/.claude/skills/vercel-देплой/assets/examples/serverless-api

# Preview деплой
vercel

# Production деплой
vercel --prod
```

### 3. Проверьте работу

```bash
# Тестируем hello endpoint
curl https://ВАШ_ДОМЕН.vercel.app/api/hello

# Проверяем webhook (POST запрос)
curl -X POST https://ВАШ_ДОМЕН.vercel.app/api/webhook \
  -H "Content-Type: application/json" \
  -d '{"message": {"chat": {"id": 123}, "text": "test"}}'
```

## Логи и отладка

```bash
# Просмотр логов
vercel logs ВАШ_ДОМЕН.vercel.app

# Логи конкретной функции
vercel logs ВАШ_ДОМЕН.vercel.app --follow
```

## Особенности

- **Автоматическое масштабирование** - функции запускаются по требованию
- **Холодный старт** - первый запрос может быть медленнее
- **Timeout** - максимум 10 секунд для Hobby плана, 60 секунд для Pro
- **Размер** - максимум 50MB на функцию

## Расширение

### Добавить новый endpoint

1. Создайте файл `api/ваш-endpoint.js`
2. Экспортируйте handler функцию
3. Задеплойте: `vercel --prod`

### Использовать базу данных

```javascript
// Пример с MongoDB
import { MongoClient } from 'mongodb';

const client = new MongoClient(process.env.MONGODB_URI);

export default async function handler(req, res) {
  await client.connect();
  const db = client.db('mydb');
  const data = await db.collection('items').find().toArray();
  res.json(data);
}
```

### CORS настройки

```javascript
export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Ваша логика
}
```

## Полезные ссылки

- [Vercel Serverless Functions](https://vercel.com/docs/functions)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Environment Variables](https://vercel.com/docs/environment-variables)
