#!/usr/bin/env node

/**
 * Database Seed Generator using Faker.js
 * Generates realistic test data for development
 * Usage: node seed.js [--count 100] [--clear] [--seed-file path]
 */

const db = require('./db');
const logger = require('./logger');

// Mock faker implementation (if faker.js not installed)
class SimpleGenerator {
  static faker = {
    person: {
      firstName: () => ['John', 'Jane', 'Bob', 'Alice', 'Charlie'][Math.floor(Math.random() * 5)],
      lastName: () => ['Smith', 'Johnson', 'Brown', 'Davis', 'Wilson'][Math.floor(Math.random() * 5)],
      email: function() {
        return `${this.firstName().toLowerCase()}.${this.lastName().toLowerCase()}@example.com`;
      },
    },
    internet: {
      username: () => `user_${Math.random().toString(36).substring(7)}`,
      password: () => Math.random().toString(36).substring(2, 15),
    },
    phone: {
      number: () => `+1${Math.floor(Math.random() * 9000000000) + 1000000000}`,
    },
    location: {
      country: () => ['USA', 'Canada', 'UK', 'Germany', 'France'][Math.floor(Math.random() * 5)],
      city: () => ['New York', 'Toronto', 'London', 'Berlin', 'Paris'][Math.floor(Math.random() * 5)],
    },
    datatype: {
      number: (max = 1000) => Math.floor(Math.random() * max),
      boolean: () => Math.random() > 0.5,
      uuid: () => 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      }),
    },
    date: {
      past: () => new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000),
      future: () => new Date(Date.now() + Math.random() * 365 * 24 * 60 * 60 * 1000),
    },
    lorem: {
      word: () => ['hello', 'world', 'test', 'data', 'sample'][Math.floor(Math.random() * 5)],
      sentence: () => 'This is a sample test sentence.',
    },
  };

  static generateUser(index) {
    const firstName = this.faker.person.firstName();
    const lastName = this.faker.person.lastName();
    return {
      id: this.faker.datatype.uuid(),
      email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}.${index}@test.com`,
      username: this.faker.internet.username(),
      first_name: firstName,
      last_name: lastName,
      phone: this.faker.phone.number(),
      country: this.faker.location.country(),
      created_at: new Date(),
    };
  }

  static generateProduct(index) {
    return {
      id: this.faker.datatype.uuid(),
      name: `Product ${index}`,
      description: this.faker.lorem.sentence(),
      price: Math.floor(Math.random() * 1000) + 10,
      stock: Math.floor(Math.random() * 100),
      created_at: new Date(),
    };
  }

  static generateOrder(index) {
    return {
      id: this.faker.datatype.uuid(),
      user_id: this.faker.datatype.uuid(),
      total: Math.floor(Math.random() * 500) + 10,
      status: ['pending', 'completed', 'cancelled'][Math.floor(Math.random() * 3)],
      created_at: new Date(),
    };
  }
}

class DatabaseSeeder {
  constructor() {
    this.count = parseInt(process.argv.find(a => a.includes('--count'))?.split('=')[1] || '100');
    this.shouldClear = process.argv.includes('--clear');
  }

  async init() {
    try {
      await db.connect();
    } catch (err) {
      logger.error('Failed to connect to database', err.message);
      process.exit(1);
    }
  }

  async seedUsers() {
    logger.info(`Seeding ${this.count} users...`);

    try {
      const values = [];
      for (let i = 0; i < this.count; i++) {
        const user = SimpleGenerator.generateUser(i);
        values.push([
          user.id,
          user.email,
          user.username,
          user.first_name,
          user.last_name,
          user.phone,
          user.country,
          user.created_at,
        ]);

        if ((i + 1) % 10 === 0) {
          logger.progress(i + 1, this.count, 'users');
        }
      }

      // Insert in batches
      for (let i = 0; i < values.length; i += 100) {
        const batch = values.slice(i, i + 100);
        const placeholders = batch.map((_, idx) => {
          const offset = idx * 8;
          return `($${offset + 1}, $${offset + 2}, $${offset + 3}, $${offset + 4}, $${offset + 5}, $${offset + 6}, $${offset + 7}, $${offset + 8})`;
        }).join(',');

        const sql = `INSERT INTO users (id, email, username, first_name, last_name, phone, country, created_at)
          VALUES ${placeholders}
          ON CONFLICT (email) DO NOTHING`;

        const flatParams = batch.flat();
        await db.query(sql, flatParams);
      }

      logger.progressEnd();
      logger.success(`Seeded ${this.count} users`);
    } catch (err) {
      logger.error('Failed to seed users', err.message);
    }
  }

  async seedProducts() {
    logger.info(`Seeding ${this.count} products...`);

    try {
      const values = [];
      for (let i = 0; i < this.count; i++) {
        const product = SimpleGenerator.generateProduct(i);
        values.push([
          product.id,
          product.name,
          product.description,
          product.price,
          product.stock,
          product.created_at,
        ]);

        if ((i + 1) % 10 === 0) {
          logger.progress(i + 1, this.count, 'products');
        }
      }

      // Insert in batches
      for (let i = 0; i < values.length; i += 100) {
        const batch = values.slice(i, i + 100);
        const placeholders = batch.map((_, idx) => {
          const offset = idx * 6;
          return `($${offset + 1}, $${offset + 2}, $${offset + 3}, $${offset + 4}, $${offset + 5}, $${offset + 6})`;
        }).join(',');

        const sql = `INSERT INTO products (id, name, description, price, stock, created_at)
          VALUES ${placeholders}
          ON CONFLICT (id) DO NOTHING`;

        const flatParams = batch.flat();
        await db.query(sql, flatParams);
      }

      logger.progressEnd();
      logger.success(`Seeded ${this.count} products`);
    } catch (err) {
      logger.error('Failed to seed products', err.message);
    }
  }

  async clearTables() {
    logger.warn('Clearing existing data...');

    const tables = ['orders', 'products', 'users'];
    for (const table of tables) {
      try {
        await db.query(`TRUNCATE TABLE ${table} CASCADE`);
        logger.success(`Cleared ${table}`);
      } catch (err) {
        logger.debug(`Could not clear ${table} (may not exist)`);
      }
    }
  }

  async seed() {
    try {
      if (this.shouldClear) {
        await this.clearTables();
      }

      await this.seedUsers();
      await this.seedProducts();

      logger.success('Database seeding completed!');
    } catch (err) {
      logger.error('Seeding failed', err.message);
      process.exit(1);
    }
  }
}

async function main() {
  const seeder = new DatabaseSeeder();

  try {
    await seeder.init();
    await seeder.seed();
  } catch (err) {
    logger.error('Fatal error', err.message);
    process.exit(1);
  } finally {
    await db.disconnect();
  }
}

main();
