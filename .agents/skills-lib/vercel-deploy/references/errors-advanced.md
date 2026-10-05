# Расширенные ошибки и решения (5-12)

> Базовые ошибки 1-4 (CLI not found, Auth failed, Build failed, Env vars) описаны в SKILL.md.
> Полный troubleshooting: `references/troubleshooting.md`

---

## Ошибка 5: Functions timeout

**Симптомы:**
```bash
Error: Task timed out after 10.00 seconds
```

**Причина:** Функция выполняется дольше лимита (10s на Free, 60s на Pro).

**Решение:**

**1. Оптимизация кода:**
```javascript
// BAD (синхронная обработка)
export default function handler(req, res) {
  const data = processLargeData(); // Долгая операция
  res.status(200).json(data);
}

// GOOD (асинхронная обработка)
export default async function handler(req, res) {
  const data = await processLargeDataAsync(); // Быстрее
  res.status(200).json(data);
}
```

**2. Используйте кэширование:**
```javascript
let cache = null;
let cacheTime = 0;

export default async function handler(req, res) {
  const now = Date.now();

  // Кэш на 5 минут
  if (cache && (now - cacheTime) < 300000) {
    return res.status(200).json(cache);
  }

  const data = await fetchData();
  cache = data;
  cacheTime = now;

  res.status(200).json(data);
}
```

**3. Разбейте на несколько функций:**
```javascript
// Вместо одной долгой функции
// api/process-all.js → timeout

// Создайте несколько быстрых
// api/process-step1.js
// api/process-step2.js
// api/process-step3.js
```

**4. Обновите план (если критично):**
- Free: 10s → Pro: 60s
- Pro: 60s → Enterprise: 900s

---

## Ошибка 6: 404 на API routes

**Симптомы:**
```bash
GET /api/hello → 404 Not Found
```

**Причина:** Неправильная структура папок или файла.

**Решение:**

**Проверьте структуру:**
```bash
# ПРАВИЛЬНО:
api/
└── hello.js  # → /api/hello

# НЕПРАВИЛЬНО:
src/api/hello.js  # НЕ РАБОТАЕТ!
functions/hello.js  # НЕ РАБОТАЕТ!
```

**Проверьте export:**
```javascript
// ПРАВИЛЬНО:
export default function handler(req, res) {
  res.status(200).json({ message: 'OK' });
}

// НЕПРАВИЛЬНО:
function handler(req, res) {
  res.status(200).json({ message: 'OK' });
}
// Отсутствует export default!
```

**Динамические роуты:**
```bash
# ПРАВИЛЬНО:
api/users/[id].js  # → /api/users/123

# НЕПРАВИЛЬНО:
api/users/:id.js  # НЕ РАБОТАЕТ!
```

**Проверьте vercel.json (если используете):**
```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "/api/:path*"  // Убедитесь, что не переопределено
    }
  ]
}
```

---

## Ошибка 7: Slow builds

**Симптомы:**
```bash
Building... (takes 5+ minutes)
```

**Причина:** Отсутствие кэширования, большие зависимости.

**Решение:**

**1. Используйте кэширование:**
```json
// vercel.json
{
  "build": {
    "env": {
      "NEXT_TELEMETRY_DISABLED": "1"
    }
  }
}
```

**2. Проверьте размер node_modules:**
```bash
npm ls --depth=0
```

Удалите неиспользуемые пакеты:
```bash
npm uninstall unused-package
```

**3. Используйте .vercelignore:**
```bash
# .vercelignore
tests/
docs/
*.test.js
*.md
```

**4. Оптимизация Next.js:**
```javascript
// next.config.js
module.exports = {
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  swcMinify: true,  // Быстрый минификатор
};
```

**5. Проверьте build команду:**
```json
// package.json
{
  "scripts": {
    "build": "next build",  // Оптимальная команда
  }
}
```

---

## Ошибка 8: Git Integration не работает

**Симптомы:**
- Push в GitHub, но нет автоматического деплоя
- PR создан, но нет комментария от Vercel

**Причина:** Webhook не настроен или отключён.

**Решение:**

