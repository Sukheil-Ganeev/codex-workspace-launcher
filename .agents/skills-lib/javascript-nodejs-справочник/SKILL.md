---
name: javascript-nodejs-справочник
description: "Use when building serverless functions, REST APIs, or backend logic - covers modern JavaScript ES6+, Node.js runtime, Express, database integration, authentication, and production deployment"
---
# JavaScript & Node.js Production Справочник

**Версия:** 1.0
**Последнее обновление:** 2026-02-04
**Уровень:** Продвинутый (Production-ready)
**Охват:** Serverless + Full Stack Node.js

---

## 1. Введение и философия

### Что такое современный JavaScript/Node.js stack

JavaScript эволюционировал от простого языка для анимаций на веб-страницах до полноценной платформы для создания масштабируемых серверных приложений. **Node.js** — это runtime, который позволяет запускать JavaScript на сервере, используя движок V8 от Google Chrome.

**Ключевые концепции:**

- **Event-driven архитектура**: Node.js основан на событийной модели, где операции выполняются асинхронно
- **Non-blocking I/O**: Операции ввода-вывода не блокируют выполнение кода
- **Single-threaded Event Loop**: Один поток обрабатывает множество запросов параллельно
- **NPM экосистема**: Крупнейший реестр пакетов с миллионами готовых решений

```javascript
// Философия Node.js: асинхронность и неблокирующий код
const http = require('http');

const server = http.createServer((req, res) => {
  // Каждый запрос обрабатывается асинхронно
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Hello World');
});

server.listen(3000);
// Сервер продолжает работать, обрабатывая тысячи запросов
```

### Serverless vs Traditional Server: когда что использовать

**Serverless (Functions as a Service):**
- **Когда использовать**: API endpoints, webhooks, scheduled tasks, event processing
- **Преимущества**: Zero infrastructure management, automatic scaling, pay-per-use
- **Ограничения**: Cold starts, execution time limits (обычно 10-30 сек), stateless
- **Платформы**: Netlify Functions, Vercel Functions, AWS Lambda, Google Cloud Functions

**Traditional Server (Full Stack):**
- **Когда использовать**: Complex applications, WebSockets, long-running processes, full control
- **Преимущества**: No time limits, persistent connections, full customization
- **Ограничения**: Infrastructure management, scaling complexity, fixed costs
- **Платформы**: VPS (DigitalOcean, Linode), PaaS (Heroku, Railway), Containers (Docker, Kubernetes)

**Сравнительная таблица:**

| Критерий | Serverless | Traditional Server |
|----------|-----------|-------------------|
| Setup time | Минуты | Часы/дни |
| Scaling | Автоматический | Ручной/полуавтоматический |
| Cost | Pay-per-execution | Fixed monthly |
| Cold starts | Да (100-500ms) | Нет |
| Execution time | 10-30 сек | Неограничено |
| WebSockets | Ограниченно | Полная поддержка |
| Ideal for | API, webhooks, cron | Full apps, real-time |

### Production-ready подход

Разработка production-ready приложений требует внимания к:

1. **Безопасность**: Input validation, SQL injection prevention, CORS, rate limiting, secrets management
2. **Производительность**: Caching, database indexing, query optimization, CDN
3. **Надёжность**: Error handling, logging, monitoring, health checks, graceful shutdown
4. **Масштабируемость**: Horizontal scaling, load balancing, stateless design
5. **Поддерживаемость**: Code quality, tests, documentation, CI/CD

### Для кого этот справочник

**Целевая аудитория:**
- Разработчики с базовыми знаниями JavaScript (ES6+)
- Frontend разработчики, желающие освоить backend
- Разработчики, переходящие на Node.js с других языков
- Предприниматели в туризме, создающие собственные системы бронирования

**Что вы получите:**
- 8 модульных справочников по ключевым темам
- 15 готовых шаблонов для быстрого старта
- 15 полных рабочих примеров с тестами (с фокусом на туристический бизнес)
- 12 production-ready скриптов для автоматизации

---

## 2. Quick Start Guide

### Сценарий А: Serverless Function за 5 минут

**Задача**: Создать функцию для обработки формы бронирования экскурсий

**Шаги:**

1. **Создайте структуру проекта:**
```bash
mkdir booking-api-dubai
cd booking-api-dubai
npm init -y
mkdir netlify
mkdir netlify/functions
```

2. **Скопируйте шаблон:**
```bash
# Копируйте из assets/templates/serverless-function-template.js
# в netlify/functions/booking.js
```

3. **Настройте environment variables:**
```bash
# Создайте .env файл
echo "SENDGRID_API_KEY=your_api_key" > .env
echo "ADMIN_EMAIL=suheil@dubai-tours.ae" >> .env
echo "WHATSAPP_API_KEY=your_whatsapp_key" >> .env
```

4. **Тестируйте локально:**
```bash
npm install -g netlify-cli
netlify dev
```

5. **Деплой:**
```bash
netlify deploy --prod
```

**Готово!** Ваша функция доступна по адресу:
`https://yoursite.netlify.app/.netlify/functions/booking`

