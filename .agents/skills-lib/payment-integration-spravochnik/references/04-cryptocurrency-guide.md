# Cryptocurrency Payment Guide - USDT & Bitcoin for UAE Tourism

**Последнее обновление:** 2026-02-04
**Уровень:** Intermediate
**Провайдеры:** USDT (Tether), Bitcoin, Alternative Cryptos
**Цель:** Integrate cryptocurrency payments for UAE tourism business

---

## Введение

Cryptocurrency payments становятся популярны в туристической индустрии ОАЭ по нескольким причинам:

**Преимущества:**
- **Low fees:** 1-2% vs 2.9-3.4% для карт
- **No chargebacks:** Transactions irreversible (защита от fraud)
- **Fast settlements:** 10-60 минут (vs 2-7 дней для банков)
- **International:** No currency conversion, no bank restrictions
- **Privacy:** Некоторые клиенты предпочитают anonymity
- **ОАЭ friendly:** Crypto-friendly regulation (VARA licensing)

**Недостатки:**
- **Volatility:** Price может измениться за минуты
- **Manual verification:** Нет automatic webhooks (нужно monitor blockchain)
- **Technical barrier:** Клиенты должны иметь wallet
- **Irreversible:** No refunds без cooperation клиента
- **Tax complexity:** Accounting для crypto transactions сложнее

**Типичные use cases:**
- Large bookings (yacht charters >$5,000)
- International clients (avoiding bank fees)
- Recurring clients who prefer crypto
- Corporate payments (some companies hold crypto treasuries)

---

## USDT (Tether) - Recommended for Tourism

**Почему USDT?**
- **Stablecoin:** 1 USDT ≈ 1 USD (no volatility)
- **Most popular:** Highest trading volume
- **Multiple networks:** Ethereum (ERC-20), Tron (TRC-20), Polygon
- **Easy conversion:** Can exchange to AED instantly

**Popular networks comparison:**

| Network | Fee | Speed | Recommended? |
|---------|-----|-------|--------------|
| **Ethereum (ERC-20)** | $5-20 | 2-15 min | ⚠️ High fees |
| **Tron (TRC-20)** | $1-2 | 1-3 min | ✅ BEST for payments |
| **Polygon (MATIC)** | $0.01-0.1 | <1 min | ✅ Good for small amounts |
| **Binance Smart Chain** | $0.20 | 3 min | ✅ Alternative |

**Рекомендация:** Use **Tron (TRC-20)** для туристических платежей (low fees, fast).

---

## Bitcoin - Alternative Option

**Почему Bitcoin?**
- **Most recognized:** Customers trust BTC
- **Store of value:** Some prefer BTC over stablecoins
- **Network effect:** Largest cryptocurrency

**Почему НЕ Bitcoin для regular payments:**
- **High fees:** $2-10 per transaction (иногда $20+)
- **Slow:** 10-60 minutes for confirmation
- **Volatility:** Price changes -5% to +5% daily
- **Complexity:** Need to convert BTC → USD → AED

**When to use Bitcoin:**
- High-value bookings (>$10,000)
- Customers specifically request BTC
- Long-term holds (не конвертируем сразу)

---

## Wallet Setup

### Hot Wallet vs Cold Wallet

**Hot Wallet** (connected to internet):
- **Pros:** Instant access, easy automation
- **Cons:** Security risk (hackable)
- **Use for:** Daily operations, small amounts (<$5,000)
- **Examples:** Trust Wallet, MetaMask, Exodus

**Cold Wallet** (offline storage):
- **Pros:** Maximum security
- **Cons:** Manual process, slower
- **Use for:** Long-term storage, large amounts (>$50,000)
- **Examples:** Ledger Nano X, Trezor

**Рекомендация для бизнеса:**
- Hot wallet для receiving payments
- Daily sweep to cold wallet для хранения

---

### Creating USDT Wallet (Tron TRC-20)

