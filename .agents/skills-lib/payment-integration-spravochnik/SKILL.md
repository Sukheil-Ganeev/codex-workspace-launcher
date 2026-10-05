---
name: payment-integration-spravochnik
description: "Production-ready integration of payment systems (Stripe, Telr, USDT, PayPal) for UAE tourism business - covers deposits, refunds, splits, recurring, WhatsApp links, fraud detection, multi-currency"
---
# Payment Integration Production Справочник

**Версия:** 1.0
**Последнее обновление:** 2026-02-04
**Уровень:** Продвинутый (Production-ready)
**Охват:** International + UAE + Crypto Payment Systems

---

## 1. Введение и философия платёжных интеграций

### Почему payment integration критичен для туристического бизнеса

Туристический бизнес в ОАЭ работает с **международными клиентами** из разных стран, каждый со своими предпочтениями в оплате:

- **Россия:** Карты Мир, переводы на Сбер/Тинькофф (санкции на Visa/MC)
- **Казахстан:** Kaspi.kz (самый популярный метод)
- **Европа/США:** Stripe, PayPal (доверенные бренды)
- **Локально в ОАЭ:** Telr, Network International (AED, местные карты)
- **Crypto-энтузиасты:** USDT, Bitcoin (анонимность, низкие fees)

**Без правильной интеграции вы теряете 30-50% потенциальных клиентов** просто потому что им неудобно платить.

**Ключевые требования:**
- Multi-currency support (AED, USD, RUB, KZT, EUR)
- Deposits (30-50% сейчас, остальное позже)
- Instant confirmations (автоматизация через webhooks)
- Fraud prevention (защита от мошенников)
- WhatsApp/Telegram integration (клиенты общаются там)
- Accounting compliance (ОАЭ VAT 5%, multi-currency reconciliation)

### Hosted vs Direct API vs SDK интеграция

**3 основных подхода к интеграции платёжных систем:**

#### 1. Hosted Payment Pages (самый простой)

**Как работает:**
- Вы redirect клиента на страницу платёжной системы
- Клиент вводит данные карты там
- После оплаты redirect обратно на ваш сайт

**Преимущества:**
- ✅ Быстрая интеграция (1-2 часа)
- ✅ PCI DSS compliant (вы не трогаете card data)
- ✅ Минимум кода
- ✅ Автоматические security updates

**Недостатки:**
- ❌ Меньше контроля над UI/UX
- ❌ Redirect может снизить conversion (клиенты покидают сайт)
- ❌ Брендинг платёжной системы, не ваш

**Пример (Stripe Checkout):**
```javascript
const session = await stripe.checkout.sessions.create({
  payment_method_types: ['card'],
  line_items: [{
    price_data: {
      currency: 'aed',
      product_data: { name: 'Desert Safari Tour' },
      unit_amount: 25000, // 250.00 AED
    },
    quantity: 1,
  }],
  mode: 'payment',
  success_url: 'https://yoursite.com/success',
  cancel_url: 'https://yoursite.com/cancel',
});

// Redirect клиента
res.redirect(303, session.url);
```

**Когда использовать:** MVP, Quick Start, low-volume, или если у вас нет времени на complex integration.

#### 2. Direct API Integration (гибкость)

**Как работает:**
- Клиент вводит данные на вашем сайте
- Вы отправляете API request напрямую к провайдеру
- Получаете response и обрабатываете result

**Преимущества:**
- ✅ Полный контроль над UX
- ✅ Customization (branding, multi-step, A/B tests)
- ✅ Меньше redirects = higher conversion
- ✅ Можно комбинировать multiple providers

**Недостатки:**
- ❌ Больше кода (security, validation, error handling)
- ❌ PCI DSS требования (если трогаете card data)
- ❌ Нужно обрабатывать edge cases

**Пример (Stripe Payment Intents):**
```javascript
// Server-side: Create Payment Intent
const paymentIntent = await stripe.paymentIntents.create({
  amount: 25000, // 250.00 AED
  currency: 'aed',
  payment_method_types: ['card'],
  metadata: {
    booking_id: 'BOOK-12345',
    tour_name: 'Desert Safari',
  },
});

// Client-side: Confirm payment с Stripe.js
const {error} = await stripe.confirmCardPayment(
  paymentIntent.client_secret,
  {
    payment_method: {
      card: cardElement,
      billing_details: {name: 'Customer Name'},
    },
  }
);
```

**Когда использовать:** Production apps, high-volume, когда нужен custom UI, или multiple payment flows.

#### 3. SDK Integration (developer-friendly)

**Как работает:**
- Используете официальную библиотеку провайдера
- SDK абстрагирует low-level API calls
- Type-safe, auto-completion, built-in validation

**Преимущества:**
- ✅ Меньше boilerplate code
- ✅ Type safety (TypeScript support)
- ✅ Автоматическая retry logic
- ✅ Built-in error handling

**Недостатки:**
- ❌ Зависимость от SDK updates
- ❌ Иногда SDK отстаёт от API features
- ❌ Bundle size (если используете client-side)

