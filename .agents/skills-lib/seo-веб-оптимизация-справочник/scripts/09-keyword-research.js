#!/usr/bin/env node

/**
 * Keyword Research Tool
 * Analyzes keywords with volume, difficulty, intent classification
 * Usage: npm run keywords
 */

import chalk from 'chalk';
import ora from 'ora';

class KeywordResearch {
  constructor() {
    this.keywords = [];
  }

  /**
   * Generate mock keyword data
   */
  generateMockKeywords() {
    return [
      { keyword: 'dubai desert safari', volume: 12000, difficulty: 65, intent: 'transactional' },
      { keyword: 'best desert safari in dubai', volume: 2100, difficulty: 42, intent: 'commercial' },
      { keyword: 'evening desert safari dubai', volume: 890, difficulty: 38, intent: 'commercial' },
      { keyword: 'morning desert safari dubai', volume: 720, difficulty: 35, intent: 'commercial' },
      { keyword: 'desert safari with dinner dubai', volume: 540, difficulty: 32, intent: 'transactional' },
      { keyword: 'camel ride dubai desert', volume: 1200, difficulty: 45, intent: 'commercial' },
      { keyword: 'dune bashing dubai', volume: 2800, difficulty: 48, intent: 'transactional' },
      { keyword: 'abu dhabi tours from dubai', volume: 3400, difficulty: 52, intent: 'transactional' },
      { keyword: 'dubai city tour', volume: 9200, difficulty: 60, intent: 'transactional' },
      { keyword: 'dubai yacht tour', volume: 5400, difficulty: 72, intent: 'transactional' },
      { keyword: 'what to do in dubai', volume: 18000, difficulty: 75, intent: 'informational' },
      { keyword: 'best time to visit dubai', volume: 14500, difficulty: 68, intent: 'informational' },
      { keyword: 'dubai travel tips', volume: 8900, difficulty: 62, intent: 'informational' },
      { keyword: 'dubai visa requirements', volume: 12300, difficulty: 70, intent: 'informational' }
    ];
  }

  /**
   * Analyze keywords
   */
  async analyzeKeywords() {
    const spinner = ora('Analyzing keywords...').start();

    try {
      this.keywords = this.generateMockKeywords();

      this.keywords = this.keywords.map(kw => ({
        ...kw,
        opportunity: this.calculateOpportunity(kw),
        priority: this.getPriority(kw),
        recommendation: this.getRecommendation(kw)
      }));

      spinner.succeed(`Analyzed ${this.keywords.length} keywords`);
      return true;
    } catch (error) {
      spinner.fail('Analysis failed');
      return false;
    }
  }

  /**
   * Calculate opportunity score
   */
  calculateOpportunity(kw) {
    // High volume + low difficulty = good opportunity
    return Math.round((kw.volume * (100 - kw.difficulty)) / 100);
  }

  /**
   * Get priority level
   */
  getPriority(kw) {
    if (kw.difficulty < 30 && kw.volume > 1000) return 'CRITICAL';
    if (kw.difficulty < 40 && kw.volume > 500) return 'HIGH';
    if (kw.difficulty < 50) return 'MEDIUM';
    if (kw.difficulty >= 70) return 'LOW';
    return 'MEDIUM';
  }

  /**
   * Get recommendation
   */
  getRecommendation(kw) {
    if (kw.priority === 'CRITICAL') {
      return 'Priority target - high volume with achievable difficulty';
    } else if (kw.priority === 'HIGH') {
      return 'Good opportunity - good balance of volume and difficulty';
    } else if (kw.difficulty > 70) {
      return 'Hard to rank - focus on long-tail variations';
    } else if (kw.volume < 500) {
      return 'Low volume - supplement with similar keywords';
    }
    return 'Moderate difficulty - included in comprehensive strategy';
  }

  /**
   * Get keywords by intent
   */
  getByIntent(intent) {
    return this.keywords.filter(k => k.intent === intent);
  }

  /**
   * Get keywords by priority
   */
  getByPriority(priority) {
    return this.keywords.filter(k => k.priority === priority);
  }

