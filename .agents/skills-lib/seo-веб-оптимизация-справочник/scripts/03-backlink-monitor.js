#!/usr/bin/env node

/**
 * Backlink Monitor
 * Monitors new and lost backlinks (requires Ahrefs or SEMrush API)
 * Usage: npm run backlinks
 */

import axios from 'axios';
import fs from 'fs';
import chalk from 'chalk';
import ora from 'ora';
import config from './config/api-keys.config.js';

class BacklinkMonitor {
  constructor() {
    this.ahrefs_key = config.get('AHREFS_API_KEY');
    this.semrush_key = config.get('SEMRUSH_API_KEY');
    this.dataPath = './exports/backlink-history.json';
  }

  /**
   * Get new backlinks
   */
  async getNewBacklinks(domain) {
    if (!this.ahrefs_key && !this.semrush_key) {
      console.log(chalk.yellow('⚠️  No API keys configured. Using mock data for demo.\n'));
      return this.getMockData('new');
    }

    const spinner = ora('Fetching new backlinks...').start();

    try {
      if (this.ahrefs_key) {
        return await this.getAhrefsBacklinks(domain, 'new');
      } else {
        return await this.getSemrushBacklinks(domain, 'new');
      }
    } catch (error) {
      spinner.fail('Failed to fetch backlinks');
      console.error(chalk.red('Error:'), error.message);
      return this.getMockData('new');
    }
  }

  /**
   * Get lost backlinks
   */
  async getLostBacklinks(domain) {
    if (!this.ahrefs_key && !this.semrush_key) {
      return this.getMockData('lost');
    }

    const spinner = ora('Fetching lost backlinks...').start();

    try {
      if (this.ahrefs_key) {
        return await this.getAhrefsBacklinks(domain, 'lost');
      } else {
        return await this.getSemrushBacklinks(domain, 'lost');
      }
    } catch (error) {
      spinner.fail('Failed to fetch backlinks');
      return this.getMockData('lost');
    }
  }

  /**
   * Get backlinks from Ahrefs (placeholder)
   */
  async getAhrefsBacklinks(domain, type) {
    // This would integrate with actual Ahrefs API
    // For demo, returning mock data
    console.log(chalk.yellow('Note: Ahrefs integration requires API implementation'));
    return this.getMockData(type);
  }

  /**
   * Get backlinks from SEMrush (placeholder)
   */
  async getSemrushBacklinks(domain, type) {
    // This would integrate with actual SEMrush API
    console.log(chalk.yellow('Note: SEMrush integration requires API implementation'));
    return this.getMockData(type);
  }

  /**
   * Get mock data for demo
   */
  getMockData(type) {
    const mockBacklinks = [
      {
        source: 'travelblog.ae',
        anchor: 'Dubai Desert Safari',
        targetUrl: 'https://example.com/desert-safari',
        DR: 28,
        backlinks: 145,
        traffic: 12500,
        dateDiscovered: new Date().toISOString().split('T')[0]
      },
      {
        source: 'dubaitourism.com',
        anchor: 'Best Tours in Dubai',
        targetUrl: 'https://example.com',
        DR: 45,
        backlinks: 892,
        traffic: 145000,
        dateDiscovered: new Date().toISOString().split('T')[0]
      },
      {
        source: 'abudhabi-guide.com',
        anchor: 'Abu Dhabi Excursions',
        targetUrl: 'https://example.com/abu-dhabi',
        DR: 32,
        backlinks: 234,
        traffic: 28500,
        dateDiscovered: new Date().toISOString().split('T')[0]
      }
    ];

    return mockBacklinks;
  }

  /**
   * Analyze backlink quality
   */
  analyzeQuality(backlinks) {
    const quality = {
      excellent: backlinks.filter(b => b.DR >= 40).length,
      good: backlinks.filter(b => b.DR >= 30 && b.DR < 40).length,
      fair: backlinks.filter(b => b.DR >= 20 && b.DR < 30).length,
      poor: backlinks.filter(b => b.DR < 20).length
    };

    const avgDR = (backlinks.reduce((sum, b) => sum + b.DR, 0) / backlinks.length).toFixed(1);
    const totalDomain = [...new Set(backlinks.map(b => b.source))].length;

    return { quality, avgDR, totalDomain };
  }

  /**
   * Load backlink history
   */
  loadHistory() {
    if (fs.existsSync(this.dataPath)) {
      return JSON.parse(fs.readFileSync(this.dataPath, 'utf8'));
    }
    return { new: [], lost: [] };
  }

  /**
   * Save backlink history
   */
  saveHistory(data) {
    const exportDir = './exports';
    if (!fs.existsSync(exportDir)) {
      fs.mkdirSync(exportDir, { recursive: true });
    }
    fs.writeFileSync(this.dataPath, JSON.stringify(data, null, 2));
  }

  /**
   * Print results
   */
  printResults(title, backlinks, analysis) {
    console.log(chalk.bold.cyan(`\n${title}`));
    console.log(chalk.gray('─'.repeat(100)));

    console.log(
      `Quality: ${chalk.green(analysis.quality.excellent)} Excellent | ` +
      `${chalk.blue(analysis.quality.good)} Good | ` +
      `${chalk.yellow(analysis.quality.fair)} Fair | ` +
      `${chalk.red(analysis.quality.poor)} Poor`
    );
    console.log(`Average DR: ${chalk.cyan(analysis.avgDR)} | Unique Domains: ${chalk.cyan(analysis.totalDomain)}\n`);

    backlinks.slice(0, 15).forEach((bl, i) => {
      const drColor = bl.DR >= 40 ? chalk.green : bl.DR >= 30 ? chalk.blue : bl.DR >= 20 ? chalk.yellow : chalk.red;
      console.log(
        `${i + 1}. ${chalk.yellow(bl.source)} (${drColor(`DR:${bl.DR}`)}) | ` +
        `${chalk.cyan(bl.anchor)} | Traffic: ${chalk.magenta(bl.traffic.toLocaleString())}`
      );
    });
  }
}

/**
 * Main execution
 */
async function main() {
  console.log(chalk.bold.blue('\n🔗 Backlink Monitor\n'));

  const monitor = new BacklinkMonitor();
  const domain = config.get('WEBSITE_DOMAIN', 'example.com');

  try {
    const newBacklinks = await monitor.getNewBacklinks(domain);
    const lostBacklinks = await monitor.getLostBacklinks(domain);

    const newAnalysis = monitor.analyzeQuality(newBacklinks);
    const lostAnalysis = monitor.analyzeQuality(lostBacklinks);

    monitor.printResults('🟢 NEW BACKLINKS', newBacklinks, newAnalysis);
    monitor.printResults('🔴 LOST BACKLINKS', lostBacklinks, lostAnalysis);

    console.log(chalk.green('\n✓ Backlink monitoring complete!\n'));
  } catch (error) {
    console.error(chalk.red('\n✗ Error:'), error.message);
    process.exit(1);
  }
}

main();
