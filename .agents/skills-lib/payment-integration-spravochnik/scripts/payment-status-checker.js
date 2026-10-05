#!/usr/bin/env node

/**
 * Payment Status Checker
 * CLI tool to check transaction status across multiple payment providers
 *
 * Usage:
 *   node payment-status-checker.js --transaction-id=pi_123456
 *   node payment-status-checker.js --booking-id=BOOK-789
 *   node payment-status-checker.js --email=customer@example.com
 *   node payment-status-checker.js --bulk transactions.csv --export results.csv
 */

require('dotenv').config();
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const chalk = require('chalk');
const { program } = require('commander');
const fs = require('fs');
const { parse } = require('csv-parse/sync');
const { stringify } = require('csv-stringify/sync');

program
  .name('payment-status-checker')
  .description('Check payment transaction status across providers')
  .version('1.0.0')
  .option('-t, --transaction-id <id>', 'Stripe PaymentIntent ID')
  .option('-b, --booking-id <id>', 'Booking ID')
  .option('-e, --email <email>', 'Customer email')
  .option('--bulk <file>', 'CSV file with transaction IDs')
  .option('--export <file>', 'Export results to CSV')
  .option('--provider <name>', 'Provider: stripe, telr, paypal', 'stripe')
  .option('--days <number>', 'Check last N days', '30')
  .parse();

const options = program.opts();

/**
 * Format status with color coding
 */
function formatStatus(status) {
  const statusMap = {
    'succeeded': chalk.green('✅ SUCCEEDED'),
    'requires_payment_method': chalk.yellow('⏳ AWAITING PAYMENT'),
    'requires_confirmation': chalk.yellow('⏳ NEEDS CONFIRMATION'),
    'requires_action': chalk.yellow('⚠️  REQUIRES ACTION'),
    'processing': chalk.blue('⏳ PROCESSING'),
    'canceled': chalk.gray('⚫ CANCELED'),
    'failed': chalk.red('❌ FAILED'),
    'requires_capture': chalk.yellow('💰 NEEDS CAPTURE')
  };

  return statusMap[status] || chalk.white(status.toUpperCase());
}

/**
 * Check Stripe payment
 */
async function checkStripePayment(transactionId) {
  try {
    const paymentIntent = await stripe.paymentIntents.retrieve(transactionId);

    return {
      provider: 'Stripe',
      id: paymentIntent.id,
      status: paymentIntent.status,
      amount: paymentIntent.amount / 100,
      currency: paymentIntent.currency.toUpperCase(),
      customer: paymentIntent.receipt_email || paymentIntent.metadata.email || 'N/A',
      created: new Date(paymentIntent.created * 1000),
      metadata: paymentIntent.metadata,
      error: null
    };
  } catch (error) {
    return {
      provider: 'Stripe',
      id: transactionId,
      error: error.message,
      status: 'error'
    };
  }
}

/**
 * Find payments by booking ID
 */
async function findByBookingId(bookingId) {
  try {
    const paymentIntents = await stripe.paymentIntents.list({
      limit: 100,
    });

    const matches = paymentIntents.data.filter(
      pi => pi.metadata.booking_id === bookingId || pi.metadata.bookingId === bookingId
    );

    return matches.map(pi => ({
      provider: 'Stripe',
      id: pi.id,
      status: pi.status,
      amount: pi.amount / 100,
      currency: pi.currency.toUpperCase(),
      customer: pi.receipt_email || 'N/A',
      created: new Date(pi.created * 1000),
      metadata: pi.metadata
    }));
  } catch (error) {
    return [{ error: error.message }];
  }
}

/**
 * Find payments by email
 */
async function findByEmail(email) {
  try {
    const paymentIntents = await stripe.paymentIntents.list({
      limit: 100,
    });

    const matches = paymentIntents.data.filter(
      pi => pi.receipt_email === email || pi.metadata.email === email
    );

    return matches.map(pi => ({
      provider: 'Stripe',
      id: pi.id,
      status: pi.status,
      amount: pi.amount / 100,
      currency: pi.currency.toUpperCase(),
      created: new Date(pi.created * 1000),
      metadata: pi.metadata
    }));
  } catch (error) {
    return [{ error: error.message }];
  }
}

/**
 * Display single payment result
 */
