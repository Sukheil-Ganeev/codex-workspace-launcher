#!/usr/bin/env node

/**
 * Fraud Detection System - Real-time Risk Scoring
 *
 * Features:
 * - IP geolocation checks
 * - Velocity limits (same card/IP/email)
 * - Risk scoring (0-100)
 * - Blacklist management
 * - Suspicious pattern detection
 * - Automatic payment blocking for high-risk transactions
 *
 * Usage: node server.js
 */

require('dotenv').config();
const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const axios = require('axios');
const { createClient } = require('@supabase/supabase-js');

const app = express();
app.use(express.json());
app.use(express.static('public'));

// Database setup (using Supabase for demo)
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
);

// Risk scoring thresholds
const RISK_THRESHOLDS = {
  LOW: 20,
  MEDIUM: 50,
  HIGH: 75,
  BLOCK: 90,
};

// Velocity limits (per hour)
const VELOCITY_LIMITS = {
  SAME_CARD: 3,
  SAME_IP: 5,
  SAME_EMAIL: 4,
};

/**
 * Get IP geolocation data
 */
async function getIPGeolocation(ip) {
  try {
    const response = await axios.get(`http://ip-api.com/json/${ip}`, {
      timeout: 3000,
    });
    return response.data;
  } catch (error) {
    console.error('IP lookup failed:', error.message);
    return null;
  }
}

/**
 * Check if IP is in blacklist
 */
async function isIPBlacklisted(ip) {
  const { data } = await supabase
    .from('blacklisted_ips')
    .select('*')
    .eq('ip_address', ip)
    .single();

  return !!data;
}

/**
 * Check email blacklist
 */
async function isEmailBlacklisted(email) {
  const { data } = await supabase
    .from('blacklisted_emails')
    .select('*')
    .eq('email', email.toLowerCase())
    .single();

  return !!data;
}

/**
 * Check velocity limits (transactions in last hour)
 */
async function checkVelocityLimits(cardFingerprint, ip, email) {
  const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000).toISOString();

  // Check same card
  const { data: cardTxs } = await supabase
    .from('transactions')
    .select('*')
    .eq('card_fingerprint', cardFingerprint)
    .gte('created_at', oneHourAgo);

  if (cardTxs && cardTxs.length >= VELOCITY_LIMITS.SAME_CARD) {
    return { exceeded: true, type: 'SAME_CARD', count: cardTxs.length };
  }

  // Check same IP
  const { data: ipTxs } = await supabase
    .from('transactions')
    .select('*')
    .eq('ip_address', ip)
    .gte('created_at', oneHourAgo);

  if (ipTxs && ipTxs.length >= VELOCITY_LIMITS.SAME_IP) {
    return { exceeded: true, type: 'SAME_IP', count: ipTxs.length };
  }

  // Check same email
  const { data: emailTxs } = await supabase
    .from('transactions')
    .select('*')
    .eq('email', email.toLowerCase())
    .gte('created_at', oneHourAgo);

  if (emailTxs && emailTxs.length >= VELOCITY_LIMITS.SAME_EMAIL) {
    return { exceeded: true, type: 'SAME_EMAIL', count: emailTxs.length };
  }

  return { exceeded: false };
}

/**
 * Check for suspicious patterns
 */
function detectSuspiciousPatterns(data) {
  const flags = [];

  // Round amounts (often used by fraudsters)
  if (data.amount % 10000 === 0) { // e.g., 100.00, 200.00 AED
    flags.push('ROUND_AMOUNT');
  }

  // Disposable email providers
  const disposableDomains = ['tempmail.com', 'guerrillamail.com', 'mailinator.com'];
  const emailDomain = data.email.split('@')[1];
  if (disposableDomains.includes(emailDomain)) {
    flags.push('DISPOSABLE_EMAIL');
  }

  // VPN/Proxy detection (simplified)
  if (data.geoData && data.geoData.proxy) {
    flags.push('VPN_PROXY');
  }

  // Mismatched billing country and IP country
  if (data.billingCountry && data.geoData &&
      data.billingCountry !== data.geoData.countryCode) {
    flags.push('COUNTRY_MISMATCH');
  }

  // High amount for first transaction
  if (data.amount > 100000 && data.isFirstTransaction) { // > 1000 AED
    flags.push('HIGH_FIRST_AMOUNT');
  }

  return flags;
}

