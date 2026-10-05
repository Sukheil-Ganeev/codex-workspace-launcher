# Regional Payment Specifics

## Overview

Payment acceptance varies dramatically across different regions due to sanctions, banking infrastructure, currency preferences, and local payment methods. This guide covers regional specifics for Russia, Kazakhstan, international markets, and multi-currency handling for UAE tourism business.

## Russia: Post-2022 Sanctions Landscape

### Visa/Mastercard Blockade

**Status as of 2026:**
- Visa and Mastercard stopped processing transactions from Russian banks (March 2022)
- Russian-issued Visa/Mastercard cards work ONLY domestically within Russia
- Cards cannot be used for international transactions
- Attempting to charge Russian Visa/Mastercard abroad results in immediate decline

**Technical Impact:**
```javascript
// Common error when attempting to charge Russian card
{
  "error": {
    "code": "card_declined",
    "decline_code": "generic_decline",
    "message": "Your card was declined"
  }
}
```

### Alternative Payment Methods for Russian Tourists

#### 1. Direct Bank Transfers (Most Common)

**Sberbank (Сбербанк):**
```
Method: Manual bank transfer
Currency: RUB (Russian Rubles)
Processing Time: 1-3 business days
Fee: ~1-2% (bank charges)

Receiver Details:
- Bank Name: [Your Russian partner bank]
- Account Number: 40817810099910004312
- Recipient: LLC "Your Company Name"
- Purpose: "Payment for tour services, invoice #12345"
```

**Tinkoff (Тинькофф):**
```
Method: P2P transfer (person-to-person)
Currency: RUB
Processing Time: Instant
Fee: 0% (for P2P transfers)

Instructions for Customer:
1. Open Tinkoff app
2. Go to "Payments" → "By phone number"
3. Enter: +7 XXX XXX XX XX
4. Amount: 150,000 RUB
5. Comment: "Tour booking #12345"
```

**Implementation Example:**
```python
# Payment instruction generator for Russian clients
def generate_russian_payment_instructions(booking_id, amount_aed):
    # Exchange rate with 3% markup
    exchange_rate = get_cbr_rate() * 1.03
    amount_rub = amount_aed * exchange_rate

    return {
        "methods": [
            {
                "name": "Sberbank Transfer",
                "currency": "RUB",
                "amount": round(amount_rub, 2),
                "account": "40817810099910004312",
                "recipient": "LLC Dubai Tours",
                "purpose": f"Tour payment #{booking_id}",
                "processing_time": "1-3 business days"
            },
            {
                "name": "Tinkoff P2P",
                "currency": "RUB",
                "amount": round(amount_rub, 2),
                "phone": "+7 XXX XXX XX XX",
                "comment": f"Booking #{booking_id}",
                "processing_time": "Instant"
            }
        ],
        "exchange_rate": exchange_rate,
        "rate_valid_until": datetime.now() + timedelta(hours=24)
    }
```

#### 2. Mir Card System

**Overview:**
- Russian domestic payment system (launched 2015)
- Works within Russia and select partner countries
- **Limited acceptance in UAE** - only specific merchants

**Acceptance in UAE:**
```
Status: Very Limited
Supported By:
- Some Mashreq Bank terminals
- Emirates NBD (select locations)
- Not widely supported in 2026

Recommendation: DO NOT rely on Mir as primary method
```

#### 3. Cryptocurrency (Emerging Option)

**USDT/USDC Acceptance:**
```javascript
// Crypto payment flow for Russian clients
const cryptoPayment = {
  acceptedTokens: ['USDT', 'USDC'],
  networks: ['TRC-20', 'ERC-20'],
  walletAddress: '0xYourCompanyWallet...',
  minimumAmount: 100, // USD equivalent
  confirmations: 3, // blocks

  process: [
    '1. Customer transfers USDT to company wallet',
    '2. Provide transaction hash',
    '3. Wait for 3 confirmations (~5-10 minutes)',
    '4. Admin verifies on blockchain explorer',
    '5. Booking confirmed manually'
  ]
}
```

**Security Considerations:**
- Use separate wallet for customer payments
- Verify transactions on blockchain explorer (Tronscan, Etherscan)
- Convert to fiat immediately to avoid volatility
- Document exchange rate at time of payment

### Russian Client Best Practices

