/**
 * Serverless Function Template (Netlify/Vercel)
 *
 * Production-ready template для serverless функций.
 * Поддерживает как асинхронный обработчик, так и обработку ошибок.
 *
 * @example
 * // Развернуть на Netlify/Vercel
 * // npm install dotenv
 */

const dotenv = require('dotenv');

dotenv.config();

/**
 * Основная serverless функция
 * @param {Object} event - Event от платформы
 * @param {Object} context - Context от платформы
 * @returns {Promise<Object>} HTTP ответ
 */
exports.handler = async (event, context) => {
  try {
    // CORS headers
    const headers = {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': process.env.ALLOWED_ORIGIN || '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    };

    // Handle preflight OPTIONS request
    if (event.httpMethod === 'OPTIONS') {
      return {
        statusCode: 200,
        headers,
        body: '',
      };
    }

    // Parse request body
    const body = event.body ? JSON.parse(event.body) : {};
    const method = event.httpMethod;
    const path = event.path;

    console.log(`[${new Date().toISOString()}] ${method} ${path}`, body);

    // TODO: Добавить вашу business logic здесь
    if (!body.data) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({
          error: 'Missing required field: data',
        }),
      };
    }

    // Обработка данных
    const result = await processData(body);

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        data: result,
        timestamp: new Date().toISOString(),
      }),
    };
  } catch (error) {
    console.error('[ERROR]', error);

    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? error.message : undefined,
      }),
    };
  }
};

/**
 * Обработчик основной логики
 * @param {Object} data - Входные данные
 * @returns {Promise<Object>}
 */
async function processData(data) {
  // TODO: Реализовать вашу логику обработки
  return {
    processed: true,
    input: data,
    processingTime: `${Date.now()}ms`,
  };
}

// Environment variables required:
// ALLOWED_ORIGIN=https://example.com
// NODE_ENV=production
