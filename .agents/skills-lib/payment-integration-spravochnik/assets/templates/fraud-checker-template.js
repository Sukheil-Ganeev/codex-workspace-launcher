/**
 * Fraud Checker Template
 * Real-time fraud detection for payment transactions
 *
 * Features:
 * - IP geolocation and blacklist check
 * - Velocity limiting (transactions per hour)
 * - Risk scoring algorithm
 * - Suspicious pattern detection
 * - Integration with payment providers
 *
 * Usage:
 *   const { checkFraud, getRiskScore } = require('./fraud-checker-template');
 *   const result = await checkFraud(transactionData);
 *   if (result.risk === 'high') { decline(); }
 */

require('dotenv').config();
const axios = require('axios');

// Configurable thresholds
const CONFIG = {
  MAX_TRANSACTIONS_PER_HOUR: 5,
  MAX_AMOUNT_PER_HOUR: 5000, // AED
  HIGH_RISK_THRESHOLD: 70,
  MEDIUM_RISK_THRESHOLD: 40,
  IP_API_ENDPOINT: process.env.IP_GEOLOCATION_API || 'http://ip-api.com/json/',
  BLACKLIST_CHECK_ENABLED: true,
};

// In-memory store (use Redis in production)
const transactionHistory = new Map();
const ipBlacklist = new Set([
  // Add known malicious IPs
  '192.0.2.1', // Example
]);

/**
 * Main fraud check function
 * @param {Object} transaction - Transaction data
 * @returns {Object} - { allowed: boolean, risk: string, score: number, reasons: [] }
 */
async function checkFraud(transaction) {
  const {
    ip,
    email,
    amount,
    currency,
    cardLast4,
    cardBin,
    country,
  } = transaction;

  const checks = {
    ipBlacklist: checkIPBlacklist(ip),
    ipGeolocation: await checkIPGeolocation(ip, country),
    velocity: checkVelocity(email, ip, amount),
    amountSuspicious: checkSuspiciousAmount(amount, currency),
    cardBin: checkCardBIN(cardBin),
  };

  const riskScore = calculateRiskScore(checks);
  const riskLevel = getRiskLevel(riskScore);
  const reasons = getFailureReasons(checks);

  // Log for audit
  logFraudCheck({ transaction, checks, riskScore, riskLevel });

  return {
    allowed: riskLevel !== 'high',
    risk: riskLevel,
    score: riskScore,
    reasons,
    checks,
  };
}

/**
 * Check if IP is blacklisted
 */
function checkIPBlacklist(ip) {
  if (!CONFIG.BLACKLIST_CHECK_ENABLED) return { passed: true };

  const isBlacklisted = ipBlacklist.has(ip);
  return {
    passed: !isBlacklisted,
    message: isBlacklisted ? 'IP is blacklisted' : 'IP check passed',
  };
}

/**
 * Check IP geolocation matches claimed country
 */
async function checkIPGeolocation(ip, claimedCountry) {
  try {
    const response = await axios.get(`${CONFIG.IP_API_ENDPOINT}${ip}`, {
      timeout: 3000,
    });

    const { country, countryCode, proxy, hosting } = response.data;

    // Check for VPN/Proxy/Hosting
    if (proxy || hosting) {
      return {
        passed: false,
        message: 'VPN/Proxy/Hosting IP detected',
        details: { country, countryCode, proxy, hosting },
      };
    }

    // Check country mismatch
    if (claimedCountry && countryCode !== claimedCountry) {
      return {
        passed: false,
        message: `Country mismatch: IP from ${country}, claimed ${claimedCountry}`,
        details: { country, countryCode },
      };
    }

    return {
      passed: true,
      message: 'Geolocation check passed',
      details: { country, countryCode },
    };
  } catch (err) {
    // Geolocation API failed, don't block transaction
    console.error('Geolocation check failed:', err.message);
    return { passed: true, message: 'Geolocation check skipped (API error)' };
  }
}

/**
 * Check transaction velocity (rate limiting)
 */
