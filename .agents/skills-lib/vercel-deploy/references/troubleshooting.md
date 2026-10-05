# Troubleshooting — Решение типичных проблем

## Ошибка: `vercel: command not found`

**Симптомы:**
```bash
$ vercel
bash: vercel: command not found
```

**Причина:**
Vercel CLI не установлен или не добавлен в PATH.

**Решение:**

**Шаг 1: Установка**
```bash
npm install -g vercel
```

**Шаг 2: Проверка**
```bash
vercel --version
```

**Если не работает после установки:**
```bash
# Найти путь к npm global bin
npm config get prefix

# Добавить в PATH (для bash)
echo 'export PATH="$PATH:$(npm config get prefix)/bin"' >> ~/.bashrc
source ~/.bashrc

# Для Windows PowerShell
$env:Path += ";$(npm config get prefix)"
```

**Дополнительно:**
- Убедитесь что Node.js установлен: `node --version`
- Попробуйте перезапустить терминал
- Используйте `npx vercel` как временное решение

---

## Ошибка: Authentication failed

**Симптомы:**
```bash
Error! No existing credentials found. Please log in.
Error! Authentication timed out
```

**Причина:**
Не выполнен вход в Vercel аккаунт или истёк токен авторизации.

**Решение:**

**Шаг 1: Логин**
```bash
vercel login
```

**Шаг 2: Выбрать метод**
- Email (получите код на почту)
- GitHub
- GitLab
- Bitbucket

**Если логин не работает:**
```bash
# Удалить старые credentials
vercel logout

# Войти заново
vercel login
```

**Для CI/CD:**
```bash
# Создать токен: vercel.com/account/tokens
vercel --token=YOUR_TOKEN
```

**Дополнительно:**
- Проверьте интернет-соединение
- Убедитесь что не используется прокси/VPN блокирующий Vercel
- Проверьте файл `~/.vercel/auth.json`

---

## Ошибка: Build failed — Module not found

**Симптомы:**
```
Error: Cannot find module 'some-package'
Module not found: Can't resolve './component'
```

**Причина:**
- Зависимости не установлены
- Неправильный путь импорта
- Отсутствует пакет в package.json

**Решение:**

**Проблема 1: Зависимость не в package.json**
```bash
# Добавить зависимость
npm install some-package

# Убедитесь что она в package.json
cat package.json | grep some-package

# Закоммитить и задеплоить
git add package.json package-lock.json
git commit -m "Add missing dependency"
git push
```

**Проблема 2: DevDependency вместо Dependency**
```json
// package.json — НЕПРАВИЛЬНО
{
  "devDependencies": {
    "react": "^18.0.0"  // ❌ React нужен для сборки!
  }
}

// ПРАВИЛЬНО
{
  "dependencies": {
    "react": "^18.0.0"  // ✅
  }
}
```

**Проблема 3: Неправильный путь импорта**
```javascript
// ❌ НЕПРАВИЛЬНО (регистр важен!)
import Button from './Components/Button'  // файл: components/Button.js

// ✅ ПРАВИЛЬНО
import Button from './components/Button'
```

**Проблема 4: Отсутствует файл**
```bash
# Проверить что файл закоммичен
git ls-files | grep component

# Если нет — добавить
git add src/components/Button.js
git commit -m "Add missing file"
git push
```

**Дополнительно:**
- Очистить Vercel cache: Project Settings → Clear Cache
- Проверить .gitignore (файл не игнорируется?)
- Локально тестировать: `npm run build`

---

## Ошибка: Environment variables не видны

**Симптомы:**
```javascript
console.log(process.env.API_KEY) // undefined в production
```

**Причина:**
- Переменная не добавлена в Vercel
- Не указано правильное окружение
- Отсутствует префикс для клиентских переменных

**Решение:**

**Шаг 1: Добавить переменную через CLI**
```bash
# Для всех окружений
vercel env add API_KEY production preview development

# Ввести значение когда попросит
```

