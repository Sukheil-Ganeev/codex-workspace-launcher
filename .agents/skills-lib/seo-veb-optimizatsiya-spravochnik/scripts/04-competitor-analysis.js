#!/usr/bin/env node

/**
 * Competitor Analysis
 * Analyzes competitor keywords, rankings, and content gaps
 * Usage: npm run competitor
 */

import axios from 'axios';
import chalk from 'chalk';
import ora from 'ora';
import config from './config/api-keys.config.js';

class CompetitorAnalyzer {
  constructor() {
    this.competitors = [
      'viator.com',
      'getyourguide.com',
      'klook.com'
    ];
  }

  /**
   * Get competitor keywords (mock implementation)
   */
  async getCompetitorKeywords(domain) {
    const spinner = ora(`Analyzing ${domain}...`).start();

    try {
      // This would integrate with actual SEO APIs
      // For now, returning mock data
      const data = this.generateMockCompetitorData(domain);
      spinner.succeed(`Analyzed ${domain}`);
      return data;
    } catch (error) {
      spinner.fail(`Failed to analyze ${domain}`);
      return [];
    }
  }

  /**
   * Generate mock competitor data
   */
  generateMockCompetitorData(domain) {
    const keywords = [
      { keyword: 'dubai desert safari', volume: 12000, difficulty: 65, competition: 'high' },
      { keyword: 'abu dhabi tours', volume: 8100, difficulty: 58, competition: 'high' },
      { keyword: 'dubai yacht tour', volume: 5400, difficulty: 72, competition: 'high' },
      { keyword: 'best desert safari dubai', volume: 2100, difficulty: 42, competition: 'medium' },
      { keyword: 'evening safari dunes', volume: 890, difficulty: 35, competition: 'medium' },
      { keyword: 'camel ride dubai', volume: 1200, difficulty: 45, competition: 'medium' },
      { keyword: 'dubai city tour', volume: 9200, difficulty: 60, competition: 'high' },
      { keyword: 'burj khalifa visit', volume: 18000, difficulty: 75, competition: 'very high' }
    ];

    return {
      domain,
      topKeywords: keywords,
      estimatedTraffic: 145000,
      domainAuthority: 68,
      backlinks: 15234,
      topPages: [
        { url: '/tours/desert-safari', traffic: 45000, keyword: 'desert safari' },
        { url: '/tours/city-tour', traffic: 32000, keyword: 'city tour' },
        { url: '/tours/yacht-cruise', traffic: 28000, keyword: 'yacht tour' }
      ]
    };
  }

  /**
   * Find keyword gaps
   */
  findKeywordGaps(ourKeywords, competitorKeywords) {
    const ourKeywordSet = new Set(ourKeywords.map(k => k.keyword.toLowerCase()));
    const gaps = competitorKeywords.filter(k => !ourKeywordSet.has(k.keyword.toLowerCase()));

    return gaps
      .filter(k => k.volume > 500) // Only significant keywords
      .sort((a, b) => b.volume - a.volume)
      .slice(0, 20);
  }

  /**
   * Analyze content opportunities
   */
  analyzeContentOpportunities(gaps) {
    return gaps.map(keyword => ({
      keyword: keyword.keyword,
      volume: keyword.volume,
      difficulty: keyword.difficulty,
      opportunity: this.calculateOpportunity(keyword),
      priority: this.getPriority(keyword)
    }));
  }

  /**
   * Calculate opportunity score
   */
  calculateOpportunity(keyword) {
    const score = (keyword.volume * (100 - keyword.difficulty)) / 100;
    return Math.round(score);
  }

  /**
   * Get priority level
   */
  getPriority(keyword) {
    if (keyword.difficulty < 30 && keyword.volume > 1000) return 'CRITICAL';
    if (keyword.difficulty < 40 && keyword.volume > 500) return 'HIGH';
    if (keyword.difficulty < 50) return 'MEDIUM';
    return 'LOW';
  }