```yaml
Booking Flow for Russian Tourists:
  1. Show price in both AED and RUB
  2. Lock exchange rate for 24 hours
  3. Offer multiple payment methods
  4. Provide clear transfer instructions in Russian
  5. Manual payment confirmation (screenshot verification)
  6. Issue receipt in RUB and AED
  7. Communicate via WhatsApp (preferred by Russians)
```

## Kazakhstan: Kaspi.kz Integration

### Market Dominance

**Kaspi.kz Stats:**
- Used by 95%+ of Kazakhstan population
- Handles 70% of all digital payments in KZ
- Instant transfers, 0% fees for individuals
- Mobile-first platform

### Integration Options

#### Option 1: Kaspi API (Official)

**Requirements:**
```
1. Register as Merchant on Kaspi
2. KYC verification (business documents)
3. API credentials (merchant_id, secret_key)
4. Webhook endpoint for payment notifications
5. Kazakhstan legal entity OR partnership
```

**API Flow:**
```javascript
// Generate Kaspi payment link
const axios = require('axios');

async function createKaspiPayment(amount, orderId) {
  const response = await axios.post(
    'https://kaspi.kz/api/v1/payments',
    {
      amount: amount,
      currency: 'KZT',
      order_id: orderId,
      description: 'Dubai Safari Tour',
      success_url: 'https://yoursite.com/success',
      failure_url: 'https://yoursite.com/failure'
    },
    {
      headers: {
        'Authorization': `Bearer ${process.env.KASPI_API_KEY}`,
        'Content-Type': 'application/json'
      }
    }
  );

  return response.data.payment_url; // Redirect customer here
}

// Webhook handler
app.post('/webhooks/kaspi', (req, res) => {
  const { order_id, status, transaction_id } = req.body;

  // Verify signature
  if (!verifyKaspiSignature(req.body, req.headers['x-kaspi-signature'])) {
    return res.status(400).send('Invalid signature');
  }

  if (status === 'SUCCESS') {
    // Update booking status
    updateBookingStatus(order_id, 'paid', transaction_id);
  }

  res.status(200).send('OK');
});
```

#### Option 2: Manual Kaspi P2P (Simple)

**Most Common for Small Business:**
```
Customer Flow:
1. Open Kaspi app
2. Go to "Переводы" (Transfers)
3. Enter phone: +7 7XX XXX XX XX
4. Amount: 200,000 KZT
5. Comment: "Dubai tour #12345"
6. Send screenshot to WhatsApp

Processing Time: Instant
Fee: 0% (free for individuals)
Verification: Manual (admin checks screenshot)
```

**Screenshot Verification Checklist:**
```python
def verify_kaspi_screenshot_checklist():
    return [
        "✓ Shows correct recipient phone number",
        "✓ Shows correct amount in KZT",
        "✓ Shows booking ID in comment",
        "✓ Shows 'Успешно' (Success) status",
        "✓ Shows date/time of transfer",
        "✓ Screenshot not edited (check metadata)"
    ]
```

### KZT Currency Handling

**Exchange Rate Management:**
```javascript
// KZT/AED conversion with markup
const getKZTPrice = async (amountAED) => {
  // Fetch live rate from National Bank of Kazakhstan
  const rate = await fetch('https://nationalbank.kz/rss/rates_all.xml');
  const kztPerUSD = parseRate(rate); // ~450 KZT per USD
  const usdPerAED = 0.27; // 1 AED ≈ 0.27 USD

  const kztPerAED = kztPerUSD * usdPerAED; // ~121 KZT per AED
  const markup = 1.03; // 3% exchange markup

  return Math.round(amountAED * kztPerAED * markup);
}

// Example usage
const tourPriceAED = 1500;
const tourPriceKZT = await getKZTPrice(tourPriceAED); // ~187,000 KZT
```

### Kazakhstan Client Best Practices

```yaml
Kaspi Payment Flow:
  Display: Show price in both AED and KZT
  Method: Provide Kaspi phone number prominently
  Language: Instructions in Russian (Kazakh optional)
  Verification: Request screenshot immediately
  Confirmation: Send WhatsApp confirmation in Russian
  Receipt: Issue in both currencies
  Support: Respond quickly (Kazakhs expect fast service)
```

## International Clients: SWIFT & Wire Transfers

### SWIFT Transfers

