---
name: vercel-деплой
description: "Полное руководство по деплою и хостингу приложений на Vercel - serverless, Next.js, CDN, preview deployments"
---
# Vercel Деплой — Полное руководство

## 1. Введение

### Что такое Vercel

Vercel — это облачная платформа для деплоя и хостинга frontend-приложений и serverless функций. Изначально известная как Zeit Now, платформа была создана командой, которая разработала Next.js, что делает Vercel наиболее оптимизированным решением для деплоя Next.js приложений.

Vercel автоматизирует процесс сборки, деплоя и масштабирования веб-приложений, предоставляя глобальную CDN сеть, serverless функции и автоматическое HTTPS. Платформа поддерживает все популярные фреймворки: React, Vue, Angular, Svelte, а также статичные сайты и SPA.

### Почему Vercel

**Ключевые преимущества:**

- **Оптимизация для Next.js:** Встроенная поддержка ISR (Incremental Static Regeneration), Image Optimization, Edge Functions
- **Edge Network:** Глобальная CDN с автоматическим распределением контента
- **Zero Config:** Автоматическое определение фреймворка и настроек сборки
- **Preview Deployments:** Уникальный URL для каждого PR с автоматическим деплоем
- **Serverless Functions:** Простое создание API endpoints без настройки серверов
- **Мгновенные роллбэки:** Откат к любой предыдущей версии за секунды
- **Автоматический HTTPS:** SSL сертификаты для всех доменов
- **Developer Experience:** Интуитивный интерфейс и мощный CLI

### Ключевые возможности

| Возможность | Описание |
|-------------|----------|
| **Instant Rollbacks** | Откат к любой версии одним кликом |
| **Edge Functions** | Запуск кода на edge серверах (минимальная задержка) |
| **Analytics** | Встроенная аналитика производительности |
| **Image Optimization** | Автоматическая оптимизация изображений (Next.js) |
| **ISR Support** | Инкрементальная статическая регенерация |
| **Git Integration** | Автоматический деплой при push в репозиторий |
| **Environment Variables** | Управление переменными окружения для разных сред |
| **Custom Domains** | Неограниченное количество доменов |

### Когда Vercel, когда Netlify

**Vercel:** Next.js, Edge Functions, быстрый cold start, ISR, Image Optimization, глобальная аудитория.
**Netlify:** Сложные build hooks и плагины, гибкие редиректы, Netlify CMS, Split Testing, Gatsby.
**Оба:** React, Vue, Angular, статичные сайты, бесплатные планы, serverless, custom domains.

-> Подробное сравнение: `references/vercel-vs-netlify.md`

---

## 2. Quick Start Guide

### Три способа деплоя

| Метод | Когда использовать | Автоматизация | Сложность |
|-------|-------------------|---------------|-----------|
| **GitHub Integration** | Постоянный проект, командная работа | Полная | Низкая |
| **Vercel CLI** | Быстрый деплой, тестирование | Ручная | Средняя |
| **Git Integration** | GitLab, Bitbucket проекты | Полная | Низкая |

### Способ 1: GitHub Integration (Рекомендуется)

1. Зайдите на https://vercel.com -> "New Project" -> "Import Git Repository"
2. Авторизуйте Vercel в GitHub, выберите репозиторий
3. Настройте Project Name, Framework Preset, Root Directory (автоопределение)
4. Добавьте Environment Variables (опционально)
5. Нажмите "Deploy" -> получите production URL (`my-app.vercel.app`)

**Автоматический workflow:**
```
git push origin main    -> Vercel деплоит в Production
git push origin feature -> Vercel создаёт Preview Deployment
```

### Способ 2: Vercel CLI

```bash
npm install -g vercel    # Установка
vercel login             # Авторизация
cd your-project && vercel       # Preview deployment
vercel --prod            # Production deployment
```

**Важно:** `vercel` без флагов создаёт preview, `vercel --prod` деплоит в production!

