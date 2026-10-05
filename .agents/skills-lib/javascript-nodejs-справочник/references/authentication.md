# Authentication & Authorization

Полный справочник по аутентификации и авторизации в JavaScript/Node.js приложениях.

---

## 1. JWT Basics

JWT (JSON Web Token) — стандартный способ передачи информации в виде подписанного JSON объекта.

### Структура JWT

```
header.payload.signature
```

### Установка зависимостей

```bash
npm install jsonwebtoken
```

### Создание токена

```javascript
const jwt = require('jsonwebtoken');

const SECRET = process.env.JWT_SECRET || 'your-secret-key';

// Создание токена
function generateToken(payload, expiresIn = '1h') {
  return jwt.sign(payload, SECRET, { expiresIn });
}

// Пример использования
const token = generateToken({ userId: 123, email: 'user@example.com' });
console.log(token);
// eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Проверка и декодирование токена

```javascript
function verifyToken(token) {
  try {
    const decoded = jwt.verify(token, SECRET);
    return decoded;
  } catch (error) {
    return null; // Токен невалидный или истекший
  }
}

// Пример
const payload = verifyToken(token);
if (payload) {
  console.log('Токен валидный:', payload);
} else {
  console.log('Токен невалидный');
}
```

### Декодирование без проверки (только для отладки!)

```javascript
const decoded = jwt.decode(token);
console.log('Payload:', decoded);
```

---

## 2. Password Hashing (bcrypt)

Хеширование паролей с использованием bcrypt — защита от взлома базы данных.

### Установка

```bash
npm install bcrypt
```

### Хеширование пароля

```javascript
const bcrypt = require('bcrypt');

async function hashPassword(password) {
  const saltRounds = 10; // Количество раундов (10-12 рекомендуется)
  return await bcrypt.hash(password, saltRounds);
}

// Пример
const hashedPassword = await hashPassword('user_password_123');
console.log(hashedPassword);
// $2b$10$N9qo8uLO...
```

### Проверка пароля

```javascript
async function verifyPassword(password, hashedPassword) {
  return await bcrypt.compare(password, hashedPassword);
}

// Пример
const isMatch = await verifyPassword('user_password_123', hashedPassword);
console.log('Пароль верный:', isMatch); // true
```

### Полная система хеширования

```javascript
class PasswordManager {
  static async hash(password) {
    if (password.length < 8) {
      throw new Error('Пароль должен быть минимум 8 символов');
    }
    return await bcrypt.hash(password, 10);
  }

  static async verify(password, hash) {
    return await bcrypt.compare(password, hash);
  }

  static isStrong(password) {
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return regex.test(password);
  }
}

// Использование
const hash = await PasswordManager.hash('SecurePass123!');
const isValid = await PasswordManager.verify('SecurePass123!', hash);
const isStrong = PasswordManager.isStrong('SecurePass123!');
```

---

## 3. Login/Register Flow

Полная система регистрации и входа с JWT токенами.

### Структура базы данных (MongoDB пример)

```javascript
const userSchema = {
  _id: ObjectId,
  email: String, // Уникальный
  password: String, // Хешированный
  username: String,
  createdAt: Date,
  updatedAt: Date
};
```

### Регистрация

```javascript
const express = require('express');
const app = express();
app.use(express.json());

// Модель пользователя (Mongoose)
const User = require('./models/User');

