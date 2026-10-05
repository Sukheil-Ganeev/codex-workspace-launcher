/**
 * Database Connection Pool Manager
 * Handles connection pooling and graceful shutdown
 */

const { Pool } = require('pg');
const config = require('./config');
const logger = require('./logger');

class DatabaseManager {
  constructor() {
    this.pool = null;
    this.isConnected = false;
  }

  connect() {
    return new Promise((resolve, reject) => {
      try {
        this.pool = new Pool(config.dbConfig);

        this.pool.on('error', (err) => {
          logger.error('Unexpected error on idle client', err);
        });

        this.pool.on('connect', () => {
          logger.debug('Client connected to database');
        });

        this.pool.query('SELECT NOW()', (err) => {
          if (err) {
            logger.error('Database connection test failed', err.message);
            reject(err);
          } else {
            this.isConnected = true;
            logger.success(`Connected to ${config.dbConfig.database} at ${config.dbConfig.host}`);
            resolve();
          }
        });
      } catch (err) {
        logger.error('Failed to create pool', err.message);
        reject(err);
      }
    });
  }

  async query(sql, params = []) {
    if (!this.pool) {
      throw new Error('Database pool not initialized. Call connect() first.');
    }

    try {
      const result = await this.pool.query(sql, params);
      return result;
    } catch (err) {
      logger.error('Query execution failed', {
        sql: sql.substring(0, 100),
        error: err.message,
      });
      throw err;
    }
  }

  async transaction(callback) {
    const client = await this.pool.connect();
    try {
      await client.query('BEGIN');
      const result = await callback(client);
      await client.query('COMMIT');
      return result;
    } catch (err) {
      await client.query('ROLLBACK');
      logger.error('Transaction failed', err.message);
      throw err;
    } finally {
      client.release();
    }
  }

  async disconnect() {
    if (this.pool) {
      try {
        await this.pool.end();
        this.isConnected = false;
        logger.success('Database connection closed');
      } catch (err) {
        logger.error('Error closing connection', err.message);
        throw err;
      }
    }
  }

  getPoolStats() {
    if (!this.pool) return null;

    return {
      totalConnections: this.pool.totalCount,
      idleConnections: this.pool.idleCount,
      waitingRequests: this.pool.waitingCount,
      maxConnections: config.maxConnections,
    };
  }
}

module.exports = new DatabaseManager();
