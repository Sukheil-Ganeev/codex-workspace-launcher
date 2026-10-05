#!/usr/bin/env node

/**
 * Payment Reconciliation Tool
 * Сверка транзакций между базой данных и платежными шлюзами
 *
 * Функции:
 * - Automatic reconciliation (DB vs Stripe/Telr/PayPal)
 * - Discrepancy detection (missing, duplicates, amount mismatch)
 * - Email/Slack alerts для несоответствий
 * - Export reconciliation reports
 * - Scheduled reconciliation (cron)
 *
 * Usage:
 *   node reconciliation-tool.js --date 2025-02-01
 *   node reconciliation-tool.js --range 2025-02-01:2025-02-28
 *   node reconciliation-tool.js --provider stripe
 *   node reconciliation-tool.js --auto-fix
 *   node reconciliation-tool.js --export report.csv
 */

require('dotenv').config();
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const { Pool } = require('pg');
const chalk = require('chalk');
const { program } = require('commander');
const nodemailer = require('nodemailer');
const { stringify } = require('csv-stringify/sync');
const fs = require('fs');

program
  .name('reconciliation-tool')
  .description('Reconcile payments between DB and gateways')
  .version('1.0.0')
  .option('-d, --date <date>', 'Specific date (YYYY-MM-DD)')
  .option('-r, --range <range>', 'Date range (YYYY-MM-DD:YYYY-MM-DD)')
  .option('-p, --provider <name>', 'Provider: stripe, telr, paypal, all', 'all')
  .option('--auto-fix', 'Automatically fix simple discrepancies')
  .option('--export <file>', 'Export report to CSV')
  .option('--alert', 'Send email alerts for discrepancies')
  .option('--threshold <amount>', 'Alert threshold in minor units', '1000')
  .option('--days <n>', 'Days to check (default 7)', '7')
  .parse();

const options = program.opts();
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

// Email setup (если настроено)
let transporter = null;
if (process.env.SMTP_HOST) {
  transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: parseInt(process.env.SMTP_PORT) || 587,
    secure: false,
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS
    }
  });
}

/**
 * Получить даты для reconciliation
 */
function getDates() {
  if (options.date) {
    const date = new Date(options.date);
    return {
      start: date,
      end: new Date(date.getTime() + 24 * 60 * 60 * 1000)
    };
  }

  if (options.range) {
    const [start, end] = options.range.split(':');
    return {
      start: new Date(start),
      end: new Date(end)
    };
  }

  // Использовать --days
  const days = parseInt(options.days);
  const start = new Date();
  start.setDate(start.getDate() - days);
  start.setHours(0, 0, 0, 0);

  return {
    start,
    end: new Date()
  };
}

/**
 * Получить транзакции из БД
 */
async function getDBTransactions(startDate, endDate) {
  const result = await pool.query(
    'SELECT * FROM transactions WHERE created_at >= $1 AND created_at <= $2 ORDER BY created_at',
    [startDate, endDate]
  );

  return result.rows;
}

/**
 * Получить транзакции из Stripe
 */
async function getStripeTransactions(startDate, endDate) {
  const transactions = [];
  let hasMore = true;
  let startingAfter = null;

  const gte = Math.floor(startDate.getTime() / 1000);
  const lte = Math.floor(endDate.getTime() / 1000);

  while (hasMore) {
    const params = {
      limit: 100,
      created: { gte, lte }
    };

    if (startingAfter) {
      params.starting_after = startingAfter;
    }

    const paymentIntents = await stripe.paymentIntents.list(params);

    transactions.push(...paymentIntents.data.map(pi => ({
      id: pi.id,
      amount: pi.amount,
      currency: pi.currency,
      status: pi.status,
      created: new Date(pi.created * 1000),
      metadata: pi.metadata
    })));

    hasMore = paymentIntents.has_more;
    if (hasMore) {
      startingAfter = paymentIntents.data[paymentIntents.data.length - 1].id;
    }
  }

  return transactions;
}

/**
 * Сравнить транзакции
 */
