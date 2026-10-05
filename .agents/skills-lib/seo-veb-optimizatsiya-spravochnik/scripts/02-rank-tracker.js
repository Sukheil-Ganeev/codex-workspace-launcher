#!/usr/bin/env node

/**
 * Rank Position Tracker
 * Tracks keyword rankings over time with comparison to historical data
 * Usage: npm run rank
 */

import { google } from 'googleapis';
import fs from 'fs';
import chalk from 'chalk';
import ora from 'ora';
import config from './config/api-keys.config.js';

const searchconsole = google.searchconsole('v1');

class RankTracker {
  constructor() {
    this.auth = null;
    this.dataPath = './exports/rank-history.json';
    this.initialize();
  }

  /**
   * Initialize authentication
   */
  initialize() {
    try {
      const credentials = config.getGoogleCredentials();
      this.auth = new google.auth.GoogleAuth({
        credentials,
        scopes: ['https://www.googleapis.com/auth/webmasters.readonly']
      });
      console.log(chalk.green('✓ Authentication initialized'));
    } catch (e) {
      console.error(chalk.red('✗ Error:'), e.message);
      process.exit(1);
    }
  }

  /**
   * Get current rankings
   */
  async getCurrentRankings(siteUrl) {
    const spinner = ora('Fetching current rankings...').start();

    try {
      const response = await searchconsole.searchanalytics.query({
        siteUrl,
        requestBody: {
          startDate: this.getDateDaysAgo(1),
          endDate: this.getTodayDate(),
          dimensions: ['query'],
          rowLimit: 10000,
          dataState: 'all'
        },
        auth: this.auth
      });

      spinner.succeed('Rankings fetched');
      return this.processRankings(response.data.rows || []);
    } catch (error) {
      spinner.fail('Failed to fetch rankings');
      console.error(chalk.red('Error:'), error.message);
      throw error;
    }
  }

  /**
   * Process ranking data
   */
  processRankings(rows) {
    return rows.map(row => ({
      keyword: row.keys?.[0] || '',
      position: parseFloat((row.position || 0).toFixed(1)),
      impressions: row.impressions || 0,
      clicks: row.clicks || 0,
      timestamp: new Date().toISOString().split('T')[0]
    }));
  }

  /**
   * Compare current with previous rankings
   */
  async compareRankings(siteUrl) {
    const current = await this.getCurrentRankings(siteUrl);
    const previous = this.loadHistory();

    const today = new Date().toISOString().split('T')[0];
    const yesterday = this.getDateDaysAgo(1);

    const previousToday = previous[today] || {};
    const comparison = [];

    current.forEach(curr => {
      const prev = previousToday[curr.keyword];
      const change = prev ? (prev.position - curr.position).toFixed(1) : null;

      comparison.push({
        keyword: curr.keyword,
        currentPos: curr.position,
        previousPos: prev?.position || 'N/A',
        change: change,
        changeType: this.getChangeType(change),
        impressions: curr.impressions,
        clicks: curr.clicks
      });
    });

    // Save current rankings to history
    if (!previous[today]) {
      previous[today] = {};
    }
    current.forEach(c => {
      previous[today][c.keyword] = { position: c.position };
    });
    this.saveHistory(previous);

    return comparison;
  }

  /**
   * Determine change type (up/down/stable)
   */
  getChangeType(change) {
    if (change === null || change === 'N/A') return 'NEW';
    if (change > 0) return 'UP';
    if (change < 0) return 'DOWN';
    return 'STABLE';
  }

  /**
   * Load ranking history
   */
  loadHistory() {
    if (fs.existsSync(this.dataPath)) {
      const data = fs.readFileSync(this.dataPath, 'utf8');
      return JSON.parse(data);
    }
    return {};
  }

  /**
   * Save ranking history
   */
  saveHistory(data) {
    const exportDir = './exports';
    if (!fs.existsSync(exportDir)) {
      fs.mkdirSync(exportDir, { recursive: true });
    }
    fs.writeFileSync(this.dataPath, JSON.stringify(data, null, 2));
  }

  /**
   * Get date X days ago
   */
  getDateDaysAgo(days) {
    const date = new Date();
    date.setDate(date.getDate() - days);
    return date.toISOString().split('T')[0];
  }

  /**
   * Get today's date
   */
  getTodayDate() {
    return new Date().toISOString().split('T')[0];
  }

  /**
   * Print ranking changes
   */
  printChanges(comparison) {
    console.log(chalk.bold.cyan('\n📊 RANKING CHANGES\n'));
    console.log(chalk.gray('─'.repeat(100)));

    // Filter by change type
    const gainers = comparison.filter(c => c.changeType === 'UP').sort((a, b) => b.change - a.change);
    const losers = comparison.filter(c => c.changeType === 'DOWN').sort((a, b) => a.change - b.change);
    const new_keywords = comparison.filter(c => c.changeType === 'NEW');

    if (gainers.length > 0) {
      console.log(chalk.green.bold('🔝 GAINERS (Positions improved)'));
      gainers.slice(0, 10).forEach(item => {
        console.log(
          `${chalk.green('↑')} ${chalk.yellow(item.keyword)} | ` +
          `${chalk.red(item.previousPos)} → ${chalk.green(item.currentPos)} | ` +
          `Change: +${item.change} positions`
        );
      });
    }

    if (losers.length > 0) {
      console.log(chalk.red.bold('\n🔻 LOSERS (Positions dropped)'));
      losers.slice(0, 10).forEach(item => {
        console.log(
          `${chalk.red('↓')} ${chalk.yellow(item.keyword)} | ` +
          `${chalk.green(item.previousPos)} → ${chalk.red(item.currentPos)} | ` +
          `Change: ${item.change} positions`
        );
      });
    }

    if (new_keywords.length > 0) {
      console.log(chalk.cyan.bold(`\n✨ NEW RANKINGS (${new_keywords.length} keywords)`));
      new_keywords.slice(0, 10).forEach(item => {
        console.log(
          `${chalk.cyan('★')} ${chalk.yellow(item.keyword)} | ` +
          `Position: ${chalk.blue(item.currentPos)}`
        );
      });
    }

    console.log(chalk.gray('─'.repeat(100)));
  }

  /**
   * Check for significant drops
   */
  checkAlerts(comparison) {
    const threshold = parseFloat(config.get('RANKING_DROP_THRESHOLD', '5'));
    const alerts = comparison.filter(c => {
      if (c.changeType === 'DOWN') {
        return Math.abs(parseFloat(c.change)) >= threshold;
      }
      return false;
    });

    if (alerts.length > 0) {
      console.log(chalk.bold.red(`\n⚠️  ALERTS: ${alerts.length} keywords dropped more than ${threshold} positions\n`));
      alerts.forEach(alert => {
        console.log(
          `${chalk.red('●')} ${chalk.yellow(alert.keyword)} dropped from ` +
          `${alert.previousPos} to ${alert.currentPos}`
        );
      });
    }
  }
}

/**
 * Main execution
 */
async function main() {
  console.log(chalk.bold.blue('\n🎯 Rank Position Tracker\n'));

  const tracker = new RankTracker();
  const siteUrl = config.get('GOOGLE_PROPERTY_URL', 'https://example.com');

  try {
    const comparison = await tracker.compareRankings(siteUrl);
    tracker.printChanges(comparison);
    tracker.checkAlerts(comparison);

    console.log(chalk.green('\n✓ Rank tracking complete!\n'));
  } catch (error) {
    console.error(chalk.red('\n✗ Error:'), error.message);
    process.exit(1);
  }
}

main();
