# Cheatsheet — Быстрая справка

## CLI Команды

### Основные команды деплоя

```bash
# Preview deployment
vercel

# Production deployment
vercel --prod

# Локальная разработка
vercel dev

# Force re-deploy
vercel --force

# Deploy конкретной директории
vercel ./my-app

# Деплой с подтверждением
vercel --confirm
```

### Управление deployments

```bash
# Список всех deployments
vercel ls

# Список для конкретного проекта
vercel ls my-project

# Удалить deployment
vercel rm <url>

# Удалить несколько
vercel rm <url1> <url2> <url3>

# Информация о deployment
vercel inspect <url>

# Alias для deployment
vercel alias <deployment-url> <domain>
```

### Environment Variables

```bash
# Добавить переменную (интерактивно)
vercel env add API_KEY

# Для всех окружений
vercel env add API_KEY production preview development

# Список всех переменных
vercel env ls

# Удалить переменную
vercel env rm API_KEY

# Скачать переменные локально
vercel env pull
vercel env pull .env.local
```

### Логи

```bash
# Логи production
vercel logs

# Логи конкретного deployment
vercel logs <url>

# Real-time логи
vercel logs --follow

# Фильтр по функции
vercel logs --filter="/api/hello"

# Последние N записей
vercel logs --limit=100
```

### Домены

```bash
# Добавить домен
vercel domains add example.com

# Список доменов
vercel domains ls

# Удалить домен
vercel domains rm example.com

# Информация о домене
vercel domains inspect example.com

# Купить домен через Vercel
vercel domains buy example.com
```

### Проекты

```bash
# Список проектов
vercel projects ls

# Создать проект
vercel projects add <name>

# Удалить проект
vercel projects rm <name>

# Линк текущей директории к проекту
vercel link

# Отвязать
vercel unlink
```

### Secrets

```bash
# Добавить secret
vercel secrets add secret-name "secret-value"

# Список secrets
vercel secrets ls

# Переименовать secret
vercel secrets rename old-name new-name

# Удалить secret
vercel secrets rm secret-name
```

### Прочие команды

```bash
# Логин
vercel login

# Логаут
vercel logout

# Информация о текущем пользователе
vercel whoami

# Справка
vercel help

# Справка по команде
vercel <command> --help

# Версия CLI
vercel --version

# Переключить scope (team)
vercel switch <team-slug>
```

---

## vercel.json Конфигурация

### Базовая структура

```json
{
  "version": 2,
  "name": "my-app",
  "regions": ["iad1", "sfo1"],
  "env": {
    "API_URL": "https://api.example.com"
  }
}
```

### Redirects (301/302)

```json
{
  "redirects": [
    {
      "source": "/old-page",
      "destination": "/new-page",
      "permanent": true
    },
    {
      "source": "/blog/:slug",
      "destination": "/news/:slug",
      "permanent": false
    },
    {
      "source": "/docs/:path*",
      "destination": "https://docs.example.com/:path*"
    }
  ]
}
```

### Rewrites (прокси)

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://backend.com/api/:path*"
    },
    {
      "source": "/:path*",
      "destination": "/index.html"
    }
  ]
}
```

### Headers

```json
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "s-maxage=60, stale-while-revalidate"
        },
        {
          "key": "Access-Control-Allow-Origin",
          "value": "*"
        }
      ]
    },
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        }
      ]
    }
  ]
}
```

### Настройка сборки

```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "outputDirectory": "dist",
  "framework": "nextjs"
}
```

### Cron Jobs (Pro)

```json
{
  "crons": [
    {
      "path": "/api/cleanup",
      "schedule": "0 0 * * *"
    },
    {
      "path": "/api/backup",
      "schedule": "0 */6 * * *"
    }
  ]
}
```

### Регионы и функции

```json
{
  "functions": {
    "api/**/*.js": {
      "memory": 1024,
      "maxDuration": 10
    },
    "api/heavy.js": {
      "memory": 3008,
      "maxDuration": 60
    }
  },
  "regions": ["iad1", "sfo1", "cdg1"]
}
```

### Public routes (без авторизации)

```json
{
  "routes": [
    {
      "src": "/api/public/(.*)",
      "dest": "/api/public/$1"
    }
  ]
}
```

### Ignore paths (не билдить)

```json
{
  "github": {
    "enabled": true,
    "autoAlias": true,
    "silent": false,
    "autoJobCancelation": true
  },
  "ignoreCommand": "bash ignore-build.sh"
}
```

---

## API Routes Patterns

### Базовый handler (Node.js)

```javascript
// api/hello.js
export default function handler(req, res) {
  res.status(200).json({ message: 'Hello World' })
}
```

### HTTP методы

```javascript
export default function handler(req, res) {
  const { method } = req

  switch (method) {
    case 'GET':
      return res.json({ data: 'GET request' })
    case 'POST':
      return res.json({ data: 'POST request' })
    case 'PUT':
      return res.json({ data: 'PUT request' })
    case 'DELETE':
      return res.json({ data: 'DELETE request' })
    default:
      res.setHeader('Allow', ['GET', 'POST', 'PUT', 'DELETE'])
      return res.status(405).end(`Method ${method} Not Allowed`)
  }
}
```

### Query parameters

```javascript
// GET /api/user?id=123&name=John
export default function handler(req, res) {
  const { id, name } = req.query
  res.json({ id, name })
}
```

### Dynamic routes

```javascript
// api/users/[id].js → /api/users/123
export default function handler(req, res) {
  const { id } = req.query
  res.json({ userId: id })
}

