# Security Guide: Безопасность на Netlify

Руководство по защите сайтов и данных на Netlify.

---

## Environment Variables Security

### Базовые правила

❌ **НИКОГДА:**
- Не коммитьте `.env` файлы в Git
- Не храните секреты в исходном коде
- Не используйте секреты в клиентском коде
- Не публикуйте API ключи в публичных репозиториях

✅ **ВСЕГДА:**
- Храните секреты в Netlify Environment Variables
- Используйте `.gitignore` для `.env` файлов
- Используйте Netlify Functions для API запросов с секретами
- Ротируйте ключи регулярно

---

### Правильное хранение секретов

**Локальная разработка:**
```bash
# .env (НЕ коммитить!)
SECRET_API_KEY=abc123xyz
DATABASE_URL=postgresql://user:pass@host/db
```

**.gitignore:**
```
.env
.env.local
.env.development
.env.production
```

**Production (Netlify UI):**
```
Site Settings → Build & Deploy → Environment → Add variable
```

---

### Клиентские vs серверные переменные

**Клиентские переменные (видны в браузере):**
```js
// React
const apiUrl = process.env.REACT_APP_API_URL;  // ✅ OK для публичных данных

// ❌ НЕ ДЕЛАЙТЕ ТАК
const secretKey = process.env.REACT_APP_SECRET_KEY;  // Видно в исходниках!
```

**Серверные переменные (безопасные):**
```js
// netlify/functions/api.js
exports.handler = async (event) => {
  const secretKey = process.env.SECRET_API_KEY;  // ✅ Безопасно

  const response = await fetch('https://api.example.com/data', {
    headers: { 'Authorization': `Bearer ${secretKey}` }
  });

  return {
    statusCode: 200,
    body: JSON.stringify(await response.json())
  };
};
```

---

### Prefixes для клиентских переменных

| Фреймворк | Префикс | Видимость |
|-----------|---------|-----------|
| React | `REACT_APP_` | Клиент (браузер) |
| Vue | `VUE_APP_` | Клиент (браузер) |
| Next.js | `NEXT_PUBLIC_` | Клиент (браузер) |
| Vite | `VITE_` | Клиент (браузер) |
| Any | Без префикса | Сервер (Functions, build) |

**Правило:** Если переменная БЕЗ префикса → она безопасна (только сервер).

---

## API Keys Protection

### Проблема: Секреты в клиентском коде

```js
// ❌ ПЛОХО: API ключ виден в браузере
fetch('https://api.stripe.com/v1/charges', {
  headers: {
    'Authorization': 'Bearer sk_live_abc123xyz'  // Видно в DevTools!
  }
});
```

### Решение: Netlify Functions как прокси

**Архитектура:**
```
Browser → Netlify Function → External API
          (с секретным ключом)
```

**Реализация:**
```js
// netlify/functions/stripe-charge.js
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

exports.handler = async (event) => {
  const { amount, token } = JSON.parse(event.body);

  try {
    const charge = await stripe.charges.create({
      amount,
      currency: 'usd',
      source: token,
    });

    return {
      statusCode: 200,
      body: JSON.stringify({ success: true, charge })
    };
  } catch (error) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: error.message })
    };
  }
};
```

**Клиентский код (безопасный):**
```js
// Клиент НЕ знает API ключ
fetch('/.netlify/functions/stripe-charge', {
  method: 'POST',
  body: JSON.stringify({ amount: 1000, token: 'tok_visa' })
})
.then(res => res.json())
.then(data => console.log(data));
```

---

### Rate limiting для Functions

```js
// netlify/functions/api.js
const rateLimit = new Map();

exports.handler = async (event) => {
  const ip = event.headers['client-ip'];
  const now = Date.now();

  // Проверка rate limit (5 запросов в минуту)
  const requests = rateLimit.get(ip) || [];
  const recentRequests = requests.filter(time => now - time < 60000);

  if (recentRequests.length >= 5) {
    return {
      statusCode: 429,
      body: JSON.stringify({ error: 'Too many requests' })
    };
  }

  recentRequests.push(now);
  rateLimit.set(ip, recentRequests);

  // Ваша логика
  return {
    statusCode: 200,
    body: JSON.stringify({ message: 'Success' })
  };
};
```

---

## HTTPS

### Автоматический SSL

Netlify предоставляет **бесплатный HTTPS** через Let's Encrypt.

**Включение (автоматическое):**
- `.netlify.app` домены: HTTPS из коробки
- Custom domains: HTTPS активируется после DNS propagation

**Проверка:**
```
Domain Settings → HTTPS → Let's Encrypt certificate provisioned
```

---

### Принудительный HTTPS

**Redirect HTTP → HTTPS:**
```toml
# netlify.toml
[[redirects]]
  from = "http://example.com/*"
  to = "https://example.com/:splat"
  status = 301
  force = true
```

**Или через UI:**
```
Domain Settings → HTTPS → Force HTTPS
```

---

### HSTS (HTTP Strict Transport Security)