**Шаг 2: Или через Dashboard**
1. Project Settings → Environment Variables
2. Add New → Имя, значение
3. Выбрать окружения: Production / Preview / Development

**Шаг 3: Ре-деплой (важно!)**
```bash
vercel --prod
```

**Для Next.js клиентских переменных:**
```bash
# ❌ НЕПРАВИЛЬНО (не видна на клиенте)
vercel env add API_KEY

# ✅ ПРАВИЛЬНО (префикс NEXT_PUBLIC_)
vercel env add NEXT_PUBLIC_API_KEY
```

**Использование:**
```javascript
// Server-side (API routes, getServerSideProps)
const apiKey = process.env.API_KEY

// Client-side (браузер)
const publicKey = process.env.NEXT_PUBLIC_API_KEY
```

**Проверка:**
```bash
# Скачать переменные локально
vercel env pull .env.local

# Проверить содержимое
cat .env.local
```

**Дополнительно:**
- Переменные применяются только при новом deployment
- Preview deployments имеют отдельные переменные
- Не коммитьте .env файлы в Git!

---

## Ошибка: Functions timeout

**Симптомы:**
```
Error: Task timed out after 10.00 seconds
FUNCTION_INVOCATION_TIMEOUT
```

**Причина:**
Serverless функция выполняется дольше лимита (10 сек для Hobby, 60 сек для Pro).

**Решение:**

**Вариант 1: Оптимизация функции**
```javascript
// ❌ НЕПРАВИЛЬНО — синхронная тяжёлая операция
export default async function handler(req, res) {
  const data = await heavySync Operation() // 15 секунд
  res.json(data)
}

// ✅ ПРАВИЛЬНО — асинхронно с батчингом
export default async function handler(req, res) {
  const dataPromise = optimizedOperation() // 3 секунды
  const result = await dataPromise
  res.json(result)
}
```

**Вариант 2: Переместить в Background Job**
```javascript
// ❌ НЕПРАВИЛЬНО
export default async function handler(req, res) {
  await sendEmail() // 5 сек
  await processImage() // 8 сек
  res.json({ success: true }) // Timeout!
}

// ✅ ПРАВИЛЬНО
export default async function handler(req, res) {
  // Быстрый ответ
  res.json({ success: true, message: 'Processing...' })

  // Тяжёлые операции в background (не ждём)
  processInBackground()
}

async function processInBackground() {
  await sendEmail()
  await processImage()
}
```

**Вариант 3: Upgrade на Pro план**
```bash
# Pro план: 60 секунд timeout
# vercel.com/pricing
```

**Вариант 4: Использовать внешние сервисы**
- Тяжёлые вычисления → AWS Lambda, Google Cloud Functions
- Обработка изображений → Cloudinary, imgix
- Email → SendGrid, Resend
- Cron jobs → GitHub Actions

**Дополнительно:**
- Используйте Edge Functions для быстрых операций
- Добавьте кэширование для повторяющихся запросов
- Проверьте медленные DB запросы

---

## Ошибка: 404 на API routes

**Симптомы:**
```
GET /api/hello → 404 Not Found
```

**Причина:**
Неправильная структура папок или конфигурация.

**Решение:**

**Next.js проекты:**
```
pages/
  api/
    hello.js       → /api/hello ✅
    users/
      [id].js      → /api/users/:id ✅
```

**Другие фреймворки:**
```
api/
  hello.js         → /api/hello ✅
```

**Проверка vercel.json:**
```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "/api/:path*"
    }
  ]
}
```

**Проверка файла:**
```javascript
// api/hello.js — НЕПРАВИЛЬНО
function handler(req, res) {  // ❌ нет export
  res.json({ message: 'Hello' })
}

// ПРАВИЛЬНО
export default function handler(req, res) {  // ✅
  res.json({ message: 'Hello' })
}
```

**Локальное тестирование:**
```bash
vercel dev
curl http://localhost:3000/api/hello
```