**Use Cases:**
- Large bookings (>10,000 AED)
- European/American corporate clients
- Yacht rentals with advance payment

**Company Bank Details (Example):**
```
Bank Name: Emirates NBD
SWIFT Code: EBILAEAD
Account Number: 1234567890123
Account Name: Your Company LLC
IBAN: AE070260001234567890123
Bank Address: Sheikh Zayed Road, Dubai, UAE

Currency: AED (preferred) or USD
Processing Time: 3-5 business days
Fees: Customer's bank charges apply (15-50 USD typical)
```

**Customer Instructions Template:**
```markdown
# International Wire Transfer Instructions

**Amount:** 5,000 AED (or 1,361 USD)
**Booking Reference:** #YT-2024-05678

### Bank Details:
- **Beneficiary:** Your Company LLC
- **Bank:** Emirates NBD
- **SWIFT:** EBILAEAD
- **Account:** 1234567890123
- **IBAN:** AE070260001234567890123

### Important Notes:
1. Include booking reference in transfer notes
2. Expect 3-5 business days processing
3. Bank fees apply (typically $15-50)
4. Send transfer confirmation to: payments@yourcompany.ae
5. We'll confirm booking once funds received

**Questions?** WhatsApp: +971 XX XXX XXXX
```

### Wire Transfer Tracking

```python
# Wire transfer tracking system
class WireTransferTracker:
    def __init__(self, booking_id):
        self.booking_id = booking_id
        self.status = 'pending'

    def check_bank_account(self):
        """
        Manual process:
        1. Login to Emirates NBD business banking
        2. Check recent transactions
        3. Match amount + booking reference
        4. Update status
        """
        pass

    def send_reminders(self):
        """
        Day 1: Thank you, transfer initiated
        Day 3: Reminder to send confirmation
        Day 5: Follow-up if not received
        Day 7: Escalate to customer support
        """
        days_elapsed = (datetime.now() - self.created_at).days

        if days_elapsed == 3 and self.status == 'pending':
            send_email(self.customer_email,
                      "Gentle reminder: Wire transfer confirmation")
        elif days_elapsed == 5:
            send_whatsapp(self.customer_phone,
                         "Have you sent the transfer? We haven't received it yet")
```

## Multi-Currency Display in UI

### Dynamic Currency Conversion

**Frontend Implementation:**
```javascript
// Currency selector component
const CurrencyDisplay = ({ priceAED }) => {
  const [selectedCurrency, setSelectedCurrency] = useState('AED');

  const rates = {
    'AED': 1,
    'USD': 0.272,
    'EUR': 0.252,
    'GBP': 0.216,
    'RUB': 24.5,
    'KZT': 121,
    'SAR': 1.02
  };

  const convertedPrice = (priceAED * rates[selectedCurrency]).toFixed(2);

  return (
    <div className="price-display">
      <select onChange={(e) => setSelectedCurrency(e.target.value)}>
        <option value="AED">🇦🇪 AED</option>
        <option value="USD">🇺🇸 USD</option>
        <option value="EUR">🇪🇺 EUR</option>
        <option value="RUB">🇷🇺 RUB</option>
        <option value="KZT">🇰🇿 KZT</option>
      </select>

      <div className="price">
        {selectedCurrency} {convertedPrice}
      </div>

      <div className="base-price">
        (Base: {priceAED} AED)
      </div>
    </div>
  );
};
```

### Geolocation-Based Currency Detection

```javascript
// Detect user's country and show appropriate currency
async function detectUserCurrency(ipAddress) {
  const geoData = await fetch(`https://ipapi.co/${ipAddress}/json/`);
  const { country_code } = await geoData.json();

  const currencyMap = {
    'RU': 'RUB',
    'KZ': 'KZT',
    'US': 'USD',
    'GB': 'GBP',
    'SA': 'SAR',
    'AE': 'AED'
  };

  return currencyMap[country_code] || 'USD';
}