**Option 1: Trust Wallet (Mobile, Recommended)**

1. Download Trust Wallet: https://trustwallet.com
2. Create new wallet → **Save seed phrase securely!**
3. Tap "Receive" → Select "Tron (TRX)"
4. Copy address (starts with `T...`)
5. This address accepts both TRX and USDT (TRC-20)

**Option 2: Tron Link (Browser Extension)**

1. Install: https://www.tronlink.org
2. Create wallet → Backup seed phrase
3. Switch network to "Mainnet"
4. Copy address from dashboard

**Option 3: Binance Account (Easiest for converting to AED)**

1. Sign up on Binance.com (UAE available)
2. Complete KYC verification
3. Wallet → Deposit → USDT → Select "TRC20"
4. Copy deposit address
5. Can sell USDT → AED directly on Binance P2P

**⚠️ КРИТИЧЕСКИ ВАЖНО:**
- **ALWAYS verify network!** Sending ERC-20 to TRC-20 address = LOST FUNDS
- Backup seed phrase on paper (не в cloud, не в email!)
- Never share seed phrase (только wallet address)

---

### Payment Address Generation

**Static vs Dynamic addresses:**

**Static address** (simple, not recommended):
```
Same address for all customers
Example: TXy...abc123
```
**Pros:** Easy
**Cons:** Can't track which customer paid

**Dynamic addresses** (recommended):
```
Generate unique address per booking
Booking #123 → Address TXy...abc123
Booking #124 → Address TXy...def456
```
**Pros:** Easy tracking, better accounting
**Cons:** Need HD wallet implementation

**Compromise solution (payment tracking):**
Use single address + memo/note field:
```javascript
// Each customer sends to same address but includes booking ID in memo
Address: TXy...abc123
Memo: "BOOK-12345"
```

**Tron doesn't support memos**, so best practice:
- Generate unique address per large booking
- Use single address for small bookings + manual tracking

---

## Implementation: USDT Payment Flow

### Step 1: Display Payment Request

**What to show customer:**

```javascript
// server.js
app.post('/generate-usdt-payment', async (req, res) => {
  const { bookingId, amountUSD } = req.body;

  // Get real-time USDT rate (usually 1:1 USD)
  const usdtRate = await getUSDTRate(); // CoinGecko API
  const amountUSDT = (amountUSD / usdtRate).toFixed(2);

  // Your static Tron wallet address
  const walletAddress = process.env.TRON_WALLET_ADDRESS;

  // Save to database
  await db.query(
    'INSERT INTO crypto_payments (booking_id, amount_usdt, wallet_address, status) VALUES ($1, $2, $3, $4)',
    [bookingId, amountUSDT, walletAddress, 'pending']
  );

  res.json({
    walletAddress,
    amount: amountUSDT,
    network: 'TRC-20',
    qrCode: generateQRCode(walletAddress, amountUSDT) // Generate QR
  });
});
```

### Step 2: Generate QR Code

**Using `qrcode` library:**

```javascript
const QRCode = require('qrcode');

async function generateQRCode(address, amount) {
  // Tron URI format: tron:<address>?amount=<amount>
  const uri = `tron:${address}?amount=${amount}`;

  // Generate QR as data URL
  const qrDataUrl = await QRCode.toDataURL(uri);
  return qrDataUrl;
}
```

**Frontend display:**