**Дополнительно:**
- Убедитесь что файл закоммичен в Git
- Проверьте регистр: `Hello.js` ≠ `hello.js` (на Linux)
- Проверьте Build logs на ошибки

---

## Ошибка: CORS errors

**Симптомы:**
```
Access to fetch at 'https://my-app.vercel.app/api/data'
from origin 'https://other-site.com' has been blocked by CORS policy
```

**Причина:**
API не настроен для приёма запросов с других доменов.

**Решение:**

**Вариант 1: Middleware в функции**
```javascript
// api/data.js
export default function handler(req, res) {
  // Разрешить все домены (для разработки)
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization')

  // Preflight request
  if (req.method === 'OPTIONS') {
    return res.status(200).end()
  }

  // Ваша логика
  res.json({ data: 'Hello' })
}
```

**Вариант 2: vercel.json (глобально)**
```json
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Access-Control-Allow-Origin", "value": "*" },
        { "key": "Access-Control-Allow-Methods", "value": "GET, POST, PUT, DELETE, OPTIONS" },
        { "key": "Access-Control-Allow-Headers", "value": "Content-Type, Authorization" }
      ]
    }
  ]
}
```

**Вариант 3: Конкретный домен (безопаснее)**
```javascript
const allowedOrigins = ['https://mysite.com', 'https://app.mysite.com']

export default function handler(req, res) {
  const origin = req.headers.origin
  if (allowedOrigins.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin)
  }

  // Остальной код...
}
```

**Дополнительно:**
- `*` небезопасен для production (используйте конкретные домены)
- Для credentials добавьте: `Access-Control-Allow-Credentials: true`
- Тестируйте локально: `vercel dev`

---

## Ошибка: Slow builds (медленная сборка)

**Симптомы:**
```
Build time: 15 minutes
Often hits timeout
```

**Причина:**
- Большие node_modules
- Неэффективный build process
- Отсутствие кэширования

**Решение:**

**Оптимизация 1: Кэширование зависимостей**
```json
// vercel.json
{
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/node",
      "config": {
        "includeFiles": ["node_modules/**"]
      }
    }
  ]
}
```

**Оптимизация 2: Удалить ненужные зависимости**
```bash
# Анализ размера пакетов
npx depcheck

# Удалить неиспользуемые
npm uninstall unused-package
```

**Оптимизация 3: Lazy loading**
```javascript
// ❌ НЕПРАВИЛЬНО — импортируется всё
import _ from 'lodash'

// ✅ ПРАВИЛЬНО — только нужное
import debounce from 'lodash/debounce'
```

**Оптимизация 4: Build Output Configuration**
```json
// next.config.js
module.exports = {
  output: 'standalone',  // Уменьшает размер
  swcMinify: true,       // Быстрее minify
}
```

**Оптимизация 5: Monorepo с Turborepo**
```bash
# Установка
npm install turbo --global

# turbo.json
{
  "pipeline": {
    "build": {
      "outputs": ["dist/**", ".next/**"],
      "cache": true
    }
  }
}
```

**Дополнительно:**
- Используйте `.vercelignore` для исключения файлов
- Upgrade на Pro план для faster builds
- Проверьте Build logs на bottlenecks

---

## Ошибка: Deployment failed with exit code 1

**Симптомы:**
```
Error: Command "npm run build" exited with 1
```

**Причина:**
Ошибки в процессе сборки проекта.

**Решение:**

**Шаг 1: Проверить Build logs**
- Dashboard → Deployments → Failed deployment → View Build Logs
- Найти точную ошибку (обычно в конце логов)

**Шаг 2: Воспроизвести локально**
```bash
# Очистить
rm -rf node_modules .next

# Установить зависимости
npm install

# Собрать
npm run build
```

**Типичные причины:**

**ESLint ошибки:**
```json
// next.config.js — игнорировать ESLint при билде
module.exports = {
  eslint: {
    ignoreDuringBuilds: true
  }
}
```