### Способ 3: Git Integration (GitLab/Bitbucket)

Dashboard -> New Project -> Import Git Repository -> выберите GitLab или Bitbucket. Функции аналогичны GitHub Integration.

### Первые шаги после деплоя

1. Проверьте deployment по URL
2. Настройте Custom Domain: Dashboard -> Settings -> Domains
3. Добавьте Environment Variables: Dashboard -> Settings -> Environment Variables
4. Настройте Team: Dashboard -> Team Settings

---

## 3. Установка и настройка CLI

```bash
# Установка (любой менеджер пакетов)
npm install -g vercel     # npm
pnpm add -g vercel        # pnpm (быстрее)
yarn global add vercel    # yarn

# Авторизация
vercel login              # Откроет браузер для подтверждения
vercel login --github     # Прямая авторизация через GitHub

# Проверка
vercel --version          # Vercel CLI 28.x.x
vercel whoami             # your-username
```

### Методы авторизации

| Метод | Команда | Когда использовать |
|-------|---------|-------------------|
| **Email** | `vercel login` | Простая авторизация |
| **GitHub** | `vercel login --github` | Если используете GitHub |
| **GitLab** | `vercel login --gitlab` | Если используете GitLab |
| **Bitbucket** | `vercel login --bitbucket` | Если используете Bitbucket |

### Связывание проекта

```bash
cd your-project
vercel link
```

Vercel создаст папку `.vercel/` с конфигурацией (`project.json` с ID проекта).

**Важно:** Добавьте `.vercel` в `.gitignore`:
```bash
echo ".vercel" >> .gitignore
```

### Проверка установки

```bash
vercel --version     # Ожидаемый вывод: Vercel CLI 28.x.x
vercel whoami        # Ожидаемый вывод: your-username
vercel ls            # Список deployments
vercel               # Тестовый деплой (preview)
```

-> Полный CLI справочник: `references/cli-reference.md`

---

## 4. CLI Workflow (КРИТИЧЕСКАЯ СЕКЦИЯ)

### Preview vs Production

| Параметр | Preview | Production |
|----------|---------|------------|
| **Команда** | `vercel` | `vercel --prod` |
| **URL** | Уникальный хеш | Production домен |
| **Env Vars** | Preview vars | Production vars |
| **Git** | Каждый commit/PR | Только main/master |
| **Количество** | Неограниченно | Один активный |

### Визуальный workflow

```
Локальная разработка
  git commit -> vercel -> Preview (my-app-abc123.vercel.app)
                            |
                        Тестирование OK?
                            |
                vercel --prod -> Production (my-app.vercel.app)
```

### Основные команды

```bash
vercel                    # Preview deployment
vercel --prod             # Production deployment
vercel logs <url>         # Логи deployment
vercel logs my-app --prod # Логи production
vercel logs my-app --prod --limit 100    # Последние 100 строк
vercel logs my-app --prod --since 1h     # За последний час
vercel ls                 # Список deployments
vercel ls --prod          # Только production
vercel inspect <url>      # Детали deployment (build time, git info, env)
vercel rm <url>           # Удаление deployment (production нельзя удалить!)
vercel project ls         # Список проектов
vercel --open             # Деплой и открыть в браузере
```

### Детали deployment (inspect)

```bash
vercel inspect https://my-app-abc123.vercel.app
```

Показывает: ID deployment, время сборки, commit hash, framework detection, build command, environment variables.

-> Полный справочник команд: `references/cli-reference.md`
-> Быстрая шпаргалка: `references/cheatsheet.md`

---

## 5. vercel.json конфигурация

Файл `vercel.json` позволяет тонко настроить поведение deployments. Для многих проектов он НЕ требуется (zero config).

### Базовая структура

```json
{
  "version": 2,
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "redirects": [],
  "rewrites": [],
  "headers": []
}
```

### Redirects и Rewrites (краткий обзор)