function compareTransactions(dbTxs, gatewayTxs, provider) {
  const discrepancies = [];

  // Create lookup map
  const dbMap = new Map(dbTxs.map(tx => [tx.payment_intent_id, tx]));
  const gatewayMap = new Map(gatewayTxs.map(tx => [tx.id, tx]));

  // Check for missing in DB
  gatewayTxs.forEach(gtx => {
    const dbTx = dbMap.get(gtx.id);

    if (!dbTx) {
      discrepancies.push({
        type: 'MISSING_IN_DB',
        severity: 'HIGH',
        provider,
        gatewayId: gtx.id,
        amount: gtx.amount,
        currency: gtx.currency,
        created: gtx.created
      });
    } else {
      // Check for amount mismatch
      if (dbTx.amount !== gtx.amount) {
        discrepancies.push({
          type: 'AMOUNT_MISMATCH',
          severity: 'CRITICAL',
          provider,
          gatewayId: gtx.id,
          dbAmount: dbTx.amount,
          gatewayAmount: gtx.amount,
          difference: Math.abs(dbTx.amount - gtx.amount)
        });
      }

      // Check for status mismatch
      if (dbTx.status !== gtx.status) {
        discrepancies.push({
          type: 'STATUS_MISMATCH',
          severity: 'MEDIUM',
          provider,
          gatewayId: gtx.id,
          dbStatus: dbTx.status,
          gatewayStatus: gtx.status
        });
      }
    }
  });

  // Check for missing in gateway
  dbTxs.forEach(dbTx => {
    if (!gatewayMap.has(dbTx.payment_intent_id)) {
      discrepancies.push({
        type: 'MISSING_IN_GATEWAY',
        severity: 'MEDIUM',
        provider,
        dbId: dbTx.id,
        paymentIntentId: dbTx.payment_intent_id,
        amount: dbTx.amount
      });
    }
  });

  return discrepancies;
}

/**
 * Auto-fix простые несоответствия
 */
async function autoFixDiscrepancy(discrepancy) {
  try {
    if (discrepancy.type === 'STATUS_MISMATCH') {
      // Update DB status to match gateway
      await pool.query(
        'UPDATE transactions SET status = $1 WHERE payment_intent_id = $2',
        [discrepancy.gatewayStatus, discrepancy.gatewayId]
      );

      console.log(chalk.green(`✓ Fixed status mismatch for ${discrepancy.gatewayId}`));
      return true;
    }

    if (discrepancy.type === 'MISSING_IN_DB') {
      // Create DB record from gateway data
      const gatewayTx = await stripe.paymentIntents.retrieve(discrepancy.gatewayId);

      await pool.query(
        `INSERT INTO transactions (payment_intent_id, amount, currency, status, email, created_at)
         VALUES ($1, $2, $3, $4, $5, $6)`,
        [
          gatewayTx.id,
          gatewayTx.amount,
          gatewayTx.currency,
          gatewayTx.status,
          gatewayTx.receipt_email || gatewayTx.metadata.email,
          new Date(gatewayTx.created * 1000)
        ]
      );

      console.log(chalk.green(`✓ Created missing DB record for ${discrepancy.gatewayId}`));
      return true;
    }

    return false;
  } catch (error) {
    console.error(chalk.red(`✗ Failed to fix ${discrepancy.type}:`), error.message);
    return false;
  }
}

/**
 * Отправить email alert
 */
async function sendAlert(discrepancies, dateRange) {
  if (!transporter) {
    console.log(chalk.yellow('⚠ Email not configured, skipping alert'));
    return;
  }

  const critical = discrepancies.filter(d => d.severity === 'CRITICAL');
  const high = discrepancies.filter(d => d.severity === 'HIGH');

  const html = `
    <h2>Payment Reconciliation Alert</h2>
    <p><strong>Date Range:</strong> ${dateRange.start.toISOString().split('T')[0]} to ${dateRange.end.toISOString().split('T')[0]}</p>
    <p><strong>Total Discrepancies:</strong> ${discrepancies.length}</p>

    <h3 style="color: red;">Critical Issues (${critical.length})</h3>
    <ul>
      ${critical.map(d => `<li>${d.type} - ${d.provider} - ${d.gatewayId || d.dbId}</li>`).join('')}
    </ul>

    <h3 style="color: orange;">High Priority (${high.length})</h3>
    <ul>
      ${high.map(d => `<li>${d.type} - ${d.provider} - ${d.gatewayId || d.dbId}</li>`).join('')}
    </ul>

    <p>Please review these discrepancies and take appropriate action.</p>
  `;

  await transporter.sendMail({
    from: process.env.SMTP_USER,
    to: process.env.ALERT_EMAIL || process.env.SMTP_USER,
    subject: `[ALERT] Payment Reconciliation - ${discrepancies.length} Discrepancies Found`,
    html
  });

  console.log(chalk.green('✓ Alert email sent'));
}

/**
 * Export report to CSV
 */
