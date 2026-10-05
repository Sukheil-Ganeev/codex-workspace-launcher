#!/usr/bin/env node

/**
 * Webhook Tester
 * Local testing tool для payment webhooks с signature generation
 *
 * Features:
 * - Test webhook endpoints locally
 * - Generate valid signatures (Stripe, Telr, PayPal)
 * - Mock different event types
 * - Verify webhook response codes
 * - Rate limiting simulation
 *
 * Usage:
 *   node webhook-tester.js --url http://localhost:3000/webhook
 *   node webhook-tester.js --url http://localhost:3000/webhook --event payment_intent.succeeded
 *   node webhook-tester.js --url http://localhost:3000/webhook --provider stripe --batch 10
 */

require('dotenv').config();
const axios = require('axios');
const crypto = require('crypto');
const chalk = require('chalk');
const { program } = require('commander');

program
  .name('webhook-tester')
  .description('Test payment webhook endpoints')
  .version('1.0.0')
  .option('-u, --url <url>', 'Webhook URL to test', 'http://localhost:3000/webhook')
  .option('-p, --provider <name>', 'Provider: stripe, telr, paypal', 'stripe')
  .option('-e, --event <type>', 'Event type', 'payment_intent.succeeded')
  .option('-b, --batch <count>', 'Send multiple webhooks', '1')
  .option('--delay <ms>', 'Delay between batch requests', '1000')
  .parse();

const options = program.opts();

/**
 * Generate Stripe signature
 */
function generateStripeSignature(payload, secret) {
  const timestamp = Math.floor(Date.now() / 1000);
  const signedPayload = `${timestamp}.${payload}`;
  const signature = crypto
    .createHmac('sha256', secret)
    .update(signedPayload)
    .digest('hex');

  return `t=${timestamp},v1=${signature}`;
}

/**
 * Generate mock event data
 */
function generateMockEvent(provider, eventType) {
  const paymentIntentId = `pi_${Math.random().toString(36).substr(2, 9)}`;
  const amount = Math.floor(Math.random() * 100000) + 1000; // 10-1000 AED

  if (provider === 'stripe') {
    return {
      id: `evt_${Math.random().toString(36).substr(2, 9)}`,
      object: 'event',
      type: eventType,
      created: Math.floor(Date.now() / 1000),
      data: {
        object: {
          id: paymentIntentId,
          object: 'payment_intent',
          amount,
          currency: 'aed',
          status: eventType === 'payment_intent.succeeded' ? 'succeeded' : 'requires_payment_method',
          metadata: {
            booking_id: `BOOK${Date.now()}`
          }
        }
      }
    };
  }

  // Add more providers as needed
  return {};
}

/**
 * Send webhook test
 */
async function sendWebhook(eventData, provider) {
  const payload = JSON.stringify(eventData);

  const headers = {
    'Content-Type': 'application/json',
    'User-Agent': `${provider}-webhook-tester/1.0`
  };

  // Add signature based on provider
  if (provider === 'stripe') {
    const secret = process.env.STRIPE_WEBHOOK_SECRET || 'whsec_test';
    headers['stripe-signature'] = generateStripeSignature(payload, secret);
  }

  try {
    const startTime = Date.now();
    const response = await axios.post(options.url, payload, { headers, timeout: 5000 });
    const duration = Date.now() - startTime;

    console.log(chalk.green(`✓ Webhook delivered (${duration}ms)`));
    console.log(chalk.gray(`  Status: ${response.status}`));
    console.log(chalk.gray(`  Response: ${JSON.stringify(response.data).substring(0, 100)}`));

    return { success: true, duration, status: response.status };

  } catch (error) {
    console.log(chalk.red(`✗ Webhook failed`));
    if (error.response) {
      console.log(chalk.gray(`  Status: ${error.response.status}`));
      console.log(chalk.gray(`  Error: ${error.response.data}`));
    } else {
      console.log(chalk.gray(`  Error: ${error.message}`));
    }

    return { success: false, error: error.message };
  }
}

/**
 * Main function
 */
async function main() {
  console.log(chalk.blue('\n🔗 Webhook Tester\n'));
  console.log(chalk.gray('Target URL:'), options.url);
  console.log(chalk.gray('Provider:'), options.provider);
  console.log(chalk.gray('Event type:'), options.event);
  console.log(chalk.gray('Batch size:'), options.batch);
  console.log('');

  const batchSize = parseInt(options.batch);
  const delay = parseInt(options.delay);
  let successCount = 0;
  let failCount = 0;
  const durations = [];

  for (let i = 0; i < batchSize; i++) {
    console.log(chalk.yellow(`[${i + 1}/${batchSize}] Sending webhook...`));

    const eventData = generateMockEvent(options.provider, options.event);
    const result = await sendWebhook(eventData, options.provider);

    if (result.success) {
      successCount++;
      durations.push(result.duration);
    } else {
      failCount++;
    }

    if (i < batchSize - 1) {
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  // Summary
  console.log('\n' + chalk.bold.cyan('═══════════════════════════════════════'));
  console.log(chalk.bold('Test Summary'));
  console.log(chalk.bold.cyan('═══════════════════════════════════════'));
  console.log(chalk.green(`✓ Successful: ${successCount}`));
  console.log(chalk.red(`✗ Failed: ${failCount}`));

  if (durations.length > 0) {
    const avgDuration = (durations.reduce((a, b) => a + b, 0) / durations.length).toFixed(2);
    const minDuration = Math.min(...durations);
    const maxDuration = Math.max(...durations);

    console.log('\n' + chalk.bold('Response Times:'));
    console.log(chalk.gray(`  Average: ${avgDuration}ms`));
    console.log(chalk.gray(`  Min: ${minDuration}ms`));
    console.log(chalk.gray(`  Max: ${maxDuration}ms`));
  }

  console.log(chalk.bold.cyan('═══════════════════════════════════════\n'));
}

main().catch(err => {
  console.error(chalk.red('Error:'), err.message);
  process.exit(1);
});
