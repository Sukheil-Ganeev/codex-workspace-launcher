#!/usr/bin/env node

/**
 * Replication Setup Helper
 * Configures and manages PostgreSQL replication
 * Usage: node replication-setup.js [--role primary|replica] [--slot-name slot]
 */

const db = require('./db');
const logger = require('./logger');
const { execSync } = require('child_process');

class ReplicationSetup {
  constructor() {
    this.role = process.argv.find(a => a.includes('--role'))?.split('=')[1] || 'primary';
    this.slotName = process.argv.find(a => a.includes('--slot-name'))?.split('=')[1] || 'replication_slot';
    this.replicaHost = process.argv.find(a => a.includes('--replica-host'))?.split('=')[1];
    this.walLevel = process.argv.find(a => a.includes('--wal-level'))?.split('=')[1] || 'replica';
  }

  async setup() {
    try {
      await db.connect();

      logger.info('PostgreSQL Replication Setup');
      logger.info('='.repeat(60));

      if (this.role === 'primary') {
        await this.setupPrimary();
      } else if (this.role === 'replica') {
        await this.setupReplica();
      } else {
        logger.error('Invalid role. Use --role primary|replica');
        process.exit(1);
      }
    } catch (err) {
      logger.error('Setup error', err.message);
      process.exit(1);
    } finally {
      await db.disconnect();
    }
  }

  async setupPrimary() {
    logger.info('\nSetting up PRIMARY server...');
    logger.info('-'.repeat(60));

    try {
      // Check current wal_level
      const walResult = await db.query("SHOW wal_level");
      const currentWal = walResult.rows[0].wal_level;

      logger.info(`Current WAL level: ${currentWal}`);

      if (currentWal !== this.walLevel && this.walLevel !== 'replica') {
        logger.warn(`Current WAL level is ${currentWal}, requires ${this.walLevel}`);
        logger.warn('Update postgresql.conf and restart server');
      }

      // Create replication slot
      await this.createReplicationSlot();

      // Configure replication user if needed
      await this.checkReplicationUser();

      // Get LSN information
      await this.getLSNInfo();

      // Show backup commands
      await this.showBackupCommands();

      logger.success('Primary server configured for replication');
    } catch (err) {
      logger.error('Primary setup failed', err.message);
      throw err;
    }
  }

  async setupReplica() {
    logger.info('\nSetting up REPLICA server...');
    logger.info('-'.repeat(60));

    if (!this.replicaHost) {
      logger.error('--replica-host required for replica setup');
      process.exit(1);
    }

    try {
      // Check if server is in recovery
      const recoveryResult = await db.query('SELECT pg_is_in_recovery()');
      const inRecovery = recoveryResult.rows[0].pg_is_in_recovery;

      if (!inRecovery) {
        logger.warn('This server is not in recovery mode');
        logger.warn('Run pg_basebackup from primary first');
      }

      // Show replica status
      await this.getReplicaStatus();

      logger.success('Replica server ready for replication');
    } catch (err) {
      logger.error('Replica setup failed', err.message);
      throw err;
    }
  }

  async createReplicationSlot() {
    logger.info(`\nCreating replication slot: ${this.slotName}...`);

    try {
      // Check if slot exists
      const checkResult = await db.query(
        'SELECT slot_name FROM pg_replication_slots WHERE slot_name = $1',
        [this.slotName]
      );

      if (checkResult.rows.length > 0) {
        logger.success(`Slot already exists: ${this.slotName}`);
        return;
      }

      await db.query(
        'SELECT pg_create_logical_replication_slot($1, $2)',
        [this.slotName, 'test_decoding']
      );

      logger.success(`Created replication slot: ${this.slotName}`);
    } catch (err) {
      logger.error('Failed to create slot', err.message);
    }
  }

