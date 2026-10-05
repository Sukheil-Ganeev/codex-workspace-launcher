# Payment Automation Scripts

Production-ready CLI tools для автоматизации payment operations.

## 📋 Список скриптов

### 1. payment-status-checker.js (~290 lines)
**Проверка статуса транзакций**
```bash
node payment-status-checker.js --transaction-id pi_123456
node payment-status-checker.js --booking-id BOOK-789
node payment-status-checker.js --email customer@example.com
node payment-status-checker.js --bulk transactions.csv --export results.csv
```

### 2. invoice-generator.js (~100 lines)
**Генерация PDF инвойсов**
```bash
node invoice-generator.js --amount 50000 --currency AED --customer "John Doe"
node invoice-generator.js --template custom.html --output invoice.pdf
```

### 3. analytics-dashboard.js (~450 lines)
**Real-time payment analytics dashboard**
```bash
node analytics-dashboard.js
node analytics-dashboard.js --port 4000
# Open browser: http://localhost:4000
```

### 4. reconciliation-tool.js (~437 lines)
**Сверка DB vs Gateway**
```bash
node reconciliation-tool.js --date 2025-02-01
node reconciliation-tool.js --range 2025-02-01:2025-02-28
node reconciliation-tool.js --auto-fix --export report.csv
```

### 5. webhook-tester.js (~150 lines)
**Тестирование webhooks локально**
```bash
node webhook-tester.js --url http://localhost:3000/webhook
node webhook-tester.js --url http://localhost:3000/webhook --batch 10
```

### 6. refund-processor.js (~60 lines)
**Batch refund processing**
```bash
node refund-processor.js --transaction-id pi_123 --amount 5000
node refund-processor.js --batch refunds.csv --auto-approve
```

### 7. fraud-detection-monitor.js (~100 lines)
**Real-time fraud monitoring**
```bash
node fraud-detection-monitor.js --threshold 75 --alert email
node fraud-detection-monitor.js --threshold 90 --auto-block
```

### 8. payment-link-bulk-generator.js (~80 lines)
**Mass generation payment links**
```bash
node payment-link-bulk-generator.js --input customers.csv --output links.csv
```

### 9. currency-rate-updater.js (~40 lines)
**Auto-update exchange rates**
```bash
node currency-rate-updater.js
# Run daily via cron: 0 0 * * * node currency-rate-updater.js
```

### 10. transaction-logger.js (~30 lines)
**Structured logging**
```bash
node transaction-logger.js info "Payment processed"
node transaction-logger.js error "Payment failed" '{"tx_id": "pi_123"}'
```

### 11. health-check.js (~50 lines)
**System health monitoring**
```bash
node health-check.js
# Returns exit code 0 if healthy, 1 if unhealthy
```

### 12. backup-transactions.js (~30 lines)
**Automated backups**
```bash
node backup-transactions.js
# Creates backup-YYYY-MM-DD.csv
```

### 13. export-accounting.js (~50 lines)
**Export для бухгалтерии**
```bash
node export-accounting.js --month 2025-02 --format csv
node export-accounting.js --format json
```

### 14. send-payment-reminders.js (~50 lines)
**Email reminders для pending payments**
```bash
node send-payment-reminders.js
# Sends reminders for payments 24-72h old
```

### 15. validate-config.js (~30 lines)
**Environment validation**
```bash
node validate-config.js
# Checks all required env vars present
```

## 🚀 Установка

```bash
cd scripts/
npm install
```

## 📦 Dependencies

```json
{
  "dependencies": {
    "stripe": "^14.0.0",
    "chalk": "^4.1.2",
    "commander": "^11.0.0",
    "dotenv": "^16.0.3",
    "csv-parse": "^5.5.0",
    "csv-stringify": "^6.4.0",
    "axios": "^1.6.0",
    "nodemailer": "^6.9.0",
    "@supabase/supabase-js": "^2.38.0",
    "pg": "^8.11.0"
  }
}
```

## 🔧 Configuration

Create `.env` file:

```env
# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Database
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_KEY=...

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASS=yourpassword
ALERT_EMAIL=alerts@example.com

# Slack (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

## 📝 Примеры использования

### Daily reconciliation
```bash
# Add to crontab
0 2 * * * cd /path/to/scripts && node reconciliation-tool.js --auto-fix --alert
```

### Fraud monitoring
```bash
# Run continuously
node fraud-detection-monitor.js --threshold 75 --alert both
```

### Bulk operations
```bash
# Generate 100 payment links
node payment-link-bulk-generator.js --input customers.csv --output links.csv

# Process refunds from CSV
node refund-processor.js --batch refunds.csv --auto-approve
```

## 🎯 Best Practices

1. **Logging**: Все скрипты используют transaction-logger для audit trail
2. **Error Handling**: Graceful failures с retry logic
3. **Rate Limiting**: Built-in delays для API calls
4. **Idempotency**: Safe для повторного запуска
5. **Monitoring**: Health checks и alerts

## 📚 Documentation

Detailed documentation for each script in comments. Run any script with `--help` for usage.

## 🐛 Troubleshooting

**Script fails with "Missing env var"**
→ Run `node validate-config.js` to check configuration

**Webhook signatures invalid**
→ Check STRIPE_WEBHOOK_SECRET in .env

**Database connection fails**
→ Verify DATABASE_URL format and credentials

**Email alerts not working**
→ Check SMTP settings and firewall rules
