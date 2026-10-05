# Security & Compliance

## Overview

Payment security is non-negotiable. A single breach can destroy customer trust, result in massive fines, and shut down your business. This guide covers PCI DSS compliance, secure credential management, fraud prevention, UAE-specific regulations, and security best practices for tourism payment systems.

## PCI DSS Requirements

### Understanding PCI DSS Levels

**PCI DSS** (Payment Card Industry Data Security Standard) applies to ANY business that accepts card payments.

**Compliance Levels:**

| Level | Transaction Volume (Annual) | Validation Requirements |
|-------|----------------------------|------------------------|
| **Level 1** | >6 million | Annual on-site audit by QSA |
| **Level 2** | 1-6 million | Annual Self-Assessment Questionnaire (SAQ) |
| **Level 3** | 20,000 - 1 million | Annual SAQ |
| **Level 4** | <20,000 | Annual SAQ |

**Most tourism businesses = Level 4** (simplest compliance path)

### Level 4 Requirements (SAQ A)

**SAQ A applies when:**
- Card data is processed by third party (Stripe, Telr, PayPal)
- You redirect customer to payment processor
- You don't store, process, or transmit card data
- Your website uses HTTPS

**12 Core Requirements (Simplified):**

```yaml
1. Firewall Configuration:
   - Use firewall between your server and internet
   - Default-deny policy for inbound traffic

2. Secure Passwords:
   - No default vendor passwords
   - Change admin passwords immediately

3. Protect Cardholder Data:
   - NEVER store CVV/CVC codes
   - If you must store card numbers (you shouldn't), encrypt them

4. Encrypt Transmission:
   - Use TLS 1.2+ for all payment pages
   - HTTPS everywhere (not just checkout)

5. Antivirus Software:
   - Install on all systems processing payments
   - Update daily

6. Secure Systems:
   - Patch operating system and software
   - No unpatched vulnerabilities

7. Restrict Data Access:
   - Only authorized personnel see payment data
   - Role-based access control

8. Unique IDs:
   - Each admin user has unique credentials
   - No shared passwords

9. Restrict Physical Access:
   - Secure server room / office
   - No unauthorized access to systems

10. Track Access:
    - Log all payment-related activities
    - Review logs monthly

11. Test Security:
    - Quarterly vulnerability scans
    - Annual penetration testing

12. Security Policy:
    - Written security policy
    - Train all staff annually
```

### Compliance Checklist for Level 4

```markdown
# PCI DSS Level 4 Compliance Checklist

## Website Security
- [ ] SSL/TLS certificate installed (HTTPS)
- [ ] Certificate from trusted CA (not self-signed)
- [ ] TLS 1.2 or higher enforced
- [ ] HTTP redirects to HTTPS automatically
- [ ] Payment pages use iframe or redirect (Stripe/Telr hosted)

## Server Security
- [ ] Firewall configured (UFW, iptables, or cloud firewall)
- [ ] Only ports 80, 443, 22 (SSH) open
- [ ] SSH access restricted to specific IPs
- [ ] Operating system fully patched
- [ ] Automatic security updates enabled

## Access Control
- [ ] Separate admin accounts for each person
- [ ] Strong passwords (12+ characters, complexity)
- [ ] Two-factor authentication (2FA) enabled
- [ ] Password manager used (1Password, Bitwarden)
- [ ] Access revoked when employee leaves

## Data Handling
- [ ] NO credit card numbers stored in database
- [ ] NO CVV codes stored anywhere
- [ ] Customer email/name encrypted at rest
- [ ] Database access requires authentication
- [ ] Database backups encrypted

## Logging & Monitoring
- [ ] Payment API calls logged (timestamp, amount, result)
- [ ] Failed login attempts logged
- [ ] Logs stored for 90+ days
- [ ] Logs reviewed monthly for anomalies

## Vendor Management
- [ ] Stripe/Telr used for card processing (PCI compliant)
- [ ] Vendors provide PCI compliance documentation
- [ ] Regular vendor security reviews

## Policies & Training
- [ ] Written security policy document
- [ ] Staff trained on payment security (annually)
- [ ] Incident response plan documented

## Testing
- [ ] Quarterly vulnerability scans (Qualys, Nessus)
- [ ] Annual penetration test
- [ ] SAQ A completed annually
```

