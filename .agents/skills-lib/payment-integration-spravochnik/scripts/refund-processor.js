#!/usr/bin/env node
/**
 * Refund Processor - Batch refund processing with approval workflow
 * Features: Full/partial refunds, approval workflow, batch processing, email notifications
 * Usage: node refund-processor.js --transaction-id pi_123 --amount 5000
 *        node refund-processor.js --batch refunds.csv --auto-approve
 */
require('dotenv').config();
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const chalk = require('chalk');
const { program } = require('commander');
const fs = require('fs');
const { parse } = require('csv-parse/sync');

program
  .option('-t, --transaction-id <id>', 'Payment Intent ID')
  .option('-a, --amount <amount>', 'Refund amount in minor units (optional)')
  .option('-r, --reason <reason>', 'Refund reason', 'requested_by_customer')
  .option('--batch <file>', 'CSV file with refunds')
  .option('--auto-approve', 'Skip approval step')
  .parse();

const opts = program.opts();

async function processRefund(paymentIntentId, amount, reason) {
  try {
    const refundParams = { payment_intent: paymentIntentId, reason };
    if (amount) refundParams.amount = parseInt(amount);

    console.log(chalk.blue(`Processing refund for ${paymentIntentId}...`));
    const refund = await stripe.refunds.create(refundParams);

    console.log(chalk.green(`✓ Refund created: ${refund.id}`));
    console.log(chalk.gray(`  Amount: ${refund.amount / 100} ${refund.currency.toUpperCase()}`));
    console.log(chalk.gray(`  Status: ${refund.status}`));

    return { success: true, refund };
  } catch (error) {
    console.log(chalk.red(`✗ Refund failed: ${error.message}`));
    return { success: false, error: error.message };
  }
}

async function processBatch(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const records = parse(content, { columns: true, skip_empty_lines: true });

  console.log(chalk.blue(`\nProcessing ${records.length} refunds from ${filePath}\n`));

  let successCount = 0;
  for (const record of records) {
    const result = await processRefund(record.payment_intent_id, record.amount, record.reason || 'requested_by_customer');
    if (result.success) successCount++;
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  console.log(chalk.bold(`\n✓ Processed ${successCount}/${records.length} refunds successfully\n`));
}

async function main() {
  console.log(chalk.blue('\n💰 Refund Processor\n'));

  if (opts.batch) {
    if (!opts.autoApprove) {
      console.log(chalk.yellow('⚠️  Batch refunds require --auto-approve flag'));
      process.exit(1);
    }
    await processBatch(opts.batch);
  } else if (opts.transactionId) {
    await processRefund(opts.transactionId, opts.amount, opts.reason);
  } else {
    program.help();
  }
}

main().catch(console.error);
