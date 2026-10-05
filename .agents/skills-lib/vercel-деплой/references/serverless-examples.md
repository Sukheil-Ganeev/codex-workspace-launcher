# Serverless Functions — Примеры кода

> Перенесено из SKILL.md секция 6: TypeScript, Python, Go, Webhook примеры

## Маршрутизация

```
your-project/
├── api/
│   ├── hello.js          → /api/hello
│   ├── users.js          → /api/users
│   └── products/
│       └── [id].js       → /api/products/[id]
├── public/
└── package.json
```

**Правила:**
- `api/hello.js` → доступен по `/api/hello`
- `api/users/index.js` → доступен по `/api/users`
- `api/products/[id].js` → динамический маршрут `/api/products/123`

---

## Node.js (JavaScript) — с параметрами

```javascript
// api/users.js
export default function handler(req, res) {
  const { method, query, body } = req;

  if (method === 'GET') {
    // GET /api/users?id=123
    const userId = query.id;
    res.status(200).json({ userId, name: 'John Doe' });
  } else if (method === 'POST') {
    // POST /api/users
    const { name, email } = body;
    res.status(201).json({ message: 'User created', name, email });
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}
```

---

## Node.js (TypeScript)

```typescript
// api/hello.ts
import { VercelRequest, VercelResponse } from '@vercel/node';

export default function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  res.status(200).json({ message: 'Hello from TypeScript!' });
}
```

**Установка типов:**
```bash
npm install --save-dev @vercel/node
```

---

## Python

```python
# api/hello.py
def handler(request):
    return {
        'statusCode': 200,
        'body': 'Hello from Python!'
    }
```

**С JSON:**
```python
# api/users.py
import json

def handler(request):
    data = {
        'users': [
            {'id': 1, 'name': 'John'},
            {'id': 2, 'name': 'Jane'}
        ]
    }
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(data)
    }
```

---

## Go

```go
// api/hello.go
package handler

import (
    "fmt"
    "net/http"
)

func Handler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello from Go!")
}
```

---

## Webhook обработка (Telegram пример)

### Простой webhook

```javascript
// api/telegram-webhook.js
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { message } = req.body;

  if (!message || !message.text) {
    return res.status(200).json({ ok: true });
  }

  // Обработка сообщения
  const chatId = message.chat.id;
  const text = message.text;

  console.log(`Received message from ${chatId}: ${text}`);

  // Отправка ответа через Telegram API
  const TELEGRAM_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
  const telegramApiUrl = `https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`;

  const response = await fetch(telegramApiUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: chatId,
      text: `You said: ${text}`
    })
  });

  const data = await response.json();

  return res.status(200).json({ ok: true, data });
}
```

### Продвинутый webhook с командами

```javascript
// api/telegram-bot.js
const TELEGRAM_TOKEN = process.env.TELEGRAM_BOT_TOKEN;

async function sendMessage(chatId, text) {
  const url = `https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`;
  await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: chatId, text })
  });
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { message } = req.body;

  if (!message) {
    return res.status(200).json({ ok: true });
  }

  const chatId = message.chat.id;
  const text = message.text || '';

  // Команды
  if (text.startsWith('/start')) {
    await sendMessage(chatId, 'Welcome to the bot!');
  } else if (text.startsWith('/help')) {
    await sendMessage(chatId, 'Available commands:\n/start - Start bot\n/help - Show help');
  } else {
    await sendMessage(chatId, `Echo: ${text}`);
  }

  return res.status(200).json({ ok: true });
}
```

**Установка webhook:**
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://your-app.vercel.app/api/telegram-webhook"
```

---

## Environment Variables в Functions

Функции автоматически получают доступ к environment variables:

```javascript
// api/config.js
export default function handler(req, res) {
  const apiKey = process.env.API_KEY;
  const dbUrl = process.env.DATABASE_URL;

  // НИКОГДА не отправляйте секреты клиенту!
  res.status(200).json({
    message: 'Config loaded',
    hasApiKey: !!apiKey,
    hasDbUrl: !!dbUrl
  });
}
```

**Добавление переменных:**
```bash
# Через CLI
vercel env add API_KEY

# Через Dashboard
Settings → Environment Variables → Add
```

**Типы переменных:**
- **Production:** Только для production deployments
- **Preview:** Только для preview deployments
- **Development:** Для локальной разработки (`vercel dev`)

---

## Limits и ограничения

| Параметр | Free Plan | Pro Plan | Enterprise |
|----------|-----------|----------|------------|
| **Execution Time** | 10s | 60s | 900s |
| **Memory** | 1024 MB | 3008 MB | 3008 MB |
| **Payload Size** | 5 MB | 5 MB | 5 MB |
| **Invocations** | 100 GB-Hrs | 1000 GB-Hrs | Custom |
| **Concurrent Executions** | 1000 | 1000 | Custom |

**Важные ограничения:**
- Холодный старт (cold start): 50-200ms
- Функции stateless (не сохраняют состояние между вызовами)
- Нет доступа к файловой системе (только /tmp)
- Максимальный размер функции: 50 MB (сжатый)

---

## Сравнение с Netlify Functions

| Параметр | Vercel Functions | Netlify Functions |
|----------|------------------|-------------------|
| **Runtime** | Node.js, Python, Go, Ruby | Node.js, Go |
| **Execution Time** | 10s-900s | 10s-26s* |
| **Memory** | 1024-3008 MB | 1024 MB |
| **Холодный старт** | 50-200ms | 100-300ms |
| **Структура** | `api/` папка | `netlify/functions/` |
| **Edge Functions** | Да | Да |
| **Background Functions** | Нет | Да (Pro+) |

*26s на Pro плане, 10s на Free

**Когда использовать Vercel Functions:**
- Проект на Next.js (оптимальная интеграция)
- Нужна высокая производительность
- Требуется поддержка нескольких языков
- Длительные операции (до 900s на Enterprise)

**Когда использовать Netlify Functions:**
- Нужны Background Functions (отложенные задачи)
- Используете Netlify экосистему
- Простые webhook обработчики
