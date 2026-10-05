# Конфигурация Netlify: детальное руководство

> Перенесено из SKILL.md — подробности по настройке Build, Environment Variables, Redirects, DNS, netlify.toml.

---

## Build Settings

**Где настраивать:** Site Settings → Build & Deploy → Build settings

### Build command

Команда для сборки проекта:

```bash
# React, Vue
npm run build

# С проверкой типов
npm run lint && npm run build

# Кастомный скрипт
npm run netlify:build
```

### Publish directory

Папка с готовыми файлами для деплоя:

```bash
# React CRA
build

# Vue, Vite
dist

# Next.js
.next

# Статика
.
```

### Build settings для популярных фреймворков

| Фреймворк | Build command | Publish directory |
|-----------|---------------|-------------------|
| **Статический HTML** | (оставьте пустым) | `.` |
| **React (CRA)** | `npm run build` | `build` |
| **Vue CLI** | `npm run build` | `dist` |
| **Next.js** | `npm run build` | `.next` |
| **Vite** | `npm run build` | `dist` |
| **Svelte** | `npm run build` | `public` |
| **11ty** | `npm run build` | `_site` |

### Build hooks

Trigger build извне (без push в Git):

- Site Settings → Build & Deploy → Build hooks → Add build hook
- Название: "Manual trigger"
- Branch: `main`
- Получите URL: `https://api.netlify.com/build_hooks/abc123`

```bash
# Trigger build из терминала
curl -X POST -d '{}' https://api.netlify.com/build_hooks/abc123
```

**Кейс:** Scheduled task обновляет Google Sheets → webhook trigger → Netlify rebuild.

### Deploy contexts (netlify.toml)

Разные настройки для разных веток:

```toml
# netlify.toml в корне репозитория

[build]
  command = "npm run build"
  publish = "dist"

[context.production]
  environment = { NODE_ENV = "production" }

[context.deploy-preview]
  command = "npm run build:preview"

[context.branch-deploy]
  command = "npm run build:staging"
```

---

## Environment Variables: доступ в коде

### Добавление через Dashboard

1. Netlify Dashboard → выберите сайт → Site Settings → Environment variables
2. Кликните "Add a variable" → форма:

| Поле | Значение |
|------|----------|
| **Key** | `TELEGRAM_BOT_TOKEN` |
| **Value** | `123456:ABC-DEF...` |
| **Scopes** | Production, Deploy Previews, Branch deploys (опционально) |

**Scopes:**
- **Production:** main branch deploys
- **Deploy Previews:** Pull Request deploys
- **Branch deploys:** другие ветки (если включено)

Обычно выбирайте: Production + Deploy Previews.

**Важно:** изменения применяются **только к новым деплоям**. Для текущего: Deploys → "Trigger deploy" → "Clear cache and deploy site".

### Что хранить в Environment Variables

**Обязательно:** API ключи (Google Sheets, Telegram, SendGrid), Database URLs, OAuth секреты, JWT secrets, Webhook URLs.

**Опционально:** API endpoints, Feature flags, конфигурация (лимиты).

**НЕ хранить:** публичные данные (лучше hardcode), бинарные данные (используйте файлы).

### По фреймворкам

**В Serverless Functions:**

```javascript
const token = process.env.TELEGRAM_BOT_TOKEN;
```

**В React (Create React App):**

```javascript
const apiUrl = process.env.REACT_APP_API_URL;
const apiKey = process.env.REACT_APP_API_KEY;
```

Prefix `REACT_APP_` обязателен.

**В Vite:**

```javascript
const apiUrl = import.meta.env.VITE_API_URL;
```

Prefix `VITE_` обязателен.

**В Next.js:**

```javascript
// pages/api/data.js (server-side)
const apiKey = process.env.API_KEY; // Без prefix на сервере

// pages/index.js (client-side)
const publicVar = process.env.NEXT_PUBLIC_API_URL; // Prefix для клиента
```

### Build vs Runtime Variables

| Переменная | Build | Runtime | Где использовать |
|------------|-------|---------|------------------|
| `REACT_APP_API_URL` | да | нет | Frontend код |
| `VITE_API_URL` | да | нет | Frontend код |
| `NEXT_PUBLIC_URL` | да | да | Frontend + Backend |
| `API_KEY` (без prefix) | нет | да | Только Serverless Functions |
| `TELEGRAM_BOT_TOKEN` | нет | да | Только Serverless Functions |

