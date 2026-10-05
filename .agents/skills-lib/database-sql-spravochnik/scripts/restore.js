#!/usr/bin/env node

/**
 * Database Restore from Backup
 * Usage: node restore.js --file path/to/backup [--format custom|tar|plain] [--clean]
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const config = require('./config');
const logger = require('./logger');

class DatabaseRestore {
  constructor() {
    this.backupFile = this.getArg('--file');
    this.format = this.getArg('--format') || 'custom';
    this.shouldClean = process.argv.includes('--clean');
    this.shouldDropSchema = process.argv.includes('--drop-schema');
    this.verbose = process.argv.includes('--verbose');
  }

  getArg(name) {
    const arg = process.argv.find(a => a.startsWith(name));
    return arg ? arg.split('=')[1] : null;
  }

  validate() {
    if (!this.backupFile) {
      logger.error('Missing required argument: --file');
      logger.info('Usage: node restore.js --file path/to/backup [--format custom|tar|plain] [--clean]');
      process.exit(1);
    }

    if (!fs.existsSync(this.backupFile)) {
      logger.error(`Backup file not found: ${this.backupFile}`);
      process.exit(1);
    }
  }

  async confirmRestore() {
    return new Promise((resolve) => {
      logger.warn('WARNING: This will restore the database from backup');
      logger.warn(`Database: ${config.dbConfig.database}`);
      logger.warn(`Backup: ${this.backupFile}`);

      if (this.shouldDropSchema) {
        logger.warn('This will DROP all existing schemas!');
      }

      if (process.argv.includes('--force') || process.argv.includes('-f')) {
        logger.info('Forced restore (--force flag detected)');
        resolve(true);
      } else {
        // In non-interactive mode, require explicit confirmation
        logger.error('Add --force flag to proceed with restore');
        process.exit(1);
      }
    });
  }

  async restore() {
    this.validate();
    await this.confirmRestore();

    logger.info('Starting restore...');
    const startTime = Date.now();

    try {
      const cmd = this.buildCommand();
      logger.debug(`Command: ${cmd.replace(/password[^\\s]*/g, 'PASSWORD=***')}`);

      execSync(cmd, { stdio: 'inherit' });

      const duration = ((Date.now() - startTime) / 1000).toFixed(2);
      logger.success(`Restore completed in ${duration}s`);

      return true;
    } catch (err) {
      logger.error('Restore failed', err.message);
      throw err;
    }
  }

  buildCommand() {
    const { host, port, database, user, password } = config.dbConfig;

    let cmd = `pg_restore`;
    cmd += ` --host=${host}`;
    cmd += ` --port=${port}`;
    cmd += ` --username=${user}`;
    cmd += ` --format=${this.format[0].toUpperCase()}`;

    if (this.shouldClean) {
      cmd += ` --clean`;
    }

    if (this.shouldDropSchema) {
      cmd += ` --if-exists`;
    }

    if (this.verbose) {
      cmd += ` --verbose`;
    }

    cmd += ` --dbname=${database}`;
    cmd += ` "${this.backupFile}"`;

    if (password) {
      cmd = `PGPASSWORD='${password}' ${cmd}`;
    }

    return cmd;
  }

  async listBackupContents() {
    logger.info(`Contents of ${this.backupFile}:`);

    try {
      const { user, password } = config.dbConfig;

      let cmd = `pg_restore`;
      cmd += ` --list`;
      cmd += ` "${this.backupFile}"`;

      if (password) {
        cmd = `PGPASSWORD='${password}' ${cmd}`;
      }

      const output = execSync(cmd, { encoding: 'utf8' });
      console.log(output);
    } catch (err) {
      logger.error('Failed to list backup contents', err.message);
    }
  }

  async testRestore() {
    logger.warn('Testing restore on copy of database...');
    logger.info('(This feature requires pg_dump with --create flag)');

    // This would create a test database and restore to it
    // Not fully implemented in this example
    logger.warn('Test restore not implemented in this version');
  }
}

async function main() {
  const restore = new DatabaseRestore();
  const action = process.argv[2] || 'restore';

  try {
    switch (action) {
      case 'restore':
        await restore.restore();
        break;
      case 'list':
        await restore.listBackupContents();
        break;
      case 'test':
        await restore.testRestore();
        break;
      default:
        logger.error(`Unknown action: ${action}`);
        logger.info('Usage: node restore.js [restore|list|test] --file <backup>');
    }
  } catch (err) {
    logger.error('Fatal error', err.message);
    process.exit(1);
  }
}

main();
