#!/usr/bin/env node

/**
 * dev-server.js - Development Server with Hot Reload
 * Локальный сервер с автоперезагрузкой при изменении файлов
 *
 * Использование:
 *   npm run dev           # Запустить dev сервер
 *   npm run dev -- --port 4000  # На другом порту
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const chalk = require('chalk');
require('dotenv').config();

const args = process.argv.slice(2);

// Help текст
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
${chalk.bold('Development Server with Hot Reload')}

Использование:
  ${chalk.cyan('node scripts/dev-server.js [options]')}

Опции:
  --help, -h          Показать этот текст
  --port <port>       Порт сервера (по умолчанию 3000)
  --host <host>       Host (по умолчанию localhost)
  --proxy <url>       Прокси для API запросов
  --https             Использовать HTTPS (требует certs)
  --watch             Директории для мониторинга

Примеры:
  ${chalk.cyan('node scripts/dev-server.js')}                  # На порту 3000
  ${chalk.cyan('node scripts/dev-server.js --port 4000')}     # На порту 4000
  ${chalk.cyan('node scripts/dev-server.js --host 0.0.0.0')}  # На всех интерфейсах
  `);
  process.exit(0);
}

// Парсим аргументы
const getArgValue = (flag) => {
  const index = args.indexOf(flag);
  return index >= 0 && args[index + 1] ? args[index + 1] : null;
};

const PORT = parseInt(getArgValue('--port')) || parseInt(process.env.PORT) || 3000;
const HOST = getArgValue('--host') || process.env.HOST || 'localhost';
const ENTRY_FILE = process.env.ENTRY_FILE || 'index.js';
const ENTRY_PATH = path.join(process.cwd(), ENTRY_FILE);

// Проверка наличия основного файла
if (!fs.existsSync(ENTRY_PATH)) {
  console.error(chalk.red(`✗ Файл не найден: ${ENTRY_FILE}`));
  console.log(chalk.cyan('Создайте index.js или установите ENTRY_FILE переменную'));
  process.exit(1);
}

// Модуль для отслеживания изменений файлов
const watchedPaths = ['src', 'lib', 'index.js'];
let appModule = null;
let server = null;

function loadApp() {
  try {
    // Очищаем require cache
    delete require.cache[ENTRY_PATH];

    appModule = require(ENTRY_PATH);
    return appModule;
  } catch (error) {
    console.error(chalk.red('✗ Ошибка при загрузке приложения:'));
    console.error(error.message);
    return null;
  }
}

function startServer() {
  try {
    appModule = loadApp();

    if (!appModule) {
      console.error(chalk.red('✗ Не удалось загрузить приложение'));
      return;
    }

    // Если это Express приложение
    if (appModule.listen) {
      if (server) {
        server.close(() => {
          appModule.listen(PORT, HOST, onServerStart);
        });
      } else {
        appModule.listen(PORT, HOST, onServerStart);
      }
    } else if (typeof appModule === 'function') {
      // Если это обработчик запроса
      server = http.createServer(appModule);
      server.listen(PORT, HOST, onServerStart);
    } else {
      console.error(chalk.red('✗ Экспортируемый модуль должен быть Express приложением или функцией'));
    }
  } catch (error) {
    console.error(chalk.red('✗ Ошибка при запуске сервера:'));
    console.error(error.message);
  }
}

function onServerStart() {
  const url = `http://${HOST}:${PORT}`;
  console.log(chalk.green(`\n✓ Сервер запущен на ${chalk.bold(url)}`));
  console.log(chalk.cyan(`📝 Введите Ctrl+C для остановки\n`));
}

// Отслеживание изменений файлов
function watchFiles() {
  watchedPaths.forEach(watchPath => {
    const fullPath = path.join(process.cwd(), watchPath);

    if (!fs.existsSync(fullPath)) {
      return;
    }

    fs.watch(fullPath, { recursive: true }, (eventType, filename) => {
      if (!filename.includes('node_modules') && !filename.includes('.git')) {
        console.log(chalk.yellow(`\n📝 Изменение: ${filename}`));
        console.log(chalk.blue('🔄 Перезагружаю сервер...\n'));
        startServer();
      }
    });
  });
}

// Graceful shutdown
process.on('SIGINT', () => {
  console.log(chalk.yellow('\n\n👋 Остановка сервера...'));

  if (server) {
    server.close(() => {
      console.log(chalk.green('✓ Сервер остановлен'));
      process.exit(0);
    });

    // Принудительная остановка через 5 секунд
    setTimeout(() => {
      console.error(chalk.red('✗ Сервер не остановился вовремя'));
      process.exit(1);
    }, 5000);
  } else {
    process.exit(0);
  }
});

// Вывод информации
console.log(chalk.blue(`
╔═══════════════════════════════════════╗
║  🚀 Development Server                 ║
║  Node.js с hot reload                  ║
╚═══════════════════════════════════════╝

${chalk.cyan('Конфигурация:')}
  Порт:     ${PORT}
  Host:     ${HOST}
  Entry:    ${ENTRY_FILE}
  Watch:    ${watchedPaths.join(', ')}
  Env:      ${process.env.NODE_ENV || 'development'}

${chalk.cyan('Загруженные переменные из .env:')}
`));

// Показываем загруженные переменные (без значений для безопасности)
Object.keys(process.env).forEach(key => {
  if (key.startsWith('JWT_') || key === 'DATABASE_URL' || key === 'API_KEY' || key.includes('SECRET')) {
    console.log(`  ${key}: ${chalk.gray('***')}`);
  }
});

console.log('');

// Запускаем сервер
startServer();

// Начинаем отслеживать файлы
watchFiles();
