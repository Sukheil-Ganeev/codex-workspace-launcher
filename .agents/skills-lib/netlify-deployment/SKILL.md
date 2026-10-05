---
name: netlify-deployment
description: "Предоставляет полное руководство по деплою на Netlify для туристического бизнеса. Netlify, деплой, хостинг, CDN, Serverless Functions, формы, CI/CD."
---
# Netlify Deployment Skill

**Версия:** 1.0.0
**Дата создания:** 2026-02-04
**Автор:** Claude Code
**Назначение:** Полное руководство по деплою на Netlify для туристического бизнеса

---

## 1. Введение и философия

### Что такое Netlify

Netlify — это платформа для хостинга и деплоя статических сайтов и современных веб-приложений. Это не просто хостинг, а полноценная CI/CD платформа с:

- **Мгновенным деплоем** — от коммита до живого сайта за 30-60 секунд
- **Глобальным CDN** — сайт загружается быстро по всему миру
- **Автоматическим HTTPS** — бесплатный SSL сертификат для всех доменов
- **Serverless Functions** — бэкенд логика без сервера
- **Forms & Identity** — готовые решения для форм и авторизации

### Почему Netlify для туристического бизнеса

В туристическом бизнесе скорость = деньги. Клиент находит ваш сайт в Google, и у вас есть 3 секунды, чтобы его зацепить. Netlify помогает:

**Скорость разработки:**
- Новый прайс-лист? Обновили Google Sheets → деплой за минуту
- Изменили цены? Push в GitHub → автоматический деплой
- Тестируете новый дизайн? Preview deployment для каждого бранча

**Надёжность:**
- Сайт работает 24/7 даже при пиковых нагрузках
- Глобальный CDN — сайт быстро открывается из России, Казахстана, ОАЭ
- Автоматические бэкапы каждого деплоя

**Безопасность:**
- Автоматический HTTPS для SEO и доверия клиентов
- Environment variables для API ключей (Google Sheets, Telegram боты)
- Защита паролем для internal tools

**Экономия:**
- Бесплатный план: 100 GB трафика, 300 build минут/месяц
- Это покрывает десятки сайтов малого и среднего бизнеса
- Не нужен DevOps специалист

### Ключевые возможности

**Деплой методы:**
1. **Netlify Drop** — перетащил папку, получил URL (идеально для тестов)
2. **GitHub Integration** — автоматический деплой при push (production ready)
3. **Netlify CLI** — деплой из терминала (для продвинутых)

**Встроенные инструменты:**
- **Build система** — собирает React, Vue, Next.js автоматически
- **Serverless Functions** — обработка webhooks, интеграция с API
- **Forms** — сбор лидов без бэкенда
- **Redirects/Rewrites** — SEO redirects, SPA routing, API proxy
- **Split Testing** — A/B тесты без кода

**Для нашего бизнеса:**
- Прайс-листы с автообновлением из Google Sheets
- Телеграм боты с webhooks через Netlify Functions
- Лендинги с формами заявок
- Internal dashboards с password protection

---

## 2. Quick Start Guide

### Три способа начать работу

| Метод | Время старта | Сложность | Когда использовать |
|-------|--------------|-----------|-------------------|
| **Netlify Drop** | 30 секунд | Простой | Быстрый тест, демо клиенту |
| **GitHub Integration** | 5 минут | Средний | Production сайты, командная работа |
| **Netlify CLI** | 10 минут | Продвинутый | Автоматизация, CI/CD pipelines |

### Сценарий 1: Netlify Drop (самый быстрый)

**Когда использовать:**
- Нужно показать клиенту демо прайс-листа прямо сейчас
- Тестируете новый дизайн, хотите увидеть на живом URL
- Одноразовый деплой, не планируете обновлять

**Шаги:**
1. Откройте https://app.netlify.com/drop
2. Перетащите папку с вашим сайтом (index.html + assets)
3. Получите URL вида `random-name-123.netlify.app`
4. **ВАЖНО:** Сразу добавьте password protection (Site Settings → Visitor Access)

**Критическое замечание:** Drop создаёт **публичный** URL. Если это internal tool (dashboard с данными клиентов), **обязательно** установите пароль: Site Settings → Visitor Access → Password Protection → Set Password.

### Сценарий 2: GitHub Integration (рекомендуется)

