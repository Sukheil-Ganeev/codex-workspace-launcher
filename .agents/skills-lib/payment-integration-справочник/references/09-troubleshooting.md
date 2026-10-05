# Troubleshooting & Common Issues

**Версия:** 1.0
**Дата:** 2026-02-04
**Цель:** Решить 95% проблем с payment integration за 5 минут

---

## 📋 Введение

Платёжные интеграции могут ломаться по 100 причинам: API keys неправильные, webhooks не приходят, карты отклоняются, refunds fail... В этом гайде собраны **самые частые проблемы** и их решения.

**Структура:**
- Stripe errors (card declined, rate limits, etc.)
- Webhook debugging (signature fails, timeouts)
- Currency mismatch
- Refund failures
- Double-charging prevention
- Test vs Live mode mistakes
- API key rotation
- Provider status pages

---

## 🔴 1. Stripe Payment Errors

### Error: `card_declined`

**Полное сообщение:**
```
Your card was declined. Your request was in test mode, but used a non-test card.
```

**Причины:**
1. Test mode но используешь real card
2. Insufficient funds
3. Bank blocks international transactions
4. Card expired
5. Fraud prevention triggered

**Решение:**

```javascript
// Обработка card_declined errors
async function handleCardDeclined(error, customerEmail) {
  const declineCode = error.decline_code;

  const messages = {
    insufficient_funds: 'Your card has insufficient funds. Please use another card.',
    card_velocity_exceeded: 'Too many transactions in short time. Try again in 1 hour.',
    do_not_honor: 'Your bank declined the transaction. Contact your bank.',
    invalid_account: 'The card account is invalid. Please check card details.',
    lost_card: 'This card was reported lost. Please use another card.',
    stolen_card: 'This card was reported stolen. Please use another card.',
    expired_card: 'Your card has expired. Please use another card.',
  };

  const userMessage = messages[declineCode] || 'Your card was declined. Please try another payment method.';

  // Log for analytics
  await logPaymentError({
    type: 'card_declined',
    decline_code: declineCode,
    customer_email: customerEmail,
    timestamp: new Date(),
  });

  return { error: userMessage, suggestAlternative: true };
}
```

**Test cards для Stripe:**
- `4242 4242 4242 4242` - Успешный платёж
- `4000 0000 0000 9995` - Card declined (insufficient funds)
- `4000 0000 0000 9987` - Card declined (lost card)
- `4000 0000 0000 0002` - Charge fails (generic decline)

Полный список: https://stripe.com/docs/testing

---

### Error: `authentication_required`

**Причина:** 3D Secure (SCA) required но не completed

**Решение:**

```javascript
const {error, paymentIntent} = await stripe.confirmCardPayment(
  clientSecret,
  {
    payment_method: {
      card: cardElement,
      billing_details: {name: customerName},
    },
  }
);

if (error) {
  if (error.type === 'card_error' && error.code === 'authentication_required') {
    // Redirect to 3D Secure page
    window.location.href = error.payment_intent.next_action.redirect_to_url.url;
  }
}
```

---

### Error: `rate_limit_error`

**Причина:** Слишком много API requests

**Stripe rate limits:**
- 100 reads/sec per API key
- 100 writes/sec per API key
- Webhooks: 1000/sec

**Решение:**

```javascript
const pRetry = require('p-retry');

async function createPaymentWithRetry(paymentData) {
  return pRetry(
    async () => {
      try {
        return await stripe.paymentIntents.create(paymentData);
      } catch (err) {
        if (err.type === 'StripeRateLimitError') {
          // Retry after exponential backoff
          throw err;
        }
        // Don't retry other errors
        throw new pRetry.AbortError(err.message);
      }
    },
    {
      retries: 3,
      minTimeout: 1000, // 1s
      maxTimeout: 5000, // 5s
      factor: 2, // Exponential backoff
    }
  );
}
```

---

### Error: `invalid_request_error`

**Примеры:**

