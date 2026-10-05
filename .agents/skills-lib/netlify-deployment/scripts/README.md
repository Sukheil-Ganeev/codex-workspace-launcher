# Скрипты автоматизации Netlify

Коллекция из 4 скриптов для автоматизации работы с Netlify деплоем.

## Установка зависимостей

Все скрипты работают без дополнительных npm зависимостей. Требуется только:

```bash
# Netlify CLI (глобально)
npm install -g netlify-cli

# Или локально в проект
npm install --save-dev netlify-cli
```

**Примечание:** `validate-netlify-toml.cjs` использует встроенный TOML парсер без внешних зависимостей.

## Авторизация в Netlify

Перед использованием скриптов выполните:

```bash
# Авторизация
netlify login

# Привязка к сайту (в корне проекта)
netlify link
```

---

## 1. validate-netlify-toml.cjs

**Назначение:** Валидация netlify.toml файла перед деплоем

### Функции
- Проверка синтаксиса TOML
- Проверка обязательных полей (build.publish, build.command)
- Проверка существования путей
- Валидация redirects правил

### Использование

```bash
# Валидация netlify.toml в текущей директории
node validate-netlify-toml.cjs

# Валидация конкретного файла
node validate-netlify-toml.cjs path/to/netlify.toml
```

### Пример вывода

```
🔍 Валидация netlify.toml: ./netlify.toml

✓ TOML синтаксис корректен

[Build Settings]
  ✓ Build command: npm run build
  ✓ Publish directory: dist

[Paths Validation]
  ✓ Publish директория существует: dist

[Redirects Validation]
  Найдено редиректов: 2
  ✓ Redirect #1: /old-page → /new-page [301]
  ✓ Redirect #2: /api/* → /.netlify/functions/:splat [200]

════════════════════════════════════════
РЕЗУЛЬТАТЫ ВАЛИДАЦИИ
════════════════════════════════════════

✓ Валидация пройдена успешно!
```

---

## 2. deploy-helper.sh

**Назначение:** Упрощённый workflow деплоя с проверками

### Функции
- Проверка наличия Netlify CLI
- Выбор preview/production
- Pre-deploy валидация
- Deploy с логированием
- Post-deploy проверки

### Использование

```bash
# Интерактивный режим (спросит preview или production)
./deploy-helper.sh

# Preview деплой
./deploy-helper.sh preview

# Production деплой
./deploy-helper.sh production

# С кастомным сообщением
./deploy-helper.sh preview --message "Fix navigation bug"

# Пропустить валидацию
./deploy-helper.sh preview --skip-validation
```

### Что делает скрипт

1. **Pre-deploy проверки:**
   - Netlify CLI установлен
   - Авторизация активна
   - Сайт привязан
   - Валидация netlify.toml
   - Проверка package.json

2. **Деплой:**
   - Выполняет `netlify deploy` или `netlify deploy --prod`
   - Логирует в `logs/deploy-YYYYMMDD-HHMMSS.log`

3. **Post-deploy:**
   - Проверка доступности сайта (HTTP код)
   - Показывает последние деплои

### Логи

Все логи сохраняются в `logs/` директории:

```
logs/
├── deploy-20240204-143022.log
├── deploy-20240204-150145.log
└── deploy-20240204-163301.log
```

---

## 3. env-setup.cjs

**Назначение:** Быстрая настройка environment variables

### Функции
- Чтение .env.example или .env
- Интерактивный ввод значений
- Загрузка в Netlify через CLI
- Проверка обязательных переменных

### Использование

```bash
# Интерактивный режим (читает .env.example/.env)
node env-setup.cjs

# Загрузить все переменные из файла
node env-setup.cjs --from-file .env.local

# Показать текущие переменные в Netlify
node env-setup.cjs --list

# Удалить переменную
node env-setup.cjs --delete OLD_VAR_NAME

# Справка
node env-setup.cjs --help
```

### Интерактивный режим

```bash
$ node env-setup.cjs

🔧 Настройка Environment Variables

✓ Найден файл: .env.example

Найдено переменных: 3

Загружаю текущие значения из Netlify...

Введите значения (Enter - пропустить, "current" - использовать текущее):

API_KEY (пример: your-api-key-here): sk-1234567890abcdef
  → будет установлено
DATABASE_URL (пример: postgresql://...): current
  → оставлено текущее значение
SECRET_TOKEN (пример: random-token):
  → пропущено

Будет установлено переменных: 2
  • API_KEY
  • DATABASE_URL

Продолжить? (y/N): y

Устанавливаю переменные...

  API_KEY... ✓
  DATABASE_URL... ✓

Готово: 2 успешно, 0 ошибок
```