### PCI Compliance Through Stripe/Telr

**The Easy Path:**

When using Stripe or Telr correctly, THEY handle PCI compliance:

```javascript
// CORRECT: Stripe Checkout (Stripe handles PCI)
const session = await stripe.checkout.sessions.create({
  payment_method_types: ['card'],
  line_items: [{
    price_data: {
      currency: 'aed',
      product_data: { name: 'Desert Safari Tour' },
      unit_amount: 150000, // 1500 AED in fils
    },
    quantity: 1,
  }],
  mode: 'payment',
  success_url: 'https://yoursite.com/success',
  cancel_url: 'https://yoursite.com/cancel',
});

// Redirect to session.url - Stripe's hosted page
// YOU don't touch card data = Minimal PCI scope
```

```javascript
// WRONG: Custom payment form (HIGH PCI scope)
// DON'T DO THIS unless you're PCI Level 1 certified

app.post('/charge', async (req, res) => {
  const { cardNumber, cvv, expiry } = req.body; // ❌ Handling raw card data

  // This makes YOU responsible for PCI compliance
  // SAQ D (300+ questions), annual audit required
  // NOT recommended for small business
});
```

**Key Principle:** Let payment processors handle card data, you handle booking logic.

## Secure Credential Storage

### Environment Variables (Basic)

**NEVER hardcode API keys in code:**

```javascript
// ❌ WRONG - Keys visible in code repository
const stripe = require('stripe')('sk_live_abc123DEF456');

// ✅ CORRECT - Keys in environment variables
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
```

**Setup (.env file):**
```bash
# .env (NEVER commit to Git!)
STRIPE_SECRET_KEY=sk_live_51Abc123...
TELR_MERCHANT_ID=12345
TELR_API_KEY=xyz789...
DATABASE_URL=postgresql://user:pass@localhost/db
JWT_SECRET=random_string_64_characters
```

**.gitignore (ALWAYS include):**
```
.env
.env.local
.env.production
config/secrets.yml
```

### Cloud Secrets Management (Production)

**AWS Secrets Manager:**
```javascript
const AWS = require('aws-sdk');
const secretsManager = new AWS.SecretsManager({ region: 'me-south-1' });

async function getStripeKey() {
  const data = await secretsManager.getSecretValue({
    SecretId: 'prod/payment/stripe'
  }).promise();

  return JSON.parse(data.SecretString).api_key;
}

// Usage
const stripeKey = await getStripeKey();
const stripe = require('stripe')(stripeKey);
```

**Benefits:**
- Keys never in code or environment files
- Automatic rotation supported
- Audit logging (who accessed what key when)
- IAM permission control

**Alternative: HashiCorp Vault, Google Secret Manager, Azure Key Vault**

### Secrets Rotation Best Practices

```yaml
Key Rotation Schedule:
  Production API Keys: Every 90 days
  Database Passwords: Every 180 days
  JWT Secrets: Every 365 days
  Test/Dev Keys: No rotation needed (but don't reuse in prod!)

Rotation Process:
  1. Generate new key in Stripe/Telr dashboard
  2. Add new key to secrets manager (don't delete old yet)
  3. Update application to use new key
  4. Deploy and verify payments work
  5. Monitor for 24 hours
  6. Delete old key from Stripe/Telr
  7. Remove old key from secrets manager
  8. Document rotation in security log
```

## Webhook Signature Verification

### Why Signatures Matter

**Problem:** Anyone can send fake webhooks to your endpoint.

```javascript
// Without verification, attacker can send:
POST /webhooks/stripe
{
  "type": "payment_intent.succeeded",
  "data": {
    "object": {
      "id": "pi_fake123",
      "amount": 100, // Claims 100 AED paid
      "status": "succeeded"
    }
  }
}

// Your code marks booking as paid, but no real payment happened!
```

**Solution:** Cryptographic signature verification.

### Stripe Signature Verification