```html
<!-- payment-page.html -->
<div class="crypto-payment">
  <h2>Pay with USDT (TRC-20)</h2>

  <div class="amount">
    <span class="value">125.00 USDT</span>
    <span class="usd">(≈ 125 USD / 459 AED)</span>
  </div>

  <div class="qr-code">
    <img src="<%= qrCodeDataUrl %>" alt="Scan to pay">
  </div>

  <div class="wallet-address">
    <label>Wallet Address:</label>
    <div class="address-box">
      <code id="address">TXy7GF2rJbqSxNw8...</code>
      <button onclick="copyAddress()">Copy</button>
    </div>
  </div>

  <div class="instructions">
    <h3>Payment Instructions:</h3>
    <ol>
      <li>Open your crypto wallet (Trust Wallet, Binance, etc.)</li>
      <li>Select "Send" → Choose USDT</li>
      <li><strong>IMPORTANT:</strong> Select network "TRC-20" (Tron)</li>
      <li>Scan QR code OR paste address above</li>
      <li>Enter amount: <strong>125.00 USDT</strong></li>
      <li>Send transaction</li>
      <li>Wait 2-5 minutes for confirmation</li>
    </ol>
  </div>

  <div class="status" id="payment-status">
    ⏳ Waiting for payment...
  </div>
</div>

<script>
  function copyAddress() {
    const address = document.getElementById('address').textContent;
    navigator.clipboard.writeText(address);
    alert('Address copied!');
  }

  // Poll for payment confirmation
  setInterval(async () => {
    const response = await fetch('/check-payment?booking=BOOK-123');
    const { status } = await response.json();

    if (status === 'confirmed') {
      document.getElementById('payment-status').innerHTML =
        '✅ Payment confirmed! Redirecting...';
      setTimeout(() => window.location.href = '/success', 2000);
    }
  }, 10000); // Check every 10 seconds
</script>
```

---

### Step 3: Monitor Blockchain for Confirmation

**Option 1: Using TronGrid API (Free)**

```javascript
// check-payment.js
const axios = require('axios');

async function checkTronPayment(walletAddress, expectedAmount, bookingId) {
  const apiKey = process.env.TRONGRID_API_KEY; // Get from trongrid.io

  // Get recent transactions for wallet
  const response = await axios.get(
    `https://api.trongrid.io/v1/accounts/${walletAddress}/transactions/trc20`,
    {
      headers: { 'TRON-PRO-API-KEY': apiKey },
      params: {
        limit: 20,
        contract_address: 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t' // USDT TRC-20
      }
    }
  );

  const transactions = response.data.data;

  // Find matching transaction
  for (const tx of transactions) {
    const amountReceived = tx.value / 1e6; // USDT has 6 decimals
    const timestamp = tx.block_timestamp;

    // Check if amount matches and transaction is recent (last 1 hour)
    if (
      amountReceived >= expectedAmount * 0.99 && // Allow 1% variance
      amountReceived <= expectedAmount * 1.01 &&
      Date.now() - timestamp < 3600000
    ) {
      console.log(`✅ Payment confirmed: ${tx.transaction_id}`);

      // Update database
      await db.query(
        'UPDATE crypto_payments SET status = $1, tx_hash = $2, confirmed_at = NOW() WHERE booking_id = $3',
        ['confirmed', tx.transaction_id, bookingId]
      );

      return {
        confirmed: true,
        txHash: tx.transaction_id,
        amount: amountReceived
      };
    }
  }

  return { confirmed: false };
}
```

**Option 2: Using Tatum API (Easier, has webhooks)**

```javascript
const { TatumSDK, Network } = require('@tatumio/tatum');

const tatum = await TatumSDK.init({ network: Network.TRON });

// Subscribe to address (webhook notification)
await tatum.notification.subscribe.addressEvent({
  address: walletAddress,
  url: 'https://yoursite.com/webhook/tron'
});

