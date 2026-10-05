# PayPal Integration Guide - Express Checkout for UAE Tourism

**Последнее обновление:** 2026-02-04
**Уровень:** Intermediate
**API Version:** REST API v2
**Цель:** Integrate PayPal Express Checkout for international tourism payments

---

## Введение

PayPal остаётся одним из самых популярных способов оплаты для международных клиентов:

**Преимущества:**
- **Trust factor:** 429M+ active accounts worldwide
- **No card required:** Customers can pay from PayPal balance
- **Buyer protection:** Customers feel safer (может быть минусом для merchant)
- **Multi-currency:** 25+ currencies supported
- **International:** Works in 200+ countries
- **One-click payments:** Repeat customers = faster checkout

**Недостатки:**
- **Higher fees:** 3.4% + fixed fee (vs Stripe 2.9%)
- **Chargebacks:** PayPal sides with buyers (risk для merchant)
- **Holds:** PayPal может hold funds до 21 дней (new merchants)
- **Account freezes:** PayPal известен внезапными account freezes
- **Limited в ОАЭ:** Не все UAE residents могут открыть PayPal account

**When to use PayPal:**
- International customers (Europe, USA, Asia)
- High-value bookings (customers want buyer protection)
- Repeat customers (saved payment methods)
- When customer specifically requests PayPal

**When NOT to use PayPal:**
- UAE local customers (prefer Telr/cards)
- Low-margin products (fees too high)
- High-risk industries (PayPal may freeze account)

---

## PayPal REST API vs Classic API

**Two API options:**

### REST API (Recommended)
- Modern, JSON-based
- Better documentation
- Active development
- OAuth 2.0 authentication
- Supports latest features

### Classic API (Legacy)
- SOAP/NVP based
- Still works but deprecated
- Limited new features
- Not recommended for new integrations

**We'll use REST API v2 in this guide.**

---

## Account Setup

### Step 1: Create PayPal Business Account

1. Go to https://www.paypal.com/ae/business
2. Click "Sign Up"
3. Select "Business Account"
4. Fill in business details:
   - Business name: Your company name
   - Business type: Travel Agency / Tour Operator
   - Country: United Arab Emirates
   - Email: Your business email

**Note:** PayPal Personal accounts cannot receive payments (must upgrade to Business).

### Step 2: Get API Credentials

1. Login to PayPal Developer Dashboard: https://developer.paypal.com
2. Click "Dashboard" → "My Apps & Credentials"
3. Switch to "Sandbox" tab (for testing)
4. Under "REST API apps", click "Create App"
5. App name: "UAE Tourism Payments"
6. Copy credentials:

**Sandbox credentials:**
```
Client ID: AXx...xyz (publishable)
Secret: ELx...abc (secret, server-only)
```

**Live credentials** (after testing):
Switch to "Live" tab, same process.

---

## PayPal Express Checkout Flow

**User journey:**

```
1. Customer clicks "Pay with PayPal"
   ↓
2. Redirect to PayPal login page
   ↓
3. Customer logs in / pays with card
   ↓
4. PayPal redirects back to your site
   ↓
5. You capture payment
   ↓
6. Show confirmation
```

**Two-step process:**
- **Create Order** (server-side): Get approval URL
- **Capture Payment** (after customer approves): Finalize transaction

---

## Implementation: Express Checkout

### Step 1: Install SDK

```bash
npm install @paypal/checkout-server-sdk
npm install dotenv
```

### Step 2: Configure PayPal Client

```javascript
// paypal-client.js
const paypal = require('@paypal/checkout-server-sdk');

function environment() {
  const clientId = process.env.PAYPAL_CLIENT_ID;
  const clientSecret = process.env.PAYPAL_CLIENT_SECRET;

  // Use Sandbox for testing, Live for production
  if (process.env.NODE_ENV === 'production') {
    return new paypal.core.LiveEnvironment(clientId, clientSecret);
  } else {
    return new paypal.core.SandboxEnvironment(clientId, clientSecret);
  }
}

function client() {
  return new paypal.core.PayPalHttpClient(environment());
}

module.exports = { client };
```

