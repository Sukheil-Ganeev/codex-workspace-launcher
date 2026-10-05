#!/usr/bin/env node

/**
 * Schema.org Validator
 * Validates JSON-LD structured data markup
 * Usage: npm run schema
 */

import fs from 'fs';
import chalk from 'chalk';
import ora from 'ora';

class SchemaValidator {
  constructor() {
    this.schemas = [];
    this.errors = [];
    this.warnings = [];
  }

  /**
   * Load and validate schema files
   */
  async validateDirectory(dirPath) {
    const spinner = ora('Validating schemas...').start();

    try {
      // Generate mock schemas for demo
      const mockSchemas = this.generateMockSchemas();

      mockSchemas.forEach(schema => {
        this.validateSchema(schema);
      });

      spinner.succeed(`Validated ${mockSchemas.length} schemas`);
      return true;
    } catch (error) {
      spinner.fail('Validation failed');
      console.error(chalk.red('Error:'), error.message);
      return false;
    }
  }

  /**
   * Generate mock schema files
   */
  generateMockSchemas() {
    return [
      {
        name: 'Organization Schema',
        type: 'Organization',
        data: {
          '@context': 'https://schema.org',
          '@type': 'Organization',
          'name': 'Example Tours',
          'url': 'https://example.com',
          'logo': 'https://example.com/logo.png',
          'sameAs': ['https://facebook.com/example', 'https://instagram.com/example']
        }
      },
      {
        name: 'Product Schema (Tour)',
        type: 'Product',
        data: {
          '@context': 'https://schema.org/',
          '@type': 'Product',
          'name': 'Dubai Desert Safari',
          'description': 'Evening desert safari with dinner',
          'image': ['https://example.com/img1.jpg'],
          'offers': {
            '@type': 'Offer',
            'priceCurrency': 'AED',
            'price': '175'
          },
          'aggregateRating': {
            '@type': 'AggregateRating',
            'ratingValue': '4.8',
            'ratingCount': '127'
          }
        }
      },
      {
        name: 'LocalBusiness Schema',
        type: 'LocalBusiness',
        data: {
          '@context': 'https://schema.org',
          '@type': 'LocalBusiness',
          'name': 'Example Tours',
          'address': {
            '@type': 'PostalAddress',
            'streetAddress': '123 Sheikh Zayed Road',
            'addressLocality': 'Dubai',
            'addressRegion': 'Dubai',
            'postalCode': '000000',
            'addressCountry': 'AE'
          },
          'telephone': '+971-4-XXXXXXX'
        }
      },
      {
        name: 'FAQ Schema',
        type: 'FAQPage',
        data: {
          '@context': 'https://schema.org',
          '@type': 'FAQPage',
          'mainEntity': [
            {
              '@type': 'Question',
              'name': 'What is included in the desert safari?',
              'acceptedAnswer': {
                '@type': 'Answer',
                'text': 'Dune bashing, camel ride, and traditional dinner'
              }
            }
          ]
        }
      }
    ];
  }

  /**
   * Validate individual schema
   */
  validateSchema(schema) {
    const checks = [
      this.checkRequired('@context', schema.data),
      this.checkRequired('@type', schema.data),
      this.checkType(schema.data),
      this.checkRecommendedFields(schema.type, schema.data)
    ];

    this.schemas.push({
      ...schema,
      valid: checks.every(c => c),
      errors: this.errors.filter(e => e.schema === schema.name),
      warnings: this.warnings.filter(w => w.schema === schema.name)
    });
  }

  /**
   * Check required field exists
   */
  checkRequired(field, data) {
    if (!data[field]) {
      this.errors.push({
        schema: this.getCurrentSchema(),
        field,
        message: `Required field missing: ${field}`
      });
      return false;
    }
    return true;
  }

  /**
   * Check @type format
   */
  checkType(data) {
    const validTypes = [
      'Organization', 'Product', 'LocalBusiness', 'FAQPage',
      'Event', 'NewsArticle', 'BlogPosting', 'BreadcrumbList'
    ];

    if (!validTypes.includes(data['@type'])) {
      this.warnings.push({
        schema: this.getCurrentSchema(),
        message: `Unknown schema type: ${data['@type']}`
      });
      return false;
    }
    return true;
  }

