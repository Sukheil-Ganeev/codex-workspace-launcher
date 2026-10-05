#!/usr/bin/env node
/**
 * Affiliate Click Tracker
 * Отслеживание кликов по партнёрским ссылкам
 */

const fs = require('fs');
const path = require('path');

class AffiliateClickTracker {
  constructor(logFile = 'affiliate-clicks.json') {
    this.logFile = logFile;
    this.clicks = this.loadClicks();
  }

  /**
   * Загрузить клики из файла
   */
  loadClicks() {
    if (fs.existsSync(this.logFile)) {
      const data = fs.readFileSync(this.logFile, 'utf8');
      return JSON.parse(data);
    }
    return [];
  }

  /**
   * Сохранить клики в файл
   */
  saveClicks() {
    fs.writeFileSync(this.logFile, JSON.stringify(this.clicks, null, 2));
  }

  /**
   * Зарегистрировать клик
   * @param {object} click - Данные клика
   */
  trackClick(click) {
    const clickData = {
      timestamp: new Date().toISOString(),
      platform: click.platform || 'unknown',
      affiliate: click.affiliate || 'unknown',
      link: click.link || '',
      source: click.source || 'direct',
      medium: click.medium || '',
      campaign: click.campaign || '',
      content: click.content || '',
      userId: click.userId || null
    };

    this.clicks.push(clickData);
    this.saveClicks();

    console.log(`✓ Клик зарегистрирован: ${click.affiliate} (${click.platform})`);
    return clickData;
  }

  /**
   * Получить статистику кликов
   * @param {string} period - Период ('today', 'week', 'month', 'all')
   */
  getStats(period = 'all') {
    const now = new Date();
    let startDate;

    switch(period) {
      case 'today':
        startDate = new Date(now.setHours(0, 0, 0, 0));
        break;
      case 'week':
        startDate = new Date(now.setDate(now.getDate() - 7));
        break;
      case 'month':
        startDate = new Date(now.setMonth(now.getMonth() - 1));
        break;
      default:
        startDate = new Date(0);
    }

    // Фильтровать клики по периоду
    const filteredClicks = this.clicks.filter(click => {
      return new Date(click.timestamp) >= startDate;
    });

    // Группировать по affiliate
    const byAffiliate = {};
    filteredClicks.forEach(click => {
      const affiliate = click.affiliate;
      if (!byAffiliate[affiliate]) {
        byAffiliate[affiliate] = {
          total_clicks: 0,
          platforms: {},
          campaigns: {}
        };
      }

      byAffiliate[affiliate].total_clicks++;

      // По платформам
      const platform = click.platform;
      byAffiliate[affiliate].platforms[platform] =
        (byAffiliate[affiliate].platforms[platform] || 0) + 1;

      // По кампаниям
      if (click.campaign) {
        byAffiliate[affiliate].campaigns[click.campaign] =
          (byAffiliate[affiliate].campaigns[click.campaign] || 0) + 1;
      }
    });

    return {
      period: period,
      total_clicks: filteredClicks.length,
      by_affiliate: byAffiliate,
      recent_clicks: filteredClicks.slice(-10).reverse()
    };
  }

  /**
   * Показать отчёт
   */
  printReport(period = 'month') {
    const stats = this.getStats(period);

    console.log('\n' + '='.repeat(60));
    console.log(`ОТЧЁТ ПО AFFILIATE КЛИКАМ (${period})`);
    console.log('='.repeat(60));
    console.log(`Всего кликов: ${stats.total_clicks}`);
    console.log('\nПо партнёрским программам:');
    console.log('-'.repeat(60));

    Object.entries(stats.by_affiliate).forEach(([affiliate, data]) => {
      console.log(`\n${affiliate}:`);
      console.log(`  Всего кликов: ${data.total_clicks}`);
      console.log('  По платформам:');
      Object.entries(data.platforms).forEach(([platform, count]) => {
        console.log(`    ${platform}: ${count} (${((count/data.total_clicks)*100).toFixed(1)}%)`);
      });

      if (Object.keys(data.campaigns).length > 0) {
        console.log('  По кампаниям:');
        Object.entries(data.campaigns).forEach(([campaign, count]) => {
          console.log(`    ${campaign}: ${count}`);
        });
      }
    });

    console.log('\n' + '='.repeat(60));
    console.log('Последние 10 кликов:');
    console.log('-'.repeat(60));

    stats.recent_clicks.forEach((click, index) => {
      const date = new Date(click.timestamp).toLocaleString('ru-RU');
      console.log(`${index + 1}. ${date} - ${click.affiliate} (${click.platform})`);
      if (click.campaign) {
        console.log(`   Кампания: ${click.campaign}`);
      }
    });

    console.log('='.repeat(60) + '\n');
  }

  /**
   * Экспортировать в CSV
   */
  exportCSV(filename = 'affiliate-clicks.csv') {
    const headers = ['Timestamp', 'Platform', 'Affiliate', 'Source', 'Medium', 'Campaign', 'Content'];
    const rows = this.clicks.map(click => [
      click.timestamp,
      click.platform,
      click.affiliate,
      click.source,
      click.medium,
      click.campaign,
      click.content
    ]);

    const csv = [headers, ...rows]
      .map(row => row.join(','))
      .join('\n');

    fs.writeFileSync(filename, csv);
    console.log(`✓ Экспортировано в ${filename}`);
  }
}

// Пример использования

if (require.main === module) {
  const tracker = new AffiliateClickTracker('data/affiliate-clicks.json');

  // Команды CLI
  const args = process.argv.slice(2);
  const command = args[0];

  if (command === 'track') {
    // node track-affiliate-clicks.js track --platform=telegram --affiliate=booking --campaign=dubai_march
    const click = {};
    args.slice(1).forEach(arg => {
      const [key, value] = arg.replace('--', '').split('=');
      click[key] = value;
    });

    tracker.trackClick(click);
  }
  else if (command === 'report') {
    // node track-affiliate-clicks.js report --period=month
    const period = args.find(arg => arg.startsWith('--period='))?.split('=')[1] || 'month';
    tracker.printReport(period);
  }
  else if (command === 'export') {
    // node track-affiliate-clicks.js export --file=clicks.csv
    const filename = args.find(arg => arg.startsWith('--file='))?.split('=')[1] || 'affiliate-clicks.csv';
    tracker.exportCSV(filename);
  }
  else {
    console.log('Affiliate Click Tracker');
    console.log('\nИспользование:');
    console.log('  node track-affiliate-clicks.js track --platform=telegram --affiliate=booking --campaign=dubai_march');
    console.log('  node track-affiliate-clicks.js report --period=month');
    console.log('  node track-affiliate-clicks.js export --file=clicks.csv');
    console.log('\nПримеры:');
    console.log('  Зарегистрировать клик:');
    console.log('    node track-affiliate-clicks.js track --platform=telegram --affiliate=booking --source=post --campaign=dubai_hotels');
    console.log('  Показать отчёт за неделю:');
    console.log('    node track-affiliate-clicks.js report --period=week');
    console.log('  Экспортировать в CSV:');
    console.log('    node track-affiliate-clicks.js export --file=february-clicks.csv');
  }
}

module.exports = AffiliateClickTracker;