**Redirects** (301/302) -- перенаправление с изменением адресной строки:
```json
{ "source": "/old-page", "destination": "/new-page", "permanent": true }
```

**Rewrites** -- проксирование БЕЗ изменения адресной строки:
```json
{ "source": "/api/:path*", "destination": "https://api.example.com/:path*" }
```

### Headers и Environment Variables

```json
{
  "headers": [
    { "source": "/(.*)", "headers": [
      { "key": "X-Content-Type-Options", "value": "nosniff" }
    ]}
  ],
  "env": { "API_URL": "https://api.example.com" },
  "build": { "env": { "NODE_VERSION": "18" } }
}
```

**Для секретов используйте CLI:** `vercel env add SECRET_KEY`

### Build Configuration

```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "outputDirectory": "dist"
}
```

**Параметры:**
- `framework`: Автоопределение или ручная установка
- `buildCommand`: Команда сборки (переопределяет автоматическую)
- `devCommand`: Команда для локальной разработки
- `installCommand`: Команда установки зависимостей
- `outputDirectory`: Папка с результатом сборки

**Важно:** Next.js проекты обычно НЕ требуют `vercel.json`, конфигурация делается в `next.config.js`.

-> Подробные JSON-примеры (redirects, rewrites, headers, security, CORS, SPA, API): `references/vercel-json-examples.md`

---

## 6. Serverless Functions

Все файлы в папке `api/` автоматически становятся serverless функциями:

```
api/
  hello.js          -> /api/hello
  users.js          -> /api/users
  products/[id].js  -> /api/products/123
```

### Базовый пример (Node.js)

```javascript
// api/hello.js
export default function handler(req, res) {
  res.status(200).json({ message: 'Hello from Vercel!' });
}

// api/users.js — с параметрами и методами
export default function handler(req, res) {
  const { method, query, body } = req;
  if (method === 'GET') {
    res.status(200).json({ userId: query.id, name: 'John Doe' });
  } else if (method === 'POST') {
    res.status(201).json({ message: 'User created', ...body });
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}
```

### Environment Variables в Functions

```javascript
const apiKey = process.env.API_KEY;  // Автоматический доступ
```

### Limits

| Параметр | Free | Pro | Enterprise |
|----------|------|-----|------------|
| **Execution Time** | 10s | 60s | 900s |
| **Memory** | 1024 MB | 3008 MB | 3008 MB |
| **Payload Size** | 5 MB | 5 MB | 5 MB |
| **Invocations** | 100 GB-Hrs | 1000 GB-Hrs | Custom |
| **Concurrent** | 1000 | 1000 | Custom |

**Важные ограничения:**
- Холодный старт (cold start): 50-200ms
- Функции stateless (не сохраняют состояние между вызовами)
- Нет доступа к файловой системе (только /tmp)
- Максимальный размер функции: 50 MB (сжатый)

-> Примеры на TypeScript, Python, Go, Telegram webhook: `references/serverless-examples.md`
-> Детальное руководство по serverless: `references/serverless-guide.md`

---

## 7. Custom Domains и HTTPS

### Подключение через Dashboard

1. Dashboard -> проект -> Settings -> Domains -> "Add"
2. Введите домен (`example.com` или `www.example.com`)
3. Vercel покажет DNS записи для настройки
4. Настройте DNS у вашего провайдера
5. Vercel автоматически проверит DNS и выдаст SSL сертификат

### DNS записи

```
# Root domain
Type: A,     Name: @,    Value: 76.76.21.21

# Subdomain
Type: CNAME, Name: www,  Value: cname.vercel-dns.com

# Wildcard (все поддомены)
Type: CNAME, Name: *,    Value: cname.vercel-dns.com
```

### Через CLI

```bash
vercel domains add example.com
vercel domains inspect example.com    # Проверка DNS
vercel domains rm example.com        # Удаление
```

### Автоматический HTTPS (Let's Encrypt)

