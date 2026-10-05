import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * API Keys Configuration
 * Load environment variables and validate required keys
 */
class APIConfig {
  constructor() {
    this.validated = false;
    this.errors = [];
    this.validate();
  }

  /**
   * Validate all required API configurations
   */
  validate() {
    // Check Google Credentials
    const credentialsPath = process.env.GOOGLE_CREDENTIALS_PATH || './config/google-credentials.json';
    if (!fs.existsSync(credentialsPath)) {
      this.errors.push(`Google credentials file not found: ${credentialsPath}`);
    } else {
      try {
        JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));
      } catch (e) {
        this.errors.push(`Invalid Google credentials JSON: ${e.message}`);
      }
    }

    // Check required environment variables
    const required = ['WEBSITE_URL', 'WEBSITE_DOMAIN', 'GOOGLE_PROPERTY_URL'];
    required.forEach(key => {
      if (!process.env[key]) {
        this.errors.push(`Missing required environment variable: ${key}`);
      }
    });

    this.validated = this.errors.length === 0;
  }

  /**
   * Get Google credentials
   */
  getGoogleCredentials() {
    const path = process.env.GOOGLE_CREDENTIALS_PATH || './config/google-credentials.json';
    try {
      return JSON.parse(fs.readFileSync(path, 'utf8'));
    } catch (e) {
      throw new Error(`Failed to load Google credentials: ${e.message}`);
    }
  }

  /**
   * Get config value with fallback
   */
  get(key, defaultValue = null) {
    return process.env[key] || defaultValue;
  }

  /**
   * Check if config is valid
   */
  isValid() {
    return this.validated;
  }

  /**
   * Get validation errors
   */
  getErrors() {
    return this.errors;
  }
}

export default new APIConfig();
