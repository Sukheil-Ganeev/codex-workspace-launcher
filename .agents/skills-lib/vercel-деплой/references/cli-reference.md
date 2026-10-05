# CLI Reference — Полный справочник команд

## Установка и настройка

### Установка

```bash
# Глобальная установка
npm install -g vercel

# Или через yarn
yarn global add vercel

# Или через pnpm
pnpm add -g vercel

# Проверка версии
vercel --version
```

### Авторизация

```bash
# Логин
vercel login

# Выбор метода:
# - Email (код на почту)
# - GitHub
# - GitLab
# - Bitbucket

# Логаут
vercel logout

# Проверка текущего пользователя
vercel whoami
```

---

## Основные команды деплоя

### `vercel`

**Назначение:** Создать preview deployment

**Синтаксис:**
```bash
vercel [path] [опции]
```

**Опции:**
- `--prod` — деплой в production
- `--force` — игнорировать кэш, пересобрать
- `--yes` / `-y` — пропустить все подтверждения
- `--token <token>` — использовать токен для CI/CD
- `--scope <team>` — деплоить под командой
- `--regions <regions>` — указать регионы
- `--env <key=value>` — добавить environment variable
- `--build-env <key=value>` — добавить build environment variable
- `--name <name>` — имя проекта
- `--local-config <path>` — путь к vercel.json

**Примеры:**
```bash
# Простой preview deployment
vercel

# Production deployment
vercel --prod

# Деплой с подтверждением
vercel --yes --prod

# Деплой конкретной папки
vercel ./dist

# Force rebuild
vercel --force

# Деплой в конкретные регионы
vercel --regions sfo1,iad1

# CI/CD деплой
vercel --token=$VERCEL_TOKEN --prod
```

**См. также:** `vercel deploy`, `vercel --prod`

---

### `vercel dev`

**Назначение:** Запустить локальный dev сервер (симулирует Vercel окружение)

**Синтаксис:**
```bash
vercel dev [опции]
```

**Опции:**
- `--port <port>` / `-p` — указать порт (по умолчанию 3000)
- `--listen <host:port>` — указать host и port
- `--yes` / `-y` — автоматически отвечать yes

**Примеры:**
```bash
# Запустить на порту 3000
vercel dev

# Запустить на другом порту
vercel dev --port 8080

# Указать host и port
vercel dev --listen 0.0.0.0:3000
```

**Возможности:**
- ✅ Симулирует Serverless Functions
- ✅ Симулирует Edge Functions
- ✅ Environment variables из Vercel
- ✅ Hot reload

**См. также:** `vercel env pull`

---

### `vercel --prod`

**Назначение:** Деплоить в production (обновляет основной домен)

**Синтаксис:**
```bash
vercel --prod [опции]
```

**Примеры:**
```bash
# Production деплой
vercel --prod

# С подтверждением
vercel --prod --yes

# С токеном (CI/CD)
vercel --prod --token=$VERCEL_TOKEN
```

**⚠️ Важно:**
- Обновляет `your-app.vercel.app`
- Обновляет все custom domains
- Видно реальным пользователям

**См. также:** `vercel`, `vercel alias`

---

## Управление deployments

### `vercel ls`

**Назначение:** Показать список deployments

**Синтаксис:**
```bash
vercel ls [app] [опции]
```

**Опции:**
- `--next <number>` — показать больше результатов
- `--meta <key=value>` — фильтр по metadata

**Примеры:**
```bash
# Все deployments
vercel ls

# Для конкретного проекта
vercel ls my-app

# Показать больше
vercel ls --next 50
```

**Вывод:**
```
  my-app-abc123.vercel.app    Production    3m ago
  my-app-xyz789.vercel.app    Preview       1h ago
  my-app-def456.vercel.app    Preview       2h ago
```

**См. также:** `vercel rm`, `vercel inspect`

---

### `vercel rm`

**Назначение:** Удалить deployment

**Синтаксис:**
```bash
vercel rm <url> [url2] [url3] [опции]
```

**Опции:**
- `--safe` — удалить только preview deployments
- `--yes` / `-y` — без подтверждения

**Примеры:**
```bash
# Удалить один deployment
vercel rm my-app-abc123.vercel.app

# Удалить несколько
vercel rm url1.vercel.app url2.vercel.app

# Удалить безопасно (только preview)
vercel rm --safe

# Без подтверждения
vercel rm my-app.vercel.app --yes
```

**⚠️ Важно:**
- Production deployment нельзя удалить напрямую
- Удаление необратимо

