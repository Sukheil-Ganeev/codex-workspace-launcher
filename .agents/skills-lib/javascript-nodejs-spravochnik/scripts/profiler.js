#!/usr/bin/env node

/**
 * profiler.js - Performance Profiler
 * Профилирует производительность приложения
 *
 * Использование:
 *   npm run profile           # Профилировать приложение
 *   npm run profile -- --duration 30  # 30 секунд
 */

const fs = require('fs');
const path = require('path');
const chalk = require('chalk');
const { execSync } = require('child_process');

const args = process.argv.slice(2);

// Help текст
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
${chalk.bold('Performance Profiler')}

Использование:
  ${chalk.cyan('node scripts/profiler.js [options]')}

Опции:
  --help, -h          Показать этот текст
  --duration <sec>    Длительность профилирования (по умолчанию 10)
  --memory            Только memory profiling
  --cpu               Только CPU profiling
  --sample-rate <n>   Sample rate в Hz (по умолчанию 100)
  --output <file>     Файл для сохранения

Примеры:
  ${chalk.cyan('node scripts/profiler.js')}                    # 10 сек профилирования
  ${chalk.cyan('node scripts/profiler.js --duration 30')}      # 30 сек
  ${chalk.cyan('node scripts/profiler.js --memory')}           # Только память
  ${chalk.cyan('node scripts/profiler.js --cpu')}              # Только CPU
  `);
  process.exit(0);
}

console.log(chalk.blue(`
╔════════════════════════════════════════╗
║  📊 Performance Profiler               ║
╚════════════════════════════════════════╝
`));

// Получаем параметры
const getArgValue = (flag) => {
  const index = args.indexOf(flag);
  return index >= 0 && args[index + 1] ? args[index + 1] : null;
};

const duration = parseInt(getArgValue('--duration')) || 10;
const profileMemory = !args.includes('--cpu');
const profileCpu = !args.includes('--memory');
const outputFile = getArgValue('--output') || 'profile.json';

console.log(`
Параметры:
  Длительность:    ${duration}s
  CPU:             ${profileCpu ? 'включен' : 'отключен'}
  Memory:          ${profileMemory ? 'включена' : 'отключена'}
  Выходной файл:   ${outputFile}

