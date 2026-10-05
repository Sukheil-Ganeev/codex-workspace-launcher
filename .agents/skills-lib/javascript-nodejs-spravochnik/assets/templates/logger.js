/**
 * Logger Template (Winston)
 *
 * Production-ready логирование с:
 * - Multiple транспортов (console, file, rotation)
 * - Log levels
 * - Структурированные логи (JSON)
 * - Performance tracking
 * - Интеграция с внешними сервисами
 *
 * @example
 * npm install winston dotenv
 */

const winston = require('winston');
const path = require('path');
const fs = require('fs');

// ==================== LOG DIRECTORY ====================

const logsDir = process.env.LOGS_DIR || './logs';

// Создать директорию если не существует
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
}

// ==================== WINSTON CONFIG ====================

/**
 * Custom format для красивого вывода в консоль (development)
 */
const consoleFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.printf(({ level, message, timestamp, ...meta }) => {
    const metaStr = Object.keys(meta).length ? JSON.stringify(meta, null, 2) : '';
    return `${timestamp} [${level}] ${message} ${metaStr}`;
  })
);

/**
 * JSON format для файлов и production (machine-readable)
 */
const fileFormat = winston.format.combine(
  winston.format.timestamp(),
  winston.format.errors({ stack: true }),
  winston.format.json()
);

/**
 * Создать logger instance
 */
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: fileFormat,
  defaultMeta: {
    service: process.env.SERVICE_NAME || 'api',
    environment: process.env.NODE_ENV || 'development',
    version: process.env.APP_VERSION || '1.0.0',
  },
  transports: [
    // Console transport (для development)
    new winston.transports.Console({
      format: consoleFormat,
    }),

    // File transport - все логи
    new winston.transports.File({
      filename: path.join(logsDir, 'combined.log'),
      maxsize: 10 * 1024 * 1024, // 10MB
      maxFiles: 10,
    }),

    // File transport - только ошибки
    new winston.transports.File({
      filename: path.join(logsDir, 'error.log'),
      level: 'error',
      maxsize: 10 * 1024 * 1024,
      maxFiles: 10,
    }),

    // File transport - только warning
    new winston.transports.File({
      filename: path.join(logsDir, 'warning.log'),
      level: 'warn',
      maxsize: 5 * 1024 * 1024,
      maxFiles: 5,
    }),
  ],

  // Обработка uncaught exceptions
  exceptionHandlers: [
    new winston.transports.File({
      filename: path.join(logsDir, 'exceptions.log'),
    }),
  ],

  // Обработка unhandled rejections
  rejectionHandlers: [
    new winston.transports.File({
      filename: path.join(logsDir, 'rejections.log'),
    }),
  ],
});

// ==================== LOGGER METHODS ====================

/**
 * Info logging
 *
 * @example
 * log.info('User logged in', { userId: 123, email: 'user@example.com' });
 */
const log = {
  info: (message, meta = {}) => {
    logger.info(message, meta);
  },

  /**
   * Warning logging
   */
  warn: (message, meta = {}) => {
    logger.warn(message, meta);
  },

  /**
   * Error logging
   *
   * @example
   * log.error('Database connection failed', {
   *   error: err,
   *   retryCount: 3,
   *   nextRetryIn: '30s'
   * });
   */
  error: (message, meta = {}) => {
    logger.error(message, meta);
  },

  /**
   * Debug logging
   */
  debug: (message, meta = {}) => {
    logger.debug(message, meta);
  },

  /**
   * Critical/severe error
   */
  critical: (message, meta = {}) => {
    logger.error(`[CRITICAL] ${message}`, meta);
    // TODO: Отправить alert (Slack, PagerDuty, etc.)
  },
};

// ==================== PERFORMANCE LOGGING ====================

/**
 * Логировать время выполнения операции
 *
 * @param {string} label - Название операции
 * @param {Function} fn - Функция для выполнения
 * @returns {Promise}
 *
 * @example
 * await logPerformance('fetch-bookings', async () => {
 *   return await Booking.find().limit(100);
 * });
 */
async function logPerformance(label, fn) {
  const startTime = Date.now();
  const startMemory = process.memoryUsage().heapUsed;

  try {
    const result = await fn();
    const duration = Date.now() - startTime;
    const memoryUsed = (process.memoryUsage().heapUsed - startMemory) / 1024 / 1024;

    log.info(`Performance: ${label}`, {
      duration: `${duration}ms`,
      memory: `${memoryUsed.toFixed(2)}MB`,
      status: 'success',
    });

    return result;
  } catch (error) {
    const duration = Date.now() - startTime;
    log.error(`Performance: ${label} - FAILED`, {
      duration: `${duration}ms`,
      error: error.message,
    });
    throw error;
  }
}

