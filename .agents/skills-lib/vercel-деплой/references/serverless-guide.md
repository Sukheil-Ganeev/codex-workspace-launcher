# Serverless Functions — Детальное руководство

## Введение

Serverless Functions в Vercel — это backend код, который выполняется по требованию (on-demand) без необходимости управлять серверами. Автоматический scaling, оплата за использование, нулевая конфигурация.

**Преимущества:**
- ✅ Нулевая конфигурация сервера
- ✅ Автоматический scaling
- ✅ Оплата за выполнение
- ✅ Глобальное распределение
- ✅ Встроенный CDN cache

**Ограничения:**
- ⚠️ Cold start (50-200ms)
- ⚠️ Timeout: 10 сек (Hobby), 60 сек (Pro)
- ⚠️ Stateless (нет постоянного хранилища)
- ⚠️ Memory: 1024 MB (Hobby), 3008 MB (Pro)

---

## Структура проекта

### Next.js проекты

```
pages/
  api/
    hello.js             → /api/hello
    user.js              → /api/user
    users/
      index.js           → /api/users
      [id].js            → /api/users/:id
      create.js          → /api/users/create
    posts/
      [...slug].js       → /api/posts/*
```

**Правила:**
- Файлы в `pages/api/` автоматически становятся API endpoints
- Имя файла = путь endpoint
- `[id].js` = dynamic route параметр
- `[...slug].js` = catch-all route

### Другие фреймворки

```
api/
  hello.js               → /api/hello
  user.js                → /api/user
  users/
    [id].js              → /api/users/:id
```

**Правила:**
- Файлы в `api/` папке
- Структура аналогична Next.js

### Именование файлов

```bash
# ✅ ПРАВИЛЬНО
api/hello.js
api/users/list.js
api/posts/[id].js

# ❌ НЕПРАВИЛЬНО
api/hello.ts.js          # двойное расширение
api/users/index.html     # неправильное расширение
api/.hidden.js           # скрытый файл
```

---

## Supported Languages

### Node.js (основной)

**Версии:** 18.x, 20.x (по умолчанию)

**Пример:**
```javascript
// api/hello.js
export default function handler(req, res) {
  res.status(200).json({ message: 'Hello from Node.js' })
}
```

**Настройка версии:**
```json
// package.json
{
  "engines": {
    "node": "20.x"
  }
}
```

### Python

**Версии:** 3.9, 3.11

**Пример:**
```python
# api/hello.py
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"message": "Hello from Python"}')
        return
```

**С Flask:**
```python
# api/app.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify(message='Hello from Flask')
```

**Зависимости:**
```txt
# requirements.txt
flask==3.0.0
requests==2.31.0
```

### Go

**Версии:** 1.x

**Пример:**
```go
// api/hello.go
package handler

import (
    "encoding/json"
    "net/http"
)

type Response struct {
    Message string `json:"message"`
}

func Handler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(Response{
        Message: "Hello from Go",
    })
}
```

**Зависимости:**
```
// go.mod
module example.com/api

go 1.21
```

### Ruby

**Версии:** 3.x

**Пример:**
```ruby
# api/hello.rb
require 'json'

Handler = Proc.new do |req, res|
  res.status = 200
  res['Content-Type'] = 'application/json'
  res.body = JSON.generate({ message: 'Hello from Ruby' })
end
```

**Зависимости:**
```ruby
# Gemfile
source 'https://rubygems.org'
gem 'sinatra'
```

---

## Примеры функций

### 1. Telegram Webhook