**Пример (Stripe Node.js SDK):**
```javascript
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

const payment = await stripe.paymentIntents.create({
  amount: 25000,
  currency: 'aed',
  automatic_payment_methods: {enabled: true},
});
```

**Когда использовать:** Почти всегда! SDK = best practice для production.

**Рекомендация для туристического бизнеса:**
- **Start:** Hosted (Stripe Checkout) - первый платёж за 30 минут
- **Production:** SDK + Direct API - полный контроль и flexibility
- **Advanced:** Multiple providers (Stripe + Telr fallback)

---

### PCI DSS Compliance basics

**PCI DSS** (Payment Card Industry Data Security Standard) - это набор требований безопасности для всех, кто обрабатывает платёжные карты.

**4 уровня compliance (по объёму транзакций/год):**
- Level 1: >6 million
- Level 2: 1-6 million
- Level 3: 20,000-1 million
- **Level 4: <20,000** ← Большинство малого/среднего бизнеса

**Для Level 4 (упрощённые требования):**

✅ **Что нужно делать:**
1. Use HTTPS (TLS 1.2+) для всех payment pages
2. НИКОГДА не храни full card numbers (используй tokenization)
3. НИКОГДА не храни CVV/CVC
4. Use hosted payment pages ИЛИ Stripe Elements/PayPal SDK (они PCI compliant)
5. Keep software updated (Node.js, dependencies)
6. Use strong passwords и 2FA для admin access
7. Restrict access to card data (only необходимым employees)
8. Monitor и log все access к payment systems
9. Regular security testing

❌ **Что НИКОГДА не делать:**
- Хранить card data в plain text
- Логировать CVV или full card numbers
- Отправлять card data по email
- Hardcode API keys в коде
- Использовать weak encryption

**Пример НЕПРАВИЛЬНОГО кода:**
```javascript
// ❌ НИКОГДА так не делай!
const customer = {
  name: 'John Doe',
  card_number: '4242424242424242', // НИКОГДА не храни!
  cvv: '123', // НИКОГДА не храни!
  expiry: '12/25',
};
db.insert('customers', customer); // SECURITY BREACH!
```

**Пример ПРАВИЛЬНОГО кода:**
```javascript
// ✅ Используй tokenization
const paymentMethod = await stripe.paymentMethods.create({
  type: 'card',
  card: {
    number: '4242424242424242',
    exp_month: 12,
    exp_year: 2025,
    cvc: '123',
  },
});

// Stripe возвращает token, храни только его
const customer = {
  name: 'John Doe',
  stripe_payment_method_id: paymentMethod.id, // pm_xxx - безопасный token
  last4: '4242', // Только последние 4 цифры
};
db.insert('customers', customer); // Безопасно!
```

**Simplified compliance через Stripe/PayPal:**
- Они SAQ A compliant (самый простой вариант)
- Card data обрабатывается на их стороне
- Вы получаете только token
- Ваша PCI scope минимальна

**Self-Assessment Questionnaire (SAQ):**
Раз в год заполняете form на сайте провайдера (Stripe Dashboard → Compliance).

**Результат:** Если используете Stripe Checkout, Stripe Elements, или PayPal SDK - вы автоматически compliant для Level 4! 🎉

---

### Выбор правильного провайдера

**Decision matrix для туристического бизнеса в ОАЭ:**

| Критерий | Stripe | Telr | PayPal | USDT |
|----------|--------|------|--------|------|
| **International cards** | ✅ Excellent | ⚠️ Limited | ✅ Good | N/A |
| **UAE local cards** | ✅ Good | ✅ Excellent | ⚠️ Limited | N/A |
| **AED currency** | ✅ Yes | ✅ Yes (primary) | ✅ Yes | Convert |
| **Fees** | 2.9% + $0.30 | 2.75% + flat | 3.4% + fee | ~1-2% |
| **Setup complexity** | Easy | Medium | Easy | Medium |
| **Developer experience** | ✅ Excellent | ⚠️ OK | ✅ Good | DIY |
| **Webhooks** | ✅ Excellent | ✅ Good | ✅ Good | Manual |
| **Multi-currency** | ✅ 135+ | ⚠️ Limited | ✅ 25+ | Crypto only |
| **Fraud prevention** | ✅ Radar AI | ⚠️ Basic | ✅ Good | Manual |
| **Refunds** | ✅ Instant API | ⚠️ Manual | ✅ API | Irreversible |
| **Best for** | International | UAE locals | Trust factor | Crypto users |

**Рекомендация (multi-provider strategy):**

**Primary:** Stripe
- Лучший DX (developer experience)
- 135+ currencies
- Stripe Radar (fraud prevention)
- Instant refunds
- Webhooks работают отлично

**Fallback:** Telr
- Если Stripe fails (карта не поддерживается)
- Локальные ОАЭ карты
- AED-focused

**Optional:** PayPal
- Клиенты с PayPal balance
- Trust factor (узнаваемость бренда)
- Некоторые предпочитают PayPal > карты

**Niche:** USDT (Crypto)
- Для crypto-энтузиастов
- Низкие fees (~1%)
- Нужен manual confirmation process

