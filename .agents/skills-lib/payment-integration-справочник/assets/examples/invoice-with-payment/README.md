# Invoice with Payment Link

Generate professional invoices with embedded Stripe payment buttons.

## Features

- PDF invoice generation (Puppeteer)
- Embedded payment link (Stripe Payment Links)
- VAT 5% calculation
- Email-ready format
- WhatsApp-friendly (PDF + link)

## Setup

```bash
npm install express stripe puppeteer handlebars dotenv
node server.js
```

## API

**POST /generate-invoice**

```json
{
  "invoiceNumber": "INV-001",
  "customerName": "John Doe",
  "customerEmail": "john@example.com",
  "items": [
    {"name": "Desert Safari", "quantity": 2, "price": 25000}
  ],
  "subtotal": 50000,
  "vatRate": 0.05,
  "currency": "aed"
}
```

**Response:**
```json
{
  "invoiceNumber": "INV-001",
  "paymentLink": "https://buy.stripe.com/xxx",
  "pdfBase64": "JVBERi0xLjQK..."
}
```

## License
MIT