**Environment variables (.env):**
```bash
PAYPAL_CLIENT_ID=AXx...xyz
PAYPAL_CLIENT_SECRET=ELx...abc
NODE_ENV=development
PAYPAL_RETURN_URL=http://localhost:3000/paypal/success
PAYPAL_CANCEL_URL=http://localhost:3000/paypal/cancel
```

---

### Step 3: Create Order Endpoint

```javascript
// server.js
const express = require('express');
const paypal = require('@paypal/checkout-server-sdk');
const paypalClient = require('./paypal-client');

const app = express();
app.use(express.json());

// Create PayPal order
app.post('/api/paypal/create-order', async (req, res) => {
  const { amount, currency, bookingId, description } = req.body;

  // Create order request
  const request = new paypal.orders.OrdersCreateRequest();
  request.prefer('return=representation');
  request.requestBody({
    intent: 'CAPTURE', // или 'AUTHORIZE' (для pre-auth)
    purchase_units: [
      {
        reference_id: bookingId,
        description: description,
        amount: {
          currency_code: currency,
          value: amount
        }
      }
    ],
    application_context: {
      brand_name: 'UAE Tourism',
      landing_page: 'BILLING',
      user_action: 'PAY_NOW',
      return_url: process.env.PAYPAL_RETURN_URL,
      cancel_url: process.env.PAYPAL_CANCEL_URL
    }
  });

  try {
    const order = await paypalClient.client().execute(request);

    console.log(`✅ PayPal order created: ${order.result.id}`);

    // Save to database
    await db.query(
      'INSERT INTO paypal_payments (order_id, booking_id, amount, currency, status) VALUES ($1, $2, $3, $4, $5)',
      [order.result.id, bookingId, amount, currency, 'created']
    );

    // Return approval URL to client
    const approvalUrl = order.result.links.find(
      link => link.rel === 'approve'
    ).href;

    res.json({
      orderId: order.result.id,
      approvalUrl: approvalUrl
    });
  } catch (error) {
    console.error('❌ PayPal order creation failed:', error);
    res.status(500).json({ error: error.message });
  }
});
```

---

### Step 4: Frontend Integration

**Option 1: PayPal JavaScript SDK (Recommended)**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>PayPal Checkout</title>
</head>
<body>
  <div id="paypal-button-container"></div>

  <!-- PayPal SDK -->
  <script src="https://www.paypal.com/sdk/js?client-id=YOUR_CLIENT_ID&currency=AED"></script>

  <script>
    paypal.Buttons({
      // Create order on your server
      createOrder: async function() {
        const response = await fetch('/api/paypal/create-order', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            amount: '250.00',
            currency: 'AED',
            bookingId: 'BOOK-12345',
            description: 'Desert Safari Tour'
          })
        });

        const data = await response.json();
        return data.orderId;
      },

      // Capture payment on your server
      onApprove: async function(data) {
        const response = await fetch('/api/paypal/capture-order', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            orderId: data.orderID
          })
        });

        const details = await response.json();

        if (details.status === 'COMPLETED') {
          alert('Payment successful!');
          window.location.href = '/success';
        } else {
          alert('Payment failed');
        }
      },

      // Handle errors
      onError: function(err) {
        console.error('PayPal error:', err);
        alert('An error occurred during payment');
      }
    }).render('#paypal-button-container');
  </script>
