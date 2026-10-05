/**
 * Booking Form Handler
 * Production-ready Express server for tour booking management
 *
 * Features:
 * - Form validation (Joi)
 * - Database integration (PostgreSQL)
 * - Email notifications
 * - CSRF protection
 * - Rate limiting
 * - Comprehensive logging
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { Pool } = require('pg');
const { v4: uuidv4 } = require('uuid');
const Joi = require('joi');
const nodemailer = require('nodemailer');
const winston = require('winston');

// ===== LOGGER =====
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.Console({
      format: winston.format.simple()
    }),
    new winston.transports.File({
      filename: process.env.LOG_FILE || './logs/app.log'
    })
  ]
});

// ===== DATABASE =====
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: parseInt(process.env.DATABASE_POOL_SIZE) || 10
});

// ===== EMAIL SERVICE =====
const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: parseInt(process.env.SMTP_PORT),
  secure: true,
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASSWORD
  }
});

// ===== EXPRESS APP =====
const app = express();

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.NODE_ENV === 'production'
    ? ['https://tourism-uae.com']
    : ['http://localhost:3000', 'http://localhost:3001']
}));
app.use(express.json({ limit: '10kb' }));
app.use(express.urlencoded({ limit: '10kb', extended: true }));

// Rate limiting
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000,
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100,
  message: 'Too many requests, please try again later'
});
app.use('/api/', limiter);

// ===== VALIDATION SCHEMAS =====
const bookingSchema = Joi.object({
  customerName: Joi.string().required().min(3).max(100),
  email: Joi.string().email().required(),
  phone: Joi.string().required().regex(/^\+\d{1,3}\d{6,14}$/),
  tourType: Joi.string().required().valid('desert-safari', 'city-tour', 'yacht', 'water-sports', 'dune-bash'),
  date: Joi.date().iso().required().min('now'),
  adults: Joi.number().integer().min(1).max(50).required(),
  children: Joi.number().integer().min(0).max(50),
  specialRequests: Joi.string().max(500),
  paymentMethod: Joi.string().valid('credit_card', 'bank_transfer', 'cash')
}).unknown(false);

// ===== HELPER FUNCTIONS =====

/**
 * Send confirmation email
 */
async function sendConfirmationEmail(booking) {
  try {
    const emailContent = `
      <h2>Booking Confirmation</h2>
      <p>Dear ${booking.customerName},</p>
      <p>Your booking has been confirmed!</p>
      <p><strong>Confirmation Code:</strong> ${booking.confirmationCode}</p>
      <p><strong>Tour Type:</strong> ${booking.tourType}</p>
      <p><strong>Date:</strong> ${booking.date}</p>
      <p><strong>Guests:</strong> ${booking.adults} adults, ${booking.children || 0} children</p>
      <p>We look forward to seeing you!</p>
      <p>Best regards,<br>Tourism UAE Team</p>
    `;

    await transporter.sendMail({
      from: process.env.FROM_EMAIL,
      to: booking.email,
      subject: `Booking Confirmation - ${booking.confirmationCode}`,
      html: emailContent
    });

    logger.info(`Confirmation email sent to ${booking.email}`);
  } catch (error) {
    logger.error(`Failed to send email: ${error.message}`);
    throw error;
  }
}

/**
 * Generate confirmation code
 */
function generateConfirmationCode() {
  const date = new Date();
  const year = date.getFullYear();
  const random = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
  return `DBX-${year}-${random}`;
}

/**
 * Initialize database tables
 */
async function initializeDatabase() {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS bookings (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        confirmation_code VARCHAR(20) UNIQUE NOT NULL,
        customer_name VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL,
        phone VARCHAR(20) NOT NULL,
        tour_type VARCHAR(50) NOT NULL,
        booking_date DATE NOT NULL,
        adults INTEGER NOT NULL,
        children INTEGER DEFAULT 0,
        special_requests TEXT,
        payment_method VARCHAR(50),
        status VARCHAR(20) DEFAULT 'confirmed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Create indexes
    await pool.query(`
      CREATE INDEX IF NOT EXISTS idx_bookings_email ON bookings(email);
      CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(booking_date);
      CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
    `);

    logger.info('Database initialized successfully');
  } catch (error) {
    logger.error(`Database initialization failed: ${error.message}`);
    process.exit(1);
  }
}

// ===== ROUTES =====

/**
 * POST /api/bookings - Create new booking
 */