  /**
   * Print full report
   */
  printReport() {
    console.log(chalk.bold.cyan('\n🔍 KEYWORD RESEARCH REPORT\n'));
    console.log(chalk.gray('─'.repeat(140)));

    // Summary statistics
    console.log(chalk.bold.yellow('Summary Statistics:'));
    const critical = this.getByPriority('CRITICAL');
    const high = this.getByPriority('HIGH');
    const medium = this.getByPriority('MEDIUM');

    console.log(
      `  Critical: ${chalk.red(critical.length)} | ` +
      `High: ${chalk.yellow(high.length)} | ` +
      `Medium: ${chalk.blue(medium.length)}\n`
    );

    // By Intent
    console.log(chalk.bold.yellow('By Search Intent:'));
    const intents = [...new Set(this.keywords.map(k => k.intent))];
    intents.forEach(intent => {
      const kws = this.getByIntent(intent);
      console.log(`  ${chalk.cyan(intent.toUpperCase())}: ${kws.length} keywords`);
    });

    // Top opportunities
    console.log(chalk.bold.cyan('\n🎯 TOP OPPORTUNITIES (By Opportunity Score)\n'));
    const topOps = [...this.keywords].sort((a, b) => b.opportunity - a.opportunity).slice(0, 10);

    topOps.forEach((kw, i) => {
      const priorityColor = kw.priority === 'CRITICAL' ? chalk.red :
                           kw.priority === 'HIGH' ? chalk.yellow :
                           kw.priority === 'MEDIUM' ? chalk.blue : chalk.gray;

      console.log(
        `${i + 1}. ${priorityColor(kw.priority.padEnd(8))} | ` +
        `${chalk.white(kw.keyword.padEnd(35))} | ` +
        `Volume: ${chalk.blue(kw.volume.toString().padEnd(6))} | ` +
        `Diff: ${chalk.magenta(kw.difficulty.toString().padEnd(3))} | ` +
        `Score: ${chalk.green(kw.opportunity)}`
      );
    });

    // By Intent Breakdown
    console.log(chalk.bold.cyan('\n📊 BY SEARCH INTENT\n'));

    const intentTypes = {
      informational: { name: 'Informational', icon: 'ℹ️ ' },
      commercial: { name: 'Commercial', icon: '🛍️  ' },
      transactional: { name: 'Transactional', icon: '💰' },
      navigational: { name: 'Navigational', icon: '🗺️ ' }
    };

    Object.entries(intentTypes).forEach(([intent, info]) => {
      const kws = this.getByIntent(intent);
      if (kws.length > 0) {
        console.log(chalk.bold.yellow(`${info.icon} ${info.name} Intent (${kws.length} keywords)`));
        kws.slice(0, 5).forEach(kw => {
          console.log(
            `  • ${chalk.white(kw.keyword.padEnd(40))} | ` +
            `Volume: ${chalk.blue(kw.volume)} | Diff: ${chalk.magenta(kw.difficulty)}`
          );
        });
        if (kws.length > 5) {
          console.log(`  ... and ${chalk.gray(kws.length - 5)} more\n`);
        } else {
          console.log();
        }
      }
    });

    // Critical targets
    const criticalKws = this.getByPriority('CRITICAL');
    if (criticalKws.length > 0) {
      console.log(chalk.bold.red(`\n🔴 CRITICAL TARGETS (${criticalKws.length} keywords)\n`));
      console.log(chalk.gray('These keywords should be your primary focus'));
      console.log(chalk.gray('High volume + achievable difficulty = quick wins\n'));

      criticalKws.forEach((kw, i) => {
        console.log(
          `${i + 1}. ${chalk.red(kw.keyword)} | ` +
          `Monthly searches: ${chalk.blue(kw.volume.toLocaleString())} | ` +
          `Difficulty: ${chalk.yellow(kw.difficulty)}/100`
        );
        console.log(`   → ${chalk.cyan(kw.recommendation)}`);
      });
    }

    console.log(chalk.gray('\n─'.repeat(140)));
    console.log(chalk.green('\n✓ Keyword research complete!\n'));
  }
}

/**
 * Main execution
 */
async function main() {
  console.log(chalk.bold.blue('\n🔍 Keyword Research Tool\n'));

  const research = new KeywordResearch();

  try {
    await research.analyzeKeywords();
    research.printReport();
  } catch (error) {
    console.error(chalk.red('\n✗ Error:'), error.message);
    process.exit(1);
  }
}

main();