// Webhook handler
app.post('/webhook/tron', async (req, res) => {
  const { address, asset, amount, txId } = req.body;

  console.log(`💰 Received ${amount} ${asset} to ${address}`);
  console.log(`TX: ${txId}`);

  // Find booking by address
  const payment = await db.query(
    'SELECT * FROM crypto_payments WHERE wallet_address = $1 AND status = $2',
    [address, 'pending']
  );

  if (payment.rows.length > 0) {
    // Mark as confirmed
    await db.query(
      'UPDATE crypto_payments SET status = $1, tx_hash = $2 WHERE id = $3',
      ['confirmed', txId, payment.rows[0].id]
    );

    // Send confirmation to customer
    await sendWhatsAppConfirmation(payment.rows[0].booking_id);
  }

  res.json({ received: true });
});
```

---

### Step 4: Blockchain Confirmations

**How many confirmations needed?**

| Amount | Confirmations | Wait Time (Tron) |
|--------|---------------|------------------|
| <$500 | 1 confirmation | ~3 minutes |
| $500-$2,000 | 3 confirmations | ~9 minutes |
| $2,000-$10,000 | 6 confirmations | ~18 minutes |
| >$10,000 | 12+ confirmations | ~36 minutes |

**Tron block time:** ~3 seconds (но финality ~3 minutes)

**Code example:**
```javascript
async function waitForConfirmations(txHash, requiredConfirmations = 3) {
  let confirmations = 0;

  while (confirmations < requiredConfirmations) {
    const txInfo = await tronWeb.trx.getTransactionInfo(txHash);

    if (txInfo.blockNumber) {
      const currentBlock = await tronWeb.trx.getCurrentBlock();
      confirmations = currentBlock.block_header.raw_data.number - txInfo.blockNumber;

      console.log(`Confirmations: ${confirmations}/${requiredConfirmations}`);
    }

    if (confirmations < requiredConfirmations) {
      await sleep(10000); // Wait 10 seconds
    }
  }

  return true;
}
```

---

## Exchange Rate APIs

**Get real-time USDT/AED rate:**

### Option 1: CoinGecko (Free, no API key)

```javascript
async function getUSDTRate() {
  const response = await axios.get(
    'https://api.coingecko.com/api/v3/simple/price',
    {
      params: {
        ids: 'tether',
        vs_currencies: 'usd,aed'
      }
    }
  );

  return {
    usd: response.data.tether.usd, // Usually ~1.00
    aed: response.data.tether.aed  // Usually ~3.67
  };
}
```

### Option 2: Binance (More accurate, free)

```javascript
async function getBinanceRate() {
  const response = await axios.get(
    'https://api.binance.com/api/v3/ticker/price',
    {
      params: { symbol: 'USDTUSD' }
    }
  );

  return parseFloat(response.data.price);
}
```

### Add markup for volatility protection

```javascript
function calculateCryptoPrice(amountAED, markup = 0.02) {
  const usdtRate = await getUSDTRate();
  const usdtAmount = amountAED / usdtRate.aed;

  // Add 2% markup to cover volatility
  const finalAmount = usdtAmount * (1 + markup);

  return {
    amount: finalAmount.toFixed(2),
    rate: usdtRate.aed,
    markup: markup * 100
  };
}
```

---

## Security Best Practices

### 1. Wallet Security

**DO:**
- ✅ Use hardware wallet (Ledger) for large holdings
- ✅ Enable 2FA on exchange accounts
- ✅ Backup seed phrase on paper (fireproof safe)
- ✅ Use multi-signature wallets for >$50k
- ✅ Regular sweeps: Hot wallet → Cold wallet

**DON'T:**
- ❌ Store seed phrase in cloud/email
- ❌ Share private keys with anyone
- ❌ Use same wallet for personal + business
- ❌ Keep large amounts in hot wallet

### 2. Transaction Verification

**Always verify:**
```javascript
// Check minimum confirmations
if (confirmations < 3) {
  throw new Error('Insufficient confirmations');
}

// Check exact amount (allow 1% tolerance)
const expectedMin = expectedAmount * 0.99;
const expectedMax = expectedAmount * 1.01;
if (amount < expectedMin || amount > expectedMax) {
  throw new Error('Amount mismatch');
}

// Check transaction age (prevent replay attacks)
const txAge = Date.now() - txTimestamp;
if (txAge > 3600000) { // 1 hour
  throw new Error('Transaction too old');
}