**Когда использовать:**
- Production сайты (прайс-листы, лендинги, боты)
- Нужны автоматические обновления при изменениях
- Работаете в команде или хотите версионность

**Шаги:**

1. **Создайте репозиторий на GitHub:**
```bash
cd /d/Downloads/my-project
git init && git add . && git commit -m "Initial commit"
gh repo create my-project --public --source=. --push
```

2. **Подключите к Netlify:**
   - Откройте https://app.netlify.com → "Add new site" → "Import from GitHub"
   - Выберите репозиторий → настройте Build command и Publish directory
   - Deploy site

3. **Результат:**
   - Каждый push в `main` → автоматический деплой
   - Каждый pull request → preview deployment
   - URL: `your-site-name.netlify.app`

### Сценарий 3: Netlify CLI (для продвинутых)

**Когда использовать:**
- Хотите деплоить из терминала
- Нужен preview deployment перед production
- Локальная разработка с `netlify dev`

**Шаги:**
1. `npm install -g netlify-cli`
2. `netlify login` (откроется браузер для авторизации)
3. `netlify init` в папке проекта
4. `netlify deploy` (draft) или `netlify deploy --prod` (production)

### Таблица "Какой метод выбрать"

| Сценарий | Метод | Причина |
|----------|-------|---------|
| Показать клиенту демо прайс-листа | **Drop** | Быстро, не нужен Git |
| Production прайс-лист с автообновлением | **GitHub** | Автоматический деплой, версионность |
| Internal dashboard только для команды | **Drop + Password** | Быстро + защита паролем |
| Лендинг с формой заявок | **GitHub** | Нужны updates, Netlify Forms |
| Телеграм бот с webhooks | **GitHub + Functions** | Serverless functions, environment variables |
| Тестирование перед продакшеном | **CLI** | Draft deploys, preview URLs |
| Локальная разработка с Functions | **CLI** | `netlify dev` эмулирует production |

> Подробнее о бизнес-кейсах и детальном сравнении методов: `references/business-cases.md`

---

## 3. Netlify Drop — руководство

### Что такое Netlify Drop

Drag-and-drop интерфейс для мгновенного деплоя статических сайтов. Вы буквально перетаскиваете папку в браузер, и через 10 секунд получаете живой URL.

**Ограничения:**
- Только статические файлы (HTML, CSS, JS, images)
- Нет build процесса (не подходит для React, Vue, если не собрать локально)
- Нет Serverless Functions
- Нет автоматических обновлений (только ручной re-drop)

**Преимущества:**
- Мгновенный деплой (нет регистрации, настройки, конфигурации)
- Идеально для демо, прототипов, тестов
- Можно апдейтить: перетащите папку снова на тот же сайт

### Пошаговая инструкция

**Шаг 1: Подготовьте папку** — ваш проект должен содержать `index.html` в корне. Проверка: откройте `index.html` в браузере локально. Всё работает? Готово к деплою.

**Шаг 2: Откройте** https://app.netlify.com/drop (или Dashboard → "Add new site" → "Deploy manually")

**Шаг 3: Перетащите** всю папку (не отдельные файлы!) в область "Drag and drop your site"

**Шаг 4: Получите URL** — рандомное имя `magnificent-fairy-abc123.netlify.app`. Можно изменить: Site Settings → Site Details → Change site name

**Шаг 5 (КРИТИЧЕСКИЙ): Password Protection** — если это internal tool, демо с конфиденциальными данными или тестовая версия: Site Settings → Visitor Access → Password Protection → Set Password

**Шаг 6: Обновление** — Netlify Dashboard → Deploys → "Drag and drop" → перетащите обновлённую папку. URL остаётся прежним.

### Когда использовать Drop

**Идеальные сценарии:**
- Срочное демо клиенту (за 2 минуты: обновили дизайн → Drop → отправили URL)
- Тестирование на реальных устройствах (localhost не открыть на телефоне)
- Одноразовые лендинги (акция на 3 дня)
- Internal tools без чувствительных данных (калькулятор комиссий, инструкция для гидов)
- Internal dashboards **с password protection** (сводка бронирований, финансовый отчёт)

**НЕ использовать для:**
- Production сайтов, которые будут обновляться (→ GitHub Integration)
- Проектов с build процессом: React, Vue (→ GitHub/CLI)
- Сайтов с Serverless Functions (Drop не поддерживает)
- Когда нужна история деплоев (Drop не хранит предыдущие версии)