/**
 * Calculate risk score (0-100)
 */
async function calculateRiskScore(paymentData) {
  let score = 0;
  const reasons = [];

  // IP blacklist check (+50)
  if (await isIPBlacklisted(paymentData.ip)) {
    score += 50;
    reasons.push('IP blacklisted');
  }

  // Email blacklist check (+50)
  if (await isEmailBlacklisted(paymentData.email)) {
    score += 50;
    reasons.push('Email blacklisted');
  }

  // Velocity limits (+30)
  const velocityCheck = await checkVelocityLimits(
    paymentData.cardFingerprint,
    paymentData.ip,
    paymentData.email
  );

  if (velocityCheck.exceeded) {
    score += 30;
    reasons.push(`Velocity limit exceeded: ${velocityCheck.type} (${velocityCheck.count} txs)`);
  }

  // Geolocation risk
  if (paymentData.geoData) {
    // High-risk countries (simplified list)
    const highRiskCountries = ['NG', 'GH', 'ID', 'VN'];
    if (highRiskCountries.includes(paymentData.geoData.countryCode)) {
      score += 20;
      reasons.push('High-risk country');
    }
  }

  // Suspicious patterns
  const patterns = detectSuspiciousPatterns(paymentData);
  patterns.forEach(pattern => {
    switch (pattern) {
      case 'DISPOSABLE_EMAIL':
        score += 15;
        reasons.push('Disposable email provider');
        break;
      case 'VPN_PROXY':
        score += 10;
        reasons.push('VPN/Proxy detected');
        break;
      case 'COUNTRY_MISMATCH':
        score += 20;
        reasons.push('Billing country mismatch');
        break;
      case 'HIGH_FIRST_AMOUNT':
        score += 25;
        reasons.push('Unusually high first transaction');
        break;
      case 'ROUND_AMOUNT':
        score += 5;
        reasons.push('Round amount (common fraud pattern)');
        break;
    }
  });

  // Cap at 100
  score = Math.min(score, 100);

  return { score, reasons };
}

/**
 * Determine action based on risk score
 */
function getRiskAction(score) {
  if (score >= RISK_THRESHOLDS.BLOCK) {
    return 'BLOCK';
  } else if (score >= RISK_THRESHOLDS.HIGH) {
    return 'MANUAL_REVIEW';
  } else if (score >= RISK_THRESHOLDS.MEDIUM) {
    return 'REQUIRE_3DS';
  } else if (score >= RISK_THRESHOLDS.LOW) {
    return 'ALLOW_WITH_MONITORING';
  } else {
    return 'ALLOW';
  }
}

/**
 * Log transaction for analytics
 */
async function logTransaction(txData) {
  await supabase.from('transactions').insert({
    payment_intent_id: txData.paymentIntentId,
    amount: txData.amount,
    currency: txData.currency,
    email: txData.email.toLowerCase(),
    ip_address: txData.ip,
    card_fingerprint: txData.cardFingerprint,
    risk_score: txData.riskScore,
    risk_reasons: txData.riskReasons,
    action_taken: txData.action,
    status: txData.status,
    created_at: new Date().toISOString(),
  });
}

/**
 * Create payment with fraud detection
 */