// ==================== EXPRESS MIDDLEWARE ====================

/**
 * Express middleware для логирования requests
 *
 * @example
 * app.use(requestLogger);
 */
const requestLogger = (req, res, next) => {
  const startTime = Date.now();
  const requestId = req.id || `req-${Date.now()}`;

  req.id = requestId;
  res.setHeader('X-Request-ID', requestId);

  // Логировать при завершении response
  res.on('finish', () => {
    const duration = Date.now() - startTime;

    const logMeta = {
      requestId,
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      duration: `${duration}ms`,
      ip: req.ip,
      userAgent: req.get('user-agent'),
      userId: req.user?.id || 'anonymous',
    };

    // Логировать на основе status code
    if (res.statusCode >= 500) {
      log.error('Request failed', logMeta);
    } else if (res.statusCode >= 400) {
      log.warn('Request error', logMeta);
    } else {
      log.info('Request completed', logMeta);
    }
  });

  next();
};

// ==================== CONTEXT LOGGER ====================

/**
 * Создать logger с контекстом (для использования в разных функциях)
 *
 * @param {string} context - Контекст (например, имя функции или модуля)
 * @returns {Object} Logger methods
 *
 * @example
 * const logger = createContextLogger('BookingService');
 * logger.info('Creating booking'); // Log: [BookingService] Creating booking
 */
function createContextLogger(context) {
  return {
    info: (message, meta = {}) => {
      log.info(`[${context}] ${message}`, meta);
    },
    warn: (message, meta = {}) => {
      log.warn(`[${context}] ${message}`, meta);
    },
    error: (message, meta = {}) => {
      log.error(`[${context}] ${message}`, meta);
    },
    debug: (message, meta = {}) => {
      log.debug(`[${context}] ${message}`, meta);
    },
  };
}

// ==================== AUDIT LOGGING ====================

/**
 * Логирование действий для аудита
 *
 * @example
 * await auditLog({
 *   action: 'DELETE_BOOKING',
 *   actor: userId,
 *   resource: { type: 'Booking', id: bookingId },
 *   changes: { status: 'CONFIRMED' -> 'CANCELLED' }
 * });
 */
async function auditLog(entry) {
  const auditEntry = {
    timestamp: new Date().toISOString(),
    ...entry,
  };

  // Логировать в отдельный файл
  logger.log('info', 'Audit Log', auditEntry);

  // TODO: Сохранить в БД для compliance/GDPR
  // await AuditLog.create(auditEntry);
}

// ==================== LOG ROTATION ====================

/**
 * Очистить старые логи (старше N дней)
 *
 * @param {number} daysOld - Удалить логи старше X дней
 */
async function cleanupOldLogs(daysOld = 30) {
  try {
    const files = fs.readdirSync(logsDir);
    const now = Date.now();
    const maxAge = daysOld * 24 * 60 * 60 * 1000;

    for (const file of files) {
      const filepath = path.join(logsDir, file);
      const stats = fs.statSync(filepath);

      if (now - stats.mtimeMs > maxAge) {
        fs.unlinkSync(filepath);
        log.info('Deleted old log file', { file });
      }
    }
  } catch (error) {
    log.error('Log cleanup failed', { error: error.message });
  }
}

// ==================== EXPORTS ====================

module.exports = {
  logger,
  log,
  logPerformance,
  requestLogger,
  createContextLogger,
  auditLog,
  cleanupOldLogs,
};

// ==================== USAGE EXAMPLE ====================

/*
// В app.js
const express = require('express');
const { requestLogger, log, createContextLogger } = require('./logger');

const app = express();

// Middleware
app.use(requestLogger);

// В route handler
const bookingLogger = createContextLogger('BookingController');

app.post('/bookings', async (req, res, next) => {
  try {
    bookingLogger.info('Creating new booking', { email: req.body.email });
    // ... business logic ...
    bookingLogger.info('Booking created successfully', { bookingId: 123 });
    res.json({ success: true });
  } catch (error) {
    bookingLogger.error('Failed to create booking', { error: error.message });
    next(error);
  }
});

// Required environment variables:
// LOG_LEVEL=info
// LOGS_DIR=./logs
// SERVICE_NAME=api
// NODE_ENV=production
// APP_VERSION=1.0.0
*/