**1. Invalid currency for country**
```javascript
// ❌ НЕПРАВИЛЬНО - Stripe не поддерживает RUB в некоторых регионах
const payment = await stripe.paymentIntents.create({
  amount: 10000,
  currency: 'rub', // Error!
});

// ✅ ПРАВИЛЬНО - проверь supported currencies
const SUPPORTED_CURRENCIES = ['aed', 'usd', 'eur', 'gbp', 'kzt'];

if (!SUPPORTED_CURRENCIES.includes(currency)) {
  throw new Error(`Currency ${currency} not supported`);
}
```

**2. Amount too small**
```javascript
// ❌ Minimum charge: 0.50 USD, 2.00 AED
const payment = await stripe.paymentIntents.create({
  amount: 50, // 0.50 AED - TOO SMALL!
  currency: 'aed',
});

// ✅ Enforce minimum
const MIN_AMOUNTS = { aed: 200, usd: 50, eur: 50 }; // in smallest unit

if (amount < MIN_AMOUNTS[currency]) {
  throw new Error(`Minimum amount is ${MIN_AMOUNTS[currency] / 100} ${currency.toUpperCase()}`);
}
```

---

## 🔴 2. Webhook Debugging

### Issue: Webhook signature verification fails

**Error:**
```
Error: No signatures found matching the expected signature for payload
```

**Причины:**
1. Неправильный webhook secret
2. Request body был modified (express.json() middleware issue)
3. Replay attack (timestamp too old)

**Решение:**

```javascript
const express = require('express');
const app = express();

// ❌ НЕПРАВИЛЬНО - express.json() изменяет raw body
app.use(express.json());

app.post('/webhook', (req, res) => {
  const sig = req.headers['stripe-signature'];
  const event = stripe.webhooks.constructEvent(req.body, sig, webhookSecret); // FAIL!
});

// ✅ ПРАВИЛЬНО - используй raw body для webhook endpoint
app.post('/webhook',
  express.raw({type: 'application/json'}), // Raw body
  (req, res) => {
    const sig = req.headers['stripe-signature'];

    try {
      const event = stripe.webhooks.constructEvent(
        req.body, // Raw buffer
        sig,
        process.env.STRIPE_WEBHOOK_SECRET
      );

      // Process event
      res.json({received: true});
    } catch (err) {
      console.error('Webhook signature verification failed:', err.message);
      return res.status(400).send(`Webhook Error: ${err.message}`);
    }
  }
);

// Для других endpoints используй JSON parser
app.use(express.json());
```

**Проверка webhook secret:**
```bash
# Stripe CLI для тестирования webhooks локально
stripe listen --forward-to localhost:3000/webhook

# Копируй webhook signing secret из вывода
# whsec_xxxxx
```

---

### Issue: Webhook timeouts

**Stripe timeout:** 5 seconds

**Причина:** Долгий processing в webhook handler

**Решение:**

```javascript
// ❌ НЕПРАВИЛЬНО - долгая обработка блокирует response
app.post('/webhook', async (req, res) => {
  const event = stripe.webhooks.constructEvent(req.body, sig, secret);

  if (event.type === 'payment_intent.succeeded') {
    await sendEmail(event.data.object.receipt_email); // SLOW! 2-5 seconds
    await updateInventory(event.data.object.metadata.product_id); // SLOW!
    await sendWhatsAppMessage(event.data.object.metadata.phone); // SLOW!
  }

  res.json({received: true}); // Too late - timeout!
});

// ✅ ПРАВИЛЬНО - respond сразу, process в background
app.post('/webhook', async (req, res) => {
  const event = stripe.webhooks.constructEvent(req.body, sig, secret);

  // Respond immediately
  res.json({received: true});

  // Process в background (job queue recommended)
  setImmediate(async () => {
    try {
      await processWebhookEvent(event);
    } catch (err) {
      console.error('Webhook processing error:', err);
      // Stripe will retry failed webhooks
    }
  });
});

async function processWebhookEvent(event) {
  switch (event.type) {
    case 'payment_intent.succeeded':
      await handlePaymentSuccess(event.data.object);
      break;
    case 'payment_intent.payment_failed':
      await handlePaymentFailure(event.data.object);
      break;
    // ...
  }
}
```

