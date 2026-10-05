/**
 * Offline + Cash Hybrid Payment System
 * Partial online payment + remaining cash in office
 *
 * Flow:
 * 1. Customer pays 30% deposit online (Stripe/Telr)
 * 2. Remaining 70% paid in cash at office
 * 3. Auto-generate invoice for cash payment
 * 4. Receipt after full payment received
 */

require('dotenv').config();
const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const { Pool } = require('pg');
const PDFDocument = require('pdfkit');
const fs = require('fs');

const app = express();
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

app.use(express.json());
app.use(express.static('public'));

// Payment split configuration
const DEPOSIT_PERCENTAGE = 30; // 30% online, 70% cash

/**
 * Create booking with hybrid payment
 */
app.post('/create-booking', async (req, res) => {
  try {
    const { totalAmount, currency, customerName, customerEmail, tourName, tourDate } = req.body;

    const depositAmount = Math.round(totalAmount * (DEPOSIT_PERCENTAGE / 100));
    const cashAmount = totalAmount - depositAmount;

    // Create booking record
    const bookingResult = await pool.query(
      `INSERT INTO bookings 
       (customer_name, customer_email, tour_name, tour_date, 
        total_amount, deposit_amount, cash_amount, currency, status, created_at)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'pending_deposit', NOW())
       RETURNING *`,
      [customerName, customerEmail, tourName, tourDate, totalAmount, depositAmount, cashAmount, currency]
    );

    const booking = bookingResult.rows[0];

    // Create Stripe Payment Intent for deposit
    const paymentIntent = await stripe.paymentIntents.create({
      amount: depositAmount,
      currency: currency.toLowerCase(),
      metadata: {
        booking_id: booking.id,
        customer_name: customerName,
        tour_name: tourName,
        payment_type: 'deposit',
      },
      description: `Deposit ${DEPOSIT_PERCENTAGE}% for ${tourName}`,
    });

    res.json({
      bookingId: booking.id,
      clientSecret: paymentIntent.client_secret,
      depositAmount,
      cashAmount,
      totalAmount,
      currency,
    });

  } catch (error) {
    console.error('Booking creation failed:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Webhook - deposit paid successfully
 */
app.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  const sig = req.headers['stripe-signature'];

  try {
    const event = stripe.webhooks.constructEvent(
      req.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );

    if (event.type === 'payment_intent.succeeded') {
      const paymentIntent = event.data.object;
      const bookingId = paymentIntent.metadata.booking_id;

      // Update booking status
      await pool.query(
        `UPDATE bookings 
         SET status = 'deposit_paid', deposit_paid_at = NOW(), payment_intent_id = $1
         WHERE id = $2`,
        [paymentIntent.id, bookingId]
      );

      console.log(`✅ Deposit paid for booking ${bookingId}`);

      // TODO: Send confirmation email with cash payment instructions
    }

    res.json({ received: true });
  } catch (err) {
    console.error('Webhook error:', err.message);
    res.status(400).send(`Webhook Error: ${err.message}`);
  }
});

/**
 * Record cash payment in office
 */
app.post('/record-cash-payment', async (req, res) => {
  try {
    const { bookingId, amountReceived, receivedBy, paymentMethod, notes } = req.body;

    // Get booking details
    const bookingResult = await pool.query(
      'SELECT * FROM bookings WHERE id = $1',
      [bookingId]
    );

    if (bookingResult.rows.length === 0) {
      return res.status(404).json({ error: 'Booking not found' });
    }

    const booking = bookingResult.rows[0];

    if (booking.status !== 'deposit_paid') {
      return res.status(400).json({ error: 'Deposit not yet paid' });
    }

    // Record cash payment
    await pool.query(
      `INSERT INTO cash_payments 
       (booking_id, amount, currency, payment_method, received_by, notes, received_at)
       VALUES ($1, $2, $3, $4, $5, $6, NOW())`,
      [bookingId, amountReceived, booking.currency, paymentMethod, receivedBy, notes]
    );

    // Check if full payment completed
    const totalCashPaid = await pool.query(
      'SELECT SUM(amount) as total FROM cash_payments WHERE booking_id = $1',
      [bookingId]
    );

    const cashPaid = parseFloat(totalCashPaid.rows[0].total || 0);

    if (cashPaid >= booking.cash_amount) {
      // Full payment completed
      await pool.query(
        `UPDATE bookings 
         SET status = 'fully_paid', fully_paid_at = NOW()
         WHERE id = $1`,
        [bookingId]
      );

      // Generate receipt
      const receiptPath = await generateReceipt(booking, cashPaid);

      res.json({
        status: 'fully_paid',
        message: 'Payment completed',
        receiptPath,
      });
    } else {
      res.json({
        status: 'partial_cash_paid',
        remainingCash: booking.cash_amount - cashPaid,
      });
    }

  } catch (error) {
    console.error('Cash recording failed:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Generate receipt PDF
 */
async function generateReceipt(booking, cashPaid) {
  const doc = new PDFDocument();
  const fileName = `receipt-${booking.id}.pdf`;
  const filePath = `./receipts/${fileName}`;

  doc.pipe(fs.createWriteStream(filePath));

  // Header
  doc.fontSize(20).text('PAYMENT RECEIPT', { align: 'center' });
  doc.moveDown();

  // Booking details
  doc.fontSize(12);
  doc.text(`Receipt #: ${booking.id}`);
  doc.text(`Date: ${new Date().toLocaleDateString()}`);
  doc.text(`Customer: ${booking.customer_name}`);
  doc.text(`Email: ${booking.customer_email}`);
  doc.text(`Tour: ${booking.tour_name}`);
  doc.text(`Tour Date: ${new Date(booking.tour_date).toLocaleDateString()}`);
  doc.moveDown();

  // Payment breakdown
  doc.text('PAYMENT BREAKDOWN:');
  doc.text(`Total Amount: ${booking.total_amount / 100} ${booking.currency}`);
  doc.text(`Online Deposit (${DEPOSIT_PERCENTAGE}%): ${booking.deposit_amount / 100} ${booking.currency}`);
  doc.text(`Cash Payment: ${cashPaid / 100} ${booking.currency}`);
  doc.moveDown();

  doc.fontSize(14).text(`TOTAL PAID: ${booking.total_amount / 100} ${booking.currency}`, { underline: true });
  doc.moveDown();

  doc.fontSize(10).text('Thank you for your business!', { align: 'center' });

  doc.end();

  return filePath;
}

/**
 * Get booking status
 */
app.get('/booking/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const bookingResult = await pool.query(
      'SELECT * FROM bookings WHERE id = $1',
      [id]
    );

    if (bookingResult.rows.length === 0) {
      return res.status(404).json({ error: 'Booking not found' });
    }

    const booking = bookingResult.rows[0];

    // Get cash payments
    const cashPayments = await pool.query(
      'SELECT * FROM cash_payments WHERE booking_id = $1 ORDER BY received_at DESC',
      [id]
    );

    res.json({
      booking,
      cashPayments: cashPayments.rows,
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`💵 Hybrid Payment Server running on port ${PORT}`);
});
