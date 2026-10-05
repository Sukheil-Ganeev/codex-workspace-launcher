#!/usr/bin/env node

/**
 * Image Optimizer
 * Analyzes images for SEO optimization
 * Usage: npm run images
 */

import chalk from 'chalk';
import ora from 'ora';

class ImageOptimizer {
  constructor() {
    this.images = [];
  }

  /**
   * Generate mock image data
   */
  generateMockImages() {
    return [
      {
        filename: 'hero-desert-safari.jpg',
        url: 'https://example.com/images/hero-desert-safari.jpg',
        sizeKB: 250,
        dimensions: '1920x1080',
        altText: 'Desert safari',
        format: 'JPG',
        hasWebP: false
      },
      {
        filename: 'dubai-skyline.png',
        url: 'https://example.com/images/dubai-skyline.png',
        sizeKB: 456,
        dimensions: '1200x600',
        altText: null,
        format: 'PNG',
        hasWebP: false
      },
      {
        filename: 'camel-ride.webp',
        url: 'https://example.com/images/camel-ride.webp',
        sizeKB: 85,
        dimensions: '800x600',
        altText: 'Professional camel riding experience in Dubai desert',
        format: 'WebP',
        hasWebP: true
      },
      {
        filename: 'team-photo.jpg',
        url: 'https://example.com/images/team-photo.jpg',
        sizeKB: 1200,
        dimensions: '4000x3000',
        altText: '',
        format: 'JPG',
        hasWebP: false
      },
      {
        filename: 'yacht-sunset.png',
        url: 'https://example.com/images/yacht-sunset.png',
        sizeKB: 680,
        dimensions: '2560x1440',
        altText: 'Luxury yacht cruise in Dubai Marina at sunset',
        format: 'PNG',
        hasWebP: false
      }
    ];
  }

  /**
   * Analyze all images
   */
  async analyzeImages() {
    const spinner = ora('Analyzing images...').start();

    try {
      this.images = this.generateMockImages();

      this.images = this.images.map(img => ({
        ...img,
        analysis: this.analyzeImage(img)
      }));

      spinner.succeed(`Analyzed ${this.images.length} images`);
      return true;
    } catch (error) {
      spinner.fail('Analysis failed');
      return false;
    }
  }

  /**
   * Analyze individual image
   */
  analyzeImage(image) {
    const issues = [];
    const score = { base: 100, deductions: 0 };

    // Alt text check
    if (!image.altText || image.altText.trim().length === 0) {
      issues.push('Missing alt text');
      score.deductions += 30;
    } else if (image.altText.length < 10) {
      issues.push('Alt text too short (should describe image)');
      score.deductions += 15;
    } else if (image.altText.length > 125) {
      issues.push('Alt text too long (max 125 chars)');
      score.deductions += 10;
    }

    // Format check
    if (image.format === 'PNG' && image.sizeKB > 200) {
      issues.push('PNG is not optimal - consider WebP or JPG');
      score.deductions += 20;
    } else if (image.format === 'JPG' && image.sizeKB > 300) {
      issues.push('JPG size too large - compress or use WebP');
      score.deductions += 15;
    }

    // Size check
    if (image.sizeKB > 1000) {
      issues.push(`File size too large (${image.sizeKB}KB)`);
      score.deductions += 20;
    } else if (image.sizeKB > 500) {
      issues.push('Large file - compress to improve LCP');
      score.deductions += 10;
    }

    // Dimensions check
    const [width, height] = image.dimensions.split('x').map(Number);
    if (width > 2000 || height > 2000) {
      issues.push('Image dimensions too large for web');
      score.deductions += 15;
    }

    // WebP check
    if (!image.hasWebP && image.format !== 'WebP') {
      issues.push('No WebP version available (better compression)');
      score.deductions += 10;
    }

    return {
      issues,
      score: Math.max(0, score.base - score.deductions),
      optimizationTips: this.getOptimizationTips(image),
      estimatedSavings: this.calculateSavings(image)
    };
  }

  /**
   * Get optimization tips
   */
  getOptimizationTips(image) {
    const tips = [];

    if (!image.hasWebP) {
      const [format] = image.format;
      tips.push(`Convert to WebP format (save ~35% bandwidth)`);
    }

    if (image.sizeKB > 200) {
      tips.push(`Compress to ~50-100KB for web`);
    }

    const [width] = image.dimensions.split('x').map(Number);
    if (width > 1920) {
      tips.push(`Resize to max 1920px width`);
    }

    return tips;
  }

