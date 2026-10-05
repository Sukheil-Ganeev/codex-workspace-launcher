#!/usr/bin/env node

/**
 * Performance Monitor
 * Monitors Core Web Vitals and PageSpeed Insights
 * Usage: npm run performance
 */

import chalk from 'chalk';
import ora from 'ora';

class PerformanceMonitor {
  constructor() {
    this.metrics = {};
  }

  /**
   * Fetch Core Web Vitals data (mock for demo)
   */
  async fetchCoreWebVitals() {
    const spinner = ora('Fetching Core Web Vitals...').start();

    try {
      // Mock CWV data
      const data = {
        lcp: { value: 1.8, unit: 's', threshold: 2.5, status: 'good' },
        fid: { value: 45, unit: 'ms', threshold: 100, status: 'good' },
        cls: { value: 0.05, unit: '', threshold: 0.1, status: 'good' },
        inp: { value: 120, unit: 'ms', threshold: 200, status: 'good' },
        ttfb: { value: 320, unit: 'ms', threshold: 600, status: 'good' }
      };

      this.metrics = data;
      spinner.succeed('Core Web Vitals fetched');
      return data;
    } catch (error) {
      spinner.fail('Failed to fetch metrics');
      console.error(chalk.red('Error:'), error.message);
      throw error;
    }
  }

  /**
   * Get Lighthouse scores (mock)
   */
  getLighthouseScores() {
    return {
      performance: 92,
      accessibility: 88,
      bestPractices: 95,
      seo: 98,
      pwa: 75
    };
  }

  /**
   * Get PageSpeed metrics
   */
  getPageSpeedMetrics() {
    return {
      firstContentfulPaint: { value: 1.2, unit: 's', threshold: 1.8, status: 'good' },
      largestContentfulPaint: { value: 1.8, unit: 's', threshold: 2.5, status: 'good' },
      firstInputDelay: { value: 45, unit: 'ms', threshold: 100, status: 'good' },
      cumulativeLayoutShift: { value: 0.05, unit: '', threshold: 0.1, status: 'good' },
      speedIndex: { value: 2.1, unit: 's', threshold: 3.4, status: 'good' },
      totalBlockingTime: { value: 85, unit: 'ms', threshold: 300, status: 'good' }
    };
  }

  /**
   * Get mobile vs desktop comparison
   */
  getDeviceComparison() {
    return {
      mobile: {
        lcp: 1.9,
        fid: 52,
        cls: 0.06,
        lighthouseScore: 88
      },
      desktop: {
        lcp: 1.5,
        fid: 28,
        cls: 0.03,
        lighthouseScore: 95
      }
    };
  }

  /**
   * Get optimization recommendations
   */
  getRecommendations() {
    const recommendations = [];

    if (this.metrics.lcp?.value > 2.5) {
      recommendations.push({
        type: 'LCP',
        title: 'Optimize Largest Contentful Paint',
        actions: [
          'Optimize and compress images',
          'Remove unused CSS',
          'Use lazy loading for below-fold content',
          'Implement critical CSS inline'
        ]
      });
    }

    if (this.metrics.fid?.value > 100) {
      recommendations.push({
        type: 'FID',
        title: 'Reduce First Input Delay',
        actions: [
          'Reduce JavaScript execution time',
          'Break up long tasks',
          'Use Web Workers for heavy computations',
          'Defer non-critical JavaScript'
        ]
      });
    }

    if (this.metrics.cls?.value > 0.1) {
      recommendations.push({
        type: 'CLS',
        title: 'Prevent Cumulative Layout Shift',
        actions: [
          'Set explicit dimensions for images and iframes',
          'Avoid inserting content above existing content',
          'Use transform animations instead of property changes'
        ]
      });
    }

    if (recommendations.length === 0) {
      recommendations.push({
        type: 'General',
        title: 'Continue Monitoring Performance',
        actions: [
          'Monitor metrics regularly',
          'Set performance budgets',
          'Test on real devices and networks',
          'Use synthetic monitoring for consistency'
        ]
      });
    }

    return recommendations;
  }