```javascript
const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET; // whsec_...

app.post('/webhooks/stripe', express.raw({type: 'application/json'}), (req, res) => {
  const sig = req.headers['stripe-signature'];

  let event;

  try {
    // Verify signature - throws error if invalid
    event = stripe.webhooks.constructEvent(req.body, sig, endpointSecret);
  } catch (err) {
    console.error('⚠️ Webhook signature verification failed:', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // Signature valid - process event
  switch (event.type) {
    case 'payment_intent.succeeded':
      const paymentIntent = event.data.object;
      console.log('✅ Payment succeeded:', paymentIntent.id);
      updateBookingStatus(paymentIntent.metadata.booking_id, 'paid');
      break;

    case 'payment_intent.payment_failed':
      console.log('❌ Payment failed:', event.data.object.id);
      break;

    default:
      console.log(`Unhandled event type ${event.type}`);
  }

  res.status(200).json({received: true});
});
```

**Key Points:**
- Use `express.raw()` - Stripe needs raw body for signature
- `endpointSecret` from Stripe Dashboard → Webhooks → Add endpoint
- ALWAYS verify signature before processing

### Telr Signature Verification

```javascript
const crypto = require('crypto');

app.post('/webhooks/telr', (req, res) => {
  const { order_id, status, amount, signature } = req.body;

  // Telr signature = HMAC-SHA256 of concatenated values
  const payload = `${order_id}${status}${amount}${process.env.TELR_STORE_KEY}`;
  const expectedSignature = crypto
    .createHmac('sha256', process.env.TELR_SECRET_KEY)
    .update(payload)
    .digest('hex');

  if (signature !== expectedSignature) {
    console.error('⚠️ Invalid Telr webhook signature');
    return res.status(400).send('Invalid signature');
  }

  // Signature valid - process payment
  if (status === 'success') {
    updateBookingStatus(order_id, 'paid');
  }

  res.status(200).send('OK');
});
```

### PayPal Signature Verification

```javascript
const axios = require('axios');

app.post('/webhooks/paypal', async (req, res) => {
  const webhookId = process.env.PAYPAL_WEBHOOK_ID;

  // PayPal verification requires API call
  const verification = await axios.post(
    'https://api-m.paypal.com/v1/notifications/verify-webhook-signature',
    {
      transmission_id: req.headers['paypal-transmission-id'],
      transmission_time: req.headers['paypal-transmission-time'],
      cert_url: req.headers['paypal-cert-url'],
      auth_algo: req.headers['paypal-auth-algo'],
      transmission_sig: req.headers['paypal-transmission-sig'],
      webhook_id: webhookId,
      webhook_event: req.body
    },
    {
      headers: {
        'Authorization': `Bearer ${await getPayPalAccessToken()}`
      }
    }
  );

  if (verification.data.verification_status !== 'SUCCESS') {
    console.error('⚠️ Invalid PayPal webhook signature');
    return res.status(400).send('Invalid signature');
  }

  // Process event
  const event = req.body;
  if (event.event_type === 'PAYMENT.CAPTURE.COMPLETED') {
    const captureId = event.resource.id;
    updateBookingStatus(event.resource.invoice_id, 'paid');
  }

  res.status(200).send('OK');
});
```

## Rate Limiting

### Protection Against Abuse

**Attacks to prevent:**
1. **Brute force** - Trying thousands of card combinations
2. **API abuse** - Overwhelming your server with requests
3. **Credential stuffing** - Testing leaked passwords
4. **Scraping** - Extracting pricing data

### Implementation with Express-Rate-Limit

```javascript
const rateLimit = require('express-rate-limit');

// Payment endpoint rate limit (strict)
const paymentLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 requests per 15 minutes
  message: 'Too many payment attempts, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
});

app.post('/api/create-payment', paymentLimiter, async (req, res) => {
  // Payment logic
});

// Login rate limit (medium)
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  message: 'Too many login attempts, try again in 15 minutes'
});

app.post('/api/login', loginLimiter, async (req, res) => {
  // Login logic
});

// General API rate limit (lenient)
const apiLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 100,
  message: 'Too many requests'
});

app.use('/api/', apiLimiter);
```

