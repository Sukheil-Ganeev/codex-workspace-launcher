/**
 * Google Sheets API Sync
 * Bidirectional sync between database and Google Sheets
 */

require('dotenv').config();
const express = require('express');
const { google } = require('googleapis');
const { Pool } = require('pg');
const schedule = require('node-schedule');
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: './logs/sync.log' })
  ]
});

const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

const app = express();
app.use(express.json());

let lastSyncTime = null;
let syncStatus = 'idle';

/**
 * Initialize Google Sheets client
 */
function getSheetsClient() {
  const auth = new google.auth.GoogleAuth({
    keyFile: process.env.GOOGLE_SHEETS_KEY,
    scopes: ['https://www.googleapis.com/auth/spreadsheets']
  });

  return google.sheets({ version: 'v4', auth });
}

/**
 * Sync database to Sheets
 */
async function syncDatabaseToSheets() {
  try {
    syncStatus = 'syncing';
    logger.info('Starting database to Sheets sync');

    const sheets = getSheetsClient();

    // Get data from database
    const result = await pool.query('SELECT * FROM tours ORDER BY created_at DESC');
    const tours = result.rows;

    // Prepare data for Sheets (headers + data)
    const values = [
      ['ID', 'Name', 'Price', 'Date', 'Status', 'Updated At'],
      ...tours.map(t => [
        t.id,
        t.name,
        t.price,
        t.date,
        t.status,
        t.updated_at.toISOString()
      ])
    ];

    // Update Sheets
    await sheets.spreadsheets.values.update({
      spreadsheetId: process.env.GOOGLE_SHEETS_ID,
      range: 'Tours!A1',
      valueInputOption: 'RAW',
      requestBody: { values }
    });

    lastSyncTime = new Date();
    syncStatus = 'idle';
    logger.info(`Synced ${tours.length} tours to Sheets`);
  } catch (error) {
    syncStatus = 'error';
    logger.error(`Sync failed: ${error.message}`);
    throw error;
  }
}

/**
 * Sync Sheets to database
 */
async function syncSheetsToDatabase() {
  try {
    syncStatus = 'syncing';
    logger.info('Starting Sheets to database sync');

    const sheets = getSheetsClient();

    // Get data from Sheets
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId: process.env.GOOGLE_SHEETS_ID,
      range: 'Prices!A2:D'
    });

    const rows = response.data.values || [];

    // Update database
    for (const row of rows) {
      await pool.query(
        'UPDATE tours SET price = $1, updated_at = NOW() WHERE id = $2',
        [parseFloat(row[2]), row[0]]
      );
    }

    lastSyncTime = new Date();
    syncStatus = 'idle';
    logger.info(`Synced ${rows.length} rows from Sheets to database`);
  } catch (error) {
    syncStatus = 'error';
    logger.error(`Sync failed: ${error.message}`);
    throw error;
  }
}

/**
 * POST /sync/trigger
 */
app.post('/sync/trigger', async (req, res) => {
  try {
    const { direction = 'both' } = req.body;

    if (direction === 'db-to-sheets' || direction === 'both') {
      await syncDatabaseToSheets();
    }

    if (direction === 'sheets-to-db' || direction === 'both') {
      await syncSheetsToDatabase();
    }

    res.json({ status: 'success', lastSync: lastSyncTime });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

/**
 * GET /sync/status
 */
app.get('/sync/status', (req, res) => {
  res.json({
    status: syncStatus,
    lastSyncTime,
    nextSyncIn: '5 minutes'
  });
});

/**
 * GET /sync/logs
 */
app.get('/sync/logs', async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM sync_logs ORDER BY created_at DESC LIMIT 20'
    );
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * Initialize database
 */
async function initializeDatabase() {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS tours (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        price DECIMAL(10, 2),
        date DATE,
        status VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    await pool.query(`
      CREATE TABLE IF NOT EXISTS sync_logs (
        id SERIAL PRIMARY KEY,
        sync_type VARCHAR(50),
        status VARCHAR(20),
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    logger.info('Database initialized');
  } catch (error) {
    logger.error(`Database init failed: ${error.message}`);
  }
}

/**
 * Schedule periodic sync
 */
function scheduleSyncJob() {
  const interval = parseInt(process.env.SYNC_INTERVAL) || 5 * 60 * 1000;

  setInterval(async () => {
    try {
      await syncDatabaseToSheets();
    } catch (error) {
      logger.error(`Scheduled sync failed: ${error.message}`);
    }
  }, interval);

  logger.info(`Sync scheduled every ${interval / 1000} seconds`);
}

const PORT = process.env.PORT || 3000;

async function start() {
  await initializeDatabase();
  scheduleSyncJob();

  app.listen(PORT, () => {
    logger.info(`Sync server running on port ${PORT}`);
  });
}

start();

module.exports = app;
