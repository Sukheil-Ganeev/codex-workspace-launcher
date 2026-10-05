# Payment Integration - Critical Lessons Learned

**Последнее обновление:** 2026-02-04

## Топ-5 Критических уроков

### 1. ⚠️ НИКОГДА не храни API keys в коде
**Проблема:** Hardcoded credentials = security breach
**Решение:** Всегда используй environment variables
```javascript
// ❌ НЕПРАВИЛЬНО
const stripe = require('stripe')('sk_live_XXXXXX');

// ✅ ПРАВИЛЬНО
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
```

### 2. 🔐 Webhook signature verification обязательна
**Проблема:** Без verification любой может отправить fake webhook
**Решение:** Проверяй подпись на каждом webhook
```javascript
const sig = req.headers['stripe-signature'];
const event = stripe.webhooks.constructEvent(
  req.body, sig, process.env.STRIPE_WEBHOOK_SECRET
);
```

### 3. 💰 Idempotency для предотвращения duplicate charges
**Проблема:** Network retry может создать duplicate платежи
**Решение:** Используй idempotency keys
```javascript
stripe.paymentIntents.create({
  amount: 1000,
  currency: 'aed',
}, {
  idempotencyKey: `booking-${bookingId}`
});
```

### 4. 🌍 Multi-currency: храни amounts как integers в smallest currency unit
**Проблема:** Floating point errors в финансовых расчётах
**Решение:** 100 AED = 10000 fils (smallest unit)
```javascript
// ✅ ПРАВИЛЬНО
const amountInFils = 10000; // 100.00 AED
stripe.paymentIntents.create({ amount: amountInFils, currency: 'aed' });
```

### 5. 📊 Логируй ВСЁ (но без sensitive data)
**Проблема:** Debugging payment issues без логов невозможен
**Решение:** Structured logging, но exclude card data
```javascript
logger.info('Payment attempt', {
  transactionId: tx.id,
  amount: tx.amount,
  currency: tx.currency,
  // ❌ НЕ логируй: card numbers, CVV, full names
});
```

## Дополнительные уроки

### Testing: Всегда используй sandbox/test mode
- Stripe: `sk_test_...` keys
- Telr: Test merchant ID
- Never test on production!

### Refunds: Проверяй available balance
```javascript
// Stripe автоматически fails если insufficient funds
// Но лучше проверить заранее:
const balance = await stripe.balance.retrieve();
```

### Webhooks: Retry logic у провайдеров
- Stripe retries failed webhooks до 3 дней
- Убедись что endpoint stable и быстрый (<5s response)

### VAT: В ОАЭ 5% добавляется к цене
```javascript
const subtotal = 1000; // AED
const vat = Math.round(subtotal * 0.05);
const total = subtotal + vat; // 1050 AED
```

## 🚀 Parallel Agents для масштабных справочников

### 6. Dispatching Parallel Agents методология
**Проблема:** Создание больших справочников (300+ файлов) занимает 8-12 часов
**Решение:** Разбить на независимые группы, dispatching parallel agents
**Результат:** 382 файла за 46 минут (92% экономия)
**Детали:** `experience/improvements/EXP-001-parallel-agents-creation.md`

---

**Последнее обновление:** 2026-02-05
**Файлов в experience/:** 2 (1 improvement)

## Записи опыта

### Improvements
- [EXP-001: Parallel Agents Methodology](improvements/EXP-001-parallel-agents-creation.md) (2026-02-04)
  - **Impact:** 92% time savings
  - **Tags:** parallel-agents, methodology, productivity
