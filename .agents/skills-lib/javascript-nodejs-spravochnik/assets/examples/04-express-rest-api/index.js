/**
 * Express REST API
 * Tours management API with JWT authentication
 */

require('dotenv').config();
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const { Pool } = require('pg');
const Joi = require('joi');
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const winston = require('winston');

// Logger
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: './logs/api.log' })
  ]
});

// Database
const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

const app = express();

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100
}));

// ===== VALIDATION SCHEMAS =====
const tourSchema = Joi.object({
  name: Joi.string().required().max(255),
  description: Joi.string().max(500),
  price: Joi.number().positive().required(),
  duration: Joi.number().integer().positive(),
  maxGuests: Joi.number().integer().positive()
});

const authSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(6).required()
});

// ===== AUTH MIDDLEWARE =====
const authenticate = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.userId = decoded.id;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};

// ===== AUTH ROUTES =====

app.post('/api/auth/register', async (req, res) => {
  try {
    const { error, value } = authSchema.validate(req.body);

    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const hashedPassword = await bcrypt.hash(value.password, 10);

    const result = await pool.query(
      'INSERT INTO users (email, password) VALUES ($1, $2) RETURNING id, email',
      [value.email, hashedPassword]
    );

    const token = jwt.sign(
      { id: result.rows[0].id },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRE || '7d' }
    );

    res.status(201).json({
      message: 'User created',
      token,
      user: result.rows[0]
    });
  } catch (error) {
    logger.error(`Registration failed: ${error.message}`);
    res.status(500).json({ error: 'Registration failed' });
  }
});

app.post('/api/auth/login', async (req, res) => {
  try {
    const { error, value } = authSchema.validate(req.body);

    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const result = await pool.query(
      'SELECT id, password FROM users WHERE email = $1',
      [value.email]
    );

    if (result.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const user = result.rows[0];
    const passwordMatch = await bcrypt.compare(value.password, user.password);

    if (!passwordMatch) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = jwt.sign(
      { id: user.id },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRE || '7d' }
    );

    res.json({ token });
  } catch (error) {
    logger.error(`Login failed: ${error.message}`);
    res.status(500).json({ error: 'Login failed' });
  }
});

// ===== TOURS ROUTES =====

// GET all tours (public)
app.get('/api/tours', async (req, res) => {
  try {
    const { page = 1, limit = 10, sort = '-created_at' } = req.query;

    const offset = (page - 1) * limit;

    const result = await pool.query(
      `SELECT * FROM tours ORDER BY created_at DESC LIMIT $1 OFFSET $2`,
      [limit, offset]
    );

    res.json({
      tours: result.rows,
      pagination: { page, limit }
    });
  } catch (error) {
    logger.error(`Failed to fetch tours: ${error.message}`);
    res.status(500).json({ error: 'Failed to fetch tours' });
  }
});

// GET single tour
app.get('/api/tours/:id', async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM tours WHERE id = $1',
      [req.params.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Tour not found' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch tour' });
  }
});

// POST create tour (authenticated)
app.post('/api/tours', authenticate, async (req, res) => {
  try {
    const { error, value } = tourSchema.validate(req.body);

    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const result = await pool.query(
      `INSERT INTO tours (name, description, price, duration, max_guests, created_by)
       VALUES ($1, $2, $3, $4, $5, $6)
       RETURNING *`,
      [
        value.name,
        value.description,
        value.price,
        value.duration,
        value.maxGuests,
        req.userId
      ]
    );

    logger.info(`Tour created: ${result.rows[0].id}`);

    res.status(201).json(result.rows[0]);
  } catch (error) {
    logger.error(`Failed to create tour: ${error.message}`);
    res.status(500).json({ error: 'Failed to create tour' });
  }
});

// PUT update tour
app.put('/api/tours/:id', authenticate, async (req, res) => {
  try {
    const { error, value } = tourSchema.validate(req.body);

    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const result = await pool.query(
      `UPDATE tours SET name = $1, description = $2, price = $3, duration = $4, max_guests = $5, updated_at = NOW()
       WHERE id = $6 AND created_by = $7
       RETURNING *`,
      [
        value.name,
        value.description,
        value.price,
        value.duration,
        value.maxGuests,
        req.params.id,
        req.userId
      ]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Tour not found or unauthorized' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    res.status(500).json({ error: 'Failed to update tour' });
  }
});

// DELETE tour
app.delete('/api/tours/:id', authenticate, async (req, res) => {
  try {
    const result = await pool.query(
      'DELETE FROM tours WHERE id = $1 AND created_by = $2 RETURNING id',
      [req.params.id, req.userId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Tour not found or unauthorized' });
    }

    logger.info(`Tour deleted: ${req.params.id}`);

    res.json({ message: 'Tour deleted' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to delete tour' });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// ===== DATABASE INITIALIZATION =====
async function initializeDatabase() {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    await pool.query(`
      CREATE TABLE IF NOT EXISTS tours (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        price DECIMAL(10, 2) NOT NULL,
        duration INTEGER,
        max_guests INTEGER,
        created_by INTEGER REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    logger.info('Database initialized');
  } catch (error) {
    logger.error(`Database initialization failed: ${error.message}`);
  }
}

// ===== SERVER STARTUP =====
const PORT = process.env.PORT || 3000;

async function start() {
  await initializeDatabase();

  app.listen(PORT, () => {
    logger.info(`API running on port ${PORT}`);
  });
}

start();

module.exports = app;