**Пример запроса:**
```javascript
// Отправка с сайта бронирования
const response = await fetch('/.netlify/functions/booking', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Ahmed Al-Mansoori',
    email: 'ahmed@example.com',
    phone: '+971501234567',
    tour: 'Desert Safari Premium',
    date: '2026-03-15',
    guests: 4,
    language: 'ru'
  })
});

const result = await response.json();
// { success: true, bookingId: 'BK-20260315-A4F2' }
```

### Сценарий Б: Express REST API за 10 минут

**Задача**: Создать REST API для управления экскурсиями и бронированиями

**Шаги:**

1. **Инициализация:**
```bash
mkdir tours-api
cd tours-api
npm init -y
npm install express dotenv cors helmet morgan
```

2. **Скопируйте базовый шаблон:**
```bash
# Копируйте assets/templates/express-server-template.js в index.js
```

3. **Настройте .env:**
```bash
cat > .env << EOF
PORT=3000
NODE_ENV=development
ALLOWED_ORIGINS=https://dubai-tours.ae,http://localhost:3000
DATABASE_URL=postgresql://user:pass@localhost:5432/tours_db
JWT_SECRET=your_jwt_secret_key_here
EOF
```

4. **Добавьте routes для туров** (`routes/tours.js`):
   Создайте CRUD routes: GET `/` (все туры), GET `/:id` (тур по ID), POST `/:id/book` (бронирование с валидацией).
   → Подробные примеры routes с кодом: `references/express-api.md` (секция "REST Routes")

5. **Подключите роуты в index.js:**
```javascript
const toursRouter = require('./routes/tours');
app.use('/api/tours', toursRouter);
```

6. **Запустите сервер:**
```bash
node index.js
# Сервер запущен на http://localhost:3000
# Протестируйте: curl http://localhost:3000/api/tours
```

### Сценарий В: Production Full Stack за 30 минут

**Задача**: Развернуть полноценное приложение с базой данных PostgreSQL для туристического агентства

**Шаги:**

1. **Скопируйте готовый пример:**
```bash
cp -r assets/examples/04-express-rest-api dubai-tours-backend
cd dubai-tours-backend
```

2. **Установите зависимости:**
```bash
npm install
```

3. **Настройте базу данных:**
```bash
# Создайте PostgreSQL database
createdb dubai_tours_db

# Скопируйте .env.example в .env
cp .env.example .env

# Заполните DATABASE_URL в .env:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/dubai_tours_db
```

4. **Запустите миграции:**
```bash
npm run migrate
# Создаст таблицы: users, tours, bookings, payments

npm run seed
# Заполнит начальными данными (популярные туры в Дубае)
```

5. **Тестируйте:**
```bash
npm test
# Все тесты должны пройти (API endpoints, database CRUD)
```

6. **Запустите в dev режиме:**
```bash
npm run dev
# Сервер с hot reload на http://localhost:3000
```

7. **Деплой на production:**
```bash
npm run build
npm run deploy
# Railway / Heroku / DigitalOcean
```

**API Endpoints готовы к использованию:**
- `GET /api/tours` - Список всех туров
- `GET /api/tours/:id` - Детали тура
- `POST /api/tours/:id/book` - Создать бронирование
- `GET /api/bookings` - Все бронирования (admin)
- `POST /api/auth/register` - Регистрация
- `POST /api/auth/login` - Вход

---

## 3. Навигация по модулям

### Модули references (8 справочников)

| Модуль | Размер | Описание | Когда использовать |
|--------|--------|----------|-------------------|
| **javascript-fundamentals.md** | 1200 слов | ES6+, async/await, modules, functional programming | Освежить знания современного JS, изучить новые возможности |
| **nodejs-basics.md** | 1000 слов | Runtime, npm, core modules (fs, http, path), process | Начало работы с Node.js, понимание основ платформы |
| **express-api.md** | 1400 слов | REST API, routing, middleware, validation | Создание backend API, веб-серверов для туристических сайтов |
| **serverless-functions.md** | 1200 слов | Netlify/Vercel/AWS Lambda functions | Быстрые API для форм бронирования без управления серверами |
| **database-integration.md** | 1000 слов | PostgreSQL, MongoDB, Sequelize, Mongoose | Работа с базами данных туров, клиентов, бронирований |
| **authentication.md** | 1200 слов | JWT, OAuth 2.0, sessions, password hashing | Авторизация туристов и администраторов, защита API |
| **error-handling.md** | 800 слов | Error classes, global handlers, logging | Production stability, debugging, мониторинг сбоев |
| **testing-deployment.md** | 1000 слов | Jest, Supertest, CI/CD, deployment | Тестирование API, автоматизация деплоя |

### Рекомендуемые пути обучения

**Путь 1: Начинающий (Serverless-first)**
1. `javascript-fundamentals.md` - Современный JavaScript ES6+
2. `nodejs-basics.md` - Основы Node.js
3. `serverless-functions.md` - Создание первых API для форм
4. `error-handling.md` - Обработка ошибок
5. `testing-deployment.md` - Тестирование и деплой