**Пример multi-provider logic:**
```javascript
async function processPayment(amount, currency, customerPreference) {
  if (customerPreference === 'crypto') {
    return await processUSDTPayment(amount);
  }

  if (currency === 'AED' && customerLocation === 'UAE') {
    try {
      return await processTelrPayment(amount, currency);
    } catch (err) {
      // Fallback to Stripe
      return await processStripePayment(amount, currency);
    }
  }

  // Default: Stripe
  return await processStripePayment(amount, currency);
}
```

---

## 2. Quick Start: Первый платёж за 30 минут

### Универсальный payment flow

Независимо от провайдера, все платёжные интеграции следуют одному базовому flow:

```
1. Create Payment Intent → 2. Collect Payment Info → 3. Process Payment
→ 4. Handle Webhook → 5. Confirm to Customer
```

### Шаг 1: Setup (5 минут)

**1.1 Установка dependencies:**
```bash
npm install stripe express dotenv
```

**1.2 Создание .env файла:**
```env
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
PORT=3000
```

**1.3 Получение API keys:**
- Зарегистрируйтесь на stripe.com
- Dashboard → API keys
- Используйте **test mode keys** для начала (префикс `sk_test_`)

### Шаг 2: Create server + payment form (20 минут)

Создайте Express-сервер с двумя endpoints: `/create-payment-intent` (создание платежа) и `/webhook` (получение уведомлений от Stripe). Фронтенд использует Stripe.js + Card Element для безопасного ввода данных карты.

**Ключевые моменты:**
- Webhook endpoint использует `express.raw()` для верификации подписи
- Payment Intent создается на сервере, client получает только `client_secret`
- Card Element обрабатывает данные карты на стороне Stripe (PCI compliant)

> **Полный код server.js и index.html:** `references/01-quick-start-guide.md` (Steps 4-5)

### Шаг 4: Testing (5 минут)

**1. Запустите server:**
```bash
node server.js
```

**2. Откройте в браузере:**
```
http://localhost:3000
```

**3. Test cards (Stripe test mode):**
- **Success:** 4242 4242 4242 4242
- **Decline:** 4000 0000 0000 0002
- **3D Secure:** 4000 0025 0000 3155

**CVV:** любые 3 цифры (например, 123)
**Expiry:** любая будущая дата (например, 12/25)

### Шаг 5: Webhook setup (optional, но рекомендуется)

**1. Install Stripe CLI для local testing:**
```bash
stripe listen --forward-to localhost:3000/webhook
```

**2. Копируйте webhook signing secret в .env:**
```env
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

**3. Test payment и смотрите webhook events в консоли**

### Troubleshooting Quick Start

**Проблема:** "Invalid API Key provided"
**Решение:** Проверьте что `STRIPE_SECRET_KEY` начинается с `sk_test_` или `sk_live_`

**Проблема:** "No such payment_intent"
**Решение:** Убедитесь что используете правильный `clientSecret` от server

**Проблема:** Webhook не приходит
**Решение:** Используйте Stripe CLI для local testing, или ngrok для public URL

**Результат:** Вы только что приняли свой первый платёж! 🎉

---

## 3. Stripe Integration (детально)

### Payment Intents API (рекомендуемый подход)

**Payment Intent** - это объект, представляющий намерение собрать платёж. Он проходит через несколько статусов:

```
requires_payment_method → requires_confirmation → processing → succeeded
                                                           ↓
                                                        failed
```

**Создание Payment Intent:**
```javascript
const paymentIntent = await stripe.paymentIntents.create({
  amount: 25000, // 250.00 AED (в fils - smallest unit)
  currency: 'aed',
  payment_method_types: ['card'],
  metadata: {
    booking_id: 'BOOK-12345',
    customer_email: 'customer@example.com',
    tour_name: 'Desert Safari',
  },
  description: 'Desert Safari Tour - Booking BOOK-12345',
  receipt_email: 'customer@example.com', // Auto-send receipt
});
```

**Metadata best practices:**
- Используйте metadata для связи с вашей системой
- Максимум 50 ключей, каждое значение до 500 символов
- Metadata появляется в Dashboard и webhooks

### Webhooks (критически важно!)

**Почему нужны webhooks:**
- Клиент может закрыть браузер после оплаты
- Network может прерваться
- Асинхронные события (refunds, disputes)
- Subscription renewals

**Основные события:**
```javascript
// payment_intent.succeeded - Платёж успешен
if (event.type === 'payment_intent.succeeded') {
  const paymentIntent = event.data.object;
  // Update database: booking status = 'paid'
  // Send confirmation email
  // Update inventory
}

// payment_intent.payment_failed - Платёж failed
if (event.type === 'payment_intent.payment_failed') {
  const paymentIntent = event.data.object;
  // Notify customer
  // Retry logic or suggest alternative payment method
}

