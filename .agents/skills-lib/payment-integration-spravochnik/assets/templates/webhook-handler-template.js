/**
 * Webhook Handler Template
 *
 * Express endpoint for handling payment webhooks with signature verification,
 * event routing, and database updates.
 *
 * Supports: Stripe, Telr, PayPal webhooks
 *
 * Features:
 * - Signature verification (security)
 * - Event routing to specific handlers
 * - Idempotency (prevent duplicate processing)
 * - Error handling and retry logic
 * - Database transaction updates
 * - Email notifications
 *
 * Usage:
 *   app.use('/webhooks/stripe', stripeWebhookHandler);
 *   app.use('/webhooks/telr', telrWebhookHandler);
 */

require('dotenv').config();
const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
// const db = require('./database'); // Your database connection
// const emailService = require('./email'); // Email service

const router = express.Router();

/**
 * Stripe Webhook Handler
 *
 * IMPORTANT: Use raw body for signature verification
 * app.use('/webhooks/stripe', express.raw({type: 'application/json'}), stripeWebhookHandler);
 */
async function stripeWebhookHandler(req, res) {
  const sig = req.headers['stripe-signature'];
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

  let event;

  try {
    // Verify webhook signature
    event = stripe.webhooks.constructEvent(req.body, sig, webhookSecret);
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // Check idempotency (prevent duplicate processing)
  const eventId = event.id;
  // const processed = await db.query('SELECT 1 FROM webhook_events WHERE event_id = ?', [eventId]);
  // if (processed.length > 0) {
  //   console.log('Event already processed:', eventId);
  //   return res.json({ received: true, note: 'Already processed' });
  // }

  console.log('Webhook event received:', event.type);

  // Route to specific handler based on event type
  try {
    switch (event.type) {
      case 'payment_intent.succeeded':
        await handlePaymentSuccess(event.data.object);
        break;

      case 'payment_intent.payment_failed':
        await handlePaymentFailed(event.data.object);
        break;

      case 'charge.refunded':
        await handleRefund(event.data.object);
        break;

      case 'checkout.session.completed':
        await handleCheckoutCompleted(event.data.object);
        break;

      case 'customer.subscription.created':
        await handleSubscriptionCreated(event.data.object);
        break;

      case 'customer.subscription.deleted':
        await handleSubscriptionCancelled(event.data.object);
        break;

      case 'invoice.payment_succeeded':
        await handleInvoicePaid(event.data.object);
        break;

      default:
        console.log('Unhandled event type:', event.type);
    }

    // Mark event as processed
    // await db.query('INSERT INTO webhook_events (event_id, event_type, processed_at) VALUES (?, ?, NOW())',
    //   [eventId, event.type]);

    // Return 200 to acknowledge receipt
    res.json({ received: true });
  } catch (err) {
    console.error('Error processing webhook:', err);
    // Return 500 so Stripe retries
    res.status(500).json({ error: 'Webhook processing failed' });
  }
}

/**
 * Handle successful payment
 */
async function handlePaymentSuccess(paymentIntent) {
  console.log('Payment succeeded:', paymentIntent.id);

  const {
    id,
    amount,
    currency,
    metadata,
    customer,
    receipt_email,
  } = paymentIntent;

  // Update database
  // await db.query(
  //   'UPDATE bookings SET payment_status = ?, payment_id = ?, paid_at = NOW() WHERE id = ?',
  //   ['paid', id, metadata.booking_id]
  // );

  // Send confirmation email
  // await emailService.sendPaymentConfirmation({
  //   email: receipt_email,
  //   amount: amount / 100,
  //   currency: currency.toUpperCase(),
  //   transactionId: id,
  //   customerName: metadata.customer_name,
  // });

  // Send WhatsApp notification (optional)
  // if (metadata.customer_phone) {
  //   await whatsappService.sendMessage(metadata.customer_phone, {
  //     template: 'payment_confirmed',
  //     params: {
  //       name: metadata.customer_name,
  //       amount: `${amount / 100} ${currency.toUpperCase()}`,
  //     },
  //   });
  // }

  console.log('Payment processed successfully:', id);
}

/**
 * Handle failed payment
 */
async function handlePaymentFailed(paymentIntent) {
  console.log('Payment failed:', paymentIntent.id);

  const { id, metadata, last_payment_error } = paymentIntent;

  // Update database
  // await db.query(
  //   'UPDATE bookings SET payment_status = ?, payment_error = ? WHERE id = ?',
  //   ['failed', last_payment_error?.message, metadata.booking_id]
  // );

  // Send failure notification
  // await emailService.sendPaymentFailed({
  //   email: metadata.customer_email,
  //   errorMessage: last_payment_error?.message,
  //   retryUrl: `${process.env.BASE_URL}/retry-payment?booking=${metadata.booking_id}`,
  // });

  console.log('Payment failure recorded:', id);
}

/**
 * Handle refund
 */
async function handleRefund(charge) {
  console.log('Refund processed:', charge.id);

  const { id, amount_refunded, currency, refunds } = charge;

  // Get refund details
  const refund = refunds.data[0];

  // Update database
  // await db.query(
  //   'INSERT INTO refunds (charge_id, refund_id, amount, currency, reason, created_at) VALUES (?, ?, ?, ?, ?, NOW())',
  //   [id, refund.id, amount_refunded / 100, currency, refund.reason]
  // );

  // Send refund confirmation email
  // await emailService.sendRefundConfirmation({
  //   email: charge.billing_details.email,
  //   amount: amount_refunded / 100,
  //   currency: currency.toUpperCase(),
  //   refundId: refund.id,
  // });

  console.log('Refund recorded:', refund.id);
}

/**
 * Handle checkout session completed
 */
async function handleCheckoutCompleted(session) {
  console.log('Checkout completed:', session.id);

  const { id, payment_intent, customer_email, metadata } = session;

  // Similar to handlePaymentSuccess but for Checkout Sessions
  // await db.query(
  //   'UPDATE bookings SET checkout_session_id = ?, payment_status = ? WHERE id = ?',
  //   [id, 'completed', metadata.booking_id]
  // );

  console.log('Checkout session processed:', id);
}

/**
 * Handle subscription created
 */
async function handleSubscriptionCreated(subscription) {
  console.log('Subscription created:', subscription.id);

  const { id, customer, items, current_period_end } = subscription;

  // Create subscription record
  // await db.query(
  //   'INSERT INTO subscriptions (stripe_subscription_id, customer_id, status, next_billing_date) VALUES (?, ?, ?, ?)',
  //   [id, customer, subscription.status, new Date(current_period_end * 1000)]
  // );

  console.log('Subscription recorded:', id);
}

/**
 * Handle subscription cancelled
 */
async function handleSubscriptionCancelled(subscription) {
  console.log('Subscription cancelled:', subscription.id);

  // Update database
  // await db.query(
  //   'UPDATE subscriptions SET status = ?, cancelled_at = NOW() WHERE stripe_subscription_id = ?',
  //   ['cancelled', subscription.id]
  // );

  console.log('Subscription cancellation processed:', subscription.id);
}

/**
 * Handle invoice paid (for subscriptions)
 */
async function handleInvoicePaid(invoice) {
  console.log('Invoice paid:', invoice.id);

  const { id, subscription, amount_paid, currency } = invoice;

  // Record payment
  // await db.query(
  //   'INSERT INTO subscription_payments (invoice_id, subscription_id, amount, currency, paid_at) VALUES (?, ?, ?, ?, NOW())',
  //   [id, subscription, amount_paid / 100, currency]
  // );

  console.log('Invoice payment recorded:', id);
}

/**
 * Telr Webhook Handler
 */
async function telrWebhookHandler(req, res) {
  const { order, status, message } = req.body;

  // TODO: Verify Telr signature (check Telr docs for verification method)

  console.log('Telr webhook received:', { order, status });

  try {
    if (status === 'paid') {
      // await db.query('UPDATE bookings SET payment_status = ? WHERE telr_order_id = ?', ['paid', order]);
      console.log('Telr payment confirmed:', order);
    } else if (status === 'failed') {
      // await db.query('UPDATE bookings SET payment_status = ?, payment_error = ? WHERE telr_order_id = ?',
      //   ['failed', message, order]);
      console.log('Telr payment failed:', order);
    }

    res.json({ received: true });
  } catch (err) {
    console.error('Telr webhook error:', err);
    res.status(500).json({ error: 'Processing failed' });
  }
}

/**
 * PayPal IPN Handler
 */
async function paypalIPNHandler(req, res) {
  // Send back to PayPal for verification
  const verificationBody = `cmd=_notify-validate&${new URLSearchParams(req.body).toString()}`;

  const response = await fetch(
    process.env.PAYPAL_MODE === 'live'
      ? 'https://www.paypal.com/cgi-bin/webscr'
      : 'https://www.sandbox.paypal.com/cgi-bin/webscr',
    {
      method: 'POST',
      body: verificationBody,
    }
  );

  const verification = await response.text();

  if (verification === 'VERIFIED') {
    const { txn_id, payment_status, mc_gross, custom } = req.body;

    if (payment_status === 'Completed') {
      // await db.query('UPDATE bookings SET payment_status = ?, paypal_txn_id = ? WHERE id = ?',
      //   ['paid', txn_id, custom]);
      console.log('PayPal payment verified:', txn_id);
    }

    res.status(200).send('OK');
  } else {
    console.error('PayPal IPN verification failed');
    res.status(400).send('Verification failed');
  }
}

module.exports = {
  stripeWebhookHandler,
  telrWebhookHandler,
  paypalIPNHandler,
};