**Путь 2: Опытный (Full Stack)**
1. `express-api.md` - Express сервер и REST API
2. `database-integration.md` - Подключение PostgreSQL для туров
3. `authentication.md` - Аутентификация клиентов и админов
4. `error-handling.md` - Production error handling
5. `testing-deployment.md` - Полный CI/CD pipeline

**Путь 3: Production (Best Practices)**
1. `error-handling.md` - Централизованная обработка ошибок
2. `authentication.md` - Безопасная авторизация с JWT
3. Изучить все templates для best practices
4. Применить security-audit.js скрипт
5. Настроить monitoring и logging (Sentry, Winston)

---

## 4. Templates & Examples

### 15 Production-Ready Templates

#### 1. serverless-function-template.js
**Назначение**: Boilerplate для Netlify/Vercel functions
**Включает**: CORS, env variables, error handling, validation
**Использование**: API endpoints для форм бронирования, webhooks от payment providers
**Копировать в**: `netlify/functions/` или `api/`

**Пример для туризма:**
```javascript
// netlify/functions/tour-booking.js
exports.handler = async (event) => {
  const { tour, date, guests, name, email, phone } = JSON.parse(event.body);

  // Валидация
  if (!tour || !date || !guests) {
    return { statusCode: 400, body: JSON.stringify({ error: 'Missing data' }) };
  }

  // Создать бронирование
  const bookingId = `BK-${Date.now()}`;

  // Отправить email подтверждение
  await sendConfirmationEmail(email, bookingId);

  return {
    statusCode: 200,
    body: JSON.stringify({ success: true, bookingId })
  };
};
```

#### 2. express-server-template.js
**Назначение**: Базовый Express сервер
**Включает**: Middleware (helmet, cors, morgan), error handling, health check
**Использование**: Starting point для API туристического сайта
**Копировать в**: `server.js` или `index.js`

#### 3. rest-api-route.js
**Назначение**: CRUD операции для одного ресурса
**Включает**: GET/POST/PUT/DELETE routes, validation
**Использование**: API routes для tours, bookings, customers, payments
**Копировать в**: `routes/resource-name.js`

**Пример:**
```javascript
// routes/bookings.js - управление бронированиями
router.get('/', authMiddleware, async (req, res) => {
  const bookings = await Booking.findAll({ where: { userId: req.user.id } });
  res.json(bookings);
});

router.post('/', async (req, res) => {
  const { tourId, date, guests, customerInfo } = req.body;
  const booking = await Booking.create({ tourId, date, guests, customerInfo });
  res.status(201).json(booking);
});
```

#### 4. middleware-template.js
**Назначение**: Custom middleware boilerplate
**Включает**: Authentication, logging, rate limiting примеры
**Использование**: Защита admin роутов, rate limiting для публичного API
**Копировать в**: `middleware/`

#### 5. database-model.js
**Назначение**: Database model/schema
**Включает**: Sequelize и Mongoose примеры, validation, methods
**Использование**: Tour, Booking, Customer, Payment models
**Копировать в**: `models/`

**Пример Tour model:**
```javascript
// models/Tour.js
const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  const Tour = sequelize.define('Tour', {
    name: {
      type: DataTypes.STRING,
      allowNull: false
    },
    description: DataTypes.TEXT,
    duration: DataTypes.STRING, // "6 hours"
    price_aed: {
      type: DataTypes.DECIMAL(10, 2),
      allowNull: false
    },
    price_usd: {
      type: DataTypes.DECIMAL(10, 2),
      allowNull: false
    },
    max_guests: DataTypes.INTEGER,
    available: {
      type: DataTypes.BOOLEAN,
      defaultValue: true
    },
    category: {
      type: DataTypes.ENUM('desert', 'city', 'water', 'cultural', 'adventure'),
      allowNull: false
    }
  });

  return Tour;
};
```

#### 6. jwt-auth-template.js
**Назначение**: JWT authentication система
**Включает**: Token generation, verification, refresh tokens
**Использование**: Login/logout/register для клиентов и админов
**Копировать в**: `utils/auth.js`

#### 7. webhook-handler.js
**Назначение**: Обработка внешних webhooks
**Включает**: Signature verification (Stripe, Paddle), retry logic
**Использование**: Payment confirmations от Stripe/PayPal, WhatsApp Business API webhooks
**Копировать в**: `webhooks/`

**Пример для Stripe:**
```javascript
// webhooks/stripe.js
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

exports.handler = async (event) => {
  const sig = event.headers['stripe-signature'];

  let stripeEvent;
  try {
    stripeEvent = stripe.webhooks.constructEvent(
      event.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    return { statusCode: 400, body: 'Webhook signature verification failed' };
  }

  if (stripeEvent.type === 'payment_intent.succeeded') {
    const paymentIntent = stripeEvent.data.object;
    // Обновить бронирование на "paid"
    await Booking.update(
      { status: 'paid', paymentId: paymentIntent.id },
      { where: { stripePaymentIntentId: paymentIntent.id } }
    );
  }

  return { statusCode: 200, body: 'Success' };
};
```

#### 8. email-sender.js
**Назначение**: Email отправка через Nodemailer/SendGrid
**Включает**: Templates, attachments, error handling
**Использование**: Booking confirmations, tour reminders, newsletters
**Копировать в**: `utils/email.js`

