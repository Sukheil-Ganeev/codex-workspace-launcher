# Troubleshooting: Решение проблем Netlify

Типичные ошибки при деплое на Netlify и их решение.

---

## Password Protection

### Ошибка: Password protection на Drop деплое

**Симптомы:**
- Задеплоили сайт через Drop Deploy (drag & drop)
- Сайт требует пароль при открытии
- Нет опции отключить пароль в настройках

**Причина:**
Drop Deploy по умолчанию создаёт защищённый паролем сайт для предпросмотра. Эта функция **не может быть отключена** для Drop Deploy.

**Решение:**

✅ **Метод 1: GitHub Integration (рекомендуется)**
```bash
# 1. Создай GitHub репозиторий
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/username/repo.git
git push -u origin main

# 2. Netlify → New site from Git
# 3. Выбери репозиторий
# 4. Настрой Build Settings
```

✅ **Метод 2: Netlify CLI**
```bash
# Установка CLI
npm install -g netlify-cli

# Логин
netlify login

# Деплой
netlify deploy --prod --dir=build
```

⚠️ **Важно:** После перехода на GitHub/CLI старый Drop Deploy сайт можно удалить.

---

## CORS Errors

### Ошибка: CORS при локальном просмотре

**Симптомы:**
```
Access to fetch at 'http://localhost:3000/api' from origin 'http://localhost:3000'
has been blocked by CORS policy
```

**Причина:**
Локальный сервер разработки (например, `npm start`) не эмулирует Netlify окружение, включая redirects и functions.

**Решение:**

✅ **Используй `netlify dev` для локальной разработки**
```bash
# Вместо npm start
netlify dev

# Автоматически:
# - Запускает dev сервер
# - Эмулирует redirects
# - Запускает Functions локально
# - Применяет Environment Variables
```

**Настройка в netlify.toml:**
```toml
[dev]
  command = "npm start"       # Команда для dev сервера
  targetPort = 3000           # Порт вашего приложения
  port = 8888                 # Порт Netlify Dev (по умолчанию)
  publish = "build"           # Папка с билдом
```

---

## Redirects и SPA

### Ошибка: 404 на прямых ссылках в SPA

**Симптомы:**
- React/Vue/Angular приложение
- Главная страница (`/`) работает
- Прямые ссылки (`/about`, `/products/123`) возвращают 404
- Навигация внутри приложения работает

**Причина:**
SPA использует client-side routing. Когда пользователь переходит по прямой ссылке, Netlify ищет файл `/about/index.html`, которого не существует.

**Решение:**

✅ **Создай файл `_redirects` в папке с билдом**

**Для React (CRA):**
```bash
# public/_redirects
/*    /index.html   200
```

**Для Vue/Vite:**
```bash
# public/_redirects
/*    /index.html   200
```

**Для Next.js (static export):**
```bash
# out/_redirects
/*    /index.html   200
```

**Альтернатива через netlify.toml:**
```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

⚠️ **Важно:**
- Статус `200` (rewrite), НЕ `301` (redirect)!
- Правило должно быть последним (catch-all)

---

## Functions

### Ошибка: Functions не деплоятся

**Симптомы:**
- Function локально работает
- После деплоя получаете 404 на `/.netlify/functions/my-function`
- В логах нет упоминания о Functions

**Причина:**
Netlify не нашёл папку с Functions или неправильная структура.

**Решение:**

✅ **Проверь структуру проекта**
```
project/
├── netlify/
│   └── functions/
│       └── hello.js          ← ✅ Правильно
├── functions/
│   └── goodbye.js            ← ❌ Не найдёт
└── netlify.toml
```

✅ **Укажи путь в netlify.toml (если кастомная папка)**
```toml
[build]
  functions = "my-functions"
```

✅ **Проверь формат функции**
```js
// ✅ Правильно
exports.handler = async (event, context) => {
  return {
    statusCode: 200,
    body: JSON.stringify({ message: "Success" })
  };
};

// ❌ Неправильно (нет exports.handler)
async function myFunction(event) {
  return { statusCode: 200, body: "Success" };
}
```

---

### Ошибка: Function timeout

**Симптомы:**
```
Task timed out after 10.00 seconds
```

**Причина:**
Free tier ограничивает время выполнения Function до **10 секунд**.

**Решение:**

✅ **Оптимизация:**
1. Используй асинхронные операции
2. Убери долгие вычисления
3. Кэшируй результаты
4. Разбей на несколько Functions

✅ **Платный план:**
Pro план увеличивает лимит до **26 секунд**.

---

## Build Failures

### Ошибка: Build command failed

**Симптомы:**
```
Error during build:
"build" exited with 1
```

**Причина:** Может быть 5+ разных причин.

**Решение (чеклист):**

✅ **1. Проверь Build Command**
```toml
# netlify.toml
[build]
  command = "npm run build"    # ← Правильная команда?
  publish = "build"            # ← Правильная папка?
