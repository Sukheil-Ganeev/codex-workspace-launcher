#!/usr/bin/env node

/**
 * Link Checker Script
 * Checks for broken links in HTML files
 * Usage: node test-links.js [options]
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const https = require('https');
const { URL } = require('url');

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
Link Checker Script
===================

Usage: node test-links.js [options]

Options:
  --help          Show this help message
  --path <dir>    Directory to scan (default: ./content)
  --timeout <ms>  Request timeout (default: 5000)
  --external      Check external links (slow)
  --ignore <list> Ignore patterns (comma-separated)
  --verbose       Show detailed output

Examples:
  node test-links.js
  node test-links.js --path ./dist
  node test-links.js --external --timeout 10000
  node test-links.js --ignore "example.com,localhost"
  `, 'cyan');
}

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    help: false,
    path: './content',
    timeout: 5000,
    external: false,
    ignore: '',
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
      case '--timeout':
        options.timeout = parseInt(args[++i]);
        break;
      case '--external':
        options.external = true;
        break;
      case '--ignore':
        options.ignore = args[++i];
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
    return files;
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

function extractLinks(htmlContent, filePath) {
  const links = [];

  // Match href and src attributes
  const hrefRegex = /href=["']([^"']+)["']/g;
  const srcRegex = /src=["']([^"']+)["']/g;

  let match;

  while ((match = hrefRegex.exec(htmlContent)) !== null) {
    links.push({ type: 'href', url: match[1], file: filePath });
  }

  while ((match = srcRegex.exec(htmlContent)) !== null) {
    links.push({ type: 'src', url: match[1], file: filePath });
  }

  return links;
}

function isExternalLink(url) {
  try {
    return url.startsWith('http://') || url.startsWith('https://');
  } catch {
    return false;
  }
}

function isIgnored(url, ignorePatterns) {
  if (!ignorePatterns.length) return false;

  for (const pattern of ignorePatterns) {
    if (url.includes(pattern)) {
      return true;
    }
  }

  return false;
}

function checkInternalLink(url, basePath, options) {
  return new Promise((resolve) => {
    // Remove hash
    const cleanUrl = url.split('#')[0];

    if (!cleanUrl) {
      resolve({ success: true, status: 'anchor', message: 'Anchor link' });
      return;
    }

    // Resolve relative path
    let filePath = path.join(path.dirname(basePath), cleanUrl);

    if (!fs.existsSync(filePath)) {
      // Try without extension
      if (!filePath.endsWith('.html')) {
        filePath = path.join(filePath, 'index.html');
      }
    }

    if (fs.existsSync(filePath)) {
      resolve({ success: true, status: 200, message: 'OK' });
    } else {
      resolve({ success: false, status: 404, message: 'Not found' });
    }
  });
}

function checkExternalLink(url, options) {
  return new Promise((resolve) => {
    const timeout = setTimeout(() => {
      resolve({ success: false, status: 0, message: 'Timeout' });
    }, options.timeout);

    try {
      const protocol = url.startsWith('https') ? https : http;

      protocol.head(url, {
        timeout: options.timeout,
        headers: { 'User-Agent': 'LinkChecker/1.0' }
      }, (res) => {
        clearTimeout(timeout);
        resolve({
          success: res.statusCode < 400,
          status: res.statusCode,
          message: `${res.statusCode} ${res.statusMessage}`
        });
      }).on('error', (error) => {
        clearTimeout(timeout);
        resolve({
          success: false,
          status: 0,
          message: error.message
        });
      });
    } catch (error) {
      clearTimeout(timeout);
      resolve({
        success: false,
        status: 0,
        message: error.message
      });
    }
  });
}

async function checkLink(link, options, ignorePatterns) {
  const { url, file } = link;

  // Check if should ignore
  if (isIgnored(url, ignorePatterns)) {
    return { link, status: 'ignored', message: 'Ignored' };
  }

  // External links
  if (isExternalLink(url)) {
    if (!options.external) {
      return { link, status: 'skipped', message: 'External (skipped)' };
    }
    const result = await checkExternalLink(url, options);
    return { link, ...result };
  }

  // Internal links
  const result = await checkInternalLink(url, file, options);
  return { link, ...result };
}

async function main() {
  const options = parseArgs();

  if (options.help) {
    printHelp();
    process.exit(0);
  }

  print('🔗 Link Checker', 'blue');
  print('='.repeat(50), 'blue');
  print(`📁 Scanning: ${options.path}`, 'cyan');

  if (options.external) {
    print('🌐 External links: ENABLED', 'cyan');
  } else {
    print('🌐 External links: DISABLED (use --external)', 'yellow');
  }

  print('='.repeat(50), 'blue');
  print();

  try {
    if (!fs.existsSync(options.path)) {
      throw new Error(`Directory not found: ${options.path}`);
    }

    const htmlFiles = findHtmlFiles(options.path);

    if (htmlFiles.length === 0) {
      print('⚠️  No HTML files found', 'yellow');
      process.exit(0);
    }

    print(`📄 Found ${htmlFiles.length} HTML file(s)\n`, 'cyan');

    // Extract all links
    const allLinks = [];
    for (const file of htmlFiles) {
      const content = fs.readFileSync(file, 'utf-8');
      const links = extractLinks(content, file);
      allLinks.push(...links);
    }

    if (allLinks.length === 0) {
      print('No links found', 'yellow');
      process.exit(0);
    }

    print(`🔎 Checking ${allLinks.length} link(s)...\n`, 'cyan');

    // Parse ignore patterns
    const ignorePatterns = options.ignore
      .split(',')
      .map(p => p.trim())
      .filter(p => p.length > 0);

    // Check links with progress
    const results = [];
    let processed = 0;

    for (const link of allLinks) {
      process.stdout.write(`[${++processed}/${allLinks.length}] ${link.url} ... `);

      const result = await checkLink(link, options, ignorePatterns);
      results.push(result);

      if (result.success) {
        print('✓', 'green');
      } else if (result.status === 'skipped') {
        print('⊘', 'yellow');
      } else if (result.status === 'ignored') {
        print('⊘', 'cyan');
      } else {
        print(`✗ (${result.message})`, 'red');
      }
    }

    // Summary
    const broken = results.filter(r => !r.success && r.status !== 'skipped' && r.status !== 'ignored');
    const skipped = results.filter(r => r.status === 'skipped');
    const ignored = results.filter(r => r.status === 'ignored');

    print('\n' + '='.repeat(50), 'blue');
    print('📊 Link Check Summary', 'blue');
    print('='.repeat(50), 'blue');
    print(`✓ Valid: ${results.length - broken.length - skipped.length - ignored.length}`, 'green');

    if (skipped.length > 0) {
      print(`⊘ Skipped: ${skipped.length} (external)`, 'yellow');
    }

    if (ignored.length > 0) {
      print(`⊘ Ignored: ${ignored.length}`, 'cyan');
    }

    if (broken.length > 0) {
      print(`✗ Broken: ${broken.length}`, 'red');
      print();

      broken.forEach(result => {
        const file = path.relative('.', result.link.file);
        print(`  ${file}: ${result.link.url} (${result.message})`, 'red');
      });

      process.exit(1);
    } else {
      print(`\n✓ All links are valid!`, 'green');
      process.exit(0);
    }
  } catch (error) {
    print(`\n❌ Error: ${error.message}`, 'red');
    process.exit(1);
  }
}

main();