**Пример:**
```javascript
// utils/email.js
const sgMail = require('@sendgrid/mail');
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

async function sendBookingConfirmation(booking) {
  const msg = {
    to: booking.customerEmail,
    from: 'bookings@dubai-tours.ae',
    subject: `Booking Confirmation - ${booking.tourName}`,
    html: `
      <h1>Your booking is confirmed!</h1>
      <p>Booking ID: ${booking.id}</p>
      <p>Tour: ${booking.tourName}</p>
      <p>Date: ${booking.date}</p>
      <p>Guests: ${booking.guests}</p>
      <p>Total: ${booking.totalPrice} AED</p>
      <p>Thank you for choosing Dubai Tours!</p>
    `
  };

  await sgMail.send(msg);
}
```

#### 9. file-upload.js
**Назначение**: File upload handler с Multer
**Включает**: Validation (size, type), local/S3/Cloudinary storage
**Использование**: Customer passport scans, tour photos, payment receipts
**Копировать в**: `middleware/upload.js`

#### 10. websocket-server.js
**Назначение**: WebSocket server setup
**Включает**: Connection handling, rooms, authentication
**Использование**: Real-time booking notifications, live chat с support
**Копировать в**: `websocket.js`

#### 11. graphql-schema.js
**Назначение**: GraphQL schema и resolvers
**Включает**: Queries, mutations, subscriptions
**Использование**: Гибкое API для мобильного приложения туров
**Копировать в**: `graphql/`

#### 12. cron-job.js
**Назначение**: Scheduled tasks с node-cron
**Включает**: Daily reports, cleanup, reminders
**Использование**: Ежедневные отчёты по бронированиям, напоминания за 24 часа до тура
**Копировать в**: `jobs/`

**Пример:**
```javascript
// jobs/daily-reports.js
const cron = require('node-cron');

// Каждый день в 9:00 утра
cron.schedule('0 9 * * *', async () => {
  const today = new Date();
  const bookings = await Booking.findAll({
    where: {
      date: {
        [Op.gte]: today,
        [Op.lt]: new Date(today.getTime() + 24 * 60 * 60 * 1000)
      }
    }
  });

  // Отправить отчёт администратору
  await sendDailyReport(bookings);
});
```

#### 13. error-handler.js
**Назначение**: Centralized error handling
**Включает**: Logging, error responses, Sentry integration
**Использование**: Express error middleware
**Копировать в**: `middleware/error.js`

#### 14. logger.js
**Назначение**: Winston/Pino logger setup
**Включает**: Levels, transports, formatting
**Использование**: Production logging всех операций
**Копировать в**: `utils/logger.js`

#### 15. env-config.js
**Назначение**: Environment configuration
**Включает**: dotenv, validation, defaults
**Использование**: Multi-environment setup (dev/staging/production)
**Копировать в**: `config/`

### 15 Полных Working Examples

| # | Пример | Технологии | Сложность | Применение в туризме |
|---|--------|------------|-----------|---------------------|
| 01 | **booking-form-handler** | Serverless, validation | Простой | Форма бронирования тура на сайте |
| 02 | **payment-webhook** | Stripe, signature verify | Средний | Обработка оплаты туров через Stripe |
| 03 | **sheets-api-sync** | Google Sheets API, cron | Средний | Синхронизация бронирований с Google Sheets |
| 04 | **express-rest-api** | Express, PostgreSQL | Средний | Полный API для туристического сайта |
| 05 | **database-crud** | Sequelize/Mongoose | Простой | CRUD для туров, клиентов, бронирований |
| 06 | **email-sender** | Nodemailer, templates | Простой | Отправка подтверждений бронирования |
| 07 | **whatsapp-webhook** | WhatsApp Business API | Средний | Уведомления клиентов через WhatsApp |
| 08 | **file-upload** | Multer, S3/Cloudinary | Средний | Загрузка фото туров, паспортов клиентов |
| 09 | **rate-limiter** | Redis, express-rate-limit | Продвинутый | Защита публичного API от abuse |
| 10 | **cron-jobs** | node-cron, automation | Средний | Автоматические напоминания и отчёты |
| 11 | **oauth-integration** | OAuth 2.0, JWT | Продвинутый | Вход через Google/Facebook |
| 12 | **websocket-chat** | WebSockets, real-time | Продвинутый | Live chat поддержка на сайте |
| 13 | **graphql-api** | GraphQL, Apollo Server | Продвинутый | Гибкое API для мобильного приложения |
| 14 | **microservices** | Docker, service mesh | Экспертный | Разделение на сервисы (tours, bookings, payments) |
| 15 | **jwt-auth** | JWT, refresh tokens | Средний | Полная система авторизации клиентов |

**Все примеры находятся в**: `assets/examples/`

**Каждый пример включает:**
- `README.md` - Подробное описание, установка, использование
- `package.json` - Все зависимости
- `.env.example` - Пример environment variables
- `tests/` - Unit и integration тесты
- Готовый к запуску код

---

## 5. Scripts & Automation

### 12 Production-Ready Scripts

