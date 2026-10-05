/**
 * Express Server Template
 *
 * Production-ready Express приложение с middleware,
 * обработкой ошибок и логированием.
 *
 * @example
 * npm install express cors dotenv morgan
 * node express-server-template.js
 */

const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const morgan = require('morgan');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || 'development';

// ==================== MIDDLEWARE ====================

// Logging
if (NODE_ENV === 'development') {
  app.use(morgan('dev'));
} else {
  app.use(morgan('combined'));
}

// CORS
app.use(
  cors({
    origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
    credentials: true,
  })
);

// Body parser
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ limit: '10mb', extended: true }));

// Request ID middleware
app.use((req, res, next) => {
  req.id = Date.now().toString();
  res.setHeader('X-Request-ID', req.id);
  next();
});

// ==================== ROUTES ====================

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

/**
 * API routes
 * TODO: Добавить ваши routes
 */
app.get('/api/data', (req, res) => {
  res.json({ message: 'Data endpoint', data: [] });
});

// ==================== ERROR HANDLING ====================

/**
 * 404 handler
 */
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    path: req.path,
    method: req.method,
  });
});

/**
 * Error handler middleware
 */
app.use((err, req, res, next) => {
  console.error('[ERROR]', err);

  const statusCode = err.statusCode || 500;
  const message = NODE_ENV === 'development' ? err.message : 'Internal Server Error';

  res.status(statusCode).json({
    error: message,
    requestId: req.id,
    timestamp: new Date().toISOString(),
  });
});

// ==================== SERVER START ====================

const server = app.listen(PORT, () => {
  console.log(`[${NODE_ENV}] Server running on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

module.exports = app;

// Required environment variables:
// PORT=3000
// NODE_ENV=development
// ALLOWED_ORIGINS=http://localhost:3000,https://example.com
