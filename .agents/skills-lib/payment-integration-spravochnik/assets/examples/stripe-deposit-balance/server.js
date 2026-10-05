/**
 * Stripe Deposit + Balance Payment Server
 *
 * Business scenario: Customer pays 30% deposit now, 70% balance later
 * Example: Desert Safari tour costs 1000 AED
 *  - Deposit: 300 AED (paid immediately)
 *  - Balance: 700 AED (paid 48h before tour)
 *
 * Features:
 * - Dual payment flow (deposit + balance)
 * - Payment status tracking
 * - Webhook handling
 * - Email confirmations
 * - Database persistence
 */

require('dotenv').config();
const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const { Pool } = require('pg');
const nodemailer = require('nodemailer');

const app = express();
const PORT = process.env.PORT || 3000;

// Database connection
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// Email transporter
const emailTransporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: process.env.SMTP_PORT,
  secure: true,
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS,
  },
});

// Middleware
app.use(express.static('public'));
app.use(express.json());

// For webhook signature verification, use raw body
app.use('/webhook', express.raw({ type: 'application/json' }));

/**
 * Create a booking with deposit payment
 * POST /api/create-booking
 */
app.post('/api/create-booking', async (req, res) => {
  try {
    const { customerName, email, phone, tourName, totalAmount, depositPercent = 30 } = req.body;

    // Validate input
    if (!customerName || !email || !tourName || !totalAmount) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    const depositAmount = Math.round(totalAmount * (depositPercent / 100));
    const balanceAmount = totalAmount - depositAmount;

    // Create booking in database
    const bookingResult = await pool.query(
      `INSERT INTO bookings (customer_name, email, phone, tour_name, total_amount, deposit_amount, balance_amount, status)
       VALUES ($1, $2, $3, $4, $5, $6, $7, 'pending')
       RETURNING id, booking_reference`,
      [customerName, email, phone, tourName, totalAmount, depositAmount, balanceAmount]
    );

    const booking = bookingResult.rows[0];

    // Create Stripe Payment Intent for deposit
    const paymentIntent = await stripe.paymentIntents.create({
      amount: depositAmount * 100, // Convert to fils (smallest currency unit)
      currency: 'aed',
      metadata: {
        booking_id: booking.id,
        booking_reference: booking.booking_reference,
        payment_type: 'deposit',
        tour_name: tourName,
      },
      description: `Deposit for ${tourName} - Booking ${booking.booking_reference}`,
    });

    // Store payment intent ID
    await pool.query(
      `UPDATE bookings SET deposit_payment_intent_id = $1 WHERE id = $2`,
      [paymentIntent.id, booking.id]
    );

    res.json({
      bookingId: booking.id,
      bookingReference: booking.booking_reference,
      depositAmount,
      balanceAmount,
      clientSecret: paymentIntent.client_secret,
    });
  } catch (error) {
    console.error('Create booking error:', error);
    res.status(500).json({ error: 'Failed to create booking' });
  }
});

/**
 * Create balance payment for existing booking
 * POST /api/create-balance-payment
 */
app.post('/api/create-balance-payment', async (req, res) => {
  try {
    const { bookingReference } = req.body;

    // Get booking
    const bookingResult = await pool.query(
      `SELECT * FROM bookings WHERE booking_reference = $1`,
      [bookingReference]
    );

    if (bookingResult.rows.length === 0) {
      return res.status(404).json({ error: 'Booking not found' });
    }

    const booking = bookingResult.rows[0];

    // Validate booking status
    if (booking.status !== 'deposit_paid') {
      return res.status(400).json({ error: 'Deposit not yet paid' });
    }

    if (booking.balance_paid_at) {
      return res.status(400).json({ error: 'Balance already paid' });
    }

    // Create Payment Intent for balance
    const paymentIntent = await stripe.paymentIntents.create({
      amount: booking.balance_amount * 100,
      currency: 'aed',
      metadata: {
        booking_id: booking.id,
        booking_reference: booking.booking_reference,
        payment_type: 'balance',
        tour_name: booking.tour_name,
      },
      description: `Balance payment for ${booking.tour_name} - Booking ${booking.booking_reference}`,
    });

    // Store payment intent ID
    await pool.query(
      `UPDATE bookings SET balance_payment_intent_id = $1 WHERE id = $2`,
      [paymentIntent.id, booking.id]
    );

    res.json({
      bookingReference: booking.booking_reference,
      balanceAmount: booking.balance_amount,
      clientSecret: paymentIntent.client_secret,
    });
  } catch (error) {
    console.error('Create balance payment error:', error);
    res.status(500).json({ error: 'Failed to create balance payment' });
  }
});

/**
 * Get booking status
 * GET /api/booking/:reference
 */