**Development:**
```bash
npm run lint          # lint.js - ESLint проверка кода
npm run format        # format.js - Prettier форматирование
npm run dev           # dev-server.js - Hot reload dev server
npm run type-check    # type-check.js - JSDoc/TypeScript проверка
```

**Testing:**
```bash
npm test              # test.js - Jest unit/integration tests
npm run test:watch    # test.js --watch
npm run test:coverage # test.js --coverage (должно быть >80%)
```

**Database:**
```bash
npm run migrate       # migrate.js - Database migrations
npm run migrate:undo  # Откатить последнюю миграцию
npm run seed          # seed.js - Заполнить тестовыми данными
```

**Production:**
```bash
npm run build         # build.js - Production build
npm run security      # security-audit.js - npm audit + OWASP checks
npm run deploy        # deploy-helper.js - Deployment automation
```

**Utilities:**
```bash
npm run docs          # docs-generator.js - Generate API docs
npm run profile       # profiler.js - Performance profiling
```

### Описание ключевых скриптов

**dev-server.js** - Локальный сервер с hot reload:
- Auto-restart при изменении файлов
- Загрузка .env variables
- Proxy для API запросов
- HTTPS для локальной разработки

**migrate.js** - Database migrations:
- Создание/изменение таблиц
- Версионирование схемы БД
- Rollback поддержка
- Пример: создание таблиц tours, bookings, customers

**security-audit.js** - Security checks:
- npm audit для уязвимостей в зависимостях
- OWASP Top 10 проверки
- Secrets scanning (не закоммичены ли API keys)
- Dependency license checking

**deploy-helper.js** - Deployment automation:
- Pre-deployment checks (tests pass, no vulnerabilities)
- Environment setup
- Database migrations
- Rollback в случае ошибки
- Slack/Email уведомления

---

## 6. Типичные ошибки Node.js

### Top 10 ошибок и решения

#### 1. Необработанные Promise rejections

```javascript
// Ошибка
async function fetchTours() {
  const response = await fetch('/api/tours');
  return response.json();
}
fetchTours(); // Забыли .catch() или try/catch!

// Решение 1: try/catch
async function fetchTours() {
  try {
    const response = await fetch('/api/tours');
    return response.json();
  } catch (error) {
    console.error('Failed to fetch tours:', error);
    throw error;
  }
}

// Решение 2: Global handler
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  // Отправить в Sentry/logging
  process.exit(1); // Завершить процесс
});
```

#### 2. Блокирующие операции в event loop

```javascript
// Ошибка - блокирует event loop!
const fs = require('fs');
const data = fs.readFileSync('large-file.txt'); // Synchronous!

// Решение - используйте async версии
const fs = require('fs').promises;
const data = await fs.readFile('large-file.txt', 'utf-8');

// Или callback версию
fs.readFile('large-file.txt', 'utf-8', (err, data) => {
  if (err) throw err;
  console.log(data);
});
```

#### 3. Memory leaks (утечки памяти)

```javascript
// Ошибка - глобальный cache растёт бесконечно
global.toursCache = {};
global.toursCache[tourId] = tourData; // Memory leak!

// Решение - LRU cache с лимитами
const LRU = require('lru-cache');
const cache = new LRU({
  max: 500,           // Максимум 500 записей
  maxAge: 1000 * 60 * 5 // 5 минут TTL
});

cache.set(tourId, tourData);
const tour = cache.get(tourId);
```

#### 4. Не закрытые database connections

```javascript
// Ошибка - connection leak
const { Pool } = require('pg');
const pool = new Pool();

async function getTour(id) {
  const client = await pool.connect();
  const result = await client.query('SELECT * FROM tours WHERE id = $1', [id]);
  return result.rows[0];
  // Забыли client.release()! Утечка соединений!
}

// Решение - всегда используйте try/finally
async function getTour(id) {
  const client = await pool.connect();
  try {
    const result = await client.query('SELECT * FROM tours WHERE id = $1', [id]);
    return result.rows[0];
  } finally {
    client.release(); // Всегда освобождаем
  }
}
```

#### 5. Секреты в коде или git

```javascript
// Ошибка - API key в коде!
const STRIPE_SECRET_KEY = 'sk_live_123456789abcdef'; // НИКОГДА!!!

// Решение - используйте environment variables
require('dotenv').config();
const STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY;

// .env файл (НЕ коммитить в git!)
STRIPE_SECRET_KEY=sk_live_123456789abcdef
DATABASE_URL=postgresql://user:pass@localhost:5432/db
JWT_SECRET=super_secret_key_here

// .gitignore
.env
.env.local
```

#### 6. Отсутствие rate limiting

```javascript
// Проблема - API доступен без ограничений (DDoS уязвимость)

// Решение - rate limiting
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 минут
  max: 100, // Макс 100 запросов с одного IP
  message: 'Too many requests, please try again later'
});

// Применить ко всем routes
app.use('/api/', limiter);

// Строже для login endpoint
const loginLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 5, // 5 попыток в минуту
  message: 'Too many login attempts'
});

app.post('/api/auth/login', loginLimiter, loginHandler);
```

#### 7. SQL injection уязвимости

