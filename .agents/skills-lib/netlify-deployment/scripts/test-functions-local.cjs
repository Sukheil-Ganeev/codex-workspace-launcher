#!/usr/bin/env node

/**
 * Test Netlify Functions Locally
 *
 * Локальное тестирование serverless функций перед деплоем
 *
 * Использование:
 *   node test-functions-local.js                        # Список функций
 *   node test-functions-local.js hello                  # Тест функции hello
 *   node test-functions-local.js hello --method POST    # С методом POST
 *   node test-functions-local.js hello --body '{"key":"value"}'  # С телом запроса (JSON)
 *   node test-functions-local.js hello --query "id=123&name=test"  # Query параметры
 *   node test-functions-local.js hello --env KEY=value  # С env переменной
 *   node test-functions-local.js --help                 # Справка
 *
 * Функции:
 * - Запуск функций локально без Netlify Dev
 * - Мок HTTP запросов (GET, POST, PUT, DELETE)
 * - Мок event и context объектов
 * - Проверка environment variables
 * - Логирование ошибок с stack trace
 * - Поддержка callback и Promise API
 * - Измерение времени выполнения
 * - Красивый вывод JSON ответов
 *
 * Директория функций:
 * - netlify/functions/
 * - functions/
 * - .netlify/functions/
 * - или из netlify.toml (build.functions)
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// Цвета для консоли
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  gray: '\x1b[90m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// Найти директорию с функциями
function findFunctionsDir() {
  // Проверяем netlify.toml
  const tomlPath = 'netlify.toml';
  if (fs.existsSync(tomlPath)) {
    const content = fs.readFileSync(tomlPath, 'utf-8');
    const match = content.match(/^\s*functions\s*=\s*"([^"]+)"/m);
    if (match) {
      const dir = match[1];
      if (fs.existsSync(dir)) {
        return dir;
      }
    }
  }

  // Стандартные директории
  const standardDirs = ['netlify/functions', 'functions', '.netlify/functions'];
  for (const dir of standardDirs) {
    if (fs.existsSync(dir)) {
      return dir;
    }
  }

  return null;
}

// Получить список функций
function listFunctions(functionsDir) {
  if (!functionsDir || !fs.existsSync(functionsDir)) {
    return [];
  }

  const files = fs.readdirSync(functionsDir);
  const functions = [];

  for (const file of files) {
    const fullPath = path.join(functionsDir, file);
    const stat = fs.statSync(fullPath);

    if (stat.isFile() && (file.endsWith('.js') || file.endsWith('.ts'))) {
      // Файл с функцией
      functions.push({
        name: file.replace(/\.(js|ts)$/, ''),
        path: fullPath,
        type: file.endsWith('.ts') ? 'typescript' : 'javascript'
      });
    } else if (stat.isDirectory()) {
      // Папка с функцией (должна содержать index.js или имя_папки.js)
      const indexPath = path.join(fullPath, 'index.js');
      const namedPath = path.join(fullPath, `${file}.js`);

      if (fs.existsSync(indexPath)) {
        functions.push({
          name: file,
          path: indexPath,
          type: 'javascript'
        });
      } else if (fs.existsSync(namedPath)) {
        functions.push({
          name: file,
          path: namedPath,
          type: 'javascript'
        });
      }
    }
  }

  return functions;
}

// Создать мок event объекта
function createMockEvent(options = {}) {
  const {
    method = 'GET',
    path = '/.netlify/functions/test',
    headers = {},
    body = null,
    queryStringParameters = {}
  } = options;

  return {
    httpMethod: method,
    path: path,
    headers: {
      'user-agent': 'Netlify-Functions-Local-Tester/1.0',
      'content-type': 'application/json',
      ...headers
    },
    queryStringParameters: queryStringParameters,
    body: body ? (typeof body === 'string' ? body : JSON.stringify(body)) : null,
    isBase64Encoded: false
  };
}

// Создать мок context объекта
function createMockContext(functionName = 'test-function') {
  const now = new Date();
  const dateStr = now.toISOString().split('T')[0].replace(/-/g, '/');

  return {
    callbackWaitsForEmptyEventLoop: false,
    functionName: functionName,
    functionVersion: '1.0',
    invokedFunctionArn: `arn:aws:lambda:us-east-1:123456789012:function:${functionName}`,
    memoryLimitInMB: 1024,
    awsRequestId: 'test-request-id-' + Date.now(),
    logGroupName: `/aws/lambda/${functionName}`,
    logStreamName: `${dateStr}/[$LATEST]${functionName}`,
    identity: {
      cognitoIdentityId: null,
      cognitoIdentityPoolId: null
    },
    clientContext: {
      client: {
        installation_id: 'test-installation',
        app_title: 'Netlify Functions Local Tester',
        app_version_name: '1.0'
      },
      env: {
        platform: 'netlify'
      }
    },
    // Netlify-specific context
    getRemainingTimeInMillis: () => 10000
  };
}

// Загрузить и выполнить функцию
async function testFunction(functionInfo, options = {}) {
  const { method, body, headers, query, env } = options;

  console.log('');
  log(`🧪 Тестирование функции: ${functionInfo.name}`, 'cyan');
  log(`   Файл: ${functionInfo.path}`, 'gray');
  console.log('');

  // Устанавливаем env переменные
  if (env) {
    for (const [key, value] of Object.entries(env)) {
      process.env[key] = value;
      log(`   ENV: ${key} = ${value}`, 'gray');
    }
  }

  // Парсим query параметры
  const queryParams = {};
  if (query) {
    const pairs = query.split('&');
    for (const pair of pairs) {
      const [key, value] = pair.split('=');
      queryParams[key] = decodeURIComponent(value || '');
    }
  }

  // Создаём мок объекты
  const event = createMockEvent({
    method: method || 'GET',
    body: body,
    headers: headers || {},
    queryStringParameters: queryParams
  });

  const context = createMockContext(functionInfo.name);

  console.log('');
  log('📥 Request:', 'blue');
  log(`   Method: ${event.httpMethod}`, 'gray');
  log(`   Path: ${event.path}`, 'gray');
  if (body) {
    log(`   Body: ${body}`, 'gray');
  }
  if (Object.keys(queryParams).length > 0) {
    log(`   Query: ${JSON.stringify(queryParams)}`, 'gray');
  }
  console.log('');

  // Загружаем функцию
  let handler;
  try {
    // Очищаем require cache для перезагрузки
    delete require.cache[require.resolve(path.resolve(functionInfo.path))];

    const functionModule = require(path.resolve(functionInfo.path));
    handler = functionModule.handler || functionModule;

    if (typeof handler !== 'function') {
      throw new Error('Экспортирован не функция-обработчик');
    }
  } catch (error) {
    log('✗ Ошибка загрузки функции:', 'red');
    log(`   ${error.message}`, 'red');
    console.log('');
    return false;
  }

  // Выполняем функцию
  const startTime = Date.now();
  let response;

  try {
    log('⏳ Выполнение...', 'yellow');
    console.log('');

    // Функция может возвращать Promise или использовать callback
    response = await new Promise((resolve, reject) => {
      const result = handler(event, context, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });

      // Если вернулся Promise, используем его
      if (result && typeof result.then === 'function') {
        result.then(resolve).catch(reject);
      }
    });

    const duration = Date.now() - startTime;

    console.log('');
    log(`✓ Выполнено за ${duration}ms`, 'green');
    console.log('');

    // Выводим ответ
    log('📤 Response:', 'blue');
    log(`   Status: ${response.statusCode || 200}`, 'gray');

    if (response.headers) {
      log(`   Headers:`, 'gray');
      for (const [key, value] of Object.entries(response.headers)) {
        log(`     ${key}: ${value}`, 'gray');
      }
    }

    if (response.body) {
      console.log('');
      log('   Body:', 'gray');

      // Пытаемся распарсить JSON для красивого вывода
      try {
        const parsed = JSON.parse(response.body);
        console.log(JSON.stringify(parsed, null, 2).split('\n').map(line => `     ${line}`).join('\n'));
      } catch (e) {
        // Не JSON, выводим как есть
        const lines = response.body.split('\n');
        for (const line of lines) {
          console.log(`     ${line}`);
        }
      }
    }

    console.log('');
    return true;

  } catch (error) {
    const duration = Date.now() - startTime;

    console.log('');
    log(`✗ Ошибка выполнения (${duration}ms):`, 'red');
    log(`   ${error.message}`, 'red');

    if (error.stack) {
      console.log('');
      log('   Stack trace:', 'gray');
      const stackLines = error.stack.split('\n').slice(1);
      for (const line of stackLines) {
        log(`   ${line.trim()}`, 'gray');
      }
    }

    console.log('');
    return false;
  }
}

// Показать список функций
function showFunctionsList(functions) {
  console.log('');
  log('📋 Доступные функции:', 'cyan');
  console.log('');

  if (functions.length === 0) {
    log('   (нет функций)', 'yellow');
  } else {
    for (const func of functions) {
      console.log(`   • ${func.name} (${func.type})`);
      log(`     ${func.path}`, 'gray');
    }
  }

  console.log('');
  console.log('Использование:');
  console.log('  node test-functions-local.js <function-name> [options]');
  console.log('');
  console.log('Опции:');
  console.log('  --method <GET|POST|PUT|DELETE>   HTTP метод (по умолчанию GET)');
  console.log('  --body <json>                    Тело запроса');
  console.log('  --query <key=value&key2=value2>  Query параметры');
  console.log('  --env <KEY=value>                Environment переменная');
  console.log('');
}

// Главная функция
async function main() {
  const args = process.argv.slice(2);

  // Находим директорию с функциями
  const functionsDir = findFunctionsDir();

  if (!functionsDir) {
    log('✗ Не найдена директория с функциями', 'red');
    console.log('');
    console.log('Проверьте:');
    console.log('  • netlify/functions/');
    console.log('  • functions/');
    console.log('  • Настройку build.functions в netlify.toml');
    console.log('');
    process.exit(1);
  }

  // Получаем список функций
  const functions = listFunctions(functionsDir);

  // Если нет аргументов, показываем список
  if (args.length === 0) {
    showFunctionsList(functions);
    process.exit(0);
  }

  // Парсим аргументы
  const functionName = args[0];
  const options = {
    method: 'GET',
    body: null,
    headers: {},
    query: '',
    env: {}
  };

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--method' && args[i + 1]) {
      options.method = args[i + 1].toUpperCase();
      i++;
    } else if (args[i] === '--body' && args[i + 1]) {
      options.body = args[i + 1];
      i++;
    } else if (args[i] === '--query' && args[i + 1]) {
      options.query = args[i + 1];
      i++;
    } else if (args[i] === '--env' && args[i + 1]) {
      const [key, value] = args[i + 1].split('=');
      if (key && value) {
        options.env[key] = value;
      }
      i++;
    } else if (args[i] === '--help' || args[i] === '-h') {
      showFunctionsList(functions);
      process.exit(0);
    }
  }

  // Находим функцию
  const functionInfo = functions.find(f => f.name === functionName);

  if (!functionInfo) {
    log(`✗ Функция не найдена: ${functionName}`, 'red');
    console.log('');
    console.log('Доступные функции:');
    for (const func of functions) {
      console.log(`  • ${func.name}`);
    }
    console.log('');
    process.exit(1);
  }

  // Тестируем функцию
  const success = await testFunction(functionInfo, options);

  process.exit(success ? 0 : 1);
}

// Запуск
if (require.main === module) {
  main().catch(error => {
    log(`✗ Критическая ошибка: ${error.message}`, 'red');
    console.error(error.stack);
    process.exit(1);
  });
}

module.exports = {
  findFunctionsDir,
  listFunctions,
  testFunction,
  createMockEvent,
  createMockContext
};
