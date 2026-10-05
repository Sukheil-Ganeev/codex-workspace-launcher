#!/usr/bin/env node

/**
 * Automated Database Backup with pg_dump
 * Usage: node backup.js [--format custom|tar|plain] [--compression 0-9] [--output path]
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const config = require('./config');
const logger = require('./logger');

class DatabaseBackup {
  constructor() {
    this.format = this.getArg('--format') || 'custom';
    this.compression = parseInt(this.getArg('--compression') || '6');
    this.backupDir = this.getArg('--output') || config.backupDir;
    this.timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
  }

  getArg(name) {
    const arg = process.argv.find(a => a.startsWith(name));
    return arg ? arg.split('=')[1] : null;
  }

  generateFilename() {
    const ext = {
      custom: 'dump',
      tar: 'tar',
      plain: 'sql',
    }[this.format];

    return `backup_${config.dbConfig.database}_${this.timestamp}_${Date.now()}.${ext}`;
  }

  ensureBackupDir() {
    if (!fs.existsSync(this.backupDir)) {
      try {
        fs.mkdirSync(this.backupDir, { recursive: true });
        logger.success(`Created backup directory: ${this.backupDir}`);
      } catch (err) {
        logger.error('Failed to create backup directory', err.message);
        throw err;
      }
    }
  }

  async backup() {
    this.ensureBackupDir();

    const filename = this.generateFilename();
    const filepath = path.join(this.backupDir, filename);

    logger.info(`Starting backup of ${config.dbConfig.database}...`);
    logger.info(`Format: ${this.format} | Compression: ${this.compression}`);

    try {
      const startTime = Date.now();

      const cmd = this.buildCommand(filepath);
      logger.debug(`Command: ${cmd.replace(/password[^\\s]*/g, 'PASSWORD=***')}`);

      execSync(cmd, { stdio: 'inherit' });

      const duration = ((Date.now() - startTime) / 1000).toFixed(2);
      const size = fs.statSync(filepath).size;
      const sizeInMB = (size / 1024 / 1024).toFixed(2);

      logger.success(`Backup completed in ${duration}s`);
      logger.info(`File: ${filepath}`);
      logger.info(`Size: ${sizeInMB} MB`);

      return filepath;
    } catch (err) {
      logger.error('Backup failed', err.message);
      process.exit(1);
    }
  }

  buildCommand(filepath) {
    const { host, port, database, user, password } = config.dbConfig;

    let cmd = `pg_dump`;
    cmd += ` --host=${host}`;
    cmd += ` --port=${port}`;
    cmd += ` --username=${user}`;
    cmd += ` --format=${this.format[0].toUpperCase()}`;
    cmd += ` --compress=${this.compression}`;
    cmd += ` --file="${filepath}"`;
    cmd += ` --verbose`;

    // Add password if provided
    if (password) {
      cmd = `PGPASSWORD='${password}' ${cmd}`;
    }

    cmd += ` ${database}`;

    return cmd;
  }

  async verifyBackup(filepath) {
    logger.info('Verifying backup integrity...');

    try {
      const { user, password } = config.dbConfig;

      let cmd = `pg_restore`;
      cmd += ` --data-only`;
      cmd += ` --list`;
      cmd += ` "${filepath}"`;

      if (password) {
        cmd = `PGPASSWORD='${password}' ${cmd}`;
      }

      execSync(cmd);
      logger.success('Backup verification passed');
      return true;
    } catch (err) {
      logger.warn('Backup verification failed', err.message);
      return false;
    }
  }

  async list() {
    logger.info(`Backups in ${this.backupDir}:`);

    try {
      const files = fs.readdirSync(this.backupDir)
        .filter(f => f.includes('backup_'))
        .sort()
        .reverse();

      if (files.length === 0) {
        logger.warn('No backups found');
        return;
      }

      files.forEach(file => {
        const filepath = path.join(this.backupDir, file);
        const stats = fs.statSync(filepath);
        const size = (stats.size / 1024 / 1024).toFixed(2);
        const date = new Date(stats.mtime).toLocaleString();
        console.log(`  ${file} (${size} MB) - ${date}`);
      });

      logger.info(`\nTotal: ${files.length} backup(s)`);
    } catch (err) {
      logger.error('Failed to list backups', err.message);
    }
  }

  async cleanup(keepCount = 5) {
    logger.info(`Cleaning up backups (keeping last ${keepCount})...`);

    try {
      const files = fs.readdirSync(this.backupDir)
        .filter(f => f.includes('backup_'))
        .sort()
        .reverse();

      if (files.length <= keepCount) {
        logger.success('No backups to cleanup');
        return;
      }

      const toDelete = files.slice(keepCount);
      for (const file of toDelete) {
        const filepath = path.join(this.backupDir, file);
        fs.unlinkSync(filepath);
        logger.success(`Deleted: ${file}`);
      }

      logger.success(`Cleaned up ${toDelete.length} backup(s)`);
    } catch (err) {
      logger.error('Cleanup failed', err.message);
    }
  }
}

async function main() {
  const backup = new DatabaseBackup();
  const action = process.argv[2] || 'create';

  try {
    switch (action) {
      case 'create':
        await backup.backup();
        break;
      case 'list':
        await backup.list();
        break;
      case 'cleanup':
        await backup.cleanup(parseInt(process.argv[3]) || 5);
        break;
      default:
        logger.error(`Unknown action: ${action}`);
        logger.info('Usage: node backup.js [create|list|cleanup]');
    }
  } catch (err) {
    logger.error('Fatal error', err.message);
    process.exit(1);
  }
}

main();