### Redis-Based Rate Limiting (Production)

```javascript
const Redis = require('ioredis');
const redis = new Redis();

async function checkRateLimit(userId, action, limit, windowSeconds) {
  const key = `ratelimit:${action}:${userId}`;
  const current = await redis.incr(key);

  if (current === 1) {
    await redis.expire(key, windowSeconds);
  }

  if (current > limit) {
    const ttl = await redis.ttl(key);
    throw new Error(`Rate limit exceeded. Try again in ${ttl} seconds`);
  }

  return current;
}

// Usage
app.post('/api/create-payment', async (req, res) => {
  try {
    await checkRateLimit(req.ip, 'payment', 5, 900); // 5 per 15 min

    // Process payment
    const paymentIntent = await stripe.paymentIntents.create({...});
    res.json(paymentIntent);

  } catch (err) {
    res.status(429).json({ error: err.message });
  }
});
```

## Fraud Prevention

### IP Geolocation Checks

**Detect suspicious transactions:**

```javascript
const axios = require('axios');

async function checkTransactionRisk(customerData, paymentData) {
  // Get customer's IP location
  const ipInfo = await axios.get(`https://ipapi.co/${customerData.ip}/json/`);

  const risks = [];

  // Risk 1: IP country doesn't match card country
  if (ipInfo.data.country_code !== paymentData.card_country) {
    risks.push({
      level: 'medium',
      reason: 'IP country mismatch with card country'
    });
  }

  // Risk 2: VPN/Proxy detected
  if (ipInfo.data.proxy === true) {
    risks.push({
      level: 'high',
      reason: 'VPN or proxy detected'
    });
  }

  // Risk 3: High-risk country
  const highRiskCountries = ['XX', 'YY', 'ZZ']; // Configure based on experience
  if (highRiskCountries.includes(ipInfo.data.country_code)) {
    risks.push({
      level: 'high',
      reason: 'Transaction from high-risk country'
    });
  }

  // Risk 4: Unusual amount for region
  const avgBookingValue = await getAverageBookingValue(ipInfo.data.country_code);
  if (paymentData.amount > avgBookingValue * 3) {
    risks.push({
      level: 'medium',
      reason: 'Amount unusually high for region'
    });
  }

  return {
    riskScore: calculateRiskScore(risks),
    risks: risks,
    requiresManualReview: risks.some(r => r.level === 'high')
  };
}

// Usage
app.post('/api/create-booking', async (req, res) => {
  const riskAssessment = await checkTransactionRisk(
    { ip: req.ip },
    { amount: req.body.amount, card_country: 'US' }
  );

  if (riskAssessment.requiresManualReview) {
    // Hold booking, notify admin
    await createPendingBooking(req.body, riskAssessment);
    return res.json({
      status: 'pending_review',
      message: 'Booking requires verification, we\'ll contact you within 2 hours'
    });
  }

  // Low risk - proceed automatically
  const payment = await createPayment(req.body);
  res.json(payment);
});
```

### Velocity Limits

**Detect suspicious patterns:**

```javascript
async function checkVelocity(customerId, action) {
  const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);

  const recentActions = await db.query(
    'SELECT COUNT(*) as count FROM transactions WHERE customer_id = $1 AND action = $2 AND created_at > $3',
    [customerId, action, oneHourAgo]
  );

  const limits = {
    'payment_attempt': 3,   // Max 3 payment attempts per hour
    'booking_create': 5,    // Max 5 bookings per hour
    'refund_request': 2     // Max 2 refund requests per hour
  };

  if (recentActions.rows[0].count >= limits[action]) {
    throw new Error(`Velocity limit exceeded for ${action}`);
  }
}
```

### Email Validation

```javascript
const validator = require('validator');
const dns = require('dns').promises;