```javascript
// api/telegram-webhook.js
export default async function handler(req, res) {
  // Проверка метода
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const { message } = req.body

    // Обработка сообщения
    const chatId = message.chat.id
    const text = message.text

    // Отправка ответа в Telegram
    const TELEGRAM_TOKEN = process.env.TELEGRAM_TOKEN
    const response = await fetch(
      `https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          text: `Вы написали: ${text}`
        })
      }
    )

    const data = await response.json()
    res.status(200).json(data)
  } catch (error) {
    console.error('Error:', error)
    res.status(500).json({ error: error.message })
  }
}
```

**Настройка webhook:**
```bash
curl -X POST \
  "https://api.telegram.org/bot$TOKEN/setWebhook" \
  -d "url=https://your-app.vercel.app/api/telegram-webhook"
```

### 2. Обработка форм

```javascript
// api/contact-form.js
export default async function handler(req, res) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') {
    return res.status(200).end()
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const { name, email, message } = req.body

  // Валидация
  if (!name || !email || !message) {
    return res.status(400).json({ error: 'Missing required fields' })
  }

  try {
    // Отправка email через SendGrid
    const SENDGRID_API_KEY = process.env.SENDGRID_API_KEY

    const response = await fetch('https://api.sendgrid.com/v3/mail/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${SENDGRID_API_KEY}`
      },
      body: JSON.stringify({
        personalizations: [{
          to: [{ email: 'your-email@example.com' }]
        }],
        from: { email: 'noreply@example.com' },
        subject: `New contact from ${name}`,
        content: [{
          type: 'text/plain',
          value: `Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}`
        }]
      })
    })

    if (!response.ok) {
      throw new Error('Failed to send email')
    }

    res.status(200).json({ success: true, message: 'Email sent!' })
  } catch (error) {
    console.error('Error:', error)
    res.status(500).json({ error: 'Failed to send email' })
  }
}
```

### 3. Proxy API

```javascript
// api/proxy.js
export default async function handler(req, res) {
  const { url } = req.query

  if (!url) {
    return res.status(400).json({ error: 'URL parameter required' })
  }

  try {
    // Проксирование запроса
    const API_KEY = process.env.API_KEY

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
      }
    })

    const data = await response.json()

    // Кэширование на 1 минуту
    res.setHeader('Cache-Control', 's-maxage=60, stale-while-revalidate')
    res.status(200).json(data)
  } catch (error) {
    console.error('Error:', error)
    res.status(500).json({ error: error.message })
  }
}
```

**Использование:**
```
GET /api/proxy?url=https://api.example.com/data
```

### 4. Scheduled Functions (Cron)

**⚠️ Требует Pro план**

```javascript
// api/cleanup.js
export default async function handler(req, res) {
  // Проверка что вызов от Vercel Cron
  const authHeader = req.headers.authorization
  const CRON_SECRET = process.env.CRON_SECRET

  if (authHeader !== `Bearer ${CRON_SECRET}`) {
    return res.status(401).json({ error: 'Unauthorized' })
  }

  try {
    // Очистка старых данных
    console.log('Running cleanup...')

    // Ваша логика
    await cleanupOldData()

    res.status(200).json({ success: true, message: 'Cleanup completed' })
  } catch (error) {
    console.error('Error:', error)
    res.status(500).json({ error: error.message })
  }
}
```

**Настройка в vercel.json:**
```json
{
  "crons": [
    {
      "path": "/api/cleanup",
      "schedule": "0 0 * * *"
    }
  ]
}
```

**Cron формат:**
```
* * * * *
│ │ │ │ │
│ │ │ │ └─ День недели (0-7, 0=Sunday)
│ │ │ └─── Месяц (1-12)
│ │ └───── День месяца (1-31)
│ └─────── Час (0-23)
└───────── Минута (0-59)

Примеры:
0 0 * * *     → Каждый день в полночь
0 */6 * * *   → Каждые 6 часов
0 9 * * 1     → Каждый понедельник в 9:00
*/15 * * * *  → Каждые 15 минут
```

### 5. Image Processing

```javascript
// api/image-resize.js
import sharp from 'sharp'