- SSL сертификат выдаётся автоматически после валидации DNS
- HTTP автоматически редиректит на HTTPS
- Сертификат обновляется каждые 90 дней
- Несколько доменов для одного проекта: неограниченно

-> Редирект www <-> без www: `references/vercel-json-examples.md`

---

## 8. Preview Deployments

### Как работает (с GitHub Integration)

1. Создаёте ветку, делаете изменения, пушите
2. Vercel автоматически собирает и создаёт preview с уникальным URL
3. При создании PR -- Vercel Bot добавляет комментарий со ссылками
4. Каждый новый commit создаёт новый preview, старые остаются доступны

**Формат URL:**
```
https://[project]-[hash].vercel.app
https://[project]-git-[branch]-[team].vercel.app
```

**Комментарий от Vercel Bot в PR:**
- Статус сборки (success/failed)
- Commit hash
- Ссылка на инспекцию (детали deployment)
- Ссылка на preview URL
- Обновляется при новых commits

### Сценарии использования

**Тестирование фичи:**
```bash
git checkout -b feature/new-auth
# ...делаем изменения...
git push origin feature/new-auth
# Vercel создаёт preview -> тестируем -> вносим правки -> push
```

**Демонстрация клиенту:**
```bash
git checkout -b demo/client-review
git push origin demo/client-review
# Отправляем preview URL клиенту -> фидбек -> правки -> push
```

**A/B тестирование:** Создайте две ветки (variant-a, variant-b), каждая получит свой preview URL для сравнения.

### Preview Environment Variables

Preview deployments используют отдельные env vars (тип "Preview"):
```bash
vercel env add API_URL preview    # Добавить для preview
```

### Управление

- **Автоудаление после merge PR:** Settings -> Git -> "Auto-delete preview deployments after merge"
- **Ручное удаление:** `vercel rm <preview-url>`
- **Срок хранения:** По умолчанию 30 дней (настраивается)

---

## 9. Environment Variables

### Три типа переменных

| Тип | Когда используется | Примеры |
|-----|-------------------|---------|
| **Production** | `vercel --prod` | Production API keys, DB URLs |
| **Preview** | PR, branches | Staging API, Test DB |
| **Development** | `vercel dev` | Local DB, Mock APIs |

### Добавление через Dashboard

1. Откройте проект в Dashboard
2. Settings -> Environment Variables -> "Add"
3. Заполните: Name, Value, выберите среды (Production / Preview / Development)
4. Save

### Управление через CLI

```bash
vercel env add API_KEY              # Интерактивное добавление
vercel env ls                       # Список переменных
vercel env rm API_KEY production    # Удаление
vercel env pull                     # Скачать Development vars в .env.local
```

**Важно:** После `vercel env pull` создаётся файл `.env.local` -- добавьте его в `.gitignore`. Запускайте `vercel env pull` после добавления новых переменных.

### Безопасность (секреты, API ключи)

**НЕ делайте:**
- Не коммитьте секреты в Git (`const API_KEY = 'abc123'`)
- Не передавайте секреты клиенту (`res.json({ apiKey: process.env.API_KEY })`)
- Не используйте одинаковые ключи для production и preview

**Делайте:**
- Используйте `process.env.API_KEY`
- Разные ключи для разных сред
- Проверяйте наличие переменных перед использованием
- Добавьте `.env.local` и `.vercel` в `.gitignore`

```javascript
// Проверка наличия переменной
export default function handler(req, res) {
  const apiKey = process.env.API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: 'API_KEY not configured' });
  }
  // Используйте apiKey для внутренних запросов, НЕ отправляйте клиенту!
}
```

### Безопасность в Next.js

**Серверные переменные (безопасные):** Доступны только в API routes и getServerSideProps.
**Клиентские переменные:** Только с префиксом `NEXT_PUBLIC_` -- видны в браузере, НЕ для секретов!