### Troubleshooting Drop

| Проблема | Причина | Решение |
|----------|---------|---------|
| 404 Not Found | `index.html` не в корне папки | Перетаскивайте папку где `index.html` в корне |
| Изображения не загружаются | Абсолютные пути (`C:/Users/...`) | Используйте относительные: `images/logo.png` |
| CSS/JS не применяются | Неправильные пути к файлам | Проверьте что файлы рядом с `index.html` |
| SPA 404 на роутах | React/Vue routing не настроен | Добавьте файл `_redirects`: `/* /index.html 200` |

> Примеры HTML для Drop (прайс-лист, dashboard, обновление): `references/code-examples.md`

---

## 4. GitHub Integration

### Почему это лучший выбор для production

**Автоматический деплой:**
- Push в `main` → автоматический production deploy
- Merge PR → новый deploy за минуту
- Rollback → один клик в Netlify Dashboard

**Preview Deployments:**
- Каждый Pull Request → уникальный preview URL
- Тестируйте изменения до merge
- Показывайте клиенту новые фичи без риска

**Build процесс:**
- React, Vue, Svelte, Next.js → собирается автоматически
- TypeScript, SASS, PostCSS → всё из коробки
- Environment variables для API ключей

**Serverless Functions:**
- `/netlify/functions/` → автоматически деплоятся
- Webhooks, API интеграции, scheduled tasks

**История деплоев:**
- Каждый deploy сохраняется, можно откатиться к любой версии

### Подключение GitHub репозитория

1. **Создайте репозиторий:** `gh repo create my-project --public --source=. --push`
2. **Подключите к Netlify:** Dashboard → "Add new site" → "Import from GitHub" → авторизуйте Netlify → выберите репозиторий
3. **Настройте Build Settings:**

| Фреймворк | Build command | Publish directory |
|-----------|---------------|-------------------|
| **Статический HTML** | (пустым) | `.` |
| **React (CRA)** | `npm run build` | `build` |
| **Vue / Vite** | `npm run build` | `dist` |
| **Next.js** | `npm run build` | `.next` |
| **Svelte** | `npm run build` | `public` |

4. **Deploy Site** → через 1-3 минуты получите URL
5. **Переименуйте:** Site Settings → Change site name

### Автоматический деплой при push

1. Изменения локально → `git add . && git commit -m "Update" && git push`
2. GitHub webhook → Netlify запускает build
3. Через 30-60 секунд новая версия на production

**Отслеживание:** Netlify Dashboard → Deploys → "Building" → "Deploying" → "Published"
**Уведомления:** Email ("Deploy succeeded"/"Deploy failed"), Slack/Discord webhooks

### Branch Deployments

Каждая ветка может иметь свой деплой: `branch-name--my-project.netlify.app`

**Когда использовать:**
- Staging environment: `staging` → `staging--my-project.netlify.app`
- Feature testing: `feature/new-design` → `feature-new-design--my-project.netlify.app`

**Включение:** Site Settings → Build & Deploy → Branch deploys: "All" или отдельные ветки.

> Детали: Build hooks, Deploy contexts, netlify.toml: `references/configuration-guide.md`
> Пример React прайс-листа пошагово: `references/code-examples.md`

---

## 5. Netlify CLI

### Установка и настройка

```bash
npm install -g netlify-cli    # Установка (требуется Node.js 14+)
netlify login                 # Авторизация (откроется браузер)
netlify link                  # Связать с существующим сайтом (из списка)
netlify init                  # Создать новый сайт
```

### Основные команды

| Команда | Описание |
|---------|----------|
| `netlify dev` | Локальный сервер с эмуляцией production (Functions, Redirects, Env Vars) |
| `netlify deploy` | Draft deployment (preview URL, не затрагивает production) |
| `netlify deploy --prod` | Production deployment |
| `netlify build` | Локальный build (как на CI, для debugging) |
| `netlify functions:list` | Список functions |
| `netlify functions:create` | Создать новую function из шаблона |
| `netlify functions:invoke name` | Запустить function локально |
| `netlify env:list` | Список environment variables |
| `netlify env:set KEY value` | Добавить переменную |
| `netlify env:unset KEY` | Удалить переменную |
| `netlify open:site` | Открыть сайт в браузере |
| `netlify open:admin` | Открыть admin панель |
| `netlify logs:function name` | Логи function |
| `netlify status` | Информация о проекте (site name, URL, repo) |

