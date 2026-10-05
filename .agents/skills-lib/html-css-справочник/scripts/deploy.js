#!/usr/bin/env node

/**
 * Netlify Deployment Script
 * Deploys site to Netlify
 * Usage: node deploy.js [options]
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
  magenta: '\x1b[35m',
};

function print(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function printHelp() {
  print(`
Netlify Deployment Script
==========================

Usage: node deploy.js [options]

Options:
  --help          Show this help message
  --site-id <id>  Netlify Site ID
  --auth <token>  Netlify Auth Token
  --dir <path>    Directory to deploy (default: ./dist)
  --prod          Deploy to production
  --message <msg> Deploy message
  --open          Open deployed site
  --verbose       Show detailed output

Environment Variables:
  NETLIFY_SITE_ID    Netlify Site ID
  NETLIFY_AUTH_TOKEN Netlify Auth Token

Examples:
  node deploy.js --site-id <id> --auth <token>
  node deploy.js --dir ./build --prod --open
  node deploy.js --message "Version 1.0" --verbose
  `, 'cyan');
}

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    help: false,
    siteId: process.env.NETLIFY_SITE_ID || null,
    auth: process.env.NETLIFY_AUTH_TOKEN || null,
    dir: './dist',
    prod: false,
    message: '',
    open: false,
    verbose: false,
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--help':
        options.help = true;
        break;
      case '--site-id':
        options.siteId = args[++i];
        break;
      case '--auth':
        options.auth = args[++i];
        break;
      case '--dir':
        options.dir = args[++i];
        break;
      case '--prod':
        options.prod = true;
        break;
      case '--message':
        options.message = args[++i];
        break;
      case '--open':
        options.open = true;
        break;
      case '--verbose':
        options.verbose = true;
        break;
    }
  }

  return options;
}

function validateConfig(options) {
  const errors = [];

  if (!options.siteId) {
    errors.push('Site ID is required (use --site-id or NETLIFY_SITE_ID env var)');
  }

  if (!options.auth) {
    errors.push('Auth Token is required (use --auth or NETLIFY_AUTH_TOKEN env var)');
  }

  if (!fs.existsSync(options.dir)) {
    errors.push(`Deploy directory not found: ${options.dir}`);
  }

  return errors;
}

function getTotalSize(dir) {
  let size = 0;

  if (!fs.existsSync(dir)) {
    return size;
  }

  const items = fs.readdirSync(dir, { withFileTypes: true });

  for (const item of items) {
    const fullPath = path.join(dir, item.name);

    if (item.isDirectory()) {
      size += getTotalSize(fullPath);
    } else {
      size += fs.statSync(fullPath).size;
    }
  }

  return size;
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i];
}

function countFiles(dir) {
  let count = 0;

  if (!fs.existsSync(dir)) {
    return count;
  }

  const items = fs.readdirSync(dir, { withFileTypes: true });

  for (const item of items) {
    const fullPath = path.join(dir, item.name);

    if (item.isDirectory()) {
      count += countFiles(fullPath);
    } else {
      count++;
    }
  }

  return count;
}

function deployToNetlify(options) {
  try {
    // Check if netlify-cli is installed
    try {
      execSync('npx netlify --version', { stdio: 'pipe' });
    } catch {
      print('❌ netlify-cli is not installed', 'red');
      print('Install with: npm install --save-dev netlify-cli', 'yellow');
      throw new Error('netlify-cli not installed');
    }

    let command = 'npx netlify deploy';

    command += ` --site=${options.siteId}`;
    command += ` --auth=${options.auth}`;
    command += ` --dir="${options.dir}"`;

    if (options.prod) {
      command += ' --prod';
    }

    if (options.message) {
      command += ` --message="${options.message}"`;
    }

    if (!options.verbose) {
      command += ' --json';
    }

    const output = execSync(command, {
      stdio: options.verbose ? 'inherit' : 'pipe',
      encoding: 'utf-8'
    });

    return { success: true, output };
  } catch (error) {
    return { success: false, error: error.message, output: error.stdout };
  }
}

function openDeployedSite(url) {
  try {
    if (process.platform === 'win32') {
      execSync(`start ${url}`);
    } else if (process.platform === 'darwin') {
      execSync(`open ${url}`);
    } else {
      execSync(`xdg-open ${url}`);
    }
    print(`🌐 Opening ${url}`, 'green');
  } catch (error) {
    print(`⚠️  Could not open browser`, 'yellow');
    print(`   Visit: ${url}`, 'cyan');
  }
}

async function main() {
  const options = parseArgs();

  if (options.help) {
    printHelp();
    process.exit(0);
  }

  // Validate configuration
  const errors = validateConfig(options);
  if (errors.length > 0) {
    print('❌ Configuration errors:', 'red');
    errors.forEach(err => print(`  • ${err}`, 'red'));
    print('');
    printHelp();
    process.exit(1);
  }

  const fileCount = countFiles(options.dir);
  const totalSize = getTotalSize(options.dir);

  print('🚀 Netlify Deployment', 'blue');
  print('='.repeat(50), 'blue');
  print(`📁 Directory: ${path.resolve(options.dir)}`, 'cyan');
  print(`📊 Files: ${fileCount}`, 'cyan');
  print(`💾 Size: ${formatBytes(totalSize)}`, 'cyan');

  if (options.prod) {
    print(`🔴 Mode: PRODUCTION`, 'red');
  } else {
    print(`🟡 Mode: Preview`, 'yellow');
  }

  if (options.message) {
    print(`💬 Message: ${options.message}`, 'cyan');
  }

  print('='.repeat(50), 'blue');
  print();

  const startTime = Date.now();

  print('📤 Uploading to Netlify...', 'blue');
  print();

  try {
    const result = deployToNetlify(options);

    if (!result.success) {
      throw new Error(result.error);
    }

    // Parse response
    let deployUrl = 'https://app.netlify.com/';
    let productionUrl = '';

    if (result.output) {
      try {
        const jsonOutput = JSON.parse(result.output);
        deployUrl = jsonOutput.url || deployUrl;
        productionUrl = jsonOutput.deploy_url || '';
      } catch {
        // Not JSON output, try to parse from text
        const urlMatch = result.output.match(/https:\/\/[^\s]+/);
        if (urlMatch) {
          deployUrl = urlMatch[0];
        }
      }
    }

    const duration = ((Date.now() - startTime) / 1000).toFixed(2);

    // Summary
    print('='.repeat(50), 'blue');
    print('✓ Deployment Successful!', 'green');
    print('='.repeat(50), 'blue');

    if (options.prod) {
      print(`🌐 Live URL: ${productionUrl || deployUrl}`, 'green');
    } else {
      print(`🌐 Preview URL: ${deployUrl}`, 'cyan');
    }

    print(`⏱️  Duration: ${duration}s`, 'cyan');
    print();

    if (options.open && deployUrl) {
      openDeployedSite(deployUrl);
    }

    process.exit(0);
  } catch (error) {
    print(`\n❌ Deployment failed: ${error.message}`, 'red');

    if (options.verbose) {
      print('');
      print('Details:', 'yellow');
      print(error.message, 'yellow');
    }

    process.exit(1);
  }
}

main();