app.get('/api/booking/:reference', async (req, res) => {
  try {
    const { reference } = req.params;

    const result = await pool.query(
      `SELECT id, booking_reference, customer_name, email, tour_name,
              total_amount, deposit_amount, balance_amount, status,
              deposit_paid_at, balance_paid_at, created_at
       FROM bookings
       WHERE booking_reference = $1`,
      [reference]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Booking not found' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Get booking error:', error);
    res.status(500).json({ error: 'Failed to get booking' });
  }
});

/**
 * Stripe webhook handler
 * POST /webhook
 */
app.post('/webhook', async (req, res) => {
  const sig = req.headers['stripe-signature'];

  let event;
  try {
    event = stripe.webhooks.constructEvent(
      req.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // Handle the event
  try {
    switch (event.type) {
      case 'payment_intent.succeeded':
        await handlePaymentSuccess(event.data.object);
        break;

      case 'payment_intent.payment_failed':
        await handlePaymentFailure(event.data.object);
        break;

      default:
        console.log(`Unhandled event type ${event.type}`);
    }

    res.json({ received: true });
  } catch (error) {
    console.error('Webhook handler error:', error);
    res.status(500).json({ error: 'Webhook processing failed' });
  }
});

/**
 * Handle successful payment
 */
async function handlePaymentSuccess(paymentIntent) {
  const { metadata } = paymentIntent;
  const bookingId = metadata.booking_id;
  const paymentType = metadata.payment_type;

  if (paymentType === 'deposit') {
    // Update deposit payment
    await pool.query(
      `UPDATE bookings
       SET status = 'deposit_paid', deposit_paid_at = NOW()
       WHERE id = $1`,
      [bookingId]
    );

    // Send confirmation email
    const booking = await pool.query('SELECT * FROM bookings WHERE id = $1', [bookingId]);
    await sendDepositConfirmationEmail(booking.rows[0]);

  } else if (paymentType === 'balance') {
    // Update balance payment
    await pool.query(
      `UPDATE bookings
       SET status = 'fully_paid', balance_paid_at = NOW()
       WHERE id = $1`,
      [bookingId]
    );

    // Send final confirmation email
    const booking = await pool.query('SELECT * FROM bookings WHERE id = $1', [bookingId]);
    await sendFullPaymentConfirmationEmail(booking.rows[0]);
  }

  console.log(`Payment succeeded for booking ${bookingId} (${paymentType})`);
}

/**
 * Handle failed payment
 */
async function handlePaymentFailure(paymentIntent) {
  const { metadata } = paymentIntent;
  const bookingId = metadata.booking_id;

  await pool.query(
    `UPDATE bookings SET status = 'payment_failed' WHERE id = $1`,
    [bookingId]
  );

  console.log(`Payment failed for booking ${bookingId}`);
}

/**
 * Send deposit confirmation email
 */
async function sendDepositConfirmationEmail(booking) {
  try {
    await emailTransporter.sendMail({
      from: process.env.SMTP_FROM,
      to: booking.email,
      subject: `Deposit Confirmed - ${booking.tour_name}`,
      html: `
        <h2>Deposit Payment Confirmed</h2>
        <p>Dear ${booking.customer_name},</p>
        <p>Your deposit payment has been successfully received!</p>
        <ul>
          <li><strong>Booking Reference:</strong> ${booking.booking_reference}</li>
          <li><strong>Tour:</strong> ${booking.tour_name}</li>
          <li><strong>Deposit Paid:</strong> ${booking.deposit_amount} AED</li>
          <li><strong>Balance Due:</strong> ${booking.balance_amount} AED</li>
        </ul>
        <p>Please pay the balance 48 hours before your tour date.</p>
        <p>Balance payment link: ${process.env.APP_URL}/balance-payment.html?ref=${booking.booking_reference}</p>
      `,
    });
  } catch (error) {
    console.error('Email send error:', error);
  }
}

/**
 * Send full payment confirmation email
 */
async function sendFullPaymentConfirmationEmail(booking) {
  try {
    await emailTransporter.sendMail({
      from: process.env.SMTP_FROM,
      to: booking.email,
      subject: `Full Payment Confirmed - ${booking.tour_name}`,
      html: `
        <h2>Payment Complete!</h2>
        <p>Dear ${booking.customer_name},</p>
        <p>All payments have been received. Your booking is confirmed!</p>
        <ul>
          <li><strong>Booking Reference:</strong> ${booking.booking_reference}</li>
          <li><strong>Tour:</strong> ${booking.tour_name}</li>
          <li><strong>Total Paid:</strong> ${booking.total_amount} AED</li>
        </ul>
        <p>See you soon!</p>
      `,
    });
  } catch (error) {
    console.error('Email send error:', error);
  }
}

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
});
