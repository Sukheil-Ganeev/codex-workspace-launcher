/**
 * Database Utility Scripts Configuration
 * Central configuration for all database operations
 */

const path = require('path');
const fs = require('fs');

class Config {
  constructor() {
    this.env = process.env.NODE_ENV || 'development';
    this.dbConfig = this.loadDatabaseConfig();
    this.logLevel = process.env.LOG_LEVEL || 'info';
    this.backupDir = process.env.BACKUP_DIR || path.join(process.cwd(), 'backups');
    this.maxConnections = parseInt(process.env.MAX_CONNECTIONS || '20');
    this.timeout = parseInt(process.env.DB_TIMEOUT || '30000');
  }

  loadDatabaseConfig() {
    // Priority: env vars > .env file > config.json > defaults
    const configPath = path.join(process.cwd(), '.env');

    return {
      host: process.env.DB_HOST || 'localhost',
      port: parseInt(process.env.DB_PORT || '5432'),
      database: process.env.DB_NAME || 'postgres',
      user: process.env.DB_USER || 'postgres',
      password: process.env.DB_PASSWORD || 'postgres',
      ssl: process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : false,
      connectionTimeoutMillis: parseInt(process.env.DB_TIMEOUT || '30000'),
      idleTimeoutMillis: parseInt(process.env.DB_IDLE_TIMEOUT || '30000'),
      max: this.maxConnections,
    };
  }

  validate() {
    const required = ['host', 'port', 'database', 'user'];
    const missing = required.filter(key => !this.dbConfig[key]);

    if (missing.length > 0) {
      throw new Error(`Missing required database config: ${missing.join(', ')}`);
    }
  }

  get connectionString() {
    const { host, port, database, user, password } = this.dbConfig;
    return `postgresql://${user}:${password}@${host}:${port}/${database}`;
  }
}

module.exports = new Config();
