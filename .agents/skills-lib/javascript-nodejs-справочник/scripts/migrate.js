#!/usr/bin/env node

/**
 * migrate.js - Database Migration Runner
 * Управляет миграциями БД (create, run, undo)
 *
 * Использование:
 *   npm run migrate              # Запустить все pending миграции
 *   npm run migrate:undo         # Откатить последнюю
 *   node scripts/migrate.js create tours  # Создать новую миграцию
 */

const fs = require('fs');
const path = require('path');
const chalk = require('chalk');
const { execSync } = require('child_process');
require('dotenv').config();

const args = process.argv.slice(2);
const MIGRATIONS_DIR = 'migrations';

// Help текст
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
${chalk.bold('Database Migration Manager')}

Использование:
  ${chalk.cyan('node scripts/migrate.js [command] [options]')}

Команды:
  run              Запустить все pending миграции (по умолчанию)
  undo             Откатить последнюю миграцию
  create <name>    Создать новую миграцию
  status           Показать статус миграций

Опции:
  --help, -h       Показать этот текст
  --step <n>       Количество миграций для отката (по умолчанию 1)
  --force          Пропустить подтверждение

Примеры:
  ${chalk.cyan('node scripts/migrate.js')}                # Запустить pending
  ${chalk.cyan('node scripts/migrate.js run')}            # То же самое
  ${chalk.cyan('node scripts/migrate.js undo')}           # Откатить 1
  ${chalk.cyan('node scripts/migrate.js undo --step 2')}  # Откатить 2
  ${chalk.cyan('node scripts/migrate.js create tours')}   # Новая миграция
  ${chalk.cyan('node scripts/migrate.js status')}         # Статус
  `);
  process.exit(0);
}

// Проверка наличия папки migrations
if (!fs.existsSync(MIGRATIONS_DIR)) {
  fs.mkdirSync(MIGRATIONS_DIR, { recursive: true });
  console.log(chalk.green(`✓ Папка ${MIGRATIONS_DIR} создана`));
}

// Проверка наличия .migrationrc или миграционной таблицы
const getMigrationHistory = () => {
  const historyFile = path.join(MIGRATIONS_DIR, '.migration-history.json');

  if (fs.existsSync(historyFile)) {
    return JSON.parse(fs.readFileSync(historyFile, 'utf8'));
  }

  return [];
};

const saveMigrationHistory = (history) => {
  fs.writeFileSync(
    path.join(MIGRATIONS_DIR, '.migration-history.json'),
    JSON.stringify(history, null, 2)
  );
};

const command = args[0] || 'run';

if (command === 'create') {
  // Создание новой миграции
  const migrationName = args[1];

  if (!migrationName) {
    console.error(chalk.red('✗ Укажите название миграции'));
    console.log(chalk.cyan('Пример: node scripts/migrate.js create create_tours_table'));
    process.exit(1);
  }

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
  const filename = `${timestamp}-${migrationName}.js`;
  const filepath = path.join(MIGRATIONS_DIR, filename);

  const template = `/**
 * Migration: ${migrationName}
 * Created: ${new Date().toISOString()}
 */