// charge.refunded - Возврат выполнен
if (event.type === 'charge.refunded') {
  const charge = event.data.object;
  // Update database: booking status = 'refunded'
  // Send refund confirmation
}
```

**Webhook signature verification (обязательно!):**
```javascript
app.post('/webhook', express.raw({type: 'application/json'}), async (req, res) => {
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

  // Handle event
  switch (event.type) {
    case 'payment_intent.succeeded':
      await handlePaymentSuccess(event.data.object);
      break;
    case 'payment_intent.payment_failed':
      await handlePaymentFailure(event.data.object);
      break;
    default:
      console.log(`Unhandled event type: ${event.type}`);
  }

  res.json({received: true});
});
```

### Refunds (возвраты)

**Full refund:**
```javascript
const refund = await stripe.refunds.create({
  payment_intent: 'pi_xxxxx',
  reason: 'requested_by_customer', // 'duplicate', 'fraudulent', 'requested_by_customer'
});
```

**Partial refund:**
```javascript
const refund = await stripe.refunds.create({
  payment_intent: 'pi_xxxxx',
  amount: 5000, // Refund 50 AED из 250 AED
  reason: 'requested_by_customer',
  metadata: {
    refund_reason: 'Changed booking date',
  },
});
```

**Refund timeline:**
- **Credit cards:** 5-10 business days
- **Stripe fee:** Не возвращается (2.9% + $0.30)
- **Instant status:** refund.succeeded webhook через несколько секунд

### Multi-currency (135+ валют)

**Supported currencies в ОАЭ/CIS context:**
- AED (UAE Dirham) - основная
- USD (US Dollar) - международная
- EUR (Euro)
- GBP (British Pound)
- RUB (Russian Ruble) - ограничения из-за sanctions
- KZT (Kazakhstani Tenge)

**Пример multi-currency pricing:**
```javascript
const prices = {
  aed: 25000, // 250.00 AED
  usd: 6800,  // 68.00 USD (~3.67 exchange rate)
  eur: 6200,  // 62.00 EUR
};

const currency = req.body.currency || 'aed';
const amount = prices[currency];

const paymentIntent = await stripe.paymentIntents.create({
  amount: amount,
  currency: currency,
});
```

**Currency conversion best practices:**
- Обновляйте курсы ежедневно
- Добавляйте markup (1-3%) для покрытия volatility
- Показывайте approximate amount в местной валюте
- Храните original currency для accounting

### Stripe Radar (fraud prevention)

**Автоматическая защита (included free):**
- Machine learning анализирует каждую транзакцию
- Блокирует подозрительные платежи
- Risk score 0-100

**Custom rules (Radar for Fraud Teams - $0.05/transaction):**
```javascript
// Примеры правил:
// - Block if IP country ≠ card country
// - Block if email is disposable
// - Require 3D Secure if amount > 500 AED
// - Allow only specific countries
```

**Handling declined payments:**
```javascript
try {
  const paymentIntent = await stripe.paymentIntents.create({...});
} catch (err) {
  if (err.code === 'card_declined') {
    // Suggest alternative payment method
    // Or ask customer to contact their bank
  }
}
```

---

## 4. Telr Integration (ОАЭ специфика)

### Telr Ivp5 API Overview

**Telr** - локальный ОАЭ payment gateway, оптимизированный для:
- AED транзакций
- Местных банковских карт (Emirates NBD, ADCB, etc.)
- GCC market (Gulf Cooperation Council)

**Integration modes:**
1. **Hosted Payment Page** - Redirect to Telr (самый простой)
2. **Direct API** - Custom checkout на вашем сайте

### Hosted Payment Page Integration

**Step 1: Create order:**
```javascript
const axios = require('axios');

async function createTelrOrder(amount, currency, orderId) {
  const response = await axios.post('https://secure.telr.com/gateway/order.json', {
    method: 'create',
    store: process.env.TELR_STORE_ID,
    authkey: process.env.TELR_AUTH_KEY,
    order: {
      cartid: orderId,
      amount: amount, // В основных единицах: 250 для 250 AED
      currency: currency,
      description: 'Desert Safari Tour',
    },
    return: {
      authorised: 'https://yoursite.com/payment/success',
      declined: 'https://yoursite.com/payment/declined',
      cancelled: 'https://yoursite.com/payment/cancelled',
    },
  });

  return response.data;
}

