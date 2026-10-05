#!/usr/bin/env node

/**
 * Schema Diff Tool
 * Compares schema between two databases or database and file
 * Usage: node schema-diff.js --source db1 --target db2 [--output-format sql|json]
 */

const fs = require('fs');
const { Pool } = require('pg');
const logger = require('./logger');

class SchemaDiffer {
  constructor() {
    this.sourceDb = this.getArg('--source');
    this.targetDb = this.getArg('--target');
    this.outputFormat = this.getArg('--output-format') || 'text';
    this.sourceFile = this.getArg('--source-file');
    this.differences = {
      tablesOnly: [],
      indexesOnly: [],
      columnsAdded: [],
      columnsRemoved: [],
      columnsChanged: [],
      constraintsDifferences: [],
    };
  }

  getArg(name) {
    const arg = process.argv.find(a => a.startsWith(name));
    return arg ? arg.split('=')[1] : null;
  }

  validate() {
    if (!this.sourceDb || !this.targetDb) {
      logger.error('Missing required arguments');
      logger.info('Usage: node schema-diff.js --source db1 --target db2');
      process.exit(1);
    }
  }

  async compare() {
    try {
      this.validate();

      logger.info('Schema Diff Analysis');
      logger.info('='.repeat(60));
      logger.info(`Source: ${this.sourceDb}`);
      logger.info(`Target: ${this.targetDb}`);

      const sourceSchema = await this.getSchema(this.sourceDb);
      const targetSchema = await this.getSchema(this.targetDb);

      this.findDifferences(sourceSchema, targetSchema);
      this.printReport();

      if (this.differences.totalChanges > 0) {
        await this.generateMigrationSQL();
      }
    } catch (err) {
      logger.error('Comparison error', err.message);
      process.exit(1);
    }
  }

  async getSchema(dbName) {
    const pool = new Pool({
      host: process.env.DB_HOST || 'localhost',
      port: parseInt(process.env.DB_PORT || '5432'),
      database: dbName,
      user: process.env.DB_USER || 'postgres',
      password: process.env.DB_PASSWORD || 'postgres',
    });

    try {
      const schema = {
        tables: await this.getTables(pool),
        indexes: await this.getIndexes(pool),
        constraints: await this.getConstraints(pool),
      };
      await pool.end();
      return schema;
    } catch (err) {
      logger.error(`Failed to get schema from ${dbName}`, err.message);
      throw err;
    }
  }

  async getTables(pool) {
    const query = `
      SELECT
        table_name,
        column_name,
        data_type,
        is_nullable,
        column_default,
        ordinal_position
      FROM information_schema.columns
      WHERE table_schema = 'public'
      ORDER BY table_name, ordinal_position
    `;

    const result = await pool.query(query);
    const tables = {};

    result.rows.forEach(row => {
      if (!tables[row.table_name]) {
        tables[row.table_name] = [];
      }
      tables[row.table_name].push({
        name: row.column_name,
        type: row.data_type,
        nullable: row.is_nullable === 'YES',
        default: row.column_default,
      });
    });

    return tables;
  }

  async getIndexes(pool) {
    const query = `
      SELECT indexname, tablename, indexdef
      FROM pg_indexes
      WHERE schemaname = 'public'
    `;

    const result = await pool.query(query);
    const indexes = {};

    result.rows.forEach(row => {
      if (!indexes[row.tablename]) {
        indexes[row.tablename] = [];
      }
      indexes[row.tablename].push({
        name: row.indexname,
        definition: row.indexdef,
      });
    });

    return indexes;
  }

  async getConstraints(pool) {
    const query = `
      SELECT
        constraint_name,
        table_name,
        constraint_type
      FROM information_schema.table_constraints
      WHERE table_schema = 'public'
    `;

    const result = await pool.query(query);
    const constraints = {};

    result.rows.forEach(row => {
      if (!constraints[row.table_name]) {
        constraints[row.table_name] = [];
      }
      constraints[row.table_name].push({
        name: row.constraint_name,
        type: row.constraint_type,
      });
    });

    return constraints;
  }