### netlify dev для локальной разработки

Запускает локальный сервер на порту 8888 с полной эмуляцией production:
- Serverless Functions: `/.netlify/functions/` работают локально
- Redirects & Rewrites из `_redirects` или `netlify.toml`
- Environment Variables из Netlify Dashboard (без `.env` файла!)

**Зачем вместо `npm start`:** тестировать Functions локально, проверять redirects до деплоя, использовать env vars из Netlify. Изменения в function коде → hot reload.

### Preview Deployments с CLI

1. `netlify deploy` → получаете Draft URL: `https://abc123--my-project.netlify.app`
2. Отправляете клиенту URL для проверки
3. Клиент одобрил → `netlify deploy --prod`

> Практические примеры CLI workflow, branch deployments: `references/configuration-guide.md`

---

## 6. Environment Variables

### Что это и зачем

Пары ключ-значение, хранящиеся на сервере Netlify. API ключи не в коде (не попадут в Git), разные ключи для production/staging, можно менять без редеплоя кода.

### Как добавить через Dashboard

1. Site Settings → Environment variables → "Add a variable"
2. Key: `TELEGRAM_BOT_TOKEN`, Value: `123456:ABC...`
3. Scopes: Production + Deploy Previews (обычно оба)
4. **Важно:** Изменения применяются **только к новым деплоям**. Для текущего: Deploys → "Trigger deploy" → "Clear cache and deploy site"

### Что хранить

**Обязательно:** API ключи (Google Sheets, Telegram, SendGrid), Database URLs, OAuth секреты, JWT secrets, Webhook URLs.
**Опционально:** API endpoints, Feature flags, конфигурация (лимиты).
**НЕ хранить:** публичные данные (лучше hardcode), бинарные данные.

### Ключевое правило безопасности

**Frontend переменные** (с prefix `REACT_APP_`, `VITE_`, `NEXT_PUBLIC_`) → встраиваются в bundle → **не храните секреты!** Любой может увидеть их в DevTools.

**Backend переменные** (без prefix) → доступны только в Serverless Functions → безопасно для секретов.

**Правильный паттерн:** секретный API key хранится в environment variable без prefix → Serverless Function использует его для запроса к API → frontend вызывает Function через `/.netlify/functions/...` → клиент не видит ключ.

> Доступ из кода по фреймворкам (React, Vite, Next.js), Build vs Runtime, локальная разработка с .env: `references/configuration-guide.md`

---

## 7. Serverless Functions

### Что такое Serverless Functions

Бэкенд код, который запускается на серверах Netlify без необходимости настраивать сервер.

**Преимущества:**
- Не нужен VPS, Docker, nginx — Netlify управляет инфраструктурой
- Автоматический скейлинг: 1 запрос или 1000 — Netlify справится
- Бесплатный план: 125,000 requests/месяц (покрывает большинство малых бизнесов)
- CORS настроен автоматически
- Functions доступны на `/.netlify/functions/function-name`

### Структура: netlify/functions/

```
your-project/
├── index.html
└── netlify/
    └── functions/
        ├── hello.js          → /.netlify/functions/hello
        ├── telegram-webhook.js → /.netlify/functions/telegram-webhook
        └── fetch-prices.js   → /.netlify/functions/fetch-prices
```

**Важно:** папка **MUST** называться `netlify/functions/` (не `functions/`). Каждый файл = отдельная function. Имя файла = endpoint path.

### Минимальная function

```javascript
// netlify/functions/hello.js
exports.handler = async (event, context) => {
  return {
    statusCode: 200,
    body: JSON.stringify({ message: 'Hello, World!' }),
  };
};
```

**Вызов:** `curl https://your-site.netlify.app/.netlify/functions/hello`

### Лимиты

| План | Requests/месяц | Timeout | Memory |
|------|----------------|---------|--------|
| **Бесплатный** | 125,000 | 10 сек | 1024 MB |
| **Pro ($19/мес)** | 2,000,000 | 26 сек | 1024 MB |

Для туристического бизнеса бесплатного плана достаточно (125k = ~4000 req/день).

**Pro план** добавляет Background Functions (до 15 минут) для long-running tasks.