// Usage:
const telrOrder = await createTelrOrder(250, 'AED', 'BOOK-12345');
const paymentUrl = telrOrder.order.url;
// Redirect customer: res.redirect(paymentUrl);
```

**Step 2: Handle return:**
```javascript
app.get('/payment/success', async (req, res) => {
  const orderId = req.query.cart_id;
  const telrRef = req.query.order_ref;

  // Verify transaction
  const verification = await verifyTelrTransaction(telrRef);

  if (verification.order.status.code === 3) { // 3 = Paid
    // Update database
    await updateBookingStatus(orderId, 'paid');
    res.render('success', {orderId: orderId});
  } else {
    res.render('error', {message: 'Payment verification failed'});
  }
});
```

**Step 3: Verify transaction (important!):**
```javascript
async function verifyTelrTransaction(orderRef) {
  const response = await axios.post('https://secure.telr.com/gateway/order.json', {
    method: 'check',
    store: process.env.TELR_STORE_ID,
    authkey: process.env.TELR_AUTH_KEY,
    order: {
      ref: orderRef,
    },
  });

  return response.data;
}
```

### Telr Status Codes

```javascript
const TELR_STATUS = {
  1: 'Initiated', // Order created
  2: 'Processing', // Payment in progress
  3: 'Paid', // ✅ Success
  4: 'Failed', // ❌ Declined
  5: 'Cancelled', // User cancelled
  6: 'Refunded', // Refund processed
  7: 'Pending', // Awaiting confirmation
};
```

### AED Currency Specifics

**Smallest unit:** AED doesn't use smallest unit like fils in Telr
- Telr expects: `250` for 250.00 AED (не 25000)
- Отличается от Stripe!

**VAT calculation (5% в ОАЭ):**
```javascript
const subtotal = 250; // AED
const vat = Math.round(subtotal * 0.05); // 12.50 AED
const total = subtotal + vat; // 262.50 AED

// Display to customer
console.log(`Subtotal: ${subtotal} AED`);
console.log(`VAT (5%): ${vat} AED`);
console.log(`Total: ${total} AED`);
```

### Refunds (manual process)

**Telr refunds** не имеют instant API (в отличие от Stripe):
1. Login to Telr Dashboard
2. Find transaction
3. Click "Refund"
4. Approve refund

**Alternative:** Contact Telr support для API refunds (требует специального доступа)

### Test Credentials

**Test Store ID:** Предоставляется Telr после регистрации
**Test cards:**
```
Success: 4005 5500 0000 0001
Declined: 4005 5500 0000 0019
```

**3D Secure test:**
```
Password: secret
```

---

## 5. Cryptocurrency Payments (USDT/Bitcoin)

### Почему Crypto для туризма?

**Преимущества:**
- **Low fees:** ~1-2% vs 2.9-3.4% для cards
- **Fast:** Bitcoin ~10-60 min, USDT ~5-15 min
- **No chargebacks:** Irreversible
- **Privacy:** Анонимность для клиентов
- **International:** Работает везде

**Недостатки:**
- **Volatility:** Цена может измениться за минуты
- **Complexity:** Клиенты должны иметь wallet
- **Manual confirmation:** Нужно проверять blockchain
- **Irreversible:** Ошибка = потеря средств

### USDT (Tether) - Рекомендация

**USDT** = stablecoin, привязанный к USD (1 USDT ≈ $1)
- **Сети:** Ethereum (ERC-20), Tron (TRC-20), Binance Smart Chain (BEP-20)
- **Рекомендуем:** TRC-20 (низкие fees, ~$1 vs $10+ на Ethereum)

### Wallet Setup

**1. Create wallet (cold storage для безопасности):**
```javascript
// НЕ используйте в production! Это пример.
// Используйте hardware wallet или secure cloud HSM.
const ethers = require('ethers');

const wallet = ethers.Wallet.createRandom();
console.log('Address:', wallet.address);
console.log('Private Key:', wallet.privateKey); // ⚠️ ХРАНИ В БЕЗОПАСНОСТИ!
```

**2. Для каждого платежа генерируйте unique address:**
```javascript
// Используйте HD wallets (BIP-39) для derivation
const hdNode = ethers.utils.HDNode.fromMnemonic(MASTER_MNEMONIC);
const derivedWallet = hdNode.derivePath(`m/44'/60'/0'/0/${bookingId}`);
const paymentAddress = derivedWallet.address;
```

### Payment Flow

**Step 1: Calculate USDT amount:**
```javascript
const axios = require('axios');

async function convertAEDtoUSDT(aedAmount) {
  // Get AED → USD rate
  const response = await axios.get('https://api.exchangerate-api.com/v4/latest/AED');
  const aedToUsd = response.data.rates.USD;

  const usdAmount = aedAmount * aedToUsd; // 250 AED → ~68 USD
  const usdtAmount = usdAmount; // USDT ≈ USD

  // Add 1-2% markup для volatility buffer
  const markup = 1.02;
  return (usdtAmount * markup).toFixed(2);
}

// Usage:
const usdtAmount = await convertAEDtoUSDT(250); // ~69.36 USDT
```

**Step 2: Display QR code:**
```javascript
const QRCode = require('qrcode');

app.get('/crypto-payment/:bookingId', async (req, res) => {
  const bookingId = req.params.bookingId;
  const booking = await getBooking(bookingId);

  const paymentAddress = await generatePaymentAddress(bookingId);
  const usdtAmount = await convertAEDtoUSDT(booking.amount);

  // Generate QR code
  const qrCode = await QRCode.toDataURL(paymentAddress);

  res.render('crypto-payment', {
    address: paymentAddress,
    amount: usdtAmount,
    qrCode: qrCode,
    expiresIn: '30 minutes',
  });
});
```

**Step 3: Monitor blockchain:**
```javascript
// Tron network (TRC-20 USDT)
const TronWeb = require('tronweb');