**См. также:** `vercel ls`

---

### `vercel inspect`

**Назначение:** Показать детальную информацию о deployment

**Синтаксис:**
```bash
vercel inspect <url> [опции]
```

**Опции:**
- `--timeout <ms>` — timeout для запроса

**Примеры:**
```bash
# Информация о deployment
vercel inspect my-app-abc123.vercel.app
```

**Вывод:**
```json
{
  "id": "dpl_abc123",
  "url": "my-app-abc123.vercel.app",
  "name": "my-app",
  "state": "READY",
  "creator": "user@example.com",
  "created": 1609459200000,
  "buildingAt": 1609459205000,
  "ready": 1609459260000
}
```

**См. также:** `vercel ls`

---

### `vercel alias`

**Назначение:** Создать или управлять алиасами (custom domains)

**Синтаксис:**
```bash
vercel alias [deployment-url] [alias] [опции]
```

**Примеры:**
```bash
# Назначить alias
vercel alias my-app-abc123.vercel.app my-app.com

# Список алиасов
vercel alias ls

# Удалить alias
vercel alias rm my-app.com
```

**Использование:**
- Переключение между версиями
- Rollback к старой версии
- A/B тестирование

**См. также:** `vercel domains`

---

## Логи

### `vercel logs`

**Назначение:** Показать логи функций

**Синтаксис:**
```bash
vercel logs [deployment-url] [опции]
```

**Опции:**
- `--follow` / `-f` — real-time логи (follow mode)
- `--limit <number>` / `-n` — количество записей
- `--since <time>` — логи с определённого времени
- `--until <time>` — логи до определённого времени
- `--filter <path>` — фильтр по пути функции
- `--output <format>` — формат вывода (raw, short)

**Примеры:**
```bash
# Логи production
vercel logs

# Логи конкретного deployment
vercel logs my-app-abc123.vercel.app

# Real-time логи
vercel logs --follow

# Последние 100 записей
vercel logs --limit 100

# Фильтр по функции
vercel logs --filter="/api/hello"

# Логи за последний час
vercel logs --since 1h

# Логи с временного промежутка
vercel logs --since "2024-01-01" --until "2024-01-02"
```

**Форматы времени:**
- `1h` — 1 час назад
- `30m` — 30 минут назад
- `1d` — 1 день назад
- `2024-01-01` — конкретная дата

**⚠️ Retention:**
- Hobby: 1 час
- Pro: 1 день
- Enterprise: custom

**См. также:** `vercel dev`

---

## Environment Variables

### `vercel env`

**Назначение:** Управление environment variables

**Команды:**
- `vercel env ls` — список переменных
- `vercel env add` — добавить переменную
- `vercel env rm` — удалить переменную
- `vercel env pull` — скачать переменные локально

---

#### `vercel env add`

**Назначение:** Добавить environment variable

**Синтаксис:**
```bash
vercel env add <name> [environment] [опции]
```

**Окружения:**
- `production` — production
- `preview` — preview deployments
- `development` — `vercel dev`

**Примеры:**
```bash
# Добавить переменную (интерактивно)
vercel env add API_KEY

# Для production
vercel env add API_KEY production

# Для всех окружений
vercel env add API_KEY production preview development

# Из stdin
echo "secret-value" | vercel env add API_KEY production
```

**См. также:** `vercel env pull`

---

#### `vercel env pull`

**Назначение:** Скачать переменные в локальный файл

**Синтаксис:**
```bash
vercel env pull [file] [опции]
```

**Опции:**
- `--environment <env>` — конкретное окружение
- `--yes` / `-y` — без подтверждения

**Примеры:**
```bash
# Скачать в .env.local
vercel env pull

# В другой файл
vercel env pull .env.development

# Development переменные
vercel env pull --environment development

# Без подтверждения
vercel env pull --yes
```

**Использование:**
```javascript
// Теперь в проекте доступны переменные
const apiKey = process.env.API_KEY
```

**См. также:** `vercel dev`, `vercel env add`

---

#### `vercel env ls`

**Назначение:** Список всех environment variables

**Синтаксис:**
```bash
vercel env ls [environment] [опции]
```

**Примеры:**
```bash
# Все переменные
vercel env ls

# Только production
vercel env ls production

# Только preview
vercel env ls preview
```

**Вывод:**
```
  API_KEY              production, preview, development
  DATABASE_URL         production
  NEXT_PUBLIC_API_URL  production, preview, development
```