```javascript
// Серверная (безопасная)
const secret = process.env.SECRET_API_KEY;

// Клиентская (публичная, НЕ для секретов!)
const apiUrl = process.env.NEXT_PUBLIC_API_URL;
```

---

## 10. Типичные ошибки (КРИТИЧЕСКАЯ СЕКЦИЯ)

### Ошибка 1: CLI not found

```bash
vercel: command not found
```
**Решение:** `npm install -g vercel`, перезапустите терминал. Альтернатива: `npx vercel`.

### Ошибка 2: Authentication failed

```bash
Error! Authentication failed. Run `vercel login` to log in.
```
**Решение:** `vercel login` -> подтвердить в браузере. Если не помогло -- удалите `~/.vercel/auth.json` и авторизуйтесь заново.

### Ошибка 3: Build failed

```bash
npm ERR! missing script: build
```
**Решение:** Проверьте `package.json` (должен быть `"build": "next build"`), `vercel logs <url>`, `npm run build` локально.

### Ошибка 4: Environment variables не видны

```javascript
console.log(process.env.API_KEY); // undefined
```
**Для локальной разработки:** `vercel env add API_KEY development` -> `vercel env pull` -> перезапуск dev сервера.
**Для production/preview:** `vercel env ls` -> `vercel env add API_KEY production` -> `vercel --prod`.

-> Ошибки 5-12 (timeout, 404 API, slow builds, Git integration, domains, cold start, out of memory): `references/errors-advanced.md`
-> Полный troubleshooting: `references/troubleshooting.md`

---

## 11. FAQ (краткие ответы)

**1. Vercel vs Netlify?** Vercel для Next.js и Edge Functions, Netlify для плагинов и CMS. -> `references/vercel-vs-netlify.md`

**2. vercel vs vercel --prod?** `vercel` = тестирование (preview), `vercel --prod` = релиз (production). С Git Integration: push в feature -> preview, merge в main -> production.

**3. Как удалить deployment?** `vercel rm <url>`. Production нельзя удалить, пока он активен.

**4. Как откатиться?** Dashboard -> Deployments -> выберите предыдущий -> "Promote to Production". Мгновенно.

**5. Без Next.js?** Да: React, Vue, Angular, Svelte, Gatsby, Astro, статичные HTML/CSS/JS.

**6. Бесплатный план?** Unlimited deployments, 100 GB bandwidth/мес, custom domains, HTTPS, preview. Лимиты: 10s функции, 1024 MB, только personal.

**7. Редирект www?** Через `vercel.json` redirects с условием `has: [{ type: "host", value: "www.example.com" }]`. -> `references/vercel-json-examples.md`

**8. GitLab/Bitbucket?** Да, полная поддержка: автодеплой, preview для MR, комментарии.

**9. Логи ошибок?** `vercel logs <url>`, `vercel logs my-app --prod`, Dashboard -> Deployments -> View Function Logs.

**10. Кэширование?** Автоматическое для статичных файлов, SSG, ISR. API routes НЕ кэшируются по умолчанию.

**11. Analytics?** Vercel Analytics (Pro+): Dashboard -> Analytics -> Enable. Для Next.js:
```javascript
// pages/_app.js
import { Analytics } from '@vercel/analytics/react';
export default function App({ Component, pageProps }) {
  return (<><Component {...pageProps} /><Analytics /></>);
}
```
Также поддерживаются Google Analytics, Plausible и другие.

**12. Cron jobs?** Нет встроенных. Варианты:
- Внешний сервис (EasyCron, cron-job.org) для вызова API endpoint
- GitHub Actions с schedule:

```yaml
# .github/workflows/cron.yml
name: Cron Job
on:
  schedule:
    - cron: '0 0 * * *'  # Каждый день в 00:00
jobs:
  call-vercel:
    runs-on: ubuntu-latest
    steps:
      - name: Call Vercel API
        run: |
          curl -X GET https://your-app.vercel.app/api/cron \
            -H "Authorization: Bearer ${{ secrets.CRON_SECRET }}"
```

