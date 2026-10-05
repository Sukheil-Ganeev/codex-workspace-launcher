-- Offline/Cash Hybrid Payment Schema

-- Bookings table
CREATE TABLE bookings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  booking_code VARCHAR(50) UNIQUE NOT NULL,
  customer_name VARCHAR(255) NOT NULL,
  customer_email VARCHAR(255) NOT NULL,
  customer_phone VARCHAR(50),
  tour_name VARCHAR(255) NOT NULL,
  tour_date DATE NOT NULL,
  total_amount INTEGER NOT NULL,
  deposit_amount INTEGER NOT NULL,
  balance_amount INTEGER NOT NULL,
  currency VARCHAR(3) NOT NULL,
  payment_intent_id VARCHAR(255),
  deposit_status VARCHAR(20) DEFAULT 'pending',
  balance_status VARCHAR(20) DEFAULT 'pending',
  payment_complete BOOLEAN DEFAULT FALSE,
  qr_code TEXT,
  deposit_paid_at TIMESTAMP WITH TIME ZONE,
  balance_paid_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cash payments table
CREATE TABLE cash_payments (
  id SERIAL PRIMARY KEY,
  booking_code VARCHAR(50) REFERENCES bookings(booking_code),
  amount_received INTEGER NOT NULL,
  currency VARCHAR(3) NOT NULL,
  payment_method VARCHAR(50) NOT NULL,
  staff_name VARCHAR(255),
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_bookings_code ON bookings(booking_code);
CREATE INDEX idx_bookings_email ON bookings(customer_email);
CREATE INDEX idx_bookings_date ON bookings(tour_date);
CREATE INDEX idx_cash_payments_booking ON cash_payments(booking_code);