async function validateEmail(email) {
  // Basic format check
  if (!validator.isEmail(email)) {
    return { valid: false, reason: 'Invalid format' };
  }

  // Disposable email check
  const disposableDomains = ['tempmail.com', 'guerrillamail.com', '10minutemail.com'];
  const domain = email.split('@')[1];
  if (disposableDomains.includes(domain)) {
    return { valid: false, reason: 'Disposable email not allowed' };
  }

  // DNS MX record check (does domain accept email?)
  try {
    const mxRecords = await dns.resolveMx(domain);
    if (mxRecords.length === 0) {
      return { valid: false, reason: 'Domain has no mail server' };
    }
  } catch (err) {
    return { valid: false, reason: 'Invalid domain' };
  }

  return { valid: true };
}
```

### Blacklist Management

```javascript
// Redis-based blacklist
async function isBlacklisted(identifier, type) {
  const key = `blacklist:${type}:${identifier}`;
  return await redis.exists(key);
}

async function addToBlacklist(identifier, type, reason, durationDays = 365) {
  const key = `blacklist:${type}:${identifier}`;
  await redis.setex(key, durationDays * 86400, reason);

  // Also log to database for audit
  await db.query(
    'INSERT INTO blacklist (identifier, type, reason, added_at) VALUES ($1, $2, $3, NOW())',
    [identifier, type, reason]
  );
}

// Usage
app.post('/api/create-booking', async (req, res) => {
  // Check if email blacklisted
  if (await isBlacklisted(req.body.email, 'email')) {
    return res.status(403).json({ error: 'Account suspended' });
  }

  // Check if IP blacklisted
  if (await isBlacklisted(req.ip, 'ip')) {
    return res.status(403).json({ error: 'Access denied' });
  }

  // Proceed with booking...
});
```

## Transaction Logging

### What to Log

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'payment.log' })
  ]
});

function logPaymentAttempt(data) {
  logger.info('payment_attempt', {
    timestamp: new Date().toISOString(),
    booking_id: data.booking_id,
    amount: data.amount,
    currency: data.currency,
    customer_id: data.customer_id,
    customer_email: maskEmail(data.customer_email), // mask@*********.com
    customer_ip: data.customer_ip,
    payment_method: data.payment_method,
    provider: data.provider, // stripe, telr, etc.
    status: data.status, // attempted, succeeded, failed
    error_code: data.error_code,
    // ❌ NEVER log: card number, CVV, full card details
  });
}

function maskEmail(email) {
  const [local, domain] = email.split('@');
  return `${local.slice(0, 3)}***@***${domain.slice(-4)}`;
}
```

### What NEVER to Log

```yaml
NEVER LOG (PCI Violation):
  ❌ Full credit card number (even encrypted)
  ❌ CVV/CVC codes
  ❌ Full magnetic stripe data
  ❌ PIN codes
  ❌ Card verification values

SAFE TO LOG:
  ✅ Last 4 digits of card (1234 **** **** 5678 → 5678)
  ✅ Card brand (Visa, Mastercard)
  ✅ Expiry month/year (if needed)
  ✅ Cardholder name (if needed for dispute)
  ✅ Transaction ID from payment processor
  ✅ Amount, currency, timestamp
  ✅ Success/failure status
  ✅ Error codes (but not raw error messages with sensitive data)
```

### Log Retention Policy

```yaml
Log Types & Retention:
  Payment transactions: 7 years (legal requirement in UAE)
  Access logs: 90 days
  Error logs: 1 year
  Webhook events: 1 year
  User activity: 2 years

Storage:
  Active logs: PostgreSQL (fast queries)
  Archived logs: AWS S3 Glacier (cheap long-term storage)

Compliance:
  - Logs must be tamper-proof (write-once)
  - Encrypted at rest
  - Access audited (who viewed what log when)
```

## UAE KYC/AML Compliance

### When KYC is Required

**UAE Central Bank Regulations:**

```yaml
KYC Required When:
  - Single transaction ≥ 15,000 AED (~4,100 USD)
  - Cumulative transactions from same customer ≥ 15,000 AED in 30 days
  - Any suspicious transaction (regardless of amount)
  - Cash payment ≥ 55,000 AED (illegal to accept more)

KYC Documents Needed:
  UAE Residents:
    - Emirates ID (both sides)
    - Passport copy
    - Proof of address (utility bill)

  Tourists:
    - Passport copy
    - Entry stamp or visa
    - Hotel booking confirmation
    - Return flight ticket
```

