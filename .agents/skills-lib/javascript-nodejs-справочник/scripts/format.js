#!/usr/bin/env node

/**
 * format.js - Prettier Code Formatter
 * Форматирует код в соответствии с Prettier стилем
 *
 * Использование:
 *   npm run format        # Отформатировать весь код
 *   npm run format -- --check  # Проверить без изменений
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const chalk = require('chalk');

const args = process.argv.slice(2);

// Help текст
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
${chalk.bold('Prettier Code Formatter')}

Использование:
  ${chalk.cyan('node scripts/format.js [options] [files]')}

Опции:
  --help, -h          Показать этот текст
  --check             Проверить форматирование без изменений
  --write, -w         Записать форматированный код (по умолчанию)
  --parser <parser>   Парсер (babel, typescript, json и т.д.)
  --tab-width <n>     Ширина табуляции (по умолчанию 2)
  --semi              Добавлять ли ; в конце (по умолчанию true)
  --single-quote      Использовать одиночные кавычки (по умолчанию false)
  --trailing-comma    trailing commas (all, es5, none)

Примеры:
  ${chalk.cyan('node scripts/format.js')}                    # Отформатировать всё
  ${chalk.cyan('node scripts/format.js --check')}           # Проверить без изменений
  ${chalk.cyan('node scripts/format.js src/**/*.js')}       # Форматировать только src/
  ${chalk.cyan('node scripts/format.js --tab-width 4')}     # С 4-пробельным отступом
  `);
  process.exit(0);
}

// Проверка наличия .prettierrc
const prettierConfigExists = fs.existsSync(path.join(process.cwd(), '.prettierrc')) ||
                             fs.existsSync(path.join(process.cwd(), '.prettierrc.json')) ||
                             fs.existsSync(path.join(process.cwd(), 'prettier.config.js'));

if (!prettierConfigExists) {
  console.log(chalk.yellow('⚠️  .prettierrc не найден. Создаём конфигурацию...'));

  const defaultConfig = {
    semi: true,
    trailingComma: 'es5',
    singleQuote: true,
    printWidth: 100,
    tabWidth: 2,
    useTabs: false,
    arrowParens: 'always',
    endOfLine: 'lf'
  };

  fs.writeFileSync(
    path.join(process.cwd(), '.prettierrc'),
    JSON.stringify(defaultConfig, null, 2)
  );
  console.log(chalk.green('✓ .prettierrc создан'));
}

try {
  console.log(chalk.blue('✨ Запускаю Prettier...\n'));

  // Формируем команду
  let command = `prettier ${args.join(' ')}`;

  // Если нет аргументов, форматируем стандартные файлы
  if (args.length === 0 || (!args[0].includes('*') && !args[0].includes('.'))) {
    command = 'prettier --write "**/*.{js,jsx,ts,tsx,json,css,md,yml,yaml}" --ignore-unknown';
  } else if (!args.includes('--write') && !args.includes('-w') && !args.includes('--check')) {
    command += ' --write';
  }

  const startTime = Date.now();

  execSync(command, {
    stdio: 'inherit',
    cwd: process.cwd()
  });

  const duration = ((Date.now() - startTime) / 1000).toFixed(2);

  if (args.includes('--check')) {
    console.log(chalk.green(`\n✓ Проверка форматирования завершена за ${duration}s`));
  } else {
    console.log(chalk.green(`\n✓ Код отформатирован за ${duration}s`));
  }

  process.exit(0);
} catch (error) {
  if (args.includes('--check')) {
    console.log(chalk.red('\n✗ Код требует форматирования'));
    console.log(chalk.cyan('\n💡 Запустите без --check чтобы отформатировать'));
  } else {
    console.error(chalk.red('✗ Ошибка при выполнении Prettier:'));
    console.error(error.message);
  }
  process.exit(1);
}
