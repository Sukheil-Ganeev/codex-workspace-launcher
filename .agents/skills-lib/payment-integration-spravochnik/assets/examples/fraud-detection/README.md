# Fraud Detection System

Real-time fraud detection and risk scoring for payment processing.

## Features

- **IP Geolocation**: Checks IP country and proxy/VPN detection
- **Velocity Limits**: Prevents too many transactions from same card/IP/email
- **Risk Scoring**: 0-100 score with configurable thresholds
- **Blacklist Management**: Block suspicious IPs and emails
- **Pattern Detection**: Identifies suspicious transaction patterns
- **3D Secure**: Automatically requires 3DS for high-risk transactions
- **Manual Review Queue**: High-risk payments held for review

## Risk Scoring Logic

### Score Components:
- IP Blacklisted: +50 points
- Email Blacklisted: +50 points
- Velocity Limit Exceeded: +30 points
- High-Risk Country: +20 points
- Country Mismatch: +20 points
- Disposable Email: +15 points
- VPN/Proxy: +10 points
- Round Amount: +5 points

### Actions Based on Score:
- **0-19**: Allow (no restrictions)
- **20-49**: Allow with monitoring
- **50-74**: Require 3D Secure
- **75-89**: Manual review required
- **90-100**: Block transaction

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Create database tables:
```bash
psql -U your_user -d your_database -f database-schema.sql
```

4. Start server:
```bash
npm start
```

## API Endpoints

### Create Payment (with fraud check)
```bash
POST /create-payment
{
  "amount": 25000,
  "currency": "aed",
  "email": "customer@example.com",
  "cardToken": "tok_visa",
  "billingCountry": "AE"
}
```

### Add IP to Blacklist
```bash
POST /admin/blacklist-ip
{
  "ip": "123.45.67.89",
  "reason": "Multiple failed attempts"
}
```

### View High-Risk Transactions
```bash
GET /admin/high-risk-transactions
```

## Testing

### Low-Risk Transaction:
```bash
curl -X POST http://localhost:3000/create-payment \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 25000,
    "currency": "aed",
    "email": "john@gmail.com",
    "cardToken": "tok_visa",
    "billingCountry": "AE"
  }'
```

### High-Risk Transaction (disposable email):
```bash
curl -X POST http://localhost:3000/create-payment \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100000,
    "currency": "aed",
    "email": "test@tempmail.com",
    "cardToken": "tok_visa",
    "billingCountry": "US"
  }'
```

## Production Checklist

- [ ] Configure proper risk thresholds for your business
- [ ] Set up alerting for high-risk transactions
- [ ] Regularly review manual review queue
- [ ] Update high-risk country list
- [ ] Monitor false positive rate
- [ ] Integrate with your CRM/notification system
- [ ] Set up database backups
- [ ] Configure webhook retry logic

## Security Notes

- Never log full card numbers or CVV
- Use environment variables for all credentials
- Enable HTTPS in production
- Rotate webhook secrets regularly
- Monitor for unusual patterns

## License

MIT