export default async function handler(req, res) {
  const { url, width, height } = req.query

  if (!url) {
    return res.status(400).json({ error: 'URL required' })
  }

  try {
    // Скачать изображение
    const response = await fetch(url)
    const buffer = await response.arrayBuffer()

    // Resize
    const resized = await sharp(Buffer.from(buffer))
      .resize(parseInt(width) || 800, parseInt(height) || 600, {
        fit: 'cover'
      })
      .jpeg({ quality: 80 })
      .toBuffer()

    // Кэш на 1 день
    res.setHeader('Cache-Control', 's-maxage=86400, stale-while-revalidate')
    res.setHeader('Content-Type', 'image/jpeg')
    res.send(resized)
  } catch (error) {
    console.error('Error:', error)
    res.status(500).json({ error: error.message })
  }
}
```

**package.json:**
```json
{
  "dependencies": {
    "sharp": "^0.33.0"
  }
}
```

---

## Environment Variables в Functions

### Серверные переменные (только API)

```javascript
// api/private.js
export default function handler(req, res) {
  const dbUrl = process.env.DATABASE_URL
  const apiKey = process.env.API_KEY

  // ✅ Доступны только на сервере
  res.json({ hasDb: !!dbUrl, hasKey: !!apiKey })
}
```

### Клиентские переменные (Next.js)

```javascript
// pages/index.js
export default function Home() {
  // Префикс NEXT_PUBLIC_ для клиента
  const apiUrl = process.env.NEXT_PUBLIC_API_URL

  return <div>API URL: {apiUrl}</div>
}
```

### Добавление переменных

```bash
# Через CLI
vercel env add DATABASE_URL production
vercel env add API_KEY production preview development

# Через Dashboard
# Settings → Environment Variables
```

### Локальное использование

```bash
# Скачать переменные
vercel env pull .env.local

# Использовать в dev
vercel dev
```

---

## Limits и ограничения

### Free Tier (Hobby)

| Параметр | Значение |
|----------|----------|
| **Execution time** | 10 секунд |
| **Memory** | 1024 MB |
| **Payload size** | 4.5 MB (request body) |
| **Response size** | 4.5 MB |
| **Concurrent executions** | 100 |
| **Regions** | 1 (auto) |
| **Monthly execution** | 100 GB-Hours |

### Pro Plan

| Параметр | Значение |
|----------|----------|
| **Execution time** | 60 секунд (300 сек max) |
| **Memory** | 1024-3008 MB |
| **Payload size** | 4.5 MB |
| **Response size** | 4.5 MB |
| **Concurrent executions** | 1000 |
| **Regions** | Выбор нескольких |
| **Monthly execution** | 1000 GB-Hours |

### Streaming Responses

```javascript
// api/stream.js
export default function handler(req, res) {
  res.setHeader('Content-Type', 'text/event-stream')
  res.setHeader('Cache-Control', 'no-cache')
  res.setHeader('Connection', 'keep-alive')

  let count = 0
  const interval = setInterval(() => {
    res.write(`data: ${JSON.stringify({ count: count++ })}\n\n`)

    if (count > 10) {
      clearInterval(interval)
      res.end()
    }
  }, 1000)

  req.on('close', () => {
    clearInterval(interval)
    res.end()
  })
}
```

**⚠️ Ограничения streaming:**
- Максимум 60 секунд (Pro план)
- Нет гарантии доставки
- Не работает через CDN cache

---

## Best Practices

### 1. Cold Starts оптимизация

```javascript
// ❌ ПЛОХО — импорт тяжёлой библиотеки в каждом запросе
export default async function handler(req, res) {
  const AWS = require('aws-sdk')
  const s3 = new AWS.S3()
  // ...
}

// ✅ ХОРОШО — импорт на уровне модуля
const AWS = require('aws-sdk')
const s3 = new AWS.S3()