**Правило:**
- **Frontend переменные** (с prefix) → встраиваются в bundle → **не храните секреты!**
- **Backend переменные** (без prefix) → только в Functions → безопасно для секретов

**Пример небезопасного использования:**

```javascript
// ПЛОХО: API key в React коде
const apiKey = process.env.REACT_APP_API_KEY;
// Переменная встроится в bundle → любой может её увидеть в DevTools
```

**Правильно:**

```javascript
// ХОРОШО: API key в Serverless Function
// netlify/functions/fetch-data.js
exports.handler = async () => {
  const apiKey = process.env.API_KEY; // Не доступен клиенту
  const data = await fetch(`https://api.example.com/data?key=${apiKey}`);
  return { statusCode: 200, body: JSON.stringify(data) };
};

// Frontend
fetch('/.netlify/functions/fetch-data')
  .then(r => r.json())
  .then(data => console.log(data)); // Клиент не видит API key
```

### Локальная разработка с Environment Variables

**Решение 1: .env файл**

```bash
# .env (добавить в .gitignore!)
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
GOOGLE_SHEETS_API_KEY=AIzaSyD...
```

**Решение 2: netlify dev** — автоматически подтягивает variables из Netlify Dashboard.

**Решение 3: netlify env:import .env** — импорт переменных из Netlify в локальный файл.

**Best Practice:**
1. Создайте `.env.example` (без секретов):
```bash
# .env.example
TELEGRAM_BOT_TOKEN=your_token_here
GOOGLE_SHEETS_API_KEY=your_key_here
```
2. Закоммитьте `.env.example` в Git
3. Не коммитьте `.env` (добавьте в `.gitignore`)
4. Документируйте в README, какие переменные нужны

### Пример для туристического бизнеса

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=-1001234567890

# Google Sheets
GOOGLE_SHEETS_API_KEY=AIzaSyD...
SPREADSHEET_ID=1abc...xyz

# Email notifications
SENDGRID_API_KEY=SG.abc...
FROM_EMAIL=noreply@dxbtours.com

# Payment gateway
PAYMENT_API_KEY=sk_test_...
PAYMENT_WEBHOOK_SECRET=whsec_...
```

---

## Redirects и Rewrites: детальная конфигурация

### netlify.toml

**Базовая структура:**

```toml
# netlify.toml в корне репозитория

[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/old-page"
  to = "/new-page"
  status = 301

[[redirects]]
  from = "/api/*"
  to = "https://api.example.com/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Условные redirects

```toml
# Redirect по стране
[[redirects]]
  from = "/"
  to = "/ae"
  status = 302
  conditions = {Country = ["AE"]}  # UAE visitors

[[redirects]]
  from = "/"
  to = "/ru"
  status = 302
  conditions = {Country = ["RU", "KZ"]}  # Russia/Kazakhstan visitors
```

### Headers

```toml
[[headers]]
  for = "/api/*"
  [headers.values]
    Access-Control-Allow-Origin = "*"
    Cache-Control = "public, max-age=3600"
```

### Environment-specific redirects

```toml
[context.production.redirects]
  from = "/api/*"
  to = "https://api.production.com/:splat"
  status = 200

[context.deploy-preview.redirects]
  from = "/api/*"
  to = "https://api.staging.com/:splat"
  status = 200
```

### Практические примеры _redirects

**Старый домен → новый домен:**

```
https://old-site.com/*    https://new-site.com/:splat   301!
```

`!` — force redirect (даже если есть файл с таким именем).

**SEO redirects:**

```
# Remove trailing slash
/about/    /about    301

# Canonical URLs
/tours/Safari    /tours/safari    301
/tours/SAFARI    /tours/safari    301
```

**Language redirects (netlify.toml):**

```toml
[[redirects]]
  from = "/"
  to = "/en"
  status = 302
  conditions = {Language = ["en"]}

[[redirects]]
  from = "/"
  to = "/ru"
  status = 302
  conditions = {Language = ["ru"]}

[[redirects]]
  from = "/"
  to = "/en"
  status = 302  # Default
