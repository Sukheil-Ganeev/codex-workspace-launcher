#!/usr/bin/env node

/**
 * type-check.js - TypeScript / JSDoc Type Checker
 * Проверяет типы через TypeScript или JSDoc
 *
 * Использование:
 *   npm run type-check    # Проверить типы
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const chalk = require('chalk');

const args = process.argv.slice(2);

// Help текст
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
${chalk.bold('Type Checker (TypeScript / JSDoc)')}

Использование:
  ${chalk.cyan('node scripts/type-check.js [options]')}

Опции:
  --help, -h          Показать этот текст
  --watch             Watch mode
  --emit              Эмитировать скомпилированный код
  --noEmit            Только проверка типов (по умолчанию)
  --strict            Строгий режим типов
  --jsx               Включить JSX
  --jsdoc             Использовать JSDoc вместо TypeScript

Примеры:
  ${chalk.cyan('node scripts/type-check.js')}              # Базовая проверка
  ${chalk.cyan('node scripts/type-check.js --watch')}     # Watch mode
  ${chalk.cyan('node scripts/type-check.js --emit')}      # С компиляцией
  ${chalk.cyan('node scripts/type-check.js --strict')}    # Строгий режим
  `);
  process.exit(0);
}

// Проверяем TypeScript
const tscExists = fs.existsSync(path.join(process.cwd(), 'node_modules', 'typescript'));
const tsConfigExists = fs.existsSync(path.join(process.cwd(), 'tsconfig.json'));

// Проверяем JSDoc
const packageJsonPath = path.join(process.cwd(), 'package.json');
const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
const useJsDoc = args.includes('--jsdoc') || !tscExists;

if (tscExists && tsConfigExists) {
  // Используем TypeScript
  console.log(chalk.blue('✓ Используется TypeScript для проверки типов\n'));

  try {
    console.log(chalk.blue('🔍 Запускаю TypeScript type checker...\n'));

    let command = 'tsc';

    if (!args.includes('--emit')) {
      command += ' --noEmit';
    }

    if (args.includes('--watch')) {
      command += ' --watch';
    }

    if (args.includes('--strict')) {
      command += ' --strict';
    }

    // Добавляем остальные аргументы
    const validArgs = args.filter(arg => !arg.startsWith('--jsdoc'));
    if (validArgs.length > 0) {
      command += ' ' + validArgs.join(' ');
    }

    const startTime = Date.now();

    execSync(command, {
      stdio: 'inherit',
      cwd: process.cwd()
    });

    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log(chalk.green(`\n✓ Проверка типов завершена за ${duration}s`));
    process.exit(0);
  } catch (error) {
    console.log(chalk.red('\n✗ Обнаружены ошибки типов'));
    process.exit(1);
  }
} else {
  // Используем JSDoc через TypeScript в режиме checkJs
  console.log(chalk.blue('✓ Используется JSDoc для проверки типов\n'));

  // Создаём минимальный tsconfig.json для JSDoc проверки
  if (!tsConfigExists) {
    console.log(chalk.yellow('⚠️  tsconfig.json не найден. Создаём для JSDoc проверки...'));

    const jsdocTsConfig = {
      compilerOptions: {
        allowJs: true,
        checkJs: true,
        noEmit: true,
        target: 'ES2020',
        module: 'commonjs',
        lib: ['ES2020'],
        skipLibCheck: true,
        esModuleInterop: true,
        resolveJsonModule: true
      },
      include: ['**/*.js'],
      exclude: ['node_modules', 'dist', 'build']
    };

    fs.writeFileSync(
      path.join(process.cwd(), 'tsconfig.json'),
      JSON.stringify(jsdocTsConfig, null, 2)
    );
    console.log(chalk.green('✓ tsconfig.json создан'));
  }

  // Используем TypeScript в режиме JSDoc проверки
  if (tscExists) {
    try {
      console.log(chalk.blue('🔍 Запускаю JSDoc type checker (TypeScript)...\n'));

      let command = 'tsc --allowJs --checkJs --noEmit';

      if (args.includes('--watch')) {
        command += ' --watch';
      }

      if (args.includes('--emit')) {
        command = command.replace('--noEmit', '--outDir ./dist');
      }

      const startTime = Date.now();

      execSync(command, {
        stdio: 'inherit',
        cwd: process.cwd()
      });

      const duration = ((Date.now() - startTime) / 1000).toFixed(2);
      console.log(chalk.green(`\n✓ Проверка типов завершена за ${duration}s`));
      process.exit(0);
    } catch (error) {
      console.log(chalk.red('\n✗ Обнаружены ошибки типов'));
      process.exit(1);
    }
  } else {
    console.error(chalk.red('✗ TypeScript не установлен'));
    console.log(chalk.cyan('\nДля проверки типов установите: npm install --save-dev typescript'));
    process.exit(1);
  }
}
