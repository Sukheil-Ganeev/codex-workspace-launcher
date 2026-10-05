# Stripe Complete Integration Guide

**Stripe** is the world's leading payment infrastructure provider, supporting 135+ currencies and used by millions of businesses globally.

**Best for:** International payments, excellent developer experience, advanced features (Radar fraud detection, instant refunds, comprehensive webhooks)

**Market position:** Gold standard for payment processing

---

## Table of Contents

1. Account Setup
2. API Keys Management
3. Payment Intents API (Recommended)
4. Stripe Elements (UI Components)
5. Webhooks (Critical for Production)
6. Multi-Currency Support
7. Refunds & Disputes
8. Stripe Radar (Fraud Prevention)
9. Testing with Test Cards
10. Production Checklist

---

## 1. Account Setup (15 minutes)

### Step 1: Create Account

1. Go to [stripe.com](https://stripe.com) → Sign Up
2. Verify email
3. Complete business profile:
   - **Business type:** Individual or Company
   - **Business location:** UAE
   - **Industry:** Travel & Tourism
   - **Website:** Your domain

### Step 2: Activate Account

**For test mode:** No activation needed!

**For live mode:**
- Provide business details (trade license for UAE)
- Upload ID verification
- Add bank account (for payouts)
- Typical approval: 1-3 business days

### Step 3: Configure Settings

**Dashboard → Settings:**

- ✅ **Business details** - Legal name, address
- ✅ **Branding** - Logo, colors (shows on checkout)
- ✅ **Email receipts** - Auto-send receipts to customers
- ✅ **Public details** - What customers see
- ✅ **Payout schedule** - Daily, weekly, or manual

---

## 2. API Keys Management

### Understanding API Keys

Stripe uses **two types of keys**:

**1. Publishable Key** (starts with `pk_`)
- ✅ Safe to embed in client-side code
- ✅ Can be in HTML, mobile apps
- Used for: Creating tokens, mounting Stripe Elements

**2. Secret Key** (starts with `sk_`)
- ❌ NEVER expose in client code
- ❌ NEVER commit to git
- Used for: Server-side API calls (creating charges, refunds)

### Test vs Live Mode

| Mode | Keys | Purpose | Real Money? |
|------|------|---------|-------------|
| **Test** | `pk_test_...`, `sk_test_...` | Development, testing | ❌ No |
| **Live** | `pk_live_...`, `sk_live_...` | Production | ✅ Yes |

**Get your keys:**
1. Dashboard → Developers → API keys
2. Toggle "Viewing test data" (top-right)
3. Copy both keys

### Secure Storage

**✅ Correct:**
```bash
# .env file
STRIPE_SECRET_KEY=sk_test_51abcdef...
STRIPE_PUBLISHABLE_KEY=pk_test_51abcdef...
STRIPE_WEBHOOK_SECRET=whsec_...
```

```javascript
// Load from environment
require('dotenv').config();
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
```

**❌ Wrong:**
```javascript
// NEVER hardcode!
const stripe = require('stripe')('sk_test_51abcdef...');
```

### Key Rotation (Security)

**When to rotate:**
- Key compromised (leaked in git, logs)
- Employee departure (had access to keys)
- Regular schedule (every 90 days)

**How to rotate:**
1. Dashboard → API keys → "Roll key"
2. Update `.env` with new key
3. Deploy changes
4. Old key works for 24 hours (grace period)

---

## 3. Payment Intents API (Recommended)

**Payment Intents** = Modern Stripe API for accepting payments.

**Why use Payment Intents?**
- ✅ Handles 3D Secure authentication automatically
- ✅ Supports Strong Customer Authentication (SCA)
- ✅ Tracks entire payment lifecycle
- ✅ Better error handling
- ✅ Works with all payment methods (cards, wallets)

### Payment Flow

```
1. Customer clicks "Pay"
   ↓
2. Client requests payment intent from server
   POST /create-payment-intent
   ↓
3. Server creates PaymentIntent
   stripe.paymentIntents.create({...})
   Returns client_secret
   ↓
4. Client confirms payment (Stripe.js)
   stripe.confirmCardPayment(client_secret, {...})
   ↓
5. Stripe processes payment
   (3D Secure if needed)
   ↓
6. Payment succeeds/fails
   ↓
7. Webhook notification to server
   payment_intent.succeeded
   ↓
8. Server fulfills order
   (update DB, send email)
```

### Server-Side: Create Payment Intent

```javascript
const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

const app = express();
app.use(express.json());

app.post('/create-payment-intent', async (req, res) => {
  try {
    const { amount, currency, customerEmail, metadata } = req.body;

    // Validate input
    if (!amount || amount < 50) {
      return res.status(400).json({ error: 'Amount must be at least 0.50 AED' });
    }

    const paymentIntent = await stripe.paymentIntents.create({
      amount: amount, // Amount in smallest unit (fils for AED)
      currency: currency || 'aed',

      // Optional: Automatic payment methods
      automatic_payment_methods: {
        enabled: true,
      },

      // Receipt email
      receipt_email: customerEmail,

      // Custom metadata (appears in Dashboard)
      metadata: {
        booking_id: metadata?.bookingId,
        tour_name: metadata?.tourName,
        customer_email: customerEmail,
      },

      // Description (shows on statement)
      description: `Tour booking - ${metadata?.tourName}`,

      // Idempotency key (prevent duplicate charges)
      idempotencyKey: `booking-${metadata?.bookingId}`,
    });

    res.json({
      clientSecret: paymentIntent.client_secret,
      paymentIntentId: paymentIntent.id,
    });
  } catch (error) {
    console.error('Payment Intent Error:', error);
    res.status(500).json({ error: error.message });
  }
});
```

### Client-Side: Confirm Payment

```javascript
// Initialize Stripe
const stripe = Stripe('pk_test_YOUR_PUBLISHABLE_KEY');
const elements = stripe.elements();

// Create card element
const cardElement = elements.create('card');
cardElement.mount('#card-element');

// Handle form submission
async function handlePayment(event) {
  event.preventDefault();

  // Step 1: Create payment intent
  const response = await fetch('/create-payment-intent', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      amount: 25000, // 250.00 AED
      currency: 'aed',
      customerEmail: 'customer@example.com',
      metadata: {
        bookingId: 'BOOK-12345',
        tourName: 'Desert Safari',
      },
    }),
  });

  const { clientSecret } = await response.json();

  // Step 2: Confirm payment
  const { error, paymentIntent } = await stripe.confirmCardPayment(
    clientSecret,
    {
      payment_method: {
        card: cardElement,
        billing_details: {
          name: document.getElementById('name').value,
          email: document.getElementById('email').value,
        },
      },
    }
  );

  if (error) {
    // Show error to customer
    console.error('Payment failed:', error.message);
    document.getElementById('error-message').textContent = error.message;
  } else if (paymentIntent.status === 'succeeded') {
    // Payment successful!
    console.log('Payment succeeded:', paymentIntent.id);
    showSuccessMessage();
  }
}
```

### Payment Intent Statuses

| Status | Description | Action Required |
|--------|-------------|-----------------|
| `requires_payment_method` | Waiting for payment details | Client submits card |
| `requires_confirmation` | Ready to confirm | Client calls confirmCardPayment |
| `requires_action` | 3D Secure needed | Stripe.js handles automatically |
| `processing` | Being processed | Wait |
| `succeeded` | ✅ Payment complete | Fulfill order |
| `canceled` | Canceled | Create new intent |

---

## 4. Stripe Elements (UI Components)

**Stripe Elements** = Pre-built, secure UI components for collecting payment info.

**Benefits:**
- ✅ PCI compliant (card data never touches your server)
- ✅ Mobile-responsive
- ✅ Automatic validation
- ✅ Customizable styling
- ✅ Real-time error messages

### Basic Setup

```html
<!-- Include Stripe.js -->
<script src="https://js.stripe.com/v3/"></script>

<!-- Card input container -->
<div id="card-element"></div>
<div id="card-errors"></div>
```

```javascript
const stripe = Stripe('pk_test_...');
const elements = stripe.elements();

// Create card element
const cardElement = elements.create('card', {
  style: {
    base: {
      fontSize: '16px',
      color: '#32325d',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      '::placeholder': {
        color: '#aab7c4',
      },
    },
    invalid: {
      color: '#fa755a',
      iconColor: '#fa755a',
    },
  },
});

cardElement.mount('#card-element');

// Display validation errors
cardElement.on('change', (event) => {
  const displayError = document.getElementById('card-errors');
  if (event.error) {
    displayError.textContent = event.error.message;
  } else {
    displayError.textContent = '';
  }
});
```

### Individual Elements (Advanced)

```javascript
// Separate inputs for card number, expiry, CVC
const cardNumber = elements.create('cardNumber');
const cardExpiry = elements.create('cardExpiry');
const cardCvc = elements.create('cardCvc');

cardNumber.mount('#card-number-element');
cardExpiry.mount('#card-expiry-element');
cardCvc.mount('#card-cvc-element');
```

### Styling Customization

```javascript
const style = {
  base: {
    color: '#32325d',
    fontFamily: 'Arial, sans-serif',
    fontSmoothing: 'antialiased',
    fontSize: '16px',
    '::placeholder': {
      color: '#aab7c4'
    }
  },
  invalid: {
    color: '#fa755a',
    iconColor: '#fa755a'
  }
};

const cardElement = elements.create('card', { style });
```

---

## 5. Webhooks (Critical for Production)

**Webhooks** = Server-to-server notifications from Stripe when events occur.

**Why mandatory?**
- Client can close browser before success page
- Network failures
- User manipulates client-side code
- Async payment methods (bank transfers)

### Setup Webhooks

**1. Add endpoint in Dashboard:**
- Dashboard → Developers → Webhooks
- Add endpoint: `https://yourdomain.com/webhook`
- Select events:
  - `payment_intent.succeeded`
  - `payment_intent.payment_failed`
  - `charge.refunded`
  - `charge.dispute.created`

**2. Get signing secret:**
- Copy webhook signing secret (starts with `whsec_`)
- Add to `.env`

### Handle Webhooks

```javascript
const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

const app = express();

// ⚠️ Important: Use raw body for webhook signature verification
app.post('/webhook',
  express.raw({ type: 'application/json' }),
  async (req, res) => {
    const sig = req.headers['stripe-signature'];
    let event;

    try {
      // Verify webhook signature (SECURITY!)
      event = stripe.webhooks.constructEvent(
        req.body,
        sig,
        process.env.STRIPE_WEBHOOK_SECRET
      );
    } catch (err) {
      console.error('⚠️ Webhook signature verification failed:', err.message);
      return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    // Handle the event
    switch (event.type) {
      case 'payment_intent.succeeded':
        const paymentIntent = event.data.object;
        console.log('✅ Payment succeeded:', paymentIntent.id);

        // Fulfill the order
        await fulfillOrder(paymentIntent);
        break;

      case 'payment_intent.payment_failed':
        const failedPayment = event.data.object;
        console.log('❌ Payment failed:', failedPayment.id);

        // Notify customer
        await notifyPaymentFailure(failedPayment);
        break;

      case 'charge.refunded':
        const refund = event.data.object;
        console.log('💰 Refund processed:', refund.id);

        // Update database
        await processRefund(refund);
        break;

      case 'charge.dispute.created':
        const dispute = event.data.object;
        console.log('⚠️ Dispute created:', dispute.id);

        // Alert team
        await alertDispute(dispute);
        break;

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    // Return 200 to acknowledge receipt
    res.json({ received: true });
  }
);

async function fulfillOrder(paymentIntent) {
  // 1. Update database
  await db.query(
    'UPDATE bookings SET status = $1, payment_id = $2 WHERE id = $3',
    ['paid', paymentIntent.id, paymentIntent.metadata.booking_id]
  );

  // 2. Send confirmation email
  await sendEmail({
    to: paymentIntent.receipt_email,
    subject: 'Payment Confirmation',
    body: `Your payment of ${paymentIntent.amount / 100} AED was successful!`,
  });

  // 3. Send WhatsApp confirmation
  await sendWhatsApp({
    to: paymentIntent.metadata.phone,
    message: '✅ Payment confirmed! See you on the tour!',
  });
}
```

### Webhook Best Practices

**1. Idempotency**
```javascript
// Store event ID to prevent duplicate processing
const eventId = event.id;
const processed = await db.query('SELECT * FROM processed_events WHERE event_id = $1', [eventId]);

if (processed.rows.length > 0) {
  return res.json({ received: true }); // Already processed
}

// Process event...

// Mark as processed
await db.query('INSERT INTO processed_events (event_id) VALUES ($1)', [eventId]);
```

**2. Error Handling**
```javascript
try {
  await fulfillOrder(paymentIntent);
  res.json({ received: true });
} catch (err) {
  console.error('Error fulfilling order:', err);
  // Return 500 → Stripe will retry
  res.status(500).json({ error: 'Internal error' });
}
```

**3. Fast Response**
```javascript
// Respond quickly (<5s), process async
res.json({ received: true });

// Queue heavy operations
queue.add('fulfill-order', { paymentIntentId: paymentIntent.id });
```

### Test Webhooks Locally

**Using Stripe CLI:**
```bash
# Install
brew install stripe/stripe-cli/stripe  # Mac
# or download from stripe.com/docs/stripe-cli

# Login
stripe login

# Forward webhooks to localhost
stripe listen --forward-to localhost:3000/webhook

# Trigger test events
stripe trigger payment_intent.succeeded
stripe trigger payment_intent.payment_failed
stripe trigger charge.refunded
```

---

## 6. Multi-Currency Support

**Stripe supports 135+ currencies!**

**UAE Tourism Common Currencies:**
- AED (UAE Dirham)
- USD (US Dollar)
- EUR (Euro)
- GBP (British Pound)
- RUB (Russian Ruble) - *Check current support*
- SAR (Saudi Riyal)

### Currency Codes (ISO 4217)

```javascript
const SUPPORTED_CURRENCIES = {
  aed: { name: 'UAE Dirham', symbol: 'د.إ', decimals: 2 },
  usd: { name: 'US Dollar', symbol: '$', decimals: 2 },
  eur: { name: 'Euro', symbol: '€', decimals: 2 },
  gbp: { name: 'British Pound', symbol: '£', decimals: 2 },
  rub: { name: 'Russian Ruble', symbol: '₽', decimals: 2 },
  sar: { name: 'Saudi Riyal', symbol: '﷼', decimals: 2 },
};
```

### Smallest Currency Unit

**Critical:** Stripe amounts are in smallest unit (no decimals!)

| Currency | Unit | Example |
|----------|------|---------|
| AED | Fils (1/100) | 100.00 AED = 10000 fils |
| USD | Cents (1/100) | 50.00 USD = 5000 cents |
| EUR | Cents (1/100) | 20.00 EUR = 2000 cents |

```javascript
function toStripeAmount(amount, currency) {
  const decimals = SUPPORTED_CURRENCIES[currency].decimals;
  return Math.round(amount * Math.pow(10, decimals));
}

function fromStripeAmount(stripeAmount, currency) {
  const decimals = SUPPORTED_CURRENCIES[currency].decimals;
  return stripeAmount / Math.pow(10, decimals);
}

// Usage
const priceAED = 250.00;
const stripeAmount = toStripeAmount(priceAED, 'aed'); // 25000
```

### Dynamic Currency Selection

```javascript
app.post('/create-payment-intent', async (req, res) => {
  const { amount, currency, customerCountry } = req.body;

  // Auto-select currency based on customer location
  const selectedCurrency = currency || detectCurrency(customerCountry);

  const paymentIntent = await stripe.paymentIntents.create({
    amount: toStripeAmount(amount, selectedCurrency),
    currency: selectedCurrency,
  });

  res.json({ clientSecret: paymentIntent.client_secret });
});

function detectCurrency(country) {
  const countryToCurrency = {
    AE: 'aed',
    US: 'usd',
    GB: 'gbp',
    DE: 'eur',
    FR: 'eur',
    RU: 'rub',
    SA: 'sar',
  };
  return countryToCurrency[country] || 'aed'; // Default AED
}
```

---

## 7. Refunds & Disputes

### Full Refund

```javascript
const refund = await stripe.refunds.create({
  payment_intent: 'pi_xxxxxxxxxxxxx',
  reason: 'requested_by_customer', // or 'duplicate', 'fraudulent'
});

console.log('Refund status:', refund.status); // 'succeeded'
```

### Partial Refund

```javascript
// Original charge: 1000 AED (100000 fils)
const partialRefund = await stripe.refunds.create({
  payment_intent: 'pi_xxxxxxxxxxxxx',
  amount: 50000, // Refund 500 AED (half)
  metadata: {
    reason: 'Partial cancellation',
    refunded_items: 'Tour cancelled, kept deposit',
  },
});
```

### Multiple Partial Refunds

```javascript
// Scenario: 1000 AED tour, customer cancels late
// Policy: Refund 70%, keep 30% cancellation fee

// Refund 1
await stripe.refunds.create({
  payment_intent: 'pi_xxxxxxxxxxxxx',
  amount: 70000, // 700 AED
  metadata: { reason: 'Cancellation refund (70%)' },
});

// Keep 30000 fils (300 AED) as cancellation fee
```

### Refund Timeline

| Method | Refund Time |
|--------|-------------|
| Credit cards | 5-10 business days |
| Debit cards | 5-10 business days |
| Bank transfers | 5-10 business days |

**Note:** Refund is instant on Stripe side, bank processing takes time.

### Disputes (Chargebacks)

**When customer disputes charge with bank:**

```javascript
// Webhook: charge.dispute.created
app.post('/webhook', async (req, res) => {
  const event = req.body;

  if (event.type === 'charge.dispute.created') {
    const dispute = event.data.object;

    console.log('⚠️ Dispute created:', dispute.id);
    console.log('Reason:', dispute.reason); // e.g., 'fraudulent'
    console.log('Amount:', dispute.amount);

    // Respond to dispute (within 7-21 days)
    await stripe.disputes.update(dispute.id, {
      evidence: {
        customer_name: 'John Doe',
        customer_email_address: 'john@example.com',
        customer_signature: 'https://yourbucket.com/signature.png',
        receipt: 'https://yourbucket.com/receipt.pdf',
        shipping_documentation: 'https://yourbucket.com/confirmation.pdf',
      },
    });

    // Alert team
    await sendSlackAlert(`⚠️ Dispute: ${dispute.id} - ${dispute.amount / 100} AED`);
  }
});
```

**Best practices:**
- Respond quickly (better chances)
- Provide clear evidence (receipts, contracts, confirmations)
- Keep records (emails, WhatsApp screenshots)

---

## 8. Stripe Radar (Fraud Prevention)

**Stripe Radar** = AI-powered fraud detection (included free!)

### Features

- ✅ Real-time risk scoring (0-100)
- ✅ 3D Secure triggers (high-risk transactions)
- ✅ Customizable rules
- ✅ Block suspicious cards/IPs
- ✅ Machine learning (learns from your data)

### Risk Score

```javascript
// After payment, check risk score
const charge = await stripe.charges.retrieve('ch_xxxxxxxxxxxxx');
console.log('Risk level:', charge.outcome.risk_level); // 'normal', 'elevated', 'highest'
console.log('Risk score:', charge.outcome.risk_score); // 0-100
```

### Custom Rules

**Dashboard → Radar → Rules:**

**Example rules:**
```
Block if ::ip_country:: != AE AND ::amount:: > 50000
  → Block non-UAE IPs for charges >500 AED

Request 3D Secure if ::risk_score:: > 60
  → Extra authentication for risky transactions

Block if ::email_domain:: in ['tempmail.com', 'guerrillamail.com']
  → Block disposable emails
```

### Integration with Fraud Detection

```javascript
app.post('/create-payment-intent', async (req, res) => {
  const { amount, customerEmail, customerIP } = req.body;

  // Check internal fraud database
  const isFraud = await checkFraudDatabase(customerEmail, customerIP);

  if (isFraud) {
    return res.status(403).json({ error: 'Payment blocked - fraud detected' });
  }

  const paymentIntent = await stripe.paymentIntents.create({
    amount: amount,
    currency: 'aed',
    // Radar automatically analyzes transaction
  });

  res.json({ clientSecret: paymentIntent.client_secret });
});
```

---

## 9. Testing with Test Cards

**Never test in live mode!** Use test mode with test cards.

### Common Test Cards

| Card Number | Scenario | Result |
|-------------|----------|--------|
| `4242 4242 4242 4242` | Success (any country) | ✅ Payment succeeds |
| `4000 0000 0000 9995` | Insufficient funds | ❌ Card declined |
| `4000 0025 0000 3155` | 3D Secure required | 🔐 Authentication popup |
| `4000 0000 0000 0069` | Expired card | ❌ Card expired |
| `4000 0000 0000 0341` | Attach fails | ❌ Card cannot be used |
| `4000 0000 0000 0119` | Processing error | ❌ Error occurred |

**For any test card:**
- Expiry: Any future date (e.g., `12/28`)
- CVV: Any 3 digits (e.g., `123`)
- ZIP: Any 5 digits (e.g., `12345`)

### Test 3D Secure

**Card:** `4000 0025 0000 3155`
**Flow:**
1. Enter card details
2. Click "Pay"
3. Stripe shows authentication popup
4. Click "Complete" (test mode)
5. Payment succeeds

### Test Webhooks

```bash
# Trigger test events
stripe trigger payment_intent.succeeded
stripe trigger payment_intent.payment_failed
stripe trigger charge.refunded
```

---

## 10. Production Checklist

**Before going live:**

### 1. Activate Live Mode
- [ ] Complete business verification
- [ ] Add bank account (payouts)
- [ ] Switch to live API keys

### 2. Security
- [ ] API keys in `.env` (not hardcoded)
- [ ] Webhook signature verification
- [ ] HTTPS enabled (required!)
- [ ] `.env` in `.gitignore`
- [ ] Rate limiting on endpoints

### 3. Webhooks
- [ ] Webhook endpoint live (https://yourdomain.com/webhook)
- [ ] Events configured: `payment_intent.succeeded`, `payment_intent.payment_failed`, `charge.refunded`
- [ ] Webhook secret in `.env`
- [ ] Idempotency handling
- [ ] Error handling (retry logic)

### 4. Error Handling
- [ ] Display user-friendly errors
- [ ] Log errors (without sensitive data)
- [ ] Monitoring (Sentry, Datadog)
- [ ] Alert on failures

### 5. Testing
- [ ] Test all payment flows
- [ ] Test 3D Secure
- [ ] Test refunds
- [ ] Test webhooks
- [ ] Load testing (simulate high volume)

### 6. Compliance
- [ ] Terms & Conditions
- [ ] Privacy Policy
- [ ] Refund Policy
- [ ] PCI DSS compliance (using Stripe Elements = compliant)

### 7. Business Logic
- [ ] Store transactions in database
- [ ] Send confirmation emails
- [ ] Update inventory/bookings
- [ ] Generate invoices
- [ ] Accounting integration

### 8. Monitoring
- [ ] Set up alerts (failed payments, disputes)
- [ ] Dashboard for analytics
- [ ] Reconciliation process
- [ ] Backup webhook handlers

---

## Summary

**Stripe strengths:**
- ✅ Best developer experience
- ✅ 135+ currencies
- ✅ Excellent documentation
- ✅ Advanced fraud prevention
- ✅ Instant refunds
- ✅ Reliable webhooks

**Best for:**
- International customers
- Multi-currency support
- High transaction volumes
- Businesses needing advanced features

**Fees:** 2.9% + $0.30 per transaction (AED equivalent)

**Setup time:** 30 minutes (test) → 1 day (production)

**Next steps:**
- Test integration with Quick Start Guide
- Set up webhooks
- Configure fraud rules
- Go live!

---

**Stripe Resources:**
- [Official Docs](https://stripe.com/docs)
- [API Reference](https://stripe.com/docs/api)
- [Test Cards](https://stripe.com/docs/testing)
- [Stripe CLI](https://stripe.com/docs/stripe-cli)
- [Support](https://support.stripe.com/)