```

**Protect admin routes:**

```toml
[[redirects]]
  from = "/admin/*"
  to = "/login"
  status = 302
  conditions = {Role = ["admin"]}  # Требует Netlify Identity
```

**A/B testing:**

```toml
[[redirects]]
  from = "/"
  to = "/variant-a"
  status = 200
  conditions = {Cookie = ["ab_test=a"]}

[[redirects]]
  from = "/"
  to = "/variant-b"
  status = 200
  conditions = {Cookie = ["ab_test=b"]}
```

---

## Custom Domains: DNS настройки

### Вариант A: Netlify DNS (рекомендуется)

1. Netlify покажет nameservers:
   ```
   dns1.p08.nsone.net
   dns2.p08.nsone.net
   dns3.p08.nsone.net
   dns4.p08.nsone.net
   ```
2. Откройте регистратор домена (Namecheap, etc)
3. Найдите "Nameservers" settings
4. Переключите на "Custom DNS"
5. Введите nameservers Netlify

**Время распространения:** 24-48 часов (обычно < 1 часа).

### Вариант B: External DNS

1. Netlify Dashboard → Domain Settings → "Use external DNS"
2. Добавьте DNS records:

| Type | Host | Value | Назначение |
|------|------|-------|------------|
| **A** | @ | 75.2.60.5 | Root domain (dxbtours.com) |
| **AAAA** | @ | 2600:1f14:fff:f700::1 | IPv6 support |
| **CNAME** | www | your-site.netlify.app | www subdomain |
| **CNAME** | blog | blog-site.netlify.app | Subdomain для блога |

### Проверка DNS

```bash
# Проверка A record
nslookup dxbtours.com

# Проверка CNAME
nslookup www.dxbtours.com
```

### HTTPS (Let's Encrypt)

Netlify предоставляет бесплатный HTTPS:
- Let's Encrypt сертификат
- Автоматическое обновление (каждые 90 дней)
- Никаких настроек не требуется

**Force HTTPS:** Domain Settings → HTTPS → Force HTTPS: ON

### Subdomain деплой

Можно деплоить разные проекты на subdomains:
- `dxbtours.com` → главный сайт
- `blog.dxbtours.com` → блог (отдельный Netlify сайт)
- `dashboard.dxbtours.com` → internal dashboard

**Настройка:**
1. Создайте отдельный Netlify сайт для блога
2. Добавьте custom domain: `blog.dxbtours.com`
3. DNS: CNAME `blog` → `blog-site.netlify.app`

### Wildcard subdomain

```
# DNS
*.dxbtours.com → your-site.netlify.app
```

Теперь любой subdomain (`test.dxbtours.com`, `demo.dxbtours.com`) ведёт на ваш сайт.

### HTTPS (Let's Encrypt)

**Что такое HTTPS:**
- Шифрование трафика между браузером и сервером
- Зелёный замок в адресной строке
- Требуется для SEO (Google ранжирует выше)
- Требуется для современных API (Geolocation, Camera, etc)

**Netlify предоставляет бесплатный HTTPS:**
- Let's Encrypt сертификат
- Автоматическое обновление (каждые 90 дней)
- Никаких настроек не требуется

**Проверка:**
- Откройте `https://your-domain.com`
- Кликните на замок в адресной строке → "Certificate is valid"

**Force HTTPS:** Domain Settings → HTTPS → Force HTTPS: ON. Теперь `http://your-domain.com` → автоматически редиректит на `https://`.

### Практический пример: подключить dxbtours.com

1. Купили домен на Namecheap
2. Netlify Dashboard → Site: `price-list.netlify.app` → Domain Settings → Add custom domain → `dxbtours.com`
3. Выбрали Netlify DNS → Netlify показал nameservers:
   ```
   dns1.p08.nsone.net
   dns2.p08.nsone.net
   dns3.p08.nsone.net
   dns4.p08.nsone.net
   ```
4. Namecheap → Domain List → Manage → Nameservers → Custom DNS → вставили nameservers
5. Подождали 30 минут
6. Проверка: `nslookup dxbtours.com` → Address: 75.2.60.5
7. Открыли `https://dxbtours.com` → прайс-лист работает!
8. Domain Settings → HTTPS → Force HTTPS: ON. Теперь `http://dxbtours.com` → `https://dxbtours.com`

---

