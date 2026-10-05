/**
 * Multi-Currency Pricer Template
 *
 * Real-time currency conversion with markup application for tourism pricing.
 * Supports AED, USD, RUB, KZT, EUR, GBP with automatic rate updates.
 *
 * Features:
 * - Fetch real-time exchange rates
 * - Apply markup (profit margin)
 * - Cache rates to reduce API calls
 * - Format prices for display
 * - Support for multiple currency APIs
 *
 * Usage:
 *   const pricer = new MultiCurrencyPricer({
 *     baseCurrency: 'AED',
 *     markup: 3.0 // 3% markup
 *   });
 *
 *   await pricer.updateRates();
 *   const priceUSD = pricer.convert(100, 'AED', 'USD');
 */

require('dotenv').config();
const fs = require('fs');
const path = require('path');

// Supported currencies
const SUPPORTED_CURRENCIES = ['AED', 'USD', 'RUB', 'KZT', 'EUR', 'GBP'];

class MultiCurrencyPricer {
  constructor(options = {}) {
    const {
      baseCurrency = 'AED',
      markup = 2.0, // Default 2% markup
      cacheFile = './currency-rates-cache.json',
      cacheExpiryHours = 24,
    } = options;

    this.baseCurrency = baseCurrency;
    this.markup = markup;
    this.cacheFile = cacheFile;
    this.cacheExpiryHours = cacheExpiryHours;
    this.rates = {};
    this.lastUpdated = null;

    // Load cached rates
    this.loadCache();
  }

  /**
   * Update exchange rates from API
   */
  async updateRates() {
    try {
      // Check cache first
      if (this.isCacheValid()) {
        console.log('Using cached rates');
        return this.rates;
      }

      console.log('Fetching fresh exchange rates...');

      // Try primary API
      const rates = await this.fetchRatesFromAPI();

      if (rates) {
        this.rates = rates;
        this.lastUpdated = new Date();
        this.saveCache();
        console.log('Rates updated successfully');
        return this.rates;
      }

      throw new Error('Failed to fetch rates from all sources');
    } catch (err) {
      console.error('Failed to update rates:', err.message);

      // Fallback to cached rates if available
      if (Object.keys(this.rates).length > 0) {
        console.log('Using stale cached rates as fallback');
        return this.rates;
      }

      throw err;
    }
  }

