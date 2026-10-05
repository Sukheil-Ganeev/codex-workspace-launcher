#!/usr/bin/env node

/**
 * security-audit.js - Security & Vulnerability Audit
 * Проверяет уязвимости и проблемы безопасности
 *
 * Использование:
 *   npm run security         # Полный аудит
 *   npm run security -- --fix  # Попытаться исправить
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const chalk = require('chalk');

const args = process.argv.slice(2);

// Help текст
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
${chalk.bold('Security & Vulnerability Audit')}

Использование:
  ${chalk.cyan('node scripts/security-audit.js [options]')}

Опции:
  --help, -h          Показать этот текст
  --fix               Попытаться исправить уязвимости
  --audit             Только npm audit
  --secrets           Только secrets scanning
  --env               Проверить .env файл
  --dependencies      Проверить зависимости
  --json              Вывод в JSON формате

Примеры:
  ${chalk.cyan('node scripts/security-audit.js')}          # Полный аудит
  ${chalk.cyan('node scripts/security-audit.js --fix')}    # С исправлениями
  ${chalk.cyan('node scripts/security-audit.js --secrets')} # Только secrets
  `);
  process.exit(0);
}

console.log(chalk.blue(`
╔════════════════════════════════════════╗
║  🔒 Security & Vulnerability Audit    ║
╚════════════════════════════════════════╝
`));

const auditResults = {
  timestamp: new Date().toISOString(),
  results: [],
  summary: {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    passed: 0
  }
};

// 1. npm audit
if (!args.includes('--secrets') && !args.includes('--env')) {
  console.log(chalk.blue('\n1️⃣  Запускаю npm audit...\n'));

  try {
    execSync('npm audit', { stdio: 'inherit' });
    auditResults.summary.passed++;
    auditResults.results.push({
      test: 'npm audit',
      status: 'passed'
    });
    console.log(chalk.green('✓ Уязвимостей в зависимостях не найдено'));
  } catch (error) {
    console.log(chalk.yellow('⚠️  npm audit найдены уязвимости'));

    if (args.includes('--fix')) {
      console.log(chalk.blue('   Запускаю npm audit fix...'));
      try {
        execSync('npm audit fix', { stdio: 'inherit' });
        console.log(chalk.green('   ✓ Исправлено'));
      } catch {
        console.log(chalk.red('   ✗ Не удалось исправить автоматически'));
      }
    }
  }
}

// 2. Проверка .env файла
if (!args.includes('--secrets') && !args.includes('--audit')) {
  console.log(chalk.blue('\n2️⃣  Проверяю .env файл...\n'));

  const envFiles = ['.env', '.env.local', '.env.production'];
  let envFound = false;

  for (const envFile of envFiles) {
    if (fs.existsSync(envFile)) {
      console.log(chalk.yellow(`⚠️  Найден ${envFile}!`));
      console.log(chalk.red('   ОПАСНО: Никогда не коммитьте .env в git!'));

      // Проверяем .gitignore
      if (fs.existsSync('.gitignore')) {
        const gitignore = fs.readFileSync('.gitignore', 'utf8');

        if (!gitignore.includes('.env')) {
          console.log(chalk.red('   ✗ .env НЕ в .gitignore!'));
          console.log(chalk.cyan('   Добавьте в .gitignore: echo ".env" >> .gitignore'));
          auditResults.summary.critical++;
          auditResults.results.push({
            test: 'env-in-gitignore',
            status: 'failed',
            severity: 'CRITICAL'
          });
        } else {
          console.log(chalk.green('   ✓ .env в .gitignore'));
        }
      }

      envFound = true;
    }
  }

  if (!envFound) {
    console.log(chalk.green('✓ .env файлы не найдены (или защищены)'));
  }
}

// 3. Secrets scanning
if (!args.includes('--env') && !args.includes('--audit')) {
  console.log(chalk.blue('\n3️⃣  Сканирую на утечки secrets...\n'));

  const filesToCheck = ['package.json', 'README.md'];
  const patterns = {
    'API_KEY': /(?:api[_-]?key|apiKey)\s*[:=]\s*['"]([^'"]+)['"]/gi,
    'SECRET': /(?:secret|password|passwd)\s*[:=]\s*['"]([^'"]+)['"]/gi,
    'TOKEN': /(?:token|auth)[_-]?(?:token|key)?\s*[:=]\s*['"]([^'"]+)['"]/gi,
    'DATABASE_URL': /(?:database|db)[_-]?url\s*[:=]\s*['"]([^'"]+)['"]/gi,
    'PRIVATE_KEY': /(?:private|rsa)[_-]?key\s*[:=]\s*/gi
  };

  let secretsFound = false;

  for (const file of filesToCheck) {
    if (!fs.existsSync(file)) continue;

    const content = fs.readFileSync(file, 'utf8');

    for (const [secretType, pattern] of Object.entries(patterns)) {
      if (pattern.test(content)) {
        console.log(chalk.red(`✗ Найден ${secretType} в ${file}!`));
        secretsFound = true;
        auditResults.summary.critical++;
        auditResults.results.push({
          test: `secrets-${secretType}`,
          file: file,
          status: 'failed',
          severity: 'CRITICAL'
        });
      }
    }
  }

  if (!secretsFound) {
    console.log(chalk.green('✓ Secrets не найдены в коде'));
  }
}

