/**
 * Error Handler & Middleware Template
 *
 * Production-ready обработка ошибок с:
 * - Глобальный error handler middleware
 * - Custom error классы
 * - Структурированное логирование
 * - Error tracking (Sentry)
 *
 * @example
 * npm install express dotenv
 */

// ==================== CUSTOM ERROR CLASSES ====================

/**
 * Base application error class
 */
class AppError extends Error {
  constructor(message, statusCode, code = 'INTERNAL_ERROR') {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
    this.timestamp = new Date().toISOString();

    // Сохранить stack trace
    Error.captureStackTrace(this, this.constructor);
  }

  toJSON() {
    return {
      error: {
        message: this.message,
        code: this.code,
        statusCode: this.statusCode,
        timestamp: this.timestamp,
      },
    };
  }
}

/**
 * Validation error - 400
 */
class ValidationError extends AppError {
  constructor(message, details = []) {
    super(message, 400, 'VALIDATION_ERROR');
    this.details = details;
  }

  toJSON() {
    return {
      error: {
        ...super.toJSON().error,
        details: this.details,
      },
    };
  }
}

/**
 * Authentication error - 401
 */
class AuthenticationError extends AppError {
  constructor(message = 'Authentication required') {
    super(message, 401, 'UNAUTHENTICATED');
  }
}

/**
 * Authorization error - 403
 */
class AuthorizationError extends AppError {
  constructor(message = 'Access denied') {
    super(message, 403, 'FORBIDDEN');
  }
}

/**
 * Not found error - 404
 */
class NotFoundError extends AppError {
  constructor(resource = 'Resource') {
    super(`${resource} not found`, 404, 'NOT_FOUND');
  }
}

/**
 * Conflict error - 409
 */
class ConflictError extends AppError {
  constructor(message = 'Resource already exists') {
    super(message, 409, 'CONFLICT');
  }
}

/**
 * Rate limit error - 429
 */
class RateLimitError extends AppError {
  constructor(message = 'Too many requests', retryAfter = 60) {
    super(message, 429, 'RATE_LIMITED');
    this.retryAfter = retryAfter;
  }
}

/**
 * Internal server error - 500
 */
class InternalServerError extends AppError {
  constructor(message = 'Internal server error') {
    super(message, 500, 'INTERNAL_ERROR');
  }
}

// ==================== ERROR LOGGING ====================

/**
 * Логирование ошибок с different levels
 */
class ErrorLogger {
  /**
   * Log error
   */
  static error(message, error, context = {}) {
    const logEntry = {
      level: 'error',
      timestamp: new Date().toISOString(),
      message,
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack,
        code: error.code,
      },
      context,
    };

    console.error('[ERROR]', JSON.stringify(logEntry, null, 2));

    // TODO: Отправить в внешний сервис логирования (Sentry, DataDog)
    // if (process.env.SENTRY_DSN) {
    //   Sentry.captureException(error, { extra: context });
    // }

    return logEntry;
  }

  /**
   * Log warning
   */
  static warn(message, context = {}) {
    const logEntry = {
      level: 'warn',
      timestamp: new Date().toISOString(),
      message,
      context,
    };

    console.warn('[WARN]', JSON.stringify(logEntry, null, 2));
    return logEntry;
  }

  /**
   * Log info
   */
  static info(message, context = {}) {
    const logEntry = {
      level: 'info',
      timestamp: new Date().toISOString(),
      message,
      context,
    };

    console.log('[INFO]', JSON.stringify(logEntry, null, 2));
    return logEntry;
  }
}

// ==================== EXPRESS MIDDLEWARE ====================

/**
 * Валидация query parameters
 *
 * @param {Object} schema - Объект с правилами валидации
 * @returns {Function} Express middleware
 *
 * @example
 * app.get('/api/bookings', validateQuery({
 *   limit: { type: 'number', min: 1, max: 100 },
 *   status: { type: 'string', enum: ['pending', 'completed'] }
 * }), handler);
 */