**TypeScript ошибки:**
```json
// next.config.js
module.exports = {
  typescript: {
    ignoreBuildErrors: true  // ⚠️ Временное решение
  }
}
```

**Импорт несуществующего файла:**
```bash
# Проверить все импорты
git ls-files | xargs grep "import.*from.*nonexistent"
```

**Дополнительно:**
- Проверьте версии Node.js: `.nvmrc` или `engines` в package.json
- Убедитесь что build script правильный в package.json
- Проверьте .gitignore (важные файлы не игнорируются?)

---

## Ошибка: Port already in use (dev mode)

**Симптомы:**
```bash
$ vercel dev
Error: Port 3000 is already in use
```

**Причина:**
Другой процесс использует порт 3000.

**Решение:**

**Вариант 1: Убить процесс на порту**
```bash
# macOS/Linux
lsof -ti:3000 | xargs kill -9

# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process

# Windows CMD
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Вариант 2: Использовать другой порт**
```bash
vercel dev --listen 3001
```

**Вариант 3: Настроить в vercel.json**
```json
{
  "devCommand": "next dev --port 3001"
}
```

**Дополнительно:**
- Проверьте запущенные процессы: `ps aux | grep node`
- Перезапустите терминал
- Проверьте Docker контейнеры: `docker ps`

---

## Ошибка: Git integration issues

**Симптомы:**
```
Vercel не создаёт deployments при push
Missing webhooks
```

**Причина:**
Проблемы с интеграцией Git репозитория.

**Решение:**

**Шаг 1: Проверить подключение**
- Dashboard → Project Settings → Git
- Убедитесь что репозиторий подключен

**Шаг 2: Переподключить репозиторий**
1. Project Settings → Git → Disconnect
2. Connect Git Repository → Выбрать заново
3. Install Vercel app (если GitHub)

**Шаг 3: Проверить права доступа**
- GitHub: Settings → Applications → Vercel
- Убедитесь что Vercel имеет доступ к репозиторию

**Шаг 4: Проверить webhooks**
```bash
# GitHub
Repo → Settings → Webhooks → vercel.com/git/...
Status: ✅ Recent Deliveries
```

**Шаг 5: Ручной деплой**
```bash
# Если автоматика не работает
vercel --prod
```

**Дополнительно:**
- Проверьте Ignored Build Step settings
- Убедитесь что не используете [skip ci]
- Проверьте branch protection rules

---

## Ошибка: Custom domain не работает

**Симптомы:**
```
DNS_PROBE_FINISHED_NXDOMAIN
This site can't be reached
```

**Причина:**
Неправильно настроены DNS записи.

**Решение:**

**Шаг 1: Проверить конфигурацию в Vercel**
```bash
vercel domains inspect example.com
```

**Шаг 2: Настроить DNS у регистратора**

**Для корневого домена (example.com):**
```
Type: A
Name: @
Value: 76.76.21.21
TTL: 300
```

**Для поддомена (www.example.com):**
```
Type: CNAME
Name: www
Value: cname.vercel-dns.com
TTL: 300
```

**Шаг 3: Проверить распространение DNS**
```bash
# Проверка A записи
dig example.com

# Проверка CNAME
dig www.example.com

# Или онлайн: whatsmydns.net
```

**Шаг 4: Подождать**
- DNS обновляется 5-30 минут (обычно)
- Максимум 48 часов

**Проблема: Invalid Configuration**
```bash
# Удалить и добавить заново
vercel domains rm example.com
vercel domains add example.com
```

**Дополнительно:**
- Отключите прокси CDN (например Cloudflare) временно
- Проверьте что домен не указывает на старый хостинг
- SSL автоматически выпускается после успешной привязки

---

**Больше информации:**
- **FAQ:** `faq.md`
- **CLI команды:** `cli-reference.md`
- **Сравнение с Netlify:** `vercel-vs-netlify.md`
