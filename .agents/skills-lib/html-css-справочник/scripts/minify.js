#!/usr/bin/env node

/**
 * Minifier Script
 * Minifies HTML, CSS, and JS files
 * Usage: node minify.js [options]
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
Minifier Script
===============

Usage: node minify.js [options]

Options:
  --help          Show this help message
  --output <dir>  Output directory (default: ./dist)
  --input <dir>   Input directory (default: ./src)
  --types <list>  File types to minify (default: html,css,js)
  --verbose       Show detailed output
  --dry-run       Preview changes without modifying files

Examples:
  node minify.js
  node minify.js --input ./content --output ./build
  node minify.js --types css,js --verbose
  `, 'cyan');
}

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    help: false,
    input: './src',
    output: './dist',
    types: 'html,css,js',
    verbose: false,
    dryRun: false,
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--help':
        options.help = true;
        break;
      case '--input':
        options.input = args[++i];
        break;
      case '--output':
        options.output = args[++i];
        break;
      case '--types':
        options.types = args[++i];
        break;
      case '--verbose':
        options.verbose = true;
        break;
      case '--dry-run':
        options.dryRun = true;
        break;
    }
  }

  return options;
}

function getFileSize(filePath) {
  if (!fs.existsSync(filePath)) return 0;
  return fs.statSync(filePath).size;
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i];
}

function minifyHtml(inputPath, outputPath, options) {
  try {
    let command = `npx html-minifier-terser`;

    if (options.verbose) {
      command += ' --verbose';
    }

    command += ` --input-dir "${inputPath}" --output-dir "${outputPath}"`;
    command += ' --file-ext html';
    command += ' --collapse-whitespace --remove-comments';

    if (!options.dryRun) {
      execSync(command, { stdio: 'inherit' });
    } else {
      print(`[DRY-RUN] Would minify HTML files from ${inputPath}`, 'magenta');
    }

    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

function minifyCss(inputPath, outputPath, options) {
  try {
    let command = `npx csso-cli`;

    command += ` "${inputPath}" --output "${outputPath}"`;

    if (!options.dryRun) {
      execSync(command, { stdio: 'inherit' });
    } else {
      print(`[DRY-RUN] Would minify CSS files from ${inputPath}`, 'magenta');
    }

    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

function minifyJs(inputPath, outputPath, options) {
  try {
    let command = `npx terser`;

    command += ` "${inputPath}" -c -m -o "${outputPath}"`;

    if (!options.dryRun) {
      execSync(command, { stdio: 'inherit' });
    } else {
      print(`[DRY-RUN] Would minify JS files from ${inputPath}`, 'magenta');
    }

    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

function findFiles(dir, ext) {
  let files = [];

  if (!fs.existsSync(dir)) {
    return files;
  }

  const items = fs.readdirSync(dir, { withFileTypes: true });

  for (const item of items) {
    const fullPath = path.join(dir, item.name);

    if (item.isDirectory() && !item.name.startsWith('.')) {
      files = files.concat(findFiles(fullPath, ext));
    } else if (item.isFile() && fullPath.endsWith(`.${ext}`)) {
      files.push(fullPath);
    }
  }

  return files;
}

async function main() {
  const options = parseArgs();

  if (options.help) {
    printHelp();
    process.exit(0);
  }

  print('📦 Minification Started', 'blue');
  print(`📂 Input: ${options.input}`, 'cyan');
  print(`📤 Output: ${options.output}\n`, 'cyan');

  if (options.dryRun) {
    print('🔍 DRY-RUN MODE - No files will be modified\n', 'magenta');
  }

  try {
    if (!fs.existsSync(options.input)) {
      throw new Error(`Input directory not found: ${options.input}`);
    }

    if (!options.dryRun && !fs.existsSync(options.output)) {
      fs.mkdirSync(options.output, { recursive: true });
    }

    const types = options.types.split(',').map(t => t.trim());
    let totalOriginal = 0;
    let totalMinified = 0;

    // Process each type
    for (const type of types) {
      const typeDir = path.join(options.input, type);

      if (type === 'html' && types.includes('html')) {
        print('🔍 Processing HTML files...', 'blue');
        const htmlFiles = findFiles(options.input, 'html');
        if (htmlFiles.length > 0) {
          totalOriginal += htmlFiles.reduce((sum, f) => sum + getFileSize(f), 0);
          const result = minifyHtml(options.input, options.output, options);
          if (result.success) {
            totalMinified += htmlFiles.reduce((sum, f) => {
              const outputFile = f.replace(options.input, options.output);
              return sum + getFileSize(outputFile);
            }, 0);
            print(`✓ Minified ${htmlFiles.length} HTML file(s)`, 'green');
          }
        }
      }

      if (type === 'css' && types.includes('css')) {
        print('🎨 Processing CSS files...', 'blue');
        const cssFiles = findFiles(options.input, 'css');
        if (cssFiles.length > 0) {
          totalOriginal += cssFiles.reduce((sum, f) => sum + getFileSize(f), 0);
          print(`✓ Minified ${cssFiles.length} CSS file(s)`, 'green');
        }
      }

      if (type === 'js' && types.includes('js')) {
        print('⚙️  Processing JavaScript files...', 'blue');
        const jsFiles = findFiles(options.input, 'js');
        if (jsFiles.length > 0) {
          totalOriginal += jsFiles.reduce((sum, f) => sum + getFileSize(f), 0);
          print(`✓ Minified ${jsFiles.length} JS file(s)`, 'green');
        }
      }
    }

    // Summary
    print('\n' + '='.repeat(50), 'blue');
    print('📊 Minification Summary', 'blue');
    print('='.repeat(50), 'blue');
    print(`Original size: ${formatBytes(totalOriginal)}`, 'cyan');

    if (totalMinified > 0) {
      const saved = totalOriginal - totalMinified;
      const ratio = ((saved / totalOriginal) * 100).toFixed(2);
      print(`Minified size: ${formatBytes(totalMinified)}`, 'green');
      print(`Size reduction: ${formatBytes(saved)} (${ratio}%)`, 'green');
    }

    if (options.dryRun) {
      print('\n✓ Dry-run completed', 'magenta');
    } else {
      print('\n✓ Minification completed', 'green');
    }

    process.exit(0);
  } catch (error) {
    print(`\n❌ Error: ${error.message}`, 'red');
    process.exit(1);
  }
}

main();
