#!/usr/bin/env node

/**
 * Meta Tags Optimizer
 * Analyzes and optimizes meta tags (titles, descriptions, keywords)
 * Usage: npm run meta
 */

import chalk from 'chalk';
import ora from 'ora';

class MetaOptimizer {
  constructor() {
    this.pages = [];
    this.issues = [];
  }

  /**
   * Generate mock page data
   */
  generateMockPages() {
    return [
      {
        url: 'https://example.com/',
        title: 'Best Desert Safari Tours in Dubai | Professional Guides 2026',
        description: 'Book authentic desert safaris in Dubai with experienced guides. Evening & morning tours available. Competitive prices, 4.8★ reviews. Premium dune bashing experience.',
        keywords: 'desert safari dubai, dune bashing, camel ride, bedouin dinner'
      },
      {
        url: 'https://example.com/tours/city-tour',
        title: 'Dubai City Tour - Burj Khalifa & Mall of the Emirates',
        description: 'Explore iconic Dubai landmarks with our professional city tour guide.',
        keywords: null
      },
      {
        url: 'https://example.com/tours/yacht',
        title: 'Very Long Title That Exceeds The Maximum Recommended Character Limit For Google Search Results And Will Get Truncated In The SERP Making It Less Effective',
        description: 'Short',
        keywords: 'yacht, dubai'
      },
      {
        url: 'https://example.com/about',
        title: 'About Us',
        description: null,
        keywords: null
      },
      {
        url: 'https://example.com/blog/dubai-tips',
        title: 'Dubai Travel Tips & Best Time to Visit - Complete Guide 2026',
        description: 'Discover insider tips for visiting Dubai. Learn about visa requirements, best time to visit, weather, local customs, and travel budget for your UAE vacation.',
        keywords: 'dubai travel tips, best time visit dubai, dubai guide'
      }
    ];
  }

  /**
   * Analyze all pages
   */
  async analyzePages() {
    const spinner = ora('Analyzing meta tags...').start();

    try {
      this.pages = this.generateMockPages();

      this.pages.forEach(page => {
        this.analyzePage(page);
      });

      spinner.succeed(`Analyzed ${this.pages.length} pages`);
      return true;
    } catch (error) {
      spinner.fail('Analysis failed');
      console.error(chalk.red('Error:'), error.message);
      return false;
    }
  }

  /**
   * Analyze individual page
   */
  analyzePage(page) {
    const analysis = {
      url: page.url,
      title: this.analyzeTitle(page.title),
      description: this.analyzeDescription(page.description),
      keywords: this.analyzeKeywords(page.keywords),
      score: 0
    };

    // Calculate overall score
    analysis.score = Math.round(
      (analysis.title.score + analysis.description.score + analysis.keywords.score) / 3
    );

    this.pages[this.pages.indexOf(page)].analysis = analysis;
  }

  /**
   * Analyze title tag
   */
  analyzeTitle(title) {
    const issues = [];
    const score = { base: 100, deductions: 0 };

    if (!title) {
      issues.push('Missing title tag');
      return { score: 0, issues, suggestions: 'Add a title (50-60 chars)' };
    }

    const length = title.length;
    if (length < 30) {
      issues.push(`Too short (${length} chars, minimum 30)`);
      score.deductions += 30;
    } else if (length < 50) {
      issues.push(`Slightly short (${length} chars, recommended 50-60)`);
      score.deductions += 10;
    } else if (length > 60) {
      issues.push(`Too long (${length} chars, maximum 60)`);
      score.deductions += 20;
    }

    // Check for keyword at beginning
    if (!title.toLowerCase().includes('dubai') && !title.toLowerCase().includes('tour')) {
      issues.push('Missing primary keyword');
      score.deductions += 15;
    }

    return {
      score: Math.max(0, score.base - score.deductions),
      issues,
      length,
      suggestions: '50-60 chars, include primary keyword, include brand'
    };
  }

  /**
   * Analyze meta description
   */
  analyzeDescription(description) {
    const issues = [];
    const score = { base: 100, deductions: 0 };

    if (!description) {
      issues.push('Missing meta description');
      return { score: 0, issues, suggestions: 'Add description (150-160 chars)' };
    }

    const length = description.length;
    if (length < 120) {
      issues.push(`Too short (${length} chars, minimum 120)`);
      score.deductions += 25;
    } else if (length < 150) {
      issues.push(`Slightly short (${length} chars, recommended 150-160)`);
      score.deductions += 10;
    } else if (length > 160) {
      issues.push(`Too long (${length} chars, maximum 160)`);
      score.deductions += 20;
    }

    // Check for CTA
    if (!description.match(/book|get|learn|discover|explore|find/i)) {
      issues.push('No clear call-to-action');
      score.deductions += 10;
    }

    // Check for unique value proposition
    if (description.length > 0 && !description.match(/best|professional|affordable|premium|expert/i)) {
      issues.push('Missing unique value proposition');
      score.deductions += 5;
    }

    return {
      score: Math.max(0, score.base - score.deductions),
      issues,
      length,
      suggestions: '150-160 chars, include benefit, include CTA, compelling copy'
    };
  }