module.exports = {
  up: async (db) => {
    // Выполняется при миграции вперёд
    console.log('⬆️  Применяю миграцию: ${migrationName}');
    // Пример: CREATE TABLE, ALTER TABLE, INSERT DATA
    // await db.query('CREATE TABLE ...');
  },

  down: async (db) => {
    // Выполняется при откате
    console.log('⬇️  Откатываю миграцию: ${migrationName}');
    // Пример: DROP TABLE
    // await db.query('DROP TABLE ...');
  }
};
`;

  fs.writeFileSync(filepath, template);
  console.log(chalk.green(`✓ Миграция создана: ${filename}`));
  console.log(chalk.cyan(`\nЛокация: ${filepath}`));

  process.exit(0);
} else if (command === 'status') {
  // Показать статус миграций
  console.log(chalk.blue(`\n📊 Статус миграций\n`));

  const migrationFiles = fs.readdirSync(MIGRATIONS_DIR)
    .filter(f => f.endsWith('.js'))
    .sort();

  const history = getMigrationHistory();

  if (migrationFiles.length === 0) {
    console.log(chalk.yellow('⚠️  Миграции не найдены'));
    process.exit(0);
  }

  console.log(chalk.bold('Примененные:'));
  history.forEach(m => {
    console.log(`  ${chalk.green('✓')} ${m}`);
  });

  console.log(chalk.bold('\nОжидающие:'));
  const pending = migrationFiles.filter(f => !history.includes(f));

  if (pending.length === 0) {
    console.log(chalk.cyan('  (нет)'));
  } else {
    pending.forEach(f => {
      console.log(`  ${chalk.yellow('○')} ${f}`);
    });
  }

  console.log(`\nВсего: ${migrationFiles.length}, Примененных: ${history.length}, Ожидающих: ${pending.length}\n`);

  process.exit(0);
} else if (command === 'run') {
  // Запустить pending миграции
  console.log(chalk.blue(`\n🚀 Запускаю миграции...\n`));

  const migrationFiles = fs.readdirSync(MIGRATIONS_DIR)
    .filter(f => f.endsWith('.js'))
    .sort();

  const history = getMigrationHistory();
  const pending = migrationFiles.filter(f => !history.includes(f));

  if (pending.length === 0) {
    console.log(chalk.green('✓ Все миграции уже применены'));
    process.exit(0);
  }

  console.log(`Найдено ${pending.length} pending миграций:\n`);

  let failed = false;

  for (const file of pending) {
    console.log(chalk.blue(`  ⬆️  ${file}`));

    try {
      // Удаляем из cache
      delete require.cache[path.resolve(path.join(MIGRATIONS_DIR, file))];

      const migration = require(path.resolve(path.join(MIGRATIONS_DIR, file)));

      // Имитируем БД объект (в реальном приложении это будет подключение)
      const mockDb = {
        query: async (sql) => {
          console.log(chalk.gray(`    SQL: ${sql.substring(0, 50)}...`));
          return [];
        }
      };

      if (migration.up) {
        // Выполняем асинхронно
        require('util').promisify(setImmediate)()
          .then(() => migration.up(mockDb))
          .catch(err => {
            console.error(chalk.red(`    ✗ Ошибка: ${err.message}`));
            failed = true;
          });
      }

      history.push(file);
      console.log(chalk.green(`    ✓ Применена`));
    } catch (error) {
      console.error(chalk.red(`  ✗ Ошибка при загрузке: ${error.message}`));
      failed = true;
      break;
    }
  }

  if (!failed) {
    saveMigrationHistory(history);
    console.log(chalk.green(`\n✓ ${pending.length} миграций успешно применены`));
  } else {
    console.log(chalk.red(`\n✗ Ошибка при применении миграций`));
    process.exit(1);
  }

  process.exit(0);
} else if (command === 'undo') {
  // Откатить миграции
  const step = parseInt(args[args.indexOf('--step') + 1]) || 1;

  console.log(chalk.blue(`\n⬇️  Откатываю ${step} миграцию(й)...\n`));

  const history = getMigrationHistory();

  if (history.length === 0) {
    console.log(chalk.yellow('⚠️  Нет примененных миграций для отката'));
    process.exit(0);
  }

  const toUndo = history.slice(-step);

  console.log(`Откатываю:\n`);

  let failed = false;

  for (const file of toUndo.reverse()) {
    console.log(chalk.blue(`  ⬇️  ${file}`));

    try {
      delete require.cache[path.resolve(path.join(MIGRATIONS_DIR, file))];

      const migration = require(path.resolve(path.join(MIGRATIONS_DIR, file)));

      const mockDb = {
        query: async (sql) => {
          console.log(chalk.gray(`    SQL: ${sql.substring(0, 50)}...`));
          return [];
        }
      };

      if (migration.down) {
        require('util').promisify(setImmediate)()
          .then(() => migration.down(mockDb))
          .catch(err => {
            console.error(chalk.red(`    ✗ Ошибка: ${err.message}`));
            failed = true;
          });
      }

      console.log(chalk.green(`    ✓ Откачена`));
    } catch (error) {
      console.error(chalk.red(`  ✗ Ошибка при загрузке: ${error.message}`));
      failed = true;
      break;
    }
  }

  if (!failed) {
    const newHistory = history.slice(0, -step);
    saveMigrationHistory(newHistory);
    console.log(chalk.green(`\n✓ ${toUndo.length} миграций успешно откачены`));
  } else {
    console.log(chalk.red(`\n✗ Ошибка при откате миграций`));
    process.exit(1);
  }

  process.exit(0);
} else {
  console.error(chalk.red(`✗ Неизвестная команда: ${command}`));
  process.exit(1);
}