### Implementation

```javascript
async function checkKYCRequired(customerId, transactionAmount) {
  const threshold = 15000; // AED

  // Check if single transaction exceeds threshold
  if (transactionAmount >= threshold) {
    return { required: true, reason: 'Single transaction ≥ 15,000 AED' };
  }

  // Check cumulative transactions in last 30 days
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
  const cumulativeResult = await db.query(
    'SELECT SUM(amount) as total FROM transactions WHERE customer_id = $1 AND created_at > $2',
    [customerId, thirtyDaysAgo]
  );

  const cumulativeAmount = cumulativeResult.rows[0].total || 0;

  if (cumulativeAmount + transactionAmount >= threshold) {
    return {
      required: true,
      reason: `Cumulative transactions (${cumulativeAmount + transactionAmount} AED) ≥ 15,000 AED`
    };
  }

  return { required: false };
}

// Usage
app.post('/api/create-booking', async (req, res) => {
  const kycCheck = await checkKYCRequired(req.user.id, req.body.amount);

  if (kycCheck.required) {
    const kycStatus = await getKYCStatus(req.user.id);

    if (kycStatus !== 'verified') {
      return res.status(403).json({
        error: 'KYC verification required',
        reason: kycCheck.reason,
        next_steps: 'Please upload Emirates ID and passport'
      });
    }
  }

  // Proceed with booking...
});
```

### Suspicious Activity Reporting

```javascript
// Triggers for suspicious activity
function assessSuspiciousActivity(transaction) {
  const flags = [];

  // Large cash payment
  if (transaction.method === 'cash' && transaction.amount > 20000) {
    flags.push('Large cash payment');
  }

  // Multiple small transactions to avoid KYC
  if (transaction.pattern === 'frequent_small' && transaction.total_near_threshold) {
    flags.push('Structuring (smurfing) suspected');
  }

  // Mismatch between customer profile and transaction
  if (transaction.customer_risk === 'low' && transaction.amount > 50000) {
    flags.push('Transaction inconsistent with profile');
  }

  if (flags.length > 0) {
    // Report to UAE Financial Intelligence Unit (FIU)
    reportToFIU({
      transaction_id: transaction.id,
      flags: flags,
      customer_id: transaction.customer_id,
      amount: transaction.amount
    });
  }
}
```

## VAT 5% Calculation (UAE)

### Correct VAT Implementation

```javascript
// UAE VAT is 5% on all tourism services

function calculateVATInclusive(priceExcludingVAT) {
  const vatRate = 0.05;
  const vat = priceExcludingVAT * vatRate;
  const totalIncludingVAT = priceExcludingVAT + vat;

  return {
    subtotal: priceExcludingVAT,
    vat: vat,
    total: totalIncludingVAT
  };
}

// Example
const tourPrice = 1000; // AED excluding VAT
const invoice = calculateVATInclusive(tourPrice);
// { subtotal: 1000, vat: 50, total: 1050 }

// Reverse calculation (if price shown is VAT-inclusive)
function calculateVATExclusive(priceIncludingVAT) {
  const vatRate = 0.05;
  const subtotal = priceIncludingVAT / (1 + vatRate);
  const vat = priceIncludingVAT - subtotal;

  return {
    subtotal: subtotal,
    vat: vat,
    total: priceIncludingVAT
  };
}

// Example
const displayedPrice = 1050; // AED including VAT
const breakdown = calculateVATExclusive(displayedPrice);
// { subtotal: 1000, vat: 50, total: 1050 }
```

### VAT Invoice Requirements

```javascript
// UAE VAT invoice must include:
const vatInvoice = {
  invoiceNumber: 'INV-2024-00123',
  date: '2024-03-15',
  supplierName: 'Your Company LLC',
  supplierTRN: '100123456789003', // 15-digit Tax Registration Number
  customerName: 'John Doe',
  customerTRN: null, // Optional for B2C

  lineItems: [
    {
      description: 'Desert Safari Tour',
      quantity: 2,
      unitPrice: 500,
      subtotal: 1000,
      vatRate: 5,
      vatAmount: 50,
      total: 1050
    }
  ],

  subtotal: 1000,
  totalVAT: 50,
  totalIncludingVAT: 1050,

  currency: 'AED'
};
```

