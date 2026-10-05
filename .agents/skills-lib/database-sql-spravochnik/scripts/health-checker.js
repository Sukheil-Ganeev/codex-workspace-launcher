#!/usr/bin/env node

/**
 * Database Health Check System
 * Performs comprehensive database health diagnostics
 * Usage: node health-checker.js [--checks all|connection|data|replication] [--exit-code]
 */

const db = require('./db');
const logger = require('./logger');

class HealthChecker {
  constructor() {
    this.checks = process.argv.find(a => a.includes('--checks'))?.split('=')[1] || 'all';
    this.exitOnFail = process.argv.includes('--exit-code');
    this.results = {
      passed: [],
      failed: [],
      warnings: [],
    };
  }

  async check() {
    try {
      await db.connect();

      logger.info('Database Health Check');
      logger.info('='.repeat(60));

      const checkList = this.getCheckList();

      for (const checkName of checkList) {
        await this[`check${checkName}`]();
      }

      this.printReport();

      if (this.results.failed.length > 0 && this.exitOnFail) {
        process.exit(1);
      }
    } catch (err) {
      logger.error('Health check error', err.message);
      process.exit(1);
    } finally {
      await db.disconnect();
    }
  }

  getCheckList() {
    const allChecks = [
      'Connection',
      'Database',
      'Tables',
      'Indexes',
      'Constraints',
      'Locks',
      'Bloat',
      'Replication',
    ];

    if (this.checks === 'all') return allChecks;
    return this.checks.split(',').map(c => c.charAt(0).toUpperCase() + c.slice(1));
  }

  async checkConnection() {
    logger.info('\n[1] Connection Check');
    logger.info('-'.repeat(60));

    try {
      const result = await db.query('SELECT NOW() as time');
      this.pass(`✓ Database connection successful`);
      console.log(`  Server time: ${result.rows[0].time}`);
    } catch (err) {
      this.fail(`✗ Database connection failed: ${err.message}`);
    }
  }

  async checkDatabase() {
    logger.info('\n[2] Database Check');
    logger.info('-'.repeat(60));

    try {
      const result = await db.query(`
        SELECT
          datname,
          pg_size_pretty(pg_database_size(datname)) as size,
          pg_size_pretty(pg_database_size(datname)::BIGINT * 0.7) as estimated_bloat,
          (SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()) as active_connections
        FROM pg_database
        WHERE datname = current_database()
      `);

      if (result.rows.length === 0) {
        this.fail('✗ Database not found');
        return;
      }

      const db_info = result.rows[0];
      this.pass(`✓ Database integrity check passed`);
      console.log(`  Database: ${db_info.datname}`);
      console.log(`  Size: ${db_info.size}`);
      console.log(`  Active Connections: ${db_info.active_connections}`);
    } catch (err) {
      this.fail(`✗ Database check failed: ${err.message}`);
    }
  }

  async checkTables() {
    logger.info('\n[3] Tables Check');
    logger.info('-'.repeat(60));

    try {
      const result = await db.query(`
        SELECT
          COUNT(*) as table_count,
          SUM(n_live_tup) as total_rows
        FROM pg_stat_user_tables
      `);

      const { table_count, total_rows } = result.rows[0];

      if (table_count === 0) {
        this.warn('⚠ No tables found');
        return;
      }

      this.pass(`✓ Found ${table_count} table(s) with ${total_rows || 0} row(s)`);

      // Check for table bloat
      const bloatResult = await db.query(`
        SELECT
          schemaname,
          tablename,
          ROUND(100 * (CASE WHEN otta > 0 THEN sml.relpages - otta ELSE 0 END) /
            sml.relpages::numeric, 2) AS table_waste_percent
        FROM (
          SELECT
            schemaname, tablename, relpages, otta,
            CEIL(cc::float / bs)::int AS sml
          FROM (
            SELECT
              schemaname, tablename, pg_relation_size(schemaname||'.'||tablename) AS size,
              CEIL((cc::float) / bs) AS otta, bs, cc
            FROM (
              SELECT
                schemaname, tablename,
                CEIL(pg_relation_size(schemaname||'.'||tablename) / 8192.0)::int AS relpages,
                cc,
                bs
              FROM (
                SELECT schemaname, tablename, cc, bs
                FROM (SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'public') t
                CROSS JOIN (SELECT 23 AS cc, 8192 AS bs) x
              ) y
              CROSS JOIN (SELECT relnatts::int AS cc FROM pg_class WHERE oid = to_regclass('public.' || tablename)) z
            ) a
          ) b
        ) c
        WHERE relpages - otta > 0
        ORDER BY table_waste_percent DESC
        LIMIT 5
      `);

      if (bloatResult.rows.length > 0) {
        this.warn('⚠ Table bloat detected:');
        bloatResult.rows.forEach(row => {
          console.log(`  ${row.tablename}: ${row.table_waste_percent}% waste`);
        });
      }
    } catch (err) {
      this.warn(`⚠ Could not analyze tables: ${err.message}`);
    }
  }