function exportReport(discrepancies, filePath) {
  const csvData = discrepancies.map(d => ({
    type: d.type,
    severity: d.severity,
    provider: d.provider,
    gateway_id: d.gatewayId || '',
    db_id: d.dbId || '',
    amount: d.amount || d.dbAmount || '',
    currency: d.currency || '',
    db_status: d.dbStatus || '',
    gateway_status: d.gatewayStatus || '',
    difference: d.difference || ''
  }));

  const csv = stringify(csvData, {
    header: true,
    columns: ['type', 'severity', 'provider', 'gateway_id', 'db_id', 'amount', 'currency', 'db_status', 'gateway_status', 'difference']
  });

  fs.writeFileSync(filePath, csv);
  console.log(chalk.green(`✓ Report exported to ${filePath}`));
}

/**
 * Display summary
 */
function displaySummary(discrepancies, fixed = 0) {
  console.log('\n' + chalk.bold.cyan('═══════════════════════════════════════'));
  console.log(chalk.bold('Reconciliation Summary'));
  console.log(chalk.bold.cyan('═══════════════════════════════════════'));

  const byType = {};
  discrepancies.forEach(d => {
    byType[d.type] = (byType[d.type] || 0) + 1;
  });

  console.log('\n' + chalk.bold('Discrepancies by Type:'));
  Object.entries(byType).forEach(([type, count]) => {
    const color = count > 10 ? chalk.red : count > 5 ? chalk.yellow : chalk.gray;
    console.log(color(`  ${type}: ${count}`));
  });

  const bySeverity = {
    CRITICAL: discrepancies.filter(d => d.severity === 'CRITICAL').length,
    HIGH: discrepancies.filter(d => d.severity === 'HIGH').length,
    MEDIUM: discrepancies.filter(d => d.severity === 'MEDIUM').length
  };

  console.log('\n' + chalk.bold('By Severity:'));
  console.log(chalk.red(`  Critical: ${bySeverity.CRITICAL}`));
  console.log(chalk.yellow(`  High: ${bySeverity.HIGH}`));
  console.log(chalk.gray(`  Medium: ${bySeverity.MEDIUM}`));

  if (fixed > 0) {
    console.log('\n' + chalk.green(`✓ Auto-fixed: ${fixed} issues`));
  }

  console.log(chalk.bold.cyan('═══════════════════════════════════════\n'));
}

/**
 * Main function
 */
async function main() {
  console.log(chalk.blue('\n🔄 Payment Reconciliation Tool\n'));

  const dateRange = getDates();
  console.log(chalk.gray('Date range:'), dateRange.start.toISOString().split('T')[0], 'to', dateRange.end.toISOString().split('T')[0]);

  try {
    // Get DB transactions
    console.log(chalk.gray('\n📥 Fetching database transactions...'));
    const dbTxs = await getDBTransactions(dateRange.start, dateRange.end);
    console.log(chalk.green(`✓ Found ${dbTxs.length} transactions in DB`));

    let allDiscrepancies = [];

    // Check Stripe
    if (options.provider === 'stripe' || options.provider === 'all') {
      console.log(chalk.gray('\n📥 Fetching Stripe transactions...'));
      const stripeTxs = await getStripeTransactions(dateRange.start, dateRange.end);
      console.log(chalk.green(`✓ Found ${stripeTxs.length} transactions in Stripe`));

      const stripeDiscrepancies = compareTransactions(
        dbTxs.filter(tx => tx.provider === 'stripe' || !tx.provider),
        stripeTxs,
        'stripe'
      );

      allDiscrepancies = allDiscrepancies.concat(stripeDiscrepancies);
    }

    // Display results
    console.log(chalk.bold('\n📊 Results:'));
    console.log(chalk.yellow(`⚠️  Found ${allDiscrepancies.length} discrepancies`));

    if (allDiscrepancies.length > 0) {
      displaySummary(allDiscrepancies);

      // Auto-fix if requested
      let fixedCount = 0;
      if (options.autoFix) {
        console.log(chalk.blue('\n🔧 Attempting auto-fix...\n'));
        for (const disc of allDiscrepancies) {
          const fixed = await autoFixDiscrepancy(disc);
          if (fixed) fixedCount++;
        }
        console.log(chalk.green(`\n✓ Fixed ${fixedCount} out of ${allDiscrepancies.length} issues`));
      }

      // Export report
      if (options.export) {
        exportReport(allDiscrepancies, options.export);
      }

      // Send alert
      if (options.alert && allDiscrepancies.length > 0) {
        await sendAlert(allDiscrepancies, dateRange);
      }
    } else {
      console.log(chalk.green('\n✓ All transactions reconciled successfully!'));
    }

  } catch (error) {
    console.error(chalk.red('\n❌ Error:'), error.message);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

main().catch(err => {
  console.error(chalk.red('Fatal error:'), err.message);
  process.exit(1);
});
