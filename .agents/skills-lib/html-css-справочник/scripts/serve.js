#!/usr/bin/env node

/**
 * Development Server Script
 * Starts a local dev server with live reload
 * Usage: node serve.js [options]
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

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
Development Server Script
==========================

Usage: node serve.js [options]

Options:
  --help          Show this help message
  --port <n>      Server port (default: 8080)
  --root <dir>    Root directory (default: .)
  --open          Open in browser
  --watch         Enable file watching
  --verbose       Show detailed output

Examples:
  node serve.js
  node serve.js --port 3000 --open
  node serve.js --root ./dist --watch
  `, 'cyan');
}

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    help: false,
    port: 8080,
    root: '.',
    open: false,
    watch: false,
    verbose: false,
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--help':
        options.help = true;
        break;
      case '--port':
        options.port = parseInt(args[++i]);
        break;
      case '--root':
        options.root = args[++i];
        break;
      case '--open':
        options.open = true;
        break;
      case '--watch':
        options.watch = true;
        break;
      case '--verbose':
        options.verbose = true;
        break;
    }
  }

  return options;
}

function getMimeType(ext) {
  const mimeTypes = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.ttf': 'font/ttf',
    '.eot': 'application/vnd.ms-fontobject',
  };
  return mimeTypes[ext] || 'application/octet-stream';
}

function serveFile(filePath, res) {
  fs.readFile(filePath, (err, content) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/html' });
      res.end('<h1>404 Not Found</h1>', 'utf-8');
      return;
    }

    const ext = path.extname(filePath);
    const mimeType = getMimeType(ext);

    res.writeHead(200, {
      'Content-Type': mimeType,
      'Cache-Control': 'no-cache',
      'Access-Control-Allow-Origin': '*',
    });
    res.end(content);
  });
}

function createServer(options) {
  const server = http.createServer((req, res) => {
    const pathname = decodeURIComponent(req.url);
    let filePath = path.join(options.root, pathname);

    // If path is directory, serve index.html
    if (filePath.endsWith('/') || !path.extname(filePath)) {
      filePath = path.join(filePath, 'index.html');
    }

    if (options.verbose) {
      print(`${req.method} ${pathname}`, 'cyan');
    }

    serveFile(filePath, res);
  });

  return server;
}

function watchFiles(options, callback) {
  const watchDir = options.root;

  try {
    fs.watch(watchDir, { recursive: true }, (eventType, filename) => {
      if (filename && (filename.endsWith('.html') || filename.endsWith('.css') || filename.endsWith('.js'))) {
        print(`\n📝 File changed: ${filename}`, 'yellow');
        if (callback) callback();
      }
    });
    print('👁️  File watching enabled\n', 'magenta');
  } catch (error) {
    print(`⚠️  File watching error: ${error.message}`, 'yellow');
  }
}

function openBrowser(url) {
  const { execSync } = require('child_process');

  try {
    if (process.platform === 'win32') {
      execSync(`start ${url}`);
    } else if (process.platform === 'darwin') {
      execSync(`open ${url}`);
    } else {
      execSync(`xdg-open ${url}`);
    }
    print(`🌐 Opening ${url} in browser`, 'green');
  } catch (error) {
    print(`⚠️  Could not open browser automatically`, 'yellow');
    print(`   Visit: ${url}`, 'cyan');
  }
}

async function main() {
  const options = parseArgs();

  if (options.help) {
    printHelp();
    process.exit(0);
  }

  // Validate port
  if (isNaN(options.port) || options.port < 1 || options.port > 65535) {
    print(`❌ Invalid port: ${options.port}`, 'red');
    process.exit(1);
  }

  // Check if root directory exists
  if (!fs.existsSync(options.root)) {
    print(`❌ Root directory not found: ${options.root}`, 'red');
    process.exit(1);
  }

  print('🚀 Development Server', 'blue');
  print('='.repeat(50), 'blue');
  print(`📁 Root: ${path.resolve(options.root)}`, 'cyan');
  print(`🌐 URL: http://localhost:${options.port}`, 'cyan');

  if (options.watch) {
    print(`👁️  Watching for changes`, 'magenta');
  }

  print('='.repeat(50), 'blue');
  print('Press Ctrl+C to stop server\n', 'yellow');

  const server = createServer(options);

  server.listen(options.port, '0.0.0.0', () => {
    print(`✓ Server started on http://localhost:${options.port}`, 'green');

    if (options.watch) {
      watchFiles(options, () => {
        print('Server ready for live reload', 'green');
      });
    }

    if (options.open) {
      setTimeout(() => {
        openBrowser(`http://localhost:${options.port}`);
      }, 500);
    }
  });

  server.on('error', (error) => {
    if (error.code === 'EADDRINUSE') {
      print(`\n❌ Port ${options.port} is already in use`, 'red');
      print(`Try another port: node serve.js --port ${options.port + 1}`, 'yellow');
    } else {
      print(`\n❌ Server error: ${error.message}`, 'red');
    }
    process.exit(1);
  });

  // Graceful shutdown
  process.on('SIGINT', () => {
    print('\n\n🛑 Shutting down server...', 'yellow');
    server.close(() => {
      print('✓ Server stopped', 'green');
      process.exit(0);
    });
  });
}

main();
