#!/usr/bin/env node

/**
 * Database Migration Runner
 * Executes SQL migration files in order
 * Usage: node migrate.js [action] [--dir path/to/migrations]
 * Actions: up, down, status, create
 */

const fs = require('fs');
const path = require('path');
const db = require('./db');
const logger = require('./logger');

const args = process.argv.slice(2);
const action = args[0] || 'status';
const migrationsDir = path.join(process.cwd(), 'migrations');

class MigrationRunner {
  constructor() {
    this.migrationsDir = migrationsDir;
    this.table = 'schema_migrations';
  }

  async init() {
    try {
      await db.connect();
      await this.createMigrationsTable();
    } catch (err) {
      logger.error('Initialization failed', err.message);
      process.exit(1);
    }
  }

  async createMigrationsTable() {
    const createTableSQL = `
      CREATE TABLE IF NOT EXISTS ${this.table} (
        version VARCHAR(255) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        duration_ms INTEGER
      )
    `;

    try {
      await db.query(createTableSQL);
      logger.debug(`Migrations table ready: ${this.table}`);
    } catch (err) {
      logger.error('Failed to create migrations table', err.message);
      throw err;
    }
  }

  getMigrationFiles() {
    if (!fs.existsSync(this.migrationsDir)) {
      logger.warn(`Migrations directory not found: ${this.migrationsDir}`);
      return [];
    }

    return fs
      .readdirSync(this.migrationsDir)
      .filter(f => f.endsWith('.sql'))
      .sort();
  }

  async getExecutedMigrations() {
    try {
      const result = await db.query(`SELECT version FROM ${this.table} ORDER BY version`);
      return result.rows.map(r => r.version);
    } catch (err) {
      logger.debug('No executed migrations found');
      return [];
    }
  }

  async status() {
    logger.info('Migration Status Report');
    logger.info('======================');

    const files = this.getMigrationFiles();
    const executed = await this.getExecutedMigrations();

    if (files.length === 0) {
      logger.warn('No migration files found');
      return;
    }

    files.forEach(file => {
      const version = file.split('_')[0];
      const isExecuted = executed.includes(version);
      const status = isExecuted ? '✓ EXECUTED' : '○ PENDING';
      console.log(`${status} ${file}`);
    });

    logger.info(`\nTotal: ${files.length} | Executed: ${executed.length} | Pending: ${files.length - executed.length}`);
  }

  async up(steps = Infinity) {
    logger.info(`Running migrations (up to ${steps} steps)...`);

    const files = this.getMigrationFiles();
    const executed = await this.getExecutedMigrations();
    const pending = files.filter(f => !executed.includes(f.split('_')[0]));

    if (pending.length === 0) {
      logger.success('All migrations are up to date');
      return;
    }

    let count = 0;
    for (const file of pending.slice(0, steps)) {
      await this.executeMigration(file, 'up');
      count++;
    }

    logger.success(`Executed ${count} migration(s)`);
  }

  async executeMigration(file, direction = 'up') {
    const filePath = path.join(this.migrationsDir, file);
    const version = file.split('_')[0];
    const name = file.replace('.sql', '');

    try {
      const sql = fs.readFileSync(filePath, 'utf8');
      const startTime = Date.now();

      // Execute migration in transaction
      await db.transaction(async (client) => {
        await client.query(sql);

        // Record migration
        if (direction === 'up') {
          const duration = Date.now() - startTime;
          await client.query(
            `INSERT INTO ${this.table} (version, name, duration_ms) VALUES ($1, $2, $3)`,
            [version, name, duration]
          );
        } else {
          await client.query(
            `DELETE FROM ${this.table} WHERE version = $1`,
            [version]
          );
        }
      });

      const duration = Date.now() - startTime;
      logger.success(`${direction === 'up' ? '→' : '←'} ${file} (${duration}ms)`);
    } catch (err) {
      logger.error(`Migration failed: ${file}`, err.message);
      throw err;
    }
  }

  async down(steps = 1) {
    logger.info(`Rolling back ${steps} migration(s)...`);

    const executed = await this.getExecutedMigrations();
    const files = this.getMigrationFiles();
    const toRollback = executed
      .reverse()
      .slice(0, steps)
      .map(v => files.find(f => f.startsWith(v)))
      .filter(Boolean);

    if (toRollback.length === 0) {
      logger.warn('No migrations to rollback');
      return;
    }

    for (const file of toRollback) {
      // For rollback, you would need separate .down.sql files
      logger.warn(`Rollback not implemented for ${file}`);
    }
  }

  async create(name) {
    const version = Date.now();
    const upFile = `${version}_${name}.sql`;
    const upPath = path.join(this.migrationsDir, upFile);

    if (!fs.existsSync(this.migrationsDir)) {
      fs.mkdirSync(this.migrationsDir, { recursive: true });
    }

    const template = `-- Migration: ${name}
-- Created: ${new Date().toISOString()}

BEGIN;

-- Add your SQL statements here

COMMIT;
`;

    try {
      fs.writeFileSync(upPath, template);
      logger.success(`Migration created: ${upFile}`);
    } catch (err) {
      logger.error('Failed to create migration', err.message);
      throw err;
    }
  }
}

async function main() {
  const runner = new MigrationRunner();

  try {
    await runner.init();

    switch (action) {
      case 'up':
        await runner.up();
        break;
      case 'down':
        await runner.down();
        break;
      case 'status':
        await runner.status();
        break;
      case 'create':
        if (!args[1]) {
          logger.error('Usage: migrate.js create <migration_name>');
          process.exit(1);
        }
        await runner.create(args[1]);
        break;
      default:
        logger.error(`Unknown action: ${action}`);
        process.exit(1);
    }
  } catch (err) {
    logger.error('Migration runner error', err.message);
    process.exit(1);
  } finally {
    await db.disconnect();
  }
}

main();
