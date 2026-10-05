# FAQ — Часто задаваемые вопросы о Vercel

## Общие вопросы

### 1. Что такое Vercel и для чего он нужен?

Vercel — это облачная платформа для деплоя и хостинга веб-приложений с фокусом на фронтенд. Автоматически собирает и публикует проекты из Git-репозиториев, предоставляет serverless functions, CDN, SSL-сертификаты и preview deployments из коробки.

**Основные преимущества:**
- ✅ Нулевая конфигурация для Next.js
- ✅ Автоматические preview для каждого PR
- ✅ Глобальный CDN
- ✅ Edge Functions с минимальной задержкой
- ✅ Бесплатный SSL

### 2. Чем Vercel отличается от Netlify?

**Vercel:**
- Оптимизирован под Next.js (разработчики Next.js)
- Лучше для SSR/SSG проектов
- Быстрее сборка
- Мощные Edge Functions
- Нет встроенных форм и авторизации

**Netlify:**
- Универсальная платформа
- Проще интерфейс для новичков
- Есть Drop deploy (drag & drop)
- Встроенные формы и Identity
- Больше плагинов

**Вывод:** Vercel для Next.js и сложных SSR-проектов, Netlify для простых статичных сайтов и быстрого прототипирования.

Детальное сравнение: см. `vercel-vs-netlify.md`

### 3. Когда использовать `vercel` vs `vercel --prod`?

**`vercel` (без флагов):**
- Создаёт preview deployment
- Уникальный URL (например, `my-app-abc123.vercel.app`)
- Для тестирования изменений
- Не влияет на production
- Можно создавать неограниченно

**`vercel --prod`:**
- Деплоит на production домен
- Обновляет `my-app.vercel.app` и кастомные домены
- Используется для финальных релизов
- ⚠️ Применяется к реальным пользователям

**Рекомендуемый workflow:**
1. `vercel` — проверяем изменения
2. Тестируем preview URL
3. `vercel --prod` — публикуем для пользователей

### 4. Как удалить deployment?

**Через CLI:**
```bash
# Список deployments
vercel ls

# Удаление по URL
vercel rm my-app-abc123.vercel.app

# Удаление последнего
vercel rm --safe
```

**Через Dashboard:**
1. Зайти на vercel.com → Проект
2. Deployments → Выбрать нужный
3. ⋮ (три точки) → Delete

**⚠️ Важно:** Production deployment нельзя удалить напрямую — сначала нужно сделать другой deployment production.

### 5. Как откатиться к предыдущей версии?

**Способ 1 — через Dashboard:**
1. Deployments → Выбрать старый deployment
2. ⋮ → Promote to Production

**Способ 2 — через CLI:**
```bash
# Найти deployment
vercel ls

# Сделать его production
vercel alias set old-deployment-url.vercel.app my-app.vercel.app
```

**Способ 3 — через Git:**
```bash
git revert HEAD
git push
# Vercel автоматически задеплоит предыдущее состояние
```

### 6. Можно ли использовать Vercel без Next.js?

✅ **Да!** Vercel поддерживает множество фреймворков:

- React (Create React App, Vite)
- Vue.js (Nuxt, Vite)
- Angular
- Svelte / SvelteKit
- Solid.js
- Astro
- Gatsby
- Статичный HTML/CSS/JS
- И многие другие

**Автоматическое определение:** Vercel сам определяет фреймворк и настраивает сборку.

### 7. Что такое Preview Deployments и как они работают?

Preview Deployments — это автоматические деплои для каждой ветки или Pull Request.

**Как работает:**
1. Делаете commit в ветку
2. Push на GitHub/GitLab/Bitbucket
3. Vercel автоматически деплоит
4. Получаете уникальный URL
5. В PR появляется комментарий с preview ссылкой

**Преимущества:**
- ✅ Тестирование без влияния на production
- ✅ Показ изменений команде/клиенту
- ✅ Каждый PR имеет свою изолированную версию
- ✅ Автоматическое удаление после мерджа

### 8. Что такое Edge Functions?

Edge Functions — это serverless функции, которые выполняются на серверах близко к пользователю (на краю CDN сети).

**Отличия от обычных Serverless Functions:**
- ⚡ Меньше latency (ближе к пользователю)
- ⚡ Быстрее cold start
- ⚠️ Ограничения по runtime (нет Node.js API)
- ⚠️ Время выполнения: до 30 секунд

**Когда использовать:**
- Персонализация контента
- A/B тесты
- Geo-routing
- Auth middleware
- Rate limiting

**Пример:** `middleware.ts` в Next.js автоматически становится Edge Function.

### 9. Как настроить CI/CD с Vercel?

**Автоматический способ (рекомендуется):**
1. Подключить Git репозиторий
2. Vercel сам настроит webhooks
3. Автоматический деплой при push