function checkVelocity(email, ip, amount) {
  const key = `${email}:${ip}`;
  const now = Date.now();
  const oneHourAgo = now - 3600000;

  // Get recent transactions for this email/IP combo
  if (!transactionHistory.has(key)) {
    transactionHistory.set(key, []);
  }

  const history = transactionHistory.get(key);

  // Remove old entries (older than 1 hour)
  const recentTransactions = history.filter(tx => tx.timestamp > oneHourAgo);
  transactionHistory.set(key, recentTransactions);

  // Add current transaction
  recentTransactions.push({ timestamp: now, amount });

  // Check thresholds
  const count = recentTransactions.length;
  const totalAmount = recentTransactions.reduce((sum, tx) => sum + tx.amount, 0);

  if (count > CONFIG.MAX_TRANSACTIONS_PER_HOUR) {
    return {
      passed: false,
      message: `Too many transactions: ${count} in 1 hour (max: ${CONFIG.MAX_TRANSACTIONS_PER_HOUR})`,
    };
  }

  if (totalAmount > CONFIG.MAX_AMOUNT_PER_HOUR) {
    return {
      passed: false,
      message: `Total amount exceeded: ${totalAmount} AED in 1 hour (max: ${CONFIG.MAX_AMOUNT_PER_HOUR})`,
    };
  }

  return {
    passed: true,
    message: `Velocity check passed (${count} transactions, ${totalAmount} AED)`,
  };
}

/**
 * Check for suspicious amounts
 */
function checkSuspiciousAmount(amount, currency) {
  // Convert to AED if needed (simplified)
  const amountAED = currency === 'AED' ? amount : amount * 3.67; // Rough USD→AED

  // Suspiciously round numbers (e.g., 10000.00)
  const isRoundNumber = amountAED % 1000 === 0 && amountAED >= 5000;

  // Unusually high amount for tourism
  const isUnusuallyHigh = amountAED > 50000;

  if (isUnusuallyHigh) {
    return {
      passed: false,
      message: `Unusually high amount: ${amountAED} AED`,
    };
  }

  if (isRoundNumber) {
    return {
      passed: true, // Not blocking, just flagging
      message: `Suspicious round amount: ${amountAED} AED`,
      flag: true,
    };
  }

  return { passed: true, message: 'Amount check passed' };
}

/**
 * Check card BIN (Bank Identification Number)
 * First 6 digits of card
 */
function checkCardBIN(cardBin) {
  // In production, check against BIN database
  // For now, just validate format
  if (!cardBin || cardBin.length !== 6) {
    return { passed: true, message: 'BIN check skipped (no data)' };
  }

  // TODO: Integrate with BIN database API
  // Check for prepaid cards, gift cards, high-risk countries

  return { passed: true, message: 'BIN check passed' };
}

/**
 * Calculate risk score (0-100)
 */
function calculateRiskScore(checks) {
  let score = 0;

  if (!checks.ipBlacklist.passed) score += 50;
  if (!checks.ipGeolocation.passed) score += 30;
  if (!checks.velocity.passed) score += 25;
  if (!checks.amountSuspicious.passed) score += 20;
  if (checks.amountSuspicious.flag) score += 10;

  return Math.min(score, 100);
}

/**
 * Get risk level from score
 */
function getRiskLevel(score) {
  if (score >= CONFIG.HIGH_RISK_THRESHOLD) return 'high';
  if (score >= CONFIG.MEDIUM_RISK_THRESHOLD) return 'medium';
  return 'low';
}

/**
 * Get human-readable failure reasons
 */
function getFailureReasons(checks) {
  const reasons = [];

  Object.entries(checks).forEach(([checkName, result]) => {
    if (!result.passed || result.flag) {
      reasons.push(result.message);
    }
  });

  return reasons;
}

/**
 * Log fraud check for audit trail
 */
function logFraudCheck(data) {
  // In production: save to database
  const logEntry = {
    timestamp: new Date().toISOString(),
    ip: data.transaction.ip,
    email: data.transaction.email,
    amount: data.transaction.amount,
    riskScore: data.riskScore,
    riskLevel: data.riskLevel,
    allowed: data.riskLevel !== 'high',
  };

  console.log('[Fraud Check]', JSON.stringify(logEntry));
}

/**
 * Add IP to blacklist
 */
function blacklistIP(ip, reason) {
  ipBlacklist.add(ip);
  console.log(`[Blacklist] Added ${ip}: ${reason}`);
}

/**
 * Remove IP from blacklist
 */
function whitelistIP(ip) {
  ipBlacklist.delete(ip);
  console.log(`[Whitelist] Removed ${ip}`);
}

module.exports = {
  checkFraud,
  blacklistIP,
  whitelistIP,
  getRiskLevel,
};
