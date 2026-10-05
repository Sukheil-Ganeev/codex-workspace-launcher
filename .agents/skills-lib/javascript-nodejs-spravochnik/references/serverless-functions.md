# Serverless Functions

Полный справочник по работе с бессерверными функциями в JavaScript/Node.js. Охватывает Netlify Functions, Vercel Functions и основные паттерны развёртывания.

---

## 1. Netlify Functions Setup

Netlify Functions позволяет создавать бессерверные функции без управления инфраструктурой.

### Установка и конфигурация

```bash
# Инициализация проекта
npm init -y
npm install -D netlify-cli

# Логин в Netlify
netlify login

# Создание структуры
mkdir -p netlify/functions
```

### netlify.toml конфигурация

```toml
[build]
  command = "npm run build"
  functions = "netlify/functions"
  publish = "dist"

[dev]
  functions = "netlify/functions"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

### Локальное тестирование

```bash
# Запускdev сервера
netlify dev

# Функции доступны по адресу:
# http://localhost:8888/.netlify/functions/функция-name
```

---

## 2. Vercel Functions (API Routes)

Vercel Functions встроены в Next.js и предоставляют файловый роутинг для API.

### Структура проекта Next.js

```
pages/
├── api/
│   ├── hello.js              # GET http://localhost:3000/api/hello
│   ├── users/
│   │   ├── [id].js          # GET http://localhost:3000/api/users/123
│   │   └── index.js         # GET http://localhost:3000/api/users
│   └── webhooks/
│       └── payment.js        # POST для вебхуков
├── index.js
└── ...
```

### Базовый маршрут

```javascript
// pages/api/hello.js
export default function handler(req, res) {
  if (req.method === 'GET') {
    res.status(200).json({ message: 'Hello World' });
  } else {
    res.status(405).end();
  }
}
```

### Динамические маршруты

```javascript
// pages/api/users/[id].js
export default function handler(req, res) {
  const { id } = req.query;

  if (req.method === 'GET') {
    // Получить пользователя по ID
    res.status(200).json({ id, name: `User ${id}` });
  } else if (req.method === 'PUT') {
    // Обновить пользователя
    res.status(200).json({ id, updated: true });
  } else if (req.method === 'DELETE') {
    // Удалить пользователя
    res.status(204).end();
  } else {
    res.status(405).end();
  }
}
```

---

## 3. Function Structure и Handler

### Общая структура функции

```javascript
// netlify/functions/process-booking.js или pages/api/booking.js

/**
 * Обработка бронирований
 * HTTP метод: POST
 * Возвращает: { success: boolean, bookingId: string }
 */
export async function handler(event, context) {
  // Для Netlify используется (event, context)
  // Для Vercel: (req, res)

  try {
    // Валидация метода
    if (event.httpMethod !== 'POST') {
      return {
        statusCode: 405,
        body: JSON.stringify({ error: 'Method not allowed' })
      };
    }

    // Парсинг тела запроса
    const data = JSON.parse(event.body);

    // Валидация данных
    if (!data.email || !data.date) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Missing required fields' })
      };
    }

    // Бизнес-логика
    const bookingId = await createBooking(data);

    // Успешный ответ
    return {
      statusCode: 201,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        success: true,
        bookingId,
        message: 'Booking created successfully'
      })
    };

  } catch (error) {
    console.error('Booking error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal server error' })
    };
  }
}

