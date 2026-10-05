/**
 * Environment Configuration Template
 *
 * Production-ready конфигурация приложения:
 * - Загрузка из .env файла
 * - Валидация переменных окружения
 * - Type casting (string -> number, boolean)
 * - Default values
 * - Environment-specific configs
 *
 * @example
 * npm install dotenv
 */

const dotenv = require('dotenv');
const path = require('path');

// ==================== LOAD ENV FILE ====================

/**
 * Загрузить переменные окружения из .env файла
 * Порядок приоритета:
 * 1. process.env (из shell/deployment)
 * 2. .env.{NODE_ENV}.local
 * 3. .env.{NODE_ENV}
 * 4. .env.local
 * 5. .env
 */

const NODE_ENV = process.env.NODE_ENV || 'development';
const envFiles = [
  `.env.${NODE_ENV}.local`,
  `.env.${NODE_ENV}`,
  '.env.local',
  '.env',
];

for (const file of envFiles) {
  const envPath = path.resolve(process.cwd(), file);
  dotenv.config({ path: envPath });
}

// ==================== TYPE CONVERSION ====================

/**
 * Конвертировать строку в boolean
 */
function toBoolean(value) {
  if (typeof value === 'boolean') return value;
  if (typeof value !== 'string') return false;

  return ['true', '1', 'yes', 'on'].includes(value.toLowerCase());
}

/**
 * Конвертировать строку в number
 */
function toNumber(value) {
  const num = Number(value);
  return isNaN(num) ? 0 : num;
}

/**
 * Парсить JSON строку
 */
function toJSON(value) {
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

// ==================== VALIDATION ====================

/**
 * Проверить что переменная требуется
 */
function validateRequired(name, value) {
  if (!value) {
    throw new Error(
      `Environment variable "${name}" is required but not provided`
    );
  }
  return value;
}

/**
 * Проверить что значение в допустимом диапазоне
 */
function validateEnum(name, value, allowedValues) {
  if (!allowedValues.includes(value)) {
    throw new Error(
      `Environment variable "${name}" must be one of: ${allowedValues.join(', ')}`
    );
  }
  return value;
}

/**
 * Проверить что число в диапазоне
 */
function validateRange(name, value, min, max) {
  const num = toNumber(value);
  if (num < min || num > max) {
    throw new Error(
      `Environment variable "${name}" must be between ${min} and ${max}`
    );
  }
  return num;
}

// ==================== CONFIG OBJECT ====================

/**
 * Основной конфиг объект
 */
const config = {
  // ================ SERVER CONFIG ================

  NODE_ENV: validateEnum(
    'NODE_ENV',
    process.env.NODE_ENV || 'development',
    ['development', 'staging', 'production']
  ),

  PORT: toNumber(process.env.PORT || '3000'),

  HOST: process.env.HOST || '0.0.0.0',

  // ================ DATABASE CONFIG ================

  DB_HOST: process.env.DB_HOST || 'localhost',

  DB_PORT: toNumber(process.env.DB_PORT || '5432'),

  DB_USER: process.env.DB_USER,

  DB_PASSWORD: process.env.DB_PASSWORD,

  DB_NAME: process.env.DB_NAME,

  DB_POOL_MIN: toNumber(process.env.DB_POOL_MIN || '2'),

  DB_POOL_MAX: toNumber(process.env.DB_POOL_MAX || '10'),

  // ================ AUTHENTICATION ================

  JWT_SECRET: validateRequired('JWT_SECRET', process.env.JWT_SECRET),

  JWT_REFRESH_SECRET: validateRequired(
    'JWT_REFRESH_SECRET',
    process.env.JWT_REFRESH_SECRET
  ),

  JWT_EXPIRY: process.env.JWT_EXPIRY || '15m',

  // ================ API KEYS & SECRETS ================

  SENDGRID_API_KEY: process.env.SENDGRID_API_KEY,

  AWS_ACCESS_KEY_ID: process.env.AWS_ACCESS_KEY_ID,

  AWS_SECRET_ACCESS_KEY: process.env.AWS_SECRET_ACCESS_KEY,

  AWS_REGION: process.env.AWS_REGION || 'us-east-1',

  AWS_BUCKET_NAME: process.env.AWS_BUCKET_NAME,

  // ================ WEBHOOK CONFIG ================

  WEBHOOK_SECRET: process.env.WEBHOOK_SECRET,

  STRIPE_API_KEY: process.env.STRIPE_API_KEY,

  STRIPE_WEBHOOK_SECRET: process.env.STRIPE_WEBHOOK_SECRET,

  // ================ LOGGING ================

  LOG_LEVEL: validateEnum(
    'LOG_LEVEL',
    process.env.LOG_LEVEL || 'info',
    ['debug', 'info', 'warn', 'error']
  ),

  LOGS_DIR: process.env.LOGS_DIR || './logs',

  // ================ CORS & SECURITY ================

  ALLOWED_ORIGINS: process.env.ALLOWED_ORIGINS
    ? process.env.ALLOWED_ORIGINS.split(',')
    : ['http://localhost:3000'],

  ALLOWED_METHODS: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],

  CORS_CREDENTIALS: toBoolean(process.env.CORS_CREDENTIALS || 'true'),

  // ================ RATE LIMITING ================

  RATE_LIMIT_WINDOW_MS: toNumber(process.env.RATE_LIMIT_WINDOW_MS || '900000'), // 15 min

  RATE_LIMIT_MAX_REQUESTS: toNumber(
    process.env.RATE_LIMIT_MAX_REQUESTS || '100'
  ),

  // ================ FILE UPLOAD ================

  UPLOAD_DIR: process.env.UPLOAD_DIR || './uploads',

  MAX_FILE_SIZE: toNumber(process.env.MAX_FILE_SIZE || '10485760'), // 10 MB

  // ================ CACHING ================

  CACHE_ENABLED: toBoolean(process.env.CACHE_ENABLED || 'true'),

  CACHE_TTL: toNumber(process.env.CACHE_TTL || '3600'), // 1 hour

  REDIS_URL: process.env.REDIS_URL || 'redis://localhost:6379',

  // ================ MONITORING ================

  SENTRY_DSN: process.env.SENTRY_DSN,

  NEWRELIC_LICENSE_KEY: process.env.NEWRELIC_LICENSE_KEY,

  // ================ FEATURE FLAGS ================

  FEATURE_RATE_LIMITING: toBoolean(process.env.FEATURE_RATE_LIMITING || 'true'),

  FEATURE_CACHING: toBoolean(process.env.FEATURE_CACHING || 'true'),

  FEATURE_API_LOGGING: toBoolean(process.env.FEATURE_API_LOGGING || 'true'),
};

