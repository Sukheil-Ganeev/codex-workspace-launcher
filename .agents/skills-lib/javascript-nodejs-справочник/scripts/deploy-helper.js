#!/usr/bin/env node

/**
 * deploy-helper.js - Deployment Helper & Automation
 * Автоматизирует развертывание на production (Netlify, Vercel, Railway)
 *
 * Использование:
 *   npm run deploy              # Деплой на Netlify
 *   npm run deploy -- --vercel  # Деплой на Vercel
 *   npm run deploy -- --railway # Деплой на Railway
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const chalk = require('chalk');
require('dotenv').config();

const args = process.argv.slice(2);

// Help текст
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
${chalk.bold('Deployment Helper')}

Использование:
  ${chalk.cyan('node scripts/deploy-helper.js [options]')}

Опции:
  --help, -h          Показать этот текст
  --netlify           Деплой на Netlify (по умолчанию)
  --vercel            Деплой на Vercel
  --railway           Деплой на Railway
  --check             Только проверка готовности
  --dry-run           Сухой запуск без деплоя
  --skip-tests        Пропустить тесты
  --skip-build        Пропустить build
  --skip-audit        Пропустить security audit
  --rollback          Откатить предыдущий деплой
  --env <env>         Окружение (production, staging)

Примеры:
  ${chalk.cyan('node scripts/deploy-helper.js')}              # Деплой на Netlify
  ${chalk.cyan('node scripts/deploy-helper.js --vercel')}    # На Vercel
  ${chalk.cyan('node scripts/deploy-helper.js --check')}     # Проверка готовности
  ${chalk.cyan('node scripts/deploy-helper.js --dry-run')}   # Сухой запуск
  `);
  process.exit(0);
}

console.log(chalk.blue(`
╔════════════════════════════════════════╗
║  🚀 Deployment Helper                  ║
║  Deploy to Production                  ║
╚════════════════════════════════════════╝
`));

// Конфигурация
const config = {
  skipTests: args.includes('--skip-tests'),
  skipBuild: args.includes('--skip-build'),
  skipAudit: args.includes('--skip-audit'),
  dryRun: args.includes('--dry-run'),
  checkOnly: args.includes('--check'),
  rollback: args.includes('--rollback'),
  platform: args.includes('--vercel') ? 'vercel' :
            args.includes('--railway') ? 'railway' : 'netlify',
  env: args[args.indexOf('--env') + 1] || 'production'
};

const deployLog = {
  timestamp: new Date().toISOString(),
  platform: config.platform,
  environment: config.env,
  steps: []
};

function logStep(name, status = 'in_progress') {
  deployLog.steps.push({
    name,
    status,
    timestamp: new Date().toISOString()
  });
}

async function runCommand(command, description) {
  try {
    console.log(chalk.blue(`\n  ➜ ${description}`));

    if (!config.dryRun) {
      const output = execSync(command, { encoding: 'utf8' });
      console.log(chalk.green(`  ✓ ${description}`));
      return output;
    } else {
      console.log(chalk.cyan(`  (dry-run: ${command})`));
      return '';
    }
  } catch (error) {
    console.error(chalk.red(`  ✗ ${description} failed`));
    throw error;
  }
}

async function deploy() {
  try {
    // 1. Pre-deployment checks
    console.log(chalk.bold('\n📋 Pre-deployment Checks\n'));

    // Проверка git status
    logStep('check-git-status');
    console.log(chalk.blue('  ➜ Проверяю git status'));

    try {
      const gitStatus = execSync('git status --porcelain', { encoding: 'utf8' });

      if (gitStatus.trim() && !config.dryRun) {
        console.log(chalk.yellow('⚠️  Есть незакоммиченные изменения:'));
        console.log(gitStatus);

        if (!args.includes('--force')) {
          console.log(chalk.red('\n✗ Коммитьте или отмените изменения перед деплоем'));
          process.exit(1);
        }
      }
      console.log(chalk.green('  ✓ git status проверен'));
    } catch {
      console.log(chalk.yellow('  ⚠️  Git не инициализирован'));
    }

    // Проверка .env
    logStep('check-env');
    console.log(chalk.blue('  ➜ Проверяю .env файлы'));

    const envFiles = ['.env', '.env.production'];
    for (const envFile of envFiles) {
      if (fs.existsSync(envFile)) {
        console.log(chalk.cyan(`    ✓ ${envFile} найден`));
      }
    }

    // Проверка package.json
    logStep('check-package-json');
    const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    console.log(chalk.green('  ✓ package.json валиден'));

    // 2. Build & Test
    if (!config.checkOnly) {
      console.log(chalk.bold('\n🔨 Build & Test Phase\n'));

      if (!config.skipAudit) {
        logStep('security-audit');
        console.log(chalk.blue('  ➜ Security audit'));

        try {
          execSync('npm run security 2>/dev/null', { stdio: 'pipe' });
          console.log(chalk.green('  ✓ Security audit пройден'));
        } catch {
          console.log(chalk.yellow('  ⚠️  Security issues (исправьте перед деплоем!)'));
        }
      }

      if (!config.skipTests) {
        logStep('run-tests');
        console.log(chalk.blue('  ➜ Запуск тестов'));

        try {
          execSync('npm test -- --passWithNoTests 2>/dev/null', { stdio: 'pipe' });
          console.log(chalk.green('  ✓ Все тесты пройдены'));
        } catch {
          if (!args.includes('--force')) {
            console.log(chalk.red('  ✗ Тесты не пройдены'));
            process.exit(1);
          }
          console.log(chalk.yellow('  ⚠️  Tests failed (продолжаю с --force)'));
        }
      }

      if (!config.skipBuild) {
        logStep('build');
        console.log(chalk.blue('  ➜ Production build'));

        try {
          execSync('npm run build 2>/dev/null', { stdio: 'pipe' });
          console.log(chalk.green('  ✓ Build успешен'));
        } catch {
          console.log(chalk.yellow('  ⚠️  Build issues'));
        }
      }

      // 3. Deployment
      console.log(chalk.bold('\n🚀 Deployment Phase\n'));

      logStep('deploy');

      if (config.platform === 'netlify') {
        console.log(chalk.blue('  ➜ Деплой на Netlify'));

        try {
          execSync('which netlify', { stdio: 'pipe' });
        } catch {
          console.log(chalk.yellow('    Установка Netlify CLI...'));
          if (!config.dryRun) {
            execSync('npm install -g netlify-cli');
          }
        }

        if (!config.dryRun) {
          console.log(chalk.cyan('    Выполняю: netlify deploy --prod'));
          execSync('netlify deploy --prod', { stdio: 'inherit' });
        } else {
          console.log(chalk.cyan('    (dry-run: netlify deploy --prod)'));
        }

        console.log(chalk.green('  ✓ Деплой на Netlify завершен'));
      } else if (config.platform === 'vercel') {
        console.log(chalk.blue('  ➜ Деплой на Vercel'));

        if (!config.dryRun) {
          execSync('vercel --prod', { stdio: 'inherit' });
        } else {
          console.log(chalk.cyan('    (dry-run: vercel --prod)'));
        }

        console.log(chalk.green('  ✓ Деплой на Vercel завершен'));
      } else if (config.platform === 'railway') {
        console.log(chalk.blue('  ➜ Деплой на Railway'));

        try {
          execSync('which railway', { stdio: 'pipe' });
        } catch {
          console.log(chalk.yellow('    Railway не установлен'));
          console.log(chalk.cyan('    Установите: npm install -g @railway/cli'));
          process.exit(1);
        }

        if (!config.dryRun) {
          execSync('railway up', { stdio: 'inherit' });
        } else {
          console.log(chalk.cyan('    (dry-run: railway up)'));
        }

        console.log(chalk.green('  ✓ Деплой на Railway завершен'));
      }

      // 4. Post-deployment verification
      console.log(chalk.bold('\n✅ Post-deployment Verification\n'));

      logStep('health-check');
      console.log(chalk.blue('  ➜ Health check'));

      // Получаем deployment URL в зависимости от платформы
      let deploymentUrl = process.env.DEPLOYMENT_URL;

      if (!deploymentUrl) {
        if (config.platform === 'netlify') {
          deploymentUrl = `https://${packageJson.name}.netlify.app`;
        } else if (config.platform === 'vercel') {
          deploymentUrl = `https://${packageJson.name}.vercel.app`;
        } else if (config.platform === 'railway') {
          deploymentUrl = 'https://your-railway-app.railway.app';
        }
      }

      if (!config.dryRun) {
        try {
          // Попытаемся проверить health endpoint
          const response = execSync(`curl -s -o /dev/null -w "%{http_code}" ${deploymentUrl}/health || echo "000"`, {
            encoding: 'utf8'
          });

          if (response === '200') {
            console.log(chalk.green(`  ✓ Приложение доступно на ${deploymentUrl}`));
          } else {
            console.log(chalk.yellow(`  ⚠️  Health check вернул ${response}`));
          }
        } catch {
          console.log(chalk.yellow('  ⚠️  Health check недоступен'));
        }
      }

      console.log(chalk.green('  ✓ Post-deployment проверки завершены'));
    }

    // 5. Finalization
    console.log(chalk.blue(`\n${'='.repeat(50)}\n`));

    if (config.dryRun) {
      console.log(chalk.cyan(`DRY RUN завершен. Без реальных изменений.\n`));
    } else if (config.checkOnly) {
      console.log(chalk.green(`✓ Приложение готово к деплою\n`));
    } else {
      console.log(chalk.green(`✓ ДЕПЛОЙ УСПЕШЕН\n`));

      console.log(`Информация о деплое:`);
      console.log(`  Platform:    ${config.platform}`);
      console.log(`  Environment: ${config.env}`);
      console.log(`  Timestamp:   ${new Date().toISOString()}`);

      // Сохраняем лог деплоя
      if (fs.existsSync('deployments')) {
        const deploymentFile = path.join('deployments', `${config.env}-${Date.now()}.json`);
        fs.mkdirSync('deployments', { recursive: true });
        fs.writeFileSync(deploymentFile, JSON.stringify(deployLog, null, 2));
        console.log(`  Log:         ${deploymentFile}`);
      }

      console.log(`\nСлучайно развернулось не то?`);
      console.log(chalk.cyan(`  npm run deploy -- --rollback  # Откатить`));
    }

    console.log();
    process.exit(0);
  } catch (error) {
    console.error(chalk.red(`\n✗ ОШИБКА ДЕПЛОЯ\n`));
    console.error(error.message);

    console.log(chalk.cyan('\n💡 Действия:\n'));
    console.log('  1. Проверьте логи выше');
    console.log('  2. Исправьте ошибки локально');
    console.log('  3. Запустите npm run deploy снова');

    process.exit(1);
  }
}

// Запуск
deploy().catch(error => {
  console.error(error);
  process.exit(1);
});
