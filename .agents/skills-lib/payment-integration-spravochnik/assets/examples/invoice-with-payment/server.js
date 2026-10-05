#!/usr/bin/env node

/**
 * Invoice with Embedded Payment Button
 *
 * Generate professional invoices with Stripe payment links
 * Perfect for sending quotes/invoices via email/WhatsApp
 */

require('dotenv').config();
const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const puppeteer = require('puppeteer');
const handlebars = require('handlebars');
const fs = require('fs').promises;
const path = require('path');

const app = express();
app.use(express.json());

/**
 * Generate invoice PDF with payment link
 */
app.post('/generate-invoice', async (req, res) => {
  try {
    const {
      invoiceNumber,
      customerName,
      customerEmail,
      items,
      subtotal,
      vatRate,
      currency,
    } = req.body;

    const vat = Math.round(subtotal * vatRate);
    const total = subtotal + vat;

    // Create Stripe Payment Link
    const paymentLink = await stripe.paymentLinks.create({
      line_items: items.map(item => ({
        price_data: {
          currency,
          product_data: { name: item.name },
          unit_amount: item.price,
        },
        quantity: item.quantity,
      })),
      metadata: {
        invoice_number: invoiceNumber,
        customer_email: customerEmail,
      },
    });

    // Load HTML template
    const templatePath = path.join(__dirname, 'invoice-template.html');
    const templateHtml = await fs.readFile(templatePath, 'utf-8');
    const template = handlebars.compile(templateHtml);

    // Render invoice
    const html = template({
      invoiceNumber,
      date: new Date().toLocaleDateString(),
      customerName,
      customerEmail,
      items,
      subtotal: (subtotal / 100).toFixed(2),
      vat: (vat / 100).toFixed(2),
      total: (total / 100).toFixed(2),
      currency: currency.toUpperCase(),
      paymentLink: paymentLink.url,
    });

    // Generate PDF
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    await page.setContent(html);
    const pdf = await page.pdf({ format: 'A4', printBackground: true });
    await browser.close();

    res.json({
      invoiceNumber,
      paymentLink: paymentLink.url,
      pdfBase64: pdf.toString('base64'),
    });

  } catch (error) {
    console.error('Invoice generation failed:', error);
    res.status(500).json({ error: error.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`📄 Invoice server on port ${PORT}`));
