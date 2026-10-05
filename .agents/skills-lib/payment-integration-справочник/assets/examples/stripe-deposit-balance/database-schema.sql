/**
 * Database Schema for Stripe Deposit + Balance Payment System
 * PostgreSQL
 */

-- Create bookings table
CREATE TABLE IF NOT EXISTS bookings (
  id SERIAL PRIMARY KEY,
  booking_reference VARCHAR(20) UNIQUE NOT NULL DEFAULT 'BOOK-' || LPAD(nextval('bookings_id_seq')::TEXT, 6, '0'),

  -- Customer information
  customer_name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  phone VARCHAR(50),

  -- Tour details
  tour_name VARCHAR(255) NOT NULL,
  tour_date DATE,

  -- Payment amounts (in AED)
  total_amount DECIMAL(10, 2) NOT NULL,
  deposit_amount DECIMAL(10, 2) NOT NULL,
  balance_amount DECIMAL(10, 2) NOT NULL,

  -- Payment tracking
  deposit_payment_intent_id VARCHAR(255),
  balance_payment_intent_id VARCHAR(255),

  -- Status: pending, deposit_paid, fully_paid, payment_failed, cancelled
  status VARCHAR(50) DEFAULT 'pending',

  -- Timestamps
  deposit_paid_at TIMESTAMP,
  balance_paid_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  -- Indexes
  INDEX idx_booking_reference (booking_reference),
  INDEX idx_email (email),
  INDEX idx_status (status),
  INDEX idx_created_at (created_at)
);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_bookings_updated_at
  BEFORE UPDATE ON bookings
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Sample data for testing
INSERT INTO bookings (customer_name, email, phone, tour_name, total_amount, deposit_amount, balance_amount)
VALUES
  ('John Doe', 'john@example.com', '+971501234567', 'Desert Safari Tour', 1000.00, 300.00, 700.00),
  ('Jane Smith', 'jane@example.com', '+971509876543', 'Dubai City Tour', 500.00, 150.00, 350.00);