### Формат .env файла

```bash
# API Configuration
API_KEY=your-api-key-here
API_SECRET=your-secret

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Feature flags
ENABLE_ANALYTICS=true
```

---

## 4. test-functions-local.cjs

**Назначение:** Локальное тестирование serverless функций

### Функции
- Запуск функций локально (без Netlify Dev)
- Мок HTTP запросов
- Проверка environment variables
- Логирование ошибок
- Поддержка GET/POST/PUT/DELETE

### Использование

```bash
# Показать список доступных функций
node test-functions-local.cjs

# Тест функции (GET запрос)
node test-functions-local.cjs hello

# POST запрос с телом
node test-functions-local.cjs create-user --method POST --body '{"name":"John","email":"john@example.com"}'

# GET с query параметрами
node test-functions-local.cjs search --query "q=test&limit=10"

# С environment переменной
node test-functions-local.cjs protected --env API_KEY=test-key-123

# Комбинация опций
node test-functions-local.cjs webhook --method POST --body '{"event":"purchase"}' --env SECRET=abc123
```

### Пример вывода

```
🧪 Тестирование функции: hello
   Файл: /project/netlify/functions/hello.js

📥 Request:
   Method: GET
   Path: /.netlify/functions/test

⏳ Выполнение...

✓ Выполнено за 45ms

📤 Response:
   Status: 200
   Headers:
     content-type: application/json

   Body:
     {
       "message": "Hello, World!",
       "timestamp": "2024-02-04T14:30:22.123Z"
     }
```

### Поддерживаемые директории

Скрипт автоматически ищет функции в:
1. `netlify/functions/`
2. `functions/`
3. `.netlify/functions/`
4. Или в директории из `netlify.toml` (build.functions)

### Структура функции

Netlify функции должны экспортировать handler:

```javascript
// netlify/functions/hello.js
exports.handler = async (event, context) => {
  return {
    statusCode: 200,
    body: JSON.stringify({
      message: 'Hello from Netlify Function!'
    })
  };
};
```

---

## Workflow: От разработки до production

### 1. Разработка функций

```bash
# Тестируем функцию локально
node test-functions-local.cjs my-function

# Если нужны env переменные
node test-functions-local.cjs my-function --env API_KEY=test
```

### 2. Настройка environment variables

```bash
# Интерактивная настройка
node env-setup.cjs

# Или загрузка из файла
node env-setup.cjs --from-file .env.production
```

### 3. Валидация конфигурации

```bash
# Проверяем netlify.toml
node validate-netlify-toml.cjs
```

### 4. Preview деплой

```bash
# Деплоим в preview
./deploy-helper.sh preview --message "Add new feature"

# Проверяем preview URL
# Тестируем на preview окружении
```

### 5. Production деплой

```bash
# После тестирования preview — деплоим в production
./deploy-helper.sh production

# Скрипт попросит подтверждение
# Логи сохранятся в logs/
```

---

## Troubleshooting

### Netlify CLI не найден

```bash
# Установите глобально
npm install -g netlify-cli

# Или локально в проект
npm install --save-dev netlify-cli
npx netlify login
```

### Ошибка "Not logged in"

```bash
netlify login
```

### Ошибка "No site linked"

```bash
# В корне проекта
netlify link

# Или явно указать Site ID
netlify link --id YOUR-SITE-ID
```

### validate-netlify-toml.cjs: Ошибка парсинга

Скрипт использует встроенный TOML парсер. Если возникают проблемы:
- Проверьте синтаксис TOML файла
- Убедитесь, что кавычки парные
- Проверьте секции [[redirects]] и [build]

### Функции не найдены (test-functions-local.cjs)

Создайте директорию:
```bash
mkdir -p netlify/functions
```

Или укажите в `netlify.toml`:
```toml
[build]
  functions = "functions"
```

---

## Git Bash (Windows)

Все скрипты работают в Git Bash на Windows:

```bash
# Конвертируйте путь
cd /c/Users/londo/.claude/skills/netlify-deployment/scripts

# Запускайте скрипты
./deploy-helper.sh preview
node validate-netlify-toml.cjs
```

---

## Дополнительная информация

- **SKILL.md** — Полное руководство по Netlify деплою
- **references/cheatsheet.md** — Шпаргалка по командам
- **references/troubleshooting.md** — Решение проблем
- **experience/** — Накопленный опыт и уроки

## Автор

Часть скилла **netlify-deployment** для Claude Code
