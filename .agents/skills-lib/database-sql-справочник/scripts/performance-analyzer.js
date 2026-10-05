#!/usr/bin/env node

/**
 * Slow Query Analyzer
 * Identifies and analyzes slow queries using pg_stat_statements
 * Usage: node performance-analyzer.js [--limit 10] [--min-time 100]
 */

const db = require('./db');
const logger = require('./logger');

class PerformanceAnalyzer {
  constructor() {
    this.limit = parseInt(process.argv.find(a => a.includes('--limit'))?.split('=')[1] || '10');
    this.minTime = parseInt(process.argv.find(a => a.includes('--min-time'))?.split('=')[1] || '100');
  }

  async analyze() {
    try {
      await db.connect();

      logger.info('Database Performance Analysis');
      logger.info('='.repeat(60));

      // Check if pg_stat_statements is available
      const hasExtension = await this.checkExtension();

      if (!hasExtension) {
        logger.warn('pg_stat_statements extension not installed');
        logger.info('Install with: CREATE EXTENSION pg_stat_statements;');
        await this.analyzeWithoutStats();
      } else {
        await this.analyzeSlowQueries();
        await this.analyzeQueryPatterns();
      }

      await this.analyzeIndexUsage();
      await this.analyzeTableStats();
    } catch (err) {
      logger.error('Analysis error', err.message);
      process.exit(1);
    } finally {
      await db.disconnect();
    }
  }

  async checkExtension() {
    try {
      await db.query('SELECT * FROM pg_stat_statements LIMIT 1');
      return true;
    } catch (err) {
      return false;
    }
  }

  async analyzeSlowQueries() {
    logger.info(`\nTop ${this.limit} Slow Queries (min ${this.minTime}ms):`);
    logger.info('-'.repeat(60));

    const query = `
      SELECT
        query,
        calls,
        total_time,
        mean_time,
        max_time,
        min_time,
        stddev_time,
        ROUND(total_time::numeric, 2) as total_time_ms,
        ROUND(mean_time::numeric, 2) as mean_time_ms
      FROM pg_stat_statements
      WHERE mean_time >= $1
      ORDER BY mean_time DESC
      LIMIT $2
    `;

    try {
      const result = await db.query(query, [this.minTime, this.limit]);

      if (result.rows.length === 0) {
        logger.success('No slow queries found!');
        return;
      }

      result.rows.forEach((row, idx) => {
        const truncated = row.query.substring(0, 80).replace(/\s+/g, ' ');
        console.log(`\n${idx + 1}. ${truncated}...`);
        console.log(`   Calls: ${row.calls}`);
        console.log(`   Total: ${row.total_time_ms}ms | Mean: ${row.mean_time_ms}ms | Max: ${row.max_time}ms`);
        console.log(`   Std Dev: ${row.stddev_time ? row.stddev_time.toFixed(2) : 'N/A'}ms`);
      });
    } catch (err) {
      logger.error('Failed to analyze slow queries', err.message);
    }
  }

  async analyzeQueryPatterns() {
    logger.info(`\nQuery Pattern Statistics:`);
    logger.info('-'.repeat(60));

    const query = `
      SELECT
        COUNT(*) as total_queries,
        COUNT(DISTINCT userid) as distinct_users,
        SUM(calls) as total_calls,
        AVG(mean_time)::NUMERIC(10,2) as avg_time_ms,
        MAX(mean_time)::NUMERIC(10,2) as max_time_ms
      FROM pg_stat_statements
    `;

    try {
      const result = await db.query(query);
      const stats = result.rows[0];

      console.log(`  Total Queries Tracked: ${stats.total_queries}`);
      console.log(`  Distinct Users: ${stats.distinct_users}`);
      console.log(`  Total Calls: ${stats.total_calls}`);
      console.log(`  Average Execution Time: ${stats.avg_time_ms}ms`);
      console.log(`  Max Execution Time: ${stats.max_time_ms}ms`);
    } catch (err) {
      logger.error('Failed to analyze patterns', err.message);
    }
  }

  async analyzeIndexUsage() {
    logger.info(`\nIndex Usage Analysis:`);
    logger.info('-'.repeat(60));

    const query = `
      SELECT
        schemaname,
        tablename,
        indexname,
        idx_scan,
        idx_tup_read,
        idx_tup_fetch
      FROM pg_stat_user_indexes
      WHERE idx_scan = 0
      ORDER BY tablename
    `;

    try {
      const result = await db.query(query);

      if (result.rows.length === 0) {
        logger.success('All indexes are being used');
        return;
      }

      logger.warn(`Found ${result.rows.length} unused index(es):`);
      result.rows.forEach(row => {
        console.log(`  - ${row.tablename}.${row.indexname}`);
      });
    } catch (err) {
      logger.debug('Index analysis not available', err.message);
    }
  }

  async analyzeTableStats() {
    logger.info(`\nTable Statistics:`);
    logger.info('-'.repeat(60));

    const query = `
      SELECT
        schemaname,
        tablename,
        seq_scan,
        seq_tup_read,
        idx_scan,
        idx_tup_fetch,
        n_tup_ins,
        n_tup_upd,
        n_tup_del,
        ROUND(pg_total_relation_size(schemaname||'.'||tablename)::numeric / 1024 / 1024, 2) as size_mb
      FROM pg_stat_user_tables
      WHERE schemaname = 'public'
      ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
      LIMIT 10
    `;

    try {
      const result = await db.query(query);

      result.rows.forEach(row => {
        console.log(`\n  ${row.tablename} (${row.size_mb}MB)`);
        console.log(`    Sequential Scans: ${row.seq_scan} | Index Scans: ${row.idx_scan}`);
        console.log(`    Inserts: ${row.n_tup_ins} | Updates: ${row.n_tup_upd} | Deletes: ${row.n_tup_del}`);
      });
    } catch (err) {
      logger.error('Failed to analyze tables', err.message);
    }
  }

  async analyzeWithoutStats() {
    logger.info('\nAnalyzing with basic statistics...');

    const query = `
      SELECT
        schemaname,
        tablename,
        seq_scan,
        idx_scan,
        n_live_tup
      FROM pg_stat_user_tables
      ORDER BY seq_scan DESC
      LIMIT 10
    `;

    try {
      const result = await db.query(query);

      logger.info('Tables with most sequential scans:');
      result.rows.forEach((row, idx) => {
        console.log(`${idx + 1}. ${row.tablename}: ${row.seq_scan} seq scans`);
      });
    } catch (err) {
      logger.error('Failed to analyze', err.message);
    }
  }

  async reset() {
    logger.warn('Resetting pg_stat_statements...');

    const query = `SELECT pg_stat_statements_reset()`;

    try {
      await db.query(query);
      logger.success('Statistics reset');
    } catch (err) {
      logger.error('Failed to reset statistics', err.message);
    }
  }
}

async function main() {
  const analyzer = new PerformanceAnalyzer();
  const action = process.argv[2] || 'analyze';

  try {
    switch (action) {
      case 'analyze':
        await analyzer.analyze();
        break;
      case 'reset':
        await analyzer.reset();
        break;
      default:
        logger.error(`Unknown action: ${action}`);
        logger.info('Usage: node performance-analyzer.js [analyze|reset]');
    }
  } catch (err) {
    logger.error('Fatal error', err.message);
    process.exit(1);
  }
}

main();
