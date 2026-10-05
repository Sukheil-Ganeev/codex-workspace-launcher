# Error Handling & Logging

Полный справочник по обработке ошибок и логированию в Node.js приложениях. Покрывает best practices, кастомные классы ошибок, middleware для Express и системы мониторинга.

---

## 1. Try/Catch Best Practices

### Базовая структура

```javascript
// ✅ Правильно: обработка конкретных ошибок
async function bookTour(tourId, userId) {
  try {
    const tour = await Tour.findById(tourId);
    if (!tour) {
      throw new NotFoundError('Tour not found');
    }
    const booking = await Booking.create({
      tourId,
      userId,
      status: 'pending'
    });
    return booking;
  } catch (error) {
    if (error instanceof NotFoundError) {
      logger.warn(`Tour ${tourId} not found for user ${userId}`);
      throw error;
    }
    if (error.code === 'E_DB_CONNECTION') {
      logger.error('Database connection failed', { error });
      throw new InternalServerError('Service temporarily unavailable');
    }
    logger.error('Unexpected error in bookTour', { error, tourId, userId });
    throw error;
  }
}

// ❌ Неправильно: слишком общая обработка
async function bookTourBad(tourId, userId) {
  try {
    return await Booking.create({ tourId, userId });
  } catch (error) {
    // Ловим ВСЕ ошибки, не различаем типы
    throw new Error('Something went wrong');
  }
}
```

### Async/Await с множественными операциями

```javascript
// ✅ Обработка каскадных ошибок
async function completeBooking(bookingId, paymentDetails) {
  const session = await db.startTransaction();

  try {
    // Шаг 1: Обновить бронирование
    const booking = await Booking.findByIdAndUpdate(
      bookingId,
      { status: 'processing' },
      { session }
    );

    if (!booking) {
      throw new NotFoundError(`Booking ${bookingId} not found`);
    }

    // Шаг 2: Обработать платёж
    let paymentResult;
    try {
      paymentResult = await processPayment(booking, paymentDetails);
    } catch (paymentError) {
      // Откатить статус бронирования перед повтором
      await Booking.findByIdAndUpdate(
        bookingId,
        { status: 'pending' },
        { session }
      );
      throw paymentError; // Пробросить дальше
    }

    // Шаг 3: Отправить подтверждение
    await sendConfirmationEmail(booking, paymentResult);

    // Коммитить транзакцию
    await session.commitTransaction();
    return booking;

  } catch (error) {
    await session.abortTransaction();
    logger.error('Booking completion failed', {
      bookingId,
      error: error.message,
      stack: error.stack
    });
    throw error;
  } finally {
    await session.endSession();
  }
}
```

---

## 2. Custom Error Classes

### Базовая иерархия ошибок

```javascript
// errors/AppError.js - Базовый класс
class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true; // Ошибка предусмотрена (не баг)

    Error.captureStackTrace(this, this.constructor);
  }
}

// Специфичные ошибки
class ValidationError extends AppError {
  constructor(message, fields = {}) {
    super(message, 400);
    this.fields = fields;
  }
}

class NotFoundError extends AppError {
  constructor(resource = 'Resource') {
    super(`${resource} not found`, 404);
  }
}

class AuthenticationError extends AppError {
  constructor(message = 'Authentication failed') {
    super(message, 401);
  }
}

class AuthorizationError extends AppError {
  constructor(message = 'Insufficient permissions') {
    super(message, 403);
  }
}

class ConflictError extends AppError {
  constructor(message = 'Resource conflict') {
    super(message, 409);
  }
}

class InternalServerError extends AppError {
  constructor(message = 'Internal server error') {
    super(message, 500);
    this.isOperational = false; // Неожиданная ошибка
  }
}

// Ошибка внешнего API
class ExternalServiceError extends AppError {
  constructor(service, statusCode = 502, message) {
    super(message || `${service} service error`, statusCode);
    this.service = service;
  }
}

module.exports = {
  AppError,
  ValidationError,
  NotFoundError,
  AuthenticationError,
  AuthorizationError,
  ConflictError,
  InternalServerError,
  ExternalServiceError
};
```