**13. Node.js версия?** Через `package.json`: `"engines": { "node": "18.x" }`. Поддерживаются: 14.x, 16.x, 18.x (LTS), 19.x, 20.x.

**14. Пароль на preview?** Password Protection (Pro+) через Dashboard -> Settings -> Deployment Protection. Для Free плана -- собственная авторизация в коде.

**15. WebSocket?** Нет прямой поддержки в Serverless Functions. Альтернативы: Server-Sent Events (SSE), Polling, Pusher, Ably, Socket.io (hosted), отдельный WS сервер на другом хостинге.

-> Расширенный FAQ: `references/faq.md`

---

## 12. Vercel vs Netlify (краткое сравнение)

| Функция | Vercel | Netlify |
|---------|--------|---------|
| **Next.js** | Лучшая оптимизация | Хорошая |
| **Serverless** | Node, Python, Go, Ruby | Node, Go |
| **Execution Time** | 10-900s | 10-26s |
| **Edge Functions** | Да (быстрые) | Да |
| **Build Plugins** | Ограниченные | Обширная экосистема |
| **Split Testing** | Нет | Да (Pro+) |
| **Forms / Identity** | Нет | Да |

**Vercel:** Next.js приложения, SaaS, e-commerce, глобальные веб-приложения, API с высокой нагрузкой.
**Netlify:** Gatsby блоги, статичные сайты с формами, проекты с Netlify CMS, A/B тесты лендингов.

### Миграция между платформами

**Netlify -> Vercel:**
1. Конфигурация: `netlify.toml` -> `vercel.json` (redirects, rewrites)
2. Функции: `netlify/functions/` -> `api/` (изменить формат handler)
3. Environment Variables: экспорт из Netlify Dashboard -> импорт в Vercel

```javascript
// Netlify формат
exports.handler = async (event, context) => {
  return { statusCode: 200, body: JSON.stringify({ message: 'Hello' }) };
};

// Vercel формат
export default function handler(req, res) {
  res.status(200).json({ message: 'Hello' });
}
```

**Vercel -> Netlify:** обратный процесс (vercel.json -> netlify.toml, api/ -> netlify/functions/).

-> Полное сравнение и миграция: `references/vercel-vs-netlify.md`

---

## 13. Ресурсы

### References в этом скилле

| Файл | Содержание |
|------|------------|
| `references/cheatsheet.md` | Быстрая справка по командам |
| `references/cli-reference.md` | Полный CLI справочник |
| `references/faq.md` | Расширенный FAQ |
| `references/troubleshooting.md` | Детальное решение проблем |
| `references/serverless-guide.md` | Руководство по Serverless Functions |
| `references/serverless-examples.md` | Примеры кода (TS, Python, Go, webhook) |
| `references/vercel-json-examples.md` | Примеры vercel.json конфигурации |
| `references/vercel-vs-netlify.md` | Полное сравнение платформ |
| `references/errors-advanced.md` | Расширенные ошибки 5-12 |

### Официальная документация

- Vercel: https://vercel.com/docs
- Next.js: https://nextjs.org/docs
- Примеры: https://vercel.com/templates
- GitHub: https://github.com/vercel

### Community

- Discussions: https://github.com/vercel/vercel/discussions
- Discord: https://discord.gg/vercel
- Next.js Learn: https://nextjs.org/learn

---

## Заключение

**Ключевые takeaways:**
- `vercel` для preview, `vercel --prod` для production
- Environment variables через Dashboard или CLI (`vercel env`)
- Preview Deployments для каждого PR
- Serverless Functions в папке `api/`
- Автоматический HTTPS для всех доменов

```bash
# Быстрый старт
vercel login && vercel          # Preview
vercel --prod                   # Production
vercel env ls                   # Переменные
vercel logs <url>               # Логи
```