// Usage on page load
app.get('/checkout', async (req, res) => {
  const userCurrency = await detectUserCurrency(req.ip);
  const tour = await getTour(req.params.id);

  res.render('checkout', {
    tour,
    defaultCurrency: userCurrency,
    priceAED: tour.price
  });
});
```

## Exchange Rate Markup Configuration

### Markup Strategies

**Standard Markup Model:**
```javascript
const markupConfig = {
  // Fixed percentage markup
  fixed: 0.03, // 3%

  // Tiered markup by amount
  tiered: [
    { min: 0, max: 1000, markup: 0.04 },      // 4% for small amounts
    { min: 1001, max: 5000, markup: 0.03 },   // 3% for medium
    { min: 5001, max: 999999, markup: 0.02 }  // 2% for large
  ],

  // Currency-specific markup (higher for volatile currencies)
  byCurrency: {
    'RUB': 0.05, // 5% for Ruble (volatility risk)
    'KZT': 0.03, // 3% for Tenge
    'USD': 0.02, // 2% for stable currencies
    'EUR': 0.02,
    'AED': 0.00  // No markup for base currency
  }
};

function calculatePriceWithMarkup(amountAED, targetCurrency) {
  const baseRate = getExchangeRate('AED', targetCurrency);
  const markup = markupConfig.byCurrency[targetCurrency] || 0.03;

  const rateWithMarkup = baseRate * (1 + markup);
  return amountAED * rateWithMarkup;
}
```

### Rate Update Strategy

```python
# Scheduled job to update exchange rates
from apscheduler.schedulers.background import BackgroundScheduler
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def update_exchange_rates():
    """
    Run every 6 hours
    Fetch from multiple sources for accuracy
    """
    sources = [
        'https://api.exchangerate-api.com/v4/latest/AED',
        'https://api.currencyfreaks.com/latest?apikey=YOUR_KEY',
        'https://openexchangerates.org/api/latest.json?app_id=YOUR_ID'
    ]

    rates = {}
    for source in sources:
        response = requests.get(source).json()
        rates[source] = response['rates']

    # Average rates from all sources
    averaged_rates = calculate_average(rates)

    # Store in Redis with 6-hour expiry
    redis_client.setex('exchange_rates', 21600, json.dumps(averaged_rates))

    logger.info(f"Exchange rates updated at {datetime.now()}")

# Schedule job
scheduler = BackgroundScheduler()
scheduler.add_job(update_exchange_rates, 'interval', hours=6)
scheduler.start()
```

## Regional Payment Summary

### Quick Reference Table

| Region | Preferred Method | Currency | Processing Time | Fee | Automation |
|--------|-----------------|----------|----------------|-----|-----------|
| **Russia** | Bank Transfer (Sberbank/Tinkoff) | RUB | 1-3 days / Instant | 1-2% / 0% | Manual |
| **Kazakhstan** | Kaspi.kz P2P | KZT | Instant | 0% | Manual |
| **USA/Europe** | Stripe Card | USD/EUR | Instant | 2.9% + 0.30 | Automatic |
| **UAE Locals** | Card / Bank Transfer | AED | Instant / 1 day | 2-3% / 0% | Both |
| **GCC Countries** | Telr Card | SAR/AED | Instant | 2.5% | Automatic |
| **China** | WeChat Pay / Alipay | CNY | Instant | 2% | API Available |

### Implementation Priority

```yaml
Phase 1 (Essential):
  - Stripe for card payments (international tourists)
  - Manual bank transfer instructions (Russia, Kazakhstan)
  - Multi-currency display on website

Phase 2 (Optimization):
  - Telr integration (GCC-specific)
  - Kaspi.kz official API
  - Automated exchange rate updates

Phase 3 (Advanced):
  - Cryptocurrency acceptance (USDT)
  - WeChat Pay / Alipay
  - Dynamic currency conversion at checkout
```

## Key Takeaways

1. **No one-size-fits-all solution** - Different regions require different methods
2. **Russian market requires manual processes** - Sanctions force bank transfer workarounds
3. **Kaspi.kz dominates Kazakhstan** - Integrate or provide P2P instructions
4. **Multi-currency is mandatory** - Show prices in customer's currency
5. **Exchange rate markup is business decision** - 2-5% is industry standard
6. **Compliance varies by region** - Research local KYC/AML requirements
7. **Manual verification needed** - For bank transfers, have clear process

## Next Steps

- Implement currency detection on website
- Create payment instruction templates in Russian/English
- Set up exchange rate update automation
- Test payment flows for each region
- Train staff on verification procedures

---

**Last Updated:** 2026-02-04
**Review Frequency:** Quarterly (sanctions/regulations change frequently)