  async checkReplicationUser() {
    logger.info('\nChecking replication user...');

    try {
      const result = await db.query(`
        SELECT usename, usesuper, userepl
        FROM pg_user
        WHERE userepl = true
      `);

      if (result.rows.length === 0) {
        logger.warn('No replication user found');
        logger.info('Create with: CREATE USER replicator WITH PASSWORD \'password\' REPLICATION');
        return;
      }

      result.rows.forEach(user => {
        console.log(`  ${user.usename}: replication enabled`);
      });
    } catch (err) {
      logger.error('Failed to check replication user', err.message);
    }
  }

  async getLSNInfo() {
    logger.info('\nLSN Information:');

    try {
      const result = await db.query(`
        SELECT
          pg_current_wal_lsn() as current_lsn,
          pg_current_wal_insert_lsn() as insert_lsn,
          pg_current_wal_flush_lsn() as flush_lsn
      `);

      const info = result.rows[0];
      console.log(`  Current LSN: ${info.current_lsn}`);
      console.log(`  Insert LSN:  ${info.insert_lsn}`);
      console.log(`  Flush LSN:   ${info.flush_lsn}`);
    } catch (err) {
      logger.debug('LSN info not available');
    }
  }

  async showBackupCommands() {
    logger.info('\nBase Backup Command (run on replica):');
    logger.info('-'.repeat(60));

    const config = require('./config');
    const { host, port, user } = config.dbConfig;

    const cmd = `pg_basebackup -h ${host} -p ${port} -U ${user} -D /path/to/replica -Fp -Xs -Pv`;

    console.log(`\n${cmd}\n`);

    const archiveCmd = `archive_command = 'test ! -f /archive/%f && cp %p /archive/%f'`;
    console.log(`Set in postgresql.conf:`);
    console.log(`  ${archiveCmd}\n`);
  }

  async getReplicaStatus() {
    logger.info('\nReplica Status:');

    try {
      const result = await db.query(`
        SELECT
          client_addr,
          usename,
          application_name,
          backend_start,
          backend_xmin,
          write_lsn,
          flush_lsn,
          replay_lsn
        FROM pg_stat_replication
      `);

      if (result.rows.length === 0) {
        logger.warn('No replica connections');
        return;
      }

      result.rows.forEach(row => {
        console.log(`\n  Client: ${row.client_addr}`);
        console.log(`  User: ${row.usename}`);
        console.log(`  Application: ${row.application_name}`);
        console.log(`  Write LSN: ${row.write_lsn}`);
        console.log(`  Flush LSN: ${row.flush_lsn}`);
        console.log(`  Replay LSN: ${row.replay_lsn}`);
      });
    } catch (err) {
      logger.error('Failed to get replica status', err.message);
    }
  }

  async dropSlot() {
    logger.warn(`Dropping replication slot: ${this.slotName}...`);

    try {
      await db.query(
        'SELECT pg_drop_replication_slot($1)',
        [this.slotName]
      );
      logger.success('Slot dropped');
    } catch (err) {
      logger.error('Failed to drop slot', err.message);
    }
  }

  async testConnection() {
    logger.info('\nTesting replication connection...');

    if (!this.replicaHost) {
      logger.error('--replica-host required');
      return;
    }

    try {
      const cmd = `pg_isready -h ${this.replicaHost} -p 5432`;
      const output = execSync(cmd, { encoding: 'utf8' });
      logger.success(`Connection to ${this.replicaHost} successful`);
    } catch (err) {
      logger.error(`Connection to ${this.replicaHost} failed`, err.message);
    }
  }
}

async function main() {
  const replication = new ReplicationSetup();
  const action = process.argv[2] || 'setup';

  try {
    switch (action) {
      case 'setup':
        await replication.setup();
        break;
      case 'drop-slot':
        await replication.dropSlot();
        break;
      case 'test':
        await replication.testConnection();
        break;
      default:
        logger.error(`Unknown action: ${action}`);
        logger.info('Usage: node replication-setup.js [setup|drop-slot|test] [--role primary|replica]');
    }
  } catch (err) {
    logger.error('Fatal error', err.message);
    process.exit(1);
  }
}

main();