> Полные примеры: Telegram webhook, Google Sheets API, форма заявки, email (SendGrid), проверка дат, Event/Context объекты: `references/code-examples.md`

---

## 8. Redirects и Rewrites

### Файл _redirects

Файл в publish directory, который настраивает URL redirects и rewrites:

```
from_path    to_path    status_code
```

**Где разместить:**
- Статический сайт: в корне публикуемой папки
- React CRA: `public/_redirects`
- Vite: `public/_redirects`
- Next.js: не нужен (Next.js управляет роутингом сам)

**Приоритет:** Netlify обрабатывает redirects сверху вниз. Первое совпадение = применяется.

### Ключевые сценарии

**SPA Routing Fix (React, Vue):**

Проблема: `/about` → 404 (Netlify ищет файл `about.html`).
Решение: все запросы перенаправляются на `index.html`, React Router обрабатывает URL:

```
/*    /index.html   200
```

**Важно:** status code **200** (rewrite, не redirect). Эта строка должна быть **последней** в файле.

**Проксирование API (решает CORS):**

Проблема: внешний API блокирует запросы с вашего домена (CORS error).
Решение: Netlify проксирует запрос:

```
/api/*    https://api.example.com/:splat   200
```

Как работает: браузер запрашивает `/api/data` (same-origin, нет CORS) → Netlify проксирует на `https://api.example.com/data` → возвращает ответ. Браузер не знает о внешнем API.

**Simple redirect:**
```
/old-page    /new-page    301
```

### Troubleshooting Redirects

| Проблема | Решение |
|----------|---------|
| Redirects не работают | Проверьте: `_redirects` в `build/` или `dist/` после build. Пробелы (не табы). Ctrl+Shift+R. |
| SPA routing не работает | `/* /index.html 200` должен быть в конце файла (не перед другими redirects) |
| Proxy не убирает CORS | Используйте финальный URL API (не redirect URL) |

> netlify.toml, условные redirects (country, language), A/B testing, headers: `references/configuration-guide.md`

---

## 9. Custom Domains

### Подключение домена

1. **Купите домен** (Namecheap, Cloudflare Registrar, Google Domains)
2. **Добавьте в Netlify:** Domain Settings → Add custom domain → `dxbtours.com`
3. **Настройте DNS:**
   - **Netlify DNS (рекомендуется):** Netlify покажет nameservers → добавьте их у регистратора. Проще, автоматический HTTPS.
   - **External DNS:** Добавьте A record (75.2.60.5) и CNAME (www → your-site.netlify.app) у регистратора. Больше контроля.
4. **Дождитесь HTTPS:** автоматический Let's Encrypt сертификат (обычно < 10 минут)
5. **Force HTTPS:** Domain Settings → HTTPS → Force HTTPS: ON

### HTTPS (Let's Encrypt)

Netlify предоставляет бесплатный HTTPS:
- Let's Encrypt сертификат
- Автоматическое обновление (каждые 90 дней)
- Никаких настроек не требуется
- Нужен для SEO (Google ранжирует HTTPS выше) и современных API (Geolocation, Camera)

### Subdomain деплой

Можно деплоить разные проекты на subdomains:
- `dxbtours.com` → главный сайт
- `blog.dxbtours.com` → блог (отдельный Netlify сайт)
- `dashboard.dxbtours.com` → internal dashboard (с password protection)

> Детальные инструкции DNS, DNS records таблица, практический пример подключения домена: `references/configuration-guide.md`

---

## 10. Netlify Forms

### Создание форм

Добавьте атрибут `netlify` к `<form>` — Netlify автоматически обрабатывает submissions:

```html
<form name="contact" method="POST" netlify>
  <label>Имя: <input type="text" name="name" required /></label>
  <label>Email: <input type="email" name="email" required /></label>
  <label>Сообщение: <textarea name="message" required></textarea></label>
  <button type="submit">Отправить</button>
</form>
```

Netlify: распознаёт атрибут при деплое → создаёт endpoint → сохраняет данные в Dashboard.

**Submissions:** Netlify Dashboard → Forms → выберите форму.

### Обработка Submissions

**Custom success page:**
```html
<form name="contact" method="POST" netlify action="/thank-you">
```
При отправке → редирект на `/thank-you`.