```toml
# netlify.toml
[[headers]]
  for = "/*"
  [headers.values]
    Strict-Transport-Security = "max-age=31536000; includeSubDomains; preload"
```

**Что делает:**
- Браузер ВСЕГДА использует HTTPS
- Даже если пользователь вводит `http://`
- Защита от SSL stripping атак

---

## Access Control

### Password Protection

**Доступно только для GitHub/GitLab/Bitbucket интеграций.**

```
Site Settings → Access control → Visitor access → Password protection
```

**Параметры:**
- Password: Единый пароль для всех
- Netlify Identity: User authentication

---

### Role-based access с Netlify Identity

```html
<!-- Signup form -->
<div data-netlify-identity-menu></div>
<script src="https://identity.netlify.com/v1/netlify-identity-widget.js"></script>
```

```toml
# netlify.toml
[[redirects]]
  from = "/admin/*"
  to = "/admin/:splat"
  status = 200
  conditions = {Role = ["admin"]}
  force = true
```

**Назначение ролей:**
```
Identity → Users → [User] → Edit → Roles → admin
```

---

### JWT Authentication

```js
// netlify/functions/protected.js
exports.handler = async (event, context) => {
  const { user } = context.clientContext;

  if (!user) {
    return {
      statusCode: 401,
      body: JSON.stringify({ error: 'Unauthorized' })
    };
  }

  // User authenticated
  return {
    statusCode: 200,
    body: JSON.stringify({
      message: `Hello, ${user.email}!`,
      roles: user.app_metadata.roles
    })
  };
};
```

---

## Security Headers

### Essential Security Headers

```toml
# netlify.toml
[[headers]]
  for = "/*"
  [headers.values]
    # Защита от clickjacking
    X-Frame-Options = "DENY"

    # Защита от XSS
    X-XSS-Protection = "1; mode=block"

    # Запрет MIME sniffing
    X-Content-Type-Options = "nosniff"

    # Referrer Policy
    Referrer-Policy = "strict-origin-when-cross-origin"

    # Permissions Policy
    Permissions-Policy = "geolocation=(), microphone=(), camera=()"
```

---

### Content Security Policy (CSP)

```toml
[[headers]]
  for = "/*"
  [headers.values]
    Content-Security-Policy = """
      default-src 'self';
      script-src 'self' 'unsafe-inline' https://cdn.example.com;
      style-src 'self' 'unsafe-inline';
      img-src 'self' data: https:;
      font-src 'self' data:;
      connect-src 'self' https://api.example.com;
      frame-ancestors 'none';
    """
```

**Что защищает:**
- XSS атаки
- Data injection
- Clickjacking
- Unauthorized resource loading

---

### CORS Headers

```toml
[[headers]]
  for = "/api/*"
  [headers.values]
    Access-Control-Allow-Origin = "https://yourdomain.com"
    Access-Control-Allow-Methods = "GET, POST, PUT, DELETE, OPTIONS"
    Access-Control-Allow-Headers = "Content-Type, Authorization"
    Access-Control-Max-Age = "86400"
```

**Для публичного API:**
```toml
[[headers]]
  for = "/api/*"
  [headers.values]
    Access-Control-Allow-Origin = "*"
```

⚠️ **Внимание:** `*` разрешает доступ ВСЕМ. Используйте только для публичных данных.

---

## Forms Security

### Spam Protection

**Honeypot (рекомендуется):**
```html
<form name="contact" method="POST" data-netlify="true" netlify-honeypot="bot-field">
  <!-- Hidden field для ботов -->
  <p style="display:none">
    <label>Don't fill: <input name="bot-field" /></label>
  </p>

  <input type="text" name="name" required />
  <button type="submit">Send</button>
</form>
```

**reCAPTCHA:**
```html
<form name="contact" method="POST" data-netlify="true" data-netlify-recaptcha="true">
  <input type="text" name="name" />
  <div data-netlify-recaptcha="true"></div>
  <button type="submit">Send</button>
</form>
```

---

### Form Validation

**Client-side:**
```html
<input type="email" required pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$" />
<input type="tel" required pattern="[0-9]{10}" />
```

**Server-side (Function):**
```js
exports.handler = async (event) => {
  const { email, message } = JSON.parse(event.body);

  // Валидация
  if (!email || !email.includes('@')) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Invalid email' })
    };
  }

  if (!message || message.length < 10) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Message too short' })
    };
  }

  // Обработка
  return {
    statusCode: 200,
    body: JSON.stringify({ success: true })
  };
};
```

---

## Secrets Management

### Не храните в коде

```js
// ❌ ПЛОХО
const apiKey = "sk_live_abc123xyz";

// ✅ ХОРОШО
const apiKey = process.env.API_KEY;
```

---

### Используйте .gitignore

```
# .gitignore
.env
.env.local
.env.development
.env.production
.env.test

# Секретные файлы
secrets.json
credentials.json
serviceAccount.json
```

---

### Ротация ключей

