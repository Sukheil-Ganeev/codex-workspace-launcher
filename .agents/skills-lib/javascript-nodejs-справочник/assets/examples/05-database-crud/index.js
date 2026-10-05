/**
 * Database CRUD Operations
 * Guides management with optimized queries and transactions
 */

require('dotenv').config();
const express = require('express');
const { Pool } = require('pg');
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [new winston.transports.Console()]
});

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: parseInt(process.env.DATABASE_POOL_SIZE) || 10
});

const app = express();
app.use(express.json());

// CREATE - Add new guide
app.post('/guides', async (req, res) => {
  try {
    const { name, email, languages, experience } = req.body;

    const result = await pool.query(
      'INSERT INTO guides (name, email, languages, experience) VALUES ($1, $2, $3, $4) RETURNING *',
      [name, email, languages, experience]
    );

    res.status(201).json(result.rows[0]);
  } catch (error) {
    logger.error(`Create failed: ${error.message}`);
    res.status(500).json({ error: 'Create failed' });
  }
});

// READ - Get all guides
app.get('/guides', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM guides ORDER BY created_at DESC');
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({ error: 'Read failed' });
  }
});

// READ - Get single guide
app.get('/guides/:id', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM guides WHERE id = $1', [req.params.id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Not found' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    res.status(500).json({ error: 'Read failed' });
  }
});

// UPDATE - Modify guide
app.put('/guides/:id', async (req, res) => {
  try {
    const { name, email, languages, experience } = req.body;

    const result = await pool.query(
      'UPDATE guides SET name = $1, email = $2, languages = $3, experience = $4 WHERE id = $5 RETURNING *',
      [name, email, languages, experience, req.params.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Not found' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    res.status(500).json({ error: 'Update failed' });
  }
});

// DELETE - Remove guide
app.delete('/guides/:id', async (req, res) => {
  const client = await pool.connect();

  try {
    await client.query('BEGIN');

    // Delete related bookings first
    await client.query('DELETE FROM bookings WHERE guide_id = $1', [req.params.id]);

    // Delete guide
    const result = await client.query(
      'DELETE FROM guides WHERE id = $1 RETURNING id',
      [req.params.id]
    );

    await client.query('COMMIT');

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Not found' });
    }

    res.json({ message: 'Deleted' });
  } catch (error) {
    await client.query('ROLLBACK');
    logger.error(`Delete failed: ${error.message}`);
    res.status(500).json({ error: 'Delete failed' });
  } finally {
    client.release();
  }
});

// BULK CREATE
app.post('/guides/bulk', async (req, res) => {
  try {
    const { guides } = req.body;

    const values = guides.map((g, i) => `($${i * 4 + 1}, $${i * 4 + 2}, $${i * 4 + 3}, $${i * 4 + 4})`).join(',');
    const params = guides.flatMap(g => [g.name, g.email, g.languages, g.experience]);

    const result = await pool.query(
      `INSERT INTO guides (name, email, languages, experience) VALUES ${values} RETURNING *`,
      params
    );

    res.status(201).json(result.rows);
  } catch (error) {
    res.status(500).json({ error: 'Bulk create failed' });
  }
});

// Initialize database
async function init() {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS guides (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        languages VARCHAR(255),
        experience INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    await pool.query(`
      CREATE TABLE IF NOT EXISTS bookings (
        id SERIAL PRIMARY KEY,
        guide_id INTEGER REFERENCES guides(id),
        tour_date DATE,
        guests INTEGER
      )
    `);

    logger.info('Database initialized');
  } catch (error) {
    logger.error(`Init failed: ${error.message}`);
  }
}

const PORT = process.env.PORT || 3000;

init().then(() => {
  app.listen(PORT, () => logger.info(`Server running on port ${PORT}`));
});

module.exports = app;