</body>
</html>
```

**Option 2: Redirect Flow (Simpler)**

```javascript
// Frontend
async function payWithPayPal() {
  const response = await fetch('/api/paypal/create-order', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      amount: '250.00',
      currency: 'AED',
      bookingId: 'BOOK-12345',
      description: 'Desert Safari Tour'
    })
  });

  const { approvalUrl } = await response.json();

  // Redirect customer to PayPal
  window.location.href = approvalUrl;
}
```

---

### Step 5: Capture Payment

**After customer approves on PayPal, they return to your return_url:**

```javascript
// server.js
app.post('/api/paypal/capture-order', async (req, res) => {
  const { orderId } = req.body;

  const request = new paypal.orders.OrdersCaptureRequest(orderId);
  request.requestBody({});

  try {
    const capture = await paypalClient.client().execute(request);

    console.log(`✅ Payment captured: ${capture.result.id}`);

    // Update database
    await db.query(
      'UPDATE paypal_payments SET status = $1, capture_id = $2, captured_at = NOW() WHERE order_id = $3',
      ['completed', capture.result.id, orderId]
    );

    // Get transaction details
    const transaction = capture.result.purchase_units[0].payments.captures[0];

    res.json({
      status: capture.result.status,
      transactionId: transaction.id,
      amount: transaction.amount.value,
      currency: transaction.amount.currency_code
    });
  } catch (error) {
    console.error('❌ Capture failed:', error);
    res.status(500).json({ error: error.message });
  }
});
```

---

## Capture vs Authorize

**Two payment intents:**

### CAPTURE (Immediate payment)
- Money captured immediately
- Best for: Regular bookings, immediate services
- Customer charged right away

```javascript
request.requestBody({
  intent: 'CAPTURE',
  // ...
});
```

### AUTHORIZE (Pre-authorization)
- Money reserved but not captured
- Capture later (within 3 days for PayPal)
- Best for: Deposits, future services

```javascript
// 1. Create order with AUTHORIZE
request.requestBody({
  intent: 'AUTHORIZE',
  // ...
});

// 2. Later, capture authorization
app.post('/api/paypal/capture-authorization', async (req, res) => {
  const { authorizationId } = req.body;

  const request = new paypal.payments.AuthorizationsCaptureRequest(authorizationId);
  request.requestBody({
    amount: {
      currency_code: 'AED',
      value: '250.00'
    }
  });

  const capture = await paypalClient.client().execute(request);
  // ...
});
```

**Use case для туризма:**
```javascript
// Deposit flow
// 1. Authorize full amount (1000 AED)
// 2. Capture 30% now (300 AED)
// 3. Capture remaining 70% before tour (700 AED)
```

---

## IPN (Instant Payment Notification)

**Webhooks для PayPal.**

### Setup IPN

1. PayPal Dashboard → Account Settings → Notifications
2. IPN Enabled: Yes
3. Notification URL: `https://yoursite.com/paypal/ipn`

### Handle IPN

```javascript
// server.js
app.post('/paypal/ipn', express.urlencoded({ extended: false }), async (req, res) => {
  // 1. Verify IPN came from PayPal
  const verified = await verifyIPN(req.body);

  if (!verified) {
    console.error('⚠️  IPN verification failed');
    return res.status(400).send('INVALID');
  }

  // 2. Parse IPN data
  const paymentStatus = req.body.payment_status;
  const txnId = req.body.txn_id;
  const amount = req.body.mc_gross;
  const currency = req.body.mc_currency;
  const custom = req.body.custom; // Your booking ID

  console.log(`📨 IPN received: ${paymentStatus} for ${txnId}`);

  // 3. Handle payment status
  switch (paymentStatus) {
    case 'Completed':
      // Payment successful
      await db.query(
        'UPDATE paypal_payments SET status = $1 WHERE order_id = $2',
        ['completed', custom]
      );
      // Send confirmation email
      await sendConfirmationEmail(custom);
      break;

    case 'Pending':
      // Payment pending (eCheck, etc.)
      console.log('Payment pending...');
      break;

    case 'Refunded':
      // Payment refunded
      await handleRefund(txnId);
      break;

    case 'Reversed':
      // Chargeback!
      await handleChargeback(txnId);
      break;

    default:
      console.log(`Unhandled status: ${paymentStatus}`);
  }

  // 4. Acknowledge IPN
  res.status(200).send('OK');
});

async function verifyIPN(ipnData) {
  // Send IPN back to PayPal for verification
  const params = new URLSearchParams(ipnData);
  params.set('cmd', '_notify-validate');

  const response = await fetch('https://ipnpb.paypal.com/cgi-bin/webscr', {
    method: 'POST',
    body: params
  });

  const verification = await response.text();
  return verification === 'VERIFIED';
}
```

---

## Refunds

**Refund API:**

