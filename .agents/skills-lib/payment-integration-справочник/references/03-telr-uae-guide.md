# Telr UAE Integration Guide

**Telr** is a leading payment gateway in the Middle East, specializing in local payment methods and AED transactions.

**Best for:** UAE local businesses, AED payments, local bank cards, customers preferring regional payment processors

**Market position:** Strong in UAE, Saudi Arabia, and Middle East region

---

## Table of Contents

1. Telr Overview
2. Account Setup
3. Telr Ivp5 API
4. Hosted Payment Page Integration
5. Direct API Integration
6. Transaction Verification
7. Refund Process
8. Test Credentials
9. Common Issues & Solutions
10. Production Checklist

---

## 1. Telr Overview

### Why Choose Telr?

**Advantages:**
- ✅ UAE-based (local support, fast payouts)
- ✅ Lower fees for AED transactions
- ✅ Supports UAE local bank cards
- ✅ Arabic language support
- ✅ Middle East compliance (UAE Central Bank)
- ✅ Integration with local banks (Emirates NBD, ADCB, FAB)

**Supported Payment Methods:**
- Credit/Debit cards (Visa, Mastercard)
- UAE local cards (Etisalat Cash, du Pay)
- Digital wallets (coming soon)

**Currencies:**
- Primary: AED (UAE Dirham)
- Secondary: USD, EUR, GBP, SAR

### Fees

**Typical pricing:**
- 2.75% per transaction
- No setup fee
- No monthly fee
- AED payouts (next business day)

**Note:** Fees may vary based on business volume and negotiation.

---

## 2. Account Setup

### Step 1: Register with Telr

