#!/usr/bin/env node

/**
 * CSS Validator Script
 * Validates CSS files using stylelint
 * Usage: node lint-css.js [options]
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Color codes
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
CSS Validator Script (stylelint)
================================

Usage: node lint-css.js [options]

Options:
  --help          Show this help message
  --path <dir>    Directory to scan (default: ./styles)
  --fix           Auto-fix issues where possible
  --strict        Fail on warnings (not just errors)
  --config <file> Custom stylelint config
  --verbose       Show detailed output
  --pattern <pat> File pattern (default: **/*.css)

Examples:
  node lint-css.js
  node lint-css.js --path ./src/styles --fix
  node lint-css.js --strict --verbose
  `, 'cyan');
}

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    help: false,
    path: './styles',
    fix: false,
    strict: false,
    config: null,
    verbose: false,
    pattern: '**/*.css',
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
      case '--pattern':
        options.pattern = args[++i];
        break;
    }
  }

  return options;
}

function findCssFiles(dir) {
  let files = [];

  if (!fs.existsSync(dir)) {
    throw new Error(`Directory not found: ${dir}`);
  }

  const items = fs.readdirSync(dir, { withFileTypes: true });

  for (const item of items) {
    const fullPath = path.join(dir, item.name);

    if (item.isDirectory() && !item.name.startsWith('.')) {
      files = files.concat(findCssFiles(fullPath));
    } else if (item.isFile() && item.name.endsWith('.css')) {
      files.push(fullPath);
    }
  }

  return files;
}

function lintCssFile(filePath, options) {
  try {
    let command = `npx stylelint "${filePath}"`;

    if (options.config) {
      command += ` --config "${options.config}"`;
    }

    if (options.fix) {
      command += ' --fix';
    }

    if (options.verbose) {
      command += ' --formatter verbose';
    } else {
      command += ' --formatter compact';
    }

    execSync(command, { stdio: 'pipe' });
    return { success: true, errors: 0, warnings: 0 };
  } catch (error) {
    const output = error.stdout ? error.stdout.toString() : error.message;

    // Parse error/warning info
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

  print('🎨 CSS Validation Started', 'blue');
  print(`📁 Scanning: ${options.path}\n`, 'cyan');

  try {
    // Check if stylelint is installed
    try {
      execSync('npx stylelint --version', { stdio: 'pipe' });
    } catch {
      print('❌ stylelint is not installed', 'red');
      print('Install it with: npm install --save-dev stylelint stylelint-config-standard', 'yellow');
      process.exit(1);
    }

    const cssFiles = findCssFiles(options.path);

    if (cssFiles.length === 0) {
      print('⚠️  No CSS files found', 'yellow');
      process.exit(0);
    }

    print(`📄 Found ${cssFiles.length} CSS file(s)\n`, 'cyan');

    let totalErrors = 0;
    let totalWarnings = 0;

    // Lint each file with progress
    cssFiles.forEach((file, index) => {
      const relative = path.relative('.', file);
      process.stdout.write(`[${index + 1}/${cssFiles.length}] ${relative} ... `);

      const result = lintCssFile(file, options);

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
    print('📊 Linting Summary', 'blue');
    print('='.repeat(50), 'blue');

    if (totalErrors === 0 && totalWarnings === 0) {
      print('✓ All CSS files are valid!', 'green');
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
