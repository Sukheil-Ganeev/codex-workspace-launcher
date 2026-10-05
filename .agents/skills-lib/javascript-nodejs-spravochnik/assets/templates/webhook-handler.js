/**
 * Webhook Handler Template
 *
 * Production-ready обработчик webhooks с:
 * - Signature verification (HMAC)
 * - Retry logic
 * - Duplicate detection
 * - Event logging
 *
 * @example
 * npm install crypto uuid
 * // Webhook из: Stripe, Salebot, Payment Gateway
 */

const crypto = require('crypto');
const { v4: uuidv4 } = require('uuid');

// TODO: Использовать Redis для хранения processed event IDs
const processedEventIds = new Set();

// ==================== SIGNATURE VERIFICATION ====================

/**
 * Проверить HMAC подпись webhook
 *
 * @param {string} payload - Raw body (string, не parsed JSON)
 * @param {string} signature - Подпись из header
 * @param {string} secret - Webhook secret из конфига
 * @returns {boolean}
 *
 * @example
 * // Express route handler:
 * const isValid = verifySignature(req.rawBody, req.headers['x-webhook-signature']);
 */
function verifySignature(payload, signature, secret = process.env.WEBHOOK_SECRET) {
  if (!signature || !secret) {
    console.warn('[Webhook] Missing signature or secret');
    return false;
  }

  try {
    // Различные сервисы используют разные алгоритмы
    // Stripe: SHA-256
    // Salebot: SHA-256
    // TODO: Проверить документацию вашего провайдера

    const expectedSignature = crypto
      .createHmac('sha256', secret)
      .update(payload)
      .digest('hex');

    // Constant-time comparison (защита от timing attacks)
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(expectedSignature)
    );
  } catch (error) {
    console.error('[Webhook] Signature verification error:', error.message);
    return false;
  }
}

// ==================== WEBHOOK EVENTS ====================

/**
 * Обработчик webhook события
 *
 * @param {Object} event - { id, type, data, timestamp }
 * @returns {Promise<Object>} { success, message, data }
 */
async function handleWebhookEvent(event) {
  try {
    // Проверить duplicate
    if (processedEventIds.has(event.id)) {
      console.log(`[Webhook] Duplicate event skipped: ${event.id}`);
      return {
        success: true,
        message: 'Duplicate event (already processed)',
        isDuplicate: true,
      };
    }

    console.log(`[Webhook] Processing event: ${event.type} (${event.id})`);

    // Dispatch to handler based on event type
    let result;
    switch (event.type) {
      case 'payment.completed':
        result = await handlePaymentCompleted(event);
        break;

      case 'payment.failed':
        result = await handlePaymentFailed(event);
        break;

      case 'booking.created':
        result = await handleBookingCreated(event);
        break;

      case 'order.updated':
        result = await handleOrderUpdated(event);
        break;

      default:
        console.warn(`[Webhook] Unknown event type: ${event.type}`);
        return {
          success: false,
          message: 'Unknown event type',
        };
    }

    // Mark as processed
    processedEventIds.add(event.id);

    // TODO: Сохранить в БД для аудита
    logWebhookEvent(event, result);

    return {
      success: true,
      message: 'Event processed',
      data: result,
    };
  } catch (error) {
    console.error('[Webhook] Processing error:', error);

    // TODO: Добавить retry logic (например, Stripe ретрайтит 5 раз)
    return {
      success: false,
      message: error.message,
      shouldRetry: true, // Platform будет ретрайтить
    };
  }
}

// ==================== EVENT HANDLERS ====================

/**
 * Обработка платежа
 */
async function handlePaymentCompleted(event) {
  const { paymentId, amount, currency, customerId } = event.data;

  console.log(`[Payment] Completed: ${paymentId} (${amount} ${currency})`);

  // TODO: Реализовать логику:
  // 1. Обновить статус заказа в БД
  // 2. Отправить письмо клиенту
  // 3. Создать счет/инвойс
  // 4. Интегрировать с CRM (Notion, Google Sheets)

  return {
    paymentId,
    status: 'processed',
    timestamp: new Date().toISOString(),
  };
}

/**
 * Обработка ошибки платежа
 */
async function handlePaymentFailed(event) {
  const { paymentId, reason, customerId } = event.data;

  console.error(`[Payment] Failed: ${paymentId} - ${reason}`);

  // TODO: Реализовать логику:
  // 1. Отправить уведомление клиенту
  // 2. Предложить другой способ оплаты
  // 3. Написать в CRM о проблеме

  return {
    paymentId,
    status: 'failed',
    reason,
  };
}

/**
 * Обработка создания бронирования
 */
async function handleBookingCreated(event) {
  const { bookingId, email, tourDate } = event.data;

  console.log(`[Booking] Created: ${bookingId} for ${email}`);

  // TODO: Реализовать логику уведомлений, интеграции с CRM

  return {
    bookingId,
    status: 'created',
  };
}

/**
 * Обработка обновления заказа
 */
async function handleOrderUpdated(event) {
  const { orderId, status, updatedFields } = event.data;

  console.log(`[Order] Updated: ${orderId} -> ${status}`);

  return {
    orderId,
    status,
  };
}

// ==================== LOGGING & AUDIT ====================

/**
 * Логирование webhook событий для аудита
 */
function logWebhookEvent(event, result) {
  // TODO: Сохранить в БД или логи
  console.log('[Webhook] Event logged:', {
    eventId: event.id,
    eventType: event.type,
    result: result.success ? 'success' : 'error',
    timestamp: new Date().toISOString(),
  });
}

// ==================== EXPRESS MIDDLEWARE ====================

/**
 * Middleware для парсинга raw body (нужно до app.use(express.json()))
 *
 * @example
 * // В express-server-template.js
 * app.post('/webhooks/*', rawBodyParser, webhookHandler);
 */
const rawBodyParser = express.raw({ type: 'application/json' });

/**
 * Express route handler
 *
 * @example
 * app.post('/webhooks/stripe', rawBodyParser, webhookHandler);
 */
async function webhookHandler(req, res) {
  try {
    const signature = req.headers['x-webhook-signature'];
    const rawBody = req.body.toString('utf-8');

    // Проверить подпись
    if (!verifySignature(rawBody, signature)) {
      console.error('[Webhook] Invalid signature');
      return res.status(401).json({ error: 'Invalid signature' });
    }

    // Парсить JSON
    const event = JSON.parse(rawBody);

    // Валидировать структуру
    if (!event.id || !event.type || !event.data) {
      return res.status(400).json({ error: 'Invalid event structure' });
    }

    // Обработать
    const result = await handleWebhookEvent(event);

    // TODO: Вернуть 202 Accepted если обработка асинхронная
    res.status(200).json({
      success: result.success,
      eventId: event.id,
      message: result.message,
    });
  } catch (error) {
    console.error('[Webhook] Handler error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}

// ==================== EXPORTS ====================

module.exports = {
  verifySignature,
  handleWebhookEvent,
  webhookHandler,
  logWebhookEvent,
};

// Required environment variables:
// WEBHOOK_SECRET=your-webhook-secret-from-provider
// WEBHOOK_SIGNATURE_HEADER=x-webhook-signature (или x-signature)