```javascript
// Ошибка - SQL injection!
const userId = req.params.id;
const query = `SELECT * FROM users WHERE id = ${userId}`; // ОПАСНО!
const result = await db.query(query);

// Решение - параметризованные запросы
const userId = req.params.id;
const result = await db.query(
  'SELECT * FROM users WHERE id = $1', // Placeholder
  [userId] // Параметры отдельно
);

// С ORM (Sequelize)
const user = await User.findByPk(userId); // Безопасно
```

#### 8. Не валидация входных данных

```javascript
// Ошибка - принимаем данные без проверки
app.post('/api/bookings', async (req, res) => {
  const booking = await Booking.create(req.body); // Опасно!
  res.json(booking);
});

// Решение - валидация
const { body, validationResult } = require('express-validator');

app.post('/api/bookings', [
  body('tourId').isInt(),
  body('date').isISO8601(),
  body('guests').isInt({ min: 1, max: 20 }),
  body('email').isEmail().normalizeEmail(),
  body('phone').matches(/^\+?[\d\s-()]+$/)
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  const booking = await Booking.create(req.body);
  res.json(booking);
});
```

#### 9. Синхронные ошибки в async функциях

```javascript
// Ошибка - sync throw в async function
async function processBooking(data) {
  if (!data.tourId) {
    throw new Error('Tour ID required'); // Может не попасть в catch!
  }

  const tour = await Tour.findByPk(data.tourId);
  return tour;
}

// Решение - оборачивайте в try/catch
app.post('/api/bookings', async (req, res, next) => {
  try {
    const result = await processBooking(req.body);
    res.json(result);
  } catch (error) {
    next(error); // Передать в error handler
  }
});

// Или используйте wrapper
const catchAsync = (fn) => {
  return (req, res, next) => {
    fn(req, res, next).catch(next);
  };
};

app.post('/api/bookings', catchAsync(async (req, res) => {
  const result = await processBooking(req.body);
  res.json(result);
}));
```

#### 10. Неправильная обработка multipart/form-data

```javascript
// Ошибка - забыли multer для file uploads
app.post('/api/upload', (req, res) => {
  const file = req.body.file; // undefined!
});

// Решение - multer middleware
const multer = require('multer');
const upload = multer({
  dest: 'uploads/',
  limits: { fileSize: 5 * 1024 * 1024 }, // 5MB max
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith('image/')) {
      cb(null, true);
    } else {
      cb(new Error('Only images allowed'));
    }
  }
});

app.post('/api/upload', upload.single('file'), (req, res) => {
  const file = req.file; // Теперь доступен!
  res.json({ filename: file.filename, path: file.path });
});
```

---

## 7. Best Practices для Production

### 7.1 Security (Безопасность)

```javascript
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');

// 1. Security headers с Helmet
app.use(helmet());

// 2. CORS настроен правильно
const allowedOrigins = process.env.ALLOWED_ORIGINS.split(',');
app.use(cors({
  origin: (origin, callback) => {
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true
}));

// 3. Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false
});
app.use('/api/', limiter);

// 4. Input validation
const { body, validationResult } = require('express-validator');

app.post('/api/bookings', [
  body('email').isEmail().normalizeEmail(),
  body('date').isISO8601(),
  body('guests').isInt({ min: 1, max: 20 })
], (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  // Process...
});

// 5. Secrets management
require('dotenv').config();
const config = {
  jwtSecret: process.env.JWT_SECRET,
  dbUrl: process.env.DATABASE_URL,
  stripeKey: process.env.STRIPE_SECRET_KEY
};

// Проверка наличия критических secrets при запуске
if (!config.jwtSecret || !config.dbUrl) {
  console.error('Missing critical environment variables!');
  process.exit(1);
}
```

### 7.2 Error Handling (Обработка ошибок)

```javascript
// Кастомные Error классы
class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}

class NotFoundError extends AppError {
  constructor(resource) {
    super(`${resource} not found`, 404);
  }
}

class ValidationError extends AppError {
  constructor(message) {
    super(message, 400);
  }
}

// Global error handler (должен быть последним middleware)
app.use((err, req, res, next) => {
  err.statusCode = err.statusCode || 500;

  if (process.env.NODE_ENV === 'production') {
    // Production: не показываем stack trace
    if (err.isOperational) {
      res.status(err.statusCode).json({
        status: 'error',
        message: err.message
      });
    } else {
      // Программные ошибки - логируем и показываем generic message
      console.error('ERROR:', err);
      res.status(500).json({
        status: 'error',
        message: 'Something went wrong'
      });
    }
  } else {
    // Development: показываем всё
    res.status(err.statusCode).json({
      status: 'error',
      message: err.message,
      stack: err.stack
    });
  }
});

// Unhandled rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// Uncaught exceptions
process.on('uncaughtException', (err) => {
  console.error('Uncaught Exception:', err);
  process.exit(1);
});
```

### 7.3 Logging (Логирование)

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}

// Использование
logger.info('Server started', { port: 3000 });
logger.error('Database connection failed', { error: err.message });
logger.warn('High memory usage', { memoryUsage: process.memoryUsage() });