app.post('/api/auth/register', async (req, res) => {
  try {
    const { email, password, username } = req.body;

    // Валидация
    if (!email || !password || password.length < 8) {
      return res.status(400).json({ error: 'Некорректные данные' });
    }

    // Проверка существования
    const existing = await User.findOne({ email });
    if (existing) {
      return res.status(409).json({ error: 'Email уже зарегистрирован' });
    }

    // Хеширование пароля
    const hashedPassword = await bcrypt.hash(password, 10);

    // Создание пользователя
    const user = new User({
      email,
      password: hashedPassword,
      username: username || email.split('@')[0]
    });

    await user.save();

    res.status(201).json({
      message: 'Пользователь успешно зарегистрирован',
      userId: user._id
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

### Вход

```javascript
app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    // Поиск пользователя
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(401).json({ error: 'Email или пароль неверный' });
    }

    // Проверка пароля
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(401).json({ error: 'Email или пароль неверный' });
    }

    // Создание токенов
    const accessToken = jwt.sign(
      { userId: user._id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );

    const refreshToken = jwt.sign(
      { userId: user._id },
      process.env.REFRESH_TOKEN_SECRET,
      { expiresIn: '7d' }
    );

    // Сохранение refresh token в БД или cookie
    user.refreshToken = refreshToken;
    await user.save();

    res.json({
      accessToken,
      refreshToken,
      user: {
        id: user._id,
        email: user.email,
        username: user.username
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

---

## 4. Middleware Protection

Защита маршрутов с проверкой JWT токена.

### Базовое middleware

```javascript
function authMiddleware(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1]; // Bearer токен

  if (!token) {
    return res.status(401).json({ error: 'Токен отсутствует' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    res.status(403).json({ error: 'Неверный или истекший токен' });
  }
}

// Использование
app.get('/api/profile', authMiddleware, (req, res) => {
  res.json({
    message: 'Защищённый маршрут',
    userId: req.user.userId
  });
});
```

### Продвинутое middleware с логированием

```javascript
class AuthMiddleware {
  static authenticate(req, res, next) {
    const token = req.headers.authorization?.split(' ')[1];

    if (!token) {
      return res.status(401).json({
        error: 'Токен отсутствует',
        code: 'NO_TOKEN'
      });
    }

    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      req.user = decoded;
      req.token = token;

      // Логирование
      console.log(`[AUTH] User ${decoded.userId} authenticated`);

      next();
    } catch (error) {
      if (error.name === 'TokenExpiredError') {
        return res.status(401).json({
          error: 'Токен истек',
          code: 'TOKEN_EXPIRED',
          expiredAt: error.expiredAt
        });
      }

      res.status(403).json({
        error: 'Неверный токен',
        code: 'INVALID_TOKEN'
      });
    }
  }

  static optional(req, res, next) {
    const token = req.headers.authorization?.split(' ')[1];

    if (token) {
      try {
        req.user = jwt.verify(token, process.env.JWT_SECRET);
      } catch (error) {
        // Игнорируем ошибку, переходим дальше
      }
    }

    next();
  }
}

app.use('/api/protected', AuthMiddleware.authenticate);
app.use('/api/public', AuthMiddleware.optional);
```

---

## 5. Refresh Tokens

Система обновления токенов для долгосрочных сессий.

### Структура с refresh tokens

```javascript
// Короткоживущий accessToken (1 час)
const accessToken = jwt.sign(
  { userId, email },
  process.env.JWT_SECRET,
  { expiresIn: '1h' }
);

// Долгоживущий refreshToken (7 дней)
const refreshToken = jwt.sign(
  { userId, tokenVersion: 1 },
  process.env.REFRESH_TOKEN_SECRET,
  { expiresIn: '7d' }
);
```

### Endpoint для обновления токена

```javascript
app.post('/api/auth/refresh', async (req, res) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(401).json({ error: 'Refresh token отсутствует' });
    }

    // Проверка refresh токена
    const decoded = jwt.verify(refreshToken, process.env.REFRESH_TOKEN_SECRET);

    // Проверка версии токена (защита от взлома)
    const user = await User.findById(decoded.userId);
    if (!user || user.tokenVersion !== decoded.tokenVersion) {
      return res.status(401).json({ error: 'Refresh token невалидный' });
    }

    // Создание нового accessToken
    const newAccessToken = jwt.sign(
      { userId: user._id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );

    res.json({ accessToken: newAccessToken });
  } catch (error) {
    res.status(403).json({ error: 'Refresh token истек или невалидный' });
  }
});
```

### Клиентская логика

```javascript
// Axios Interceptor
axiosInstance.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const { data } = await axios.post('/api/auth/refresh', {
          refreshToken: localStorage.getItem('refreshToken')
        });

        localStorage.setItem('accessToken', data.accessToken);
        axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${data.accessToken}`;

        return axiosInstance(originalRequest);
      } catch (refreshError) {
        // Выход и редирект на login
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```

---

## 6. OAuth 2.0

Аутентификация через внешние сервисы (Google, GitHub).

### Установка

```bash
npm install passport passport-google-oauth20 passport-github2 express-session
```

### Google OAuth конфигурация

```javascript
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;

passport.use(new GoogleStrategy({
  clientID: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  callbackURL: 'http://localhost:3000/api/auth/google/callback'
}, async (accessToken, refreshToken, profile, done) => {
  try {
    // Поиск или создание пользователя
    let user = await User.findOne({ googleId: profile.id });

    if (!user) {
      user = new User({
        googleId: profile.id,
        email: profile.emails[0].value,
        username: profile.displayName,
        avatar: profile.photos[0]?.value
      });
      await user.save();
    }

    return done(null, user);
  } catch (error) {
    return done(error, null);
  }
}));

passport.serializeUser((user, done) => {
  done(null, user.id);
});

passport.deserializeUser(async (id, done) => {
  const user = await User.findById(id);
  done(null, user);
});
```

### Маршруты OAuth

```javascript
// Инициация Google login
app.get('/api/auth/google',
  passport.authenticate('google', { scope: ['profile', 'email'] })
);

// Callback после аутентификации
app.get('/api/auth/google/callback',
  passport.authenticate('google', { failureRedirect: '/login' }),
  (req, res) => {
    const accessToken = jwt.sign(
      { userId: req.user._id },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );

    res.redirect(`http://localhost:3000?token=${accessToken}`);
  }
);
```

---

## 7. Role-Based Access Control (RBAC)

Система управления доступом на основе ролей.

### Модель с ролями

```javascript
const userSchema = {
  _id: ObjectId,
  email: String,
  password: String,
  roles: ['user', 'admin', 'moderator'], // Массив ролей
  permissions: ['read:posts', 'write:posts'], // Гранулярные разрешения
  createdAt: Date
};

const ROLES = {
  ADMIN: 'admin',
  MODERATOR: 'moderator',
  USER: 'user'
};

const PERMISSIONS = {
  READ_POSTS: 'read:posts',
  WRITE_POSTS: 'write:posts',
  DELETE_POSTS: 'delete:posts',
  MANAGE_USERS: 'manage:users'
};
```

### Middleware для проверки ролей

```javascript
function requireRole(...roles) {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Не авторизован' });
    }

    const userRoles = req.user.roles || [];
    const hasRole = roles.some(role => userRoles.includes(role));

    if (!hasRole) {
      return res.status(403).json({
        error: 'Доступ запрещен',
        requiredRoles: roles,
        userRoles
      });
    }

    next();
  };
}

