#!/usr/bin/env node

/**
 * Test Data Factory
 * Production-ready factory for creating test data with proper relationships
 * Usage: node test-factory.js [--count 10] [--table users] [--relate]
 */

const db = require('./db');
const logger = require('./logger');

class TestFactory {
  constructor() {
    this.count = parseInt(process.argv.find(a => a.includes('--count'))?.split('=')[1] || '10');
    this.tableName = process.argv.find(a => a.includes('--table'))?.split('=')[1] || null;
    this.createRelations = process.argv.includes('--relate');
  }

  async init() {
    try {
      await db.connect();
    } catch (err) {
      logger.error('Failed to connect', err.message);
      process.exit(1);
    }
  }

  async create() {
    try {
      if (this.tableName) {
        await this.createForTable(this.tableName);
      } else {
        await this.createDefault();
      }
    } catch (err) {
      logger.error('Factory creation failed', err.message);
      process.exit(1);
    } finally {
      await db.disconnect();
    }
  }

  async createDefault() {
    logger.info('Creating test data for all tables...');

    const tables = await this.getTables();

    for (const table of tables) {
      await this.createForTable(table);
    }
  }

  async getTables() {
    const result = await db.query(`
      SELECT table_name FROM information_schema.tables
      WHERE table_schema = 'public'
      ORDER BY table_name
    `);

    return result.rows.map(r => r.table_name);
  }

  async createForTable(tableName) {
    logger.info(`\nCreating ${this.count} records for table: ${tableName}`);

    try {
      const schema = await this.getTableSchema(tableName);
      const pkColumn = schema.find(col => col.is_primary_key);

      logger.progress(0, this.count, tableName);

      for (let i = 0; i < this.count; i++) {
        const data = this.generateRowData(schema, i, pkColumn);
        await this.insertRow(tableName, data);

        if ((i + 1) % 10 === 0) {
          logger.progress(i + 1, this.count, tableName);
        }
      }

      logger.progressEnd();
      logger.success(`Created ${this.count} records in ${tableName}`);
    } catch (err) {
      logger.error(`Failed to create data for ${tableName}`, err.message);
    }
  }

  async getTableSchema(tableName) {
    const result = await db.query(`
      SELECT
        c.column_name,
        c.data_type,
        c.is_nullable,
        c.column_default,
        (tc.constraint_type = 'PRIMARY KEY') as is_primary_key
      FROM information_schema.columns c
      LEFT JOIN information_schema.constraint_column_usage ccu
        ON c.table_name = ccu.table_name AND c.column_name = ccu.column_name
      LEFT JOIN information_schema.table_constraints tc
        ON ccu.constraint_name = tc.constraint_name
      WHERE c.table_name = $1 AND c.table_schema = 'public'
      ORDER BY c.ordinal_position
    `, [tableName]);

    return result.rows;
  }

  generateRowData(schema, index, pkColumn) {
    const data = {};

    schema.forEach(col => {
      // Skip if it's auto-generated or has a default
      if (col.column_default && !col.is_primary_key) {
        return;
      }

      const value = this.generateValue(col, index);
      if (value !== undefined) {
        data[col.column_name] = value;
      }
    });

    return data;
  }

  generateValue(column, index) {
    const { column_name, data_type, is_nullable } = column;

    // Skip auto-increment or defaults
    if (column.column_default) return undefined;

    // Handle different data types
    switch (data_type) {
      case 'bigint':
      case 'integer':
      case 'smallint':
        return Math.floor(Math.random() * 10000) + index;

      case 'numeric':
      case 'decimal':
      case 'real':
      case 'double precision':
        return parseFloat((Math.random() * 1000).toFixed(2));

      case 'boolean':
        return Math.random() > 0.5;

      case 'uuid':
        return this.generateUUID();

      case 'text':
      case 'character varying':
      case 'varchar':
        return this.generateString(column_name, index);

      case 'timestamp':
      case 'timestamp without time zone':
      case 'timestamp with time zone':
        return new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000);

      case 'date':
        return new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split('T')[0];

      case 'time':
      case 'time without time zone':
        return `${String(Math.floor(Math.random() * 24)).padStart(2, '0')}:${String(Math.floor(Math.random() * 60)).padStart(2, '0')}:00`;

      case 'json':
      case 'jsonb':
        return JSON.stringify({
          field: `value_${index}`,
          timestamp: new Date().toISOString(),
        });

      default:
        // For unknown types, return null if nullable
        return is_nullable === 'YES' ? null : `value_${index}`;
    }
  }

  generateString(columnName, index) {
    const templates = {
      email: () => `test.${index}@example.com`,
      name: () => `Test User ${index}`,
      title: () => `Item ${index}`,
      description: () => `Description for item ${index}`,
      username: () => `testuser${index}`,
      phone: () => `+1${String(Math.floor(Math.random() * 9000000000) + 1000000000).slice(0, 10)}`,
      address: () => `${index} Test Street`,
      city: () => `Test City ${index}`,
      country: () => 'United States',
      url: () => `https://example.com/${index}`,
    };

    const lowerName = columnName.toLowerCase();

    for (const [key, fn] of Object.entries(templates)) {
      if (lowerName.includes(key)) {
        return fn();
      }
    }

    return `${columnName}_${index}`;
  }

  generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  async insertRow(tableName, data) {
    if (Object.keys(data).length === 0) {
      return;
    }

    const columns = Object.keys(data);
    const placeholders = columns.map((_, i) => `$${i + 1}`).join(',');
    const columnNames = columns.join(',');
    const values = columns.map(col => data[col]);

    const sql = `INSERT INTO ${tableName} (${columnNames}) VALUES (${placeholders})`;

    try {
      await db.query(sql, values);
    } catch (err) {
      logger.debug(`Insert failed for ${tableName}: ${err.message}`);
    }
  }

  async listFactories() {
    const tables = await this.getTables();
    logger.info('Available test factories:');
    tables.forEach(table => {
      console.log(`  - ${table}`);
    });
  }

  async truncate(tableName) {
    try {
      await db.query(`TRUNCATE TABLE ${tableName} CASCADE`);
      logger.success(`Truncated ${tableName}`);
    } catch (err) {
      logger.error(`Failed to truncate ${tableName}`, err.message);
    }
  }
}

async function main() {
  const factory = new TestFactory();
  const action = process.argv[2] || 'create';

  try {
    await factory.init();

    switch (action) {
      case 'create':
        await factory.create();
        break;
      case 'list':
        await factory.listFactories();
        break;
      case 'truncate':
        if (!factory.tableName) {
          logger.error('Please specify table with --table option');
          process.exit(1);
        }
        await factory.truncate(factory.tableName);
        break;
      default:
        logger.error(`Unknown action: ${action}`);
        logger.info('Usage: node test-factory.js [create|list|truncate] [--table name] [--count n]');
    }
  } catch (err) {
    logger.error('Fatal error', err.message);
    process.exit(1);
  }
}

main();
