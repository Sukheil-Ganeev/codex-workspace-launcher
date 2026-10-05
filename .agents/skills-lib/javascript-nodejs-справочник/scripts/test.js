#!/usr/bin/env node

/**
 * test.js - Jest Test Runner
 * Запускает unit и integration тесты
 *
 * Использование:
 *   npm test              # Запустить все тесты
 *   npm run test:watch    # Watch mode
 *   npm run test:coverage # Покрытие
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const chalk = require('chalk');

const args = process.argv.slice(2);

// Help текст
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
${chalk.bold('Jest Test Runner')}

Использование:
  ${chalk.cyan('node scripts/test.js [options] [testFiles]')}

Опции:
  --help, -h          Показать этот текст
  --watch, -w         Watch mode (перезапуск при изменениях)
  --coverage, -c      Показать покрытие кода
  --bail              Остановить на первой ошибке
  --verbose           Подробный вывод
  --detectOpenHandles Найти незакрытые handles
  --forceExit         Принудительно завершить после тестов
  --no-cache          Не использовать cache

Примеры:
  ${chalk.cyan('node scripts/test.js')}                   # Запустить все тесты
  ${chalk.cyan('node scripts/test.js --watch')}          # Watch mode
  ${chalk.cyan('node scripts/test.js --coverage')}       # С покрытием
  ${chalk.cyan('node scripts/test.js --bail')}           # Остановить на первой ошибке
  ${chalk.cyan('node scripts/test.js auth.test.js')}     # Конкретный тест
  ${chalk.cyan('node scripts/test.js --verbose')}        # Подробный вывод
  `);
  process.exit(0);
}

// Проверка наличия package.json и jest конфигурации
const packageJsonPath = path.join(process.cwd(), 'package.json');
if (!fs.existsSync(packageJsonPath)) {
  console.error(chalk.red('✗ package.json не найден'));
  process.exit(1);
}

const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
const jestConfigExists = packageJson.jest ||
                         fs.existsSync(path.join(process.cwd(), 'jest.config.js'));

if (!jestConfigExists) {
  console.log(chalk.yellow('⚠️  Jest конфигурация не найдена. Создаём...'));

  const defaultConfig = {
    testEnvironment: 'node',
    coveragePathIgnorePatterns: ['/node_modules/'],
    testMatch: ['**/__tests__/**/*.js', '**/*.test.js', '**/*.spec.js'],
    collectCoverageFrom: [
      '**/*.js',
      '!**/*.test.js',
      '!**/*.spec.js',
      '!**/node_modules/**',
      '!**/scripts/**'
    ],
    coverageThreshold: {
      global: {
        branches: 70,
        functions: 70,
        lines: 70,
        statements: 70
      }
    }
  };

  fs.writeFileSync(
    path.join(process.cwd(), 'jest.config.js'),
    `module.exports = ${JSON.stringify(defaultConfig, null, 2)};`
  );

  // Обновляем package.json
  packageJson.jest = defaultConfig;
  fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));

  console.log(chalk.green('✓ Jest конфигурация создана'));
}

try {
  console.log(chalk.blue('🧪 Запускаю Jest...\n'));

  // Формируем команду
  let command = 'jest';

  if (args.length > 0) {
    command += ' ' + args.join(' ');
  }

  const startTime = Date.now();

  execSync(command, {
    stdio: 'inherit',
    cwd: process.cwd()
  });

  const duration = ((Date.now() - startTime) / 1000).toFixed(2);
  console.log(chalk.green(`\n✓ Тесты завершены за ${duration}s`));
  process.exit(0);
} catch (error) {
  console.log(chalk.red('\n✗ Тесты завершились с ошибками'));
  process.exit(1);
}
