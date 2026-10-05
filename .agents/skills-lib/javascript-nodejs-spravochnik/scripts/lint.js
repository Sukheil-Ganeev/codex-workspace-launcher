#!/usr/bin/env node

/**
 * lint.js - ESLint Runner
 * Проверяет качество кода с помощью ESLint
 *
 * Использование:
 *   npm run lint              # Проверить весь код
 *   npm run lint -- --fix     # Автоисправить проблемы
 *   node scripts/lint.js --fix src/**/*.js
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const chalk = require('chalk');

const args = process.argv.slice(2);

// Help текст
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
${chalk.bold('ESLint Runner')}

Использование:
  ${chalk.cyan('node scripts/lint.js [options] [files]')}

Опции:
  --help, -h          Показать этот текст
  --fix, -f           Автоматически исправить проблемы
  --cache             Использовать cache для ускорения
  --format <format>   Формат вывода (stylish, json, compact)
  --ext <ext>         Расширения файлов для проверки (по умолчанию .js,.jsx,.ts,.tsx)
  --max-warnings <n>  Максимум warning перед ошибкой
  --quiet             Показывать только ошибки
  --stats             Показать статистику

Примеры:
  ${chalk.cyan('node scripts/lint.js')}                    # Проверить всё
  ${chalk.cyan('node scripts/lint.js --fix')}             # Исправить ошибки
  ${chalk.cyan('node scripts/lint.js src/**/*.js --fix')} # Исправить только src/
  ${chalk.cyan('node scripts/lint.js --cache')}           # С кешированием
  `);
  process.exit(0);
}

// Проверка наличия .eslintrc
const eslintConfigExists = fs.existsSync(path.join(process.cwd(), '.eslintrc')) ||
                          fs.existsSync(path.join(process.cwd(), '.eslintrc.json')) ||
                          fs.existsSync(path.join(process.cwd(), '.eslintrc.js'));

if (!eslintConfigExists) {
  console.log(chalk.yellow('⚠️  .eslintrc не найден. Создаём базовую конфигурацию...'));

  const defaultConfig = {
    env: {
      node: true,
      es2021: true,
      jest: true
    },
    extends: ['eslint:recommended'],
    parserOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module'
    },
    rules: {
      'no-console': ['warn', { allow: ['warn', 'error', 'info'] }],
      'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      'prefer-const': 'error',
      'no-var': 'error',
      'semi': ['error', 'always'],
      'quotes': ['error', 'single', { avoidEscape: true }]
    }
  };

  fs.writeFileSync(
    path.join(process.cwd(), '.eslintrc.json'),
    JSON.stringify(defaultConfig, null, 2)
  );
  console.log(chalk.green('✓ .eslintrc.json создан'));
}

try {
  console.log(chalk.blue('🔍 Запускаю ESLint...\n'));

  // Формируем команду
  let command = 'eslint';

  if (args.length === 0 || !args[0].includes('*')) {
    // Если нет аргументов, сканируем стандартные директории
    command += ' . --ignore-path .gitignore';
  } else {
    command += ' ' + args.join(' ');
  }

  const startTime = Date.now();

  try {
    execSync(command, {
      stdio: 'inherit',
      cwd: process.cwd()
    });

    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log(chalk.green(`\n✓ Проверка завершена успешно за ${duration}s`));
    process.exit(0);
  } catch (error) {
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log(chalk.red(`\n✗ Обнаружены ошибки за ${duration}s`));

    if (args.includes('--fix') || args.includes('-f')) {
      console.log(chalk.yellow('\n💡 Запустите без --fix чтобы увидеть ошибки'));
    } else {
      console.log(chalk.cyan('\n💡 Запустите с --fix чтобы исправить автоматически'));
    }

    process.exit(1);
  }
} catch (error) {
  console.error(chalk.red('✗ Ошибка при выполнении ESLint:'));
  console.error(error.message);
  process.exit(1);
}