// Check not already processed
const existing = await db.query(
  'SELECT * FROM crypto_payments WHERE tx_hash = $1',
  [txHash]
);
if (existing.rows.length > 0) {
  throw new Error('Transaction already processed');
}
```

### 3. Scam Prevention

**Common scams:**
- **Fake payment screenshots:** Always verify on blockchain
- **Wrong network:** Customer sends ERC-20 instead of TRC-20
- **Underpayment:** Sends 99 USDT instead of 100 USDT
- **Phishing:** Fake wallet apps

**Prevention:**
```javascript
// Verify on MULTIPLE block explorers
const tronscan = await verifyOnTronscan(txHash);
const trongrid = await verifyOnTrongrid(txHash);

if (tronscan.amount !== trongrid.amount) {
  throw new Error('Block explorer mismatch - possible fraud');
}
```

---

## Refunds in Crypto

**Challenge:** Crypto transactions are irreversible.

**Refund process:**

1. Customer provides their wallet address
2. Verify customer identity (email, booking ID)
3. Calculate refund amount (may differ due to volatility)
4. Send refund transaction
5. Provide transaction hash to customer

**Code example:**
```javascript
async function processCryptoRefund(bookingId, customerAddress) {
  // Get original payment
  const payment = await db.query(
    'SELECT * FROM crypto_payments WHERE booking_id = $1',
    [bookingId]
  );

  const originalAmount = payment.rows[0].amount_usdt;

  // Verify customer address format
  if (!TronWeb.isAddress(customerAddress)) {
    throw new Error('Invalid Tron address');
  }

  // Send refund
  const tronWeb = new TronWeb({
    fullHost: 'https://api.trongrid.io',
    privateKey: process.env.TRON_PRIVATE_KEY
  });

  const contract = await tronWeb.contract().at(
    'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t' // USDT contract
  );

  const tx = await contract.transfer(
    customerAddress,
    originalAmount * 1e6 // 6 decimals
  ).send();

  console.log(`✅ Refund sent: ${tx}`);

  // Update database
  await db.query(
    'UPDATE crypto_payments SET status = $1, refund_tx = $2 WHERE booking_id = $3',
    ['refunded', tx, bookingId]
  );

  return tx;
}
```

---

## Tax Implications (UAE)

**ОАЭ crypto regulations:**
- Crypto payments are LEGAL in UAE
- VARA (Virtual Asset Regulatory Authority) oversees crypto
- No capital gains tax on crypto (yet)
- VAT 5% still applies to tourism services

**Accounting:**
```javascript
// Record crypto payment in AED equivalent
const payment = {
  booking_id: 'BOOK-123',
  amount_usdt: 125.00,
  usdt_rate_aed: 3.67,
  amount_aed: 125.00 * 3.67, // 458.75 AED
  vat_aed: 458.75 * 0.05,    // 22.94 AED
  total_aed: 481.69,
  payment_method: 'USDT_TRC20',
  tx_hash: '0xabc...'
};

await db.query(
  'INSERT INTO payments (booking_id, amount_aed, vat_aed, payment_method, tx_hash) VALUES ($1, $2, $3, $4, $5)',
  [payment.booking_id, payment.amount_aed, payment.vat_aed, payment.payment_method, payment.tx_hash]
);
```

**Converting to fiat:**
- Use Binance P2P (AED available)
- BitOasis (UAE-based exchange)
- Rain (licensed in Bahrain, supports AED)

---

## Complete Example: USDT Payment Integration

```javascript
// Full working example
const express = require('express');
const TronWeb = require('tronweb');
const QRCode = require('qrcode');
const axios = require('axios');

const app = express();
app.use(express.json());

const tronWeb = new TronWeb({
  fullHost: 'https://api.trongrid.io',
  headers: { 'TRON-PRO-API-KEY': process.env.TRONGRID_API_KEY }
});