## GitHub Integration: подробные шаги

### Подключение GitHub репозитория к Netlify

**Шаг 1: Создайте репозиторий**

Если проект уже существует локально:
```bash
cd /d/Downloads/my-project
git init
git add .
git commit -m "Initial commit"
gh repo create my-project --public --source=. --push
```

Если создаёте новый:
```bash
gh repo create my-project --public --clone
cd my-project
echo "# My Project" > README.md
git add .
git commit -m "Initial commit"
git push
```

**Шаг 2: Подключите к Netlify**

1. Откройте https://app.netlify.com
2. Кликните "Add new site" → "Import an existing project"
3. Выберите "GitHub"
4. Авторизуйте Netlify (рекомендую: "All repositories")
5. Выберите репозиторий из списка

**Шаг 3: Настройте Build Settings**

| Поле | Что указать |
|------|-------------|
| **Branch to deploy** | `main` (или `master`) |
| **Build command** | Зависит от проекта (см. таблицу фреймворков) |
| **Publish directory** | Зависит от проекта |
| **Environment variables** | Пока оставьте пустым (настроим позже) |

**Шаг 4: Deploy Site** → Netlify клонирует, установит зависимости, соберёт, опубликует. Время: 1-3 минуты.

**Шаг 5: Переименуйте** → Site Settings → Change site name

### Автоматический деплой при push

1. Изменения локально → `git add . && git commit -m "Update" && git push`
2. GitHub webhook → уведомляет Netlify → автоматический build
3. Через 30-60 секунд: новая версия на production

**Уведомления:** Email ("Deploy succeeded"/"Deploy failed"), Slack/Discord webhooks (Site Settings → Build hooks).

### Branch Deployments

Каждая ветка может иметь свой деплой: `branch-name--my-project.netlify.app`

**Когда использовать:**
- Staging environment: `staging` branch → `staging--my-project.netlify.app`
- Feature testing: `feature/new-design` → `feature-new-design--my-project.netlify.app`

**Как включить:** Site Settings → Build & Deploy → Branch deploys: "All" или отдельные ветки.

---

## CLI: практические примеры

### netlify dev для Serverless Functions

**Структура проекта:**

```
price-list/
├── index.html
├── script.js
└── netlify/
    └── functions/
        └── fetch-prices.js
```

**Serverless Function:**

```javascript
// netlify/functions/fetch-prices.js
exports.handler = async (event, context) => {
  const prices = [
    { name: 'Джип-сафари', price: 150 },
    { name: 'Бурдж Халифа', price: 120 },
  ];

  return {
    statusCode: 200,
    body: JSON.stringify(prices),
  };
};
```

**Frontend:**

```javascript
// script.js
fetch('/.netlify/functions/fetch-prices')
  .then(r => r.json())
  .then(data => {
    console.log(data);
    // Рендерим таблицу
  });
```

**Запуск:**

```bash
cd /d/Downloads/price-list
netlify dev
# Static server: http://localhost:8888
# Functions: http://localhost:8888/.netlify/functions/fetch-prices
```

### CLI workflow: Internal dashboard

```bash
# Шаг 1: Инициализация
cd /d/Downloads/dashboard
netlify init
# Create new site → Site name: team-dashboard

# Шаг 2: Локальная разработка
netlify dev
# Разрабатываете на http://localhost:8888

# Шаг 3: Draft deploy для проверки
netlify deploy
# Проверяете на draft URL

# Шаг 4: Production deploy
netlify deploy --prod
# URL: https://team-dashboard.netlify.app

# Шаг 5: Password protection
netlify open:admin
# Site Settings → Visitor Access → Password Protection
```

### Branch Deployments

```bash
# Создать feature branch
git checkout -b feature/ab-test-hero

# Сделать изменения
nano src/Hero.js
git add .
git commit -m "A/B test: new hero design"
git push -u origin feature/ab-test-hero

# Netlify автоматически создаст:
# https://feature-ab-test-hero--my-project.netlify.app

# Показать клиенту оба варианта:
# - Production: https://my-project.netlify.app
# - Feature: https://feature-ab-test-hero--my-project.netlify.app

# Клиент выбрал новый дизайн:
git checkout main
git merge feature/ab-test-hero
git push
# Netlify автоматически обновит production
```
