# HTML/CSS Reference Scripts

Набор из 8 automation scripts для управления HTML/CSS справочником.

## Быстрый старт

```bash
# Установить зависимости
npm install

# Просмотр доступных команд
npm run --list

# Стандартное использование
npm run lint          # Проверить HTML и CSS
npm run serve         # Запустить dev сервер
npm run build:prod    # Production build
npm run deploy:prod   # Deploy на Netlify
```

## Скрипты

### 1. lint-html.js - HTML Validator

Валидирует HTML файлы используя html-validate.

```bash
# Базовое использование
node lint-html.js

# С опциями
node lint-html.js --path ./content --fix --strict --verbose

# npm scripts
npm run lint:html
```

**Опции:**
- `--path <dir>` - Директория для проверки (default: ./content)
- `--fix` - Автоматически исправлять ошибки
- `--strict` - Fail на warnings (не только errors)
- `--config <file>` - Кастомный конфиг файл
- `--verbose` - Детальный вывод

**Вывод:**
```
🔍 HTML Validation Started
📁 Scanning: ./content

📄 Found 5 HTML file(s)

[1/5] content/index.html ... ✓
[2/5] content/pages/about.html ... ✓
[3/5] content/pages/contact.html ... ✗ (2 errors, 1 warning)
[4/5] content/sections/tutorial.html ... ✓
[5/5] content/docs/api.html ... ✓

==================================================
📊 Validation Summary
==================================================
✓ All files are valid!
```

---

### 2. lint-css.js - CSS Validator

Линтит CSS файлы используя stylelint.

```bash
# Базовое использование
node lint-css.js

# С опциями
node lint-css.js --path ./styles --fix --strict

# npm scripts
npm run lint:css
```

