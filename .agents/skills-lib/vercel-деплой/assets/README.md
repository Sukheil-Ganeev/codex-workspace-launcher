# Assets - Шаблоны, примеры и скрипты

Полный набор готовых к использованию ресурсов для работы с Vercel.

## Структура

```
assets/
├── templates/          # Готовые конфигурации (5 файлов)
├── examples/           # Рабочие примеры проектов (3 проекта)
└── README.md          # Этот файл
```

## 📋 Templates (Шаблоны)

Готовые файлы конфигурации `vercel.json` для разных типов проектов.

### Доступные шаблоны

| Файл | Описание | Когда использовать |
|------|----------|-------------------|
| `vercel-static-basic.json` | Базовый статичный сайт | HTML/CSS/JS без серверной логики |
| `vercel-static-with-api.json` | Статичный сайт + API | Frontend + serverless функции |
| `vercel-nextjs.json` | Next.js проект | Next.js приложения (minimal config) |
| `vercel-spa.json` | Single Page Application | React/Vue с client-side routing |
| `env-template.txt` | Шаблон переменных окружения | Настройка env переменных |

### Использование

```bash
# Скопировать нужный шаблон в проект
cp ~/.claude/skills/vercel-деплой/assets/templates/vercel-static-basic.json ./vercel.json

# Или через скрипт setup-vercel.sh (интерактивный выбор)
```

## 📁 Examples (Примеры проектов)

Три полноценных рабочих проекта с документацией.

### 1. Static Landing

**Путь:** `examples/static-landing/`

**Что внутри:**
- `index.html` - Красивый одностраничный лендинг
- `vercel.json` - Конфигурация для статичного сайта
- `README.md` - Инструкции по деплою и кастомизации

**Для кого:**
- Простые landing pages
- Портфолио
- Информационные страницы

**Как использовать:**
```bash
# Скопировать пример
cp -r ~/.claude/skills/vercel-деплой/assets/examples/static-landing ~/my-landing

# Перейти и задеплоить
cd ~/my-landing
vercel --prod
```

### 2. Serverless API

**Путь:** `examples/serverless-api/`

**Что внутри:**
- `api/hello.js` - Простой GET endpoint
- `api/webhook.js` - Telegram webhook endpoint
- `vercel.json` - Конфигурация serverless функций
- `README.md` - Документация API + интеграции

**Для кого:**
- REST API endpoints
- Telegram/Discord боты (webhooks)
- Микросервисы
- Backend для frontend проектов

**Фичи:**
- Готовый Telegram webhook
- Примеры GET/POST запросов
- Варианты интеграций (Telegram, Email, DB)

**Как использовать:**
```bash
# Скопировать пример
cp -r ~/.claude/skills/vercel-деплой/assets/examples/serverless-api ~/my-api

# Настроить env переменные
cd ~/my-api
vercel env add TELEGRAM_BOT_TOKEN

# Задеплоить
vercel --prod
```

### 3. Static with Forms

**Путь:** `examples/static-with-forms/`

**Что внутри:**
- `index.html` - Страница с формой обратной связи
- `api/submit-form.js` - Backend обработки формы
- `vercel.json` - Конфигурация
- `README.md` - Инструкции + 3 варианта интеграций

**Для кого:**
- Сайты с формами обратной связи
- Landing pages с лидогенерацией
- Контактные формы

**Фичи:**
- Client-side валидация
- Serverless обработка
- 3 варианта интеграций:
  - Telegram (отправка в чат)
  - Email (через SendGrid)
  - Database (MongoDB)
- Feedback пользователю (успех/ошибка)

**Как использовать:**
```bash
# Скопировать пример
cp -r ~/.claude/skills/vercel-деплой/assets/examples/static-with-forms ~/my-form

# Выбрать интеграцию (раскомментировать в api/submit-form.js)
# Настроить env переменные
cd ~/my-form
vercel env add TELEGRAM_BOT_TOKEN  # для Telegram
# или
vercel env add SENDGRID_API_KEY    # для Email
# или
vercel env add MONGODB_URI         # для Database

# Задеплоить
vercel --prod
```

