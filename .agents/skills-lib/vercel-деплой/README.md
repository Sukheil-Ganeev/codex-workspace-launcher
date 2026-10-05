# Vercel Deployment — Справочник

Полный справочник по деплою на Vercel: CLI workflow, serverless functions, сравнение с Netlify.

## Структура

```
vercel-деплой/
├── SKILL.md                     # 📘 Основное руководство (~4000 слов)
├── README.md                    # 📍 Этот файл — навигация
├── marketplace.json             # ⚙️ Метаданные скилла
├── assets/
│   ├── templates/               # 📝 vercel.json шаблоны
│   └── examples/                # 💡 Готовые примеры проектов
├── references/                  # 📚 Справочники
│   ├── faq.md                   # ❓ Часто задаваемые вопросы
│   ├── troubleshooting.md       # 🔧 Решение 12+ ошибок
│   ├── cheatsheet.md            # ⚡ Шпаргалка команд
│   ├── vercel-vs-netlify.md     # ⚖️ Детальное сравнение (ВАЖНО!)
│   ├── cli-reference.md         # 📋 CLI команды
│   └── serverless-guide.md      # 🚀 Serverless functions
├── scripts/                     # 🤖 Скрипты автоматизации
│   ├── setup-vercel.sh
│   ├── deploy-workflow.sh
│   └── validate-config.js
└── experience/                  # 📖 Накопленный опыт
    └── _index.md                # 🎯 Критические уроки
```

## Quick Start

### Для новичков
1. **SKILL.md** → секция "Quick Start Guide"
2. **SKILL.md** → секция "Установка и настройка"
3. **references/cli-reference.md** — команды CLI

### Выбор платформы: Vercel или Netlify?
**Читай:** **references/vercel-vs-netlify.md** — детальное сравнение (1500 слов)

**Кратко:**
- **Vercel:** Next.js, React, сложные SSR/SSG проекты, быстрее для фронтенда
- **Netlify:** Простые статичные сайты, формы, Drop деплой, проще для новичков

### При проблемах
1. **references/troubleshooting.md** — 12+ типичных ошибок
2. **references/faq.md** — ответы на частые вопросы
3. **experience/_index.md** — уроки из реального опыта

### Для копирования
- **assets/templates/** — готовые vercel.json конфиги
- **assets/examples/** — полные примеры проектов

## Триггеры активации

Используй этот скилл когда:
- "vercel"
- "деплой на vercel"
- "vercel cli"
- "vercel vs netlify"
- "serverless function vercel"
- "preview deployment"

## CLI Workflow

**Основные команды:**
```bash
# Preview деплой (тестовый)
vercel

# Production деплой
vercel --prod

# Логи
vercel logs <deployment-url>

# Environment variables
vercel env add
```

**Подробно:** SKILL.md → секция "CLI Workflow"

## Бизнес-кейсы

✅ **Next.js приложения** — оптимизировано для Next.js
✅ **Статичные сайты** — простой деплой через GitHub
✅ **Serverless API** — webhooks, обработка данных
✅ **Preview Deployments** — автоматические превью для каждого PR

## Первый шаг

**Прочитай:** `experience/_index.md` — критические уроки из реального опыта

---

Создано: 2026-02-04
Версия: 1.0.0
Автор: Claude Code + Сухейль
