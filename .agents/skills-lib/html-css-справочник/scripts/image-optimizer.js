#!/usr/bin/env node

/**
 * Image Optimizer Script
 * Compresses and optimizes images using imagemin
 * Usage: node image-optimizer.js [options]
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
Image Optimizer Script
======================

Usage: node image-optimizer.js [options]

Options:
  --help          Show this help message
  --input <dir>   Input directory (default: ./images)
  --output <dir>  Output directory (default: ./images-optimized)
  --quality <n>   JPEG quality 0-100 (default: 80)
  --progressive   Save progressive JPEGs
  --webp          Also create WebP versions
  --verbose       Show detailed output

Examples:
  node image-optimizer.js
  node image-optimizer.js --input ./assets/images --output ./dist/images
  node image-optimizer.js --quality 90 --webp --verbose
  `, 'cyan');
}

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    help: false,
    input: './images',
    output: './images-optimized',
    quality: 80,
    progressive: false,
    webp: false,
    verbose: false,
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
      case '--quality':
        options.quality = parseInt(args[++i]);
        break;
      case '--progressive':
        options.progressive = true;
        break;
      case '--webp':
        options.webp = true;
        break;
      case '--verbose':
        options.verbose = true;
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

function getFileSize(filePath) {
  if (!fs.existsSync(filePath)) return 0;
  return fs.statSync(filePath).size;
}

function findImages(dir) {
  let images = [];
  const extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg'];

  if (!fs.existsSync(dir)) {
    return images;
  }

  const items = fs.readdirSync(dir, { withFileTypes: true });

  for (const item of items) {
    const fullPath = path.join(dir, item.name);

    if (item.isDirectory() && !item.name.startsWith('.') && item.name !== 'node_modules') {
      images = images.concat(findImages(fullPath));
    } else if (item.isFile()) {
      const ext = path.extname(item.name).toLowerCase();
      if (extensions.includes(ext)) {
        images.push(fullPath);
      }
    }
  }

  return images;
}

function optimizeImages(images, options) {
  const results = {
    processed: 0,
    failed: 0,
    totalOriginal: 0,
    totalOptimized: 0,
    errors: [],
  };

  images.forEach((imagePath, index) => {
    const relative = path.relative('.', imagePath);
    const originalSize = getFileSize(imagePath);
    results.totalOriginal += originalSize;

    process.stdout.write(`[${index + 1}/${images.length}] ${relative} ... `);

    try {
      const ext = path.extname(imagePath).toLowerCase();
      const basename = path.basename(imagePath, ext);
      const dirname = path.dirname(imagePath).replace(options.input, options.output);

      // Create output directory
      if (!fs.existsSync(dirname)) {
        fs.mkdirSync(dirname, { recursive: true });
      }

      const outputPath = path.join(dirname, path.basename(imagePath));

      let command = `npx imagemin "${imagePath}" --out-dir="${dirname}"`;

      if (ext === '.jpg' || ext === '.jpeg') {
        command += ` --plugin=mozjpeg --plugin.quality=${options.quality}`;
        if (options.progressive) {
          command += ' --plugin.progressive=true';
        }
      } else if (ext === '.png') {
        command += ' --plugin=pngquant';
      }

      execSync(command, { stdio: 'pipe' });

      const optimizedSize = getFileSize(outputPath);
      results.totalOptimized += optimizedSize;

      const saved = originalSize - optimizedSize;
      const ratio = originalSize > 0 ? ((saved / originalSize) * 100).toFixed(1) : 0;

      print(`✓ (${formatBytes(original)} → ${formatBytes(optimizedSize)}, -${ratio}%)`, 'green');
      results.processed++;

      // Create WebP version if requested
      if (options.webp && (ext === '.jpg' || ext === '.jpeg' || ext === '.png')) {
        const webpPath = path.join(dirname, `${basename}.webp`);
        const webpCommand = `npx imagemin "${imagePath}" --out-dir="${dirname}" --plugin=webp`;
        execSync(webpCommand, { stdio: 'pipe' });

        const webpSize = getFileSize(webpPath);
        results.totalOptimized += webpSize;

        if (options.verbose) {
          print(`   WebP: ${formatBytes(webpSize)}`, 'cyan');
        }
      }
    } catch (error) {
      print(`✗ (${error.message})`, 'red');
      results.failed++;
      results.errors.push({ file: relative, error: error.message });
    }
  });

  return results;
}

async function main() {
  const options = parseArgs();

  if (options.help) {
    printHelp();
    process.exit(0);
  }

  print('🖼️  Image Optimizer Started', 'blue');
  print(`📁 Input: ${options.input}`, 'cyan');
  print(`📤 Output: ${options.output}`, 'cyan');
  print(`⚙️  Quality: ${options.quality}%\n`, 'cyan');

  try {
    // Check if imagemin is installed
    try {
      execSync('npx imagemin --version', { stdio: 'pipe' });
    } catch {
      print('❌ imagemin is not installed', 'red');
      print('Install with: npm install --save-dev imagemin imagemin-mozjpeg imagemin-pngquant', 'yellow');
      process.exit(1);
    }

    const images = findImages(options.input);

    if (images.length === 0) {
      print('⚠️  No images found', 'yellow');
      process.exit(0);
    }

    print(`📄 Found ${images.length} image(s)\n`, 'cyan');

    const results = optimizeImages(images, options);

    // Summary
    print('\n' + '='.repeat(50), 'blue');
    print('📊 Optimization Summary', 'blue');
    print('='.repeat(50), 'blue');
    print(`✓ Processed: ${results.processed}`, 'green');
    if (results.failed > 0) {
      print(`✗ Failed: ${results.failed}`, 'red');
    }
    print(`Original size: ${formatBytes(results.totalOriginal)}`, 'cyan');
    print(`Optimized size: ${formatBytes(results.totalOptimized)}`, 'green');

    if (results.totalOriginal > 0) {
      const saved = results.totalOriginal - results.totalOptimized;
      const ratio = ((saved / results.totalOriginal) * 100).toFixed(2);
      print(`Size reduction: ${formatBytes(saved)} (${ratio}%)`, 'green');
    }

    if (results.errors.length > 0 && options.verbose) {
      print('\nErrors:', 'red');
      results.errors.forEach(err => {
        print(`  ${err.file}: ${err.error}`, 'yellow');
      });
    }

    process.exit(results.failed > 0 ? 1 : 0);
  } catch (error) {
    print(`\n❌ Error: ${error.message}`, 'red');
    process.exit(1);
  }
}

main();
