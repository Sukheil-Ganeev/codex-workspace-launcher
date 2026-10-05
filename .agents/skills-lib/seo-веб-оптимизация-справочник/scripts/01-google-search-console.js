#!/usr/bin/env node

/**
 * Google Search Console API Integration
 * Fetches impressions, clicks, CTR, and ranking data
 * Usage: npm run gsc
 */

import { google } from 'googleapis';
import fs from 'fs';
import chalk from 'chalk';
import ora from 'ora';
import { createObjectCsvWriter } from 'csv-writer';
import config from './config/api-keys.config.js';

const searchconsole = google.searchconsole('v1');

class SearchConsoleAnalytics {
  constructor() {
    this.auth = null;
    this.validated = false;
    this.initialize();
  }

  /**
   * Initialize authentication
   */
  initialize() {
    try {
      if (!config.isValid()) {
        throw new Error(config.getErrors().join(', '));
      }

      const credentials = config.getGoogleCredentials();
      this.auth = new google.auth.GoogleAuth({
        credentials,
        scopes: ['https://www.googleapis.com/auth/webmasters.readonly']
      });
      this.validated = true;
      console.log(chalk.green('✓ Google Authentication initialized'));
    } catch (e) {
      console.error(chalk.red('✗ Authentication Error:'), e.message);
      process.exit(1);
    }
  }

  /**
   * Get performance data (impressions, clicks, CTR)
   */
  async getPerformanceData(siteUrl, params = {}) {
    const {
      startDate = this.getDateDaysAgo(30),
      endDate = this.getTodayDate(),
      dimensions = ['query', 'page'],
      rowLimit = 10000
    } = params;

    const spinner = ora('Fetching GSC data...').start();

    try {
      const response = await searchconsole.searchanalytics.query({
        siteUrl,
        requestBody: {
          startDate,
          endDate,
          dimensions,
          rowLimit,
          dataState: 'all'
        },
        auth: this.auth
      });

      spinner.succeed(`Fetched ${response.data.rows?.length || 0} records`);
      return this.processData(response.data.rows || []);
    } catch (error) {
      spinner.fail('Failed to fetch GSC data');
      console.error(chalk.red('API Error:'), error.message);
      throw error;
    }
  }

  /**
   * Get top queries
   */
  async getTopQueries(siteUrl, limit = 50) {
    const data = await this.getPerformanceData(siteUrl, {
      dimensions: ['query'],
      rowLimit: limit
    });
    return data.sort((a, b) => b.impressions - a.impressions);
  }

  /**
   * Get top pages
   */
  async getTopPages(siteUrl, limit = 50) {
    const data = await this.getPerformanceData(siteUrl, {
      dimensions: ['page'],
      rowLimit: limit
    });
    return data.sort((a, b) => b.clicks - a.clicks);
  }

  /**
   * Get data by ranking position
   */
  async getByPosition(siteUrl, limit = 100) {
    const data = await this.getPerformanceData(siteUrl, { rowLimit: limit });

    return {
      position1to3: data.filter(d => d.position <= 3).length,
      position4to10: data.filter(d => d.position > 3 && d.position <= 10).length,
      position11to20: data.filter(d => d.position > 10 && d.position <= 20).length,
      position21plus: data.filter(d => d.position > 20).length,
      avgPosition: (data.reduce((sum, d) => sum + d.position, 0) / data.length).toFixed(2),
      totalImpressions: data.reduce((sum, d) => sum + d.impressions, 0),
      totalClicks: data.reduce((sum, d) => sum + d.clicks, 0)
    };
  }

  /**
   * Process and enrich data
   */
  processData(rows) {
    if (!rows || rows.length === 0) return [];
    return rows.map(row => ({
      keyword: row.keys?.[0] || 'unknown',
      page: row.keys?.[1] || 'unknown',
      impressions: row.impressions || 0,
      clicks: row.clicks || 0,
      ctr: parseFloat(((row.ctr || 0) * 100).toFixed(2)),
      position: parseFloat((row.position || 0).toFixed(1))
    }));
  }

  /**
   * Export to CSV
   */
  async exportToCSV(data, filename) {
    const spinner = ora(`Exporting to ${filename}...`).start();
    try {
      const writer = createObjectCsvWriter({
        path: filename,
        header: [
          { id: 'keyword', title: 'Keyword' },
          { id: 'page', title: 'Page URL' },
          { id: 'impressions', title: 'Impressions' },
          { id: 'clicks', title: 'Clicks' },
          { id: 'ctr', title: 'CTR (%)' },
          { id: 'position', title: 'Avg Position' }
        ]
      });
      await writer.writeRecords(data);
      spinner.succeed(`Exported to ${chalk.cyan(filename)}`);
    } catch (error) {
      spinner.fail('Export failed');
      console.error(chalk.red('Export Error:'), error.message);
    }
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
   * Pretty print results
   */
  printResults(title, data) {
    console.log(chalk.bold.cyan(`\n${title}:`));
    console.log(chalk.gray('─'.repeat(80)));

    if (Array.isArray(data)) {
      data.slice(0, 10).forEach((item, i) => {
        console.log(
          `${i + 1}. ${chalk.yellow(item.keyword || item.page)} | ` +
          `Impressions: ${chalk.blue(item.impressions)} | ` +
          `Clicks: ${chalk.green(item.clicks)} | ` +
          `CTR: ${chalk.magenta(item.ctr + '%')} | ` +
          `Pos: ${chalk.cyan(item.position)}`
        );
      });
      if (data.length > 10) {
        console.log(chalk.gray(`... and ${data.length - 10} more`));
      }
    } else {
      Object.entries(data).forEach(([key, value]) => {
        console.log(`${chalk.yellow(key)}: ${chalk.blue(value)}`);
      });
    }
  }
}

/**
 * Main execution
 */
async function main() {
  console.log(chalk.bold.blue('\n📊 Google Search Console Analytics\n'));

  const gsc = new SearchConsoleAnalytics();
  const siteUrl = config.get('GOOGLE_PROPERTY_URL', 'https://example.com');

  try {
    // Get top queries
    const topQueries = await gsc.getTopQueries(siteUrl, 50);
    gsc.printResults('TOP QUERIES', topQueries);

    // Get top pages
    const topPages = await gsc.getTopPages(siteUrl, 50);
    gsc.printResults('TOP PAGES', topPages);

    // Get position breakdown
    const posBreakdown = await gsc.getByPosition(siteUrl, 100);
    gsc.printResults('POSITION BREAKDOWN', posBreakdown);

    // Export to CSV
    await gsc.exportToCSV(topQueries, './exports/gsc-top-queries.csv');
    await gsc.exportToCSV(topPages, './exports/gsc-top-pages.csv');

    console.log(chalk.green('\n✓ Analysis complete!\n'));
  } catch (error) {
    console.error(chalk.red('\n✗ Error:'), error.message);
    process.exit(1);
  }
}

main();
