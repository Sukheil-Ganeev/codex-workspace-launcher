#!/usr/bin/env node

/**
 * Payment Analytics Dashboard Server
 * Real-time payment metrics visualization with Chart.js
 *
 * Features:
 * - Revenue trends (daily/monthly/yearly)
 * - Success rate tracking
 * - Provider comparison
 * - Top customers
 * - Real-time updates via WebSocket
 * - Export to CSV/JSON
 *
 * Usage:
 *   node analytics-dashboard.js
 *   node analytics-dashboard.js --port 4000
 *   node analytics-dashboard.js --db mysql://localhost/payments
 */

require('dotenv').config();
const express = require('express');
const { createClient } = require('@supabase/supabase-js');
const chalk = require('chalk');
const { program } = require('commander');
const http = require('http');
const { Server } = require('socket.io');

program
  .name('analytics-dashboard')
  .description('Payment analytics dashboard server')
  .version('1.0.0')
  .option('-p, --port <number>', 'Server port', '4000')
  .option('--db <url>', 'Database URL')
  .option('--refresh <seconds>', 'Auto-refresh interval', '30')
  .parse();

const options = program.opts();
const PORT = options.port;
const REFRESH_INTERVAL = parseInt(options.refresh) * 1000;

// Database setup
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
);

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.json());
app.use(express.static('public'));

/**
 * Получить статистику за период
 */
async function getRevenueStats(days = 30) {
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  const { data, error } = await supabase
    .from('transactions')
    .select('*')
    .eq('status', 'succeeded')
    .gte('created_at', startDate.toISOString());

  if (error) throw error;

  // Группировка по дням
  const dailyRevenue = {};
  data.forEach(tx => {
    const date = tx.created_at.split('T')[0];
    if (!dailyRevenue[date]) {
      dailyRevenue[date] = {
        date,
        amount: 0,
        count: 0,
        currency: tx.currency
      };
    }
    dailyRevenue[date].amount += tx.amount / 100;
    dailyRevenue[date].count += 1;
  });

  return Object.values(dailyRevenue).sort((a, b) =>
    new Date(a.date) - new Date(b.date)
  );
}

/**
 * Процент успешных платежей
 */
async function getSuccessRate(days = 30) {
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  const { data } = await supabase
    .from('transactions')
    .select('status')
    .gte('created_at', startDate.toISOString());

  if (!data || data.length === 0) {
    return { rate: 0, succeeded: 0, failed: 0, total: 0 };
  }

  const succeeded = data.filter(tx => tx.status === 'succeeded').length;
  const failed = data.filter(tx => tx.status === 'failed').length;
  const total = data.length;
  const rate = ((succeeded / total) * 100).toFixed(2);

  return { rate, succeeded, failed, total };
}

/**
 * Сравнение провайдеров
 */
async function getProviderComparison(days = 30) {
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  const { data } = await supabase
    .from('transactions')
    .select('provider, status, amount')
    .gte('created_at', startDate.toISOString());

  const providers = {};

  data.forEach(tx => {
    if (!providers[tx.provider]) {
      providers[tx.provider] = {
        name: tx.provider,
        total: 0,
        succeeded: 0,
        failed: 0,
        revenue: 0
      };
    }

    providers[tx.provider].total += 1;
    if (tx.status === 'succeeded') {
      providers[tx.provider].succeeded += 1;
      providers[tx.provider].revenue += tx.amount / 100;
    } else if (tx.status === 'failed') {
      providers[tx.provider].failed += 1;
    }
  });

  // Добавить процент успеха
  Object.values(providers).forEach(p => {
    p.successRate = p.total > 0
      ? ((p.succeeded / p.total) * 100).toFixed(2)
      : 0;
  });

  return Object.values(providers);
}

/**
 * Топ клиентов
 */
async function getTopCustomers(limit = 10, days = 30) {
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  const { data } = await supabase
    .from('transactions')
    .select('email, amount, status')
    .eq('status', 'succeeded')
    .gte('created_at', startDate.toISOString());

  const customers = {};

  data.forEach(tx => {
    const email = tx.email.toLowerCase();
    if (!customers[email]) {
      customers[email] = {
        email,
        totalSpent: 0,
        transactionCount: 0
      };
    }
    customers[email].totalSpent += tx.amount / 100;
    customers[email].transactionCount += 1;
  });

  return Object.values(customers)
    .sort((a, b) => b.totalSpent - a.totalSpent)
    .slice(0, limit);
}

