# Cheatsheet: Netlify Quick Reference

Быстрая справка по командам и паттернам Netlify.

---

## CLI Commands

### Установка и авторизация
```bash
# Установка
npm install -g netlify-cli

# Авторизация
netlify login

# Проверка статуса
netlify status
```

---

### Deployment

```bash
# Draft deploy (предпросмотр)
netlify deploy

# Production deploy
netlify deploy --prod

# Deploy конкретной папки
netlify deploy --prod --dir=build

# Deploy с сообщением
netlify deploy --prod --message="Fix header bug"
```

---

### Local Development

```bash
# Запуск dev сервера с эмуляцией Netlify
netlify dev

# Указать порт
netlify dev --port=3000

# Запуск Functions локально
netlify functions:serve

# Создание новой Function
netlify functions:create
```

---

### Site Management

```bash
# Список сайтов
netlify sites:list

# Связать локальную папку с сайтом
netlify link

# Открыть сайт в браузере
netlify open

# Открыть админ панель
netlify open:admin
```

---

### Environment Variables

```bash
# Список переменных
netlify env:list

# Добавить переменную
netlify env:set API_KEY "your-key-value"

# Удалить переменную
netlify env:unset API_KEY

# Импорт из .env файла
netlify env:import .env
```

---

### Functions

```bash
# Создать новую Function
netlify functions:create hello-world

# Просмотр логов Functions
netlify functions:log

# Список Functions
netlify functions:list

# Invoke Function локально
netlify functions:invoke hello-world
```

---

### Build

```bash
# Локальный билд (эмуляция Netlify)
netlify build

# Просмотр логов последнего билда
netlify watch
```

---

## netlify.toml Configuration

### Базовая конфигурация

```toml
[build]
  # Команда для сборки
  command = "npm run build"

  # Папка с готовым сайтом
  publish = "build"

  # Папка с Functions
  functions = "netlify/functions"

# Переменные окружения для билда
[build.environment]
  NODE_VERSION = "18"
  REACT_APP_API_URL = "https://api.example.com"
```

---

### Context-specific настройки

```toml
# Production
[context.production]
  command = "npm run build:prod"

[context.production.environment]
  REACT_APP_ENV = "production"

# Deploy Previews (Pull Requests)
[context.deploy-preview]
  command = "npm run build:preview"

# Branch deploys
[context.branch-deploy]
  command = "npm run build:dev"

# Конкретная ветка
[context.staging]
  command = "npm run build:staging"
```

---

### Redirects

```toml
# Простой редирект
[[redirects]]
  from = "/old-path"
  to = "/new-path"
  status = 301

# SPA fallback (client-side routing)
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

# Proxy к внешнему API
[[redirects]]
  from = "/api/*"
  to = "https://api.example.com/:splat"
  status = 200
  force = true

# Редирект с параметрами
[[redirects]]
  from = "/news/:year/:month/:day/:slug"
  to = "/blog/:year-:month-:day-:slug"
  status = 301
```

---

### Headers

```toml
# Кэширование статики
[[headers]]
  for = "/*.js"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.css"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

# CORS
[[headers]]
  for = "/api/*"
  [headers.values]
    Access-Control-Allow-Origin = "*"
    Access-Control-Allow-Methods = "GET, POST, PUT, DELETE, OPTIONS"
    Access-Control-Allow-Headers = "Content-Type"

# Security headers
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
```

---

### Plugins

```toml
# Next.js plugin
[[plugins]]
  package = "@netlify/plugin-nextjs"

# Lighthouse CI
[[plugins]]
  package = "@netlify/plugin-lighthouse"

[[plugins.inputs.audits]]
  path = "/"

[[plugins.inputs.audits]]
  path = "/about"

# Gatsby Cache
[[plugins]]
  package = "netlify-plugin-gatsby-cache"
```

---

## _redirects File

Альтернатива `netlify.toml` для простых редиректов.

Создайте файл `public/_redirects`:

```
# SPA fallback
/*    /index.html   200

# Simple redirect
/old-url    /new-url    301

# Redirect с сохранением query params
/search    /products?category=all    301

# Redirect домена
https://olddomain.com/*    https://newdomain.com/:splat    301!

# API proxy
/api/*    https://api.example.com/:splat    200

# Redirect по языку (i18n)
/    /en    302    Language=en
/    /ru    302    Language=ru

# Redirect по стране
/    /us/home    302    Country=us
/    /uk/home    302    Country=gb
```

⚠️ **Важно:** Порядок имеет значение! Первое совпадение применяется.

---

## _headers File

Альтернатива `netlify.toml` для headers.

Создайте файл `public/_headers`:

```
# Глобальные headers
/*
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block
  X-Content-Type-Options: nosniff

# Кэширование JS/CSS
/*.js
  Cache-Control: public, max-age=31536000, immutable

/*.css
  Cache-Control: public, max-age=31536000, immutable

# CORS для API
/api/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE

# Security headers для продакшена
/
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  Content-Security-Policy: default-src 'self'
```