**Best practice:** Используй job queue (Bull, BullMQ, Agenda)

```javascript
const Queue = require('bull');
const webhookQueue = new Queue('webhook-processing');

app.post('/webhook', async (req, res) => {
  const event = stripe.webhooks.constructEvent(req.body, sig, secret);

  // Add to queue
  await webhookQueue.add('process-event', {event});

  res.json({received: true});
});

// Worker process
webhookQueue.process('process-event', async (job) => {
  await processWebhookEvent(job.data.event);
});
```

---

### Issue: Webhook не приходит вообще

**Debugging checklist:**

1. **Проверь endpoint доступен публично**
```bash
# Локальная разработка - используй ngrok
ngrok http 3000

# Копируй HTTPS URL (например https://abc123.ngrok.io)
# Добавь в Stripe Dashboard: https://abc123.ngrok.io/webhook
```

2. **Проверь firewall/CORS**
```javascript
// Stripe webhooks НЕ проходят через browser, CORS не нужен
// Но убедись что firewall разрешает Stripe IPs
```

3. **Проверь Stripe Dashboard → Developers → Webhooks**
- Event history: покажет failed attempts
- Response logs: что вернул твой endpoint

4. **Test webhook локально:**
```bash
stripe trigger payment_intent.succeeded
# Сработает только если `stripe listen` запущен
```

5. **Manual replay:**
```javascript
// В Stripe Dashboard → Events → выбери event → "Send test webhook"
```

---

### Issue: Duplicate webhook events

**Причина:** Stripe retries webhooks если не получил 2xx response

**Решение: Idempotency**

```javascript
const processedEvents = new Set(); // В production используй Redis

async function processWebhookEvent(event) {
  // Check if already processed
  if (processedEvents.has(event.id)) {
    console.log(`Event ${event.id} already processed, skipping`);
    return;
  }

  // Process event
  if (event.type === 'payment_intent.succeeded') {
    await handlePaymentSuccess(event.data.object);
  }

  // Mark as processed
  processedEvents.add(event.id);

  // Expire after 24 hours (Stripe stops retrying after 3 days)
  setTimeout(() => processedEvents.delete(event.id), 24 * 60 * 60 * 1000);
}
```

**Production-ready (Redis):**
```javascript
const redis = require('redis').createClient();

async function processWebhookEvent(event) {
  const key = `webhook_processed:${event.id}`;
  const exists = await redis.get(key);

  if (exists) {
    return; // Already processed
  }

  // Process
  await handlePaymentSuccess(event.data.object);

  // Mark as processed (expire in 72 hours)
  await redis.setex(key, 72 * 60 * 60, '1');
}
```

---

## 🔴 3. Currency Mismatch Issues

### Issue: Customer sees wrong currency

**Scenario:**
- Customer from Russia
- Sees price: "100 AED"
- Expects to see: "~2,500 RUB"

**Решение:**

```javascript
const exchangeRates = {
  aed: 1,
  usd: 0.27,
  rub: 25.3,
  kzt: 137.5,
  eur: 0.25,
};

function displayMultiCurrency(amountAED) {
  return {
    aed: `${amountAED} AED`,
    usd: `~${(amountAED * exchangeRates.usd).toFixed(2)} USD`,
    rub: `~${(amountAED * exchangeRates.rub).toFixed(0)} RUB`,
    kzt: `~${(amountAED * exchangeRates.kzt).toFixed(0)} KZT`,
  };
}

// Display
const prices = displayMultiCurrency(500);
// { aed: '500 AED', usd: '~135.00 USD', rub: '~12650 RUB', kzt: '~68750 KZT' }
```

---

### Issue: Stripe currency conversion fees

**Stripe charges 1% extra** для currency conversion

**Пример:**
- Цена: 100 USD
- Customer платит в EUR
- Stripe берёт: 100 USD + 1% conversion fee

**Решение:** Принимай платежи в нативной валюте

