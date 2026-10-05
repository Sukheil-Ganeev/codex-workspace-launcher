#!/usr/bin/env node

/**
 * Sitemap Generator
 * Automatically generates XML sitemap and robots.txt
 * Usage: npm run sitemap
 */

import fs from 'fs';
import chalk from 'chalk';
import ora from 'ora';

class SitemapGenerator {
  constructor(websiteUrl) {
    this.baseUrl = websiteUrl;
    this.urls = [];
    this.sitemapPath = './exports/sitemap.xml';
    this.robotsPath = './exports/robots.txt';
  }

  /**
   * Generate mock URLs for demonstration
   */
  generateMockUrls() {
    const pages = [
      { url: '/', priority: 1.0, changefreq: 'weekly', lastmod: '2026-02-04' },
      { url: '/tours', priority: 0.9, changefreq: 'weekly', lastmod: '2026-02-04' },
      { url: '/tours/desert-safari', priority: 0.8, changefreq: 'weekly', lastmod: '2026-02-03' },
      { url: '/tours/city-tour', priority: 0.8, changefreq: 'weekly', lastmod: '2026-02-02' },
      { url: '/tours/yacht-cruise', priority: 0.8, changefreq: 'weekly', lastmod: '2026-02-01' },
      { url: '/about', priority: 0.7, changefreq: 'monthly', lastmod: '2026-01-15' },
      { url: '/contact', priority: 0.7, changefreq: 'monthly', lastmod: '2026-01-20' },
      { url: '/blog', priority: 0.7, changefreq: 'daily', lastmod: '2026-02-04' },
      { url: '/blog/dubai-desert-tips', priority: 0.6, changefreq: 'monthly', lastmod: '2026-01-25' },
      { url: '/blog/best-time-visit-uae', priority: 0.6, changefreq: 'monthly', lastmod: '2026-01-30' },
      { url: '/faq', priority: 0.6, changefreq: 'monthly', lastmod: '2026-02-01' },
      { url: '/terms', priority: 0.5, changefreq: 'yearly', lastmod: '2026-01-01' },
      { url: '/privacy', priority: 0.5, changefreq: 'yearly', lastmod: '2026-01-01' }
    ];

    return pages.map(page => ({
      ...page,
      url: this.baseUrl + page.url
    }));
  }

  /**
   * Generate XML Sitemap
   */
  generateXMLSitemap() {
    const spinner = ora('Generating XML sitemap...').start();

    try {
      this.urls = this.generateMockUrls();

      let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
      xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';

      this.urls.forEach(page => {
        xml += '  <url>\n';
        xml += `    <loc>${this.escapeXml(page.url)}</loc>\n`;
        xml += `    <lastmod>${page.lastmod}</lastmod>\n`;
        xml += `    <changefreq>${page.changefreq}</changefreq>\n`;
        xml += `    <priority>${page.priority}</priority>\n`;
        xml += '  </url>\n';
      });

      xml += '</urlset>';

      const exportDir = './exports';
      if (!fs.existsSync(exportDir)) {
        fs.mkdirSync(exportDir, { recursive: true });
      }

      fs.writeFileSync(this.sitemapPath, xml);
      spinner.succeed(`Sitemap generated (${this.urls.length} URLs)`);
      return true;
    } catch (error) {
      spinner.fail('Failed to generate sitemap');
      console.error(chalk.red('Error:'), error.message);
      return false;
    }
  }