async function checkUSDTPayment(address, expectedAmount) {
  const tronWeb = new TronWeb({
    fullHost: 'https://api.trongrid.io',
  });

  // USDT contract на Tron: TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t
  const contract = await tronWeb.contract().at('TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t');

  // Check balance
  const balance = await contract.balanceOf(address).call();
  const balanceUSDT = balance / 1e6; // USDT has 6 decimals

  if (balanceUSDT >= expectedAmount) {
    return {confirmed: true, amount: balanceUSDT};
  }

  return {confirmed: false};
}

// Poll every 30 seconds
setInterval(async () => {
  const result = await checkUSDTPayment(paymentAddress, expectedUSDT);
  if (result.confirmed) {
    await updateBookingStatus(bookingId, 'paid');
    // Send confirmation
  }
}, 30000);
```

### Security Best Practices

**1. Use cold storage для main balance:**
- Hardware wallet (Ledger, Trezor)
- Multi-sig wallet (требует 2+ подписей)

**2. Hot wallet только для incoming payments:**
- Периодически sweep funds в cold storage
- Limit exposure

**3. Confirmations:**
- Bitcoin: Wait 1-3 confirmations (~10-30 min)
- USDT (Tron): Wait 1 confirmation (~5 min)
- USDT (Ethereum): Wait 12 confirmations (~3 min)

**4. Monitor для double-spend attacks:**
- Для больших сумм (>10,000 AED) wait больше confirmations

---

## 6. Regional Payment Methods

### Russia: Sanctions и альтернативы

**Проблема:** Visa/Mastercard не работают для российских карт (sanctions)

**Альтернативы:**
1. **Карты МИР:** Работают только внутри России
2. **Банковские переводы:** SWIFT (медленно, высокие fees)
3. **Криптовалюта:** USDT, Bitcoin (популярно)
4. **Payment aggregators:** Например, YooMoney, QIWI (если они доступны internationally)
5. **Cash:** Клиент платит наличными в офисе или через Western Union

**Recommended approach:**
```javascript
if (customerCountry === 'RU') {
  // Offer:
  // 1. USDT/Bitcoin payment (fast, low fees)
  // 2. SWIFT transfer (3-5 days, high fees)
  // 3. Cash on arrival (если клиент в ОАЭ)
}
```

### Kazakhstan: Kaspi.kz Integration

**Kaspi.kz** - самый популярный payment метод в Казахстане (70%+ market share)

**Integration options:**
1. **Kaspi Pay API** (требует бизнес-аккаунт)
2. **Manual:** Клиент переводит на ваш Kaspi wallet, присылает чек в WhatsApp

**Manual flow (simple):**
```javascript
app.post('/kaspi-payment-request', async (req, res) => {
  const {bookingId, amount} = req.body;

  // Generate payment instructions
  const instructions = {
    kaspi_phone: '+7 777 123 4567', // Ваш Kaspi номер
    amount_kzt: amount * 180, // 250 AED → 45,000 KZT (approximate rate)
    reference: `BOOK-${bookingId}`,
    instructions: [
      '1. Откройте Kaspi app',
      '2. Переводы → По номеру телефона',
      `3. Введите: ${kaspi_phone}`,
      `4. Сумма: ${amount_kzt} KZT`,
      `5. Комментарий: BOOK-${bookingId}`,
      '6. Отправьте screenshot в WhatsApp',
    ],
  };

  // Send to customer via WhatsApp
  await sendWhatsAppMessage(customer.phone, formatInstructions(instructions));

  res.json({status: 'instructions_sent'});
});
```

### International: SWIFT Transfers

**Для больших сумм (>5,000 AED):**
```javascript
const swiftDetails = {
  beneficiary_name: 'Your Business LLC',
  bank_name: 'Emirates NBD',
  swift_code: 'EBILAEAD',
  iban: 'AE070260001012345678901',
  reference: `BOOKING-${bookingId}`,
  amount: `${amount} AED`,
  timeline: '3-5 business days',
  fees: 'Customer pays all transfer fees',
};
```

**Verification:**
- Клиент присылает transfer receipt
- Вы проверяете bank statement через 3-5 дней
- После подтверждения → confirm booking

---

## 7. Business Scenarios для туризма

### Deposit + Balance Payments

**Scenario:** Клиент платит 30% сейчас, 70% за 48h до тура

**Flow:** Создание бронирования с deposit (30%) через Stripe Payment Intent, обработка webhook при оплате, автоматическое напоминание о balance (70%) за 48 часов до тура через cron/scheduler.

**Database:** Две таблицы -- `bookings` (статусы deposit/balance, даты) и `transactions` (тип, провайдер, статус).

### Group Split Payments

**Scenario:** 5 человек бронируют яхту, каждый платит свою часть

**Flow:** Создание group booking, генерация индивидуальных payment links для каждого участника, отправка через WhatsApp, автоматическая проверка полной оплаты группы.

> **Полный код (DB schema, deposit flow, group split, balance reminder):** `references/08-business-scenarios.md` (Sections 1-2)

### Refund Workflows

**Cancellation policy (автоматическая):**
- 7+ дней до тура: 100% возврат
- 3-6 дней: 50% возврат
- менее 3 дней: без возврата

Реализация через Stripe Refunds API с metadata (booking_id, refund_percentage, причина отмены) + обновление DB + уведомление клиента.

> **Полный код refund workflow:** `references/08-business-scenarios.md` (Section 3)

---

## 8. Security & Compliance

### Environment Variables (обязательно!)

**НИКОГДА не храни credentials в коде:**
```javascript
// ❌ WRONG
const stripe = require('stripe')('sk_live_XXXXXX');

