# Установка и настройка Scripts

## Системные требования

- Node.js 14+ (`node --version`)
- npm 6+ (`npm --version`)
- Git (для версионирования)

## Быстрая установка

```bash
# Перейти в папку скриптов
cd "C:/Users/londo/.claude/skills/html-css-справочник/scripts"

# Установить все зависимости
npm install

# Проверить установку
npm run --list
```

## Конфигурация для разных ОС

### Windows (MINGW64/Git Bash)

```bash
# Используйте полные пути
node lint-html.js --path "D:/my-project/content"

# Или используйте npm scripts
npm run lint:html
```

### macOS/Linux

```bash
# Функционирует аналогично
node lint-html.js --path ./content
npm run lint:html
```

## Netlify Setup (для deploy скрипта)

### Шаг 1: Получить Netlify Token

1. Зайти на https://app.netlify.com
2. User settings → Applications → Personal access tokens
3. Создать новый token
4. Скопировать token

### Шаг 2: Получить Site ID

1. Зайти в settings вашего сайта
2. Скопировать Site ID

### Шаг 3: Установить переменные окружения

**Windows (cmd):**
```cmd
set NETLIFY_SITE_ID=your-site-id-here
set NETLIFY_AUTH_TOKEN=your-token-here
```

**Windows (PowerShell):**
```powershell
$env:NETLIFY_SITE_ID="your-site-id-here"
$env:NETLIFY_AUTH_TOKEN="your-token-here"
```

**Git Bash / macOS / Linux:**
```bash
export NETLIFY_SITE_ID=your-site-id-here
export NETLIFY_AUTH_TOKEN=your-token-here
```

### Шаг 4: Проверить deploy

```bash
npm run deploy
```

## Кастомная конфигурация

### HTML Validation (.htmlvalidaterc.json)

```json
{
  "extends": ["html-validate:recommended"],
  "rules": {
    "void-content": "off",
    "no-trailing-whitespace": "warn"
  }
}
```

### CSS Linting (.stylelintrc.json)

```json
{
  "extends": "stylelint-config-standard",
  "rules": {
    "selector-type-case": "lower",
    "property-no-unknown": true
  }
}
```

## Troubleshooting

### npm: command not found

Установите Node.js с https://nodejs.org

### Port 8080 already in use

```bash
# Используйте другой port
npm run serve -- --port 3000
```

### Netlify deploy fails

Проверьте:
```bash
echo %NETLIFY_SITE_ID%
echo %NETLIFY_AUTH_TOKEN%
```

Или для Linux/macOS:
```bash
echo $NETLIFY_SITE_ID
echo $NETLIFY_AUTH_TOKEN
```

## Обновление зависимостей

```bash
npm update
```

## Полное переустановление

```bash
# Удалить node_modules и package-lock.json
rm -rf node_modules package-lock.json

# Переустановить
npm install
```

