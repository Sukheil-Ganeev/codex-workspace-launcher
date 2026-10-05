/**
 * Refund Request Template
 *
 * Handles full and partial refunds with reason tracking and notifications.
 * Supports multiple payment providers (Stripe, Telr, PayPal).
 *
 * Features:
 * - Full and partial refunds
 * - Reason tracking for accounting
 * - Email notifications
 * - Refund policy validation
 * - Database logging
 *
 * Usage:
 *   const result = await processRefund({
 *     transactionId: 'pi_xxx',
 *     amount: 100, // Optional: for partial refund
 *     reason: 'customer_request',
 *     note: 'Customer cancelled 48 hours before tour'
 *   });
 */

require('dotenv').config();
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
// const db = require('./database');
// const emailService = require('./email');

/**
 * Process refund for any payment provider
 */
async function processRefund(options) {
  const {
    transactionId,
    provider = 'stripe', // 'stripe', 'telr', 'paypal'
    amount, // Optional: for partial refund (in AED, not fils)
    reason = 'requested_by_customer',
    note = '',
    notifyCustomer = true,
  } = options;

  // Validate inputs
  if (!transactionId) {
    throw new Error('Transaction ID is required');
  }

  // Validate refund policy
  // const booking = await db.query('SELECT * FROM bookings WHERE payment_id = ?', [transactionId]);
  // if (!booking) {
  //   throw new Error('Transaction not found');
  // }

  // const canRefund = await validateRefundPolicy(booking);
  // if (!canRefund.allowed) {
  //   throw new Error(`Refund not allowed: ${canRefund.reason}`);
  // }

  console.log(`Processing refund for ${transactionId}...`);

  let refundResult;

  switch (provider) {
    case 'stripe':
      refundResult = await processStripeRefund(transactionId, amount, reason, note);
      break;

    case 'telr':
      refundResult = await processTelrRefund(transactionId, amount, reason);
      break;

    case 'paypal':
      refundResult = await processPayPalRefund(transactionId, amount, reason);
      break;

    default:
      throw new Error(`Unsupported provider: ${provider}`);
  }

  // Log refund in database
  // await db.query(
  //   'INSERT INTO refunds (transaction_id, refund_id, provider, amount, reason, note, processed_at) VALUES (?, ?, ?, ?, ?, ?, NOW())',
  //   [transactionId, refundResult.refundId, provider, refundResult.amount, reason, note]
  // );

  // Update booking status
  // await db.query(
  //   'UPDATE bookings SET payment_status = ?, refund_id = ? WHERE payment_id = ?',
  //   ['refunded', refundResult.refundId, transactionId]
  // );

  // Send notification
  if (notifyCustomer) {
    // await emailService.sendRefundConfirmation({
    //   email: booking.customer_email,
    //   amount: refundResult.amount,
    //   currency: refundResult.currency,
    //   refundId: refundResult.refundId,
    //   estimatedDays: refundResult.estimatedDays,
    // });
  }

  console.log('Refund processed successfully:', refundResult.refundId);

  return refundResult;
}

/**
 * Process Stripe refund
 */
async function processStripeRefund(paymentIntentId, amount, reason, note) {
  try {
    // Get payment intent to validate
    const paymentIntent = await stripe.paymentIntents.retrieve(paymentIntentId);

    if (paymentIntent.status !== 'succeeded') {
      throw new Error(`Cannot refund payment with status: ${paymentIntent.status}`);
    }

    // Calculate refund amount
    const refundAmount = amount
      ? Math.round(amount * 100) // Convert AED to fils
      : paymentIntent.amount; // Full refund

    if (refundAmount > paymentIntent.amount) {
      throw new Error('Refund amount exceeds original payment');
    }

    // Create refund
    const refund = await stripe.refunds.create({
      payment_intent: paymentIntentId,
      amount: refundAmount,
      reason: reason,
      metadata: {
        note: note,
        refund_type: amount ? 'partial' : 'full',
      },
    });

    return {
      refundId: refund.id,
      amount: refund.amount / 100, // Convert back to AED
      currency: refund.currency.toUpperCase(),
      status: refund.status,
      estimatedDays: '5-10 business days',
    };
  } catch (err) {
    console.error('Stripe refund error:', err.message);
    throw new Error(`Stripe refund failed: ${err.message}`);
  }
}