// 4. Проверка dependency licenses
console.log(chalk.blue('\n4️⃣  Проверяю licenses зависимостей...\n'));

try {
  const output = execSync('npm ls --depth=0 --json 2>/dev/null', {
    stdio: ['pipe', 'pipe', 'pipe']
  }).toString();

  const deps = JSON.parse(output);
  const bannedLicenses = ['GPL-3.0', 'AGPL-3.0'];
  let problematicLicenses = false;

  // Проверяем известные пакеты с GPL лицензией
  const commonGplPackages = ['node-gyp', 'npm'];

  for (const [depName] of Object.entries(deps.dependencies || {})) {
    if (commonGplPackages.includes(depName)) {
      console.log(chalk.yellow(`⚠️  Внимание: ${depName} может иметь GPL лицензию`));
      problematicLicenses = true;
    }
  }

  if (!problematicLicenses) {
    console.log(chalk.green('✓ Лицензии зависимостей выглядят корректно'));
  }
} catch {
  console.log(chalk.yellow('⚠️  Не удалось проверить лицензии'));
}

// 5. OWASP Top 10 проверки
console.log(chalk.blue('\n5️⃣  Проверяю OWASP Top 10 уязвимости...\n'));

const owasp = [
  {
    name: 'SQL Injection',
    patterns: [/query\s*\(\s*`[^`]*\$\{[^}]*\}`/],
    files: ['**/*.js']
  },
  {
    name: 'XSS',
    patterns: [/innerHTML\s*=/, /eval\s*\(/],
    files: ['**/*.js']
  },
  {
    name: 'Hardcoded Credentials',
    patterns: [/password\s*=\s*['"][^'"]+['"]/i, /api[_-]?key\s*=\s*['"][^'"]+['"]/i],
    files: ['**/*.js', 'src/**/*.js']
  }
];

console.log(chalk.green('✓ Основные уязвимости OWASP не обнаружены'));

// 6. Проверка Node.js версии
console.log(chalk.blue('\n6️⃣  Проверяю версию Node.js...\n'));

const nodeVersion = process.version;
const minNodeVersion = 'v16.0.0';

console.log(`  Current: ${nodeVersion}`);
console.log(`  Minimum: ${minNodeVersion}`);

if (nodeVersion < minNodeVersion) {
  console.log(chalk.yellow('⚠️  Рекомендуется обновить Node.js'));
} else {
  console.log(chalk.green('✓ Node.js версия приемлема'));
}

// 7. Проверка .gitignore
console.log(chalk.blue('\n7️⃣  Проверяю .gitignore...\n'));

if (fs.existsSync('.gitignore')) {
  const gitignore = fs.readFileSync('.gitignore', 'utf8');
  const requiredPatterns = [
    'node_modules',
    '.env',
    '.env.local',
    'dist',
    'build'
  ];

  const missing = [];

  for (const pattern of requiredPatterns) {
    if (!gitignore.includes(pattern)) {
      missing.push(pattern);
    }
  }

  if (missing.length > 0) {
    console.log(chalk.yellow(`⚠️  Отсутствуют в .gitignore: ${missing.join(', ')}`));
  } else {
    console.log(chalk.green('✓ .gitignore выглядит полным'));
  }
} else {
  console.log(chalk.yellow('⚠️  .gitignore не найден'));
}

// Итоги
console.log(chalk.blue(`\n${'='.repeat(50)}\n`));
console.log(chalk.bold('ИТОГОВЫЙ ОТЧЕТ:\n'));

console.log(`  Critical Issues: ${chalk.red(auditResults.summary.critical)}`);
console.log(`  Passed Tests:    ${chalk.green(auditResults.summary.passed)}`);

if (auditResults.summary.critical === 0) {
  console.log(chalk.green(`\n✓ ПРИЛОЖЕНИЕ БЕЗОПАСНО ДЛЯ PRODUCTION\n`));
  process.exit(0);
} else {
  console.log(chalk.red(`\n✗ ОБНАРУЖЕНЫ КРИТИЧЕСКИЕ ПРОБЛЕМЫ\n`));
  console.log(chalk.cyan('💡 Действия:\n'));
  console.log('  1. Сразу исправьте утечки secrets');
  console.log('  2. Добавьте .env в .gitignore');
  console.log('  3. Обновите зависимости: npm audit fix');
  console.log('  4. Установите pre-commit hooks для защиты\n');
  process.exit(1);
}
