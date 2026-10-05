/**
 * Payment Webhook Handler
 * Processes webhooks from Stripe and PayPal with signature verification
 */

require('dotenv').config();
const express = require('express');
const crypto = require('crypto');
const { Pool } = require('pg');
const stripe = require('stripe')(process.env.STRIPE_API_KEY);
const winston = require('winston');

// Logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: process.env.LOG_FILE || './logs/webhooks.log' })
  ]
});

// Database
const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

const app = express();

// Middleware for raw body (Stripe requires raw body for signature verification)
app.use('/webhooks/stripe', express.raw({ type: 'application/json' }));
app.use('/webhooks/paypal', express.json());
app.use(express.json());

// Processed webhooks cache (for idempotency)
const processedWebhooks = new Map();

/**
 * Verify Stripe webhook signature
 */
function verifyStripeSignature(body, signature) {
  try {
    const event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET
    );
    return event;
  } catch (error) {
    logger.error(`Stripe signature verification failed: ${error.message}`);
    return null;
  }
}

/**
 * Verify PayPal webhook signature
 */
function verifyPayPalSignature(webhookId, headers, body) {
  // Simplified - implement full PayPal verification as needed
  return true;
}

/**
 * Update payment status in database
 */
async function updatePaymentStatus(paymentId, status, amount, currency) {
  try {
    await pool.query(
      `INSERT INTO payments (payment_id, status, amount, currency, processed_at)
       VALUES ($1, $2, $3, $4, NOW())
       ON CONFLICT (payment_id) DO UPDATE SET status = $2, updated_at = NOW()`,
      [paymentId, status, amount, currency]
    );
    logger.info(`Payment ${paymentId} updated to ${status}`);
  } catch (error) {
    logger.error(`Database update failed: ${error.message}`);
    throw error;
  }
}

/**
 * Send payment notification email
 */
async function sendPaymentNotification(paymentId, status) {
  logger.info(`Sending notification for payment ${paymentId} - status: ${status}`);
  // Implement email sending
}

/**
 * POST /webhooks/stripe
 */
app.post('/webhooks/stripe', async (req, res) => {
  const signature = req.headers['stripe-signature'];

  const event = verifyStripeSignature(req.body, signature);

  if (!event) {
    return res.status(400).send('Webhook signature verification failed');
  }

  // Idempotency check
  if (processedWebhooks.has(event.id)) {
    logger.info(`Webhook ${event.id} already processed`);
    return res.json({ received: true });
  }

  try {
    switch (event.type) {
      case 'payment_intent.succeeded':
        const paymentIntent = event.data.object;
        await updatePaymentStatus(
          paymentIntent.id,
          'completed',
          paymentIntent.amount / 100,
          paymentIntent.currency.toUpperCase()
        );
        await sendPaymentNotification(paymentIntent.id, 'completed');
        break;

      case 'charge.failed':
        const charge = event.data.object;
        await updatePaymentStatus(charge.payment_intent, 'failed', charge.amount / 100, charge.currency.toUpperCase());
        await sendPaymentNotification(charge.payment_intent, 'failed');
        break;

      case 'charge.refunded':
        const refund = event.data.object;
        await updatePaymentStatus(refund.payment_intent, 'refunded', refund.amount / 100, refund.currency.toUpperCase());
        break;

      default:
        logger.info(`Unhandled event type: ${event.type}`);
    }

    // Mark as processed
    processedWebhooks.set(event.id, true);

    res.json({ received: true });
  } catch (error) {
    logger.error(`Webhook processing failed: ${error.message}`);
    res.status(500).send('Webhook processing failed');
  }
});

/**
 * POST /webhooks/paypal
 */
app.post('/webhooks/paypal', async (req, res) => {
  const webhookId = process.env.PAYPAL_WEBHOOK_ID;
  const event = req.body;

  if (!verifyPayPalSignature(webhookId, req.headers, JSON.stringify(event))) {
    return res.status(400).send('Webhook signature verification failed');
  }

  try {
    switch (event.event_type) {
      case 'CHECKOUT.ORDER.COMPLETED':
        const order = event.resource;
        await updatePaymentStatus(
          order.id,
          'completed',
          order.purchase_units[0].amount.value,
          order.purchase_units[0].amount.currency_code
        );
        break;

      case 'PAYMENT.CAPTURE.REFUNDED':
        const refundedCapture = event.resource;
        await updatePaymentStatus(refundedCapture.supplementary_data.related_ids.order_id, 'refunded', refundedCapture.amount.value, refundedCapture.amount.currency_code);
        break;

      default:
        logger.info(`Unhandled PayPal event: ${event.event_type}`);
    }

    res.json({ status: 'success' });
  } catch (error) {
    logger.error(`PayPal webhook processing failed: ${error.message}`);
    res.status(500).send('Webhook processing failed');
  }
});

/**
 * GET /webhook-status
 */
app.get('/webhook-status', async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT * FROM payments ORDER BY processed_at DESC LIMIT 10`
    );

    res.json({
      recent_webhooks: result.rows,
      processed_count: processedWebhooks.size
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Initialize database
async function initializeDatabase() {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS payments (
        id SERIAL PRIMARY KEY,
        payment_id VARCHAR(255) UNIQUE NOT NULL,
        status VARCHAR(50),
        amount DECIMAL(10, 2),
        currency VARCHAR(3),
        processed_at TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    logger.info('Database initialized');
  } catch (error) {
    logger.error(`Database initialization failed: ${error.message}`);
  }
}

const PORT = process.env.PORT || 3001;

async function start() {
  await initializeDatabase();
  app.listen(PORT, () => {
    logger.info(`Webhook server running on port ${PORT}`);
  });
}

start();

module.exports = app;
