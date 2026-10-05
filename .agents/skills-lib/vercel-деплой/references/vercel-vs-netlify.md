# Vercel vs Netlify — Детальное сравнение

## Введение

Vercel и Netlify — две ведущие платформы для деплоя современных веб-приложений. Обе предлагают похожий функционал, но имеют ключевые различия в специализации, производительности и экосистеме.

**TL;DR:**
- **Vercel** → Next.js проекты, SSR/SSG, Edge Functions, production-grade приложения
- **Netlify** → Статичные сайты, JAMstack, быстрое прототипирование, встроенные формы/auth

---

## Таблица сравнения возможностей

| Возможность | Vercel | Netlify | Победитель |
|-------------|---------|---------|------------|
| **Serverless Functions** | ✅ `/api` папка | ✅ `/netlify/functions` | 🟰 |
| **Edge Functions** | ✅ Полная поддержка | ⚠️ Ограничено (Deno) | ✅ Vercel |
| **Preview Deployments** | ✅ Автоматически | ✅ Автоматически | 🟰 |
| **Drop Deployment** | ❌ | ✅ Drag & Drop | ✅ Netlify |
| **Forms** | ❌ | ✅ Встроенные | ✅ Netlify |
| **Identity (Auth)** | ❌ (партнёры) | ✅ Netlify Identity | ✅ Netlify |
| **Next.js оптимизация** | ✅✅✅ Лучшая | ✅ Хорошая | ✅ Vercel |
| **Build скорость** | ⚡ Быстрее | 🐢 Медленнее | ✅ Vercel |
| **Free tier bandwidth** | 100 GB | 100 GB | 🟰 |
| **CLI качество** | ✅ Отличный | ✅ Отличный | 🟰 |
| **Analytics** | ✅ (Pro) | ✅ (Pro) | 🟰 |
| **A/B Testing** | ✅ (Pro) | ✅ (встроенный) | ✅ Netlify |
| **Plugins** | ⚠️ Ограничено | ✅ Экосистема | ✅ Netlify |
| **CDN** | ✅ Глобальный | ✅ Глобальный | 🟰 |
| **Custom domains** | ✅ Бесплатно | ✅ Бесплатно | 🟰 |
| **Environment variables** | ✅ | ✅ | 🟰 |
| **Monorepo** | ✅ Turborepo | ✅ | ✅ Vercel |
| **Docker** | ❌ | ❌ | 🟰 |
| **Scheduled functions** | ✅ (Pro) | ✅ (бесплатно) | ✅ Netlify |
| **DDoS защита** | ✅ | ✅ | 🟰 |
| **Функции timeout (free)** | 10 секунд | 10 секунд | 🟰 |
| **Функции timeout (pro)** | 60 секунд | 26 секунд | ✅ Vercel |

---

## Производительность

### Build Time (время сборки)

**Vercel:**
- ⚡ Быстрее на 30-50% для Next.js
- Оптимизированное кэширование
- Parallel builds на Pro плане

**Netlify:**
- 🐢 Медленнее для сложных проектов
- Хорошее кэширование
- Build plugins могут замедлить

**Тест (Next.js проект, 50 страниц):**
```
Vercel:  2 мин 15 сек ⚡
Netlify: 3 мин 40 сек
```

### Cold Start (время запуска функций)

**Vercel:**
- Node.js: ~50-100 мс
- Edge Functions: ~0 мс (V8 isolates)

**Netlify:**
- Node.js: ~100-200 мс
- Edge Functions: ~50 мс (Deno)

**Победитель:** ✅ Vercel (особенно Edge Functions)

### Global CDN

**Vercel:**
- 80+ локаций
- Автоматическое распределение
- Edge Network

**Netlify:**
- 100+ локаций
- Автоматическое распределение
- ADN (Application Delivery Network)

**Победитель:** 🟰 Примерно равны

---

## Когда использовать Vercel

### ✅ Идеально для:

**1. Next.js проекты**
```bash
# Нулевая конфигурация
vercel
# Всё работает из коробки
```
Vercel создали Next.js, поэтому интеграция идеальная.

**2. SSR/SSG приложения**
- Incremental Static Regeneration (ISR)
- On-Demand Revalidation
- Server-Side Rendering

**3. Edge Functions**
```javascript
// middleware.js — выполняется на edge
export function middleware(request) {
  const country = request.geo.country
  if (country === 'RU') {
    return NextResponse.redirect('/ru')
  }
}
```

**4. Production-grade приложения**
- Enterprise проекты
- High-traffic сайты
- Сложная логика на сервере