```

✅ **2. Проверь package.json**
```json
{
  "scripts": {
    "build": "react-scripts build"   // ← Команда существует?
  },
  "dependencies": {
    "react": "^18.0.0"                // ← Зависимости указаны?
  }
}
```

✅ **3. Проверь Node.js версию**
```toml
# netlify.toml
[build.environment]
  NODE_VERSION = "18"
```

Или в UI: Site Settings → Build & Deploy → Environment → NODE_VERSION

✅ **4. Проверь логи детально**
```
Deploy log → Find exact error line
```

**Типичные ошибки:**
- `Module not found` → Забыли добавить зависимость в package.json
- `command not found` → Неправильный Build Command
- `ENOENT` → Файл не найден, проверь пути

---

### Ошибка: Out of memory

**Симптомы:**
```
FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed
```

**Причина:**
Билд требует больше памяти, чем доступно (1GB на Free tier).

**Решение:**

✅ **Увеличь memory limit для Node.js**
```toml
# netlify.toml
[build.environment]
  NODE_OPTIONS = "--max_old_space_size=4096"
```

✅ **Оптимизация:**
1. Отключи source maps в продакшене
```js
// React
GENERATE_SOURCEMAP=false npm run build
```

2. Используй code splitting
3. Оптимизируй зависимости (убери неиспользуемые)

---

## Environment Variables

### Ошибка: Environment variables не видны

**Симптомы:**
- Добавили переменную в Netlify UI
- В коде `process.env.MY_VAR` возвращает `undefined`

**Причина:**
React/Vue требуют специальный префикс для клиентских переменных.

**Решение:**

✅ **Используй правильный префикс**

| Фреймворк | Префикс |
|-----------|---------|
| React (CRA) | `REACT_APP_` |
| Vue | `VUE_APP_` |
| Next.js | `NEXT_PUBLIC_` |
| Vite | `VITE_` |

**Пример:**
```bash
# ❌ Не работает в клиентском коде
API_KEY=abc123

# ✅ Работает
REACT_APP_API_KEY=abc123
```

✅ **Redeploy после добавления переменных**
```
Site Settings → Deploys → Trigger deploy
```

⚠️ **Важно:** Переменные применяются только во время билда, не в runtime!

---

### Ошибка: Секретные ключи видны в браузере

**Симптомы:**
- API ключ добавлен в Environment Variables
- Видно в DevTools → Sources

**Причина:**
Клиентский код **весь виден** в браузере. Environment Variables встраиваются в билд.

**Решение:**

✅ **Используй Netlify Functions как прокси**
```js
// netlify/functions/api-proxy.js
exports.handler = async (event) => {
  const apiKey = process.env.SECRET_API_KEY;  // ← Безопасно!

  const response = await fetch(`https://api.example.com/data`, {
    headers: { 'Authorization': `Bearer ${apiKey}` }
  });

  const data = await response.json();
  return {
    statusCode: 200,
    body: JSON.stringify(data)
  };
};
```

```js
// Клиентский код
fetch('/.netlify/functions/api-proxy')
  .then(res => res.json())
  .then(data => console.log(data));
```

📖 **Подробнее:** [security-guide.md](security-guide.md)

---

## Custom Domains

### Ошибка: Domain не работает после настройки

**Симптомы:**
- Добавили домен в Netlify
- Настроили DNS
- Сайт не открывается

**Причина:**
DNS propagation занимает до 24-48 часов.

**Решение:**

✅ **Проверь DNS настройки**
```bash
# Windows
nslookup yourdomain.com

# Linux/Mac
dig yourdomain.com
```

**Должны видеть:**
```
Non-authoritative answer:
Name:    yourdomain.com
Address: 75.2.60.5
```

✅ **Проверь правильность записей**

| Тип | Имя | Значение |
|-----|-----|----------|
| A | @ | 75.2.60.5 |
| CNAME | www | your-site.netlify.app |

✅ **Подожди 24 часа**
Если всё настроено правильно, просто дождитесь DNS propagation.

---

### Ошибка: HTTPS не активируется

**Симптомы:**
```
Certificate provisioning in progress
```

**Причина:**
Let's Encrypt не может проверить домен (неправильные DNS или ждём propagation).

**Решение:**

✅ **Проверь DNS**
- Domain должен указывать на Netlify (A или CNAME запись)
- Propagation завершилась

✅ **Повторная попытка**
```
Domain Settings → HTTPS → Verify DNS configuration
```

✅ **Если не помогает через 48 часов**
```
Support → New ticket с деталями домена
```

---

## Deployment Issues

### Ошибка: Slow builds (долгая сборка)

**Симптомы:**
- Билд занимает 5+ минут
- Большая часть времени на `npm install`

**Причина:**
Зависимости устанавливаются заново при каждом билде.

**Решение:**

✅ **Включи кэширование (автоматически включено)**
Netlify кэширует `node_modules` между билдами.

✅ **Оптимизация package.json**
```bash
# Убери неиспользуемые зависимости
npm uninstall unused-package