// ==================== CONFIG VALIDATION ====================

/**
 * Валидировать конфиг при запуске
 */
function validateConfig() {
  const errors = [];

  // Production requirements
  if (config.NODE_ENV === 'production') {
    if (!process.env.JWT_SECRET || process.env.JWT_SECRET === 'your-secret-key') {
      errors.push('JWT_SECRET must be set and strong in production');
    }

    if (!process.env.DB_PASSWORD) {
      errors.push('DB_PASSWORD is required in production');
    }

    if (!process.env.SENDGRID_API_KEY) {
      errors.push('SENDGRID_API_KEY is required in production');
    }
  }

  // Database config
  if (!config.DB_HOST) {
    errors.push('DB_HOST is required');
  }

  // Port validation
  if (config.PORT < 1 || config.PORT > 65535) {
    errors.push('PORT must be between 1 and 65535');
  }

  if (errors.length > 0) {
    console.error('Config validation failed:');
    errors.forEach((error) => {
      console.error(`  - ${error}`);
    });
    process.exit(1);
  }

  return true;
}

// ==================== CONFIG GETTERS ====================

/**
 * Получить конфиг значение с type checking
 *
 * @example
 * const port = getConfig('PORT', 'number');
 * const isDev = getConfig('NODE_ENV') === 'development';
 */
function getConfig(key, type = 'string') {
  const value = config[key];

  if (value === undefined) {
    throw new Error(`Config key "${key}" not found`);
  }

  switch (type) {
    case 'number':
      return toNumber(value);
    case 'boolean':
      return toBoolean(value);
    default:
      return value;
  }
}

/**
 * Получить DATABASE_URL для ORM (Prisma, TypeORM)
 */
function getDatabaseUrl() {
  const { DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME } = config;

  if (DB_USER && DB_PASSWORD) {
    return `postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}`;
  } else {
    return `postgresql://${DB_HOST}:${DB_PORT}/${DB_NAME}`;
  }
}

// ==================== PRINT CONFIG ====================

/**
 * Вывести загруженный конфиг (safe version - скрыть secrets)
 */
function printConfig() {
  const safeConfig = { ...config };

  // Скрыть sensitive данные
  const secretKeys = [
    'JWT_SECRET',
    'JWT_REFRESH_SECRET',
    'SENDGRID_API_KEY',
    'AWS_SECRET_ACCESS_KEY',
    'STRIPE_API_KEY',
    'WEBHOOK_SECRET',
    'DB_PASSWORD',
  ];

  secretKeys.forEach((key) => {
    if (safeConfig[key]) {
      safeConfig[key] = '***HIDDEN***';
    }
  });

  console.log('\n=== Config Loaded ===');
  console.log(JSON.stringify(safeConfig, null, 2));
  console.log('=====================\n');
}

// ==================== INITIALIZATION ====================

// Валидировать при импорте
validateConfig();

// Вывести в development
if (config.NODE_ENV === 'development') {
  printConfig();
}

// ==================== EXPORTS ====================

module.exports = {
  config,
  getConfig,
  getDatabaseUrl,
  validateConfig,
  printConfig,
  // Type converters
  toBoolean,
  toNumber,
  toJSON,
  // Validators
  validateRequired,
  validateEnum,
  validateRange,
};

// ==================== EXAMPLE .env FILE ====================

/*
# .env

# Server
NODE_ENV=development
PORT=3000
HOST=0.0.0.0

# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=bookings_db
DB_POOL_MIN=2
DB_POOL_MAX=10

# Authentication
JWT_SECRET=your-super-secret-key-min-32-chars-long!!!
JWT_REFRESH_SECRET=your-refresh-secret-key-also-32-chars!!!
JWT_EXPIRY=15m

# APIs
SENDGRID_API_KEY=SG.xxxxxxxxxxxx
STRIPE_API_KEY=sk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# AWS
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
AWS_BUCKET_NAME=my-bucket

# Webhooks
WEBHOOK_SECRET=webhook-secret-key

# Logging
LOG_LEVEL=info
LOGS_DIR=./logs

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://example.com
CORS_CREDENTIALS=true

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# File Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# Caching
CACHE_ENABLED=true
CACHE_TTL=3600
REDIS_URL=redis://localhost:6379

# Monitoring
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
NEWRELIC_LICENSE_KEY=xxxxxxxxxxxx

# Feature Flags
FEATURE_RATE_LIMITING=true
FEATURE_CACHING=true
FEATURE_API_LOGGING=true
*/