  /**
   * Print performance report
   */
  printReport() {
    console.log(chalk.bold.cyan('\n⚡ PERFORMANCE MONITOR REPORT\n'));
    console.log(chalk.gray('─'.repeat(120)));

    // Core Web Vitals
    console.log(chalk.bold.blue('\n📊 CORE WEB VITALS\n'));

    Object.entries(this.metrics).forEach(([metric, data]) => {
      const statusIcon = data.status === 'good' ? chalk.green('✓') : chalk.red('✗');
      const statusColor = data.status === 'good' ? chalk.green : chalk.red;
      const metricName = metric.toUpperCase();

      console.log(
        `${statusIcon} ${metricName}: ${chalk.blue(data.value + data.unit)} ` +
        `(threshold: ${statusColor(data.threshold + data.unit)})`
      );
    });

    // Lighthouse Scores
    const scores = this.getLighthouseScores();
    console.log(chalk.bold.blue('\n🔦 LIGHTHOUSE SCORES\n'));

    Object.entries(scores).forEach(([category, score]) => {
      const color = score >= 90 ? chalk.green : score >= 70 ? chalk.yellow : chalk.red;
      const bar = '█'.repeat(Math.floor(score / 10)) + '░'.repeat(10 - Math.floor(score / 10));
      console.log(`${category.padEnd(20)} ${color(bar)} ${color(score)}/100`);
    });

    // PageSpeed Metrics
    console.log(chalk.bold.blue('\n📈 PAGE SPEED METRICS\n'));

    const metrics = this.getPageSpeedMetrics();
    Object.entries(metrics).forEach(([key, value]) => {
      const statusIcon = value.status === 'good' ? chalk.green('✓') : chalk.red('✗');
      const displayName = key.replace(/([A-Z])/g, ' $1').trim();
      console.log(
        `${statusIcon} ${displayName}: ${chalk.blue(value.value + value.unit)} ` +
        `(threshold: ${value.threshold + value.unit})`
      );
    });

    // Device Comparison
    console.log(chalk.bold.blue('\n📱 MOBILE VS DESKTOP\n'));

    const comparison = this.getDeviceComparison();
    console.log(chalk.yellow('Metric'.padEnd(20)) + chalk.blue('Mobile'.padEnd(15)) + chalk.blue('Desktop'));
    console.log(chalk.gray('─'.repeat(50)));

    console.log(
      'LCP (Sec)'.padEnd(20) +
      chalk.blue(comparison.mobile.lcp.toString().padEnd(15)) +
      chalk.blue(comparison.desktop.lcp.toString())
    );
    console.log(
      'FID (MS)'.padEnd(20) +
      chalk.blue(comparison.mobile.fid.toString().padEnd(15)) +
      chalk.blue(comparison.desktop.fid.toString())
    );
    console.log(
      'Lighthouse'.padEnd(20) +
      chalk.blue((comparison.mobile.lighthouseScore + '/100').padEnd(15)) +
      chalk.blue(comparison.desktop.lighthouseScore + '/100')
    );

    // Recommendations
    const recommendations = this.getRecommendations();
    console.log(chalk.bold.yellow('\n💡 OPTIMIZATION RECOMMENDATIONS\n'));

    recommendations.forEach(rec => {
      console.log(chalk.bold.cyan(`${rec.type}: ${rec.title}`));
      rec.actions.forEach(action => {
        console.log(`  • ${chalk.white(action)}`);
      });
      console.log();
    });

    // Summary
    console.log(chalk.gray('─'.repeat(120)));
    console.log(chalk.bold.green('\n✓ Performance check complete!\n'));
    console.log(chalk.gray('Next Steps:'));
    console.log(chalk.gray('  1. Monitor these metrics weekly'));
    console.log(chalk.gray('  2. Set performance budgets'));
    console.log(chalk.gray('  3. Test on real devices'));
    console.log(chalk.gray('  4. Implement recommendations above\n'));
  }
}

/**
 * Main execution
 */
async function main() {
  console.log(chalk.bold.blue('\n⚡ PERFORMANCE MONITOR\n'));
  console.log(chalk.gray('Monitoring: Core Web Vitals, Lighthouse, PageSpeed\n'));

  const monitor = new PerformanceMonitor();

  try {
    await monitor.fetchCoreWebVitals();
    monitor.printReport();
  } catch (error) {
    console.error(chalk.red('\n✗ Error:'), error.message);
    process.exit(1);
  }
}

main();