/**
 * Средний чек
 */
async function getAverageTicket(days = 30) {
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  const { data } = await supabase
    .from('transactions')
    .select('amount')
    .eq('status', 'succeeded')
    .gte('created_at', startDate.toISOString());

  if (!data || data.length === 0) {
    return { average: 0, count: 0 };
  }

  const total = data.reduce((sum, tx) => sum + tx.amount, 0) / 100;
  const average = (total / data.length).toFixed(2);

  return { average, count: data.length, total };
}

/**
 * API Endpoints
 */

// Главная страница дашборда
app.get('/', (req, res) => {
  res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Payment Analytics Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; padding: 20px; }
    .container { max-width: 1400px; margin: 0 auto; }
    h1 { color: #2d3748; margin-bottom: 30px; font-size: 32px; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .stat-card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .stat-card h3 { color: #718096; font-size: 14px; font-weight: 500; margin-bottom: 10px; text-transform: uppercase; }
    .stat-card .value { font-size: 36px; font-weight: bold; color: #2d3748; }
    .stat-card .change { font-size: 14px; margin-top: 8px; }
    .change.positive { color: #48bb78; }
    .change.negative { color: #f56565; }
    .charts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .chart-card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .chart-card h3 { color: #2d3748; margin-bottom: 20px; font-size: 18px; }
    .table-card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; padding: 12px; border-bottom: 1px solid #e2e8f0; }
    th { color: #718096; font-weight: 600; font-size: 12px; text-transform: uppercase; }
    .badge { padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 500; }
    .badge.success { background: #c6f6d5; color: #22543d; }
    .badge.warning { background: #fef3c7; color: #78350f; }
    .live-indicator { display: inline-block; width: 8px; height: 8px; background: #48bb78; border-radius: 50%; margin-right: 8px; animation: pulse 2s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
  </style>
</head>
<body>
  <div class="container">
    <h1><span class="live-indicator"></span>Payment Analytics Dashboard</h1>

    <div class="stats-grid">
      <div class="stat-card">
        <h3>Total Revenue</h3>
        <div class="value" id="totalRevenue">Loading...</div>
        <div class="change positive" id="revenueChange">+0%</div>
      </div>
      <div class="stat-card">
        <h3>Success Rate</h3>
        <div class="value" id="successRate">Loading...</div>
        <div class="change" id="successChange">0 transactions</div>
      </div>
      <div class="stat-card">
        <h3>Average Ticket</h3>
        <div class="value" id="avgTicket">Loading...</div>
        <div class="change" id="ticketChange">0 orders</div>
      </div>
      <div class="stat-card">
        <h3>Total Transactions</h3>
        <div class="value" id="totalTxs">Loading...</div>
        <div class="change positive" id="txChange">+0 today</div>
      </div>
    </div>

    <div class="charts-grid">
      <div class="chart-card">
        <h3>Revenue Trend (30 Days)</h3>
        <canvas id="revenueChart"></canvas>
      </div>
      <div class="chart-card">
        <h3>Provider Comparison</h3>
        <canvas id="providerChart"></canvas>
      </div>
    </div>

    <div class="table-card">
      <h3>Top Customers</h3>
      <table id="customersTable">
        <thead>
          <tr>
            <th>Customer</th>
            <th>Total Spent</th>
            <th>Transactions</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <script>
    const socket = io();

    let revenueChart, providerChart;

    // Инициализация графиков
    function initCharts() {
      const revenueCtx = document.getElementById('revenueChart').getContext('2d');
      revenueChart = new Chart(revenueCtx, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Revenue (AED)', data: [], borderColor: '#4299e1', tension: 0.4, fill: true, backgroundColor: 'rgba(66, 153, 225, 0.1)' }] },
        options: { responsive: true, plugins: { legend: { display: false } } }
      });

      const providerCtx = document.getElementById('providerChart').getContext('2d');
      providerChart = new Chart(providerCtx, {
        type: 'bar',
        data: { labels: [], datasets: [{ label: 'Revenue (AED)', data: [], backgroundColor: ['#48bb78', '#4299e1', '#ed8936'] }] },
        options: { responsive: true, plugins: { legend: { display: false } } }
      });
    }

    // Обновление данных
    socket.on('analytics:update', (data) => {
      // Update stats
      document.getElementById('totalRevenue').textContent = data.revenue.total.toLocaleString() + ' AED';
      document.getElementById('successRate').textContent = data.successRate.rate + '%';
      document.getElementById('avgTicket').textContent = data.averageTicket.average + ' AED';
      document.getElementById('totalTxs').textContent = data.successRate.total.toLocaleString();

      // Update revenue chart
      revenueChart.data.labels = data.revenue.daily.map(d => d.date);
      revenueChart.data.datasets[0].data = data.revenue.daily.map(d => d.amount);
      revenueChart.update();

      // Update provider chart
      providerChart.data.labels = data.providers.map(p => p.name);
      providerChart.data.datasets[0].data = data.providers.map(p => p.revenue);
      providerChart.update();

      // Update customers table
      const tbody = document.querySelector('#customersTable tbody');
      tbody.innerHTML = data.topCustomers.map(c =>
        '<tr><td>' + c.email + '</td><td>' + c.totalSpent.toFixed(2) + ' AED</td><td>' + c.transactionCount + '</td><td><span class="badge success">Active</span></td></tr>'
      ).join('');
    });

    initCharts();
  </script>
</body>
</html>
  `);
});

// API endpoint для получения всех данных
app.get('/api/analytics', async (req, res) => {
  try {
    const days = parseInt(req.query.days) || 30;

    const [revenue, successRate, providers, topCustomers, avgTicket] = await Promise.all([
      getRevenueStats(days),
      getSuccessRate(days),
      getProviderComparison(days),
      getTopCustomers(10, days),
      getAverageTicket(days)
    ]);

    const totalRevenue = revenue.reduce((sum, day) => sum + day.amount, 0);

    res.json({
      revenue: {
        daily: revenue,
        total: totalRevenue
      },
      successRate,
      providers,
      topCustomers,
      averageTicket: avgTicket
    });

  } catch (error) {
    console.error('Analytics error:', error);
    res.status(500).json({ error: error.message });
  }
});

// WebSocket для real-time updates
io.on('connection', async (socket) => {
  console.log(chalk.green('✓ Client connected'));

  // Отправить начальные данные
  const sendUpdate = async () => {
    try {
      const [revenue, successRate, providers, topCustomers, avgTicket] = await Promise.all([
        getRevenueStats(30),
        getSuccessRate(30),
        getProviderComparison(30),
        getTopCustomers(10, 30),
        getAverageTicket(30)
      ]);

      const totalRevenue = revenue.reduce((sum, day) => sum + day.amount, 0);

      socket.emit('analytics:update', {
        revenue: {
          daily: revenue,
          total: totalRevenue
        },
        successRate,
        providers,
        topCustomers,
        averageTicket: avgTicket
      });
    } catch (error) {
      console.error('Update error:', error);
    }
  };

  // Отправить сразу
  await sendUpdate();

  // Периодические обновления
  const interval = setInterval(sendUpdate, REFRESH_INTERVAL);

  socket.on('disconnect', () => {
    clearInterval(interval);
    console.log(chalk.gray('Client disconnected'));
  });
});

/**
 * Запуск сервера
 */
async function main() {
  console.log(chalk.blue('\n📊 Payment Analytics Dashboard\n'));

  server.listen(PORT, () => {
    console.log(chalk.green('✓ Server running on http://localhost:' + PORT));
    console.log(chalk.gray('  Auto-refresh every ' + (REFRESH_INTERVAL / 1000) + ' seconds'));
    console.log(chalk.gray('  Press Ctrl+C to stop\n'));
  });
}

main().catch(err => {
  console.error(chalk.red('Fatal error:'), err.message);
  process.exit(1);
});