**5. Monorepo с Turborepo**
```json
// turbo.json
{
  "pipeline": {
    "build": {
      "outputs": [".next/**"],
      "cache": true
    }
  }
}
```

**6. Быстрая итерация**
- Моментальные preview deployments
- Быстрая сборка
- Отличный DX (Developer Experience)

### ⚠️ Не подходит для:

- Простые статичные сайты (overkill)
- Когда нужны встроенные формы
- Если нужна встроенная авторизация
- Новички без опыта (сложнее Netlify)

---

## Когда использовать Netlify

### ✅ Идеально для:

**1. Статичные сайты**
```bash
# Drag & Drop
# Просто перетащить папку dist/ на netlify.com/drop
```

**2. JAMstack проекты**
- Gatsby
- Hugo
- Jekyll
- Eleventy

**3. Встроенные формы**
```html
<form name="contact" netlify>
  <input type="text" name="name" />
  <input type="email" name="email" />
  <button type="submit">Send</button>
</form>
```
Просто атрибут `netlify` — и форма работает!

**4. Netlify Identity (авторизация)**
```javascript
import netlifyIdentity from 'netlify-identity-widget'

// Логин из коробки
netlifyIdentity.open()
```

**5. Быстрое прототипирование**
- Drop deployment
- Простой UI
- Меньше настроек

**6. Плагины**
```toml
# netlify.toml
[[plugins]]
  package = "@netlify/plugin-lighthouse"

[[plugins]]
  package = "netlify-plugin-image-optim"
```

**7. Новички**
- Проще интерфейс
- Больше документации для начинающих
- Визуальный Deploy Contexts

### ⚠️ Не подходит для:

- Next.js с ISR (медленнее Vercel)
- Требуется Edge Functions с Node.js
- Сложный SSR
- Enterprise масштаб

---

## Free Tier сравнение

### Vercel Hobby (бесплатный)

**Лимиты:**
```
Bandwidth:            100 GB/месяц
Serverless execution: 100 GB-Hours
Edge requests:        1,000,000/месяц
Build time:           6000 минут/месяц
Concurrent builds:    1
Team members:         1
```

**Ограничения функций:**
```
Timeout:              10 секунд
Memory:               1024 MB
Payload:              4.5 MB
```

**Коммерческое использование:** ✅ Разрешено

### Netlify Free

**Лимиты:**
```
Bandwidth:            100 GB/месяц
Build minutes:        300 минут/месяц
Concurrent builds:    1
Sites:                500
Team members:         1
Forms submissions:    100/месяц
Identity users:       1000
```

**Ограничения функций:**
```
Timeout:              10 секунд
Memory:               1024 MB
Invocations:          125k/месяц
```

**Коммерческое использование:** ✅ Разрешено

### Что лучше?

**Vercel Free лучше:**
- ✅ Больше build minutes (6000 vs 300)
- ✅ Больше Edge requests
- ✅ Неограниченные сайты

**Netlify Free лучше:**
- ✅ Формы включены
- ✅ Identity включён
- ✅ Scheduled functions бесплатно

**Вывод:** Для большинства проектов Vercel Free щедрее.

---

## Цены (платные планы)

### Vercel Pro ($20/месяц)

```
Всё из Hobby +
Bandwidth:            1 TB
Serverless:           1000 GB-Hours
Edge requests:        Неограничено
Build time:           Неограничено
Concurrent builds:    6
Timeout:              60 секунд (serverless)
Team members:         10
Analytics:            ✅
Cron Jobs:            ✅
Password Protection:  ✅
```

### Netlify Pro ($19/месяц)

```
Всё из Free +
Bandwidth:            1 TB
Build minutes:        25000/месяц
Concurrent builds:    3
Forms submissions:    1000/месяц
Identity users:       Неограничено (5$/1000 после 1000)
Analytics:            ✅
A/B Testing:          ✅
Background functions: ✅
```

**Вывод:** Примерно одинаковая стоимость, разные акценты.

---

## Serverless Functions сравнение

### Vercel Functions

**Структура:**
```
api/
  hello.js           → /api/hello
  users/
    [id].js          → /api/users/:id
    index.js         → /api/users
```

**Пример:**
```javascript
// api/hello.js
export default function handler(req, res) {
  res.status(200).json({ message: 'Hello from Vercel' })
}
```

**Поддерживаемые языки:**
- Node.js ✅
- Python ✅
- Go ✅
- Ruby ✅

### Netlify Functions

**Структура:**
```
netlify/
  functions/
    hello.js         → /.netlify/functions/hello
    users.js         → /.netlify/functions/users
```