**См. также:** `vercel env add`, `vercel env rm`

---

#### `vercel env rm`

**Назначение:** Удалить environment variable

**Синтаксис:**
```bash
vercel env rm <name> [environment] [опции]
```

**Примеры:**
```bash
# Удалить из всех окружений (интерактивно)
vercel env rm API_KEY

# Удалить из production
vercel env rm API_KEY production

# Удалить из нескольких окружений
vercel env rm API_KEY production preview
```

**⚠️ Важно:** Требуется ре-деплой для применения изменений

**См. также:** `vercel env add`

---

## Домены

### `vercel domains`

**Назначение:** Управление доменами

**Команды:**
- `vercel domains ls` — список доменов
- `vercel domains add` — добавить домен
- `vercel domains rm` — удалить домен
- `vercel domains inspect` — информация о домене
- `vercel domains buy` — купить домен

---

#### `vercel domains add`

**Назначение:** Добавить custom domain к проекту

**Синтаксис:**
```bash
vercel domains add <domain> [опции]
```

**Примеры:**
```bash
# Добавить домен
vercel domains add example.com

# Добавить поддомен
vercel domains add blog.example.com

# Добавить к конкретному проекту
vercel domains add example.com --scope my-team
```

**После добавления:**
1. Настроить DNS у регистратора
2. Подождать распространения DNS
3. Vercel автоматически выпустит SSL

**DNS настройки:**
```
# A Record (корневой домен)
Type: A
Name: @
Value: 76.76.21.21

# CNAME (поддомен)
Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

**См. также:** `vercel domains inspect`

---

#### `vercel domains ls`

**Назначение:** Список всех доменов

**Синтаксис:**
```bash
vercel domains ls [опции]
```

**Примеры:**
```bash
# Все домены
vercel domains ls

# Для конкретной команды
vercel domains ls --scope my-team
```

**Вывод:**
```
  example.com         my-app    Verified
  blog.example.com    my-blog   Verified
  test.com            my-test   Pending
```

**См. также:** `vercel domains add`

---

#### `vercel domains inspect`

**Назначение:** Информация о домене и его конфигурации

**Синтаксис:**
```bash
vercel domains inspect <domain> [опции]
```

**Примеры:**
```bash
# Информация о домене
vercel domains inspect example.com
```

**Вывод:**
```json
{
  "domain": "example.com",
  "verified": true,
  "nameservers": ["ns1.vercel-dns.com", "ns2.vercel-dns.com"],
  "intendedNameservers": ["ns1.vercel-dns.com", "ns2.vercel-dns.com"],
  "creator": "user@example.com",
  "created": 1609459200000
}
```

**См. также:** `vercel domains add`

---

#### `vercel domains rm`

**Назначение:** Удалить домен из проекта

**Синтаксис:**
```bash
vercel domains rm <domain> [опции]
```

**Примеры:**
```bash
# Удалить домен
vercel domains rm example.com

# Без подтверждения
vercel domains rm example.com --yes
```

**⚠️ Важно:** Домен перестанет указывать на ваш проект

**См. также:** `vercel domains add`

---

#### `vercel domains buy`

**Назначение:** Купить домен через Vercel

**Синтаксис:**
```bash
vercel domains buy <domain> [опции]
```

**Примеры:**
```bash
# Купить домен
vercel domains buy example.com
```

**Особенности:**
- Автоматическая настройка DNS
- Автоматический SSL
- Renewal автоматически

**См. также:** `vercel domains add`

---

## Проекты

### `vercel projects`

**Назначение:** Управление проектами

**Команды:**
- `vercel projects ls` — список проектов
- `vercel projects add` — создать проект
- `vercel projects rm` — удалить проект

---

#### `vercel projects ls`

**Назначение:** Список всех проектов

**Синтаксис:**
```bash
vercel projects ls [опции]
```

**Примеры:**
```bash
# Все проекты
vercel projects ls

# С пагинацией
vercel projects ls --next 20
```

**Вывод:**
```
  my-app       3 deployments  Updated 2m ago
  my-blog      15 deployments Updated 1h ago
  my-api       42 deployments Updated 3h ago
```

**См. также:** `vercel projects add`

---

#### `vercel projects add`

**Назначение:** Создать новый проект

**Синтаксис:**
```bash
vercel projects add <name> [опции]
```

**Примеры:**
```bash
# Создать проект
vercel projects add my-new-app
```

**См. также:** `vercel link`

---

#### `vercel projects rm`

**Назначение:** Удалить проект

**Синтаксис:**
```bash
vercel projects rm <name> [опции]
```

**Примеры:**
```bash
# Удалить проект
vercel projects rm my-app