```javascript
app.post('/api/paypal/refund', async (req, res) => {
  const { captureId, amount, currency, reason } = req.body;

  const request = new paypal.payments.CapturesRefundRequest(captureId);
  request.requestBody({
    amount: {
      currency_code: currency,
      value: amount
    },
    note_to_payer: reason
  });

  try {
    const refund = await paypalClient.client().execute(request);

    console.log(`✅ Refund issued: ${refund.result.id}`);

    // Update database
    await db.query(
      'UPDATE paypal_payments SET status = $1, refund_id = $2 WHERE capture_id = $3',
      ['refunded', refund.result.id, captureId]
    );

    res.json({
      refundId: refund.result.id,
      status: refund.result.status,
      amount: refund.result.amount.value
    });
  } catch (error) {
    console.error('❌ Refund failed:', error);
    res.status(500).json({ error: error.message });
  }
});
```

**Refund time:**
- Credit/Debit card: 5-10 business days
- PayPal balance: Instant
- Bank account: 3-5 business days

---

## Disputes Handling

**PayPal Buyer Protection = Customer может dispute в течение 180 дней.**

### Types of Disputes

1. **Item Not Received (INR)**
   - Customer claims service не получен
   - Provide proof: Booking confirmations, tour photos, customer signatures

2. **Significantly Not As Described (SNAD)**
   - Tour/service не соответствует описанию
   - Provide proof: Original listing, communications, evidence of delivery

3. **Unauthorized Transaction**
   - Customer claims они не делали платёж
   - PayPal will investigate

### Prevent Disputes

**Best practices:**
- Clear descriptions (avoid overpromising)
- Immediate confirmations (email + WhatsApp)
- Photo evidence (customer on tour)
- Signed waivers/vouchers
- Track everything in CRM

### Handle Dispute

```javascript
// Monitor disputes via PayPal Dashboard
// Respond within 10 days with evidence:
// - Booking confirmation
// - Email trail
// - WhatsApp chat exports
// - Tour photos with customer
// - Signed vouchers
```

**If you lose dispute:** Amount refunded + $20 dispute fee.

---

## Multi-Currency

**PayPal supports 25+ currencies:**

```javascript
// Customer pays in their currency, you receive in yours
request.requestBody({
  intent: 'CAPTURE',
  purchase_units: [
    {
      amount: {
        currency_code: 'EUR', // Customer pays in EUR
        value: '100.00'
      }
    }
  ]
});

// You receive in AED (PayPal converts)
// Conversion rate: PayPal's rate (usually +2.5% markup)
```

**Available currencies:**
AED, USD, EUR, GBP, CAD, AUD, JPY, SGD, HKD, CHF, SEK, NOK, DKK, PLN, CZK, HUF, ILS, MXN, BRL, MYR, PHP, THB, TWD, NZD, RUB (suspended)

**Note:** Russian Ruble (RUB) suspended due to sanctions.

---

## Sandbox Testing

### Test Accounts

PayPal Sandbox provides test accounts:

1. Dashboard → Sandbox → Accounts
2. You have:
   - **Business account** (merchant, receives payments)
   - **Personal accounts** (buyers)

**Test login:**
```
Email: sb-buyer@personal.example.com
Password: (shown in dashboard)
```

### Test Cards

**No need for test cards - use Sandbox PayPal balance!**

Each personal account has $10,000 test balance.

### Test Flow

1. Create order via API
2. Open approval URL
3. Login with **sandbox personal account**
4. Complete payment
5. Verify capture works

---

## Production Checklist

**Before going live:**

- [ ] Switch to Live credentials (not Sandbox)
- [ ] Update `NODE_ENV=production`
- [ ] Test with small real payment ($1)
- [ ] Verify IPN endpoint accessible (HTTPS required)
- [ ] Setup webhook notifications
- [ ] Enable fraud protection (PayPal Seller Protection)
- [ ] Add Terms & Conditions link
- [ ] Display refund policy clearly
- [ ] Test refund flow
- [ ] Monitor PayPal account for holds/limits
- [ ] Document dispute response process

**PayPal may limit new accounts:**
- First 90 days: May hold funds up to 21 days
- Build history: Complete 25+ successful transactions
- Maintain <5% dispute rate

---

## Security Best Practices

### 1. Validate All Webhooks