**Ручная настройка через GitHub Actions:**
```yaml
name: Deploy to Vercel
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: npm install --global vercel
      - run: vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

**Environment variables:**
- `VERCEL_TOKEN` — из vercel.com/account/tokens
- `VERCEL_ORG_ID` — из `.vercel/project.json`
- `VERCEL_PROJECT_ID` — из `.vercel/project.json`

### 10. Каковы лимиты Free Tier?

**Vercel Hobby (бесплатный):**
- ✅ 100 GB bandwidth в месяц
- ✅ Неограниченные deployments
- ✅ 100 GB-hours serverless function execution
- ✅ 1000 Edge Functions invocations/день
- ✅ 12 serverless functions
- ✅ Unlimited preview deployments
- ✅ Коммерческое использование разрешено

**Ограничения:**
- ❌ Максимум 1 concurrent build
- ❌ 10 секунд timeout serverless functions
- ❌ 50 MB размер функции

**Когда нужен Pro:**
- Больше traffic
- Команда > 1 человека
- 60 секунд timeout
- Расширенная аналитика

### 11. Как работать с environment variables?

**Создание через CLI:**
```bash
# Добавить переменную
vercel env add API_KEY

# Development
vercel env add API_KEY development

# Preview
vercel env add API_KEY preview

# Production
vercel env add API_KEY production

# Все окружения
vercel env add API_KEY production preview development
```

**Скачать в локальный проект:**
```bash
vercel env pull .env.local
```

**⚠️ Важно:**
- Переменные применяются только при новом deployment
- Для клиента нужен префикс `NEXT_PUBLIC_` (Next.js)
- Secrets лучше добавлять через Dashboard

### 12. Можно ли использовать кастомный домен?

✅ **Да!** Даже в Free Tier.

**Добавление домена:**
```bash
vercel domains add example.com
```

**Через Dashboard:**
1. Project Settings → Domains
2. Add → Ввести домен
3. Настроить DNS записи у регистратора:
   - A запись: `76.76.21.21`
   - CNAME запись: `cname.vercel-dns.com`

**Поддомены:**
```bash
vercel domains add blog.example.com
```

**SSL:** Автоматически выпускается Let's Encrypt сертификат.

### 13. Как посмотреть логи deployment?

**Через CLI:**
```bash
# Логи production
vercel logs

# Логи конкретного deployment
vercel logs my-app-abc123.vercel.app

# Follow mode (real-time)
vercel logs --follow
```

**Через Dashboard:**
1. Project → Deployments → Выбрать deployment
2. Building / Runtime Logs

**Типы логов:**
- Build logs — процесс сборки
- Function logs — вывод serverless functions
- Edge logs — Edge Functions (только Pro)

### 14. Можно ли развернуть монорепозиторий?

✅ **Да!** Vercel поддерживает monorepos.

**Настройка:**
```json
// vercel.json
{
  "buildCommand": "cd apps/web && npm run build",
  "outputDirectory": "apps/web/dist"
}
```

**Или через Dashboard:**
1. Project Settings → General
2. Root Directory → `apps/web`

**Популярные инструменты:**
- Turborepo (от Vercel)
- Nx
- Lerna
- Yarn workspaces

### 15. Как отключить автоматический деплой?

**Для конкретной ветки:**
```bash
# Dashboard: Project Settings → Git
# Ignored Build Step → Выбрать ветки
```

**Через vercel.json:**
```json
{
  "github": {
    "enabled": false
  }
}
```

**Для конкретного commit:**
```bash
git commit -m "WIP: not ready [skip ci]"
```

Используйте `[skip ci]` или `[vercel skip]` в commit message.

### 16. Что делать если deployment завис?

**Шаги:**
1. Подождать 10-15 минут (иногда долгая сборка)
2. Проверить Vercel Status: vercel.com/status
3. Отменить через Dashboard (⋮ → Cancel)
4. Попробовать заново:
   ```bash
   vercel --force
   ```

**Если не помогает:**
- Очистить cache: Project Settings → Clear Cache
- Проверить build логи на ошибки
- Контакт support (Pro план)

### 17. Можно ли использовать Docker?

❌ **Нет**, Vercel не поддерживает Docker напрямую.

**Альтернативы:**
- Использовать Vercel Serverless Functions
- Для Docker: Railway, Render, Fly.io, AWS/GCP/Azure
- Для статики: продолжать использовать Vercel

### 18. Как работает кэширование?

**Автоматическое кэширование:**
- ✅ Статичные файлы (images, CSS, JS)
- ✅ Build cache (node_modules, etc)
- ✅ CDN cache по всему миру

**Настройка через headers:**
```json
// vercel.json
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "s-maxage=60, stale-while-revalidate"
        }
      ]
    }
  ]
}
```

**Очистка cache:**
- Новый deployment автоматически инвалидирует cache
- Project Settings → Clear Cache

### 19. Поддерживаются ли scheduled jobs (cron)?

✅ **Да!** Через Vercel Cron (Pro план) или внешние сервисы.

**Vercel Cron (Pro):**
```json
// vercel.json
{
  "crons": [
    {
      "path": "/api/cleanup",
      "schedule": "0 0 * * *"
    }
  ]
}
```

**Бесплатные альтернативы:**
- GitHub Actions
- EasyCron
- cron-job.org
- AWS EventBridge

### 20. Как мигрировать с другого хостинга?

**Общие шаги:**
1. Подготовить Git репозиторий
2. Добавить `vercel.json` (если нужна кастомная настройка)
3. `vercel` — тестовый деплой
4. Проверить работу сайта
5. Настроить environment variables
6. `vercel --prod`
7. Обновить DNS записи домена

**Миграция с конкретных платформ:**
- Netlify → см. `vercel-vs-netlify.md`
- Heroku → заменить Procfile на Serverless Functions
- GitHub Pages → просто подключить репозиторий

**⚠️ Важно:** Сначала проверьте на preview URL, затем переключайте DNS.