# Без подтверждения
vercel projects rm my-app --yes
```

**⚠️ Важно:** Все deployments будут удалены

**См. также:** `vercel projects ls`

---

### `vercel link`

**Назначение:** Связать локальную директорию с Vercel проектом

**Синтаксис:**
```bash
vercel link [опции]
```

**Опции:**
- `--yes` / `-y` — без подтверждения
- `--project <name>` — указать имя проекта
- `--repo` — автоматически определить из Git

**Примеры:**
```bash
# Линк (интерактивно)
vercel link

# К конкретному проекту
vercel link --project my-app

# Без подтверждений
vercel link --yes
```

**Результат:**
- Создаётся папка `.vercel/`
- Файл `.vercel/project.json` с project ID

**См. также:** `vercel unlink`

---

### `vercel unlink`

**Назначение:** Отвязать локальную директорию

**Синтаксис:**
```bash
vercel unlink [опции]
```

**Примеры:**
```bash
# Отвязать
vercel unlink
```

**Результат:** Удаляется папка `.vercel/`

**См. также:** `vercel link`

---

## Secrets

### `vercel secrets`

**Назначение:** Управление secrets (защищённые переменные)

**Команды:**
- `vercel secrets ls` — список secrets
- `vercel secrets add` — добавить secret
- `vercel secrets rename` — переименовать
- `vercel secrets rm` — удалить

---

#### `vercel secrets add`

**Назначение:** Добавить secret

**Синтаксис:**
```bash
vercel secrets add <name> <value> [опции]
```

**Примеры:**
```bash
# Добавить secret
vercel secrets add my-secret "secret-value"

# Из stdin
echo "secret-value" | vercel secrets add my-secret

# Из файла
cat secret.txt | vercel secrets add my-secret
```

**Использование в vercel.json:**
```json
{
  "env": {
    "API_KEY": "@my-secret"
  }
}
```

**См. также:** `vercel env add`

---

## Team Management

### `vercel teams`

**Назначение:** Управление командами

**Команды:**
- `vercel teams ls` — список команд
- `vercel teams add` — создать команду
- `vercel teams switch` — переключить команду

---

#### `vercel switch`

**Назначение:** Переключиться между личным аккаунтом и командой

**Синтаксис:**
```bash
vercel switch [team-slug] [опции]
```

**Примеры:**
```bash
# Список доступных scopes
vercel switch

# Переключиться на команду
vercel switch my-team

# Переключиться на личный аккаунт
vercel switch
```

**См. также:** `vercel teams ls`

---

## Прочие команды

### `vercel help`

**Назначение:** Справка по командам

**Синтаксис:**
```bash
vercel help [command]
```

**Примеры:**
```bash
# Общая справка
vercel help

# Справка по команде
vercel help deploy
vercel help env
vercel help domains
```

---

### `vercel --version`

**Назначение:** Показать версию CLI

**Синтаксис:**
```bash
vercel --version
```

**Вывод:**
```
Vercel CLI 33.0.0
```

---

## Глобальные опции

Доступны для всех команд:

```bash
--debug             # Включить debug режим
--scope <team>      # Выполнить от имени команды
--token <token>     # Использовать токен
--yes / -y          # Пропустить подтверждения
--help / -h         # Справка
```

**Примеры:**
```bash
# Debug mode
vercel --debug

# От имени команды
vercel --scope my-team

# С токеном (CI/CD)
vercel --token $VERCEL_TOKEN --prod
```

---

## CI/CD интеграция

### GitHub Actions

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: npm install --global vercel@latest
      - run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
      - run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}
      - run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
```

### GitLab CI

```yaml
deploy:
  script:
    - npm install --global vercel
    - vercel pull --yes --environment=production --token=$VERCEL_TOKEN
    - vercel build --prod --token=$VERCEL_TOKEN
    - vercel deploy --prebuilt --prod --token=$VERCEL_TOKEN
  only:
    - main
```

### Необходимые переменные

```bash
VERCEL_TOKEN        # Создать на vercel.com/account/tokens
VERCEL_ORG_ID       # Из .vercel/project.json
VERCEL_PROJECT_ID   # Из .vercel/project.json
```

---

**Больше информации:**
- **FAQ:** `faq.md`
- **Troubleshooting:** `troubleshooting.md`
- **Cheatsheet:** `cheatsheet.md`