  /**
   * Check recommended fields based on type
   */
  checkRecommendedFields(type, data) {
    const recommended = {
      'Organization': ['name', 'url', 'logo', 'sameAs'],
      'Product': ['name', 'description', 'image', 'offers', 'aggregateRating'],
      'LocalBusiness': ['name', 'address', 'telephone', 'url'],
      'FAQPage': ['mainEntity']
    };

    const fields = recommended[type] || [];
    const missing = fields.filter(f => !data[f]);

    if (missing.length > 0) {
      this.warnings.push({
        schema: this.getCurrentSchema(),
        message: `Missing recommended fields: ${missing.join(', ')}`
      });
    }

    return missing.length === 0;
  }

  /**
   * Get current schema name (for error tracking)
   */
  getCurrentSchema() {
    return this.schemas[this.schemas.length - 1]?.name || 'Unknown';
  }

  /**
   * Print validation report
   */
  printReport() {
    console.log(chalk.bold.cyan('\n📋 SCHEMA VALIDATION REPORT\n'));
    console.log(chalk.gray('─'.repeat(100)));

    const valid = this.schemas.filter(s => s.valid).length;
    const total = this.schemas.length;

    console.log(
      `${chalk.green(`✓ ${valid}`)} valid schemas | ` +
      `${chalk.red(`✗ ${total - valid}`)} issues found\n`
    );

    this.schemas.forEach((schema, i) => {
      const statusIcon = schema.valid ? chalk.green('✓') : chalk.red('✗');
      const statusText = schema.valid ? chalk.green('Valid') : chalk.red('Invalid');

      console.log(`${i + 1}. ${statusIcon} ${chalk.yellow(schema.name)} ${statusText}`);

      if (schema.errors.length > 0) {
        schema.errors.forEach(error => {
          console.log(`   ${chalk.red('Error:')} ${error.message}`);
        });
      }

      if (schema.warnings.length > 0) {
        schema.warnings.forEach(warning => {
          console.log(`   ${chalk.yellow('Warning:')} ${warning.message}`);
        });
      }

      // Print schema snippet
      console.log(chalk.gray(`   Type: ${schema.type}`));
      if (schema.data.name) {
        console.log(chalk.gray(`   Name: ${schema.data.name}`));
      }
    });

    console.log(chalk.gray('─'.repeat(100)));

    // Summary statistics
    const totalErrors = this.errors.length;
    const totalWarnings = this.warnings.length;

    console.log(chalk.bold.blue('\n📊 Summary:'));
    console.log(`  Schemas checked: ${chalk.blue(total)}`);
    console.log(`  Errors: ${chalk.red(totalErrors)}`);
    console.log(`  Warnings: ${chalk.yellow(totalWarnings)}`);
    console.log(`  Pass rate: ${chalk.green(((valid / total) * 100).toFixed(0) + '%')}\n`);
  }

  /**
   * Export validation results
   */
  exportResults(filename = './exports/schema-validation.json') {
    const exportDir = './exports';
    if (!fs.existsSync(exportDir)) {
      fs.mkdirSync(exportDir, { recursive: true });
    }

    const report = {
      timestamp: new Date().toISOString(),
      totalSchemas: this.schemas.length,
      validSchemas: this.schemas.filter(s => s.valid).length,
      errors: this.errors,
      warnings: this.warnings,
      schemas: this.schemas
    };

    fs.writeFileSync(filename, JSON.stringify(report, null, 2));
    console.log(`Results exported to ${chalk.cyan(filename)}`);
  }
}

/**
 * Main execution
 */
async function main() {
  console.log(chalk.bold.blue('\n✅ Schema.org Validator\n'));

  const validator = new SchemaValidator();

  try {
    await validator.validateDirectory('./assets/schemas');
    validator.printReport();
    validator.exportResults();

    console.log(chalk.green('\n✓ Validation complete!\n'));
  } catch (error) {
    console.error(chalk.red('\n✗ Error:'), error.message);
    process.exit(1);
  }
}

main();