### Пример использования в бизнес-логике

```javascript
// services/tourService.js
const { ValidationError, NotFoundError, ConflictError } = require('../errors');

class TourService {
  async createTour(data) {
    // Валидация
    if (!data.name || data.name.trim().length === 0) {
      throw new ValidationError('Tour name is required', {
        name: 'Name cannot be empty'
      });
    }

    if (data.price < 0) {
      throw new ValidationError('Invalid price', {
        price: 'Price must be non-negative'
      });
    }

    // Проверка дублирования
    const existing = await Tour.findOne({
      name: data.name,
      date: data.date
    });

    if (existing) {
      throw new ConflictError(
        `Tour "${data.name}" already exists on this date`
      );
    }

    return await Tour.create(data);
  }

  async getTourById(id) {
    if (!isValidMongoId(id)) {
      throw new ValidationError('Invalid tour ID format', { id });
    }

    const tour = await Tour.findById(id);

    if (!tour) {
      throw new NotFoundError('Tour');
    }

    return tour;
  }
}

module.exports = new TourService();
```

---

## 3. Error Handling Middleware (Express)

### Async Error Wrapper

```javascript
// middleware/asyncHandler.js
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

// Использование в маршрутах
router.post('/tours', asyncHandler(async (req, res) => {
  const tour = await tourService.createTour(req.body);
  res.status(201).json(tour);
}));

module.exports = asyncHandler;
```

### Centralized Error Handler

```javascript
// middleware/errorHandler.js
const errorHandler = (err, req, res, next) => {
  // Логировать ошибку
  if (err.isOperational) {
    logger.warn('Operational error', {
      message: err.message,
      statusCode: err.statusCode,
      path: req.path
    });
  } else {
    logger.error('Unexpected error', {
      message: err.message,
      stack: err.stack,
      path: req.path,
      method: req.method
    });
  }

  // Обработка известных ошибок
  if (err.isOperational) {
    return res.status(err.statusCode).json({
      status: 'error',
      statusCode: err.statusCode,
      message: err.message,
      ...(process.env.NODE_ENV === 'development' && {
        stack: err.stack,
        details: err.fields || {}
      })
    });
  }

  // Обработка ошибок базы данных
  if (err.name === 'MongoError' && err.code === 11000) {
    const field = Object.keys(err.keyPattern)[0];
    return res.status(409).json({
      status: 'error',
      message: `Duplicate ${field}`,
      field
    });
  }

  if (err.name === 'CastError') {
    return res.status(400).json({
      status: 'error',
      message: 'Invalid ID format'
    });
  }

  // Обработка ошибок валидации (Joi, Yup)
  if (err.isJoi) {
    const fields = {};
    err.details.forEach(detail => {
      fields[detail.path.join('.')] = detail.message;
    });
    return res.status(400).json({
      status: 'error',
      message: 'Validation failed',
      fields
    });
  }

  // Неожиданная ошибка
  return res.status(500).json({
    status: 'error',
    message: 'Internal server error',
    ...(process.env.NODE_ENV === 'development' && {
      error: err.message,
      stack: err.stack
    })
  });
};

module.exports = errorHandler;
```

### Express App Setup

```javascript
// app.js
const express = require('express');
const errorHandler = require('./middleware/errorHandler');
const asyncHandler = require('./middleware/asyncHandler');

const app = express();

// ... middleware, routes ...

// 404 Handler
app.use((req, res) => {
  res.status(404).json({
    status: 'error',
    message: 'Route not found'
  });
});

// Error Handler (ВСЕГДА последний middleware!)
app.use(errorHandler);

module.exports = app;
```

---

## 4. Async Error Handling