# Используй --production для билда
npm ci --production
```

✅ **Build plugins для оптимизации**
```toml
# netlify.toml
[[plugins]]
  package = "@netlify/plugin-nextjs"
```

✅ **Настрой deploy contexts**
```toml
# Не билдить для draft deploys
[context.deploy-preview]
  command = "echo 'Skipping build for preview'"
```

---

### Ошибка: Deploy failed без ясной причины

**Симптомы:**
```
Deploy failed
```
Нет детальной ошибки в логах.

**Причина:**
Может быть проблема с Netlify сервисами.

**Решение:**

✅ **Проверь Netlify Status**
https://www.netlifystatus.com/

✅ **Повторный деплой**
```
Deploys → Retry deploy
```

✅ **Очисть кэш и попробуй снова**
```
Site Settings → Build & Deploy → Clear cache and deploy site
```

---

## Performance

### Ошибка: Медленная загрузка сайта

**Симптомы:**
- Первая загрузка занимает 3+ секунды
- Lighthouse показывает низкий Performance Score

**Причина:**
Неоптимизированные ассеты, большие bundle sizes.

**Решение:**

✅ **Code splitting**
```js
// React lazy loading
const About = React.lazy(() => import('./About'));
```

✅ **Оптимизация изображений**
```bash
# Используй современные форматы
npm install sharp
```

✅ **CDN и кэширование**
```toml
# netlify.toml
[[headers]]
  for = "/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000"
```

✅ **Analyze bundle**
```bash
npm run build -- --stats
npx webpack-bundle-analyzer build/bundle-stats.json
```

---

## Git Integration

### Ошибка: Netlify не видит новые коммиты

**Симптомы:**
- Запушили изменения в GitHub
- Netlify не начинает автоматический билд

**Причина:**
Deploy hooks не настроены или отключены.

**Решение:**

✅ **Проверь Deploy Notifications**
```
Site Settings → Build & Deploy → Deploy notifications
```

✅ **Проверь Branch settings**
```
Site Settings → Build & Deploy → Branches
Убедись что твоя ветка включена для автодеплоя
```

✅ **Ручной trigger**
```
Deploys → Trigger deploy → Deploy site
```

---

### Ошибка: Submodules не клонируются

**Симптомы:**
```
fatal: No url found for submodule path 'libs/module'
```

**Причина:**
Netlify не клонирует Git submodules по умолчанию.

**Решение:**

✅ **Включи submodules в build**
```toml
# netlify.toml
[build]
  command = "git submodule update --init --recursive && npm run build"
```

---

## Forms

### Ошибка: Netlify Forms не работают

**Симптомы:**
- Добавили атрибут `netlify` в форму
- Отправка формы возвращает 404

**Причина:**
Форма не была обнаружена при билде.

**Решение:**

✅ **Добавь атрибуты в HTML**
```html
<form name="contact" method="POST" data-netlify="true">
  <input type="hidden" name="form-name" value="contact" />
  <input type="text" name="name" />
  <button type="submit">Send</button>
</form>
```

✅ **Для SPA (React/Vue)**
Создай статичную HTML версию формы в `public/index.html` для обнаружения:
```html
<!-- Hidden form для Netlify парсинга -->
<form name="contact" netlify netlify-honeypot="bot-field" hidden>
  <input type="text" name="name" />
  <input type="email" name="email" />
</form>
```

---

## Полезные команды для диагностики

```bash
# Проверка DNS
nslookup yourdomain.com

# Проверка SSL сертификата
openssl s_client -connect yourdomain.com:443

# Тест локального билда
netlify build

# Локальный dev с Functions
netlify dev

# Просмотр логов Functions
netlify functions:log

# Список environment variables
netlify env:list
```

---

## Когда обращаться в Support

Обратитесь в Netlify Support если:
- ✅ Проблема с DNS после 48 часов
- ✅ HTTPS сертификат не активируется
- ✅ Billing issues
- ✅ Account access problems
- ✅ Deploy failures без ясной причины после всех попыток

**Контакт:** https://www.netlify.com/support/

---

Не нашли решение? Проверьте [FAQ](faq.md) или [SKILL.md](../SKILL.md).