**1. Проверьте интеграцию:**
- Dashboard → Settings → Git
- Убедитесь, что репозиторий подключён

**2. Проверьте webhook в GitHub:**
- GitHub repo → Settings → Webhooks
- Должен быть webhook на `https://api.vercel.com/...`
- Status: Recent Deliveries

**3. Переподключите репозиторий:**
- Dashboard → Settings → Git
- Disconnect Repository
- Connect снова

**4. Проверьте права доступа:**
- GitHub → Settings → Applications
- Vercel должен иметь права на репозиторий

---

## Ошибка 9: Custom domain не работает

**Симптомы:**
```bash
DNS_ERROR
Invalid Configuration
```

**Причина:** Неправильные DNS записи.

**Решение:**

**1. Проверьте DNS записи:**
```bash
# Linux/Mac
dig example.com
dig www.example.com

# Windows
nslookup example.com
nslookup www.example.com
```

**2. Правильные записи:**
```
# Root domain
Type: A
Name: @
Value: 76.76.21.21

# Subdomain
Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

**3. Проверьте в Dashboard:**
- Settings → Domains
- Статус должен быть "Valid"

**4. Подождите:**
- DNS распространение: до 48 часов
- Обычно: 5-30 минут

**5. Очистите DNS кэш:**
```bash
# Windows
ipconfig /flushdns

# Mac
sudo dscacheutil -flushcache

# Linux
sudo systemd-resolve --flush-caches
```

---

## Ошибка 10: Serverless function cold start

**Симптомы:**
- Первый запрос медленный (500ms+)
- Последующие запросы быстрые

**Причина:** Cold start — функция "засыпает" после периода неактивности.

**Решение:**

**1. Оптимизация кода:**
```javascript
// Инициализация вне handler (выполняется один раз)
const db = initializeDatabase();

export default async function handler(req, res) {
  // Используем уже инициализированное соединение
  const data = await db.query('SELECT * FROM users');
  res.status(200).json(data);
}
```

**2. Warming (пинг функции):**
```bash
# Настройте cron job (внешний сервис):
curl https://your-app.vercel.app/api/warm
```

**3. Используйте Edge Functions (если подходит):**
```javascript
// api/hello.js
export const config = {
  runtime: 'edge',  // Почти нет cold start!
};

export default async function handler(req) {
  return new Response(JSON.stringify({ message: 'Hello' }), {
    status: 200,
    headers: { 'content-type': 'application/json' },
  });
}
```

**4. Минимизируйте зависимости:**
```javascript
// BAD (большая библиотека)
import moment from 'moment';

// GOOD (нативный API)
const now = new Date();
```

---

## Ошибка 11: Preview deployment не обновляется

**Симптомы:**
- Push новый commit, но preview показывает старую версию

**Причина:** Кэширование в браузере или CDN.

**Решение:**

**1. Жёсткое обновление:**
- Chrome/Firefox: `Ctrl + Shift + R` (Windows) / `Cmd + Shift + R` (Mac)

**2. Проверьте URL:**
- Каждый commit создаёт НОВЫЙ URL
- Убедитесь, что используете последний

**3. Проверьте deployment:**
```bash
vercel ls
```

**4. Откройте инспектор:**
```bash
vercel inspect <latest-preview-url>
```

Убедитесь, что commit hash соответствует вашему последнему коммиту.

---

## Ошибка 12: Out of memory

**Симптомы:**
```bash
Error: JavaScript heap out of memory
```

**Причина:** Функция использует больше памяти, чем доступно (1024 MB на Free).

**Решение:**

**1. Оптимизация обработки данных:**
```javascript
// BAD (загружает всё в память)
const allData = await fetchAllRecords(); // 10000+ записей
const filtered = allData.filter(x => x.active);

// GOOD (streaming/pagination)
const data = await fetchRecords({ limit: 100, offset: 0 });
```

**2. Используйте streams:**
```javascript
export default async function handler(req, res) {
  const stream = await getLargeDataStream();
  stream.pipe(res);
}
```

**3. Обновите план (если критично):**
- Free: 1024 MB → Pro: 3008 MB