  /**
   * Fetch rates from Exchange Rate API (free tier)
   */
  async fetchRatesFromAPI() {
    try {
      // Option 1: ExchangeRate-API (free, no key required for basic use)
      const url = `https://open.exchangerate-api.com/v6/latest/${this.baseCurrency}`;

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }

      const data = await response.json();

      // Filter to supported currencies
      const filteredRates = {};
      SUPPORTED_CURRENCIES.forEach((currency) => {
        if (data.rates[currency]) {
          filteredRates[currency] = data.rates[currency];
        }
      });

      return filteredRates;
    } catch (err) {
      console.error('ExchangeRate-API failed:', err.message);

      // Fallback: Try alternative API
      return await this.fetchRatesFromFallbackAPI();
    }
  }

  /**
   * Fallback API (e.g., fixer.io, currencyapi.com)
   */
  async fetchRatesFromFallbackAPI() {
    // For production, you'd use a paid API like:
    // - https://fixer.io
    // - https://currencyapi.com
    // - https://exchangeratesapi.io

    console.log('Using fallback rates (static)');

    // Static fallback rates (update these periodically)
    return {
      AED: 1.0,
      USD: 0.272, // 1 AED = 0.272 USD
      RUB: 25.0, // 1 AED = 25 RUB (approximate, varies with sanctions)
      KZT: 130.0, // 1 AED = 130 KZT
      EUR: 0.25, // 1 AED = 0.25 EUR
      GBP: 0.21, // 1 AED = 0.21 GBP
    };
  }

  /**
   * Convert amount from one currency to another
   */
  convert(amount, fromCurrency, toCurrency, applyMarkup = true) {
    if (Object.keys(this.rates).length === 0) {
      throw new Error('Rates not loaded. Call updateRates() first.');
    }

    if (!SUPPORTED_CURRENCIES.includes(fromCurrency) || !SUPPORTED_CURRENCIES.includes(toCurrency)) {
      throw new Error(`Unsupported currency: ${fromCurrency} or ${toCurrency}`);
    }

    // Convert from -> base -> to
    const fromRate = this.rates[fromCurrency] || 1;
    const toRate = this.rates[toCurrency] || 1;

    let convertedAmount = (amount / fromRate) * toRate;

    // Apply markup if needed
    if (applyMarkup && this.markup > 0) {
      convertedAmount = convertedAmount * (1 + this.markup / 100);
    }

    return convertedAmount;
  }

  /**
   * Format price for display
   */
  formatPrice(amount, currency, locale = 'en-US') {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  }

  /**
   * Get price in multiple currencies
   */
  getPricesInAllCurrencies(amount, fromCurrency = 'AED') {
    const prices = {};

    SUPPORTED_CURRENCIES.forEach((currency) => {
      const converted = this.convert(amount, fromCurrency, currency);
      prices[currency] = {
        amount: converted,
        formatted: this.formatPrice(converted, currency),
      };
    });

    return prices;
  }

  /**
   * Check if cache is valid
   */
  isCacheValid() {
    if (!this.lastUpdated) return false;

    const now = new Date();
    const diffHours = (now - this.lastUpdated) / (1000 * 60 * 60);

    return diffHours < this.cacheExpiryHours;
  }

  /**
   * Load cached rates from file
   */
  loadCache() {
    try {
      if (fs.existsSync(this.cacheFile)) {
        const cache = JSON.parse(fs.readFileSync(this.cacheFile, 'utf8'));
        this.rates = cache.rates || {};
        this.lastUpdated = cache.lastUpdated ? new Date(cache.lastUpdated) : null;
        console.log('Loaded cached rates from', this.cacheFile);
      }
    } catch (err) {
      console.warn('Failed to load cache:', err.message);
    }
  }

  /**
   * Save rates to cache file
   */
  saveCache() {
    try {
      const cache = {
        rates: this.rates,
        lastUpdated: this.lastUpdated,
      };
      fs.writeFileSync(this.cacheFile, JSON.stringify(cache, null, 2));
      console.log('Cached rates saved to', this.cacheFile);
    } catch (err) {
      console.warn('Failed to save cache:', err.message);
    }
  }

  /**
   * Get current markup percentage
   */
  getMarkup() {
    return this.markup;
  }

  /**
   * Set markup percentage
   */
  setMarkup(markup) {
    this.markup = markup;
    console.log('Markup updated to', markup, '%');
  }
}

// CLI usage example
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];

  const pricer = new MultiCurrencyPricer({
    baseCurrency: 'AED',
    markup: 2.5, // 2.5% markup
  });

  switch (command) {
    case 'update':
      pricer
        .updateRates()
        .then(() => {
          console.log('\n✅ Rates updated successfully!');
          console.log('Current rates (1 AED = ):');
          Object.entries(pricer.rates).forEach(([currency, rate]) => {
            console.log(`  ${currency}: ${rate}`);
          });
        })
        .catch((err) => console.error('Error:', err.message));
      break;

    case 'convert':
      const amount = parseFloat(args[1]);
      const from = args[2]?.toUpperCase() || 'AED';
      const to = args[3]?.toUpperCase() || 'USD';

      pricer
        .updateRates()
        .then(() => {
          const converted = pricer.convert(amount, from, to);
          console.log(
            `\n${pricer.formatPrice(amount, from)} = ${pricer.formatPrice(
              converted,
              to
            )}`
          );
          console.log(`(includes ${pricer.markup}% markup)`);
        })
        .catch((err) => console.error('Error:', err.message));
      break;

    case 'all':
      const amountAll = parseFloat(args[1]) || 100;

      pricer
        .updateRates()
        .then(() => {
          console.log(`\n📊 ${amountAll} AED in all currencies:\n`);
          const prices = pricer.getPricesInAllCurrencies(amountAll);
          Object.entries(prices).forEach(([currency, price]) => {
            console.log(`  ${currency}: ${price.formatted}`);
          });
          console.log(`\n(Markup: ${pricer.markup}%)`);
        })
        .catch((err) => console.error('Error:', err.message));
      break;

    default:
      console.log(`
Usage:
  node multi-currency-pricer.js update              # Update exchange rates
  node multi-currency-pricer.js convert <amount> <from> <to>
  node multi-currency-pricer.js all [amount]        # Show in all currencies

Examples:
  node multi-currency-pricer.js update
  node multi-currency-pricer.js convert 100 AED USD
  node multi-currency-pricer.js all 250
      `);
  }
}

module.exports = MultiCurrencyPricer;
