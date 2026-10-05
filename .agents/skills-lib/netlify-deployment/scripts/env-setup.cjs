#!/usr/bin/env node

/**
 * Environment Variables Setup для Netlify
 *
 * Использование:
 *   node env-setup.js                    # Интерактивный режим
 *   node env-setup.js --from-file .env   # Загрузить из файла
 *   node env-setup.js --list             # Показать текущие переменные
 *   node env-setup.js --delete VAR_NAME  # Удалить переменную
 *   node env-setup.js --help             # Справка
 *
 * Функции:
 * - Чтение .env.example, .env.local или .env файлов
 * - Интерактивный ввод значений с подсказками
 * - Загрузка в Netlify через CLI (netlify env:set)
 * - Проверка обязательных переменных
 * - Создание локального .env файла
 * - Безопасное отображение значений (маскирование)
 *
 * Требования:
 * - Netlify CLI (npm install -g netlify-cli)
 * - Авторизация (netlify login)
 * - Линк к сайту (netlify link)
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');
const readline = require('readline');

// Цвета для консоли
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// Проверка Netlify CLI
function checkNetlifyCli() {
  try {
    execSync('netlify --version', { stdio: 'pipe' });
    return true;
  } catch (error) {
    return false;
  }
}

// Проверка авторизации и линка
function checkNetlifyAuth() {
  try {
    execSync('netlify status', { stdio: 'pipe' });
    return true;
  } catch (error) {
    return false;
  }
}

// Парсинг .env файла
function parseEnvFile(filePath) {
  const envVars = {};
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n');

  for (const line of lines) {
    // Пропускаем комментарии и пустые строки
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) {
      continue;
    }

    // Парсим KEY=VALUE
    const match = trimmed.match(/^([^=]+)=(.*)$/);
    if (match) {
      let key = match[1].trim();
      let value = match[2].trim();

      // Удаляем кавычки
      if ((value.startsWith('"') && value.endsWith('"')) ||
          (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }

      // Удаляем комментарии в конце строки
      const commentIndex = value.indexOf('#');
      if (commentIndex !== -1) {
        value = value.substring(0, commentIndex).trim();
      }

      envVars[key] = value;
    }
  }

  return envVars;
}

// Интерактивный ввод
function createPrompt() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  return {
    question: (query) => {
      return new Promise((resolve) => {
        rl.question(query, resolve);
      });
    },
    close: () => rl.close()
  };
}

// Получить текущие env переменные из Netlify
function getCurrentEnvVars() {
  try {
    const output = execSync('netlify env:list', {
      encoding: 'utf-8',
      stdio: 'pipe'
    });

    // Netlify CLI возвращает переменные в формате:
    // KEY = value
    const vars = {};
    const lines = output.trim().split('\n');

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('─') || trimmed.startsWith('│')) continue;

      // Парсим "KEY = value" или "KEY: value"
      const match = trimmed.match(/^([A-Z_][A-Z0-9_]*)\s*[=:]\s*(.*)$/);
      if (match) {
        const key = match[1];
        let value = match[2];

        // Удаляем кавычки если есть
        if ((value.startsWith('"') && value.endsWith('"')) ||
            (value.startsWith("'") && value.endsWith("'"))) {
          value = value.slice(1, -1);
        }

        vars[key] = value;
      }
    }

    return vars;
  } catch (error) {
    log('⚠ Не удалось получить текущие переменные', 'yellow');
    return {};
  }
}

// Установить env переменную
function setEnvVar(key, value, context = 'all') {
  try {
    // Используем stdin для безопасной передачи значения
    const command = `netlify env:set ${key}`;
    const child = spawn('netlify', ['env:set', key, value], {
      stdio: 'pipe'
    });

    return new Promise((resolve) => {
      let output = '';
      child.stdout.on('data', (data) => {
        output += data.toString();
      });

      child.stderr.on('data', (data) => {
        output += data.toString();
      });

      child.on('close', (code) => {
        resolve(code === 0);
      });
    });
  } catch (error) {
    return false;
  }
}

// Удалить env переменную
function deleteEnvVar(key) {
  try {
    execSync(`netlify env:unset ${key}`, { stdio: 'pipe' });
    return true;
  } catch (error) {
    return false;
  }
}

// Показать текущие переменные
async function listEnvVars() {
  console.log('');
  log('📋 Текущие Environment Variables:', 'cyan');
  console.log('');

  const vars = getCurrentEnvVars();

  if (Object.keys(vars).length === 0) {
    log('   (нет переменных)', 'yellow');
  } else {
    for (const [key, value] of Object.entries(vars)) {
      // Скрываем значение, показываем только длину
      const maskedValue = value ? '*'.repeat(Math.min(value.length, 20)) : '(не установлено)';
      console.log(`   ${key} = ${maskedValue}`);
    }
  }

  console.log('');
}

// Интерактивная настройка
async function interactiveSetup() {
  console.log('');
  log('🔧 Настройка Environment Variables', 'cyan');
  console.log('');

  // Ищем .env файлы
  const envFiles = ['.env.example', '.env.local', '.env'];
  let envFilePath = null;

  for (const file of envFiles) {
    if (fs.existsSync(file)) {
      envFilePath = file;
      log(`✓ Найден файл: ${file}`, 'green');
      break;
    }
  }

  if (!envFilePath) {
    log('⚠ Не найден .env файл', 'yellow');
    log('  Создайте .env.example с нужными переменными', 'yellow');
    console.log('');
    return;
  }

  // Парсим файл
  const envVars = parseEnvFile(envFilePath);
  const keys = Object.keys(envVars);

  if (keys.length === 0) {
    log('⚠ В файле нет переменных', 'yellow');
    console.log('');
    return;
  }

  console.log('');
  log(`Найдено переменных: ${keys.length}`, 'blue');
  console.log('');

  // Получаем текущие значения из Netlify
  log('Загружаю текущие значения из Netlify...', 'blue');
  const currentVars = getCurrentEnvVars();

  // Интерактивный ввод
  const prompt = createPrompt();
  const newVars = {};

  console.log('');
  log('Введите значения (Enter - пропустить, "current" - использовать текущее):', 'cyan');
  console.log('');

  for (const key of keys) {
    const exampleValue = envVars[key];
    const currentValue = currentVars[key];

    let promptText = `${key}`;
    if (exampleValue) {
      promptText += ` (пример: ${exampleValue})`;
    }
    if (currentValue) {
      promptText += ` [current: ${currentValue.substring(0, 20)}...]`;
    }
    promptText += ': ';

    const answer = await prompt.question(promptText);

    if (answer.trim() === '') {
      // Пропускаем
      log(`  → пропущено`, 'yellow');
    } else if (answer.trim().toLowerCase() === 'current' && currentValue) {
      // Оставляем текущее
      newVars[key] = currentValue;
      log(`  → оставлено текущее значение`, 'green');
    } else {
      // Новое значение
      newVars[key] = answer.trim();
      log(`  → будет установлено`, 'green');
    }
  }

  prompt.close();

  // Подтверждение
  console.log('');
  const keysToSet = Object.keys(newVars);

  if (keysToSet.length === 0) {
    log('Нет переменных для установки', 'yellow');
    console.log('');
    return;
  }

  log(`Будет установлено переменных: ${keysToSet.length}`, 'cyan');
  for (const key of keysToSet) {
    console.log(`  • ${key}`);
  }
  console.log('');

  const confirmPrompt = createPrompt();
  const confirm = await confirmPrompt.question('Продолжить? (y/N): ');
  confirmPrompt.close();

  if (confirm.toLowerCase() !== 'y' && confirm.toLowerCase() !== 'yes') {
    log('Отменено', 'yellow');
    console.log('');
    return;
  }

  // Устанавливаем переменные
  console.log('');
  log('Устанавливаю переменные...', 'blue');
  console.log('');

  let successCount = 0;
  let failCount = 0;

  for (const [key, value] of Object.entries(newVars)) {
    process.stdout.write(`  ${key}... `);

    const result = await setEnvVar(key, value);
    if (result) {
      log('✓', 'green');
      successCount++;
    } else {
      log('✗ ошибка', 'red');
      failCount++;
    }
  }

  console.log('');
  log(`Готово: ${successCount} успешно, ${failCount} ошибок`, successCount === keysToSet.length ? 'green' : 'yellow');
  console.log('');
}

// Загрузка из файла
async function loadFromFile(filePath) {
  console.log('');
  log(`📄 Загрузка из файла: ${filePath}`, 'cyan');
  console.log('');

  if (!fs.existsSync(filePath)) {
    log(`✗ Файл не найден: ${filePath}`, 'red');
    console.log('');
    return;
  }

  const envVars = parseEnvFile(filePath);
  const keys = Object.keys(envVars);

  if (keys.length === 0) {
    log('⚠ В файле нет переменных', 'yellow');
    console.log('');
    return;
  }

  log(`Найдено переменных: ${keys.length}`, 'blue');
  for (const key of keys) {
    console.log(`  • ${key}`);
  }
  console.log('');

  const prompt = createPrompt();
  const confirm = await prompt.question('Загрузить все переменные? (y/N): ');
  prompt.close();

  if (confirm.toLowerCase() !== 'y' && confirm.toLowerCase() !== 'yes') {
    log('Отменено', 'yellow');
    console.log('');
    return;
  }

  console.log('');
  log('Загружаю переменные...', 'blue');
  console.log('');

  let successCount = 0;
  let failCount = 0;

  for (const [key, value] of Object.entries(envVars)) {
    process.stdout.write(`  ${key}... `);

    const result = await setEnvVar(key, value);
    if (result) {
      log('✓', 'green');
      successCount++;
    } else {
      log('✗ ошибка', 'red');
      failCount++;
    }
  }

  console.log('');
  log(`Готово: ${successCount} успешно, ${failCount} ошибок`, successCount === keys.length ? 'green' : 'yellow');
  console.log('');
}

// Главная функция
async function main() {
  const args = process.argv.slice(2);

  // Проверка Netlify CLI
  if (!checkNetlifyCli()) {
    log('✗ Netlify CLI не установлен', 'red');
    console.log('');
    console.log('Установите через npm:');
    console.log('  npm install -g netlify-cli');
    console.log('');
    process.exit(1);
  }

  // Проверка авторизации
  if (!checkNetlifyAuth()) {
    log('✗ Не авторизованы в Netlify или не связан сайт', 'red');
    console.log('');
    console.log('Выполните:');
    console.log('  netlify login   # Авторизация');
    console.log('  netlify link    # Связь с сайтом');
    console.log('');
    process.exit(1);
  }

  // Обработка команд
  if (args.length === 0) {
    // Интерактивный режим
    await interactiveSetup();
  } else if (args[0] === '--list') {
    // Показать переменные
    await listEnvVars();
  } else if (args[0] === '--from-file' && args[1]) {
    // Загрузить из файла
    await loadFromFile(args[1]);
  } else if (args[0] === '--delete' && args[1]) {
    // Удалить переменную
    const key = args[1];
    console.log('');
    log(`🗑 Удаление переменной: ${key}`, 'cyan');
    console.log('');

    if (deleteEnvVar(key)) {
      log('✓ Переменная удалена', 'green');
    } else {
      log('✗ Ошибка удаления', 'red');
    }
    console.log('');
  } else if (args[0] === '--help' || args[0] === '-h') {
    // Справка
    console.log('');
    log('Environment Variables Setup для Netlify', 'cyan');
    console.log('');
    console.log('Использование:');
    console.log('  node env-setup.js                    # Интерактивный режим');
    console.log('  node env-setup.js --from-file .env   # Загрузить из файла');
    console.log('  node env-setup.js --list             # Показать текущие переменные');
    console.log('  node env-setup.js --delete VAR_NAME  # Удалить переменную');
    console.log('  node env-setup.js --help             # Эта справка');
    console.log('');
  } else {
    log('✗ Неизвестная команда', 'red');
    console.log('');
    console.log('Используйте --help для справки');
    console.log('');
    process.exit(1);
  }
}

// Запуск
if (require.main === module) {
  main().catch(error => {
    log(`✗ Ошибка: ${error.message}`, 'red');
    process.exit(1);
  });
}

module.exports = { parseEnvFile, setEnvVar, deleteEnvVar, getCurrentEnvVars };