`);

// Функция для анализа памяти
function profileMemory() {
  const snapshot = process.memoryUsage();

  return {
    timestamp: new Date().toISOString(),
    memory: {
      rss: `${(snapshot.rss / 1024 / 1024).toFixed(2)} MB`,
      heapTotal: `${(snapshot.heapTotal / 1024 / 1024).toFixed(2)} MB`,
      heapUsed: `${(snapshot.heapUsed / 1024 / 1024).toFixed(2)} MB`,
      external: `${(snapshot.external / 1024 / 1024).toFixed(2)} MB`,
      arrayBuffers: `${(snapshot.arrayBuffers / 1024 / 1024).toFixed(2)} MB`
    },
    uptime: process.uptime().toFixed(2),
    cpuUsage: process.cpuUsage()
  };
}

// Функция для анализа CPU
function getProcessStats() {
  const stats = process.cpuUsage();
  const uptime = process.uptime();

  return {
    userTime: stats.user / 1000,
    systemTime: stats.system / 1000,
    totalTime: (stats.user + stats.system) / 1000,
    uptime: uptime,
    cpuPercent: ((((stats.user + stats.system) / 1000) / uptime) * 100).toFixed(2)
  };
}

// Профилирование
console.log(chalk.yellow(`Профилирую ${duration}s...\n`));

const profiles = [];
const startTime = Date.now();
const interval = setInterval(() => {
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  const progress = (elapsed / duration * 100).toFixed(0);

  process.stdout.write(`\rПрогресс: ${progress}% [${elapsed}s/${duration}s]`);

  if (profileMemory || profileCpu) {
    profiles.push({
      time: elapsed,
      memory: profileMemory ? profileMemory() : null,
      cpu: profileCpu ? getProcessStats() : null
    });
  }
}, 100);

// Завершение профилирования
setTimeout(() => {
  clearInterval(interval);

  console.log('\n');

  // Анализируем результаты
  if (profiles.length > 0) {
    console.log(chalk.blue('\n📊 Результаты профилирования:\n'));

    const firstProfile = profiles[0];
    const lastProfile = profiles[profiles.length - 1];

    if (profileMemory) {
      console.log(chalk.bold('Memory Usage:'));
      console.log(`  Начально:    ${firstProfile.memory.memory.heapUsed}`);
      console.log(`  Конечно:     ${lastProfile.memory.memory.heapUsed}`);

      const heapGrowth = parseFloat(lastProfile.memory.memory.heapUsed) -
                         parseFloat(firstProfile.memory.memory.heapUsed);
      const heapGrowthStr = heapGrowth > 0 ? `+${heapGrowth.toFixed(2)}` : `${heapGrowth.toFixed(2)}`;

      console.log(`  Прирост:     ${heapGrowthStr} MB`);
      console.log(`  Макс RSS:    ${lastProfile.memory.memory.rss}`);
    }

    if (profileCpu) {
      console.log(chalk.bold('\nCPU Usage:'));
      console.log(`  Процесс вверх: ${lastProfile.cpu.uptime}s`);
      console.log(`  User time:     ${lastProfile.cpu.userTime.toFixed(3)}s`);
      console.log(`  System time:   ${lastProfile.cpu.systemTime.toFixed(3)}s`);
      console.log(`  CPU %:         ${lastProfile.cpu.cpuPercent}%`);
    }

    console.log(chalk.bold('\nВремя исполнения:'));
    console.log(`  Начало:      ${new Date(startTime).toLocaleTimeString()}`);
    console.log(`  Конец:       ${new Date().toLocaleTimeString()}`);
    console.log(`  Длительность: ${duration}s`);

    // Сохраняем результаты
    const report = {
      title: 'Performance Profile Report',
      timestamp: new Date().toISOString(),
      duration: duration,
      sampling: {
        count: profiles.length,
        interval: '100ms'
      },
      summary: {
        memory: profileMemory ? {
          initial: firstProfile.memory.memory.heapUsed,
          final: lastProfile.memory.memory.heapUsed,
          maxRss: lastProfile.memory.memory.rss
        } : null,
        cpu: profileCpu ? {
          userTime: lastProfile.cpu.userTime,
          systemTime: lastProfile.cpu.systemTime,
          cpuPercent: lastProfile.cpu.cpuPercent
        } : null
      },
      profiles: profiles.slice(0, profiles.length - 1) // Исключаем последний
    };

    fs.writeFileSync(outputFile, JSON.stringify(report, null, 2));

    console.log(chalk.green(`\n✓ Результаты сохранены в ${outputFile}`));

    // Даем рекомендации
    console.log(chalk.blue('\n💡 Рекомендации:\n'));

    if (profileMemory) {
      const heapUsed = parseFloat(lastProfile.memory.memory.heapUsed);

      if (heapUsed > 100) {
        console.log(chalk.yellow('  ⚠️  Высокое использование памяти (> 100MB)'));
        console.log('      - Проверьте наличие memory leaks');
        console.log('      - Используйте LRU cache для ограничения размера');
      }
    }

    if (profileCpu) {
      const cpuPercent = parseFloat(lastProfile.cpu.cpuPercent);

      if (cpuPercent > 50) {
        console.log(chalk.yellow('  ⚠️  Высокое использование CPU (> 50%)'));
        console.log('      - Оптимизируйте алгоритмы');
        console.log('      - Используйте кеширование');
      }
    }
  }

  console.log('\n');
  process.exit(0);
}, duration * 1000);

// Graceful shutdown
process.on('SIGINT', () => {
  clearInterval(interval);
  console.log(chalk.yellow('\n\nПрофилирование остановлено пользователем'));
  process.exit(0);
});
