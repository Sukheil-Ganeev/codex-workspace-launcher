-- Fraud Detection Database Schema

-- Transactions table
CREATE TABLE transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  payment_intent_id VARCHAR(255),
  amount INTEGER NOT NULL,
  currency VARCHAR(3) NOT NULL,
  email VARCHAR(255) NOT NULL,
  ip_address VARCHAR(45) NOT NULL,
  card_fingerprint VARCHAR(255),
  risk_score INTEGER DEFAULT 0,
  risk_reasons TEXT[],
  action_taken VARCHAR(50),
  status VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  failed_at TIMESTAMP
);

-- Blacklisted IPs
CREATE TABLE blacklisted_ips (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ip_address VARCHAR(45) UNIQUE NOT NULL,
  reason TEXT,
  added_at TIMESTAMP DEFAULT NOW()
);

-- Blacklisted Emails
CREATE TABLE blacklisted_emails (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  reason TEXT,
  added_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_transactions_email ON transactions(email);
CREATE INDEX idx_transactions_ip ON transactions(ip_address);
CREATE INDEX idx_transactions_card_fingerprint ON transactions(card_fingerprint);
CREATE INDEX idx_transactions_created_at ON transactions(created_at DESC);
CREATE INDEX idx_transactions_risk_score ON transactions(risk_score DESC);
