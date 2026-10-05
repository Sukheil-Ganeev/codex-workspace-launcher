# Quick Start Guide - First Payment in 30 Minutes

**Goal:** Accept your first payment without diving into complex documentation.

**What you'll build:** A simple payment form that accepts credit cards, processes the payment, and sends a confirmation.

**Stack:** Node.js + Express + Stripe (easiest option)

---

## Prerequisites (5 minutes)

**You need:**
- Node.js 18+ installed
- A Stripe account (free, signup at stripe.com)
- Basic terminal/command line knowledge
- Text editor

**Check Node.js:**
```bash
node --version  # Should show v18.0.0 or higher
npm --version   # Should show 8.0.0 or higher
```

If not installed: Download from [nodejs.org](https://nodejs.org/)

---

## Step 1: Create Stripe Account (5 minutes)

1. Go to [stripe.com](https://stripe.com) → Sign Up
2. Skip onboarding wizard (we're using test mode)
3. Dashboard → Developers → API keys
4. Copy these keys:
   - **Publishable key:** `pk_test_...` (safe to expose in browser)
   - **Secret key:** `sk_test_...` (NEVER expose, server-only)

**Important:** We're using **test mode** - no real money charged!

---

## Step 2: Project Setup (3 minutes)

```bash
# Create project directory
mkdir my-payment-app
cd my-payment-app

# Initialize Node.js project
npm init -y

# Install dependencies
npm install express stripe dotenv

# Create project structure
touch server.js .env
mkdir public
touch public/index.html
```

**Your directory should look like:**
```
my-payment-app/
├── server.js         (backend)
├── .env              (credentials)
├── public/
│   └── index.html    (frontend)
└── package.json
```

---

## Step 3: Configure Environment Variables (2 minutes)

**File: `.env`**

```bash
# Stripe API keys (test mode)
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY_HERE

# Server
PORT=3000
```

**⚠️ Security Rule #1:** NEVER commit `.env` to git!

Add to `.gitignore`:
```bash
echo ".env" >> .gitignore
```

---

## Step 4: Create Backend (5 minutes)

**File: `server.js`**

```javascript
require('dotenv').config();
const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

const app = express();
app.use(express.static('public'));
app.use(express.json());

// Create payment intent (server-side)
app.post('/create-payment-intent', async (req, res) => {
  try {
    const { amount, currency, email } = req.body;

    // Create payment intent
    const paymentIntent = await stripe.paymentIntents.create({
      amount: amount, // Amount in smallest currency unit (fils for AED)
      currency: currency,
      receipt_email: email,
      metadata: {
        customer_email: email,
        timestamp: new Date().toISOString(),
      },
    });

    res.json({ clientSecret: paymentIntent.client_secret });
  } catch (error) {
    console.error('Payment Intent Error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Handle successful payment (webhook simulation)
app.post('/payment-success', async (req, res) => {
  const { paymentIntentId } = req.body;

  console.log('✅ Payment succeeded:', paymentIntentId);

  // TODO: Add your business logic here:
  // - Update database
  // - Send confirmation email
  // - Notify WhatsApp

  res.json({ success: true });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
  console.log(`📝 Test mode: Using Stripe test keys`);
});
```

---

## Step 5: Create Frontend (7 minutes)

**File: `public/index.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Payment - Quick Start</title>
  <script src="https://js.stripe.com/v3/"></script>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f5f5f5;
      padding: 20px;
    }
    .container {
      max-width: 500px;
      margin: 40px auto;
      background: white;
      border-radius: 12px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.1);
      padding: 40px;
    }
    h1 {
      font-size: 24px;
      margin-bottom: 8px;
      color: #1a1a1a;
    }
    .price {
      font-size: 32px;
      font-weight: bold;
      color: #0066cc;
      margin-bottom: 30px;
    }
    label {
      display: block;
      margin-bottom: 8px;
      font-weight: 500;
      color: #4a4a4a;
    }
    input {
      width: 100%;
      padding: 12px;
      border: 1px solid #ddd;
      border-radius: 6px;
      font-size: 16px;
      margin-bottom: 20px;
    }
    input:focus {
      outline: none;
      border-color: #0066cc;
    }
    #card-element {
      padding: 12px;
      border: 1px solid #ddd;
      border-radius: 6px;
      background: white;
    }
    #card-errors {
      color: #d32f2f;
      font-size: 14px;
      margin-top: 8px;
      min-height: 20px;
    }
    button {
      width: 100%;
      padding: 16px;
      background: #0066cc;
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      margin-top: 20px;
      transition: background 0.2s;
    }
    button:hover {
      background: #0052a3;
    }
    button:disabled {
      background: #cccccc;
      cursor: not-allowed;
    }
    .success {
      text-align: center;
      padding: 40px 20px;
    }
    .success-icon {
      font-size: 64px;
      margin-bottom: 20px;
    }
    .success h2 {
      color: #2e7d32;
      margin-bottom: 10px;
    }
    .hidden {
      display: none;
    }
    .loading {
      display: inline-block;
      width: 16px;
      height: 16px;
      border: 2px solid #ffffff;
      border-radius: 50%;
      border-top-color: transparent;
      animation: spin 0.6s linear infinite;
      margin-left: 8px;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  </style>
</head>
<body>
  <div class="container">
    <!-- Payment Form -->
    <div id="payment-form-container">
      <h1>Desert Safari Tour</h1>
      <div class="price">250.00 AED</div>

      <form id="payment-form">
        <label for="name">Full Name</label>
        <input type="text" id="name" required placeholder="John Doe" value="Test User">

        <label for="email">Email</label>
        <input type="email" id="email" required placeholder="john@example.com" value="test@example.com">

        <label for="card-element">Card Information</label>
        <div id="card-element"></div>
        <div id="card-errors"></div>

        <button type="submit" id="submit-button">
          <span id="button-text">Pay Now</span>
          <span id="spinner" class="loading hidden"></span>
        </button>
      </form>

      <p style="text-align: center; color: #999; font-size: 14px; margin-top: 20px;">
        🔒 Secure payment powered by Stripe
      </p>
    </div>

    <!-- Success Message -->
    <div id="success-container" class="success hidden">
      <div class="success-icon">✅</div>
      <h2>Payment Successful!</h2>
      <p style="color: #666; margin-top: 10px;">
        Thank you for your payment. A confirmation email has been sent.
      </p>
    </div>
  </div>

  <script>
    // Replace with your publishable key from .env
    const STRIPE_PUBLISHABLE_KEY = 'pk_test_YOUR_KEY_HERE';

    // Initialize Stripe
    const stripe = Stripe(STRIPE_PUBLISHABLE_KEY);
    const elements = stripe.elements();

    // Create card element
    const cardElement = elements.create('card', {
      style: {
        base: {
          fontSize: '16px',
          color: '#32325d',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
          '::placeholder': {
            color: '#aab7c4',
          },
        },
        invalid: {
          color: '#d32f2f',
        },
      },
    });

    cardElement.mount('#card-element');

    // Display validation errors
    cardElement.on('change', (event) => {
      const displayError = document.getElementById('card-errors');
      displayError.textContent = event.error ? event.error.message : '';
    });

    // Handle form submission
    const form = document.getElementById('payment-form');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const submitButton = document.getElementById('submit-button');
      const buttonText = document.getElementById('button-text');
      const spinner = document.getElementById('spinner');

      // Disable button and show loading
      submitButton.disabled = true;
      buttonText.textContent = 'Processing...';
      spinner.classList.remove('hidden');

      const name = document.getElementById('name').value;
      const email = document.getElementById('email').value;

      try {
        // Step 1: Create payment intent on server
        const response = await fetch('/create-payment-intent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            amount: 25000, // 250.00 AED (in fils)
            currency: 'aed',
            email: email,
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to create payment intent');
        }

        const { clientSecret } = await response.json();

        // Step 2: Confirm payment with Stripe
        const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
          payment_method: {
            card: cardElement,
            billing_details: {
              name: name,
              email: email,
            },
          },
        });

        if (error) {
          // Show error to customer
          const errorElement = document.getElementById('card-errors');
          errorElement.textContent = error.message;

          submitButton.disabled = false;
          buttonText.textContent = 'Pay Now';
          spinner.classList.add('hidden');
        } else if (paymentIntent.status === 'succeeded') {
          // Payment successful!
          console.log('✅ Payment Intent:', paymentIntent.id);

          // Notify server
          await fetch('/payment-success', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ paymentIntentId: paymentIntent.id }),
          });

          // Show success message
          document.getElementById('payment-form-container').classList.add('hidden');
          document.getElementById('success-container').classList.remove('hidden');
        }
      } catch (err) {
        console.error('Payment error:', err);
        const errorElement = document.getElementById('card-errors');
        errorElement.textContent = 'An unexpected error occurred. Please try again.';

        submitButton.disabled = false;
        buttonText.textContent = 'Pay Now';
        spinner.classList.add('hidden');
      }
    });
  </script>
</body>
</html>
```

**⚠️ Important:** Replace `pk_test_YOUR_KEY_HERE` with your actual publishable key from Stripe Dashboard.

---

## Step 6: Test the Payment (5 minutes)

**Start the server:**
```bash
node server.js
```

**Open browser:**
```
http://localhost:3000
```

**Use Stripe test cards:**

| Card Number | Result |
|-------------|--------|
| `4242 4242 4242 4242` | ✅ Success |
| `4000 0000 0000 9995` | ❌ Declined (insufficient funds) |
| `4000 0025 0000 3155` | 🔐 Requires authentication (3D Secure) |

**Expiry:** Any future date (e.g., `12/25`)
**CVV:** Any 3 digits (e.g., `123`)
**ZIP:** Any 5 digits (e.g., `12345`)

**Test the flow:**
1. Fill form with test card `4242 4242 4242 4242`
2. Click "Pay Now"
3. Wait 1-2 seconds
4. See success message ✅

**Check Stripe Dashboard:**
- Go to Payments → All payments
- You'll see the test transaction

---

## Universal Payment Flow (Any Provider)

**This pattern works for Stripe, Telr, PayPal, etc:**

```
1. Client submits form
   ↓
2. Server creates payment intent/order
   (validates amount, currency, customer)
   ↓
3. Server returns client_secret/token
   ↓
4. Client confirms payment
   (enters card details securely)
   ↓
5. Provider processes payment
   ↓
6. Client receives result (success/failure)
   ↓
7. Server webhook receives confirmation
   (async, reliable notification)
   ↓
8. Server updates database & sends confirmation
```

**Key principle:** Never trust the client! Always verify payment status server-side via webhook.

---

## Webhook Basics (Production Requirement)

**Why webhooks?**
- Client can close browser before success
- Network can fail after payment succeeds
- User can manipulate client-side code

**Webhooks = reliable server-to-server notifications**

**Quick webhook setup:**

```javascript
app.post('/webhook', express.raw({type: 'application/json'}), async (req, res) => {
  const sig = req.headers['stripe-signature'];
  let event;

  try {
    // Verify webhook signature (security!)
    event = stripe.webhooks.constructEvent(
      req.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    console.error('⚠️ Webhook signature verification failed:', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // Handle events
  switch (event.type) {
    case 'payment_intent.succeeded':
      const paymentIntent = event.data.object;
      console.log('✅ Payment succeeded:', paymentIntent.id);

      // TODO: Update database, send email, notify WhatsApp
      break;

    case 'payment_intent.payment_failed':
      console.log('❌ Payment failed');
      break;

    default:
      console.log('Unhandled event type:', event.type);
  }

  res.json({received: true});
});
```

**Get webhook secret:**
1. Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://yourdomain.com/webhook`
3. Select events: `payment_intent.succeeded`, `payment_intent.payment_failed`
4. Copy signing secret → add to `.env`

**Local testing:**
```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe  # Mac
# or download from stripe.com/docs/stripe-cli

# Forward webhooks to localhost
stripe listen --forward-to localhost:3000/webhook
```

---

## Debugging Checklist

**❌ Payment not working?**

1. **Check API keys:**
   - Using test keys? (`pk_test_...`, `sk_test_...`)
   - Keys match? (publishable in HTML, secret in server.js)
   - Keys in `.env` loaded? (restart server after editing `.env`)

2. **Check console logs:**
   - Browser console (F12) - client errors
   - Server terminal - backend errors

3. **Check amount format:**
   - Amount in smallest currency unit
   - 100 AED = 10000 fils
   - Wrong: `100`, Correct: `10000`

4. **Check Stripe Dashboard:**
   - Go to Logs → All logs
   - See API errors in real-time

5. **Test card not working?**
   - Use `4242 4242 4242 4242` (always succeeds)
   - Check if test mode enabled in Dashboard

**Common errors:**

| Error | Solution |
|-------|----------|
| `Invalid API Key` | Check `.env` keys, restart server |
| `Amount must be at least...` | Minimum 0.50 AED (50 fils) |
| `No such payment_intent` | Client-server key mismatch |
| `Card declined` | Use test card `4242 4242 4242 4242` |

---

## Next Steps

**✅ You now have a working payment system!**

**To go to production:**

1. **Get live API keys** (Stripe Dashboard → switch to Live mode)
2. **Setup webhooks** (mandatory for production)
3. **Add HTTPS** (required for card handling)
4. **Add database** (store transactions)
5. **Add email confirmations** (Nodemailer)
6. **Add fraud prevention** (Stripe Radar)
7. **Add error handling** (retry logic, logging)
8. **Add monitoring** (Sentry, Datadog)

**Estimated time to production:** 1 day (following guides in this справочник)

**Further reading:**
- `02-stripe-complete-guide.md` - Deep dive into Stripe
- `07-security-compliance.md` - PCI DSS, fraud prevention
- `08-business-scenarios.md` - Deposits, refunds, splits

---

## Test Credentials Reference

**Stripe Test Cards:**

| Scenario | Card Number | Result |
|----------|-------------|--------|
| Success (any country) | `4242 4242 4242 4242` | ✅ |
| Decline (insufficient funds) | `4000 0000 0000 9995` | ❌ |
| 3D Secure (authentication) | `4000 0025 0000 3155` | 🔐 |
| Expired card | `4000 0000 0000 0069` | ❌ |
| Processing error | `4000 0000 0000 0119` | ⚠️ |

**Telr Test Credentials:**
```
Merchant ID: 21499 (test)
Store ID: 24101 (test)
Auth Key: (provided by Telr support)
```

**Test URLs:**
- Stripe Dashboard: https://dashboard.stripe.com/test/payments
- Telr Test Environment: https://secure.telr.com/test/
- Webhook Testing: https://webhook.site/

---

**You're ready to accept payments!** 🎉

**Total time:** ~30 minutes
**Result:** Working payment form accepting test transactions
**Next:** Choose your provider and integrate fully!