  /**
   * Generate Robots.txt
   */
  generateRobotsTxt() {
    const spinner = ora('Generating robots.txt...').start();

    try {
      let robots = '# Robots.txt for SEO Optimization\n\n';
      robots += '# Allow all user agents\n';
      robots += 'User-agent: *\n';
      robots += 'Allow: /\n\n';

      robots += '# Disallow specific paths\n';
      robots += 'Disallow: /admin/\n';
      robots += 'Disallow: /private/\n';
      robots += 'Disallow: /temp/\n';
      robots += 'Disallow: /*.pdf$\n\n';

      robots += '# Crawl delay\n';
      robots += 'Crawl-delay: 1\n\n';

      robots += '# Sitemap location\n';
      robots += `Sitemap: ${this.baseUrl}/sitemap.xml\n\n`;

      robots += '# Common bot rules\n';
      robots += 'User-agent: Googlebot\n';
      robots += 'Allow: /\n\n';

      robots += 'User-agent: MJ12bot\n';
      robots += 'Disallow: /\n';

      const exportDir = './exports';
      if (!fs.existsSync(exportDir)) {
        fs.mkdirSync(exportDir, { recursive: true });
      }

      fs.writeFileSync(this.robotsPath, robots);
      spinner.succeed('robots.txt generated');
      return true;
    } catch (error) {
      spinner.fail('Failed to generate robots.txt');
      console.error(chalk.red('Error:'), error.message);
      return false;
    }
  }

  /**
   * Validate sitemap XML
   */
  validateSitemap() {
    const spinner = ora('Validating sitemap...').start();

    try {
      if (!fs.existsSync(this.sitemapPath)) {
        throw new Error('Sitemap file not found');
      }

      const content = fs.readFileSync(this.sitemapPath, 'utf8');

      // Basic XML validation
      if (!content.includes('<?xml') || !content.includes('</urlset>')) {
        throw new Error('Invalid XML structure');
      }

      // Count URLs
      const urlCount = (content.match(/<url>/g) || []).length;

      // Check for 50K URL limit
      if (urlCount > 50000) {
        spinner.warn(`Sitemap exceeds 50K URL limit (${urlCount} URLs)`);
      } else {
        spinner.succeed(`Sitemap valid (${urlCount} URLs)`);
      }

      return { valid: true, urlCount };
    } catch (error) {
      spinner.fail('Sitemap validation failed');
      console.error(chalk.red('Error:'), error.message);
      return { valid: false, urlCount: 0 };
    }
  }

  /**
   * Escape XML special characters
   */
  escapeXml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;');
  }

  /**
   * Print results
   */
  printResults(validation) {
    console.log(chalk.bold.cyan('\n📋 SITEMAP GENERATION REPORT\n'));
    console.log(chalk.gray('─'.repeat(80)));

    console.log(chalk.bold.yellow('Files Generated:'));
    console.log(`  ✓ ${chalk.cyan(this.sitemapPath)}`);
    console.log(`  ✓ ${chalk.cyan(this.robotsPath)}\n`);

    console.log(chalk.bold.yellow('Sitemap Details:'));
    console.log(`  Total URLs: ${chalk.blue(validation.urlCount)}`);
    console.log(`  Status: ${validation.valid ? chalk.green('Valid') : chalk.red('Invalid')}`);

    console.log(chalk.bold.yellow('\nTop URLs in Sitemap:'));
    this.urls.slice(0, 10).forEach((page, i) => {
      console.log(
        `  ${i + 1}. ${chalk.cyan(page.url.replace(this.baseUrl, ''))} | ` +
        `Priority: ${chalk.magenta(page.priority)} | ` +
        `Freq: ${chalk.blue(page.changefreq)}`
      );
    });

    if (this.urls.length > 10) {
      console.log(`  ... and ${chalk.yellow(this.urls.length - 10)} more URLs`);
    }

    console.log(chalk.gray('\n─'.repeat(80)));
    console.log(chalk.green('\n✓ Sitemap generation complete!\n'));
  }
}

/**
 * Main execution
 */
async function main() {
  console.log(chalk.bold.blue('\n🗺️  Sitemap Generator\n'));

  const baseUrl = process.env.WEBSITE_URL || 'https://example.com';
  const generator = new SitemapGenerator(baseUrl);

  try {
    const sitemapCreated = generator.generateXMLSitemap();
    const robotsCreated = generator.generateRobotsTxt();

    if (sitemapCreated && robotsCreated) {
      const validation = generator.validateSitemap();
      generator.printResults(validation);
    }
  } catch (error) {
    console.error(chalk.red('\n✗ Error:'), error.message);
    process.exit(1);
  }
}

main();
