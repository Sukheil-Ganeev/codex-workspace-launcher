# Stripe Deposit + Balance Payment Example

Production-ready implementation of a two-stage payment flow: 30% deposit now, 70% balance later.

## Business Scenario

Customer books a Desert Safari tour for 1,000 AED:
- **Deposit:** 300 AED (paid immediately)
- **Balance:** 700 AED (paid 48 hours before tour)

## Features

- Dual payment flow (deposit + balance)
- Stripe Payment Intents API
- Webhook event handling
- Email confirmations
- PostgreSQL database
- Error handling
- Security best practices

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

**Required credentials:**
- Stripe API keys (from dashboard.stripe.com)
- Database URL (PostgreSQL)
- SMTP settings (for email)

### 3. Setup Database

```bash
npm run setup-db
```

Or manually:
```bash
psql YOUR_DATABASE_URL -f database-schema.sql
```

### 4. Configure Stripe Webhook

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://yourdomain.com/webhook`
3. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
4. Copy webhook signing secret to `.env`

### 5. Start Server

```bash
npm start
```

Development mode (with auto-reload):
```bash
npm run dev
```

## Testing

### Test Cards (Stripe Test Mode)

| Card Number | Scenario |
|-------------|----------|
| 4242 4242 4242 4242 | Success |
| 4000 0000 0000 9995 | Declined (insufficient funds) |
| 4000 0000 0000 0002 | Declined (card declined) |

- **Expiry:** Any future date (e.g., 12/25)
- **CVC:** Any 3 digits (e.g., 123)

### Test Workflow

1. Open http://localhost:3000
2. Fill in customer details
3. Use test card 4242 4242 4242 4242
4. Submit payment
5. Check email for confirmation
6. Use balance payment link to complete booking

### Webhook Testing (Local Development)

Install Stripe CLI:
```bash
stripe listen --forward-to localhost:3000/webhook
```

Copy webhook signing secret to `.env` as `STRIPE_WEBHOOK_SECRET`.

## API Endpoints

### POST /api/create-booking
Create a new booking and deposit payment intent.

**Request:**
```json
{
  "customerName": "John Doe",
  "email": "john@example.com",
  "phone": "+971501234567",
  "tourName": "Desert Safari Tour",
  "totalAmount": 1000,
  "depositPercent": 30
}
```

**Response:**
```json
{
  "bookingId": 1,
  "bookingReference": "BOOK-000001",
  "depositAmount": 300,
  "balanceAmount": 700,
  "clientSecret": "pi_xxx_secret_xxx"
}
```

### POST /api/create-balance-payment
Create balance payment intent for existing booking.

**Request:**
```json
{
  "bookingReference": "BOOK-000001"
}
```

**Response:**
```json
{
  "bookingReference": "BOOK-000001",
  "balanceAmount": 700,
  "clientSecret": "pi_xxx_secret_xxx"
}
```

### GET /api/booking/:reference
Get booking status.

**Response:**
```json
{
  "id": 1,
  "bookingReference": "BOOK-000001",
  "customerName": "John Doe",
  "status": "deposit_paid",
  "depositPaidAt": "2026-02-04T10:30:00Z",
  ...
}
```

## Database Schema

**bookings** table:
- Customer info (name, email, phone)
- Tour details (name, date)
- Payment amounts (total, deposit, balance)
- Payment tracking (Stripe payment intent IDs)
- Status (pending, deposit_paid, fully_paid, payment_failed)
- Timestamps (created, deposit paid, balance paid)

## Security Features

- Environment variables for sensitive data
- Webhook signature verification
- HTTPS required in production
- PCI DSS compliant (Stripe Elements)
- No card data stored in database
- Input validation
- SQL injection prevention (parameterized queries)

## Production Checklist

- [ ] Use live Stripe keys (not test keys)
- [ ] Configure production webhook URL
- [ ] Enable HTTPS (SSL certificate)
- [ ] Set strong DATABASE_URL password
- [ ] Configure production SMTP
- [ ] Set NODE_ENV=production
- [ ] Enable rate limiting
- [ ] Setup monitoring (Sentry, LogRocket)
- [ ] Backup database regularly
- [ ] Test webhook reliability

## Customization

### Change Deposit Percentage
Edit `depositPercent` parameter (default: 30%)

### Add VAT (5% UAE)
```javascript
const subtotal = 1000;
const vat = Math.round(subtotal * 0.05);
const totalAmount = subtotal + vat; // 1050 AED
```

### Send WhatsApp Confirmation
Use Twilio/MessageBird API in email functions.

## Troubleshooting

**Webhook not working?**
- Check webhook URL is publicly accessible
- Verify webhook secret in `.env`
- Check Stripe Dashboard → Webhooks → Recent deliveries

**Payment fails silently?**
- Check browser console for errors
- Verify Stripe publishable key in HTML
- Check server logs for API errors

**Email not sending?**
- Verify SMTP credentials
- Check spam folder
- Use app password (not regular password)

## License

MIT

## Support

For issues or questions, check the main справочник documentation.