function requirePermission(...permissions) {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Не авторизован' });
    }

    const userPermissions = req.user.permissions || [];
    const hasPermission = permissions.some(perm => userPermissions.includes(perm));

    if (!hasPermission) {
      return res.status(403).json({
        error: 'Недостаточно прав',
        requiredPermissions: permissions
      });
    }

    next();
  };
}
```

### Примеры использования

```javascript
// Только администраторы
app.delete('/api/users/:id',
  authMiddleware,
  requireRole(ROLES.ADMIN),
  async (req, res) => {
    // Удаление пользователя
  }
);

// Создание постов (user и выше)
app.post('/api/posts',
  authMiddleware,
  requirePermission(PERMISSIONS.WRITE_POSTS),
  async (req, res) => {
    // Создание поста
  }
);

// Назначение роли
app.patch('/api/users/:id/roles',
  authMiddleware,
  requireRole(ROLES.ADMIN),
  async (req, res) => {
    const { userId } = req.params;
    const { roles } = req.body;

    await User.findByIdAndUpdate(userId, { roles });

    res.json({ message: 'Роли обновлены', roles });
  }
);
```

---

## 8. Security Best Practices

### Переменные окружения

```bash
# .env
JWT_SECRET=your-very-long-secret-key-min-32-chars-abcd1234
REFRESH_TOKEN_SECRET=another-secret-key-min-32-chars-xyz789
NODE_ENV=production
JWT_EXPIRY=1h
REFRESH_TOKEN_EXPIRY=7d
```

### HTTPS и Secure Cookies

```javascript
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');