/**
 * Process Telr refund (manual process - API may not support automatic refunds)
 */
async function processTelrRefund(orderId, amount, reason) {
  // Telr typically requires manual refund through merchant portal
  // This function creates a refund request record

  console.warn('Telr refunds require manual processing in merchant portal');

  // Create refund request
  const refundId = `telr_refund_${Date.now()}`;

  // TODO: Send notification to admin
  // await emailService.sendAdminNotification({
  //   subject: 'Manual Refund Required - Telr',
  //   orderId,
  //   amount,
  //   reason,
  // });

  return {
    refundId,
    amount,
    currency: 'AED',
    status: 'pending_manual_processing',
    estimatedDays: '7-14 business days',
    note: 'Requires manual processing in Telr merchant portal',
  };
}

/**
 * Process PayPal refund
 */
async function processPayPalRefund(captureId, amount, reason) {
  // PayPal REST API refund
  // Note: Requires PayPal SDK setup

  console.warn('PayPal refund implementation requires PayPal SDK');

  // Example implementation:
  // const paypal = require('@paypal/checkout-server-sdk');
  // const refund = await paypalClient.refund.create(captureId, {
  //   amount: {
  //     currency_code: 'AED',
  //     value: amount.toFixed(2),
  //   },
  // });

  return {
    refundId: `paypal_refund_${Date.now()}`,
    amount,
    currency: 'AED',
    status: 'pending',
    estimatedDays: '3-5 business days',
  };
}

/**
 * Validate refund policy
 * Returns: { allowed: boolean, reason: string }
 */
async function validateRefundPolicy(booking) {
  const now = new Date();
  const tourDate = new Date(booking.tour_date);
  const hoursUntilTour = (tourDate - now) / (1000 * 60 * 60);

  // Refund policy rules
  if (hoursUntilTour >= 48) {
    // Free cancellation 48+ hours before
    return { allowed: true, refundPercentage: 100 };
  } else if (hoursUntilTour >= 24) {
    // 50% refund 24-48 hours before
    return { allowed: true, refundPercentage: 50 };
  } else if (hoursUntilTour >= 0) {
    // No refund less than 24 hours
    return {
      allowed: false,
      reason: 'No refund available less than 24 hours before tour',
    };
  } else {
    // Tour already happened
    return {
      allowed: false,
      reason: 'Cannot refund past tour',
    };
  }
}

/**
 * Calculate refund amount based on policy
 */
function calculateRefundAmount(originalAmount, policy) {
  const refundAmount = (originalAmount * policy.refundPercentage) / 100;
  return Math.round(refundAmount * 100) / 100; // Round to 2 decimals
}

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log(`
Usage:
  node refund-request-template.js <transaction-id> [options]

Options:
  --amount=<amount>          Partial refund amount (AED)
  --reason=<reason>          Refund reason
  --note="<note>"            Additional notes
  --provider=<provider>      Provider: stripe, telr, paypal (default: stripe)
  --no-notify                Don't send customer notification

Example:
  node refund-request-template.js pi_3AbcDefGHIjklMNo --amount=100 --reason=customer_request
    `);
    process.exit(0);
  }

  const transactionId = args[0];
  const options = { transactionId };

  // Parse options
  args.slice(1).forEach((arg) => {
    if (arg.startsWith('--amount=')) {
      options.amount = parseFloat(arg.split('=')[1]);
    } else if (arg.startsWith('--reason=')) {
      options.reason = arg.split('=')[1];
    } else if (arg.startsWith('--note=')) {
      options.note = arg.split('=')[1].replace(/"/g, '');
    } else if (arg.startsWith('--provider=')) {
      options.provider = arg.split('=')[1];
    } else if (arg === '--no-notify') {
      options.notifyCustomer = false;
    }
  });

  processRefund(options)
    .then((result) => {
      console.log('\n✅ Refund processed successfully!');
      console.log('Refund ID:', result.refundId);
      console.log('Amount:', result.amount, result.currency);
      console.log('Status:', result.status);
      console.log('Estimated return:', result.estimatedDays);
      process.exit(0);
    })
    .catch((err) => {
      console.error('\n❌ Refund failed:', err.message);
      process.exit(1);
    });
}

module.exports = {
  processRefund,
  validateRefundPolicy,
  calculateRefundAmount,
};