## Быстрый старт

### Сценарий 1: Статичный сайт

```bash
# 1. Создать папку проекта
mkdir my-website && cd my-website

# 2. Скопировать шаблон
cp ~/.claude/skills/vercel-деплой/assets/templates/vercel-static-basic.json ./vercel.json

# 3. Создать index.html
echo "<h1>Hello World</h1>" > index.html

# 4. Задеплоить
vercel --prod
```

### Сценарий 2: API endpoint

```bash
# 1. Создать структуру
mkdir -p my-api/api && cd my-api

# 2. Скопировать пример API
cp ~/.claude/skills/vercel-деплой/assets/examples/serverless-api/api/hello.js ./api/

# 3. Скопировать конфиг
cp ~/.claude/skills/vercel-деплой/assets/templates/vercel-static-with-api.json ./vercel.json

# 4. Задеплоить
vercel --prod
```

### Сценарий 3: Использовать готовый пример

```bash
# Скопировать любой пример целиком
cp -r ~/.claude/skills/vercel-деплой/assets/examples/static-with-forms ~/my-project

# Перейти и задеплоить
cd ~/my-project
vercel --prod
```

## Модификация примеров

### Изменить шаблон

1. Найти нужный файл в `templates/`
2. Скопировать в проект
3. Отредактировать под свои нужды

### Комбинировать примеры

```bash
# Взять форму из static-with-forms
cp examples/static-with-forms/index.html ./

# Добавить webhook из serverless-api
cp examples/serverless-api/api/webhook.js ./api/

# Использовать конфиг для static + API
cp templates/vercel-static-with-api.json ./vercel.json
```

## Связь с scripts/

Скрипты (в папке `scripts/`) автоматически используют эти шаблоны:

- `setup-vercel.sh` - Интерактивный выбор шаблона из `templates/`
- `deploy-workflow.sh` - Валидация конфигов перед деплоем
- `validate-config.js` - Проверка vercel.json из любого проекта

## Полезные команды

```bash
# Список всех шаблонов
ls ~/.claude/skills/vercel-деплой/assets/templates/

# Список всех примеров
ls ~/.claude/skills/vercel-деплой/assets/examples/

# Просмотр README конкретного примера
cat ~/.claude/skills/vercel-деплой/assets/examples/static-landing/README.md

# Просмотр содержимого шаблона
cat ~/.claude/skills/vercel-деплой/assets/templates/vercel-spa.json
```

## Добавление своих шаблонов

Чтобы добавить свой шаблон:

1. Создать файл в `templates/`:
   ```bash
   nano ~/.claude/skills/vercel-деплой/assets/templates/my-template.json
   ```

2. Добавить конфигурацию
3. Использовать как обычно:
   ```bash
   cp ~/.claude/skills/vercel-деплой/assets/templates/my-template.json ./vercel.json
   ```

## Troubleshooting

**Проблема:** Не могу найти шаблон

**Решение:**
```bash
# Проверить путь
ls ~/.claude/skills/vercel-деплой/assets/templates/

# Использовать полный путь
cp /c/Users/londo/.claude/skills/vercel-деплой/assets/templates/vercel-spa.json ./vercel.json
```

---

**Проблема:** Пример не работает после копирования

**Решение:**
1. Проверить все файлы скопированы:
   ```bash
   ls -la
   ```
2. Проверить vercel.json валиден:
   ```bash
   node ~/.claude/skills/vercel-деплой/scripts/validate-config.js
   ```
3. Посмотреть README примера:
   ```bash
   cat README.md
   ```

---

**Проблема:** Нужен пример, которого нет

**Решение:**
- Комбинируйте существующие примеры
- Модифицируйте ближайший похожий пример
- Используйте шаблоны как основу

## Ссылки

- [Vercel Documentation](https://vercel.com/docs)
- [vercel.json Reference](https://vercel.com/docs/project-configuration)
- [Serverless Functions](https://vercel.com/docs/concepts/functions/serverless-functions)
- [Build Configuration](https://vercel.com/docs/build-step)
