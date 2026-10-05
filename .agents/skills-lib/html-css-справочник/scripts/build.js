#!/usr/bin/env node

/**
 * Production Build Script
 * Builds optimized production files
 * Usage: node build.js [options]
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
Production Build Script
=======================

Usage: node build.js [options]

Options:
  --help          Show this help message
  --input <dir>   Input directory (default: ./src)
  --output <dir>  Output directory (default: ./dist)
  --minify        Minify output files
  --optimize-img  Optimize images
  --source-maps   Generate source maps
  --verbose       Show detailed output
  --clean         Clean output directory before build

Examples:
  node build.js
  node build.js --input ./content --output ./build
  node build.js --minify --optimize-img --clean
  `, 'cyan');
}

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    help: false,
    input: './src',
    output: './dist',
    minify: false,
    optimizeImg: false,
    sourceMaps: false,
    verbose: false,
    clean: false,
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
      case '--minify':
        options.minify = true;
        break;
      case '--optimize-img':
        options.optimizeImg = true;
        break;
      case '--source-maps':
        options.sourceMaps = true;
        break;
      case '--verbose':
        options.verbose = true;
        break;
      case '--clean':
        options.clean = true;
        break;
    }
  }

  return options;
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i];
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

function cleanDirectory(dir) {
  if (!fs.existsSync(dir)) {
    return;
  }

  try {
    fs.rmSync(dir, { recursive: true, force: true });
    print(`✓ Cleaned output directory`, 'green');
  } catch (error) {
    print(`⚠️  Could not clean directory: ${error.message}`, 'yellow');
  }
}

function copyDirectory(src, dest) {
  if (!fs.existsSync(src)) {
    throw new Error(`Source directory not found: ${src}`);
  }

  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }

  const items = fs.readdirSync(src, { withFileTypes: true });

  for (const item of items) {
    const srcPath = path.join(src, item.name);
    const destPath = path.join(dest, item.name);

    if (item.isDirectory() && !item.name.startsWith('.') && item.name !== 'node_modules') {
      copyDirectory(srcPath, destPath);
    } else if (item.isFile()) {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function lintFiles(dir, options) {
  print('🔍 Linting HTML files...', 'blue');

  try {
    execSync(`npx html-validate "${dir}" --ext html`, { stdio: 'pipe' });
    print('✓ HTML validation passed', 'green');
  } catch (error) {
    print('⚠️  HTML validation warnings', 'yellow');
    if (options.verbose) {
      print(error.stdout.toString(), 'yellow');
    }
  }

  print('🎨 Linting CSS files...', 'blue');

  try {
    execSync(`npx stylelint "${dir}/**/*.css"`, { stdio: 'pipe' });
    print('✓ CSS validation passed', 'green');
  } catch (error) {
    print('⚠️  CSS validation warnings', 'yellow');
    if (options.verbose) {
      print(error.stdout.toString(), 'yellow');
    }
  }
}

function minifyFiles(dir, options) {
  print('📦 Minifying files...', 'blue');

  try {
    // HTML
    execSync(`npx html-minifier-terser --input-dir "${dir}" --output-dir "${dir}" --file-ext html --collapse-whitespace --remove-comments`, { stdio: 'pipe' });
    print('✓ Minified HTML', 'green');
  } catch (error) {
    print('⚠️  HTML minification completed with warnings', 'yellow');
  }

  try {
    // CSS
    const cssFiles = findFilesByExt(dir, '.css');
    for (const file of cssFiles) {
      execSync(`npx csso-cli "${file}" -o "${file}"`, { stdio: 'pipe' });
    }
    print('✓ Minified CSS', 'green');
  } catch (error) {
    print('⚠️  CSS minification completed with warnings', 'yellow');
  }
}

function optimizeImages(dir, options) {
  print('🖼️  Optimizing images...', 'blue');

  try {
    execSync(`npx imagemin "${dir}/**/*.{jpg,png,gif}" --out-dir="${dir}" --plugin=mozjpeg --plugin=pngquant`, { stdio: 'pipe' });
    print('✓ Optimized images', 'green');
  } catch (error) {
    print('⚠️  Image optimization completed with warnings', 'yellow');
  }
}

function findFilesByExt(dir, ext) {
  let files = [];

  if (!fs.existsSync(dir)) {
    return files;
  }

  const items = fs.readdirSync(dir, { withFileTypes: true });

  for (const item of items) {
    const fullPath = path.join(dir, item.name);

    if (item.isDirectory() && !item.name.startsWith('.')) {
      files = files.concat(findFilesByExt(fullPath, ext));
    } else if (item.isFile() && fullPath.endsWith(ext)) {
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

  const startTime = Date.now();
  const inputSize = getTotalSize(options.input);

  print('🏗️  Production Build', 'blue');
  print('='.repeat(50), 'blue');
  print(`📁 Input: ${options.input}`, 'cyan');
  print(`📤 Output: ${options.output}`, 'cyan');
  print(`💾 Input size: ${formatBytes(inputSize)}`, 'cyan');
  print('='.repeat(50), 'blue');
  print();

  try {
    // Validation
    if (!fs.existsSync(options.input)) {
      throw new Error(`Input directory not found: ${options.input}`);
    }

    // Clean
    if (options.clean) {
      print('🧹 Cleaning output directory...', 'blue');
      cleanDirectory(options.output);
    }

    // Copy files
    print('📋 Copying files...', 'blue');
    copyDirectory(options.input, options.output);
    print('✓ Files copied', 'green');
    print();

    // Lint
    print('🔍 Validation', 'magenta');
    lintFiles(options.output, options);
    print();

    // Minify
    if (options.minify) {
      print('📦 Optimization', 'magenta');
      minifyFiles(options.output, options);
      print();
    }

    // Optimize images
    if (options.optimizeImg) {
      print('🖼️  Image Optimization', 'magenta');
      optimizeImages(options.output, options);
      print();
    }

    // Final stats
    const outputSize = getTotalSize(options.output);
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);

    print('='.repeat(50), 'blue');
    print('📊 Build Summary', 'blue');
    print('='.repeat(50), 'blue');
    print(`✓ Output size: ${formatBytes(outputSize)}`, 'green');

    if (options.minify && inputSize > outputSize) {
      const saved = inputSize - outputSize;
      const ratio = ((saved / inputSize) * 100).toFixed(2);
      print(`📉 Size reduction: ${formatBytes(saved)} (${ratio}%)`, 'green');
    }

    print(`⏱️  Build time: ${duration}s`, 'cyan');
    print(`✓ Build completed successfully!`, 'green');

    process.exit(0);
  } catch (error) {
    print(`\n❌ Build failed: ${error.message}`, 'red');
    process.exit(1);
  }
}

main();