// ✅ CORRECT
require('dotenv').config();
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
```

**.env file:**
```env
# Stripe
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# Telr
TELR_STORE_ID=12345
TELR_AUTH_KEY=xxxxx

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/payments

# App
NODE_ENV=production
PORT=3000
```

**.gitignore:**
```
.env
.env.local
.env.production
node_modules/
```

### Rate Limiting (prevent abuse)

**Implementation:**
```javascript
const rateLimit = require('express-rate-limit');

// General API rate limit
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per window
  message: 'Too many requests, please try again later',
});

// Stricter limit for payment endpoints
const paymentLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 10, // Max 10 payment attempts per hour
  message: 'Too many payment attempts, please contact support',
});

app.use('/api/', apiLimiter);
app.use('/create-payment-intent', paymentLimiter);
app.use('/booking/create', paymentLimiter);
```

### Fraud Detection (real-time)

**Risk scoring система (0-100 баллов):**

| Проверка | Баллы | Описание |
|----------|-------|----------|
| IP geolocation mismatch | +20 | IP страна не совпадает с billing country |
| Disposable email | +30 | Одноразовый email (temp-mail и т.д.) |
| Velocity check | +25 | >3 платежей с одного IP за час |
| Amount anomaly | +15 | Сумма >3x средней транзакции |
| Blacklist match | +50 | Email/IP в чёрном списке |

**Действия по уровню риска:**
- **0-40:** Proceed normally
- **40-70:** Require 3D Secure / CAPTCHA
- **70+:** Decline или manual review

> **Полный код risk scoring + integration:** `references/07-security-compliance.md` (Section: Fraud Detection)

### Transaction Logging (audit trail)

**What TO log:**
```javascript
logger.info('Payment attempt', {
  timestamp: new Date().toISOString(),
  booking_id: bookingId,
  amount: amount,
  currency: currency,
  provider: 'stripe',
  ip: req.ip,
  user_agent: req.headers['user-agent'],
  risk_score: riskScore,
});
```

**What NOT TO log (PCI DSS violation!):**
```javascript
// ❌ NEVER log:
// - Full card numbers
// - CVV/CVC codes
// - Full names (use first name + last initial)
// - Full addresses (use city + country only)
// - API secret keys
```

### ОАЭ VAT Compliance (5%)

**VAT calculation:**
```javascript
function calculateVAT(subtotal) {
  const VAT_RATE = 0.05; // 5% в ОАЭ
  const vat = Math.round(subtotal * VAT_RATE * 100) / 100; // Round to 2 decimals
  const total = subtotal + vat;

  return {
    subtotal: subtotal.toFixed(2),
    vat: vat.toFixed(2),
    total: total.toFixed(2),
  };
}

// Usage:
const pricing = calculateVAT(250); // 250 AED tour
console.log(pricing);
// { subtotal: '250.00', vat: '12.50', total: '262.50' }
```

**Invoice requirements (ОАЭ FTA):**
- VAT Registration Number (TRN)
- Invoice date
- Sequential invoice number
- Seller details (name, address, TRN)
- Customer details
- Item description
- Subtotal, VAT amount (5%), Total

---

## 9. Troubleshooting & Production Checklist

### Common Errors

**Error: "No such payment_intent"**
```javascript
// Причина: Invalid payment intent ID или используется test key с live ID
// Решение:
// 1. Проверь что используешь правильный key (test vs live)
// 2. Проверь что payment intent был создан successfully
// 3. Log payment intent ID сразу после создания
```

**Error: "Your card was declined"**
```javascript
// Причины:
// - Insufficient funds
// - Card expired
// - Incorrect CVV
// - Card blocked by bank
// - Stripe Radar blocked (fraud)