  findDifferences(source, target) {
    // Tables
    const sourceTables = Object.keys(source.tables);
    const targetTables = Object.keys(target.tables);

    sourceTables.forEach(table => {
      if (!targetTables.includes(table)) {
        this.differences.tablesOnly.push({ type: 'source', table });
      }
    });

    targetTables.forEach(table => {
      if (!sourceTables.includes(table)) {
        this.differences.tablesOnly.push({ type: 'target', table });
      }
    });

    // Columns
    sourceTables.forEach(table => {
      if (!target.tables[table]) return;

      const sourceColumns = source.tables[table];
      const targetColumns = target.tables[table];

      sourceColumns.forEach(col => {
        const targetCol = targetColumns.find(c => c.name === col.name);
        if (!targetCol) {
          this.differences.columnsRemoved.push({ table, column: col });
        } else if (JSON.stringify(col) !== JSON.stringify(targetCol)) {
          this.differences.columnsChanged.push({ table, sourceCol: col, targetCol });
        }
      });

      targetColumns.forEach(col => {
        if (!sourceColumns.find(c => c.name === col.name)) {
          this.differences.columnsAdded.push({ table, column: col });
        }
      });
    });
  }

  printReport() {
    logger.info('\nSchema Differences Found:');
    logger.info('-'.repeat(60));

    let totalChanges = 0;

    if (this.differences.tablesOnly.length > 0) {
      logger.info('\nTable Differences:');
      this.differences.tablesOnly.forEach(item => {
        const type = item.type === 'source' ? 'Only in source' : 'Only in target';
        console.log(`  ${type}: ${item.table}`);
      });
      totalChanges += this.differences.tablesOnly.length;
    }

    if (this.differences.columnsAdded.length > 0) {
      logger.info('\nColumns Added (in target):');
      this.differences.columnsAdded.forEach(item => {
        console.log(`  ${item.table}.${item.column.name} [${item.column.type}]`);
      });
      totalChanges += this.differences.columnsAdded.length;
    }

    if (this.differences.columnsRemoved.length > 0) {
      logger.info('\nColumns Removed (from source):');
      this.differences.columnsRemoved.forEach(item => {
        console.log(`  ${item.table}.${item.column.name} [${item.column.type}]`);
      });
      totalChanges += this.differences.columnsRemoved.length;
    }

    if (this.differences.columnsChanged.length > 0) {
      logger.info('\nColumns Changed:');
      this.differences.columnsChanged.forEach(item => {
        console.log(`  ${item.table}.${item.sourceCol.name}`);
        console.log(`    From: ${item.sourceCol.type}`);
        console.log(`    To:   ${item.targetCol.type}`);
      });
      totalChanges += this.differences.columnsChanged.length;
    }

    if (totalChanges === 0) {
      logger.success('No differences found - schemas are identical!');
    } else {
      logger.info(`\nTotal changes: ${totalChanges}`);
    }

    this.differences.totalChanges = totalChanges;
  }

  async generateMigrationSQL() {
    logger.info('\nGenerated Migration SQL:');
    logger.info('-'.repeat(60));

    let sql = '-- Auto-generated migration\n\nBEGIN;\n\n';

    // Add columns
    this.differences.columnsAdded.forEach(item => {
      sql += `ALTER TABLE ${item.table} ADD COLUMN ${item.column.name} ${item.column.type}`;
      if (!item.column.nullable) {
        sql += ` NOT NULL`;
      }
      if (item.column.default) {
        sql += ` DEFAULT ${item.column.default}`;
      }
      sql += `;\n`;
    });

    // Remove columns
    this.differences.columnsRemoved.forEach(item => {
      sql += `ALTER TABLE ${item.table} DROP COLUMN ${item.column.name};\n`;
    });

    sql += '\nCOMMIT;\n';

    console.log(sql);

    if (this.getArg('--output')) {
      fs.writeFileSync(this.getArg('--output'), sql);
      logger.success(`Migration SQL written to ${this.getArg('--output')}`);
    }
  }
}

async function main() {
  const differ = new SchemaDiffer();

  try {
    await differ.compare();
  } catch (err) {
    logger.error('Fatal error', err.message);
    process.exit(1);
  }
}

main();
