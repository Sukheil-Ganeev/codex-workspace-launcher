# Быстрый старт

## 30-секундная установка

```bash
cd "C:/Users/londo/.claude/skills/html-css-справочник/scripts"
npm install
```

## Команды

```bash
# Валидация кода
npm run lint              # HTML + CSS проверка
npm run lint:html         # Только HTML
npm run lint:css          # Только CSS

# Разработка
npm run serve             # Запустить сервер на :8080
npm run serve:open        # Запустить и открыть браузер

# Оптимизация
npm run minify            # Минифицировать HTML/CSS/JS
npm run optimize:images   # Сжать изображения

# Production
npm run build             # Build с валидацией
npm run build:prod        # Full build: validate + minify + optimize images

# Deploy
npm run deploy            # Deploy на preview
npm run deploy:prod       # Deploy на production (live)

# Testing
npm run test:links        # Проверить все ссылки
npm run test:links:external # + внешние ссылки
```

## Примеры использования

### Сценарий 1: Dev процесс

```bash
# Terminal 1: Запустить сервер
npm run serve:open

# Terminal 2: Следить за качеством
npm run lint
npm run test:links
```

### Сценарий 2: Готовимся к production

```bash
# 1. Валидация
npm run lint
npm run test:links

# 2. Build
npm run build:prod

# 3. Результат в ./dist/
ls ./dist
```

### Сценарий 3: Deploy на Netlify

```bash
# Шаг 1: Настроить переменные (один раз)
export NETLIFY_SITE_ID=your-id-here
export NETLIFY_AUTH_TOKEN=your-token-here

# Шаг 2: Deploy
npm run deploy:prod

# Результат: сайт live на Netlify
```

## Опции для скриптов

Все скрипты поддерживают --help:

```bash
node lint-html.js --help
node minify.js --help
node serve.js --help
# и т.д.
```

## Полная документация

- **README.md** - Детальное описание всех скриптов
- **INSTALLATION.md** - Настройка и troubleshooting
- **REPORT.md** - Полный отчет о создании

## Файлы скриптов

```
C:/Users/londo/.claude/skills/html-css-справочник/scripts/
├── lint-html.js          # HTML validator
├── lint-css.js           # CSS linter
├── minify.js             # Minifier
├── image-optimizer.js    # Image optimizer
├── serve.js              # Dev server
├── build.js              # Build pipeline
├── deploy.js             # Netlify deploy
├── test-links.js         # Link checker
└── package.json          # Dependencies
```

## Требования

- Node.js 14+
- npm 6+

## Help

```bash
# Показать все доступные команды
npm run

# Помощь для конкретного скрипта
node lint-html.js --help
node deploy.js --help

# Проверить версии
node --version
npm --version
```

---

**Готово! Все скрипты работают и готовы к использованию.**