// Решение:
try {
  const paymentIntent = await stripe.paymentIntents.create({...});
} catch (err) {
  if (err.code === 'card_declined') {
    // Suggest alternative payment method
    // Or ask customer to contact bank
    res.json({
      error: 'Card declined',
      decline_code: err.decline_code,
      suggestion: 'Please try another card or contact your bank',
    });
  }
}
```

**Error: "Webhook signature verification failed"**
```javascript
// Причина: Incorrect webhook secret или modified payload
// Решение:
// 1. Проверь STRIPE_WEBHOOK_SECRET в .env
// 2. Используй express.raw() для webhook endpoint
// 3. Test с Stripe CLI: stripe listen --forward-to localhost:3000/webhook
```

**Error: "Amount must be at least $0.50"**
```javascript
// Stripe minimum: 50 cents (валюта зависит)
// AED minimum: 2 AED
// Решение: Добавь validation
if (amount < 200) { // 2 AED = 200 fils
  return res.status(400).json({error: 'Minimum amount is 2 AED'});
}
```

### Webhook Debugging

**1. Local testing с Stripe CLI:**
```bash
stripe listen --forward-to localhost:3000/webhook
```

**2. Log все webhook events:**
```javascript
app.post('/webhook', async (req, res) => {
  console.log('Webhook received:', {
    type: event.type,
    id: event.id,
    created: new Date(event.created * 1000),
  });

  // Process event...

  res.json({received: true});
});
```

**3. Check webhook dashboard:**
- Stripe Dashboard → Developers → Webhooks
- View attempts, responses, retries

### Production Deployment Checklist

**Pre-launch:**
- [ ] Switch to production API keys (sk_live_, pk_live_)
- [ ] Update webhook URLs (production domain)
- [ ] Register webhooks with provider
- [ ] Test end-to-end with real card (small amount)
- [ ] Verify refund works
- [ ] Test failure scenarios
- [ ] Enable HTTPS (TLS 1.2+)
- [ ] Set up error monitoring (Sentry, LogRocket)
- [ ] Configure rate limiting
- [ ] Database backups enabled (daily)
- [ ] Logging configured (no sensitive data)

**Security:**
- [ ] No API keys in code
- [ ] .env not in git
- [ ] Webhook signature verification enabled
- [ ] CORS configured correctly
- [ ] SQL injection protection (parameterized queries)
- [ ] XSS protection (sanitize inputs)
- [ ] Rate limiting on payment endpoints
- [ ] Fraud detection enabled

**Monitoring:**
- [ ] Failed payment alerts
- [ ] Webhook failure alerts
- [ ] High decline rate alerts (>10%)
- [ ] Unusual transaction amounts
- [ ] System uptime monitoring

**Documentation:**
- [ ] Payment flow diagram
- [ ] Refund SOP
- [ ] Customer support scripts
- [ ] Troubleshooting guide
- [ ] Disaster recovery plan

### Performance Optimization

**1. Cache exchange rates:**
```javascript
let exchangeRatesCache = {
  rates: null,
  lastUpdated: null,
};

async function getExchangeRates() {
  const now = Date.now();
  const ONE_HOUR = 60 * 60 * 1000;

  // Return cached if fresh
  if (exchangeRatesCache.rates && (now - exchangeRatesCache.lastUpdated < ONE_HOUR)) {
    return exchangeRatesCache.rates;
  }

  // Fetch fresh rates
  const rates = await fetchExchangeRatesFromAPI();
  exchangeRatesCache = {rates, lastUpdated: now};

  return rates;
}
```

**2. Database indexing:**
```sql
CREATE INDEX idx_bookings_booking_id ON bookings(booking_id);
CREATE INDEX idx_bookings_customer_email ON bookings(customer_email);
CREATE INDEX idx_transactions_booking_id ON transactions(booking_id);
CREATE INDEX idx_transactions_status ON transactions(status);
```

**3. Webhook response time:**
```javascript
// Return 200 ASAP, process async
app.post('/webhook', async (req, res) => {
  const event = stripe.webhooks.constructEvent(req.body, sig, secret);

  // Respond immediately
  res.json({received: true});

  // Process async
  processWebhookAsync(event).catch(err => {
    logger.error('Webhook processing failed:', err);
  });
});
```

---

## Summary & Next Steps

### Что вы теперь умеете:

✅ **Интегрировать платёжные системы:**
- Stripe (international standard)
- Telr (UAE local)
- USDT/Bitcoin (cryptocurrency)
- PayPal (optional)

✅ **Реализовывать бизнес-сценарии:**
- Deposit + balance payments
- Group split payments
- Refunds с cancellation policy
- WhatsApp payment links
- Multi-currency pricing

✅ **Обеспечивать security:**
- PCI DSS compliance
- Webhook signature verification
- Fraud detection
- Rate limiting
- Secure credential storage

✅ **Production-ready deployment:**
- Error handling
- Monitoring & alerts
- Performance optimization
- Troubleshooting

### Recommended Learning Path:

**Week 1:** Quick Start + Stripe integration
**Week 2:** Business scenarios (deposits, refunds)
**Week 3:** Security & fraud prevention
**Week 4:** Additional providers (Telr, USDT)
**Week 5:** Production deployment

### Resources:

- `references/01-quick-start-guide.md` - Start here!
- `references/02-stripe-complete-guide.md` - Deep dive
- `assets/examples/` - 15 working examples
- `scripts/` - 15 automation tools
- `experience/_index.md` - Critical lessons

### Support:

- **Common issues:** `references/09-troubleshooting.md`
- **Questions:** `references/faq.md`
- **Security concerns:** `references/07-security-compliance.md`

---

**Время до production:** 30 минут (Quick Start) → 1 день (full setup)

**ROI:** Экономия 10-20 часов/неделю на manual payment processing

🚀 **Готово к использованию!**