const app = express();

// Безопасность заголовков
app.use(helmet());

// CORS конфигурация
app.use(cors({
  origin: process.env.CLIENT_URL,
  credentials: true,
  optionsSuccessStatus: 200
}));

// Secure cookies
app.use(express.cookieParser());

// Установка secure cookie
res.cookie('refreshToken', refreshToken, {
  httpOnly: true,    // Недоступна для JavaScript
  secure: true,      // Только HTTPS
  sameSite: 'strict', // CSRF защита
  maxAge: 7 * 24 * 60 * 60 * 1000 // 7 дней
});
```

### Валидация и санитизация

```javascript
const { body, validationResult } = require('express-validator');

app.post('/api/auth/register',
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 8 }).trim().escape(),
  body('username').isLength({ min: 3 }).trim().escape(),
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    // Обработка...
  }
);
```

### Rate Limiting

```javascript
const rateLimit = require('express-rate-limit');

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 минут
  max: 5, // 5 попыток
  message: 'Слишком много попыток входа, попробуйте позже',
  standardHeaders: true,
  legacyHeaders: false
});

app.post('/api/auth/login', loginLimiter, async (req, res) => {
  // Логика входа
});
```

### Полная безопасная система

```javascript
class SecurityManager {
  static hashPassword = (password) => bcrypt.hash(password, 10);

  static verifyPassword = (password, hash) => bcrypt.compare(password, hash);

  static generateTokens(userId) {
    const accessToken = jwt.sign(
      { userId },
      process.env.JWT_SECRET,
      { expiresIn: '1h', algorithm: 'HS256' }
    );

    const refreshToken = jwt.sign(
      { userId },
      process.env.REFRESH_TOKEN_SECRET,
      { expiresIn: '7d', algorithm: 'HS256' }
    );

    return { accessToken, refreshToken };
  }

  static verifyToken(token, secret = process.env.JWT_SECRET) {
    try {
      return jwt.verify(token, secret);
    } catch (error) {
      throw new Error('Token verification failed');
    }
  }

  static validatePassword(password) {
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return regex.test(password);
  }
}

// Использование
const { accessToken, refreshToken } = SecurityManager.generateTokens(user._id);
```

---

## Примеры использования

### 1. User Authentication

```javascript
// Регистрация пользователя
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "username": "john_doe"
}

// Ответ
{
  "message": "Пользователь успешно зарегистрирован",
  "userId": "507f1f77bcf86cd799439011"
}
```

### 2. Admin Panel Access

```javascript
// Запрос с admin ролью
GET /api/admin/dashboard
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

// Middleware проверит роль 'admin' и предоставит доступ
```

### 3. API Token Protection

```javascript
// Клиент отправляет токен
const apiCall = async () => {
  const token = localStorage.getItem('accessToken');

  const response = await fetch('/api/protected-data', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (response.status === 401) {
    // Обновить токен и повторить запрос
  }

  return response.json();
};
```

---

## Резюме

| Концепция | Назначение | Срок действия |
|-----------|-----------|---------------|
| JWT | Передача информации пользователя | 1 час |
| Refresh Token | Обновление токена | 7 дней |
| Password Hash | Хранение пароля | Постоянно |
| Access Control | Проверка прав доступа | Во время сессии |
| OAuth | Внешняя аутентификация | По политике провайдера |