---

## Netlify Functions

### Базовая структура

```js
// netlify/functions/hello.js
exports.handler = async (event, context) => {
  // event.httpMethod - GET, POST, etc
  // event.path - URL path
  // event.body - Request body (string)
  // event.headers - Request headers
  // event.queryStringParameters - ?param=value

  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: 'Hello World'
    })
  };
};
```

---

### GET Request

```js
exports.handler = async (event) => {
  const { name } = event.queryStringParameters || {};

  return {
    statusCode: 200,
    body: JSON.stringify({
      greeting: `Hello, ${name || 'stranger'}!`
    })
  };
};

// Использование: /.netlify/functions/hello?name=John
```

---

### POST Request

```js
exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  const data = JSON.parse(event.body);

  return {
    statusCode: 200,
    body: JSON.stringify({
      received: data
    })
  };
};
```

---

### Environment Variables

```js
exports.handler = async (event) => {
  const apiKey = process.env.SECRET_API_KEY;

  const response = await fetch('https://api.example.com/data', {
    headers: {
      'Authorization': `Bearer ${apiKey}`
    }
  });

  const data = await response.json();

  return {
    statusCode: 200,
    body: JSON.stringify(data)
  };
};
```

---

### CORS для Functions

```js
const headers = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE'
};

exports.handler = async (event) => {
  // Preflight request
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

  return {
    statusCode: 200,
    headers,
    body: JSON.stringify({ message: 'Success' })
  };
};
```

---

## Environment Variables

### Naming Conventions

| Фреймворк | Префикс | Пример |
|-----------|---------|--------|
| React (CRA) | `REACT_APP_` | `REACT_APP_API_KEY` |
| Vue CLI | `VUE_APP_` | `VUE_APP_API_URL` |
| Next.js | `NEXT_PUBLIC_` | `NEXT_PUBLIC_GA_ID` |
| Vite | `VITE_` | `VITE_API_ENDPOINT` |
| Gatsby | `GATSBY_` | `GATSBY_SITE_URL` |

⚠️ **Важно:** Переменные БЕЗ префикса видны только в Node.js (билд, Functions).

---

### Использование в коде

```js
// React
const apiUrl = process.env.REACT_APP_API_URL;

// Vue
const apiUrl = process.env.VUE_APP_API_URL;

// Next.js
const gaId = process.env.NEXT_PUBLIC_GA_ID;

// Vite
const endpoint = import.meta.env.VITE_API_ENDPOINT;
```

---

## Status Codes

| Code | Значение | Использование |
|------|----------|---------------|
| 200 | OK (rewrite) | SPA routing, прокси |
| 301 | Permanent redirect | Изменён URL навсегда |
| 302 | Temporary redirect | Временное перенаправление |
| 404 | Not Found | Кастомная 404 страница |
| 410 | Gone | Страница удалена навсегда |

---

## Git Branch Contexts

```toml
# Production (main/master)
[context.production.environment]
  REACT_APP_ENV = "production"

# Staging branch
[context.staging.environment]
  REACT_APP_ENV = "staging"

# Deploy previews (PR)
[context.deploy-preview.environment]
  REACT_APP_ENV = "preview"

# Все остальные ветки
[context.branch-deploy.environment]
  REACT_APP_ENV = "development"
```

---

## Useful Patterns

### API Proxy (скрытие ключей)

```toml
[[redirects]]
  from = "/api/*"
  to = "https://api.example.com/:splat"
  status = 200
  headers = {X-API-Key = "secret-key"}
```

---

### Multi-site i18n

```
/en/*    /en/:splat    200
/ru/*    /ru/:splat    200
/        /en           302    Language=en
/        /ru           302    Language=ru
```

---

### Asset optimization

```toml
[[headers]]
  for = "/*.webp"
  [headers.values]
    Cache-Control = "public, max-age=31536000"

[[headers]]
  for = "/*.woff2"
  [headers.values]
    Cache-Control = "public, max-age=31536000"
```

---

### Custom 404 page

```toml
[[redirects]]
  from = "/*"
  to = "/404.html"
  status = 404
```

Или для SPA:
```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200  # ← SPA обработает 404 сам
```

---

## Build Performance

```toml
[build]
  command = "npm ci && npm run build"  # Быстрее чем npm install

[build.environment]
  NODE_VERSION = "18"
  NPM_FLAGS = "--production"           # Без dev dependencies
  NODE_OPTIONS = "--max_old_space_size=4096"  # Больше памяти
```

---

## Useful Links

- 📖 [SKILL.md](../SKILL.md) - Основной гайд
- ❓ [FAQ](faq.md) - Часто задаваемые вопросы
- 🔧 [Troubleshooting](troubleshooting.md) - Решение проблем
- 🔒 [Security Guide](security-guide.md) - Безопасность