1. Visit [telr.com](https://telr.com) → Get Started
2. Fill business details:
   - **Business Name**
   - **Trade License** (UAE)
   - **Business Activity:** Tourism/Travel
   - **Website URL**
3. Submit documents:
   - Trade license copy
   - Emirates ID (owner)
   - Bank statement (recent)
   - Business address proof

### Step 2: Account Approval

**Timeline:** 3-5 business days

**You'll receive:**
- Merchant ID
- Store ID
- Authentication Key (API Key)

### Step 3: Dashboard Access

**Login:** [secure.telr.com](https://secure.telr.com)

**Dashboard features:**
- View transactions
- Generate reports
- Refund management
- Settlement reports
- API credentials

---

## 3. Telr Ivp5 API

**Ivp5** = Telr's current API version (Integrated Virtual POS v5)

**API Endpoints:**

**Test Environment:**
```
https://secure.telr.com/gateway/order.json
```

**Live Environment:**
```
https://secure.telr.com/gateway/order.json
```

**Note:** Same endpoint for test/live, differentiate by credentials.

### Authentication

```javascript
const telrConfig = {
  merchantId: process.env.TELR_MERCHANT_ID,      // e.g., "21499"
  storeId: process.env.TELR_STORE_ID,            // e.g., "24101"
  authKey: process.env.TELR_AUTH_KEY,            // Secret key
  testMode: process.env.NODE_ENV !== 'production',
};
```

---

## 4. Hosted Payment Page Integration

**Easiest method:** Redirect customer to Telr's secure payment page.

### Flow

```
1. Customer clicks "Pay"
   ↓
2. Server creates order with Telr
   POST /gateway/order.json
   ↓
3. Telr returns payment URL
   ↓
4. Redirect customer to Telr page
   ↓
5. Customer enters card details on Telr
   ↓
6. Telr processes payment
   ↓
7. Redirect back to your site
   (success or failed URL)
   ↓
8. Server verifies transaction
   GET /gateway/order/status
```

### Implementation

```javascript
const axios = require('axios');

async function createTelrOrder(orderDetails) {
  const requestPayload = {
    // Authentication
    ivp_method: 'create',
    ivp_store: process.env.TELR_STORE_ID,
    ivp_authkey: process.env.TELR_AUTH_KEY,

    // Order details
    ivp_cart: orderDetails.bookingId,
    ivp_amount: orderDetails.amount.toFixed(2), // e.g., "250.00"
    ivp_currency: 'AED',
    ivp_desc: orderDetails.description,

    // Customer details
    ivp_customer_name: orderDetails.customerName,
    ivp_customer_email: orderDetails.customerEmail,
    ivp_customer_phone: orderDetails.customerPhone,

    // Return URLs
    return_auth: 'https://yoursite.com/payment/success',
    return_can: 'https://yoursite.com/payment/cancel',
    return_decl: 'https://yoursite.com/payment/declined',

    // Test mode (optional)
    ivp_test: process.env.NODE_ENV !== 'production' ? '1' : '0',
  };

  try {
    const response = await axios.post(
      'https://secure.telr.com/gateway/order.json',
      requestPayload
    );

    if (response.data.error) {
      throw new Error(`Telr Error: ${response.data.error.message}`);
    }

    return {
      orderId: response.data.order.ref,
      paymentUrl: response.data.order.url,
    };
  } catch (error) {
    console.error('Telr Order Creation Error:', error);
    throw error;
  }
}

// Usage
app.post('/create-telr-payment', async (req, res) => {
  try {
    const { amount, customerName, customerEmail, customerPhone, description, bookingId } = req.body;

    const result = await createTelrOrder({
      amount: parseFloat(amount),
      customerName,
      customerEmail,
      customerPhone,
      description,
      bookingId,
    });

    // Redirect customer to Telr payment page
    res.json({
      paymentUrl: result.paymentUrl,
      orderId: result.orderId,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

### Handle Return URLs

```javascript
// Success page
app.get('/payment/success', async (req, res) => {
  const { order_ref } = req.query; // Telr sends order_ref

  // IMPORTANT: Always verify transaction server-side!
  const status = await verifyTelrTransaction(order_ref);

  if (status.paid) {
    // Update database
    await db.query(
      'UPDATE bookings SET status = $1, telr_order_ref = $2 WHERE id = $3',
      ['paid', order_ref, status.cart_id]
    );

    // Send confirmation
    res.render('success', { order: status });
  } else {
    res.redirect('/payment/failed');
  }
});

// Cancel page
app.get('/payment/cancel', (req, res) => {
  res.render('cancel', { message: 'Payment was cancelled' });
});

// Declined page
app.get('/payment/declined', (req, res) => {
  const { order_ref } = req.query;
  res.render('declined', { message: 'Payment was declined', orderRef: order_ref });
});
```

---

## 5. Direct API Integration

**Advanced method:** Collect card details on your site, send to Telr API.

**⚠️ Warning:** This requires PCI DSS Level 1 compliance (complex). **Hosted page recommended** for most businesses.

### Remote Sale API

```javascript
async function directTelrPayment(paymentDetails) {
  const requestPayload = {
    ivp_method: 'remote',
    ivp_store: process.env.TELR_STORE_ID,
    ivp_authkey: process.env.TELR_AUTH_KEY,

    // Card details (⚠️ Never log these!)
    ivp_card: paymentDetails.cardNumber,
    ivp_expiry: paymentDetails.expiry, // MMYY format
    ivp_cvv: paymentDetails.cvv,

    // Transaction
    ivp_amount: paymentDetails.amount.toFixed(2),
    ivp_currency: 'AED',
    ivp_desc: paymentDetails.description,

    // Customer
    ivp_customer_name: paymentDetails.customerName,
    ivp_customer_email: paymentDetails.customerEmail,
  };

  const response = await axios.post(
    'https://secure.telr.com/gateway/remote.json',
    requestPayload
  );

  if (response.data.auth.status === 'A') {
    // Payment authorized
    return {
      success: true,
      transactionId: response.data.auth.tranref,
      message: response.data.auth.message,
    };
  } else {
    // Payment failed
    return {
      success: false,
      error: response.data.auth.message,
    };
  }
}
```

**Note:** Direct API is complex and requires PCI DSS Level 1 compliance. **Use hosted page unless you have specific requirements.**

---

## 6. Transaction Verification

**Critical:** Always verify transaction status server-side!

**Why?**
- User can manipulate return URLs
- Network failures
- Ensure payment actually succeeded

### Verify Transaction

```javascript
async function verifyTelrTransaction(orderRef) {
  const requestPayload = {
    ivp_method: 'check',
    ivp_store: process.env.TELR_STORE_ID,
    ivp_authkey: process.env.TELR_AUTH_KEY,
    order_ref: orderRef,
  };

  try {
    const response = await axios.post(
      'https://secure.telr.com/gateway/order.json',
      requestPayload
    );

    const order = response.data.order;

    return {
      paid: order.status.code === '3', // 3 = Paid
      orderId: order.ref,
      cartId: order.cartid,
      amount: parseFloat(order.amount),
      currency: order.currency,
      transactionRef: order.transaction.ref,
      cardLast4: order.card.last4,
      status: order.status.text,
    };
  } catch (error) {
    console.error('Telr Verification Error:', error);
    throw error;
  }
}

// Usage in success handler
app.get('/payment/success', async (req, res) => {
  const { order_ref } = req.query;

  try {
    const verification = await verifyTelrTransaction(order_ref);

    if (verification.paid) {
      console.log('✅ Payment verified:', verification.transactionRef);

      // Safe to fulfill order
      await fulfillOrder(verification);

      res.render('success', { order: verification });
    } else {
      console.log('❌ Payment not verified:', verification.status);
      res.render('failed', { error: verification.status });
    }
  } catch (error) {
    res.status(500).render('error', { error: error.message });
  }
});
```

### Transaction Status Codes

| Code | Status | Description |
|------|--------|-------------|
| `-1` | Cancelled | Payment cancelled by customer |
| `-2` | Declined | Payment declined by bank |
| `1` | Pending | Payment initiated, not complete |
| `2` | Authorized | Payment authorized (pre-auth) |
| `3` | **Paid** | ✅ Payment successful |
| `4` | Void | Transaction voided |
| `5` | Refunded | Payment refunded |

**Only fulfill orders when status = `3` (Paid)!**

---

## 7. Refund Process

### Full Refund

```javascript
async function refundTelrTransaction(orderRef, reason) {
  const requestPayload = {
    ivp_method: 'refund',
    ivp_store: process.env.TELR_STORE_ID,
    ivp_authkey: process.env.TELR_AUTH_KEY,
    order_ref: orderRef,
    ivp_refund_note: reason,
  };

  try {
    const response = await axios.post(
      'https://secure.telr.com/gateway/order.json',
      requestPayload
    );

    if (response.data.order.status.code === '5') {
      console.log('✅ Refund successful');
      return { success: true, orderId: orderRef };
    } else {
      throw new Error(response.data.order.status.text);
    }
  } catch (error) {
    console.error('Refund error:', error);
    throw error;
  }
}

// Usage
app.post('/refund', async (req, res) => {
  const { orderRef, reason } = req.body;

  try {
    await refundTelrTransaction(orderRef, reason);

    // Update database
    await db.query(
      'UPDATE bookings SET status = $1 WHERE telr_order_ref = $2',
      ['refunded', orderRef]
    );

    res.json({ success: true, message: 'Refund processed' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

### Partial Refund

**⚠️ Telr limitation:** Partial refunds require manual processing via Dashboard.

**Manual process:**
1. Login to [secure.telr.com](https://secure.telr.com)
2. Find transaction → Click "Refund"
3. Enter partial amount
4. Confirm

**Alternative:** Use Telr API support to enable partial refunds (enterprise accounts).

### Refund Timeline

- **Processing:** Instant on Telr side
- **Bank:** 5-10 business days (varies by bank)

---

## 8. Test Credentials

**Test Environment:**

```bash
# .env for testing
TELR_MERCHANT_ID=21499
TELR_STORE_ID=24101
TELR_AUTH_KEY=your-test-key-from-telr-support
TELR_TEST_MODE=true
```

**Test Cards:**

| Card Number | Result |
|-------------|--------|
| `4000 0000 0000 0002` | ✅ Success |
| `5111 1111 1111 1118` | ✅ Success (Mastercard) |
| `4000 0000 0000 0010` | ❌ Declined |
| `4000 0000 0000 0028` | ❌ Expired |

**Expiry:** Any future date (e.g., `12/25`)
**CVV:** Any 3 digits (e.g., `123`)

**Get test credentials:**
Contact Telr support: [support@telr.com](mailto:support@telr.com)

---

## 9. Common Issues & Solutions

### Issue 1: "Invalid Authentication"

**Error:** `Authentication failed`

**Causes:**
- Wrong `TELR_AUTH_KEY`
- Wrong `TELR_STORE_ID`
- Using test credentials in live mode (or vice versa)

**Solution:**
- Verify credentials in Dashboard
- Check environment (test vs live)
- Restart server after updating `.env`

### Issue 2: "Amount format error"

**Error:** `Invalid amount format`

**Cause:** Amount not in correct format

**Solution:**
```javascript
// ❌ Wrong
ivp_amount: 250

// ✅ Correct
ivp_amount: "250.00" // Always 2 decimal places, string format
```

### Issue 3: Payment succeeds but order not updated

**Cause:** Not verifying transaction server-side

**Solution:**
```javascript
// Always verify on success URL
const verification = await verifyTelrTransaction(order_ref);
if (verification.paid) {
  // Only then update database
}
```

### Issue 4: Customer redirected but payment shows pending

**Cause:** Customer closed browser before completion

**Solution:**
- Implement webhook/callback URL
- Check transaction status periodically
- Send payment reminders

### Issue 5: Refund not working

**Cause:** Transaction not settled yet

**Solution:**
- Wait 24 hours after transaction
- Settlements happen daily (next business day)
- Cannot refund unsettled transactions

---

## 10. Production Checklist

**Before going live:**

### 1. Account Setup
- [ ] Business approved by Telr
- [ ] Live credentials received (Merchant ID, Store ID, Auth Key)
- [ ] Bank account linked (for payouts)
- [ ] Dashboard access verified

### 2. Integration
- [ ] Live credentials in `.env`
- [ ] Test mode disabled (`ivp_test: '0'`)
- [ ] Return URLs pointing to production domain
- [ ] HTTPS enabled on all URLs

### 3. Security
- [ ] Auth Key never exposed (server-only)
- [ ] Transaction verification implemented
- [ ] Logging (without sensitive card data)
- [ ] Rate limiting on endpoints

### 4. Error Handling
- [ ] Handle all return URLs (success, cancel, declined)
- [ ] Display user-friendly error messages
- [ ] Retry logic for API failures
- [ ] Alert on failed transactions

### 5. Testing
- [ ] Test successful payment
- [ ] Test declined card
- [ ] Test cancelled payment
- [ ] Test transaction verification
- [ ] Test refund process

### 6. Business Logic
- [ ] Update database on success
- [ ] Send confirmation emails
- [ ] Generate invoices
- [ ] Inventory management
- [ ] Accounting integration

### 7. Compliance
- [ ] Terms & Conditions
- [ ] Refund Policy
- [ ] Privacy Policy (data handling)
- [ ] UAE compliance (VAT 5%)

---

## Summary

**Telr strengths:**
- ✅ UAE-focused (local support)
- ✅ Lower fees for AED transactions
- ✅ UAE bank integration
- ✅ Arabic language support
- ✅ Middle East compliance

**Telr limitations:**
- ❌ Limited multi-currency support
- ❌ Smaller global reach vs Stripe
- ❌ Less advanced fraud detection
- ❌ Partial refunds require manual processing

**Best for:**
- UAE local businesses
- AED-primary transactions
- Customers preferring regional processors
- Lower transaction fees

**Fees:** 2.75% per transaction
**Setup time:** 1 hour (integration) + 3-5 days (approval)

**Next steps:**
- Register account
- Get test credentials
- Integrate hosted payment page
- Test with test cards
- Submit for live approval
- Go live!

---

**Telr Resources:**
- [Official Docs](https://telr.com/support/knowledge-base/)
- [API Reference](https://telr.com/support/knowledge-base/integration/)
- [Support](mailto:support@telr.com)
- [Dashboard](https://secure.telr.com)