export default async function handler(req, res) {
  // ...
}
```

**Оптимизация:**
- Минимизировать размер функции
- Lazy import только нужных модулей
- Использовать Edge Functions для latency-critical кода

### 2. Error Handling

```javascript
// api/robust.js
export default async function handler(req, res) {
  try {
    // Валидация
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' })
    }

    // Парсинг body
    const { data } = req.body
    if (!data) {
      return res.status(400).json({ error: 'Missing data' })
    }

    // Бизнес-логика
    const result = await processData(data)

    // Успех
    res.status(200).json({ success: true, result })
  } catch (error) {
    // Логирование
    console.error('Error in /api/robust:', error)

    // Ответ клиенту
    res.status(500).json({
      error: 'Internal server error',
      message: error.message,
      // Не отправляйте stack trace в production!
      ...(process.env.NODE_ENV === 'development' && { stack: error.stack })
    })
  }
}
```

### 3. Logging

```javascript
// api/logged.js
export default async function handler(req, res) {
  const requestId = crypto.randomUUID()

  console.log(`[${requestId}] Request received:`, {
    method: req.method,
    url: req.url,
    headers: req.headers
  })

  try {
    const result = await processRequest(req)

    console.log(`[${requestId}] Success:`, result)
    res.status(200).json(result)
  } catch (error) {
    console.error(`[${requestId}] Error:`, error)
    res.status(500).json({ error: error.message })
  }
}
```

**Просмотр логов:**
```bash
vercel logs --follow
vercel logs --filter="/api/logged"
```

### 4. Кэширование

```javascript
// api/cached.js
export default async function handler(req, res) {
  const data = await fetchData()

  // Cache на CDN edge на 60 секунд
  res.setHeader('Cache-Control', 's-maxage=60, stale-while-revalidate')
  res.status(200).json(data)
}
```

**Стратегии кэширования:**
```javascript
// Без кэша
'Cache-Control': 'no-cache, no-store, must-revalidate'

// 1 минута
'Cache-Control': 's-maxage=60'

// 1 час + stale-while-revalidate
'Cache-Control': 's-maxage=3600, stale-while-revalidate=86400'

// Навсегда (immutable)
'Cache-Control': 's-maxage=31536000, immutable'
```

### 5. Database Connections

```javascript
// lib/db.js
import { Pool } from 'pg'

let pool

export function getPool() {
  if (!pool) {
    pool = new Pool({
      connectionString: process.env.DATABASE_URL,
      max: 1, // Важно: 1 connection per function!
      idleTimeoutMillis: 30000
    })
  }
  return pool
}

// api/users.js
import { getPool } from '../lib/db'

export default async function handler(req, res) {
  const pool = getPool()

  try {
    const result = await pool.query('SELECT * FROM users LIMIT 10')
    res.status(200).json(result.rows)
  } catch (error) {
    console.error('DB Error:', error)
    res.status(500).json({ error: 'Database error' })
  }
}
```

**⚠️ Важно:**
- Использовать connection pooling
- 1 connection per function (max)
- Использовать serverless-friendly БД (Planetscale, Supabase, Neon)

---

## Сравнение с Netlify Functions

| Параметр | Vercel | Netlify |
|----------|---------|---------|
| **Структура** | `/api` или `/pages/api` | `/netlify/functions` |
| **Формат** | Node.js export default | exports.handler |
| **Языки** | Node, Python, Go, Ruby | Node, Go |
| **Timeout (free)** | 10 секунд | 10 секунд |
| **Timeout (pro)** | 60 секунд | 26 секунд |
| **Memory** | 1024 MB | 1024 MB |
| **Cold start** | 50-100ms | 100-200ms |
| **Dynamic routes** | ✅ `[id].js` | ❌ Manual routing |
| **Edge Functions** | ✅ Мощные | ⚠️ Ограничено (Deno) |

**Победитель:** ✅ Vercel (лучше DX, быстрее, больше возможностей)

---

**Больше информации:**
- **FAQ:** `faq.md`
- **Troubleshooting:** `troubleshooting.md`
- **Vercel vs Netlify:** `vercel-vs-netlify.md`