// Generate payment request
app.post('/api/crypto/generate-payment', async (req, res) => {
  const { bookingId, amountAED } = req.body;

  // Get USDT rate
  const rate = await getUSDTRate();
  const amountUSDT = (amountAED / rate.aed * 1.02).toFixed(2); // 2% markup

  // Generate QR
  const walletAddress = process.env.TRON_WALLET_ADDRESS;
  const qrCode = await QRCode.toDataURL(`tron:${walletAddress}?amount=${amountUSDT}`);

  // Save to DB
  await db.query(
    'INSERT INTO crypto_payments (booking_id, amount_usdt, wallet_address) VALUES ($1, $2, $3)',
    [bookingId, amountUSDT, walletAddress]
  );

  res.json({
    walletAddress,
    amount: amountUSDT,
    network: 'TRC-20',
    qrCode,
    expiresAt: Date.now() + 3600000 // 1 hour
  });
});

// Check payment status
app.get('/api/crypto/check-payment', async (req, res) => {
  const { bookingId } = req.query;

  const result = await checkTronPayment(
    process.env.TRON_WALLET_ADDRESS,
    bookingId
  );

  res.json(result);
});

async function getUSDTRate() {
  const response = await axios.get(
    'https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=aed'
  );
  return { aed: response.data.tether.aed };
}

async function checkTronPayment(walletAddress, bookingId) {
  const payment = await db.query(
    'SELECT * FROM crypto_payments WHERE booking_id = $1',
    [bookingId]
  );

  if (payment.rows[0].status === 'confirmed') {
    return { status: 'confirmed', txHash: payment.rows[0].tx_hash };
  }

  // Check blockchain
  const response = await axios.get(
    `https://api.trongrid.io/v1/accounts/${walletAddress}/transactions/trc20`,
    {
      headers: { 'TRON-PRO-API-KEY': process.env.TRONGRID_API_KEY },
      params: {
        limit: 20,
        contract_address: 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'
      }
    }
  );

  for (const tx of response.data.data) {
    const amount = tx.value / 1e6;
    if (Math.abs(amount - payment.rows[0].amount_usdt) < 0.01) {
      // Found matching payment
      await db.query(
        'UPDATE crypto_payments SET status = $1, tx_hash = $2 WHERE booking_id = $3',
        ['confirmed', tx.transaction_id, bookingId]
      );

      return { status: 'confirmed', txHash: tx.transaction_id };
    }
  }

  return { status: 'pending' };
}

app.listen(3000, () => console.log('Server running'));
```

---

## Troubleshooting

**Problem: Customer sent to wrong network (ERC-20 instead of TRC-20)**

**Solution:** Funds are NOT lost but require recovery:
1. If you control both networks' addresses: Import same private key to ETH wallet
2. If not: Funds are unrecoverable (warn customers clearly!)

**Problem: Payment not detected**

**Checklist:**
- [ ] Verify transaction on Tronscan.io
- [ ] Check correct wallet address
- [ ] Verify network (TRC-20 vs ERC-20)
- [ ] Check blockchain sync status
- [ ] Verify API key limits not exceeded

**Problem: Amount mismatch**

**Causes:**
- Customer didn't include network fees
- Exchange rate changed mid-payment
- Customer sent from exchange (exchange fees deducted)

**Solution:** Accept ±2% variance or ask customer to top up difference.

---

## Resources

**Block Explorers:**
- Tronscan: https://tronscan.org
- TronGrid: https://www.trongrid.io

**APIs:**
- TronGrid API: https://developers.tron.network
- CoinGecko: https://www.coingecko.com/api
- Tatum: https://tatum.io

**Exchanges (UAE):**
- Binance (supports AED): https://binance.com
- BitOasis (UAE-based): https://bitoasis.net
- Rain: https://rain.bh

**Regulation:**
- VARA (UAE): https://vara.ae

---

**Word count:** ~1,500 words
**Implementation time:** 2-3 hours
**Difficulty:** Intermediate

Next: See `05-paypal-integration.md` for PayPal alternative.