### Обработка Promise.all()

```javascript
// ❌ Неправильно: ошибка в одном Promise отменяет остальные
async function fetchTourDetails(tourIds) {
  try {
    const tours = await Promise.all(
      tourIds.map(id => Tour.findById(id))
    );
    return tours;
  } catch (error) {
    // Если одна ошибка, всё падает
    logger.error('Failed to fetch tours', error);
  }
}

// ✅ Правильно: обработка частичных ошибок
async function fetchTourDetailsWithFallback(tourIds) {
  const results = await Promise.allSettled(
    tourIds.map(id => Tour.findById(id))
  );

  const tours = [];
  const errors = [];

  results.forEach((result, index) => {
    if (result.status === 'fulfilled') {
      tours.push(result.value);
    } else {
      errors.push({
        tourId: tourIds[index],
        error: result.reason.message
      });
      logger.warn(`Failed to fetch tour ${tourIds[index]}`, result.reason);
    }
  });

  return { tours, errors, hasErrors: errors.length > 0 };
}
```

### Обработка внешних API

```javascript
// ❌ Неправильно: нет retry логики
async function fetchPaymentStatus(paymentId) {
  return await axios.get(`${PAYMENT_API}/status/${paymentId}`);
}

// ✅ Правильно: retry с exponential backoff
async function fetchPaymentStatusWithRetry(paymentId, maxRetries = 3) {
  let lastError;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await axios.get(
        `${PAYMENT_API}/status/${paymentId}`,
        { timeout: 5000 }
      );
    } catch (error) {
      lastError = error;

      // Не retry для 4xx ошибок
      if (error.response?.status >= 400 && error.response?.status < 500) {
        throw new ExternalServiceError(
          'PaymentAPI',
          error.response.status,
          error.response.data?.message
        );
      }

      if (attempt < maxRetries) {
        const delay = Math.min(1000 * Math.pow(2, attempt - 1), 10000);
        logger.warn(`Payment API retry ${attempt}/${maxRetries} after ${delay}ms`, {
          paymentId,
          error: error.message
        });
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw new ExternalServiceError(
    'PaymentAPI',
    503,
    `Failed after ${maxRetries} retries: ${lastError.message}`
  );
}
```

---

## 5. Logging (Winston, Pino)

### Winston Configuration

```javascript
// config/logger.js
const winston = require('winston');
const path = require('path');

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'booking-api' },
  transports: [
    // Ошибки в отдельный файл
    new winston.transports.File({
      filename: path.join(__dirname, '../logs/error.log'),
      level: 'error'
    }),
    // Все логи
    new winston.transports.File({
      filename: path.join(__dirname, '../logs/combined.log')
    })
  ]
});

// Console для development
if (process.env.NODE_ENV !== 'production') {
  logger.add(
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    })
  );
}

module.exports = logger;
```

### Pino Configuration (более лёгкий)

```javascript
// config/logger.js
const pino = require('pino');
const path = require('path');

const logger = pino(
  {
    level: process.env.LOG_LEVEL || 'info',
    timestamp: pino.stdTimeFunctions.isoTime
  },
  pino.transport({
    targets: [
      // Консоль (development)
      {
        target: 'pino/file',
        level: 'debug',
        options: {
          destination: 1, // stdout
          colorize: process.env.NODE_ENV !== 'production'
        }
      },
      // Файл для ошибок
      {
        target: 'pino/file',
        level: 'error',
        options: {
          destination: path.join(__dirname, '../logs/error.log')
        }
      }
    ]
  })
);

module.exports = logger;
```

### Структурированное логирование

