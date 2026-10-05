# EXP-074: Vercel + Prisma v7 deployment: env() not process.env, prisma.config.ts not schema url

**Дата:** 2026-03-01
**Проект:** Tourism CRM (Next.js 16 + Prisma v7 + PostgreSQL)
**Тип:** pattern
**Severity:** high
**times_applied:** 1

## Контекст

Деплой Tourism CRM на Vercel. Prisma v7 радикально изменил конфигурацию подключения к БД. Несколько проблем обнаружены при первой попытке деплоя.

## Проблемы

### 1. `url` в schema.prisma больше не работает
Prisma v7 убрал поддержку `url = env("DATABASE_URL")` из `datasource db {}` в schema.prisma. Конфигурация подключения теперь в `prisma.config.ts`.

### 2. `process.env` не работает в prisma.config.ts на Vercel
Serverless-окружения (Vercel, Cloudflare Workers) загружают переменные окружения иначе. `process.env.DATABASE_URL` может быть `undefined` в момент инициализации Prisma.

**Правильно:** `env("DATABASE_URL")` из `prisma/config`.
**Неправильно:** `process.env.DATABASE_URL`.

```typescript
// prisma.config.ts — ПРАВИЛЬНО
import { defineConfig } from 'prisma/config'
import { env } from 'prisma/config'

export default defineConfig({
  earlyAccess: true,
  datasource: {
    url: env("DATABASE_URL"),  // НЕ process.env.DATABASE_URL
  },
})
```

### 3. `prisma migrate deploy` требует DATABASE_URL
Даже без `url` в schema.prisma, CLI-команда `prisma migrate deploy` нуждается в строке подключения. В Prisma v7 она берётся из `prisma.config.ts`.

### 4. Build command без `prisma generate`
Vercel не запускает `prisma generate` автоматически. Без Prisma Client билд падает.

### 5. Connection string в экспортированных чатах
Экспорт сессий Claude/чатов может содержать plaintext DATABASE_URL с паролем. Если закоммитить — утечка credentials.

### 6. Vercel Free tier — нет выбора региона
Free план Vercel деплоит в iad1 (Washington DC). Для пользователей в Dubai/Middle East это ~200ms latency. Выбор региона доступен только на Pro ($20/мес).

### 7. Neon PostgreSQL — лучший выбор для Vercel
Neon: 512MB free tier, serverless (auto-suspend), pooling из коробки. Frankfurt (eu-central-1) — ближайший к Dubai доступный регион.

## Решение

### prisma.config.ts
```typescript
import { defineConfig } from 'prisma/config'
import { env } from 'prisma/config'

export default defineConfig({
  earlyAccess: true,
  datasource: {
    url: env("DATABASE_URL"),
  },
})
```

### schema.prisma
```prisma
datasource db {
  provider = "postgresql"
  // НЕТ url — конфигурация в prisma.config.ts
}
```

### package.json
```json
{
  "scripts": {
    "postinstall": "prisma generate",
    "build": "prisma generate && next build"
  }
}
```

### vercel.json
```json
{
  "buildCommand": "prisma generate && next build"
}
```

## Чек-лист деплоя Vercel + Prisma v7

- [ ] `prisma.config.ts` существует и использует `env()` из `prisma/config`
- [ ] `schema.prisma` НЕ содержит `url = env("DATABASE_URL")` в datasource
- [ ] `package.json` имеет `"postinstall": "prisma generate"`
- [ ] Build command включает `prisma generate && next build`
- [ ] `DATABASE_URL` добавлен в Vercel Environment Variables (Settings → Environment Variables)
- [ ] Connection string НЕ закоммичена в git (проверить `.gitignore`, экспортированные файлы)
- [ ] Для production: Neon PostgreSQL (eu-central-1 Frankfurt для Middle East)
- [ ] Для production: Vercel Pro план если нужен выбор региона
- [ ] `prisma migrate deploy` работает локально с тем же DATABASE_URL
- [ ] Prisma Client генерируется без ошибок (`npx prisma generate`)

## Превенция

1. **При создании нового Next.js + Prisma v7 проекта** — сразу создавать `prisma.config.ts` с `env()`, не `process.env`
2. **При миграции с Prisma v6 → v7** — убрать `url` из schema.prisma, создать prisma.config.ts
3. **Перед деплоем** — `grep -r "process.env.DATABASE" prisma/` должен возвращать 0 результатов
4. **Security audit** — `grep -ri "postgresql://" .` по всему проекту, исключая node_modules и .env
5. **Экспорт чатов** — никогда не коммитить экспорты сессий без предварительной очистки credentials

## Связанные уроки

- EXP-059: Tourism CRM Master Planning (тот же проект)
- EXP-063: TaskType Routing (AI-архитектура того же проекта)
- ai-model-selection-framework.md (выбор AI-моделей для serverless)