  /**
   * Print competitor analysis
   */
  printAnalysis(competitors) {
    console.log(chalk.bold.cyan('\n🏆 COMPETITOR ANALYSIS\n'));
    console.log(chalk.gray('─'.repeat(100)));

    competitors.forEach(competitor => {
      console.log(chalk.bold.yellow(`\n${competitor.domain}`));
      console.log(
        `DA: ${chalk.blue(competitor.domainAuthority)} | ` +
        `Traffic: ${chalk.green(competitor.estimatedTraffic.toLocaleString())} | ` +
        `Backlinks: ${chalk.magenta(competitor.backlinks.toLocaleString())}`
      );

      console.log(chalk.cyan('\nTop Keywords:'));
      competitor.topKeywords.slice(0, 8).forEach((kw, i) => {
        const diffColor = kw.difficulty > 60 ? chalk.red : kw.difficulty > 40 ? chalk.yellow : chalk.green;
        console.log(
          `  ${i + 1}. ${chalk.white(kw.keyword)} | ` +
          `Volume: ${chalk.blue(kw.volume)} | ` +
          `Difficulty: ${diffColor(kw.difficulty)}`
        );
      });

      console.log(chalk.cyan('\nTop Pages:'));
      competitor.topPages.forEach(page => {
        console.log(
          `  ${chalk.yellow(page.url.padEnd(30))} | ` +
          `Traffic: ${chalk.green(page.traffic.toLocaleString())}`
        );
      });
    });
  }

  /**
   * Print keyword gaps
   */
  printKeywordGaps(gaps) {
    console.log(chalk.bold.cyan('\n📊 KEYWORD OPPORTUNITIES (Not ranking for)\n'));
    console.log(chalk.gray('─'.repeat(100)));

    const priorities = { CRITICAL: gaps.filter(g => g.priority === 'CRITICAL').length,
                         HIGH: gaps.filter(g => g.priority === 'HIGH').length,
                         MEDIUM: gaps.filter(g => g.priority === 'MEDIUM').length };

    console.log(
      `${chalk.red(`● ${priorities.CRITICAL} CRITICAL`)} | ` +
      `${chalk.yellow(`● ${priorities.HIGH} HIGH`)} | ` +
      `${chalk.blue(`● ${priorities.MEDIUM} MEDIUM`)}\n`
    );

    gaps.slice(0, 20).forEach((gap, i) => {
      const priorityColor = gap.priority === 'CRITICAL' ? chalk.red :
                           gap.priority === 'HIGH' ? chalk.yellow : chalk.blue;
      console.log(
        `${i + 1}. ${priorityColor(gap.priority.padEnd(8))} | ` +
        `${chalk.white(gap.keyword.padEnd(35))} | ` +
        `Volume: ${chalk.blue(gap.volume.toString().padEnd(6))} | ` +
        `Difficulty: ${chalk.magenta(gap.difficulty.toString().padEnd(3))} | ` +
        `Opportunity: ${chalk.green(gap.opportunity)}`
      );
    });
  }
}

/**
 * Main execution
 */
async function main() {
  console.log(chalk.bold.blue('\n🎯 Competitor Analysis\n'));

  const analyzer = new CompetitorAnalyzer();

  try {
    console.log('Analyzing competitor keywords...\n');

    const competitors = await Promise.all(
      analyzer.competitors.map(domain => analyzer.getCompetitorKeywords(domain))
    );

    analyzer.printAnalysis(competitors);

    // Find keyword gaps (mock our keywords)
    const ourKeywords = [
      { keyword: 'dubai desert safari' },
      { keyword: 'abu dhabi tours' }
    ];

    const allCompetitorKeywords = competitors.flatMap(c => c.topKeywords);
    const gaps = analyzer.findKeywordGaps(ourKeywords, allCompetitorKeywords);
    const opportunities = analyzer.analyzeContentOpportunities(gaps);

    analyzer.printKeywordGaps(opportunities);

    console.log(chalk.green('\n✓ Competitor analysis complete!\n'));
  } catch (error) {
    console.error(chalk.red('\n✗ Error:'), error.message);
    process.exit(1);
  }
}

main();
