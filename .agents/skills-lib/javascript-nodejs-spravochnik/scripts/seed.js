#!/usr/bin/env node

/**
 * seed.js - Database Seeding Script
 * Заполняет БД тестовыми/начальными данными
 *
 * Использование:
 *   npm run seed              # Запустить все seeders
 *   node scripts/seed.js tours   # Конкретный seeder
 *   node scripts/seed.js create  # Создать новый seeder
 */

const fs = require('fs');
const path = require('path');
const chalk = require('chalk');
require('dotenv').config();

const args = process.argv.slice(2);
const SEEDERS_DIR = 'seeders';

// Help текст
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
${chalk.bold('Database Seeder')}

Использование:
  ${chalk.cyan('node scripts/seed.js [command] [options]')}

Команды:
  run             Запустить все seeders (по умолчанию)
  run <name>      Запустить конкретный seeder
  create <name>   Создать новый seeder

Опции:
  --help, -h      Показать этот текст
  --force         Пропустить подтверждение
  --list          Показать доступные seeders

Примеры:
  ${chalk.cyan('node scripts/seed.js')}           # Запустить все
  ${chalk.cyan('node scripts/seed.js tours')}     # Запустить tours seeder
  ${chalk.cyan('node scripts/seed.js create users')} # Создать seeder
  ${chalk.cyan('node scripts/seed.js --list')}    # Список seeders
  `);
  process.exit(0);
}

// Создание папки если её нет
if (!fs.existsSync(SEEDERS_DIR)) {
  fs.mkdirSync(SEEDERS_DIR, { recursive: true });
  console.log(chalk.green(`✓ Папка ${SEEDERS_DIR} создана`));
}

const command = args[0];

if (command === 'create') {
  // Создание нового seeder
  const seederName = args[1];

  if (!seederName) {
    console.error(chalk.red('✗ Укажите название seeder'));
    console.log(chalk.cyan('Пример: node scripts/seed.js create tours'));
    process.exit(1);
  }

  const filename = `${seederName}-seeder.js`;
  const filepath = path.join(SEEDERS_DIR, filename);

  const template = `/**
 * Seeder: ${seederName}
 * Описание: Заполняет БД данными для ${seederName}
 * Created: ${new Date().toISOString()}
 */

module.exports = {
  // Название для логирования
  name: '${seederName}',

  // Функция для выполнения seeding
  run: async (db, sequelize) => {
    console.log(\`🌱 Заполняю ${seederName}...\`);

    // Пример данных
    const data = [
      // { id: 1, name: 'Item 1', ... }
    ];

    // Вставляем данные в БД
    // await Model.bulkCreate(data);
    // или
    // for (const item of data) {
    //   await Model.create(item);
    // }

    console.log(\`✓ ${seederName} заполнен (\${data.length} записей)\`);
    return data;
  }
};
`;

  fs.writeFileSync(filepath, template);
  console.log(chalk.green(`✓ Seeder создан: ${filename}`));
  console.log(chalk.cyan(`\nЛокация: ${filepath}`));
  console.log(chalk.cyan('\nОтредактируйте файл и добавьте логику заполнения БД'));

  process.exit(0);
} else if (args.includes('--list')) {
  // Показать доступные seeders
  console.log(chalk.blue(`\n📋 Доступные seeders\n`));

  const seederFiles = fs.readdirSync(SEEDERS_DIR)
    .filter(f => f.endsWith('.js'))
    .sort();

  if (seederFiles.length === 0) {
    console.log(chalk.yellow('  (нет)'));
  } else {
    seederFiles.forEach(f => {
      console.log(`  • ${chalk.cyan(f)}`);
    });
  }

  console.log();
  process.exit(0);
} else {
  // Запустить seeders
  const specifySeeder = command && !command.startsWith('-');
  const seederToRun = specifySeeder ? command : null;

  console.log(chalk.blue(`\n🌱 Выполняю seeding...\n`));

  let seederFiles = fs.readdirSync(SEEDERS_DIR)
    .filter(f => f.endsWith('.js'))
    .sort();

  if (seederToRun) {
    const fullName = seederToRun.endsWith('-seeder.js')
      ? seederToRun
      : `${seederToRun}-seeder.js`;

    seederFiles = seederFiles.filter(f => f === fullName);

    if (seederFiles.length === 0) {
      console.error(chalk.red(`✗ Seeder не найден: ${fullName}`));
      process.exit(1);
    }
  }

  if (seederFiles.length === 0) {
    console.log(chalk.yellow('⚠️  Seeders не найдены'));
    console.log(chalk.cyan('\nСоздайте seeder:'));
    console.log(chalk.cyan('  node scripts/seed.js create tours\n'));
    process.exit(0);
  }

  console.log(`Найдено ${seederFiles.length} seeder(ов):\n`);

  let failed = false;
  const results = [];

  for (const file of seederFiles) {
    console.log(chalk.blue(`  📝 ${file}`));

    try {
      delete require.cache[path.resolve(path.join(SEEDERS_DIR, file))];

      const seeder = require(path.resolve(path.join(SEEDERS_DIR, file)));

      if (seeder.run) {
        const mockDb = {
          query: async (sql) => {
            console.log(chalk.gray(`     SQL: ${sql.substring(0, 50)}...`));
            return [];
          }
        };

        const startTime = Date.now();
        const result = seeder.run(mockDb, null);

        if (result && result.then) {
          // Если возвращает Promise
          Promise.resolve(result)
            .then(data => {
              const duration = ((Date.now() - startTime) / 1000).toFixed(2);
              console.log(chalk.green(`     ✓ Готово за ${duration}s`));
              results.push({ file, success: true, data });
            })
            .catch(err => {
              console.error(chalk.red(`     ✗ Ошибка: ${err.message}`));
              failed = true;
            });
        } else {
          console.log(chalk.green(`     ✓ Готово`));
          results.push({ file, success: true });
        }
      } else {
        console.warn(chalk.yellow(`     ⚠️  run функция не найдена`));
      }
    } catch (error) {
      console.error(chalk.red(`  ✗ Ошибка при загрузке: ${error.message}`));
      failed = true;
      break;
    }
  }

  // Статистика
  const successful = results.filter(r => r.success).length;

  console.log(chalk.blue(`\n${'='.repeat(40)}`));

  if (!failed && successful > 0) {
    console.log(chalk.green(`\n✓ ${successful} seeder(ов) успешно выполнено\n`));
  } else if (failed) {
    console.log(chalk.red(`\n✗ Ошибка при выполнении seeding\n`));
    process.exit(1);
  } else {
    console.log(chalk.yellow(`\n⚠️  Нет выполненных seeders\n`));
  }

  process.exit(0);
}