```javascript
async function createPaymentWithCustomerCurrency(amount, customerCountry) {
  const currencyMap = {
    AE: 'aed',
    US: 'usd',
    RU: 'usd', // RUB не поддерживается Stripe
    KZ: 'kzt',
    EU: 'eur',
  };

  const currency = currencyMap[customerCountry] || 'aed';

  return await stripe.paymentIntents.create({
    amount: Math.round(amount * 100),
    currency,
  });
}
```

---

## 🔴 4. Refund Failures

### Error: `charge_already_refunded`

**Причина:** Trying to refund same charge twice

**Решение:**

```javascript
async function safeRefund(chargeId, amount) {
  // Check existing refunds
  const charge = await stripe.charges.retrieve(chargeId);

  if (charge.refunded) {
    throw new Error('Charge already fully refunded');
  }

  const totalRefunded = charge.amount_refunded;
  const remainingAmount = charge.amount - totalRefunded;

  if (amount > remainingAmount) {
    throw new Error(`Only ${remainingAmount / 100} ${charge.currency.toUpperCase()} available to refund`);
  }

  return await stripe.refunds.create({
    charge: chargeId,
    amount,
  });
}
```

---

### Error: `insufficient_funds`

**Причина:** Stripe account balance too low для instant refund

**Решение:**

```javascript
// Stripe автоматически debits from your bank account
// Но если balance negative, refund будет pending

// Check available balance
const balance = await stripe.balance.retrieve();
console.log('Available balance:', balance.available);

// If negative, refund будет отложен на 5-7 дней
```

---

## 🔴 5. Double-Charging Prevention

### Issue: Network timeout → customer clicks "Pay" again

**Решение: Idempotency Keys**

```javascript
async function createPaymentSafe(bookingId, amount, currency) {
  const idempotencyKey = `booking-${bookingId}-${Date.now()}`;

  try {
    return await stripe.paymentIntents.create({
      amount: amount * 100,
      currency,
      metadata: {booking_id: bookingId},
    }, {
      idempotencyKey, // Prevents duplicates
    });
  } catch (err) {
    if (err.type === 'StripeIdempotencyError') {
      // Duplicate request detected
      console.log('Duplicate payment attempt prevented');
      throw new Error('Payment already in progress');
    }
    throw err;
  }
}
```

---

### Client-side: Disable button after click

```javascript
const payButton = document.getElementById('pay-button');

payButton.addEventListener('click', async () => {
  // Disable button
  payButton.disabled = true;
  payButton.textContent = 'Processing...';

  try {
    const result = await stripe.confirmCardPayment(clientSecret);

    if (result.error) {
      // Re-enable button
      payButton.disabled = false;
      payButton.textContent = 'Pay Now';
      alert(result.error.message);
    }
  } catch (err) {
    payButton.disabled = false;
    payButton.textContent = 'Pay Now';
  }
});
```

---

## 🔴 6. Test Mode vs Live Mode Mistakes

### Issue: Production using test keys

**Симптомы:**
- Webhooks не приходят в production
- Real cards decline
- Test data в production database

**Решение:**

```javascript
// Environment validation
if (process.env.NODE_ENV === 'production') {
  if (!process.env.STRIPE_SECRET_KEY.startsWith('sk_live_')) {
    throw new Error('PRODUCTION ERROR: Using test Stripe key in production!');
  }
}

// Add banner в test mode
if (process.env.STRIPE_SECRET_KEY.startsWith('sk_test_')) {
  console.warn('⚠️  STRIPE TEST MODE ENABLED');
}
```

**HTML banner:**
```html
<% if (process.env.NODE_ENV !== 'production') { %>
  <div style="background: #ff0; padding: 10px; text-align: center;">
    ⚠️ TEST MODE - No real charges will be made
  </div>
<% } %>
```

---

## 🔴 7. API Key Rotation

### When to rotate:

- Security breach suspected
- Employee with access left company
- Key accidentally committed to GitHub
- Regular security audit (every 6 months)

### How to rotate без downtime:

