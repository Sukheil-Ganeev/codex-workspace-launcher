#!/usr/bin/env node
/**
 * Invoice Generator with PDF and Email
 * Usage: node invoice-generator.js --customer="John Doe" --email="john@example.com" --amount=25000 --currency=AED
 */
require('dotenv').config();
const PDFDocument = require('pdfkit');
const fs = require('fs');
const { program } = require('commander');
const chalk = require('chalk');
const QRCode = require('qrcode');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

program
  .option('-c, --customer <name>', 'Customer name')
  .option('-e, --email <email>', 'Customer email')
  .option('-a, --amount <number>', 'Amount in cents/fils')
  .option('--currency <code>', 'Currency code', 'AED')
  .option('-i, --items <json>', 'Items JSON array')
  .option('--vat <rate>', 'VAT rate', '0.05')
  .option('--output <path>', 'Output directory', './invoices')
  .option('--send-email', 'Send invoice via email')
  .parse();

const opts = program.opts();
const VAT_RATE = parseFloat(opts.vat);

async function generateInvoice() {
  const invoiceNum = `INV-${Date.now()}`;
  const amount = parseInt(opts.amount);
  const subtotal = Math.round(amount / (1 + VAT_RATE));
  const vat = amount - subtotal;

  console.log(chalk.blue('\n📄 Generating Invoice...'));
  console.log(`Invoice: ${invoiceNum}`);
  console.log(`Customer: ${opts.customer}`);
  console.log(`Amount: ${(amount/100).toFixed(2)} ${opts.currency}`);

  if (!fs.existsSync(opts.output)) fs.mkdirSync(opts.output, { recursive: true });

  const doc = new PDFDocument({ margin: 50 });
  const filePath = `${opts.output}/${invoiceNum}.pdf`;
  doc.pipe(fs.createWriteStream(filePath));

  // Header
  doc.fontSize(24).text('INVOICE', { align: 'right' });
  doc.fontSize(10).text(`#${invoiceNum}`, { align: 'right' });
  doc.text(`Date: ${new Date().toLocaleDateString()}`, { align: 'right' });
  doc.moveDown(2);

  // Company
  doc.fontSize(12).text('UAE Tourism LLC');
  doc.fontSize(10).text('Dubai, UAE');
  doc.text('TRN: 100123456789012');
  doc.moveDown();

  // Customer
  doc.text(`BILL TO: ${opts.customer}`);
  doc.text(opts.email);
  doc.moveDown(2);

  // Items
  doc.fontSize(11);
  doc.text('Item', 50, 280);
  doc.text('Amount', 450, 280);
  doc.moveTo(50, 295).lineTo(550, 295).stroke();

  let y = 310;
  doc.text('Tour Booking', 50, y);
  doc.text(`${(subtotal/100).toFixed(2)} ${opts.currency}`, 450, y);
  y += 20;
  doc.text(`VAT (${(VAT_RATE*100)}%)`, 50, y);
  doc.text(`${(vat/100).toFixed(2)} ${opts.currency}`, 450, y);
  y += 30;
  doc.fontSize(14).text('TOTAL', 50, y);
  doc.text(`${(amount/100).toFixed(2)} ${opts.currency}`, 450, y);

  // Payment link
  const paymentLink = await stripe.paymentLinks.create({
    line_items: [{ price_data: { currency: opts.currency.toLowerCase(), product_data: { name: 'Tour Payment' }, unit_amount: amount }, quantity: 1 }],
    metadata: { invoice_number: invoiceNum }
  });

  y += 50;
  doc.fontSize(10);
  const qr = await QRCode.toDataURL(paymentLink.url);
  doc.image(Buffer.from(qr.split(',')[1], 'base64'), 50, y, { width: 100 });
  doc.text('Scan to pay online', 55, y + 105);

  doc.end();

  console.log(chalk.green(`✓ Invoice generated: ${filePath}`));
  console.log(chalk.cyan(`Payment link: ${paymentLink.url}`));

  return { filePath, invoiceNum, paymentLink: paymentLink.url };
}

generateInvoice().catch(err => {
  console.error(chalk.red('Error:'), err.message);
  process.exit(1);
});
