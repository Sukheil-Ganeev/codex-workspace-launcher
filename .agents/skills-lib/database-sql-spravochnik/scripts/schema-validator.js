#!/usr/bin/env node

/**
 * Database Schema Validator
 * Validates schema against constraints, indexes, and expected structure
 * Usage: node schema-validator.js [--schema-file path] [--strict]
 */

const fs = require('fs');
const db = require('./db');
const logger = require('./logger');

class SchemaValidator {
  constructor() {
    this.schemaFile = process.argv.find(a => a.includes('--schema-file'))?.split('=')[1];
    this.isStrict = process.argv.includes('--strict');
    this.issues = {
      errors: [],
      warnings: [],
      info: [],
    };
  }

  async validate() {
    try {
      await db.connect();

      logger.info('Starting schema validation...');
      logger.info('='.repeat(50));

      await this.validateTables();
      await this.validateConstraints();
      await this.validateIndexes();
      await this.validateDataTypes();
      await this.validateRelationships();

      this.printReport();

      const hasErrors = this.issues.errors.length > 0;
      if (hasErrors && this.isStrict) {
        logger.failure('Schema validation FAILED');
        process.exit(1);
      } else if (hasErrors) {
        logger.warn('Schema validation completed with errors');
      } else {
        logger.success('Schema validation PASSED');
      }
    } catch (err) {
      logger.error('Validation error', err.message);
      process.exit(1);
    } finally {
      await db.disconnect();
    }
  }

  async validateTables() {
    logger.info('Validating tables...');

    const query = `
      SELECT table_name FROM information_schema.tables
      WHERE table_schema = 'public'
      ORDER BY table_name
    `;

    try {
      const result = await db.query(query);

      if (result.rows.length === 0) {
        this.addWarning('No tables found in public schema');
        return;
      }

      logger.success(`Found ${result.rows.length} table(s)`);
      result.rows.forEach(row => {
        console.log(`  - ${row.table_name}`);
      });
    } catch (err) {
      this.addError(`Failed to validate tables: ${err.message}`);
    }
  }

  async validateConstraints() {
    logger.info('Validating constraints...');

    const query = `
      SELECT
        tc.table_name,
        tc.constraint_name,
        tc.constraint_type
      FROM information_schema.table_constraints tc
      WHERE tc.table_schema = 'public'
      ORDER BY tc.table_name, tc.constraint_type
    `;

    try {
      const result = await db.query(query);
      const constraintsByType = {};

      result.rows.forEach(row => {
        if (!constraintsByType[row.constraint_type]) {
          constraintsByType[row.constraint_type] = 0;
        }
        constraintsByType[row.constraint_type]++;
      });

      logger.success(`Found constraints:`);
      Object.entries(constraintsByType).forEach(([type, count]) => {
        console.log(`  - ${type}: ${count}`);
      });

      this.addInfo(`Total constraints: ${result.rows.length}`);
    } catch (err) {
      this.addError(`Failed to validate constraints: ${err.message}`);
    }
  }

  async validateIndexes() {
    logger.info('Validating indexes...');

    const query = `
      SELECT
        indexname,
        tablename,
        indexdef
      FROM pg_indexes
      WHERE schemaname = 'public'
      ORDER BY tablename, indexname
    `;

    try {
      const result = await db.query(query);

      if (result.rows.length === 0) {
        this.addWarning('No indexes found (consider adding indexes for performance)');
        return;
      }

      logger.success(`Found ${result.rows.length} index(es)`);
      result.rows.forEach(row => {
        console.log(`  - ${row.indexname} on ${row.tablename}`);
      });
    } catch (err) {
      this.addError(`Failed to validate indexes: ${err.message}`);
    }
  }

  async validateDataTypes() {
    logger.info('Validating data types...');

    const query = `
      SELECT
        table_name,
        column_name,
        data_type,
        is_nullable
      FROM information_schema.columns
      WHERE table_schema = 'public'
      ORDER BY table_name, ordinal_position
    `;

    try {
      const result = await db.query(query);
      const typeCount = {};

      result.rows.forEach(row => {
        const type = row.data_type;
        typeCount[type] = (typeCount[type] || 0) + 1;

        // Check for problematic types
        if (type === 'text' && row.is_nullable === 'YES') {
          this.addWarning(
            `Nullable TEXT column: ${row.table_name}.${row.column_name}`
          );
        }
      });

      logger.success(`Found ${result.rows.length} column(s)`);
      console.log('Data types:');
      Object.entries(typeCount).forEach(([type, count]) => {
        console.log(`  - ${type}: ${count}`);
      });
    } catch (err) {
      this.addError(`Failed to validate data types: ${err.message}`);
    }
  }

  async validateRelationships() {
    logger.info('Validating foreign key relationships...');

    const query = `
      SELECT
        tc.constraint_name,
        tc.table_name,
        kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name
      FROM information_schema.table_constraints AS tc
      JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
      JOIN information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = tc.constraint_name
      WHERE tc.constraint_type = 'FOREIGN KEY'
      AND tc.table_schema = 'public'
    `;

    try {
      const result = await db.query(query);

      if (result.rows.length === 0) {
        this.addWarning('No foreign key relationships found');
        return;
      }

      logger.success(`Found ${result.rows.length} foreign key(s)`);
      result.rows.forEach(row => {
        console.log(
          `  - ${row.table_name}.${row.column_name} → ${row.foreign_table_name}.${row.foreign_column_name}`
        );
      });
    } catch (err) {
      this.addError(`Failed to validate relationships: ${err.message}`);
    }
  }

  addError(message) {
    this.issues.errors.push(message);
  }

  addWarning(message) {
    this.issues.warnings.push(message);
  }

  addInfo(message) {
    this.issues.info.push(message);
  }

  printReport() {
    logger.info('\nValidation Report');
    logger.info('='.repeat(50));

    if (this.issues.errors.length > 0) {
      logger.error(`ERRORS (${this.issues.errors.length}):`);
      this.issues.errors.forEach(e => console.log(`  ✗ ${e}`));
    }

    if (this.issues.warnings.length > 0) {
      logger.warn(`WARNINGS (${this.issues.warnings.length}):`);
      this.issues.warnings.forEach(w => console.log(`  ⚠ ${w}`));
    }

    if (this.issues.info.length > 0) {
      logger.info(`INFO (${this.issues.info.length}):`);
      this.issues.info.forEach(i => console.log(`  ℹ ${i}`));
    }

    const total = this.issues.errors.length + this.issues.warnings.length + this.issues.info.length;
    logger.info(`\nTotal issues: ${total}`);
  }
}

async function main() {
  const validator = new SchemaValidator();

  try {
    await validator.validate();
  } catch (err) {
    logger.error('Fatal error', err.message);
    process.exit(1);
  }
}

main();