  /**
   * Calculate potential size savings
   */
  calculateSavings(image) {
    let savings = 0;

    if (!image.hasWebP) {
      savings += Math.round(image.sizeKB * 0.35); // WebP saves ~35%
    }

    if (image.sizeKB > 200) {
      savings = Math.max(savings, Math.round(image.sizeKB * 0.6));
    }

    return savings;
  }

  /**
   * Print detailed report
   */
  printReport() {
    console.log(chalk.bold.cyan('\n🖼️  IMAGE OPTIMIZATION REPORT\n'));
    console.log(chalk.gray('─'.repeat(120)));

    // Summary
    const totalSize = this.images.reduce((sum, img) => sum + img.sizeKB, 0);
    const avgScore = Math.round(
      this.images.reduce((sum, img) => sum + img.analysis.score, 0) / this.images.length
    );
    const totalSavings = this.images.reduce((sum, img) => sum + img.analysis.estimatedSavings, 0);

    console.log(chalk.bold.yellow('Summary:'));
    console.log(`  Total Images: ${chalk.blue(this.images.length)}`);
    console.log(`  Total Size: ${chalk.blue(totalSize)}KB`);
    console.log(`  Average Score: ${this.getScoreColor(avgScore)}${avgScore}/100`);
    console.log(`  Potential Savings: ${chalk.green(totalSavings)}KB (~${((totalSavings/totalSize)*100).toFixed(0)}%)\n`);

    // Individual image analysis
    console.log(chalk.bold.yellow('Images:'));
    this.images.forEach((img, i) => {
      const scoreColor = this.getScoreColor(img.analysis.score);
      const statusIcon = img.analysis.score >= 80 ? chalk.green('✓') : chalk.red('⚠');

      console.log(
        `${i + 1}. ${statusIcon} ${chalk.cyan(img.filename)} ${scoreColor}(${img.analysis.score}/100)`
      );
      console.log(`   Size: ${img.sizeKB}KB | Format: ${img.format} | ` +
        `Dimensions: ${img.dimensions} | WebP: ${img.hasWebP ? chalk.green('Yes') : chalk.red('No')}`);

      if (!img.altText || img.altText.trim().length === 0) {
        console.log(`   Alt Text: ${chalk.red('MISSING')}`);
      } else {
        console.log(`   Alt Text: "${img.altText.substring(0, 60)}${img.altText.length > 60 ? '...' : ''}"`);
      }

      if (img.analysis.issues.length > 0) {
        console.log(chalk.red(`   Issues: ${img.analysis.issues.join('; ')}`));
      }

      if (img.analysis.optimizationTips.length > 0) {
        console.log(chalk.yellow(`   Tips: ${img.analysis.optimizationTips[0]}`));
      }

      console.log();
    });

    // Optimization recommendations
    console.log(chalk.bold.cyan('\n💡 OPTIMIZATION RECOMMENDATIONS\n'));

    const missingAlt = this.images.filter(img => !img.altText || img.altText.trim().length === 0);
    if (missingAlt.length > 0) {
      console.log(chalk.red(`✗ ${missingAlt.length} images missing alt text`));
      console.log(`  Add descriptive alt text to ${missingAlt.map(img => `"${img.filename}"`).join(', ')}\n`);
    }

    const notOptimized = this.images.filter(img => !img.hasWebP);
    if (notOptimized.length > 0) {
      console.log(chalk.yellow(`⚠ ${notOptimized.length} images not in WebP format`));
      console.log(`  Convert PNG/JPG to WebP for better compression\n`);
    }

    const large = this.images.filter(img => img.sizeKB > 300);
    if (large.length > 0) {
      console.log(chalk.yellow(`⚠ ${large.length} images are large (>300KB)`));
      console.log(`  Compress: ${large.map(img => `${img.filename} (${img.sizeKB}KB)`).join(', ')}\n`);
    }

    console.log(chalk.gray('─'.repeat(120)));
    console.log(chalk.green(`\n✓ Image analysis complete! Potential savings: ${chalk.yellow(totalSavings + 'KB')}\n`));
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
  console.log(chalk.bold.blue('\n🖼️  Image Optimizer\n'));

  const optimizer = new ImageOptimizer();

  try {
    await optimizer.analyzeImages();
    optimizer.printReport();
  } catch (error) {
    console.error(chalk.red('\n✗ Error:'), error.message);
    process.exit(1);
  }
}

main();