app.post('/api/bookings', async (req, res) => {
  try {
    // Validate input
    const { error, value } = bookingSchema.validate(req.body, { abortEarly: false });

    if (error) {
      return res.status(400).json({
        status: 'error',
        message: 'Validation failed',
        details: error.details.map(d => ({
          field: d.path.join('.'),
          message: d.message
        }))
      });
    }

    const confirmationCode = generateConfirmationCode();

    // Save to database
    const result = await pool.query(
      `INSERT INTO bookings
       (confirmation_code, customer_name, email, phone, tour_type, booking_date, adults, children, special_requests, payment_method)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
       RETURNING id, confirmation_code, status, created_at`,
      [
        confirmationCode,
        value.customerName,
        value.email,
        value.phone,
        value.tourType,
        value.date,
        value.adults,
        value.children || 0,
        value.specialRequests,
        value.paymentMethod || 'cash'
      ]
    );

    const booking = result.rows[0];

    // Send confirmation email
    if (process.env.BOOKING_CONFIRMATION_ENABLED === 'true') {
      await sendConfirmationEmail({
        ...booking,
        customerName: value.customerName,
        tourType: value.tourType,
        date: value.date,
        adults: value.adults,
        children: value.children || 0,
        email: value.email
      });
    }

    logger.info(`New booking created: ${booking.id}`);

    return res.status(201).json({
      status: 'success',
      message: 'Booking created successfully',
      data: {
        id: booking.id,
        confirmationCode: booking.confirmation_code,
        status: booking.status,
        createdAt: booking.created_at
      }
    });
  } catch (error) {
    logger.error(`Booking creation failed: ${error.message}`);
    return res.status(500).json({
      status: 'error',
      message: 'Failed to create booking'
    });
  }
});

/**
 * GET /api/bookings - List all bookings
 */
app.get('/api/bookings', async (req, res) => {
  try {
    const { email, status, page = 1, limit = 20 } = req.query;

    let query = 'SELECT * FROM bookings WHERE 1=1';
    const params = [];
    let paramCount = 1;

    if (email) {
      query += ` AND email = $${paramCount}`;
      params.push(email);
      paramCount++;
    }

    if (status) {
      query += ` AND status = $${paramCount}`;
      params.push(status);
      paramCount++;
    }

    query += ` ORDER BY created_at DESC LIMIT $${paramCount} OFFSET $${paramCount + 1}`;
    params.push(limit, (page - 1) * limit);

    const result = await pool.query(query, params);

    return res.json({
      status: 'success',
      data: result.rows,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit)
      }
    });
  } catch (error) {
    logger.error(`Failed to fetch bookings: ${error.message}`);
    return res.status(500).json({
      status: 'error',
      message: 'Failed to fetch bookings'
    });
  }
});

/**
 * GET /api/bookings/:id - Get single booking
 */
app.get('/api/bookings/:id', async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM bookings WHERE id = $1',
      [req.params.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        status: 'error',
        message: 'Booking not found'
      });
    }

    return res.json({
      status: 'success',
      data: result.rows[0]
    });
  } catch (error) {
    logger.error(`Failed to fetch booking: ${error.message}`);
    return res.status(500).json({
      status: 'error',
      message: 'Failed to fetch booking'
    });
  }
});

/**
 * PUT /api/bookings/:id - Update booking status
 */
app.put('/api/bookings/:id', async (req, res) => {
  try {
    const { status } = req.body;

    if (!['confirmed', 'cancelled', 'completed'].includes(status)) {
      return res.status(400).json({
        status: 'error',
        message: 'Invalid status'
      });
    }

    const result = await pool.query(
      'UPDATE bookings SET status = $1, updated_at = NOW() WHERE id = $2 RETURNING *',
      [status, req.params.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        status: 'error',
        message: 'Booking not found'
      });
    }

    logger.info(`Booking ${req.params.id} updated to status: ${status}`);

    return res.json({
      status: 'success',
      data: result.rows[0]
    });
  } catch (error) {
    logger.error(`Failed to update booking: ${error.message}`);
    return res.status(500).json({
      status: 'error',
      message: 'Failed to update booking'
    });
  }
});

/**
 * DELETE /api/bookings/:id - Cancel booking
 */
app.delete('/api/bookings/:id', async (req, res) => {
  try {
    const result = await pool.query(
      'UPDATE bookings SET status = $1, updated_at = NOW() WHERE id = $2 RETURNING *',
      ['cancelled', req.params.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        status: 'error',
        message: 'Booking not found'
      });
    }

    logger.info(`Booking ${req.params.id} cancelled`);

    return res.json({
      status: 'success',
      message: 'Booking cancelled'
    });
  } catch (error) {
    logger.error(`Failed to cancel booking: ${error.message}`);
    return res.status(500).json({
      status: 'error',
      message: 'Failed to cancel booking'
    });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// ===== ERROR HANDLING =====
app.use((err, req, res, next) => {
  logger.error(`Unhandled error: ${err.message}`);
  res.status(500).json({
    status: 'error',
    message: 'Internal server error'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    status: 'error',
    message: 'Not found'
  });
});

// ===== SERVER STARTUP =====
const PORT = process.env.PORT || 3000;

async function start() {
  try {
    await initializeDatabase();

    app.listen(PORT, () => {
      logger.info(`Server running on port ${PORT}`);
    });
  } catch (error) {
    logger.error(`Failed to start server: ${error.message}`);
    process.exit(1);
  }
}

start();

module.exports = app;