## GDPR Considerations (EU Customers)

### Data Collection Minimization

```javascript
// Only collect what you need
const customerDataMinimal = {
  // Required for booking
  name: 'John Doe',
  email: 'john@example.com',
  phone: '+44 7700 900000',

  // Optional (with consent)
  marketing_consent: true,

  // NEVER collect unless absolutely necessary:
  // - Date of birth (age discrimination risk)
  // - Passport number (high sensitivity, not needed for tour)
  // - Home address (not needed for pickup-based tours)
};
```

### Data Retention & Deletion

```javascript
// Implement "Right to be Forgotten"
async function deleteCustomerData(customerId) {
  // Check if customer has active bookings
  const activeBookings = await db.query(
    'SELECT COUNT(*) FROM bookings WHERE customer_id = $1 AND status IN ($2, $3)',
    [customerId, 'confirmed', 'pending']
  );

  if (activeBookings.rows[0].count > 0) {
    throw new Error('Cannot delete customer with active bookings');
  }

  // Anonymize transaction records (keep for accounting, remove personal data)
  await db.query(
    'UPDATE transactions SET customer_name = $1, customer_email = $2 WHERE customer_id = $3',
    ['[DELETED]', 'deleted@example.com', customerId]
  );

  // Delete personal information
  await db.query('DELETE FROM customers WHERE id = $1', [customerId]);

  console.log(`Customer ${customerId} data deleted per GDPR request`);
}
```

## Security Audit Checklist

```markdown
# Monthly Security Audit Checklist

## Access Control
- [ ] Review list of users with admin access
- [ ] Disable accounts of former employees
- [ ] Check for weak passwords (password strength audit)
- [ ] Verify 2FA enabled for all admin accounts

## Infrastructure
- [ ] Run vulnerability scan (Qualys, Nessus, or similar)
- [ ] Check for outdated software versions
- [ ] Review firewall rules
- [ ] Check SSL certificate expiry (renew if <30 days)

## Payment Security
- [ ] Test Stripe webhook signature verification
- [ ] Test Telr webhook signature verification
- [ ] Verify API keys are not exposed in code
- [ ] Check rate limiting is working (test with curl)

## Logging & Monitoring
- [ ] Review payment logs for anomalies
- [ ] Check for unusual IP addresses
- [ ] Review failed payment attempts (>10% failure rate = investigate)
- [ ] Verify log backup is working

## Compliance
- [ ] Complete SAQ A (annually)
- [ ] Update security policy document
- [ ] Train new staff on payment security
- [ ] Review KYC documentation for high-value transactions

## Incident Response
- [ ] Test backup restoration (can you recover from backup?)
- [ ] Update incident response contact list
- [ ] Review previous incidents and lessons learned

**Last Audit:** [Date]
**Next Audit:** [Date + 30 days]
**Audited By:** [Name]
```

## Key Takeaways

1. **PCI DSS is mandatory** - Use Stripe/Telr hosted checkout to simplify compliance
2. **Never store sensitive card data** - Let payment processors handle it
3. **ALWAYS verify webhook signatures** - Prevent fake payment notifications
4. **Implement rate limiting** - Protect against brute force and abuse
5. **Fraud prevention is essential** - IP checks, velocity limits, email validation
6. **Log everything (except sensitive data)** - Audit trail for disputes
7. **UAE KYC required at 15,000 AED** - Collect Emirates ID for large transactions
8. **VAT 5% must be shown separately** - Legal requirement in UAE
9. **GDPR applies to EU customers** - Minimize data collection, allow deletion
10. **Regular security audits** - Monthly checks prevent breaches

## Next Steps

- Implement webhook signature verification
- Set up rate limiting on payment endpoints
- Create KYC collection flow for high-value bookings
- Document security policies
- Train staff on fraud detection

---

**Last Updated:** 2026-02-04
**Critical Review:** Quarterly
**Compliance Standards:** PCI DSS v4.0, UAE Central Bank AML/CFT Notice