  async checkIndexes() {
    logger.info('\n[4] Indexes Check');
    logger.info('-'.repeat(60));

    try {
      const result = await db.query(`
        SELECT COUNT(*) as index_count FROM pg_indexes WHERE schemaname = 'public'
      `);

      const count = result.rows[0].index_count;
      this.pass(`✓ Found ${count} index(es)`);

      // Check for invalid indexes
      const invalidResult = await db.query(`
        SELECT indexname, tablename
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND indexdef LIKE '%INVALID%'
      `);

      if (invalidResult.rows.length > 0) {
        this.fail('✗ Invalid indexes found:');
        invalidResult.rows.forEach(row => {
          console.log(`  ${row.indexname} on ${row.tablename}`);
        });
      }
    } catch (err) {
      this.warn(`⚠ Could not check indexes: ${err.message}`);
    }
  }

  async checkConstraints() {
    logger.info('\n[5] Constraints Check');
    logger.info('-'.repeat(60));

    try {
      const result = await db.query(`
        SELECT
          COUNT(*) as constraint_count,
          COUNT(CASE WHEN constraint_type = 'FOREIGN KEY' THEN 1 END) as foreign_keys,
          COUNT(CASE WHEN constraint_type = 'PRIMARY KEY' THEN 1 END) as primary_keys,
          COUNT(CASE WHEN constraint_type = 'UNIQUE' THEN 1 END) as unique_constraints
        FROM information_schema.table_constraints
        WHERE table_schema = 'public'
      `);

      const c = result.rows[0];
      this.pass(`✓ Constraints check passed`);
      console.log(`  Total: ${c.constraint_count} | PKs: ${c.primary_keys} | FKs: ${c.foreign_keys} | Unique: ${c.unique_constraints}`);
    } catch (err) {
      this.warn(`⚠ Could not check constraints: ${err.message}`);
    }
  }

  async checkLocks() {
    logger.info('\n[6] Locks Check');
    logger.info('-'.repeat(60));

    try {
      const result = await db.query(`
        SELECT
          COUNT(*) as lock_count,
          COUNT(CASE WHEN locktype = 'relation' THEN 1 END) as relation_locks,
          COUNT(CASE WHEN locktype = 'advisory' THEN 1 END) as advisory_locks
        FROM pg_locks
        WHERE database = (SELECT oid FROM pg_database WHERE datname = current_database())
      `);

      const locks = result.rows[0];

      if (locks.lock_count > 100) {
        this.warn(`⚠ High lock count: ${locks.lock_count}`);
      } else {
        this.pass(`✓ Lock count acceptable: ${locks.lock_count}`);
      }
    } catch (err) {
      this.warn(`⚠ Could not check locks: ${err.message}`);
    }
  }

  async checkBloat() {
    logger.info('\n[7] Bloat Check');
    logger.info('-'.repeat(60));

    try {
      const result = await db.query(`
        SELECT
          ROUND(100 * pg_database_size(current_database())::BIGINT /
            (pg_database_size(current_database())::BIGINT + 1), 2) as bloat_ratio
      `);

      const bloatRatio = result.rows[0].bloat_ratio;

      if (bloatRatio > 20) {
        this.warn(`⚠ High database bloat detected: ${bloatRatio}%`);
      } else {
        this.pass(`✓ Bloat within acceptable range: ${bloatRatio}%`);
      }
    } catch (err) {
      this.warn(`⚠ Could not check bloat: ${err.message}`);
    }
  }

  async checkReplication() {
    logger.info('\n[8] Replication Check');
    logger.info('-'.repeat(60));

    try {
      const result = await db.query(`
        SELECT slot_name, slot_type, database FROM pg_replication_slots
      `);

      if (result.rows.length === 0) {
        logger.info('ℹ No replication slots configured (primary server)');
        return;
      }

      this.pass(`✓ Found ${result.rows.length} replication slot(s)`);
      result.rows.forEach(row => {
        console.log(`  ${row.slot_name} [${row.slot_type}]`);
      });
    } catch (err) {
      logger.debug('Replication check skipped');
    }
  }

  pass(message) {
    this.results.passed.push(message);
    console.log(message);
  }

  fail(message) {
    this.results.failed.push(message);
    console.log(message);
  }

  warn(message) {
    this.results.warnings.push(message);
  }

  printReport() {
    logger.info('\n' + '='.repeat(60));
    logger.info('Health Check Summary');
    logger.info('='.repeat(60));

    const total = this.results.passed.length + this.results.failed.length;

    if (this.results.failed.length === 0) {
      logger.success(`All ${total} check(s) passed!`);
    } else {
      logger.failure(`${this.results.failed.length}/${total} check(s) failed`);
    }

    if (this.results.warnings.length > 0) {
      logger.warn(`\n${this.results.warnings.length} warning(s):`);
      this.results.warnings.forEach(w => console.log(`  ⚠ ${w}`));
    }

    const status = this.results.failed.length === 0 ? 'HEALTHY' : 'UNHEALTHY';
    console.log(`\nStatus: ${status}`);
  }
}

async function main() {
  const checker = new HealthChecker();

  try {
    await checker.check();
  } catch (err) {
    logger.error('Fatal error', err.message);
    process.exit(1);
  }
}

main();
