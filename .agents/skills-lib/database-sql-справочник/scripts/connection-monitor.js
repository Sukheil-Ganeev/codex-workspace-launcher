#!/usr/bin/env node

/**
 * Database Connection Pool Monitor
 * Real-time monitoring of connection pool status
 * Usage: node connection-monitor.js [--interval 5000] [--watch]
 */

const db = require('./db');
const logger = require('./logger');

class ConnectionMonitor {
  constructor() {
    this.interval = parseInt(process.argv.find(a => a.includes('--interval'))?.split('=')[1] || '5000');
    this.isWatch = process.argv.includes('--watch');
    this.metrics = [];
  }

  async init() {
    try {
      await db.connect();
      logger.success('Connected to database');
    } catch (err) {
      logger.error('Failed to connect', err.message);
      process.exit(1);
    }
  }

  async monitor() {
    if (this.isWatch) {
      await this.watchMode();
    } else {
      await this.singleSnapshot();
    }
  }

  async singleSnapshot() {
    logger.info('Connection Pool Status');
    logger.info('='.repeat(50));

    await this.printStats();

    await db.disconnect();
  }

  async watchMode() {
    logger.info(`Monitoring pool (updating every ${this.interval}ms)`);
    logger.info('Press Ctrl+C to exit');
    logger.info('='.repeat(50));

    const showHeader = () => {
      console.clear?.();
      console.log(`Connection Pool Monitor - ${new Date().toLocaleTimeString()}`);
      console.log('='.repeat(60));
    };

    const loop = async () => {
      showHeader();
      await this.printStats();
      this.printGraph();
      setTimeout(loop, this.interval);
    };

    try {
      await loop();
    } catch (err) {
      logger.error('Monitor error', err.message);
    }
  }

  async printStats() {
    try {
      const stats = db.getPoolStats();

      if (!stats) {
        logger.warn('Pool not connected');
        return;
      }

      console.log(`
  Total Connections:  ${stats.totalConnections}/${stats.maxConnections}
  Idle Connections:   ${stats.idleConnections}
  Active Connections: ${stats.totalConnections - stats.idleConnections}
  Waiting Requests:   ${stats.waitingRequests}

  Utilization:        ${((stats.totalConnections / stats.maxConnections) * 100).toFixed(1)}%
`);

      // Store metric for graph
      this.metrics.push({
        timestamp: Date.now(),
        total: stats.totalConnections,
        idle: stats.idleConnections,
        active: stats.totalConnections - stats.idleConnections,
        waiting: stats.waitingRequests,
      });

      // Keep last 60 metrics
      if (this.metrics.length > 60) {
        this.metrics.shift();
      }

      // Get active connections from pool
      await this.queryActiveConnections();
    } catch (err) {
      logger.error('Failed to get stats', err.message);
    }
  }

  async queryActiveConnections() {
    try {
      const query = `
        SELECT
          pid,
          usename,
          application_name,
          client_addr,
          state,
          query_start,
          state_change,
          EXTRACT(EPOCH FROM (NOW() - query_start))::INT as duration_seconds
        FROM pg_stat_activity
        WHERE datname = current_database()
        AND pid != pg_backend_pid()
        ORDER BY query_start DESC
        LIMIT 10
      `;

      const result = await db.query(query);

      if (result.rows.length > 0) {
        console.log(`\n  Active Connections (${result.rows.length}):`);
        console.log('  ' + '-'.repeat(56));

        result.rows.slice(0, 5).forEach(row => {
          const duration = row.duration_seconds ? `${row.duration_seconds}s` : 'N/A';
          const app = row.application_name || 'unknown';
          console.log(
            `  PID ${row.pid}: ${app} [${row.state}] (${duration})`
          );
        });

        if (result.rows.length > 5) {
          console.log(`  ... and ${result.rows.length - 5} more`);
        }
      }
    } catch (err) {
      logger.debug('Could not query active connections', err.message);
    }
  }

  printGraph() {
    if (this.metrics.length < 2) return;

    console.log('\n  Connection Trend (last 60 samples):');
    console.log('  ' + '-'.repeat(56));

    const maxTotal = Math.max(...this.metrics.map(m => m.total)) || 1;
    const normalized = this.metrics.map(m => ({
      ...m,
      bar: Math.round((m.active / maxTotal) * 40),
    }));

    // Show simple graph
    const recentMetrics = normalized.slice(-20);
    let graph = '  ';
    recentMetrics.forEach(m => {
      const char = m.bar === 0 ? '_' : '▄▅▆▇█'[Math.min(4, m.bar)];
      graph += char;
    });
    console.log(graph);

    // Show legend
    console.log(`\n  Legend: _ = idle, █ = full utilization`);
  }

  async getConnectionWaitTime() {
    try {
      const query = `
        SELECT
          COUNT(*) as waiting_connections,
          MAX(EXTRACT(EPOCH FROM (NOW() - query_start)))::INT as oldest_wait_seconds
        FROM pg_stat_activity
        WHERE state = 'active'
        AND datname = current_database()
      `;

      const result = await db.query(query);
      return result.rows[0];
    } catch (err) {
      return null;
    }
  }

  async killLongRunningQueries(maxDuration = 300) {
    logger.warn(`Killing queries running longer than ${maxDuration}s...`);

    try {
      const query = `
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = current_database()
        AND pid != pg_backend_pid()
        AND EXTRACT(EPOCH FROM (NOW() - query_start)) > $1
      `;

      const result = await db.query(query, [maxDuration]);
      logger.success(`Terminated ${result.rowCount} query(ies)`);
    } catch (err) {
      logger.error('Failed to kill queries', err.message);
    }
  }
}

async function main() {
  const monitor = new ConnectionMonitor();
  const action = process.argv[2] || 'monitor';

  try {
    await monitor.init();

    switch (action) {
      case 'monitor':
        await monitor.monitor();
        break;
      case 'kill-long':
        const duration = parseInt(process.argv[3]) || 300;
        await monitor.killLongRunningQueries(duration);
        break;
      default:
        logger.error(`Unknown action: ${action}`);
        logger.info('Usage: node connection-monitor.js [monitor|kill-long]');
    }
  } catch (err) {
    logger.error('Fatal error', err.message);
    process.exit(1);
  } finally {
    if (!monitor.isWatch) {
      await db.disconnect();
    }
  }
}

main();
