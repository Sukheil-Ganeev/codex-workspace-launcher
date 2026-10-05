#!/usr/bin/env node

/**
 * Content Optimizer
 * Analyzes content quality, readability, keyword density
 * Usage: npm run content
 */

import chalk from 'chalk';
import ora from 'ora';

class ContentOptimizer {
  constructor() {
    this.articles = [];
  }

  /**
   * Generate mock articles
   */
  generateMockArticles() {
    return [
      {
        title: 'Dubai Desert Safari: Complete Guide for First-Timers',
        content: `Dubai Desert Safari: A Complete Guide for First-Timers

Are you planning your first desert safari in Dubai? This comprehensive guide will help you prepare for an unforgettable experience in the Arabian desert.

What is a Desert Safari?
A desert safari is an adventure tour that takes you deep into the Arabian desert surrounding Dubai. You'll experience dune bashing, camel rides, traditional Bedouin hospitality, and authentic Middle Eastern cuisine.

Why Choose a Desert Safari?
Desert safaris are one of the most popular tourist activities in Dubai. Here's why you should include it in your itinerary:
- Unique cultural experience
- Breathtaking desert landscape
- Professional guides
- Family-friendly activities
- Great value for money

Types of Desert Safaris
There are several types of desert safari experiences:

1. Evening Safari (Most Popular)
The evening safari is perfect for capturing sunset photos while enjoying dune bashing. Includes traditional dinner and entertainment.

2. Morning Safari
A cooler option for those who prefer early morning activities. Includes breakfast and wildlife spotting.

3. Overnight Desert Camp
For the ultimate experience, stay overnight in a traditional Bedouin camp.

What to Expect
Your desert safari experience typically includes:
- Hotel pickup and transfer
- 4x4 vehicle dune bashing
- Camel riding experience
- Henna tattooing
- Traditional Arabian dinner
- Live entertainment (belly dancing, fire shows)
- Hotel return

Preparation Tips
Before your desert safari:
- Wear comfortable clothing and sunscreen
- Bring a camera for stunning photos
- Inform guides about dietary restrictions
- Book in advance, especially during peak season

Book Your Desert Safari Today
Don't miss this incredible Dubai experience. Contact our professional tour operators to reserve your spot.`,
        keyword: 'desert safari dubai'
      }
    ];
  }

  /**
   * Analyze all articles
   */
  async analyzeArticles() {
    const spinner = ora('Analyzing content...').start();

    try {
      this.articles = this.generateMockArticles();

      this.articles = this.articles.map(article => ({
        ...article,
        analysis: this.analyzeContent(article)
      }));

      spinner.succeed(`Analyzed ${this.articles.length} articles`);
      return true;
    } catch (error) {
      spinner.fail('Analysis failed');
      return false;
    }
  }