// api/posts/[...slug].js → /api/posts/2024/hello
export default function handler(req, res) {
  const { slug } = req.query
  // slug = ['2024', 'hello']
  res.json({ path: slug })
}
```

### Request body

```javascript
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const { name, email } = req.body
  res.json({ received: { name, email } })
}
```

### CORS

```javascript
export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') {
    return res.status(200).end()
  }

  res.json({ message: 'CORS enabled' })
}
```

### Caching

```javascript
export default function handler(req, res) {
  // Cache на 60 секунд
  res.setHeader('Cache-Control', 's-maxage=60, stale-while-revalidate')
  res.json({ data: 'Cached response' })
}
```

### Environment variables

```javascript
export default function handler(req, res) {
  const apiKey = process.env.API_KEY
  const publicKey = process.env.NEXT_PUBLIC_API_KEY

  res.json({
    hasApiKey: !!apiKey,
    publicKey: publicKey
  })
}
```

### Error handling

```javascript
export default async function handler(req, res) {
  try {
    const data = await fetchData()
    res.json({ data })
  } catch (error) {
    console.error('Error:', error)
    res.status(500).json({
      error: 'Internal Server Error',
      message: error.message
    })
  }
}
```

---

## Edge Functions (Middleware)

### Базовый middleware (Next.js)

```javascript
// middleware.js
import { NextResponse } from 'next/server'

export function middleware(request) {
  return NextResponse.next()
}

export const config = {
  matcher: '/api/:path*'
}
```

### Geo-routing

```javascript
import { NextResponse } from 'next/server'

export function middleware(request) {
  const country = request.geo.country || 'US'

  if (country === 'RU') {
    return NextResponse.redirect(new URL('/ru', request.url))
  }

  return NextResponse.next()
}
```

### Authentication

```javascript
import { NextResponse } from 'next/server'

export function middleware(request) {
  const token = request.cookies.get('auth-token')

  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/admin/:path*']
}
```

### A/B Testing

```javascript
import { NextResponse } from 'next/server'

export function middleware(request) {
  const bucket = Math.random() < 0.5 ? 'a' : 'b'
  const response = NextResponse.next()

  response.cookies.set('bucket', bucket)

  return response
}
```

### Custom headers

```javascript
import { NextResponse } from 'next/server'

export function middleware(request) {
  const response = NextResponse.next()

  response.headers.set('X-Custom-Header', 'value')
  response.headers.set('X-Request-ID', crypto.randomUUID())

  return response
}
```

---

## Environment Variables

### Типы переменных

```bash
# Серверные (только API routes, SSR)
API_KEY=secret123
DATABASE_URL=postgres://...

# Клиентские (браузер, Next.js)
NEXT_PUBLIC_API_URL=https://api.example.com
NEXT_PUBLIC_ANALYTICS_ID=GA-123456
```

### .env.local (локальная разработка)

```bash
# .env.local (не коммитить!)
API_KEY=dev-key-123
DATABASE_URL=postgres://localhost/mydb
NEXT_PUBLIC_API_URL=http://localhost:3000
```

### Синхронизация с Vercel

```bash
# Скачать из Vercel
vercel env pull .env.local

# Добавить в Vercel
vercel env add API_KEY production
vercel env add NEXT_PUBLIC_API_URL development
```

---

## Regions (коды регионов)

```json
{
  "regions": [
    "iad1",  // Вашингтон (США, восток)
    "sfo1",  // Сан-Франциско (США, запад)
    "cdg1",  // Париж (Франция)
    "hnd1",  // Токио (Япония)
    "gru1",  // Сан-Паулу (Бразилия)
    "lhr1",  // Лондон (Великобритания)
    "sin1"   // Сингапур
  ]
}
```

---

## Полезные ссылки

- **Dashboard:** https://vercel.com/dashboard
- **Документация:** https://vercel.com/docs
- **Status:** https://vercel.com/status
- **Templates:** https://vercel.com/templates
- **CLI Docs:** https://vercel.com/docs/cli
- **Pricing:** https://vercel.com/pricing

---

## Shortcuts

```bash
# Алиасы для быстрого доступа
alias vd="vercel dev"
alias vp="vercel --prod"
alias vl="vercel logs --follow"
alias vls="vercel ls"

# Добавить в ~/.bashrc или ~/.zshrc
```

---

**Больше информации:**
- **FAQ:** `faq.md`
- **Troubleshooting:** `troubleshooting.md`
- **CLI Reference:** `cli-reference.md`
