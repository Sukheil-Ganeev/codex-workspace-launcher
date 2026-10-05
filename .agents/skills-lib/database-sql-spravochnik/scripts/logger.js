/**
 * Simple Logger for Database Scripts
 * Provides colored console output with timestamps
 */

const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  gray: '\x1b[90m',
};

class Logger {
  constructor(level = 'info') {
    this.level = level;
    this.levels = { debug: 0, info: 1, warn: 2, error: 3 };
  }

  timestamp() {
    return new Date().toISOString().replace('T', ' ').slice(0, 19);
  }

  shouldLog(level) {
    return this.levels[level] >= this.levels[this.level];
  }

  log(level, message, data = null) {
    if (!this.shouldLog(level)) return;

    const color = {
      debug: colors.gray,
      info: colors.blue,
      warn: colors.yellow,
      error: colors.red,
    }[level];

    const prefix = `${colors.cyan}[${this.timestamp()}]${colors.reset} ${color}[${level.toUpperCase()}]${colors.reset}`;
    const msg = `${prefix} ${message}`;

    if (data) {
      console.log(msg, typeof data === 'object' ? JSON.stringify(data, null, 2) : data);
    } else {
      console.log(msg);
    }
  }

  debug(message, data) {
    this.log('debug', message, data);
  }

  info(message, data) {
    this.log('info', message, data);
  }

  warn(message, data) {
    this.log('warn', message, data);
  }

  error(message, data) {
    this.log('error', message, data);
  }

  success(message) {
    console.log(`${colors.green}✓ ${message}${colors.reset}`);
  }

  failure(message) {
    console.log(`${colors.red}✗ ${message}${colors.reset}`);
  }

  progress(current, total, label = '') {
    const percent = Math.round((current / total) * 100);
    const filled = Math.round(percent / 5);
    const empty = 20 - filled;
    const bar = '[' + '='.repeat(filled) + ' '.repeat(empty) + ']';
    process.stdout.write(`\r${bar} ${percent}% ${label}`);
  }

  progressEnd() {
    process.stdout.write('\n');
  }
}

module.exports = new Logger();
