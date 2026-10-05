#!/usr/bin/env node

/**
 * Interactive Query Builder
 * Build and execute SQL queries with a simple interface
 * Usage: node query-builder.js [--template select|insert|update|delete] [--table table_name]
 */

const readline = require('readline');
const db = require('./db');
const logger = require('./logger');

class QueryBuilder {
  constructor() {
    this.template = process.argv.find(a => a.includes('--template'))?.split('=')[1] || 'select';
    this.tableName = process.argv.find(a => a.includes('--table'))?.split('=')[1];
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: 'sql> ',
    });
    this.query = '';
    this.tables = [];
  }

  async start() {
    try {
      await db.connect();

      logger.success('Connected to database');
      logger.info('Query Builder - Type "help" for commands');
      logger.info('='.repeat(60));

      // Load tables
      await this.loadTables();

      this.rl.prompt();

      this.rl.on('line', async (input) => {
        const cmd = input.trim().toLowerCase();

        try {
          switch (cmd) {
            case 'help':
              this.showHelp();
              break;
            case 'list':
              await this.listTables();
              break;
            case 'clear':
              this.query = '';
              logger.success('Query cleared');
              break;
            case 'show':
              console.log('\nCurrent Query:');
              console.log(this.query);
              break;
            case 'run':
            case 'execute':
              await this.executeQuery();
              break;
            case 'template':
              this.showTemplates();
              break;
            case 'describe':
              if (this.tableName) {
                await this.describeTable(this.tableName);
              }
              break;
            case 'exit':
            case 'quit':
              this.exit();
              return;
            default:
              // Assume it's a SQL query
              this.query += (this.query ? ' ' : '') + input;
              if (input.endsWith(';')) {
                await this.executeQuery();
              }
              break;
          }
        } catch (err) {
          logger.error('Error', err.message);
        }

        this.rl.prompt();
      });

      this.rl.on('close', () => {
        this.exit();
      });
    } catch (err) {
      logger.error('Failed to start', err.message);
      process.exit(1);
    }
  }

  async loadTables() {
    try {
      const result = await db.query(`
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
      `);
      this.tables = result.rows.map(r => r.table_name);
    } catch (err) {
      logger.debug('Failed to load tables');
    }
  }

  showHelp() {
    const help = `
  Available Commands:
  ==================
  help              - Show this help message
  list              - List all tables
  describe          - Describe current table schema
  template          - Show query templates
  show              - Show current query
  clear             - Clear current query
  run / execute     - Execute the query
  exit / quit       - Exit the builder

  Examples:
  =========
  SELECT * FROM users;
  INSERT INTO users (name, email) VALUES ('John', 'john@example.com');
  UPDATE users SET name = 'Jane' WHERE id = 1;
  DELETE FROM users WHERE id = 1;
    `;
    console.log(help);
  }

  async listTables() {
    if (this.tables.length === 0) {
      logger.warn('No tables found');
      return;
    }

    logger.info('Available Tables:');
    this.tables.forEach(table => {
      console.log(`  - ${table}`);
    });
  }

  showTemplates() {
    const templates = {
      select: 'SELECT column1, column2 FROM table_name WHERE condition;',
      insert: 'INSERT INTO table_name (col1, col2) VALUES (val1, val2);',
      update: 'UPDATE table_name SET column1 = value1 WHERE condition;',
      delete: 'DELETE FROM table_name WHERE condition;',
      join: 'SELECT a.*, b.* FROM table1 a JOIN table2 b ON a.id = b.id;',
      aggregate: 'SELECT COUNT(*) as count FROM table_name GROUP BY column;',
    };

    logger.info('Query Templates:');
    Object.entries(templates).forEach(([name, sql]) => {
      console.log(`\n  ${name}:`);
      console.log(`    ${sql}`);
    });
  }

  async describeTable(tableName) {
    try {
      const result = await db.query(`
        SELECT
          column_name,
          data_type,
          is_nullable,
          column_default
        FROM information_schema.columns
        WHERE table_name = $1
        ORDER BY ordinal_position
      `, [tableName]);

      if (result.rows.length === 0) {
        logger.warn(`Table not found: ${tableName}`);
        return;
      }

      logger.info(`\nTable: ${tableName}`);
      console.log('  Column Name          | Type           | Nullable | Default');
      console.log('  ' + '-'.repeat(65));

      result.rows.forEach(row => {
        const nullable = row.is_nullable === 'YES' ? 'YES' : 'NO';
        const defaultVal = row.column_default || '-';
        console.log(
          `  ${String(row.column_name).padEnd(20)} | ${String(row.data_type).padEnd(14)} | ${nullable.padEnd(8)} | ${defaultVal}`
        );
      });
    } catch (err) {
      logger.error('Failed to describe table', err.message);
    }
  }

  async executeQuery() {
    if (!this.query.trim()) {
      logger.warn('No query to execute');
      return;
    }

    try {
      const startTime = Date.now();
      const result = await db.query(this.query);
      const duration = Date.now() - startTime;

      console.log(`\n✓ Query executed in ${duration}ms`);

      if (result.rows.length > 0) {
        this.printResults(result.rows);
      } else {
        console.log('(No rows returned)');
      }

      console.log(`\nRows affected: ${result.rowCount}`);

      this.query = '';
    } catch (err) {
      logger.error('Query error', err.message);
    }
  }

  printResults(rows) {
    if (rows.length === 0) return;

    const columns = Object.keys(rows[0]);
    const colWidths = columns.map(col => Math.max(col.length, 15));

    // Header
    console.log('\n  ' + columns.map((col, i) =>
      col.padEnd(colWidths[i])
    ).join(' | '));

    console.log('  ' + colWidths.map(w => '-'.repeat(w)).join('-+-'));

    // Rows
    rows.slice(0, 20).forEach(row => {
      console.log('  ' + columns.map((col, i) => {
        let val = String(row[col] || '');
        if (val.length > colWidths[i]) {
          val = val.substring(0, colWidths[i] - 3) + '...';
        }
        return val.padEnd(colWidths[i]);
      }).join(' | '));
    });

    if (rows.length > 20) {
      console.log(`\n  ... and ${rows.length - 20} more rows`);
    }
  }

  exit() {
    logger.success('Goodbye!');
    this.rl.close();
    process.exit(0);
  }
}

async function main() {
  const builder = new QueryBuilder();
  await builder.start();
}

main();