const validateQuery = (schema) => {
  return (req, res, next) => {
    const errors = [];

    for (const [field, rules] of Object.entries(schema)) {
      const value = req.query[field];

      if (rules.required && !value) {
        errors.push({
          field,
          message: `${field} is required`,
        });
        continue;
      }

      if (!value) continue;

      if (rules.type === 'number' && isNaN(value)) {
        errors.push({
          field,
          message: `${field} must be a number`,
        });
      }

      if (rules.min !== undefined && Number(value) < rules.min) {
        errors.push({
          field,
          message: `${field} must be >= ${rules.min}`,
        });
      }

      if (rules.max !== undefined && Number(value) > rules.max) {
        errors.push({
          field,
          message: `${field} must be <= ${rules.max}`,
        });
      }

      if (rules.enum && !rules.enum.includes(value)) {
        errors.push({
          field,
          message: `${field} must be one of: ${rules.enum.join(', ')}`,
        });
      }
    }

    if (errors.length > 0) {
      return next(new ValidationError('Invalid query parameters', errors));
    }

    next();
  };
};

/**
 * Валидация body
 *
 * @param {Object} schema - Правила валидации
 */
const validateBody = (schema) => {
  return (req, res, next) => {
    const errors = [];

    for (const [field, rules] of Object.entries(schema)) {
      const value = req.body[field];

      if (rules.required && !value) {
        errors.push({
          field,
          message: `${field} is required`,
        });
      }

      if (rules.minLength && value && value.length < rules.minLength) {
        errors.push({
          field,
          message: `${field} must be at least ${rules.minLength} characters`,
        });
      }

      if (rules.maxLength && value && value.length > rules.maxLength) {
        errors.push({
          field,
          message: `${field} must be at most ${rules.maxLength} characters`,
        });
      }
    }

    if (errors.length > 0) {
      return next(new ValidationError('Invalid request body', errors));
    }

    next();
  };
};

/**
 * Async route wrapper для автоматической обработки ошибок
 *
 * @param {Function} fn - Async route handler
 * @returns {Function} Express route handler
 *
 * @example
 * router.get('/data', asyncHandler(async (req, res) => {
 *   const data = await getData();
 *   res.json(data);
 * }));
 */
const asyncHandler = (fn) => {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

// ==================== GLOBAL ERROR HANDLER ====================

/**
 * Глобальный middleware для обработки ошибок
 * ВАЖНО: Должен быть последним middleware в приложении
 *
 * @example
 * app.use(errorHandler);
 */
const errorHandler = (err, req, res, next) => {
  // Убедиться что это Error объект
  if (!(err instanceof Error)) {
    err = new InternalServerError(String(err));
  }

  // Определить status code
  const statusCode = err.statusCode || 500;
  const isDevelopment = process.env.NODE_ENV === 'development';

  // Логировать ошибку
  ErrorLogger.error(`[${req.method} ${req.path}]`, err, {
    requestId: req.id,
    userId: req.user?.id,
    ip: req.ip,
  });

  // Обработка specific errors
  let response = err.toJSON ? err.toJSON() : {
    error: {
      message: err.message,
      code: err.code || 'INTERNAL_ERROR',
      statusCode,
    },
  };

  // В development добавить дополнительную информацию
  if (isDevelopment) {
    response.error.stack = err.stack;
  }

  // TODO: Интеграция с Sentry/DataDog для production
  // if (process.env.SENTRY_DSN && statusCode >= 500) {
  //   Sentry.captureException(err);
  // }

  res.status(statusCode).json(response);
};

/**
 * Middleware для обработки 404
 *
 * @example
 * app.use(notFoundHandler);
 */
const notFoundHandler = (req, res, next) => {
  next(new NotFoundError(`${req.method} ${req.path}`));
};

// ==================== EXPORTS ====================

module.exports = {
  // Error classes
  AppError,
  ValidationError,
  AuthenticationError,
  AuthorizationError,
  NotFoundError,
  ConflictError,
  RateLimitError,
  InternalServerError,

  // Logger
  ErrorLogger,

  // Middleware
  validateQuery,
  validateBody,
  asyncHandler,
  errorHandler,
  notFoundHandler,
};

// ==================== USAGE EXAMPLE ====================

/*
// В express app:
const express = require('express');
const {
  errorHandler,
  notFoundHandler,
  asyncHandler,
  validateBody,
  AuthenticationError
} = require('./error-handler');

const app = express();

app.post('/login', validateBody({
  email: { required: true },
  password: { required: true, minLength: 8 }
}), asyncHandler(async (req, res) => {
  const user = await User.findByEmail(req.body.email);
  if (!user) {
    throw new AuthenticationError('Invalid credentials');
  }
  res.json({ token: 'jwt...' });
}));

// 404 handler должен быть перед error handler
app.use(notFoundHandler);

// Error handler ВСЕГДА последний
app.use(errorHandler);
*/