**Процесс:**
1. Создайте новый API ключ
2. Добавьте в Netlify Environment Variables
3. Redeploy сайт
4. Проверьте работу
5. Удалите старый ключ из API provider
6. Удалите старую переменную из Netlify

**Рекомендуемая частота:**
- API ключи: Каждые 90 дней
- Database credentials: Каждые 180 дней
- OAuth tokens: Автоматически (refresh tokens)

---

### Разделение секретов по окружениям

```toml
# Production
[context.production.environment]
  API_URL = "https://api.example.com"
  API_KEY = "prod_key_abc123"

# Staging
[context.staging.environment]
  API_URL = "https://staging-api.example.com"
  API_KEY = "staging_key_xyz789"

# Preview
[context.deploy-preview.environment]
  API_URL = "https://dev-api.example.com"
  API_KEY = "dev_key_test456"
```

---

## Database Security

### Connection Strings

```js
// ❌ ПЛОХО
const db = postgres('postgresql://user:pass@host:5432/db');

// ✅ ХОРОШО
const db = postgres(process.env.DATABASE_URL);
```

---

### SSL для database connections

```js
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: true  // Требовать валидный SSL сертификат
  }
});
```

---

### Prepared Statements (SQL Injection защита)

```js
// ❌ ПЛОХО: SQL Injection vulnerable
const query = `SELECT * FROM users WHERE email = '${email}'`;

// ✅ ХОРОШО: Prepared statement
const query = 'SELECT * FROM users WHERE email = $1';
const result = await pool.query(query, [email]);
```

---

## Third-party Scripts Security

### Subresource Integrity (SRI)

```html
<script
  src="https://cdn.example.com/library.js"
  integrity="sha384-abc123xyz..."
  crossorigin="anonymous"
></script>
```

**Генерация SRI hash:**
```bash
openssl dgst -sha384 -binary library.js | openssl base64 -A
```

---

### Content Security Policy для scripts

```toml
[[headers]]
  for = "/*"
  [headers.values]
    Content-Security-Policy = "script-src 'self' https://cdn.example.com"
```

---

## Audit и Monitoring

### Security Audit Checklist

✅ **Environment Variables:**
- [ ] Секреты не в коде
- [ ] `.env` в `.gitignore`
- [ ] Клиентские переменные без секретов

✅ **API Security:**
- [ ] Rate limiting
- [ ] API ключи в Functions
- [ ] CORS настроен правильно

✅ **HTTPS:**
- [ ] SSL сертификат активен
- [ ] Force HTTPS включён
- [ ] HSTS header добавлен

✅ **Headers:**
- [ ] Security headers настроены
- [ ] CSP определён
- [ ] X-Frame-Options установлен

✅ **Forms:**
- [ ] Spam protection включен
- [ ] Server-side validation
- [ ] CSRF protection

✅ **Access Control:**
- [ ] Password protection (если нужно)
- [ ] Role-based access (если нужно)

---

### Мониторинг

**Netlify Analytics:**
- 404 errors (возможная reconnaissance)
- Необычные traffic patterns
- Form spam submissions

**External monitoring:**
- [SecurityHeaders.com](https://securityheaders.com)
- [SSL Labs](https://www.ssllabs.com/ssltest/)
- [Mozilla Observatory](https://observatory.mozilla.org)

---

## Compliance

### GDPR

**Для EU пользователей:**
- ✅ Cookie consent banner
- ✅ Privacy policy
- ✅ Data processing agreement
- ✅ Right to deletion

**Netlify Forms:**
```
Forms → Settings → Enable "Delete submissions after 30 days"
```

---

### Privacy-friendly Analytics

**Netlify Analytics:**
- Минимум собираемых данных
- Нет cookies
- GDPR compliant из коробки

**Альтернативы:**
- Plausible
- Fathom
- Simple Analytics

---

## Emergency Response

### В случае компрометации ключа

1. **Немедленно:**
   - Удалите ключ из API provider
   - Создайте новый ключ
   - Обновите в Netlify Environment Variables
   - Trigger redeploy

2. **Проверьте:**
   - Логи API provider на подозрительную активность
   - Netlify Function logs
   - Analytics на необычный трафик

3. **Документируйте:**
   - Время обнаружения
   - Действия предприняты
   - Потенциальный ущерб

---

## Best Practices Summary

✅ **DO:**
- Используйте Environment Variables для секретов
- Используйте Functions для API запросов
- Включайте HTTPS
- Настройте Security Headers
- Используйте rate limiting
- Ротируйте ключи регулярно
- Мониторьте безопасность

❌ **DON'T:**
- Не коммитьте секреты
- Не используйте секреты в клиентском коде
- Не отключайте HTTPS
- Не игнорируйте security warnings
- Не используйте слабые пароли
- Не публикуйте API ключи

---

## Полезные ссылки

- 📖 [SKILL.md](../SKILL.md) - Основной гайд
- ❓ [FAQ](faq.md) - Частые вопросы
- 🔧 [Troubleshooting](troubleshooting.md) - Решение проблем
- 🚀 [Advanced Features](advanced-features.md) - Продвинутые функции
