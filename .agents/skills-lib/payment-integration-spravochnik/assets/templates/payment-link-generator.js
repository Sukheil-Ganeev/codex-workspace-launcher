/**
 * Payment Link Generator Template
 *
 * Generates unique payment links for WhatsApp/Telegram with expiration handling.
 * Perfect for tourism business when sending payment requests via messengers.
 *
 * Features:
 * - Unique payment links with expiration
 * - Short URL generation
 * - Tracking and analytics
 * - WhatsApp/Telegram formatted messages
 *
 * Usage:
 *   const link = await generatePaymentLink({
 *     amount: 250,
 *     currency: 'AED',
 *     customerName: 'John Doe',
 *     customerPhone: '+971501234567',
 *     description: 'Desert Safari Tour',
 *     expiresIn: 24 // hours
 *   });
 */

require('dotenv').config();
const crypto = require('crypto');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

// Database connection (adjust to your setup)
// const db = require('./database'); // PostgreSQL, MongoDB, etc.

/**
 * Generate unique payment link
 */
async function generatePaymentLink(options) {
  const {
    amount,
    currency = 'AED',
    customerName,
    customerPhone,
    customerEmail,
    description,
    expiresIn = 24, // hours
    metadata = {},
  } = options;

  // Validate inputs
  if (!amount || amount <= 0) {
    throw new Error('Amount must be greater than 0');
  }

  if (!customerPhone && !customerEmail) {
    throw new Error('Either customerPhone or customerEmail is required');
  }

  // Generate unique ID for this payment link
  const linkId = crypto.randomBytes(16).toString('hex');

  // Calculate expiration timestamp
  const expiresAt = new Date(Date.now() + expiresIn * 60 * 60 * 1000);

  // Create Stripe Payment Link (or Checkout Session)
  const session = await stripe.checkout.sessions.create({
    mode: 'payment',
    line_items: [
      {
        price_data: {
          currency: currency.toLowerCase(),
          product_data: {
            name: description || 'Tour Payment',
            description: `Payment for ${customerName}`,
          },
          unit_amount: Math.round(amount * 100), // Convert to smallest unit
        },
        quantity: 1,
      },
    ],
    customer_email: customerEmail,
    metadata: {
      link_id: linkId,
      customer_name: customerName,
      customer_phone: customerPhone,
      ...metadata,
    },
    success_url: `${process.env.BASE_URL}/payment-success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.BASE_URL}/payment-cancelled`,
    expires_at: Math.floor(expiresAt.getTime() / 1000), // Unix timestamp
  });

  // Save to database
  const paymentLink = {
    id: linkId,
    stripe_session_id: session.id,
    stripe_url: session.url,
    amount,
    currency,
    customer_name: customerName,
    customer_phone: customerPhone,
    customer_email: customerEmail,
    description,
    status: 'pending',
    expires_at: expiresAt,
    created_at: new Date(),
  };

  // TODO: Save to your database
  // await db.query('INSERT INTO payment_links SET ?', paymentLink);

  console.log('Payment link created:', paymentLink);

  return {
    linkId,
    url: session.url,
    shortUrl: await generateShortUrl(session.url), // Optional: use URL shortener
    expiresAt,
    whatsappMessage: formatWhatsAppMessage(paymentLink),
    telegramMessage: formatTelegramMessage(paymentLink),
  };
}

/**
 * Optional: Generate short URL using service like bit.ly
 */
async function generateShortUrl(longUrl) {
  // Simple implementation - you can integrate bit.ly, TinyURL, or self-hosted solution
  // For now, return original URL
  return longUrl;

  // Example with bit.ly:
  // const response = await fetch('https://api-ssl.bitly.com/v4/shorten', {
  //   method: 'POST',
  //   headers: {
  //     'Authorization': `Bearer ${process.env.BITLY_TOKEN}`,
  //     'Content-Type': 'application/json',
  //   },
  //   body: JSON.stringify({ long_url: longUrl }),
  // });
  // const data = await response.json();
  // return data.link;
}

/**
 * Format message for WhatsApp
 */
function formatWhatsAppMessage(paymentLink) {
  const { customer_name, amount, currency, description, stripe_url, expires_at } = paymentLink;

  const expiryTime = expires_at.toLocaleString('en-AE', {
    timeZone: 'Asia/Dubai',
    hour12: true
  });

  return `
✨ *Payment Request*

Hello ${customer_name}! 👋

Your payment details:
━━━━━━━━━━━━━━━━
📋 Service: *${description}*
💰 Amount: *${amount} ${currency}*
⏰ Valid until: ${expiryTime}

🔗 Pay now (secure link):
${stripe_url}

━━━━━━━━━━━━━━━━
✅ Fast & secure payment via Stripe
🔒 PCI DSS compliant
📧 Instant email confirmation

Need help? Just reply to this message! 😊
  `.trim();
}

/**
 * Format message for Telegram
 */
function formatTelegramMessage(paymentLink) {
  const { customer_name, amount, currency, description, stripe_url, expires_at } = paymentLink;

  const expiryTime = expires_at.toLocaleString('en-AE', {
    timeZone: 'Asia/Dubai',
    hour12: true
  });

  return `
<b>✨ Payment Request</b>

Hello ${customer_name}! 👋

<b>Your payment details:</b>
━━━━━━━━━━━━━━━━
📋 Service: <b>${description}</b>
💰 Amount: <b>${amount} ${currency}</b>
⏰ Valid until: ${expiryTime}

<a href="${stripe_url}">🔗 Click here to pay securely</a>

━━━━━━━━━━━━━━━━
✅ Fast & secure payment
🔒 PCI DSS compliant
📧 Instant confirmation

Need help? Just reply! 😊
  `.trim();
}

/**
 * Check payment status by link ID
 */
async function checkPaymentStatus(linkId) {
  // TODO: Query your database
  // const link = await db.query('SELECT * FROM payment_links WHERE id = ?', [linkId]);

  // If using Stripe session ID
  // const session = await stripe.checkout.sessions.retrieve(link.stripe_session_id);

  return {
    status: 'pending', // 'pending', 'paid', 'expired', 'cancelled'
    paid_at: null,
    // ...other fields
  };
}

/**
 * Expire old payment links (run as cron job)
 */
async function expireOldLinks() {
  const now = new Date();

  // TODO: Update database
  // await db.query(
  //   'UPDATE payment_links SET status = ? WHERE expires_at < ? AND status = ?',
  //   ['expired', now, 'pending']
  // );

  console.log('Expired old payment links');
}

// CLI usage example
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args[0] === 'generate') {
    generatePaymentLink({
      amount: 250,
      currency: 'AED',
      customerName: 'John Doe',
      customerPhone: '+971501234567',
      customerEmail: 'john@example.com',
      description: 'Desert Safari Tour',
      expiresIn: 24,
    })
    .then(result => {
      console.log('\n✅ Payment link generated successfully!\n');
      console.log('URL:', result.url);
      console.log('Expires:', result.expiresAt);
      console.log('\nWhatsApp Message:');
      console.log(result.whatsappMessage);
    })
    .catch(err => {
      console.error('Error:', err.message);
      process.exit(1);
    });
  } else if (args[0] === 'expire') {
    expireOldLinks()
      .then(() => process.exit(0))
      .catch(err => {
        console.error('Error:', err);
        process.exit(1);
      });
  } else {
    console.log(`
Usage:
  node payment-link-generator.js generate    # Generate sample payment link
  node payment-link-generator.js expire      # Expire old links
    `);
  }
}

module.exports = {
  generatePaymentLink,
  checkPaymentStatus,
  expireOldLinks,
};