  /**
   * Analyze content quality
   */
  analyzeContent(article) {
    const wordCount = article.content.split(/\s+/).length;
    const keywordCount = (article.content.match(new RegExp(article.keyword, 'gi')) || []).length;
    const headingCount = (article.content.match(/^#{1,6}\s/gm) || []).length;
    const paragraphCount = (article.content.match(/\n\n/g) || []).length;
    const sentenceCount = (article.content.match(/[.!?]+/g) || []).length;
    const avgSentenceLength = wordCount / sentenceCount;

    return {
      wordCount,
      keywordCount,
      keywordDensity: ((keywordCount / wordCount) * 100).toFixed(2),
      headingCount,
      paragraphCount,
      readability: this.calculateReadability(wordCount, sentenceCount),
      scores: {
        length: this.getScoreLength(wordCount),
        keyword: this.getScoreKeyword(keywordCount, wordCount),
        structure: this.getScoreStructure(headingCount),
        readability: this.getScoreReadability(avgSentenceLength)
      }
    };
  }

  /**
   * Calculate readability score (Flesch Reading Ease approximation)
   */
  calculateReadability(words, sentences) {
    // Simple approximation: fewer words per sentence = easier reading
    const avgWordsPerSent = words / sentences;
    if (avgWordsPerSent < 12) return 'Excellent';
    if (avgWordsPerSent < 17) return 'Good';
    if (avgWordsPerSent < 20) return 'Fair';
    return 'Difficult';
  }

  /**
   * Get score for content length
   */
  getScoreLength(wordCount) {
    if (wordCount < 300) return { score: 30, feedback: 'Too short (min 300 words)' };
    if (wordCount < 600) return { score: 60, feedback: 'Somewhat short (recommended 800+)' };
    if (wordCount < 1500) return { score: 80, feedback: 'Good length' };
    if (wordCount > 3000) return { score: 70, feedback: 'Very long (may be hard to scan)' };
    return { score: 100, feedback: 'Ideal length (1500-3000 words)' };
  }

  /**
   * Get score for keyword density
   */
  getScoreKeyword(keywordCount, wordCount) {
    const density = (keywordCount / wordCount) * 100;
    if (density < 0.5) return { score: 50, feedback: 'Keyword not mentioned enough' };
    if (density < 1) return { score: 80, feedback: 'Good keyword density' };
    if (density < 2) return { score: 90, feedback: 'Excellent keyword density' };
    if (density < 3) return { score: 80, feedback: 'Slightly high keyword density' };
    return { score: 50, feedback: 'Keyword stuffing detected' };
  }

  /**
   * Get score for structure
   */
  getScoreStructure(headingCount) {
    if (headingCount < 2) return { score: 40, feedback: 'Add more subheadings' };
    if (headingCount < 4) return { score: 70, feedback: 'Good heading structure' };
    if (headingCount < 8) return { score: 95, feedback: 'Excellent structure' };
    return { score: 80, feedback: 'Too many headings' };
  }

  /**
   * Get score for readability
   */
  getScoreReadability(avgSentenceLength) {
    if (avgSentenceLength < 12) return { score: 100, feedback: 'Very easy to read' };
    if (avgSentenceLength < 17) return { score: 85, feedback: 'Easy to read' };
    if (avgSentenceLength < 20) return { score: 70, feedback: 'Moderate readability' };
    return { score: 50, feedback: 'Complex sentences - simplify' };
  }

  /**
   * Get overall score
   */
  getOverallScore(analysis) {
    const scores = Object.values(analysis.scores).map(s => s.score);
    return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  }

  /**
   * Print detailed report
   */
  printReport() {
    console.log(chalk.bold.cyan('\n📄 CONTENT OPTIMIZATION REPORT\n'));
    console.log(chalk.gray('─'.repeat(120)));

    this.articles.forEach((article, i) => {
      const analysis = article.analysis;
      const overallScore = this.getOverallScore(analysis);
      const scoreColor = overallScore >= 80 ? chalk.green :
                         overallScore >= 60 ? chalk.yellow : chalk.red;

      console.log(`\n${i + 1}. ${chalk.yellow(article.title)}`);
      console.log(`   Keyword: "${chalk.cyan(article.keyword)}"`);
      console.log(`   Overall Score: ${scoreColor}${overallScore}/100\n`);

      // Content metrics
      console.log(chalk.bold.blue('   Content Metrics:'));
      console.log(`     Word Count: ${chalk.blue(analysis.wordCount)} words - ${analysis.scores.length.feedback}`);
      console.log(`     Keyword Mentions: ${chalk.blue(analysis.keywordCount)} (${analysis.keywordDensity}%) - ${analysis.scores.keyword.feedback}`);
      console.log(`     Headings: ${chalk.blue(analysis.headingCount)} subheadings - ${analysis.scores.structure.feedback}`);
      console.log(`     Readability: ${chalk.magenta(analysis.readability)} - ${analysis.scores.readability.feedback}\n`);

      // Component scores
      console.log(chalk.bold.blue('   Component Scores:'));
      Object.entries(analysis.scores).forEach(([key, value]) => {
        const color = value.score >= 80 ? chalk.green : value.score >= 60 ? chalk.yellow : chalk.red;
        console.log(`     ${key.charAt(0).toUpperCase() + key.slice(1)}: ${color}${value.score}/100`);
      });

      // Recommendations
      const recommendations = [];
      if (analysis.scores.length.score < 80) recommendations.push('• Expand content to 1500+ words');
      if (analysis.scores.keyword.score < 80) recommendations.push('• Increase keyword mentions naturally');
      if (analysis.scores.structure.score < 80) recommendations.push('• Add more descriptive subheadings');
      if (analysis.scores.readability.score < 80) recommendations.push('• Use shorter sentences and paragraphs');

      if (recommendations.length > 0) {
        console.log(chalk.bold.yellow('\n   Recommendations:'));
        recommendations.forEach(rec => console.log(`     ${rec}`));
      }
    });

    console.log(chalk.gray('\n' + '─'.repeat(120)));
    console.log(chalk.green('\n✓ Content analysis complete!\n'));
  }
}

/**
 * Main execution
 */
async function main() {
  console.log(chalk.bold.blue('\n📄 Content Optimizer\n'));

  const optimizer = new ContentOptimizer();

  try {
    await optimizer.analyzeArticles();
    optimizer.printReport();
  } catch (error) {
    console.error(chalk.red('\n✗ Error:'), error.message);
    process.exit(1);
  }
}

main();