// Middleware для логирования запросов
app.use((req, res, next) => {
  logger.info('Incoming request', {
    method: req.method,
    url: req.url,
    ip: req.ip
  });
  next();
});
```

### 7.4 Database Best Practices

**Connection pooling:**
```javascript
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20, // Максимум 20 соединений
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000
});
```

**Prepared statements (защита от SQL injection):**
```javascript
// Всегда используйте placeholders
const result = await pool.query(
  'SELECT * FROM tours WHERE category = $1 AND price <= $2',
  [category, maxPrice]
);
```

**Indexes для производительности:**
```sql
-- Индексы для часто запрашиваемых полей
CREATE INDEX idx_tours_category ON tours(category);
CREATE INDEX idx_bookings_date ON bookings(date);
CREATE INDEX idx_bookings_customer_email ON bookings(customer_email);
```

**Migrations для версионирования:**
```javascript
// migrations/20260204_create_tours.js
module.exports = {
  up: async (queryInterface, Sequelize) => {
    await queryInterface.createTable('tours', {
      id: {
        type: Sequelize.INTEGER,
        primaryKey: true,
        autoIncrement: true
      },
      name: Sequelize.STRING,
      price_aed: Sequelize.DECIMAL(10, 2),
      created_at: Sequelize.DATE,
      updated_at: Sequelize.DATE
    });
  },
  down: async (queryInterface) => {
    await queryInterface.dropTable('tours');
  }
};
```

### 7.5 Performance (Производительность)

**Caching с Redis:**
```javascript
const redis = require('redis');
const client = redis.createClient({ url: process.env.REDIS_URL });

await client.connect();

// Cache популярных туров
app.get('/api/tours/popular', async (req, res) => {
  // Попытаться получить из cache
  const cached = await client.get('tours:popular');
  if (cached) {
    return res.json(JSON.parse(cached));
  }

  // Запрос к БД
  const tours = await Tour.findAll({ where: { popular: true } });

  // Сохранить в cache на 5 минут
  await client.setEx('tours:popular', 300, JSON.stringify(tours));

  res.json(tours);
});
```

**Compression middleware:**
```javascript
const compression = require('compression');
app.use(compression()); // Сжимает ответы
```

**Pagination для больших списков:**
```javascript
app.get('/api/tours', async (req, res) => {
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 20;
  const offset = (page - 1) * limit;

  const { rows, count } = await Tour.findAndCountAll({
    limit,
    offset,
    order: [['created_at', 'DESC']]
  });

  res.json({
    tours: rows,
    total: count,
    page,
    pages: Math.ceil(count / limit)
  });
});
```

### 7.6 Monitoring (Мониторинг)

**Health check endpoint:**
```javascript
app.get('/health', async (req, res) => {
  // Проверка БД
  let dbStatus = 'ok';
  try {
    await pool.query('SELECT 1');
  } catch (err) {
    dbStatus = 'error';
  }

  res.json({
    status: dbStatus === 'ok' ? 'healthy' : 'unhealthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    database: dbStatus
  });
});
```

**Error tracking с Sentry:**
```javascript
const Sentry = require('@sentry/node');

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0
});

app.use(Sentry.Handlers.requestHandler());
app.use(Sentry.Handlers.errorHandler());
```

### 7.7 Deployment (Деплой)

**Environment variables (не хардкодить!):**
```javascript
// config/index.js
require('dotenv').config();

module.exports = {
  port: process.env.PORT || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',
  database: {
    url: process.env.DATABASE_URL,
    poolSize: parseInt(process.env.DB_POOL_SIZE) || 10
  },
  jwt: {
    secret: process.env.JWT_SECRET,
    expiresIn: process.env.JWT_EXPIRES_IN || '7d'
  },
  email: {
    apiKey: process.env.SENDGRID_API_KEY,
    from: process.env.EMAIL_FROM
  }
};
```

**Graceful shutdown:**
```javascript
const server = app.listen(PORT);

process.on('SIGTERM', async () => {
  console.log('SIGTERM received, closing server gracefully...');

  server.close(async () => {
    console.log('HTTP server closed');

    // Закрыть database connections
    await pool.end();
    console.log('Database pool closed');

    process.exit(0);
  });
});
```

**Zero-downtime deployments:**
```javascript
// ecosystem.config.js (PM2)
module.exports = {
  apps: [{
    name: 'tours-api',
    script: './server.js',
    instances: 'max', // Используем все CPU cores
    exec_mode: 'cluster',
    wait_ready: true,
    listen_timeout: 10000,
    kill_timeout: 5000,
    env_production: {
      NODE_ENV: 'production',
      PORT: 3000
    }
  }]
};