  /**
   * Analyze keywords
   */
  analyzeKeywords(keywords) {
    const issues = [];
    const score = { base: 100, deductions: 0 };

    if (!keywords) {
      issues.push('Missing meta keywords tag');
      score.deductions += 30; // Less critical than title/desc
    } else {
      const keywordList = keywords.split(',').map(k => k.trim());
      if (keywordList.length < 3) {
        issues.push(`Too few keywords (${keywordList.length}, recommended 3-5)`);
        score.deductions += 15;
      } else if (keywordList.length > 5) {
        issues.push(`Too many keywords (${keywordList.length}, maximum 5)`);
        score.deductions += 10;
      }
    }

    return {
      score: Math.max(0, score.base - score.deductions),
      issues,
      suggestions: '3-5 relevant keywords, separated by commas'
    };
  }

  /**
   * Get improvement suggestions
   */
  getImprovementSuggestions(page) {
    const suggestions = [];

    if (page.analysis.title.score < 70) {
      suggestions.push(`Rewrite title: ${page.analysis.title.suggestions}`);
    }

    if (page.analysis.description.score < 70) {
      suggestions.push(`Improve description: ${page.analysis.description.suggestions}`);
    }

    if (page.analysis.keywords.score < 70) {
      suggestions.push(`Add keywords: ${page.analysis.keywords.suggestions}`);
    }

    if (page.analysis.score < 70) {
      suggestions.push('Priority: Fix meta tags for better SERP visibility');
    }

    return suggestions;
  }

  /**
   * Print detailed report
   */
  printReport() {
    console.log(chalk.bold.cyan('\n📝 META TAGS OPTIMIZATION REPORT\n'));
    console.log(chalk.gray('─'.repeat(120)));

    const avgScore = Math.round(
      this.pages.reduce((sum, p) => sum + p.analysis.score, 0) / this.pages.length
    );

    console.log(
      `Average Score: ${this.getScoreColor(avgScore)}${avgScore}/100 | ` +
      `Pages Analyzed: ${chalk.blue(this.pages.length)}\n`
    );

    this.pages.forEach((page, i) => {
      const scoreColor = this.getScoreColor(page.analysis.score);
      const statusIcon = page.analysis.score >= 80 ? chalk.green('✓') : chalk.red('⚠');

      console.log(`${i + 1}. ${statusIcon} ${chalk.yellow(page.url)}`);
      console.log(
        `   Overall: ${scoreColor}${page.analysis.score}/100 | ` +
        `Title: ${scoreColor}${page.analysis.title.score)} | ` +
        `Desc: ${scoreColor}${page.analysis.description.score)} | ` +
        `Keywords: ${scoreColor}${page.analysis.keywords.score)}`
      );

      if (page.analysis.title.length) {
        console.log(`   Title: "${page.analysis.title.length} chars"`);
      }

      if (page.analysis.description.length) {
        console.log(`   Description: "${page.analysis.description.length} chars"`);
      }

      // Show issues if any
      const allIssues = [
        ...page.analysis.title.issues,
        ...page.analysis.description.issues,
        ...page.analysis.keywords.issues
      ];

      if (allIssues.length > 0) {
        console.log(chalk.red(`   Issues: ${allIssues.join(', ')}`));
      }

      const suggestions = this.getImprovementSuggestions(page);
      if (suggestions.length > 0) {
        console.log(chalk.yellow(`   Suggestions: ${suggestions[0]}`));
      }

      console.log();
    });

    console.log(chalk.gray('─'.repeat(120)));
    console.log(chalk.green('\n✓ Meta optimization analysis complete!\n'));
  }

  /**
   * Get score color
   */
  getScoreColor(score) {
    if (score >= 80) return chalk.green;
    if (score >= 60) return chalk.yellow;
    return chalk.red;
  }
}

/**
 * Main execution
 */
async function main() {
  console.log(chalk.bold.blue('\n📝 Meta Tags Optimizer\n'));

  const optimizer = new MetaOptimizer();

  try {
    await optimizer.analyzePages();
    optimizer.printReport();
  } catch (error) {
    console.error(chalk.red('\n✗ Error:'), error.message);
    process.exit(1);
  }
}

main();
