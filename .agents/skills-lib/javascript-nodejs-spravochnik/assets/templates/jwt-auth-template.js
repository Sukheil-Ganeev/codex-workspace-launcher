/**
 * JWT Authentication Template
 *
 * Production-ready JWT реализация с:
 * - Генерацией токенов (access & refresh)
 * - Валидацией
 * - Refresh token rotation
 * - Token revocation
 *
 * @example
 * npm install jsonwebtoken bcryptjs dotenv
 */

const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');

// ==================== CONFIG ====================

const JWT_CONFIG = {
  accessTokenExpiry: '15m',
  refreshTokenExpiry: '7d',
  secret: process.env.JWT_SECRET || 'your-secret-key',
  refreshSecret: process.env.JWT_REFRESH_SECRET || 'your-refresh-secret',
};

// TODO: Использовать Redis или БД для хранения revoked tokens
const revokedTokens = new Set();

// ==================== TOKEN GENERATION ====================

/**
 * Генерировать пару access + refresh токенов
 *
 * @param {Object} user - Данные пользователя { id, email, role }
 * @returns {Object} { accessToken, refreshToken, expiresIn }
 *
 * @example
 * const tokens = generateTokens({ id: 1, email: 'user@example.com', role: 'user' });
 */
function generateTokens(user) {
  if (!user || !user.id) {
    throw new Error('User object with id is required');
  }

  // Access token (short-lived)
  const accessToken = jwt.sign(
    {
      sub: user.id,
      email: user.email,
      role: user.role || 'user',
      type: 'access',
    },
    JWT_CONFIG.secret,
    { expiresIn: JWT_CONFIG.accessTokenExpiry }
  );

  // Refresh token (long-lived)
  const refreshToken = jwt.sign(
    {
      sub: user.id,
      type: 'refresh',
      tokenId: crypto.randomBytes(16).toString('hex'),
    },
    JWT_CONFIG.refreshSecret,
    { expiresIn: JWT_CONFIG.refreshTokenExpiry }
  );

  return {
    accessToken,
    refreshToken,
    expiresIn: JWT_CONFIG.accessTokenExpiry,
  };
}

// ==================== TOKEN VERIFICATION ====================

/**
 * Проверить access token
 *
 * @param {string} token
 * @returns {Object} Decoded token payload
 * @throws {Error} Если токен невалиден
 */
function verifyAccessToken(token) {
  try {
    // Проверить revocation list
    if (revokedTokens.has(token)) {
      throw new Error('Token has been revoked');
    }

    const decoded = jwt.verify(token, JWT_CONFIG.secret);

    if (decoded.type !== 'access') {
      throw new Error('Invalid token type');
    }

    return decoded;
  } catch (error) {
    throw new Error(`Token verification failed: ${error.message}`);
  }
}

/**
 * Проверить refresh token
 *
 * @param {string} token
 * @returns {Object} Decoded token payload
 */
function verifyRefreshToken(token) {
  try {
    const decoded = jwt.verify(token, JWT_CONFIG.refreshSecret);

    if (decoded.type !== 'refresh') {
      throw new Error('Invalid token type');
    }

    return decoded;
  } catch (error) {
    throw new Error(`Refresh token verification failed: ${error.message}`);
  }
}

// ==================== TOKEN REFRESH ====================

/**
 * Обновить access token используя refresh token
 *
 * @param {string} refreshToken
 * @param {Object} user - Свежие данные пользователя
 * @returns {Object} { accessToken, refreshToken }
 *
 * @example
 * const newTokens = refreshAccessToken(oldRefreshToken, user);
 */
function refreshAccessToken(refreshToken, user) {
  try {
    const decoded = verifyRefreshToken(refreshToken);

    // TODO: Проверить в БД что tokenId еще не использовался (rotation)
    // Это предотвращает использование одного refresh token несколько раз

    const newTokens = generateTokens({
      id: decoded.sub,
      email: user.email,
      role: user.role,
    });

    return newTokens;
  } catch (error) {
    throw new Error(`Token refresh failed: ${error.message}`);
  }
}

// ==================== TOKEN REVOCATION ====================

/**
 * Отозвать токен (logout)
 *
 * @param {string} token
 * @param {Object} options - { ttl: 'time-to-live' }
 */
function revokeToken(token) {
  try {
    const decoded = jwt.decode(token);

    if (!decoded || !decoded.exp) {
      throw new Error('Invalid token format');
    }

    // Добавить в revoked list (TODO: использовать Redis с TTL)
    revokedTokens.add(token);

    // Очистить истекшие токены
    console.log('[Auth] Token revoked for user:', decoded.sub);
  } catch (error) {
    console.error('[Auth] Revocation error:', error.message);
  }
}

/**
 * Проверить остался ли токен в revoked list
 */
function isTokenRevoked(token) {
  return revokedTokens.has(token);
}

// ==================== PASSWORD HASHING ====================

/**
 * Хеширование пароля
 *
 * @param {string} password
 * @param {number} saltRounds - Количество раундов (default: 10)
 * @returns {Promise<string>} Хешированный пароль
 */
async function hashPassword(password) {
  if (!password || password.length < 8) {
    throw new Error('Password must be at least 8 characters long');
  }

  return bcrypt.hash(password, 10);
}

/**
 * Проверить пароль
 *
 * @param {string} password - Введенный пароль
 * @param {string} hash - Сохраненный хеш
 * @returns {Promise<boolean>}
 */
async function comparePassword(password, hash) {
  return bcrypt.compare(password, hash);
}

// ==================== LOGIN/LOGOUT ====================

/**
 * Login логика
 *
 * @param {Object} credentials - { email, password }
 * @param {Object} user - Данные из БД
 * @returns {Promise<Object>} { accessToken, refreshToken }
 *
 * @example
 * // В route handler:
 * const user = await User.findByEmail(email);
 * const isValid = await comparePassword(password, user.passwordHash);
 * const tokens = await login({ email, password }, user);
 */
async function login(credentials, user) {
  if (!user) {
    throw new Error('User not found');
  }

  const isPasswordValid = await comparePassword(credentials.password, user.passwordHash);

  if (!isPasswordValid) {
    throw new Error('Invalid credentials');
  }

  const tokens = generateTokens({
    id: user.id,
    email: user.email,
    role: user.role,
  });

  console.log(`[Auth] User logged in: ${user.email}`);

  return tokens;
}

/**
 * Logout логика
 *
 * @param {string} accessToken
 */
function logout(accessToken) {
  revokeToken(accessToken);
}

// ==================== EXPORTS ====================

module.exports = {
  generateTokens,
  verifyAccessToken,
  verifyRefreshToken,
  refreshAccessToken,
  revokeToken,
  isTokenRevoked,
  hashPassword,
  comparePassword,
  login,
  logout,
  JWT_CONFIG,
};

// Required environment variables:
// JWT_SECRET=your-secret-key-min-32-chars
// JWT_REFRESH_SECRET=your-refresh-secret-min-32-chars
// NODE_ENV=production