**Spam protection:**
```html
<form name="contact" netlify netlify-honeypot="bot-field">
  <input type="hidden" name="form-name" value="contact" />
  <p style="display:none">
    <label>Don't fill this out: <input name="bot-field" /></label>
  </p>
  ...
</form>
```

### Notifications

- **Email:** Site Settings → Forms → Form notifications → Email notification → ваша почта → "Новая заявка с сайта"
- **Webhook:** → Outgoing webhook → URL Serverless Function → отправка в Telegram/Slack

### Лимиты

| План | Submissions/месяц |
|------|--------------------|
| Бесплатный | 100 |
| Pro ($19/мес) | 1,000 |

> Полная форма заявки на экскурсию, AJAX форма, thank you page, webhook → Telegram: `references/code-examples.md`

---

## 11. Типичные ошибки

### Password на Drop деплое

**Проблема:** Drop создаёт публичный URL. Если это internal tool, посторонние могут зайти.
**Решение:** Site Settings → Visitor Access → Password Protection → Set Password.

### CORS ошибки

**Решение 1: Proxy через _redirects:**
```
/api/*    https://api.example.com/:splat   200
```
Фронтенд вызывает `/api/data` вместо `https://api.example.com/data`.

**Решение 2: Serverless Function** — function вызывает API на сервере (нет CORS), frontend вызывает function.

### Redirects не работают

**Причина 1:** `_redirects` не в publish directory. Убедитесь: файл в `build/` или `dist/` после build. Для React: `public/_redirects`.

**Причина 2:** Синтаксис неправильный. Формат: `/from /to status` с пробелами (не табы).

**Причина 3:** Кэш браузера. Ctrl+Shift+R (hard refresh).

### Functions не деплоятся

| Причина | Решение |
|---------|---------|
| Неправильная папка | Только `netlify/functions/`, не `functions/` или `lambda/` |
| Нет `exports.handler` | Должно быть `exports.handler = async (event) => { ... };` |
| Dependencies не установлены | Добавьте в `package.json`, Netlify установит автоматически |

**Debugging:** Deploys → Function logs или `netlify logs:function function-name`.

> Больше решений проблем: `references/troubleshooting.md`

---

## 12. Дополнительные ресурсы

### Ссылки на references/

- **business-cases.md** — бизнес-кейсы, сценарии использования, детальная таблица сравнения методов
- **code-examples.md** — развёрнутые примеры кода: HTML для Drop, React прайс-лист, Serverless Functions (Telegram, Google Sheets, SendGrid, формы), Netlify Forms
- **configuration-guide.md** — Build Settings для фреймворков, Environment Variables доступ из кода, netlify.toml, DNS настройки, CLI workflows
- **faq.md** — часто задаваемые вопросы
- **troubleshooting.md** — детальный troubleshooting
- **cheatsheet.md** — шпаргалка команд
- **deployment-comparison.md** — детальное сравнение методов деплоя
- **advanced-features.md** — продвинутые возможности
- **security-guide.md** — руководство по безопасности

### Официальная документация

| Раздел | URL |
|--------|-----|
| Netlify Docs | https://docs.netlify.com |
| Build & Deploy | https://docs.netlify.com/configure-builds/overview/ |
| Serverless Functions | https://docs.netlify.com/functions/overview/ |
| Forms | https://docs.netlify.com/forms/setup/ |
| Redirects | https://docs.netlify.com/routing/redirects/ |
| CLI | https://docs.netlify.com/cli/get-started/ |
| Community Forums | https://answers.netlify.com |
| Discord | https://discord.gg/netlify |
| YouTube | https://youtube.com/@NetlifyApp |
| Netlify Status | https://netlifystatus.com |

---

## Заключение

Этот skill покрывает все основные сценарии деплоя на Netlify для туристического бизнеса:

- **Быстрый старт:** Drop деплой за 30 секунд
- **Production ready:** GitHub Integration с auto-deploy
- **Serverless:** Functions для webhooks и API
- **Безопасность:** Environment Variables и Password Protection
- **SEO:** Custom domains с автоматическим HTTPS
- **Forms:** Сбор заявок без бэкенда

**Следующие шаги:**
1. Задеплойте тестовый проект через Drop
2. Подключите GitHub репозиторий
3. Добавьте Serverless Function для интеграции с API
4. Настройте custom domain

**Вопросы?** См. `references/faq.md` или официальную документацию.

---

**Конец SKILL.md**