**Опции:**
- `--path <dir>` - Директория для проверки (default: ./styles)
- `--fix` - Автоматически исправлять ошибки
- `--strict` - Fail на warnings
- `--config <file>` - Кастомный stylelint config
- `--verbose` - Детальный вывод
- `--pattern <pat>` - File pattern (default: **/*.css)

**Вывод:**
```
🎨 CSS Validation Started
📁 Scanning: ./styles

📄 Found 3 CSS file(s)

[1/3] styles/main.css ... ✓
[2/3] styles/components.css ... ✓
[3/3] styles/responsive.css ... ✓

==================================================
📊 Linting Summary
==================================================
✓ All CSS files are valid!
```

---

### 3. minify.js - Minifier

Минифицирует HTML, CSS и JS файлы.

```bash
# Базовое использование
node minify.js

# С опциями
node minify.js --input ./src --output ./dist --types css,js

# Dry-run (preview без изменений)
node minify.js --dry-run

# npm scripts
npm run minify
```

**Опции:**
- `--input <dir>` - Input директория (default: ./src)
- `--output <dir>` - Output директория (default: ./dist)
- `--types <list>` - Типы файлов (default: html,css,js)
- `--verbose` - Детальный вывод
- `--dry-run` - Preview без изменения файлов

**Вывод:**
```
📦 Minification Started
📂 Input: ./src
📤 Output: ./dist

🔍 Processing HTML files...
✓ Minified 5 HTML file(s)

🎨 Processing CSS files...
✓ Minified 3 CSS file(s)

⚙️  Processing JavaScript files...
✓ Minified 2 JS file(s)

==================================================
📊 Minification Summary
==================================================
Original size: 245.50 KB
Minified size: 180.20 KB
Size reduction: 65.30 KB (26.61%)

✓ Minification completed
```

---

### 4. image-optimizer.js - Image Optimizer

Сжимает и оптимизирует изображения.

```bash
# Базовое использование
node image-optimizer.js

# С опциями
node image-optimizer.js --input ./assets/images --output ./dist/images --quality 85 --webp

# npm scripts
npm run optimize:images
```

**Опции:**
- `--input <dir>` - Input директория (default: ./images)
- `--output <dir>` - Output директория (default: ./images-optimized)
- `--quality <n>` - JPEG quality 0-100 (default: 80)
- `--progressive` - Progressive JPEGs
- `--webp` - Создавать WebP версии
- `--verbose` - Детальный вывод

**Поддерживаемые форматы:**
- JPEG / JPG (с mozjpeg)
- PNG (с pngquant)
- GIF
- SVG
- WebP

**Вывод:**
```
🖼️  Image Optimizer Started
📁 Input: ./assets/images
📤 Output: ./dist/images
⚙️  Quality: 85%

📄 Found 12 image(s)

[1/12] assets/images/hero.jpg ... ✓ (1.2 MB → 320 KB, -73.3%)
[2/12] assets/images/logo.png ... ✓ (450 KB → 120 KB, -73.3%)
...

==================================================
📊 Optimization Summary
==================================================
✓ Processed: 12
Original size: 5.60 MB
Optimized size: 1.85 MB
Size reduction: 3.75 MB (66.96%)
```

---

### 5. serve.js - Development Server

Запускает local dev сервер с live reload.

```bash
# Базовое использование
node serve.js

# С опциями
node serve.js --port 3000 --open --watch

# npm scripts
npm run serve
npm run serve:open
```

**Опции:**
- `--port <n>` - Port (default: 8080)
- `--root <dir>` - Root директория (default: .)
- `--open` - Открыть в браузере
- `--watch` - Следить за изменениями файлов
- `--verbose` - Детальный вывод

**Вывод:**
```
🚀 Development Server
==================================================
📁 Root: C:/projects/html-css-reference
🌐 URL: http://localhost:8080
👁️  Watching for changes
==================================================
Press Ctrl+C to stop server

✓ Server started on http://localhost:8080
🌐 Opening http://localhost:8080 in browser
```

**Особенности:**
- Автоматическое index.html для папок
- MIME types для всех файлов
- CORS заголовки
- Graceful shutdown на Ctrl+C

---

### 6. build.js - Production Build

Собирает оптимизированный production build.

```bash
# Базовое использование
node build.js

# Production build с минификацией и оптимизацией
node build.js --minify --optimize-img --clean

# npm scripts
npm run build
npm run build:prod
```

**Опции:**
- `--input <dir>` - Input директория (default: ./src)
- `--output <dir>` - Output директория (default: ./dist)
- `--minify` - Минифицировать файлы
- `--optimize-img` - Оптимизировать изображения
- `--source-maps` - Генерировать source maps
- `--verbose` - Детальный вывод
- `--clean` - Очистить output директорию перед build

**Вывод:**
```
🏗️  Production Build
==================================================
📁 Input: ./src
📤 Output: ./dist
💾 Input size: 8.45 MB
==================================================

📋 Copying files...
✓ Files copied

🔍 Validation
🔍 Linting HTML files...
✓ HTML validation passed

🎨 Linting CSS files...
✓ CSS validation passed

📦 Optimization
...

==================================================
📊 Build Summary
==================================================
✓ Output size: 2.15 MB
📉 Size reduction: 6.30 MB (74.56%)
⏱️  Build time: 12.34s
✓ Build completed successfully!
```

---

### 7. deploy.js - Netlify Deploy

Деплоит на Netlify.

```bash
# Установить переменные окружения
export NETLIFY_SITE_ID=your-site-id
export NETLIFY_AUTH_TOKEN=your-auth-token

# Deploy на preview
node deploy.js

# Deploy в production
node deploy.js --prod

# npm scripts
npm run deploy
npm run deploy:prod
```

**Опции:**
- `--site-id <id>` - Netlify Site ID
- `--auth <token>` - Netlify Auth Token
- `--dir <path>` - Директория для deploy (default: ./dist)
- `--prod` - Deploy в production (не preview)
- `--message <msg>` - Deploy message
- `--open` - Открыть сайт после deploy
- `--verbose` - Детальный вывод

**Environment Variables:**
```bash
NETLIFY_SITE_ID=abc123xyz
NETLIFY_AUTH_TOKEN=your-token-here
```

**Вывод:**
```
🚀 Netlify Deployment
==================================================
📁 Directory: /projects/html-css-reference/dist
📊 Files: 145
💾 Size: 2.15 MB
🔴 Mode: PRODUCTION
==================================================

📤 Uploading to Netlify...

==================================================
✓ Deployment Successful!
==================================================
🌐 Live URL: https://html-css-ref.netlify.app
⏱️  Duration: 15.42s

🌐 Opening https://html-css-ref.netlify.app
```

---

### 8. test-links.js - Link Checker

Проверяет broken links в HTML файлах.

```bash
# Базовое использование (только внутренние ссылки)
node test-links.js

# Проверить внешние ссылки (медленно)
node test-links.js --external

# С опциями
node test-links.js --timeout 10000 --ignore "example.com,localhost"

# npm scripts
npm run test:links
npm run test:links:external
```

**Опции:**
- `--path <dir>` - Директория для сканирования (default: ./content)
- `--timeout <ms>` - Request timeout (default: 5000)
- `--external` - Проверять внешние ссылки
- `--ignore <list>` - Patterns для игнорирования (comma-separated)
- `--verbose` - Детальный вывод

**Вывод:**
```
🔗 Link Checker
==================================================
📁 Scanning: ./content
🌐 External links: DISABLED (use --external)
==================================================

📄 Found 15 HTML file(s)

🔎 Checking 230 link(s)...

[1/230] /pages/about.html ... ✓
[2/230] /images/logo.png ... ✓
[3/230] https://example.com ... ⊘
[4/230] ./tutorial.html ... ✓
...

==================================================
📊 Link Check Summary
==================================================
✓ Valid: 225
⊘ Skipped: 5 (external)

✓ All links are valid!
```

---

## Полный Workflow

### Development

```bash
# 1. Установить зависимости
npm install

# 2. Запустить dev сервер с live reload
npm run serve:open

# 3. В другом терминале - линтить файлы
npm run lint

# 4. Проверить ссылки
npm run test:links
```

### Production

```bash
# 1. Линтить
npm run lint

# 2. Проверить все ссылки (включая внешние)
npm run test:links:external

# 3. Production build
npm run build:prod

# 4. Deploy на Netlify
npm run deploy:prod
```

### Полный CI/CD Pipeline

```bash
#!/bin/bash

# Validate
npm run lint
npm run test:links

# Build
npm run build:prod

# Deploy
npm run deploy:prod -- --message "Automated deploy"
```

---

## Установка зависимостей

Все скрипты используют Node.js CLI tools через npx. Зависимости указаны в `package.json`:

```bash
npm install
```

**Основные инструменты:**
- `html-validate` - HTML валидация
- `stylelint` - CSS линтинг
- `html-minifier-terser` - HTML минификация
- `csso-cli` - CSS минификация
- `terser` - JS минификация
- `imagemin` - Оптимизация изображений
- `netlify-cli` - Netlify deployment

---

## Цветовой код вывода

- 🟢 **Зеленый** - Успешно
- 🔴 **Красный** - Ошибка
- 🟡 **Желтый** - Warning / Skip
- 🔵 **Синий** - Информация
- 🔷 **Cyan** - Статус
- 🟣 **Magenta** - Дополнительно

---

## Примеры использования

### Только HTML validation

```bash
node lint-html.js --path ./content --strict
```

### Только CSS validation с автоfix

```bash
node lint-css.js --path ./styles --fix
```

### Оптимизировать изображения в WebP

```bash
node image-optimizer.js --quality 75 --webp --verbose
```

### Минифицировать только CSS и JS

```bash
node minify.js --types css,js --verbose
```

### Dev сервер с автозагрузкой

```bash
node serve.js --port 3000 --watch --open
```

### Full production build pipeline

```bash
node build.js --minify --optimize-img --clean --verbose
```

### Deploy с custom message

```bash
node deploy.js --prod --message "v1.2.0 - New features" --open
```

### Проверка ссылок с игнорированием доменов

```bash
node test-links.js --external --ignore "cdn.example.com,api.test.com"
```

---

## Troubleshooting

### "npx: command not found"
Убедитесь что установлен Node.js:
```bash
node --version
npm --version
```

### "Port already in use"
Используйте другой port:
```bash
node serve.js --port 3000
```

### Deploy fails на Netlify
Проверьте переменные окружения:
```bash
echo $NETLIFY_SITE_ID
echo $NETLIFY_AUTH_TOKEN
```

### Broken links при deploy
Запустите checker:
```bash
npm run test:links
```

---

## Лицензия

MIT