app.post('/create-payment', async (req, res) => {
  try {
    const { amount, currency, email, cardToken, billingCountry } = req.body;
    const ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;

    console.log(`\n🔍 Fraud check initiated for ${email} from ${ip}`);

    // Get IP geolocation
    const geoData = await getIPGeolocation(ip);

    // Create temporary payment method to get card fingerprint
    const paymentMethod = await stripe.paymentMethods.create({
      type: 'card',
      card: { token: cardToken },
    });

    const cardFingerprint = paymentMethod.card.fingerprint;

    // Prepare payment data for risk analysis
    const paymentData = {
      amount,
      currency,
      email,
      ip,
      cardFingerprint,
      billingCountry,
      geoData,
      isFirstTransaction: true, // TODO: Check database
    };

    // Calculate risk score
    const { score, reasons } = await calculateRiskScore(paymentData);
    const action = getRiskAction(score);

    console.log(`📊 Risk Score: ${score}/100`);
    console.log(`⚠️  Risk Reasons:`, reasons);
    console.log(`🎯 Action: ${action}`);

    // Handle based on action
    if (action === 'BLOCK') {
      // Block payment entirely
      await logTransaction({
        paymentIntentId: null,
        amount,
        currency,
        email,
        ip,
        cardFingerprint,
        riskScore: score,
        riskReasons: reasons,
        action,
        status: 'blocked',
      });

      return res.status(403).json({
        error: 'PAYMENT_BLOCKED',
        message: 'This transaction has been blocked due to high fraud risk.',
        riskScore: score,
      });
    }

    // Create Payment Intent with appropriate settings
    const paymentIntentParams = {
      amount,
      currency,
      payment_method: paymentMethod.id,
      metadata: {
        email,
        risk_score: score,
        risk_action: action,
        ip_address: ip,
      },
    };

    // Require 3D Secure for medium/high risk
    if (action === 'REQUIRE_3DS' || action === 'MANUAL_REVIEW') {
      paymentIntentParams.payment_method_options = {
        card: {
          request_three_d_secure: 'any',
        },
      };
    }

    // Manual review for high risk
    if (action === 'MANUAL_REVIEW') {
      paymentIntentParams.capture_method = 'manual'; // Don't auto-capture
    }

    const paymentIntent = await stripe.paymentIntents.create(paymentIntentParams);

    // Log transaction
    await logTransaction({
      paymentIntentId: paymentIntent.id,
      amount,
      currency,
      email,
      ip,
      cardFingerprint,
      riskScore: score,
      riskReasons: reasons,
      action,
      status: 'created',
    });

    res.json({
      clientSecret: paymentIntent.client_secret,
      riskScore: score,
      action,
      requires3DS: action === 'REQUIRE_3DS' || action === 'MANUAL_REVIEW',
      requiresReview: action === 'MANUAL_REVIEW',
    });

  } catch (error) {
    console.error('Payment creation failed:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Webhook handler - update transaction status
 */
app.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  const sig = req.headers['stripe-signature'];

  try {
    const event = stripe.webhooks.constructEvent(
      req.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );

    if (event.type === 'payment_intent.succeeded') {
      const paymentIntent = event.data.object;

      // Update transaction status
      await supabase
        .from('transactions')
        .update({ status: 'succeeded', completed_at: new Date().toISOString() })
        .eq('payment_intent_id', paymentIntent.id);

      console.log(`✅ Payment succeeded: ${paymentIntent.id}`);
    }

    if (event.type === 'payment_intent.payment_failed') {
      const paymentIntent = event.data.object;

      await supabase
        .from('transactions')
        .update({ status: 'failed', failed_at: new Date().toISOString() })
        .eq('payment_intent_id', paymentIntent.id);

      console.log(`❌ Payment failed: ${paymentIntent.id}`);
    }

    res.json({ received: true });
  } catch (err) {
    console.error('Webhook error:', err.message);
    res.status(400).send(`Webhook Error: ${err.message}`);
  }
});

/**
 * Admin: Add IP to blacklist
 */
app.post('/admin/blacklist-ip', async (req, res) => {
  const { ip, reason } = req.body;

  await supabase.from('blacklisted_ips').insert({
    ip_address: ip,
    reason,
    added_at: new Date().toISOString(),
  });

  res.json({ success: true });
});

/**
 * Admin: View high-risk transactions
 */
app.get('/admin/high-risk-transactions', async (req, res) => {
  const { data } = await supabase
    .from('transactions')
    .select('*')
    .gte('risk_score', RISK_THRESHOLDS.HIGH)
    .order('created_at', { ascending: false })
    .limit(50);

  res.json(data);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🛡️  Fraud Detection Server running on port ${PORT}`);
  console.log(`📊 Risk Thresholds: LOW=${RISK_THRESHOLDS.LOW}, MEDIUM=${RISK_THRESHOLDS.MEDIUM}, HIGH=${RISK_THRESHOLDS.HIGH}, BLOCK=${RISK_THRESHOLDS.BLOCK}`);
});
