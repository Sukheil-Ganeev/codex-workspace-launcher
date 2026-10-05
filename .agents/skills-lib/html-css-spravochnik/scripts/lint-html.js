#!/usr/bin/env node

/**
 * HTML Validator Script
 * Validates HTML files using html-validate
 * Usage: node lint-html.js [options]
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Color codes for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function print(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function printHelp() {
  print(`
HTML Validator Script
=====================

Usage: node lint-html.js [options]

Options:
  --help          Show this help message
  --path <dir>    Directory to scan (default: ./content)
  --fix           Auto-fix issues where possible
  --strict        Strict mode - fail on warnings
  --config <file> Custom config file path
  --verbose       Show detailed output

Examples:
  node lint-html.js
  node lint-html.js --path ./src --fix
  node lint-html.js --strict --verbose
  `, 'cyan');
}

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    help: false,
    path: './content',
    fix: false,
    strict: false,
    config: null,
    verbose: false,
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--help':
        options.help = true;
        break;
      case '--path':
        options.path = args[++i];
        break;
      case '--fix':
        options.fix = true;
        break;
      case '--strict':
        options.strict = true;
        break;
      case '--config':
        options.config = args[++i];
        break;
      case '--verbose':
        options.verbose = true;
        break;
    }
  }

  return options;
}

function findHtmlFiles(dir) {
  let files = [];

  if (!fs.existsSync(dir)) {
    throw new Error(`Directory not found: ${dir}`);
  }

  const items = fs.readdirSync(dir, { withFileTypes: true });

  for (const item of items) {
    const fullPath = path.join(dir, item.name);

    if (item.isDirectory() && !item.name.startsWith('.')) {
      files = files.concat(findHtmlFiles(fullPath));
    } else if (item.isFile() && item.name.endsWith('.html')) {
      files.push(fullPath);
    }
  }

  return files;
}

function validateHtmlFile(filePath, options) {
  try {
    let command = `npx html-validate "${filePath}"`;

    if (options.config) {
      command += ` --config "${options.config}"`;
    }

    if (options.fix) {
      command += ' --fix';
    }

    if (options.verbose) {
      command += ' --formatter json';
    }

    execSync(command, { stdio: 'pipe' });
    return { success: true, errors: 0, warnings: 0 };
  } catch (error) {
    const output = error.stdout ? error.stdout.toString() : error.message;

    // Parse error count from output
    const errorMatch = output.match(/(\d+)\s+error/);
    const warningMatch = output.match(/(\d+)\s+warning/);

    return {
      success: false,
      errors: errorMatch ? parseInt(errorMatch[1]) : 1,
      warnings: warningMatch ? parseInt(warningMatch[1]) : 0,
      output: output,
    };
  }
}

async function main() {
  const options = parseArgs();

  if (options.help) {
    printHelp();
    process.exit(0);
  }

  print('🔍 HTML Validation Started', 'blue');
  print(`📁 Scanning: ${options.path}\n`, 'cyan');

  try {
    // Check if html-validate is installed
    try {
      execSync('npx html-validate --version', { stdio: 'pipe' });
    } catch {
      print('❌ html-validate is not installed', 'red');
      print('Install it with: npm install --save-dev html-validate', 'yellow');
      process.exit(1);
    }

    const htmlFiles = findHtmlFiles(options.path);

    if (htmlFiles.length === 0) {
      print('⚠️  No HTML files found', 'yellow');
      process.exit(0);
    }

    print(`📄 Found ${htmlFiles.length} HTML file(s)\n`, 'cyan');

    let totalErrors = 0;
    let totalWarnings = 0;
    const results = [];

    // Validate each file with progress
    htmlFiles.forEach((file, index) => {
      const relative = path.relative('.', file);
      process.stdout.write(`[${index + 1}/${htmlFiles.length}] ${relative} ... `);

      const result = validateHtmlFile(file, options);
      results.push({ file: relative, ...result });

      if (result.success) {
        print('✓', 'green');
      } else {
        print(`✗ (${result.errors} errors, ${result.warnings} warnings)`, 'red');
        totalErrors += result.errors;
        totalWarnings += result.warnings;

        if (options.verbose && result.output) {
          print(result.output, 'yellow');
        }
      }
    });

    // Summary
    print('\n' + '='.repeat(50), 'blue');
    print('📊 Validation Summary', 'blue');
    print('='.repeat(50), 'blue');

    if (totalErrors === 0 && totalWarnings === 0) {
      print('✓ All files are valid!', 'green');
      process.exit(0);
    } else {
      if (totalErrors > 0) {
        print(`❌ Errors: ${totalErrors}`, 'red');
      }
      if (totalWarnings > 0) {
        print(`⚠️  Warnings: ${totalWarnings}`, 'yellow');
      }

      if (options.strict && (totalErrors > 0 || totalWarnings > 0)) {
        print('\nStrict mode enabled - failing on errors/warnings', 'red');
        process.exit(1);
      } else if (totalErrors > 0) {
        process.exit(1);
      } else {
        process.exit(0);
      }
    }
  } catch (error) {
    print(`\n❌ Error: ${error.message}`, 'red');
    process.exit(1);
  }
}

main();