// В коде сигнализируем PM2 что сервер готов
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  if (process.send) {
    process.send('ready'); // PM2 может начинать роутить трафик
  }
});
```

---

## 8. Дополнительные ресурсы

### Официальная документация
- **Node.js Docs**: https://nodejs.org/docs - Официальная документация Node.js
- **Express.js**: https://expressjs.com - Express фреймворк
- **Netlify Functions**: https://docs.netlify.com/functions - Serverless functions
- **MDN JavaScript**: https://developer.mozilla.org/en-US/docs/Web/JavaScript - Справочник по JavaScript

### Рекомендуемые библиотеки

**Core:**
- `express` - Веб-фреймворк
- `dotenv` - Environment variables
- `cors` - CORS middleware
- `helmet` - Security headers

**Database:**
- `sequelize` - PostgreSQL/MySQL ORM
- `mongoose` - MongoDB ODM
- `pg` - PostgreSQL client
- `knex` - SQL query builder

**Authentication:**
- `jsonwebtoken` - JWT tokens
- `bcrypt` - Password hashing
- `passport` - OAuth strategies

**Validation:**
- `joi` - Schema validation
- `express-validator` - Request validation
- `validator` - String validators

**Email & Notifications:**
- `nodemailer` - Email sending
- `@sendgrid/mail` - SendGrid integration
- `twilio` - SMS notifications
- `whatsapp-web.js` - WhatsApp integration

**Testing:**
- `jest` - Testing framework
- `supertest` - HTTP assertions
- `chai` - BDD/TDD assertions

**Utilities:**
- `lodash` - Utility functions
- `moment` / `date-fns` - Date manipulation
- `axios` - HTTP client
- `multer` - File uploads

**Logging & Monitoring:**
- `winston` - Logging
- `morgan` - HTTP request logger
- `@sentry/node` - Error tracking

### Инструменты разработки
- **Postman/Insomnia** - API тестирование
- **Docker** - Контейнеризация
- **PM2** - Process manager для production
- **nodemon** - Auto-restart в development
- **ESLint** - Code linting
- **Prettier** - Code formatting

---

## 9. Связанные скиллы и workflows

### Интеграция с другими скиллами

**Frontend → Backend:**
```
html-css-справочник → javascript-nodejs-справочник
(формы бронирования)   (обработка запросов, REST API)

Пример:
- HTML форма отправляет POST запрос
- Node.js serverless function обрабатывает
- Отправляет email подтверждение
- Сохраняет в БД или Google Sheets
```

**Backend → Database:**
```
javascript-nodejs-справочник → database-sql-справочник
(Node.js, Sequelize ORM)      (PostgreSQL, SQL queries)

Пример:
- Express API с Sequelize
- PostgreSQL база для туров и бронирований
- Оптимизация queries с indexes
- Migrations для версионирования схемы
```

**Backend → Deployment:**
```
javascript-nodejs-справочник → netlify-deployment
(код приложения, functions)    (serverless functions, CI/CD)

Пример:
- Написать функцию в netlify/functions/
- Протестировать: netlify dev
- Деплой: netlify deploy --prod
- Автоматический CI/CD через GitHub
```

**Backend → Business Logic:**
```
javascript-nodejs-справочник → api-туризм-оаэ
(общие паттерны)              (конкретный бизнес API)

Пример:
- Общие паттерны: JWT auth, error handling
- Специфика бизнеса: туры в Дубае, pricing в AED/USD
- Интеграция с payment providers (Stripe)
- WhatsApp уведомления клиентов
```

### Типичные workflows

**Workflow 1: Serverless Booking API**
1. Создать форму на сайте (HTML/CSS/JS)
2. Написать serverless function для обработки
3. Добавить валидацию данных
4. Отправить email подтверждение
5. Сохранить в Google Sheets или database
6. Деплой на Netlify
7. Настроить custom domain

**Workflow 2: Full Stack Tours Platform**
1. Разработка API: Express + PostgreSQL
2. Models: Tour, Booking, Customer, Payment
3. Authentication: JWT tokens
4. Payment integration: Stripe webhooks
5. Email notifications: SendGrid
6. Testing: Jest + Supertest
7. Контейнеризация: Docker
8. Деплой: Railway/Heroku + CI/CD

**Workflow 3: Microservices Architecture**
1. Разделить на сервисы:
   - Tours Service (каталог туров)
   - Bookings Service (бронирования)
   - Payments Service (платежи)
   - Notifications Service (email/SMS/WhatsApp)
2. API Gateway для роутинга
3. Message Queue (RabbitMQ) для communication
4. Docker Compose для local development
5. Kubernetes для production orchestration

---

## Заключение

Этот справочник создан для практического применения. Не читайте его как книгу - используйте как reference и копируйте templates/examples для своих проектов.

**Следующие шаги:**
1. Выберите Quick Start сценарий (А, Б или В)
2. Следуйте инструкциям и запустите первый проект
3. Изучайте references по мере необходимости
4. Адаптируйте examples под свои нужды
5. Применяйте best practices в production

**Система накопления опыта:**
- Все исправленные ошибки записываются в `experience/fixes/`
- Найденные улучшения в `experience/improvements/`
- Повторяющиеся паттерны в `experience/patterns/`
- Критические уроки обновляются в `experience/_index.md`

**Поддержка:**
- Все templates готовы к копированию из `assets/templates/`
- Все examples находятся в `assets/examples/`
- Все scripts в `scripts/`
- Документация в `references/`

Удачи в разработке вашего туристического API!

---

**Версия:** 1.0
**Последнее обновление:** 2026-02-04
**Следующее обновление:** После накопления опыта использования
