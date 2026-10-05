#!/usr/bin/env node
// Validate vercel.json
// Валидация конфигурации Vercel
// Использование: node validate-config.js [path/to/vercel.json]

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Цвета для вывода (ANSI escape codes)
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m'
};

// Функции для вывода
const success = (msg) => console.log(`${colors.green}✓${colors.reset} ${msg}`);
const error = (msg) => console.log(`${colors.red}✗${colors.reset} ${msg}`);
const warning = (msg) => console.log(`${colors.yellow}⚠${colors.reset} ${msg}`);
const info = (msg) => console.log(`${colors.blue}ℹ${colors.reset} ${msg}`);

console.log('==================================');
console.log('  Vercel Config Validator');
console.log('==================================\n');

// Получить путь к файлу
const configPath = process.argv[2] || 'vercel.json';
const fullPath = path.resolve(configPath);

// Проверка существования файла
if (!fs.existsSync(fullPath)) {
  error(`Файл не найден: ${fullPath}`);
  process.exit(1);
}

info(`Проверка файла: ${fullPath}\n`);

// Чтение и парсинг JSON
let config;
try {
  const content = fs.readFileSync(fullPath, 'utf8');
  config = JSON.parse(content);
  success('JSON синтаксис валиден');
} catch (err) {
  error('Ошибка парсинга JSON:');
  console.log(`  ${err.message}\n`);
  process.exit(1);
}

console.log('');

// ВАЛИДАЦИЯ СТРУКТУРЫ
let issues = 0;
let warnings = 0;

console.log('=== Проверка структуры ===\n');

// 1. Проверка version
if (!config.version) {
  error('Отсутствует обязательное поле "version"');
  issues++;
} else if (config.version !== 2) {
  warning(`Рекомендуется version: 2 (текущее: ${config.version})`);
  warnings++;
} else {
  success(`version: ${config.version}`);
}

// 2. Проверка builds
if (config.builds) {
  if (!Array.isArray(config.builds)) {
    error('"builds" должен быть массивом');
    issues++;
  } else {
    success(`builds: ${config.builds.length} конфигураций`);
    
    // Проверка каждого build
    config.builds.forEach((build, index) => {
      if (!build.src) {
        error(`  Build #${index + 1}: отсутствует "src"`);
        issues++;
      }
      if (!build.use) {
        error(`  Build #${index + 1}: отсутствует "use"`);
        issues++;
      }
      
      // Проверка известных билдеров
      const knownBuilders = [
        '@vercel/static',
        '@vercel/node',
        '@vercel/python',
        '@vercel/go',
        '@vercel/ruby',
        '@vercel/next'
      ];
      
      if (build.use && !knownBuilders.some(b => build.use.startsWith(b))) {
        warning(`  Build #${index + 1}: неизвестный билдер "${build.use}"`);
        warnings++;
      }
    });
  }
}

// 3. Проверка routes/rewrites/redirects
if (config.routes) {
  warning('Поле "routes" deprecated, используйте "rewrites" и "redirects"');
  warnings++;
}

if (config.rewrites) {
  if (!Array.isArray(config.rewrites)) {
    error('"rewrites" должен быть массивом');
    issues++;
  } else {
    success(`rewrites: ${config.rewrites.length} правил`);
    
    // Проверка каждого rewrite
    config.rewrites.forEach((rewrite, index) => {
      if (!rewrite.source) {
        error(`  Rewrite #${index + 1}: отсутствует "source"`);
        issues++;
      }
      if (!rewrite.destination) {
        error(`  Rewrite #${index + 1}: отсутствует "destination"`);
        issues++;
      }
    });
  }
}

if (config.redirects) {
  if (!Array.isArray(config.redirects)) {
    error('"redirects" должен быть массивом');
    issues++;
  } else {
    success(`redirects: ${config.redirects.length} правил`);
    
    // Проверка каждого redirect
    config.redirects.forEach((redirect, index) => {
      if (!redirect.source) {
        error(`  Redirect #${index + 1}: отсутствует "source"`);
        issues++;
      }
      if (!redirect.destination) {
        error(`  Redirect #${index + 1}: отсутствует "destination"`);
        issues++;
      }
      if (!redirect.permanent && redirect.permanent !== false) {
        warning(`  Redirect #${index + 1}: не указано "permanent"`);
        warnings++;
      }
    });
  }
}

// 4. Проверка headers
if (config.headers) {
  if (!Array.isArray(config.headers)) {
    error('"headers" должен быть массивом');
    issues++;
  } else {
    success(`headers: ${config.headers.length} правил`);
    
    config.headers.forEach((header, index) => {
      if (!header.source) {
        error(`  Header #${index + 1}: отсутствует "source"`);
        issues++;
      }
      if (!header.headers || !Array.isArray(header.headers)) {
        error(`  Header #${index + 1}: отсутствует или неверный "headers"`);
        issues++;
      }
    });
  }
}

// 5. Проверка env
if (config.env) {
  info('env: переменные окружения найдены');
  warning('  Не храните секреты в vercel.json!');
  warning('  Используйте: vercel env add');
  warnings++;
}

// 6. Проверка deprecated полей
const deprecatedFields = ['regions', 'features', 'routes', 'cleanUrls'];
deprecatedFields.forEach(field => {
  if (config[field]) {
    warning(`Поле "${field}" deprecated`);
    warnings++;
  }
});

console.log('');

// СОВЕТЫ ПО ОПТИМИЗАЦИИ
console.log('=== Советы по оптимизации ===\n');

// Проверка наличия .vercelignore
const vercelIgnorePath = path.join(path.dirname(fullPath), '.vercelignore');
if (!fs.existsSync(vercelIgnorePath)) {
  info('Создайте .vercelignore для исключения ненужных файлов');
  console.log('  Пример содержимого:');
  console.log('    node_modules');
  console.log('    .git');
  console.log('    *.log');
  console.log('    .env.local');
}

// Проверка размера конфига
const configSize = Buffer.byteLength(JSON.stringify(config));
if (configSize > 4096) {
  warning(`Большой размер конфига (${configSize} bytes). Рассмотрите упрощение.`);
  warnings++;
}

// Специфичные советы по билдерам
if (config.builds) {
  const hasStaticBuilder = config.builds.some(b => b.use === '@vercel/static');
  const hasWildcard = config.builds.some(b => b.src === '**');
  
  if (hasStaticBuilder && hasWildcard) {
    info('Статичный сайт: рассмотрите использование Zero Config (удалите vercel.json)');
  }
}

console.log('');

// ИТОГОВЫЙ РЕЗУЛЬТАТ
console.log('=== Результат ===\n');

if (issues === 0 && warnings === 0) {
  success('Конфигурация идеальна! Ошибок и предупреждений нет.');
} else {
  if (issues > 0) {
    error(`Найдено ошибок: ${issues}`);
  }
  if (warnings > 0) {
    warning(`Найдено предупреждений: ${warnings}`);
  }
}

console.log('');

// Exit code
process.exit(issues > 0 ? 1 : 0);