```javascript
// services/paymentService.js
const logger = require('../config/logger');

class PaymentService {
  async processPayment(booking, details) {
    const paymentId = generatePaymentId();
    const startTime = Date.now();

    try {
      logger.info('Payment processing started', {
        paymentId,
        bookingId: booking.id,
        amount: booking.totalPrice,
        currency: booking.currency
      });

      const result = await this.chargePayment(paymentId, details);

      const duration = Date.now() - startTime;
      logger.info('Payment processed successfully', {
        paymentId,
        bookingId: booking.id,
        duration,
        transactionId: result.transactionId
      });

      return result;

    } catch (error) {
      const duration = Date.now() - startTime;

      logger.error('Payment processing failed', {
        paymentId,
        bookingId: booking.id,
        duration,
        error: error.message,
        errorCode: error.code,
        stack: error.stack,
        details: {
          retryable: this.isRetryableError(error),
          externalError: error.service
        }
      });

      throw error;
    }
  }
}

module.exports = new PaymentService();
```

---

## 6. Monitoring (Sentry)

### Sentry Integration

```javascript
// config/sentry.js
const Sentry = require('@sentry/node');

const initSentry = (app) => {
  Sentry.init({
    dsn: process.env.SENTRY_DSN,
    environment: process.env.NODE_ENV,
    tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
    debug: process.env.NODE_ENV !== 'production',
    // Игнорировать определённые ошибки
    beforeSend(event, hint) {
      // Не отправлять 404 ошибки
      if (event.exception?.values[0]?.value?.includes('not found')) {
        return null;
      }
      return event;
    }
  });

  // Middleware должны быть после инициализации Sentry
  app.use(Sentry.Handlers.requestHandler());
  app.use(Sentry.Handlers.errorHandler());
};

module.exports = initSentry;
```

### Использование в приложении

```javascript
// app.js
const express = require('express');
const Sentry = require('@sentry/node');
const initSentry = require('./config/sentry');

const app = express();
initSentry(app);

// ... routes, middleware ...

// Пример отправки события в Sentry
app.get('/test-error', (req, res) => {
  try {
    throw new Error('Test error for Sentry');
  } catch (error) {
    Sentry.captureException(error);
    res.status(500).json({ error: 'Error captured' });
  }
});

// Отправка кастомного события
app.post('/bookings', async (req, res) => {
  try {
    const booking = await bookingService.create(req.body);

    // Отправить событие высокой стоимости
    if (booking.totalPrice > 5000) {
      Sentry.captureMessage(
        `High-value booking created: ${booking.id}`,
        'warning',
        {
          booking: {
            id: booking.id,
            totalPrice: booking.totalPrice,
            userId: booking.userId
          }
        }
      );
    }

    res.json(booking);
  } catch (error) {
    Sentry.captureException(error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = app;
```

### Отправка Performance Traces

```javascript
// services/tourService.js
const Sentry = require('@sentry/node');

class TourService {
  async searchTours(filters) {
    const transaction = Sentry.startTransaction({
      op: 'tour.search',
      name: 'Search Tours',
      description: 'Full text search across tours'
    });

    const span1 = transaction.startChild({
      op: 'db.query',
      description: 'Query database'
    });

    try {
      const tours = await Tour.find(filters);
      span1.finish();

      const span2 = transaction.startChild({
        op: 'external.api',
        description: 'Fetch prices from external API'
      });

      const enriched = await Promise.all(
        tours.map(tour => this.enrichWithPrices(tour))
      );
      span2.finish();

      transaction.finish();
      return enriched;

    } catch (error) {
      span1.finish();
      transaction.finish();
      Sentry.captureException(error);
      throw error;
    }
  }
}
```

---

## Чек-лист

- [ ] Используешь кастомные классы ошибок для разных типов
- [ ] Все async функции обёрнуты в try/catch
- [ ] Есть глобальный error handler в Express
- [ ] Логируешь с контекстом (не только сообщение)
- [ ] Используешь Promise.allSettled для параллельных операций
- [ ] Есть retry логика для внешних API
- [ ] Настроен Winston или Pino
- [ ] Интегрирован Sentry для production
- [ ] Различаешь operational vs unexpected ошибки