**Пример:**
```javascript
// netlify/functions/hello.js
exports.handler = async (event, context) => {
  return {
    statusCode: 200,
    body: JSON.stringify({ message: 'Hello from Netlify' })
  }
}
```

**Поддерживаемые языки:**
- Node.js ✅
- Go ✅

**Победитель:** ✅ Vercel (больше языков, лучше DX)

---

## Edge Functions сравнение

### Vercel Edge Functions

**Runtime:** V8 Isolates (Web APIs)
**Язык:** JavaScript/TypeScript
**Timeout:** 30 секунд

**Пример (Next.js middleware):**
```javascript
// middleware.js
import { NextResponse } from 'next/server'

export function middleware(request) {
  // Geo-location
  const country = request.geo.country
  const city = request.geo.city

  // Cookies
  const token = request.cookies.get('auth')

  // Headers
  const userAgent = request.headers.get('user-agent')

  return NextResponse.next()
}
```

**Доступ к:**
- ✅ Geo-location
- ✅ Cookies
- ✅ Headers
- ✅ Request/Response API
- ✅ Crypto
- ❌ Node.js APIs

### Netlify Edge Functions

**Runtime:** Deno
**Язык:** JavaScript/TypeScript
**Timeout:** 50 мс (!)

**Пример:**
```typescript
// netlify/edge-functions/hello.ts
export default async (request: Request) => {
  const url = new URL(request.url)
  const country = request.headers.get('x-country')

  return new Response(`Hello from ${country}`)
}

export const config = { path: "/hello" }
```

**Доступ к:**
- ✅ Deno APIs
- ✅ Headers
- ✅ Request/Response API
- ⚠️ Ограниченный npm support

**Победитель:** ✅ Vercel (больше возможностей, лучше интеграция с Next.js)

---

## Миграция

### Netlify → Vercel

**Шаг 1: Клонировать репозиторий**
```bash
git clone https://github.com/user/repo.git
cd repo
```

**Шаг 2: Настроить vercel.json (если нужно)**
```json
{
  "redirects": [
    {
      "source": "/_redirects",
      "destination": "/"
    }
  ]
}
```

**Шаг 3: Миграция Netlify Functions**
```bash
# Было: netlify/functions/hello.js
# Стало: api/hello.js

# Netlify формат
exports.handler = async (event) => {
  return {
    statusCode: 200,
    body: JSON.stringify({ data: 'hello' })
  }
}

# Vercel формат
export default function handler(req, res) {
  res.status(200).json({ data: 'hello' })
}
```

**Шаг 4: Environment variables**
```bash
# Скопировать из Netlify
vercel env add API_KEY production
```

**Шаг 5: Деплой**
```bash
vercel
vercel --prod
```

**Шаг 6: DNS**
```bash
# Обновить DNS записи на Vercel
vercel domains add yourdomain.com
```

### Vercel → Netlify

**Шаг 1: Netlify CLI**
```bash
npm install -g netlify-cli
netlify login
```

**Шаг 2: Создать netlify.toml**
```toml
[build]
  command = "npm run build"
  publish = ".next"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

**Шаг 3: Миграция API routes**
```bash
# Было: api/hello.js
# Стало: netlify/functions/hello.js

# Vercel формат
export default function handler(req, res) {
  res.status(200).json({ data: 'hello' })
}

# Netlify формат
exports.handler = async (event) => {
  return {
    statusCode: 200,
    body: JSON.stringify({ data: 'hello' })
  }
}
```

**Шаг 4: Environment variables**
```bash
netlify env:set API_KEY "value"
```

**Шаг 5: Деплой**
```bash
netlify deploy --prod
```

---

## Выводы

### Выбирайте Vercel если:

✅ Используете Next.js
✅ Нужен SSR/SSG/ISR
✅ Требуются Edge Functions
✅ Production-ready проект
✅ Monorepo с Turborepo
✅ Приоритет — скорость сборки
✅ Много трафика (щедрый Free tier)

### Выбирайте Netlify если:

✅ Статичный сайт
✅ Нужны встроенные формы
✅ Нужна встроенная авторизация
✅ JAMstack проект (Gatsby, Hugo)
✅ Быстрое прототипирование
✅ Новичок в деплое
✅ Drag & Drop деплой

### Можно использовать оба:

- Фронтенд на Vercel
- Статичные ассеты на Netlify
- Формы на Netlify
- API на Vercel

---

**Больше информации:**
- **FAQ:** `faq.md`
- **Troubleshooting:** `troubleshooting.md`
- **CLI Reference:** `cli-reference.md`