async function createBooking(data) {
  // Имитация сохранения в БД
  return `booking_${Date.now()}`;
}
```

### Для Vercel (Next.js)

```javascript
// pages/api/booking.js
export default async function handler(req, res) {
  // Проверка метода
  if (req.method !== 'POST') {
    return res.status(405).end();
  }

  try {
    const { email, date } = req.body;

    if (!email || !date) {
      return res.status(400).json({ error: 'Missing fields' });
    }

    const bookingId = await createBooking({ email, date });

    res.status(201).json({
      success: true,
      bookingId
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

async function createBooking(data) {
  return `booking_${Date.now()}`;
}
```

---

## 4. Environment Variables в Serverless

### Netlify: netlify.toml

```toml
[build]
  environment = { NODE_ENV = "production" }

[functions]
  node_bundler = "esbuild"

[build.environment]
  API_KEY = "sk_live_123456"
  DATABASE_URL = "postgres://..."
```

Или через UI: **Site settings → Build & deploy → Environment**.

### Vercel: vercel.json или .env.local

```json
{
  "env": {
    "STRIPE_SECRET_KEY": "@stripe_secret",
    "DATABASE_URL": "@db_url"
  }
}
```

```bash
# .env.local (локальное окружение)
STRIPE_SECRET_KEY=sk_test_123456
DATABASE_URL=postgres://localhost/mydb
WEBHOOK_SECRET=whsec_123456
```

### Доступ к переменным в функции

```javascript
// Netlify
export async function handler(event, context) {
  const apiKey = process.env.API_KEY;
  const dbUrl = process.env.DATABASE_URL;
  // ...
}

// Vercel/Next.js
export default async function handler(req, res) {
  const apiKey = process.env.STRIPE_SECRET_KEY;
  const dbUrl = process.env.DATABASE_URL;
  // ...
}
```

### Секреты и Best Practices

```javascript
// netlify/functions/payment-handler.js

// ✅ ПРАВИЛЬНО: Использовать переменные окружения
const STRIPE_KEY = process.env.STRIPE_SECRET_KEY;

// ❌ НЕПРАВИЛЬНО: Жёсткодировать секреты
const STRIPE_KEY = 'sk_live_123456';

// ✅ ПРАВИЛЬНО: Валидировать наличие переменной
if (!process.env.WEBHOOK_SECRET) {
  throw new Error('WEBHOOK_SECRET not configured');
}
```

---

## 5. Cold Starts Optimization

### Что такое Cold Start?

Первый запрос к функции требует времени на инициализацию (обычно 0,5-5 сек).

### Стратегии оптимизации

#### a) Минимизация зависимостей

```javascript
// ❌ МЕДЛЕННО: Импортируем всё подряд
import _ from 'lodash';
import axios from 'axios';
import moment from 'moment';

export async function handler(event) {
  // Используем только 10% функциональности
  const arr = _.chunk([1,2,3], 1);
}

// ✅ БЫСТРО: Импортируем только нужное
import chunk from 'lodash/chunk';

export async function handler(event) {
  const arr = chunk([1,2,3], 1);
}
```

#### b) Lazy loading зависимостей

```javascript
// netlify/functions/heavy-processing.js

let ffmpeg; // Инициализируем при необходимости

export async function handler(event) {
  // Загружаем тяжёлый модуль только при первом использовании
  if (!ffmpeg) {
    ffmpeg = require('fluent-ffmpeg');
  }

  // Используем ffmpeg
  return {
    statusCode: 200,
    body: JSON.stringify({ processed: true })
  };
}
```

#### c) Connection Pooling

```javascript
// netlify/functions/db-query.js

let db; // Переиспользуем подключение

export async function handler(event) {
  // Первый запрос: создаём подключение
  if (!db) {
    db = await connectToDatabase({
      connectionString: process.env.DATABASE_URL
    });
  }

  // Последующие запросы: переиспользуют существующее подключение
  const result = await db.query('SELECT * FROM users');

  return {
    statusCode: 200,
    body: JSON.stringify(result)
  };
}
```

#### d) Warmup функции

```bash
# Запланировать периодический вызов функции (каждые 5 минут)
# Netlify: Site settings → Scheduled Functions

# Или создать собственный cronjob
0 * * * * curl https://your-site/.netlify/functions/warmup
```

---

## 6. Webhooks Processing

### Пример: Обработка вебхука платежа (Stripe)

```javascript
// netlify/functions/webhook-payment.js

const crypto = require('crypto');

// Подпись вебхука проверяется с помощью HMAC
function verifyStripeSignature(body, signature, secret) {
  const hash = crypto
    .createHmac('sha256', secret)
    .update(body)
    .digest('hex');

  return signature === `t0=${hash}` || signature.includes(hash);
}

export async function handler(event) {
  // Проверяем, что это POST запрос
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405 };
  }

  try {
    // Получаем заголовок подписи
    const signature = event.headers['stripe-signature'];
    const body = event.body;

    // Верифицируем подпись
    if (!verifyStripeSignature(body, signature, process.env.STRIPE_WEBHOOK_SECRET)) {
      return {
        statusCode: 403,
        body: JSON.stringify({ error: 'Invalid signature' })
      };
    }

    // Парсим событие
    const stripeEvent = JSON.parse(body);

    // Обрабатываем разные типы событий
    switch (stripeEvent.type) {
      case 'payment_intent.succeeded':
        await handlePaymentSuccess(stripeEvent.data.object);
        break;

      case 'payment_intent.payment_failed':
        await handlePaymentFailure(stripeEvent.data.object);
        break;

      case 'customer.subscription.updated':
        await handleSubscriptionUpdate(stripeEvent.data.object);
        break;

      default:
        console.log(`Unhandled event type: ${stripeEvent.type}`);
    }

    return {
      statusCode: 200,
      body: JSON.stringify({ received: true })
    };

  } catch (error) {
    console.error('Webhook error:', error);
    return {
      statusCode: 400,
      body: JSON.stringify({ error: error.message })
    };
  }
}

async function handlePaymentSuccess(paymentIntent) {
  console.log('Payment successful:', paymentIntent.id);
  // Обновить заказ в БД
  // Отправить email пользователю
  // Запустить экспорт в CRM
}

async function handlePaymentFailure(paymentIntent) {
  console.log('Payment failed:', paymentIntent.id);
  // Уведомить пользователя
  // Запланировать повторный платёж
}

async function handleSubscriptionUpdate(subscription) {
  console.log('Subscription updated:', subscription.id);
  // Обновить план пользователя
}
```

### Пример: Обработка вебхука бронирования

```javascript
// netlify/functions/webhook-booking.js

export async function handler(event) {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405 };
  }

  try {
    const booking = JSON.parse(event.body);

    // Валидация
    if (!booking.id || !booking.email || !booking.tourDate) {
      throw new Error('Invalid booking data');
    }

    // Логирование
    console.log(`New booking: ${booking.id} for ${booking.email}`);

    // 1. Сохранить в БД
    await saveBookingToDatabase(booking);

    // 2. Отправить подтверждение email
    await sendConfirmationEmail(booking.email, booking);

    // 3. Экспортировать в CRM (если настроен)
    if (process.env.CRM_WEBHOOK) {
      await notifyCRM(booking);
    }

    return {
      statusCode: 200,
      body: JSON.stringify({
        success: true,
        bookingId: booking.id
      })
    };

  } catch (error) {
    console.error('Booking webhook error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
}

async function saveBookingToDatabase(booking) {
  // Имитация сохранения
  console.log('Saving booking to DB:', booking.id);
}

async function sendConfirmationEmail(email, booking) {
  // Использование SendGrid, Mailgun или аналога
  console.log(`Sending confirmation to ${email}`);
}

async function notifyCRM(booking) {
  // POST в CRM систему
  const response = await fetch(process.env.CRM_WEBHOOK, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(booking)
  });
  return response.json();
}
```

---

## 7. Deployment

### Netlify Deploy

```bash
# 1. Подключить репозиторий
netlify link

# 2. Автоматический deploy из Git
git push origin main
# Netlify автоматически разворачивает при push

# 3. Ручной deploy
netlify deploy --prod

# 4. Перед deploy установить зависимости
# Автоматически в netlify.toml:
[build]
  command = "npm ci && npm run build"
```

### Vercel Deploy

```bash
# 1. Установить CLI
npm install -g vercel

# 2. Deploy из каталога
vercel --prod

# 3. Автоматический deploy из GitHub
# Подключите репо в https://vercel.com/dashboard
git push origin main
# Vercel автоматически разворачивает

# 4. Окружение для production
# vercel.json
{
  "env": {
    "STRIPE_SECRET_KEY": "@stripe_secret_key"
  },
  "builds": [
    { "src": "pages/api/**/*.js", "use": "@vercel/node" }
  ]
}
```

### Environment переменные при deploy

#### Netlify

```bash
# Через CLI
netlify env:set API_KEY "sk_live_123456"
netlify env:set DATABASE_URL "postgres://..."

# Через UI: Site settings → Build & deploy → Environment
```

#### Vercel

```bash
# Через CLI
vercel env add API_KEY
# Введите значение

# Или через UI: Project Settings → Environment Variables
```

### Проверка функций после deploy

```bash
# Netlify (продакшн)
curl https://your-site.netlify.app/.netlify/functions/hello

# Vercel (продакшн)
curl https://your-project.vercel.app/api/hello

# Со скриптом для проверки
npm run test:serverless
```

---

## Сводка команд

| Задача | Netlify | Vercel |
|--------|---------|--------|
| Инициализация | `netlify init` | `vercel` |
| Локальный запуск | `netlify dev` | `npm run dev` |
| Deploy | `netlify deploy --prod` | `vercel --prod` |
| Переменные окружения | `netlify env:set KEY VALUE` | `vercel env add KEY` |
| Логи функций | `netlify logs` | `vercel logs` |
| Удалить функцию | Удалить файл + deploy | Удалить файл + deploy |

---

## Полезные ссылки

- [Netlify Functions Docs](https://docs.netlify.com/functions/overview/)
- [Vercel Serverless Functions](https://vercel.com/docs/concepts/functions/serverless-functions)
- [Next.js API Routes](https://nextjs.org/docs/api-routes/introduction)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