```javascript
// ALWAYS verify IPN/webhooks
const verified = await verifyIPN(req.body);
if (!verified) {
  return res.status(400).send('INVALID');
}
```

### 2. Environment Variables

```bash
# .env
PAYPAL_CLIENT_ID=xxx
PAYPAL_CLIENT_SECRET=xxx # NEVER commit to Git!
```

### 3. Amount Verification

```javascript
// Verify amount matches expected
const expectedAmount = await getBookingAmount(bookingId);
if (parseFloat(paidAmount) !== expectedAmount) {
  throw new Error('Amount mismatch');
}
```

### 4. Idempotency

```javascript
// Prevent duplicate captures
const existing = await db.query(
  'SELECT * FROM paypal_payments WHERE order_id = $1 AND status = $2',
  [orderId, 'completed']
);

if (existing.rows.length > 0) {
  return res.json({ status: 'already_captured' });
}
```

---

## Complete Example

```javascript
// Full PayPal integration
const express = require('express');
const paypal = require('@paypal/checkout-server-sdk');
require('dotenv').config();

const app = express();
app.use(express.json());
app.use(express.static('public'));

// PayPal client
function environment() {
  const clientId = process.env.PAYPAL_CLIENT_ID;
  const clientSecret = process.env.PAYPAL_CLIENT_SECRET;

  return process.env.NODE_ENV === 'production'
    ? new paypal.core.LiveEnvironment(clientId, clientSecret)
    : new paypal.core.SandboxEnvironment(clientId, clientSecret);
}

const paypalClient = new paypal.core.PayPalHttpClient(environment());

// Create order
app.post('/api/paypal/create-order', async (req, res) => {
  const { amount, currency, bookingId } = req.body;

  const request = new paypal.orders.OrdersCreateRequest();
  request.prefer('return=representation');
  request.requestBody({
    intent: 'CAPTURE',
    purchase_units: [{
      reference_id: bookingId,
      amount: { currency_code: currency, value: amount }
    }],
    application_context: {
      return_url: `${process.env.BASE_URL}/paypal/success`,
      cancel_url: `${process.env.BASE_URL}/paypal/cancel`
    }
  });

  const order = await paypalClient.execute(request);
  res.json({ orderId: order.result.id });
});

// Capture order
app.post('/api/paypal/capture-order', async (req, res) => {
  const { orderId } = req.body;

  const request = new paypal.orders.OrdersCaptureRequest(orderId);
  const capture = await paypalClient.execute(request);

  res.json({
    status: capture.result.status,
    transactionId: capture.result.purchase_units[0].payments.captures[0].id
  });
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

---

## Troubleshooting

**Problem: "INVALID_REQUEST - Order cannot be captured"**

**Cause:** Order not approved by customer yet.

**Solution:** Ensure customer completed PayPal flow before capturing.

---

**Problem: "PERMISSION_DENIED"**

**Cause:** API credentials incorrect or expired.

**Solution:** Regenerate credentials in PayPal Dashboard.

---

**Problem: IPN not received**

**Checklist:**
- [ ] IPN enabled in PayPal settings
- [ ] Endpoint accessible via HTTPS
- [ ] Firewall not blocking PayPal IPs
- [ ] Endpoint returns 200 OK

---

**Problem: Account hold/limitation**

**Cause:** PayPal risk algorithm flagged your account.

**Solution:**
- Contact PayPal support
- Provide business documentation
- Build transaction history gradually

---

## Resources

**Official Docs:**
- REST API: https://developer.paypal.com/api/rest/
- Node.js SDK: https://github.com/paypal/Checkout-NodeJS-SDK
- Sandbox: https://developer.paypal.com/dashboard

**Tools:**
- Postman Collection: https://www.paypal.com/us/business/platforms-and-marketplaces/resources
- API Explorer: https://developer.paypal.com/api/rest/

**Support:**
- Developer Forum: https://www.paypal-community.com/
- MTS (Merchant Technical Support): PayPal Dashboard → Help

---

**Word count:** ~1,500 words
**Implementation time:** 2-3 hours
**Difficulty:** Intermediate

Next steps: Combine with Stripe/Telr for multi-provider setup (see `08-business-scenarios.md`).
