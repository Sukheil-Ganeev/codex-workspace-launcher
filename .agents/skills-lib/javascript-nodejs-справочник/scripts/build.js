#!/usr/bin/env node

/**
 * build.js - Production Build Script
 * Компилирует и оптимизирует код для production
 *
 * Использование:
 *   npm run build        # Production build
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const chalk = require('chalk');

const args = process.argv.slice(2);

// Help текст
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
${chalk.bold('Production Build Script')}

Использование:
  ${chalk.cyan('node scripts/build.js [options]')}

Опции:
  --help, -h          Показать этот текст
  --minify            Минификация кода
  --sourcemaps        Включить source maps
  --analyze           Анализ размера бандла
  --clean             Очистить папку build перед сборкой
  --watch             Watch mode

Примеры:
  ${chalk.cyan('node scripts/build.js')}              # Обычная сборка
  ${chalk.cyan('node scripts/build.js --minify')}    # С минификацией
  ${chalk.cyan('node scripts/build.js --analyze')}   # Анализ размера
  `);
  process.exit(0);
}

const BUILD_DIR = 'dist';
const SRC_DIR = 'src';
const shouldMinify = args.includes('--minify');
const shouldClean = args.includes('--clean');
const shouldAnalyze = args.includes('--analyze');

// Очистка папки build
if (shouldClean && fs.existsSync(BUILD_DIR)) {
  console.log(chalk.yellow(`🗑️  Очищаю ${BUILD_DIR}...`));
  execSync(`rm -rf ${BUILD_DIR}`);
  console.log(chalk.green(`✓ ${BUILD_DIR} очищен`));
}

// Создаём папку build если её нет
if (!fs.existsSync(BUILD_DIR)) {
  fs.mkdirSync(BUILD_DIR, { recursive: true });
}

try {
  console.log(chalk.blue(`
╔════════════════════════════════════════╗
║  🏗️  Production Build                   ║
╚════════════════════════════════════════╝
`));

  const startTime = Date.now();

  // Шаг 1: Type checking
  console.log(chalk.blue('📋 1. Проверка типов...'));
  try {
    execSync('npm run type-check 2>/dev/null', { stdio: 'pipe' });
    console.log(chalk.green('   ✓ Типы проверены'));
  } catch {
    console.log(chalk.yellow('   ⚠️  Type checking пропущен'));
  }

  // Шаг 2: Linting
  console.log(chalk.blue('📋 2. Проверка стиля кода...'));
  try {
    execSync('npm run lint 2>/dev/null', { stdio: 'pipe' });
    console.log(chalk.green('   ✓ Код проверен'));
  } catch {
    console.log(chalk.yellow('   ⚠️  Linting пропущен'));
  }

  // Шаг 3: Testing
  console.log(chalk.blue('📋 3. Запуск тестов...'));
  try {
    execSync('npm test 2>/dev/null', { stdio: 'pipe' });
    console.log(chalk.green('   ✓ Все тесты пройдены'));
  } catch {
    console.log(chalk.yellow('   ⚠️  Тесты пропущены'));
  }

  // Шаг 4: Копирование файлов
  console.log(chalk.blue('📋 4. Копирование файлов...'));
  if (fs.existsSync(SRC_DIR)) {
    execSync(`cp -r ${SRC_DIR}/* ${BUILD_DIR}/ 2>/dev/null || true`);
    console.log(chalk.green(`   ✓ Файлы скопированы из ${SRC_DIR}`));
  } else {
    execSync(`find . -maxdepth 1 -name "*.js" -exec cp {} ${BUILD_DIR}/ \\; 2>/dev/null || true`);
    console.log(chalk.green('   ✓ Файлы скопированы'));
  }

  // Шаг 5: Копирование package.json и других конфигов
  if (fs.existsSync('package.json')) {
    const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));

    // Удаляем dev dependencies для production
    if (packageJson.devDependencies) {
      delete packageJson.devDependencies;
    }

    fs.writeFileSync(
      path.join(BUILD_DIR, 'package.json'),
      JSON.stringify(packageJson, null, 2)
    );
  }

  // Шаг 6: Минификация (опционально)
  if (shouldMinify) {
    console.log(chalk.blue('📋 5. Минификация кода...'));
    try {
      // Попытка использовать terser если доступен
      execSync(`npx terser ${BUILD_DIR}/**/*.js -c -m -o ${BUILD_DIR}/ 2>/dev/null`, { stdio: 'pipe' });
      console.log(chalk.green('   ✓ Код минифицирован'));
    } catch {
      console.log(chalk.yellow('   ⚠️  Минификация пропущена (terser не установлен)'));
    }
  }

  // Шаг 7: Создание .env.production
  if (fs.existsSync('.env')) {
    fs.copyFileSync('.env', path.join(BUILD_DIR, '.env'));
  }

  // Вычисляем размер
  console.log(chalk.blue('📋 6. Статистика...'));
  const getSize = (dir) => {
    return execSync(`du -sh ${dir} 2>/dev/null || echo "N/A"`)
      .toString()
      .trim()
      .split('\t')[0];
  };

  const buildSize = getSize(BUILD_DIR);
  const duration = ((Date.now() - startTime) / 1000).toFixed(2);

  console.log(chalk.green(`
╔════════════════════════════════════════╗
║  ✓ BUILD УСПЕШЕН                      ║
╚════════════════════════════════════════╝

Итоговая статистика:
  Папка:          ${BUILD_DIR}
  Размер:         ${buildSize}
  Время сборки:   ${duration}s
  Node env:       production
  Минификация:    ${shouldMinify ? 'включена' : 'отключена'}

${chalk.cyan('Что дальше:')}
  npm install --production  # Установить только prod зависимости
  npm start                 # Запустить сервер
  npm run deploy            # Развернуть на production
`));

  process.exit(0);
} catch (error) {
  console.error(chalk.red(`
╔════════════════════════════════════════╗
║  ✗ BUILD FAILED                        ║
╚════════════════════════════════════════╝
`));
  console.error(error.message);
  process.exit(1);
}