function displayPayment(payment) {
  if (payment.error) {
    console.log(chalk.red('\n❌ Error:'), payment.error);
    return;
  }

  console.log('\n' + chalk.bold.cyan('═══════════════════════════════════════'));
  console.log(chalk.bold('Payment ID:'), chalk.yellow(payment.id));
  console.log(chalk.bold('Provider:'), payment.provider);
  console.log(chalk.bold('Status:'), formatStatus(payment.status));
  console.log(chalk.bold('Amount:'), `${payment.amount} ${payment.currency}`);
  console.log(chalk.bold('Customer:'), payment.customer);
  console.log(chalk.bold('Created:'), payment.created.toLocaleString());

  if (payment.metadata && Object.keys(payment.metadata).length > 0) {
    console.log(chalk.bold('Metadata:'));
    Object.entries(payment.metadata).forEach(([key, value]) => {
      console.log(`  ${chalk.gray(key)}:`, value);
    });
  }

  console.log(chalk.bold.cyan('═══════════════════════════════════════'));
}

/**
 * Process bulk CSV file
 */
async function processBulk(filePath) {
  const fileContent = fs.readFileSync(filePath, 'utf-8');
  const records = parse(fileContent, {
    columns: true,
    skip_empty_lines: true
  });

  console.log(chalk.blue(`\n📋 Processing ${records.length} transactions...\n`));

  const results = [];

  for (const record of records) {
    const transactionId = record.transaction_id || record.id;
    console.log(chalk.gray(`Checking: ${transactionId}`));

    const result = await checkStripePayment(transactionId);
    results.push(result);

    // Progress indicator
    process.stdout.write(
      result.error ? chalk.red('✗ ') : chalk.green('✓ ')
    );
  }

  console.log('\n');

  return results;
}

/**
 * Export results to CSV
 */
function exportToCSV(results, filePath) {
  const csvData = results.map(r => ({
    transaction_id: r.id,
    provider: r.provider,
    status: r.status,
    amount: r.amount,
    currency: r.currency,
    customer: r.customer,
    created: r.created ? r.created.toISOString() : 'N/A',
    error: r.error || ''
  }));

  const csv = stringify(csvData, {
    header: true,
    columns: ['transaction_id', 'provider', 'status', 'amount', 'currency', 'customer', 'created', 'error']
  });

  fs.writeFileSync(filePath, csv);
  console.log(chalk.green(`\n📄 Results exported to: ${filePath}`));
}

/**
 * Main function
 */
async function main() {
  console.log(chalk.bold.blue('\n💳 Payment Status Checker\n'));

  try {
    let results = [];

    if (options.bulk) {
      // Bulk check from CSV
      results = await processBulk(options.bulk);

      if (options.export) {
        exportToCSV(results, options.export);
      } else {
        // Display summary
        const succeeded = results.filter(r => r.status === 'succeeded').length;
        const failed = results.filter(r => r.status === 'failed').length;
        const pending = results.filter(r => !['succeeded', 'failed'].includes(r.status)).length;

        console.log(chalk.bold('\n📊 Summary:'));
        console.log(chalk.green(`✓ Succeeded: ${succeeded}`));
        console.log(chalk.red(`✗ Failed: ${failed}`));
        console.log(chalk.yellow(`⏳ Pending: ${pending}`));
        console.log(chalk.blue(`Total: ${results.length}`));
      }
    } else if (options.transactionId) {
      // Single transaction check
      console.log(chalk.blue('🔍 Checking transaction:'), options.transactionId);
      const result = await checkStripePayment(options.transactionId);
      displayPayment(result);
    } else if (options.bookingId) {
      // Find by booking ID
      console.log(chalk.blue('🔍 Finding payments for booking:'), options.bookingId);
      results = await findByBookingId(options.bookingId);

      if (results.length === 0) {
        console.log(chalk.yellow('\n⚠️  No payments found for this booking ID'));
      } else {
        console.log(chalk.green(`\n✓ Found ${results.length} payment(s)`));
        results.forEach(displayPayment);
      }
    } else if (options.email) {
      // Find by email
      console.log(chalk.blue('🔍 Finding payments for email:'), options.email);
      results = await findByEmail(options.email);

      if (results.length === 0) {
        console.log(chalk.yellow('\n⚠️  No payments found for this email'));
      } else {
        console.log(chalk.green(`\n✓ Found ${results.length} payment(s)`));
        results.forEach(displayPayment);
      }
    } else {
      // No valid option provided
      program.help();
    }

  } catch (error) {
    console.error(chalk.red('\n❌ Fatal error:'), error.message);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = { checkStripePayment, findByBookingId, findByEmail };