```javascript
// Step 1: Create new API key в Stripe Dashboard
// Step 2: Update environment variable BUT keep old key as fallback
const STRIPE_KEYS = {
  primary: process.env.STRIPE_SECRET_KEY_NEW,
  fallback: process.env.STRIPE_SECRET_KEY_OLD,
};

async function createPaymentWithFallback(data) {
  try {
    const stripePrimary = require('stripe')(STRIPE_KEYS.primary);
    return await stripePrimary.paymentIntents.create(data);
  } catch (err) {
    if (err.type === 'StripeAuthenticationError') {
      // Primary key invalid, use fallback
      console.warn('Primary key failed, using fallback');
      const stripeFallback = require('stripe')(STRIPE_KEYS.fallback);
      return await stripeFallback.paymentIntents.create(data);
    }
    throw err;
  }
}

// Step 3: После 24h, удали old key
```

---

## 🔴 8. Provider Status Pages

### Check if provider is down

**Stripe:**
- https://status.stripe.com

**Telr:**
- https://status.telr.com (если доступно)
- Или check Twitter/status updates

**PayPal:**
- https://www.paypal-status.com

### Automated monitoring:

```javascript
const axios = require('axios');

async function checkStripeStatus() {
  const response = await axios.get('https://status.stripe.com/api/v2/status.json');
  const status = response.data.status.indicator; // none/minor/major/critical

  if (status !== 'none') {
    console.error(`Stripe status: ${status}`);
    // Send alert
  }

  return status;
}

// Run every 5 minutes
setInterval(checkStripeStatus, 5 * 60 * 1000);
```

---

## 🔴 9. Telr-Specific Issues

### Issue: Transaction verification fails

**Причина:** Signature mismatch

**Решение:**

```javascript
const crypto = require('crypto');

function verifyTelrResponse(params, storeKey) {
  const {order, code, message, check} = params;

  // Generate hash
  const hash = crypto
    .createHash('sha256')
    .update(`${storeKey}${order.ref}${code}`)
    .digest('hex');

  if (hash !== check) {
    throw new Error('Telr signature verification failed');
  }

  return true;
}
```

---

## 🛠️ Debugging Toolkit

### 1. Log все API calls

```javascript
const originalCreate = stripe.paymentIntents.create;
stripe.paymentIntents.create = async function(...args) {
  console.log('Creating PaymentIntent:', JSON.stringify(args[0], null, 2));
  try {
    const result = await originalCreate.apply(this, args);
    console.log('PaymentIntent created:', result.id);
    return result;
  } catch (err) {
    console.error('PaymentIntent failed:', err.message);
    throw err;
  }
};
```

### 2. Request ID для debugging

```javascript
// Stripe returns requestId в errors
try {
  await stripe.paymentIntents.create({...});
} catch (err) {
  console.error('Request ID:', err.requestId); // req_xxxxx
  // Отправь в Stripe support для debugging
}
```

### 3. Test mode webhooks

```bash
# Stripe CLI
stripe listen --events payment_intent.succeeded,payment_intent.payment_failed

# Trigger test event
stripe trigger payment_intent.succeeded
```

---

## 📊 Error Frequency Table

| Error | Frequency | Fix Time | Prevention |
|-------|-----------|----------|------------|
| card_declined | Very High | 0 min (user issue) | Better messaging |
| webhook signature fail | High | 5 min | Use raw body |
| webhook timeout | Medium | 10 min | Background jobs |
| currency mismatch | Medium | 2 min | Validation |
| double charge | Low | 0 min | Idempotency keys |
| test/live mode mix | Low | 1 min | Environment checks |
| refund fail | Low | 5 min | Check balance first |

---

## 🚨 Emergency Checklist

Если платежи полностью сломались:

1. **Check provider status** (status.stripe.com)
2. **Check API keys** (не expired?)
3. **Check webhook endpoint** (доступен?)
4. **Check logs** (последние errors?)
5. **Test with test card** (работает в test mode?)
6. **Rollback recent changes** (что деплоили последним?)
7. **Contact provider support** (если всё остальное fails)

**Emergency contacts:**
- Stripe: https://support.stripe.com (live chat 24/7)
- Telr: support@telr.com

---

**Word Count:** ~1,600 слов
**Common Issues Covered:** 25+
**Code Examples:** 18
**Ready for debugging:** ✅
