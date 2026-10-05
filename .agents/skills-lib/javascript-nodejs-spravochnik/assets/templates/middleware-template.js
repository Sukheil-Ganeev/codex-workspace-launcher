/**
 * Express Middleware Template
 *
 * Коллекция production-ready middleware для Express приложений:
 * - Authentication (JWT)
 * - Authorization (Role-based)
 * - Rate limiting
 * - Request validation
 * - Error handling
 */

const jwt = require('jsonwebtoken');

// ==================== AUTHENTICATION ====================

/**
 * JWT Authentication middleware
 * Проверяет наличие и валидность JWT токена в Authorization header
 *
 * @example
 * app.use(authMiddleware);
 */
const authMiddleware = (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Missing or invalid token' });
    }

    const token = authHeader.substring(7);

    // TODO: Добавить SECRET из .env
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;

    next();
  } catch (error) {
    return res.status(403).json({ error: 'Invalid token' });
  }
};

// ==================== AUTHORIZATION ====================

/**
 * Role-based authorization middleware
 *
 * @param {string[]} allowedRoles - Допустимые роли
 * @returns {Function} Express middleware
 *
 * @example
 * app.delete('/admin', authorize(['admin']), deleteHandler);
 */
const authorize = (allowedRoles = []) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'User not authenticated' });
    }

    if (!allowedRoles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
};

// ==================== RATE LIMITING ====================

/**
 * Simple in-memory rate limiter
 * TODO: Использовать Redis для production
 *
 * @example
 * app.use(rateLimiter({ windowMs: 15 * 60 * 1000, maxRequests: 100 }));
 */
const rateLimiter = (options = {}) => {
  const windowMs = options.windowMs || 15 * 60 * 1000; // 15 minutes
  const maxRequests = options.maxRequests || 100;
  const store = new Map();

  setInterval(() => {
    const now = Date.now();
    for (const [key, data] of store.entries()) {
      if (now - data.firstRequest > windowMs) {
        store.delete(key);
      }
    }
  }, windowMs);

  return (req, res, next) => {
    const key = req.ip || req.socket.remoteAddress;
    const now = Date.now();
    const data = store.get(key) || { firstRequest: now, count: 0 };

    if (now - data.firstRequest > windowMs) {
      data.firstRequest = now;
      data.count = 0;
    }

    data.count++;

    if (data.count > maxRequests) {
      res.set('Retry-After', Math.ceil((data.firstRequest + windowMs - now) / 1000));
      return res.status(429).json({ error: 'Too many requests' });
    }

    store.set(key, data);
    res.set('X-RateLimit-Remaining', maxRequests - data.count);
    next();
  };
};

// ==================== VALIDATION ====================

/**
 * Валидация JSON body
 */
const validateJSON = (req, res, next) => {
  if (req.is('application/json') && req.body === undefined) {
    return res.status(400).json({ error: 'Invalid JSON in request body' });
  }
  next();
};

/**
 * Валидация обязательных полей
 *
 * @param {string[]} fields - Обязательные поля
 * @returns {Function} Express middleware
 *
 * @example
 * app.post('/user', validateRequired(['email', 'password']), handler);
 */
const validateRequired = (fields = []) => {
  return (req, res, next) => {
    const missing = fields.filter((field) => !req.body[field]);

    if (missing.length > 0) {
      return res.status(400).json({
        error: 'Missing required fields',
        fields: missing,
      });
    }

    next();
  };
};

// ==================== LOGGING ====================

/**
 * Request logging middleware
 */
const requestLogger = (req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(
      `[${new Date().toISOString()}] ${req.method} ${req.path} - ${res.statusCode} (${duration}ms)`
    );
  });

  next();
};

// ==================== ERROR HANDLING ====================

/**
 * Async error wrapper для route handlers
 *
 * @param {Function} fn - Async handler
 * @returns {Function} Express middleware
 *
 * @example
 * router.get('/data', asyncHandler(async (req, res) => { ... }));
 */
const asyncHandler = (fn) => {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

module.exports = {
  authMiddleware,
  authorize,
  rateLimiter,
  validateJSON,
  validateRequired,
  requestLogger,
  asyncHandler,
};
