---
name: git-github-spravochnik
description: "Используй когда пользователь спрашивает о Git, GitHub, ветках, коммитах, CI/CD, GitHub Actions. При запросе о деплое через GitHub, настройке Git на Windows, Git Bash. Полное руководство по Git и GitHub для Windows с Git Bash."
---
# Git & GitHub Справочник

> **Назначение:** Полное руководство по Git и GitHub для Windows с Git Bash. Включает установку, основные команды, командную работу, CI/CD и решение типичных проблем.

## Когда использовать

Используй этот скилл когда пользователь спрашивает о:
- Git командах (commit, push, pull, branch, merge)
- GitHub (репозитории, PR, Issues, Actions)
- Настройке Git на Windows / Git Bash
- CI/CD через GitHub Actions
- Деплое через GitHub Integration

**Для кого:** Разработчики, работающие с Git на Windows, от новичков до опытных пользователей.

**Версия:** 1.1
**Последнее обновление:** 2026-02-17

---

## Содержание

- [Модуль 0: Установка и настройка (Windows + Git Bash)](#модуль-0-установка-и-настройка-windows--git-bash)
- [Модуль 1: Git Basics](#модуль-1-git-basics)
- [Модуль 2: GitHub Integration](#модуль-2-github-integration)
- [Модуль 3: Branches (ветки)](#модуль-3-branches-ветки)
- [Модуль 4: Collaboration (командная работа)](#модуль-4-collaboration-командная-работа)
- [Модуль 5: GitHub Actions](#модуль-5-github-actions)
- [Модуль 6: Deployment](#модуль-6-deployment)
- [Модуль 7: .gitignore](#модуль-7-gitignore)
- [Модуль 8: Advanced Topics](#модуль-8-advanced-topics)
- [Типичные ошибки](#типичные-ошибки)
- [Дополнительные ресурсы](#дополнительные-ресурсы)

---

## Модуль 0: Установка и настройка (Windows + Git Bash)

### Установка Git для Windows

**Шаг 1: Скачивание**

1. Перейдите на https://git-scm.com/download/win
2. Скачайте последнюю версию (64-bit Git for Windows Setup)
3. Запустите установщик

**Шаг 2: Настройка установщика**

Рекомендуемые опции:

| Опция | Выбор | Пояснение |
|-------|-------|-----------|
| Default editor | Visual Studio Code / Nano | Редактор для коммитов |
| PATH environment | Git from the command line and also from 3rd-party software | Доступ из любого терминала |
| SSH executable | Use bundled OpenSSH | Встроенный SSH |
| HTTPS transport | Use the OpenSSL library | Стандартная библиотека |
| Line ending conversions | Checkout Windows-style, commit Unix-style | Кросс-платформенность |
| Terminal emulator | Use MinTTY | Git Bash терминал |

**Шаг 3: Проверка установки**

Откройте Git Bash и выполните:

```bash
git --version
# Ожидаемый вывод: git version 2.xx.x
```

### Первая настройка

**Установка имени и email (обязательно!):**

```bash
git config --global user.name "Ваше Имя"
git config --global user.email "your.email@example.com"
```

**Проверка конфигурации:**

```bash
git config --list
# Или просмотр конкретных значений:
git config user.name
git config user.email
```

**Дополнительные полезные настройки:**

```bash
# Цветной вывод
git config --global color.ui auto

# Редактор по умолчанию (VSCode)
git config --global core.editor "code --wait"

# Алиасы для частых команд
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.cm commit
```

### КРИТИЧНО: Конвертация путей Windows для Git Bash

Git Bash использует Unix-стиль путей. Windows пути нужно конвертировать.

**Правила конвертации:**

| Windows путь | Git Bash путь | Правило |
|--------------|---------------|---------|
| `C:\Users\londo` | `/c/Users/londo` | `C:\` → `/c/` |
| `D:\Downloads\project` | `/d/Downloads/project` | `D:\` → `/d/` |
| `E:\Work\MyApp` | `/e/Work/MyApp` | `E:\` → `/e/` |

**Ключевые моменты:**

1. **Диск:** `D:\` превращается в `/d/` (строчная буква!)
2. **Слеши:** Обратные слеши `\` заменяются на прямые `/`
3. **Регистр:** Сохраняется регистр папок

**Примеры команд:**

```bash
# Windows: D:\Downloads\CV_Project
cd /d/Downloads/CV_Project

# Windows: C:\Users\londo\Documents\project
cd /c/Users/londo/Documents/project

# Инициализация репозитория в Windows папке
cd /d/Downloads/MyProject
git init
```

**Быстрая конвертация:**

```bash
# Текущая директория в Windows формате
pwd -W
# Вывод: D:\Downloads\project

# Текущая директория в Git Bash формате
pwd
# Вывод: /d/Downloads/project
```

**Копирование путей из Explorer:**

1. В Windows Explorer скопируйте путь: `D:\Downloads\project`
2. В Git Bash конвертируйте: `/d/Downloads/project`
3. Используйте в командах: `cd /d/Downloads/project`

---

## Модуль 1: Git Basics

Git работает в три этапа: `Working Directory → Staging Area → Repository`

### Основные команды

| Команда | Назначение | Пример |
|---------|-----------|--------|
| `git init` | Создание репозитория | `cd /d/Downloads/MyProject && git init` |
| `git add` | Добавление в staging | `git add .` (все) / `git add file.txt` (один) |
| `git commit` | Сохранение изменений | `git commit -m "Описание"` |
| `git status` | Проверка состояния | `git status` |
| `git log` | История коммитов | `git log --oneline --graph --all` |
| `git diff` | Просмотр изменений | `git diff` (рабочая) / `git diff --staged` |

**git add — варианты:**

| Команда | Что добавляет |
|---------|---------------|
| `git add file.txt` | Только указанный файл |
| `git add .` | Все изменения в текущей папке и подпапках |
| `git add -A` | Все изменения во всем проекте (включая удаления) |
| `git add -u` | Только измененные файлы (без новых) |

**Правила хороших commit messages:** до 50 символов, императив ("Добавь", "Исправь"), контекст что и зачем.

> Подробные примеры каждой команды: см. `references/git-commands-cheatsheet.md`

---

## Модуль 2: GitHub Integration

### Аутентификация

С 2021 года GitHub не принимает пароли. Два способа аутентификации:

| Способ | Когда использовать | Подробнее |
|--------|-------------------|-----------|
| **PAT (Personal Access Token)** | Временный доступ, CI/CD, скрипты | `references/pat-authentication.md` |
| **SSH ключи** | Постоянная работа (рекомендуется) | `references/ssh-setup-windows.md` |

**Быстрый старт PAT:** GitHub → Settings → Developer settings → Tokens (classic) → Generate → scope `repo` → скопировать токен → использовать вместо пароля при push.

**Быстрый старт SSH:** `ssh-keygen -t ed25519 -C "email"` → `cat ~/.ssh/id_ed25519.pub` → добавить на GitHub → `ssh -T git@github.com` для проверки.

> Подробные пошаговые инструкции: см. `references/pat-authentication.md` и `references/ssh-setup-windows.md`

### git remote — Подключение к GitHub

**Добавление remote репозитория:**

```bash
# HTTPS (требует PAT)
git remote add origin https://github.com/username/repo.git

# SSH (требует SSH ключ)
git remote add origin git@github.com:username/repo.git

# Просмотр remotes
git remote -v
```

### git push — Отправка в GitHub

**Первая отправка:**

```bash
# Отправка ветки main в origin
git push -u origin main

# -u (--set-upstream) устанавливает связь между локальной и удаленной веткой
# После этого можно использовать просто: git push
```

**Последующие отправки:**

```bash
# Отправка изменений
git push

# Отправка конкретной ветки
git push origin feature-branch

# Принудительная отправка (ОСТОРОЖНО!)
git push --force
```

### git pull — Получение изменений

**Загрузка изменений с GitHub:**

```bash
# Получение и слияние изменений
git pull

# Эквивалентно:
git fetch  # Загрузка изменений
git merge  # Слияние изменений

# Pull с rebase (чище история)
git pull --rebase
```

### git clone — Клонирование репозитория

**Скачивание репозитория с GitHub:**

```bash
# HTTPS
git clone https://github.com/username/repo.git

# SSH
git clone git@github.com:username/repo.git

# Клонирование в конкретную папку
git clone https://github.com/username/repo.git /d/Downloads/MyProject

# Клонирование конкретной ветки
git clone -b develop https://github.com/username/repo.git
```

---

## Модуль 3: Branches (ветки)

Ветки позволяют работать над разными функциями параллельно без конфликтов.

### Основные команды веток

```bash
git branch                    # Список веток
git branch feature-login      # Создать ветку
git checkout -b feature-login # Создать и переключиться
git switch -c feature-login   # То же (Git 2.23+)
git checkout main             # Переключиться на main
git merge feature-login       # Слить ветку в текущую
git branch -d feature-login   # Удалить ветку
```

### Конфликты при merge (кратко)

При конфликте Git добавляет маркеры `<<<<<<< HEAD`, `=======`, `>>>>>>> branch`. Решение: отредактировать файл, убрать маркеры, затем `git add file && git commit`.

### Именование веток

| Тип | Префикс | Пример |
|-----|---------|--------|
| Новая функция | `feature/` | `feature/user-auth` |
| Исправление | `fix/` | `fix/login-error` |
| Хотфикс | `hotfix/` | `hotfix/critical-bug` |
| Релиз | `release/` | `release/v1.2.0` |

> Подробные сценарии, merge conflicts, rebase, workflow стратегии: см. `references/branches-guide.md`

---

## Модуль 4: Collaboration (командная работа)

### Fork репозитория

**Fork** — это копия чужого репозитория в вашем GitHub аккаунте.

**Когда использовать:**

- Вы хотите внести изменения в чужой проект
- У вас нет прав на запись в оригинальный репозиторий
- Вы хотите экспериментировать с чужим кодом

**Процесс:**

1. Откройте репозиторий на GitHub
2. Нажмите кнопку "Fork" (правый верхний угол)
3. Выберите ваш аккаунт как destination
4. Клонируйте fork на локальную машину:

```bash
git clone https://github.com/YOUR-USERNAME/repo.git
cd repo
```

**Настройка upstream (оригинальный репозиторий):**

```bash
# Добавление upstream remote
git remote add upstream https://github.com/ORIGINAL-OWNER/repo.git

# Проверка remotes
git remote -v
# origin    https://github.com/YOUR-USERNAME/repo.git (fetch)
# origin    https://github.com/YOUR-USERNAME/repo.git (push)
# upstream  https://github.com/ORIGINAL-OWNER/repo.git (fetch)
# upstream  https://github.com/ORIGINAL-OWNER/repo.git (push)
```

### Pull Requests (PRs) — Создание и review

**Pull Request** — запрос на слияние вашей ветки в основную ветку (обычно main).

#### Создание Pull Request

**Шаг 1: Создание feature ветки**

```bash
git checkout -b feature/add-navbar
```

**Шаг 2: Внесение изменений**

```bash
# Редактируйте файлы
git add .
git commit -m "Добавлена навигационная панель"
```

**Шаг 3: Push ветки на GitHub**

```bash
git push origin feature/add-navbar
```

**Шаг 4: Создание PR на GitHub**

1. Перейдите в репозиторий на GitHub
2. Нажмите "Compare & pull request" (появится автоматически)
3. Заполните форму:
   - **Title:** Краткое описание (например, "Добавлена навигационная панель")
   - **Description:** Детали изменений, причины, screenshot'ы
4. Нажмите "Create pull request"

**Хороший PR description:**

```markdown
## Что изменено
- Добавлена навигационная панель с логотипом и меню
- Адаптивный дизайн для мобильных устройств

## Зачем
Улучшение UX: пользователи теперь могут легко навигировать по сайту

## Скриншоты
[Вставьте изображения]

## Тестирование
- [ ] Проверено на Chrome
- [ ] Проверено на Firefox
- [ ] Проверено на мобильных устройствах
```

#### Code Review процесс

**Reviewer проверяет:**

1. **Функциональность:** Работает ли код как задумано?
2. **Качество кода:** Читаемость, стиль, best practices
3. **Тесты:** Есть ли тесты для новой функциональности?
4. **Документация:** Обновлена ли документация?

**Оставление комментариев:**

На GitHub:
1. Перейдите в PR → Files changed
2. Наведите на строку → нажмите "+"
3. Оставьте комментарий → "Add single comment" или "Start a review"

**Типы review:**

- **Approve:** Изменения хорошие, можно сливать
- **Request changes:** Нужны исправления
- **Comment:** Общие комментарии без блокировки

**Внесение исправлений после review:**

```bash
# Внесите изменения в том же branch
git add .
git commit -m "Исправлены замечания reviewer'а"
git push origin feature/add-navbar

# PR обновится автоматически!
```

### Issues — Создание и управление

**Issue** — это задача, баг, или предложение для проекта.

**Создание Issue:**

1. Перейдите в репозиторий → Issues → New issue
2. Заполните форму:
   - **Title:** Краткое описание проблемы
   - **Description:** Детали, шаги воспроизведения, ожидаемое поведение
3. Добавьте labels (bug, enhancement, question, etc.)
4. Назначьте assignee (кто будет работать)
5. Нажмите "Submit new issue"

**Пример хорошего bug report:**

```markdown
## Описание
Кнопка "Войти" не работает на мобильных устройствах

## Шаги воспроизведения
1. Открыть сайт на iPhone
2. Перейти на страницу входа
3. Ввести логин и пароль
4. Нажать "Войти"

## Ожидаемое поведение
Пользователь авторизуется и перенаправляется в личный кабинет

## Фактическое поведение
Ничего не происходит, консоль показывает ошибку

## Окружение
- Устройство: iPhone 12
- ОС: iOS 15
- Браузер: Safari 15

## Дополнительно
[Скриншот или видео]
```

**Связывание PR с Issue:**

```bash
# В commit message или PR description укажите:
git commit -m "Исправлена кнопка входа (fixes #42)"

# Когда PR будет слит, issue #42 автоматически закроется
```

**Ключевые слова для автозакрытия:**

- `fixes #42` / `fix #42`
- `closes #42` / `close #42`
- `resolves #42` / `resolve #42`

### Workflow: fork → branch → PR

**Полный процесс контрибуции в чужой проект:**

```bash
# 1. Fork репозитория на GitHub (кнопка Fork)

# 2. Клонирование fork
git clone https://github.com/YOUR-USERNAME/repo.git
cd repo

# 3. Добавление upstream
git remote add upstream https://github.com/ORIGINAL-OWNER/repo.git

# 4. Создание feature ветки
git checkout -b feature/my-contribution

# 5. Внесение изменений
# ... редактируйте файлы ...
git add .
git commit -m "Добавлена новая функция"

# 6. Синхронизация с upstream (важно!)
git fetch upstream
git rebase upstream/main

# 7. Push в ваш fork
git push origin feature/my-contribution

# 8. Создание PR на GitHub
# Перейдите на GitHub → Compare & pull request

# 9. После merge: очистка
git checkout main
git pull upstream main
git branch -d feature/my-contribution
```

### Команды для синхронизации форка

**Обновление fork до актуального состояния upstream:**

```bash
# Получение последних изменений из upstream
git fetch upstream

# Слияние изменений в локальную main
git checkout main
git merge upstream/main

# Или rebase для линейной истории
git rebase upstream/main

# Отправка обновлений в ваш fork на GitHub
git push origin main
```

**Автоматизация с помощью алиаса:**

```bash
git config --global alias.sync '!git fetch upstream && git checkout main && git merge upstream/main && git push origin main'

# Использование:
git sync
```

---

## Модуль 5: GitHub Actions

### Что такое GitHub Actions

**GitHub Actions** — это CI/CD платформа от GitHub для автоматизации workflows.

**Возможности:**

- Запуск тестов при каждом push
- Автоматический деплой при merge в main
- Создание релизов
- Линтинг кода
- Отправка уведомлений

**Основные понятия:**

| Термин | Описание |
|--------|----------|
| **Workflow** | Автоматизированный процесс (.yml файл) |
| **Job** | Набор шагов (steps) |
| **Step** | Отдельная задача (run command или action) |
| **Action** | Переиспользуемый модуль (от GitHub или community) |
| **Runner** | Сервер, где выполняется workflow |
| **Event** | Триггер (push, pull_request, schedule, etc.) |

**Где хранятся workflows:**

```
.github/
└── workflows/
    ├── ci.yml
    ├── deploy.yml
    └── tests.yml
```

### CI/CD автоматизация

**CI (Continuous Integration):** Автоматическая проверка кода при каждом изменении.

**CD (Continuous Deployment/Delivery):** Автоматическое развертывание приложения.

**Типичный CI/CD pipeline:**

```
Push → Run Tests → Lint Code → Build → Deploy
```

### Примеры workflows

#### Пример 1: Автотесты при push

**Файл:** `.github/workflows/tests.yml`

```yaml
name: Run Tests

# Когда запускать
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

# Задачи
jobs:
  test:
    # На какой ОС запускать
    runs-on: ubuntu-latest

    steps:
      # 1. Checkout кода
      - name: Checkout code
        uses: actions/checkout@v3

      # 2. Установка Node.js
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      # 3. Установка зависимостей
      - name: Install dependencies
        run: npm ci

      # 4. Запуск тестов
      - name: Run tests
        run: npm test

      # 5. Проверка покрытия
      - name: Check coverage
        run: npm run coverage
```

**Расшифровка:**

- `on:` — триггеры (push в main/develop, любой PR в main)
- `runs-on:` — ОС (ubuntu-latest, windows-latest, macos-latest)
- `uses:` — готовый action
- `run:` — bash команда

#### Пример 2: Деплой на Netlify

**Файл:** `.github/workflows/deploy.yml`

```yaml
name: Deploy to Netlify

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Build project
        run: npm run build

      - name: Deploy to Netlify
        uses: netlify/actions/cli@master
        with:
          args: deploy --prod --dir=dist
        env:
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
```

**Секреты (secrets):**

Храните токены и пароли в Settings → Secrets → Actions → New repository secret

#### Пример 3: Линтинг и форматирование

**Файл:** `.github/workflows/lint.yml`

```yaml
name: Lint Code

on:
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run ESLint
        run: npm run lint

      - name: Check Prettier formatting
        run: npm run format:check
```

### Создание простого workflow файла

**Пошаговое создание:**

**Шаг 1: Создание структуры**

```bash
mkdir -p .github/workflows
cd .github/workflows
```

**Шаг 2: Создание файла**

```bash
# В Git Bash
touch ci.yml
```

**Шаг 3: Базовый workflow**

```yaml
name: My First Workflow

on: [push]

jobs:
  greet:
    runs-on: ubuntu-latest

    steps:
      - name: Say hello
        run: echo "Hello, GitHub Actions!"

      - name: Show date
        run: date
```

**Шаг 4: Commit и push**

```bash
git add .github/workflows/ci.yml
git commit -m "Добавлен GitHub Actions workflow"
git push origin main
```

**Шаг 5: Просмотр результата**

1. Перейдите на GitHub → ваш репозиторий
2. Вкладка "Actions"
3. Увидите запущенный workflow

**Статусы:**

- Желтый кружок — выполняется
- Зеленая галочка — успешно
- Красный крестик — ошибка

**Полезные триггеры:**

```yaml
# Только при push в main
on:
  push:
    branches: [ main ]

# По расписанию (каждый день в полночь UTC)
on:
  schedule:
    - cron: '0 0 * * *'

# Ручной запуск
on:
  workflow_dispatch:

# При создании релиза
on:
  release:
    types: [published]
```

---

## Модуль 6: Deployment

### GitHub Pages

**GitHub Pages** — бесплатный хостинг статических сайтов от GitHub.

**Возможности:**

- HTML, CSS, JS (без backend)
- Custom домены
- HTTPS по умолчанию
- URL: `https://username.github.io/repo-name/`

#### Настройка GitHub Pages

**Вариант 1: Из ветки main**

1. Перейдите в Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main` / `(root)` или `main` / `/docs`
4. Save

**Вариант 2: Из папки docs/**

```bash
# Создайте папку docs
mkdir docs
mv index.html docs/

# Commit и push
git add docs/
git commit -m "Добавлена папка docs для GitHub Pages"
git push origin main

# В Settings → Pages выберите: main / /docs
```

**Вариант 3: GitHub Actions (рекомендуется для build процесса)**

**Файл:** `.github/workflows/deploy-pages.yml`

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-pages-artifact@v1
        with:
          path: ./dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v1
```

**Настройка в Settings:**

Settings → Pages → Source: GitHub Actions

### Интеграция с Netlify

**Netlify** — популярная платформа для деплоя фронтенда с CI/CD.

**Преимущества:**

- Автоматический деплой при push
- Preview для каждого PR
- Serverless functions
- Form handling

#### Деплой через Netlify UI

**Шаг 1: Регистрация**

1. Перейдите на https://netlify.com
2. Sign up (можно через GitHub)

**Шаг 2: Подключение репозитория**

1. New site → Import an existing project
2. Connect to Git provider → GitHub
3. Выберите репозиторий
4. Настройки:
   - Branch: `main`
   - Build command: `npm run build`
   - Publish directory: `dist` (или `build`)
5. Deploy site

**Шаг 3: Custom domain (опционально)**

1. Site settings → Domain management
2. Add custom domain → введите ваш домен
3. Настройте DNS записи у регистратора

#### Деплой через Netlify CLI

```bash
# Установка Netlify CLI
npm install -g netlify-cli

# Вход в аккаунт
netlify login

# Инициализация
netlify init

# Деплой
netlify deploy --prod
```

#### Netlify TOML конфигурация

**Файл:** `netlify.toml` (в корне проекта)

```toml
[build]
  command = "npm run build"
  publish = "dist"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Интеграция с Vercel

**Vercel** — платформа для фронтенда и serverless, создатели Next.js.

**Преимущества:**

- Мгновенный деплой
- Edge Network (быстрая загрузка по всему миру)
- Preview deployments
- Serverless functions

#### Деплой через Vercel UI

**Шаг 1: Регистрация**

1. Перейдите на https://vercel.com
2. Sign up через GitHub

**Шаг 2: Импорт проекта**

1. New Project → Import Git Repository
2. Выберите репозиторий
3. Настройки (Vercel автоопределяет framework):
   - Framework Preset: Vite / React / Next.js / etc.
   - Root Directory: `./`
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. Deploy

#### Деплой через Vercel CLI

```bash
# Установка Vercel CLI
npm install -g vercel

# Вход в аккаунт
vercel login

# Деплой
vercel

# Production деплой
vercel --prod
```

#### Vercel конфигурация

**Файл:** `vercel.json`

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Автоматический деплой при push

**Все три платформы (GitHub Pages, Netlify, Vercel) поддерживают автодеплой:**

1. **Подключите репозиторий** к платформе
2. **Каждый push в main** → автоматический деплой
3. **Каждый PR** → preview deployment (Netlify, Vercel)

**Статус деплоя в PR:**

GitHub показывает статус деплоя прямо в Pull Request:

- "Deploy preview ready" — preview доступен
- "All checks have passed" — деплой успешен

---

## Модуль 7: .gitignore

### Что такое .gitignore

**`.gitignore`** — файл, указывающий Git, какие файлы НЕ нужно отслеживать.

**Зачем игнорировать файлы:**

1. **Секреты:** `.env`, `credentials.json`, токены
2. **Зависимости:** `node_modules/`, `venv/`, `vendor/`
3. **Сгенерированные файлы:** `dist/`, `build/`, `.cache/`
4. **Системные файлы:** `.DS_Store`, `Thumbs.db`, `.idea/`
5. **Логи:** `*.log`, `logs/`
6. **Временные файлы:** `*.tmp`, `*.swp`

### Создание .gitignore

**Создание файла:**

```bash
# В корне проекта
touch .gitignore
```

**Базовая структура:**

```gitignore
# Комментарии начинаются с #

# Игнорировать конкретный файл
secret.txt

# Игнорировать все файлы с расширением
*.log

# Игнорировать папку
node_modules/

# НЕ игнорировать конкретный файл (исключение)
!important.log
```

### Готовые шаблоны

#### Node.js проект

```gitignore
# Зависимости
node_modules/
npm-debug.log
yarn-error.log
package-lock.json  # Опционально

# Production build
dist/
build/
.cache/

# Переменные окружения
.env
.env.local
.env.production

# Логи
logs/
*.log

# OS файлы
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
```

#### Python проект

```gitignore
# Byte-compiled / optimized
__pycache__/
*.py[cod]
*$py.class

# Virtual environment
venv/
env/
ENV/

# Distribution / packaging
build/
dist/
*.egg-info/

# Pytest
.pytest_cache/
.coverage

# Jupyter Notebook
.ipynb_checkpoints

# Environment variables
.env

# OS
.DS_Store
```

#### React проект (Vite)

```gitignore
# Dependencies
node_modules/

# Production
dist/
build/

# Development
.vite/
.cache/

# Environment
.env
.env.local
.env.production

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Editor
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

### Распространенные паттерны

**Синтаксис .gitignore:**

| Паттерн | Описание | Пример |
|---------|----------|--------|
| `file.txt` | Конкретный файл | `secret.txt` |
| `*.log` | Все файлы с расширением | `error.log`, `app.log` |
| `folder/` | Вся папка | `node_modules/` |
| `**/temp` | Папка на любом уровне | `src/temp`, `lib/temp` |
| `!file.txt` | НЕ игнорировать (исключение) | `!important.txt` |
| `doc/*.pdf` | PDF только в doc/, не в подпапках | `doc/file.pdf` |
| `doc/**/*.pdf` | PDF в doc/ и всех подпапках | `doc/sub/file.pdf` |

**Примеры:**

```gitignore
# Игнорировать все .txt файлы
*.txt

# Кроме README.txt
!README.txt

# Игнорировать todos.txt в корне, но не в подпапках
/todos.txt

# Игнорировать build/ в корне
/build/

# Игнорировать все PDF в doc/ и подпапках
doc/**/*.pdf
```

### Игнорирование уже отслеживаемых файлов

**Проблема:** Файл уже в Git, но вы хотите его игнорировать.

**Решение:**

```bash
# Удалить файл из Git (но оставить локально)
git rm --cached secret.txt

# Удалить папку из Git
git rm -r --cached node_modules/

# Добавить в .gitignore
echo "secret.txt" >> .gitignore
echo "node_modules/" >> .gitignore

# Commit
git add .gitignore
git commit -m "Добавлен .gitignore и удалены ненужные файлы из Git"
```

### Глобальный .gitignore

**Игнорирование файлов во ВСЕХ проектах:**

```bash
# Создание глобального .gitignore
touch ~/.gitignore_global

# Настройка Git
git config --global core.excludesfile ~/.gitignore_global
```

**Содержимое `~/.gitignore_global`:**

```gitignore
# OS
.DS_Store
Thumbs.db
desktop.ini

# Editor
.vscode/
.idea/
*.swp
*.swo
*~

# Temporary
*.tmp
*.temp
```

### Проверка игнорирования

```bash
# Показать игнорируемые файлы
git status --ignored

# Проверить, почему файл игнорируется
git check-ignore -v file.txt
# Вывод: .gitignore:10:*.txt    file.txt
```

---

## Модуль 8: Advanced Topics

### git stash — Временное сохранение

**Сценарий:** Вы работаете над функцией, но вам нужно срочно переключиться на другую ветку.

**Проблема:** Git не позволит переключиться, если есть незакоммиченные изменения.

**Решение: stash**

```bash
# Сохранить текущие изменения
git stash

# Или с описанием
git stash save "Работа над формой входа"

# Теперь можно переключиться
git checkout main

# Вернуться обратно
git checkout feature-branch

# Восстановить изменения
git stash pop

# Или применить без удаления из stash
git stash apply
```

**Управление stash:**

```bash
# Список всех stash
git stash list
# Вывод:
# stash@{0}: WIP on feature-branch: a3c2b1f Add form
# stash@{1}: WIP on main: d4e5f6g Fix bug

# Показать содержимое stash
git stash show stash@{0}

# Применить конкретный stash
git stash apply stash@{1}

# Удалить stash
git stash drop stash@{0}

# Очистить все stash
git stash clear
```

**Stash с новыми файлами:**

```bash
# По умолчанию stash НЕ сохраняет untracked файлы
git stash

# Включить untracked файлы
git stash -u

# Включить все (включая ignored файлы)
git stash -a
```

### git tag — Версионирование

**Теги** используются для маркировки релизов (v1.0.0, v2.1.5).

**Типы тегов:**

1. **Lightweight tag:** Просто указатель на коммит
2. **Annotated tag:** Полноценный объект с именем, email, датой, сообщением (рекомендуется)

**Создание тегов:**

```bash
# Lightweight tag
git tag v1.0.0

# Annotated tag (рекомендуется)
git tag -a v1.0.0 -m "Релиз версии 1.0.0"

# Тег на конкретном коммите
git tag -a v0.9.0 abc123 -m "Релиз 0.9.0"

# Список тегов
git tag
# v0.9.0
# v1.0.0

# Показать информацию о теге
git show v1.0.0
```

**Push тегов на GitHub:**

```bash
# Push одного тега
git push origin v1.0.0

# Push всех тегов
git push origin --tags
```

**Удаление тегов:**

```bash
# Удаление локально
git tag -d v1.0.0

# Удаление на GitHub
git push origin --delete v1.0.0
```

**Semantic Versioning (semver):**

Формат: `MAJOR.MINOR.PATCH` (например, `2.4.1`)

- **MAJOR:** Несовместимые изменения API (breaking changes)
- **MINOR:** Новая функциональность (обратно совместимая)
- **PATCH:** Исправления багов

```bash
# Первый релиз
git tag -a v1.0.0 -m "Initial release"

# Исправление бага
git tag -a v1.0.1 -m "Fix login bug"

# Новая функция
git tag -a v1.1.0 -m "Add user profile"

# Breaking change
git tag -a v2.0.0 -m "New API architecture"
```

### git cherry-pick — Выборочное применение коммитов

**Сценарий:** Вы хотите применить конкретный коммит из одной ветки в другую.

**Использование:**

```bash
# 1. Найдите hash коммита
git log --oneline
# abc123 Fix critical bug
# def456 Add feature
# ghi789 Update docs

# 2. Переключитесь на целевую ветку
git checkout main

# 3. Cherry-pick коммита
git cherry-pick abc123

# Коммит abc123 теперь применен к main
```

**Множественные коммиты:**

```bash
# Cherry-pick диапазона коммитов
git cherry-pick abc123..def456

# Cherry-pick нескольких конкретных коммитов
git cherry-pick abc123 ghi789
```

**Разрешение конфликтов:**

```bash
# Если возник конфликт
git cherry-pick abc123
# CONFLICT (content): Merge conflict in file.js

# Разрешите конфликт в файле
# Затем:
git add file.js
git cherry-pick --continue

# Или отмените cherry-pick
git cherry-pick --abort
```

### git bisect — Поиск проблемного коммита

**Сценарий:** Баг появился, но вы не знаете в каком коммите.

**git bisect** выполняет бинарный поиск, чтобы найти коммит, который внес баг.

**Процесс:**

```bash
# 1. Начать bisect
git bisect start

# 2. Отметить текущий коммит как плохой (баг есть)
git bisect bad

# 3. Отметить старый рабочий коммит как хороший (бага не было)
git bisect good abc123

# Git переключит вас на средний коммит
# 4. Проверьте, есть ли баг
# Если баг есть:
git bisect bad

# Если бага нет:
git bisect good

# 5. Повторяйте, пока Git не найдет проблемный коммит
# Git выведет: "def456 is the first bad commit"

# 6. Завершение
git bisect reset
```

**Автоматический bisect (если есть тест):**

```bash
git bisect start
git bisect bad
git bisect good abc123

# Запустить автоматический bisect с тестом
git bisect run npm test

# Git автоматически найдет проблемный коммит
```

### git reflog — Восстановление потерянных коммитов

**Сценарий:** Вы случайно удалили ветку или сделали reset, и потеряли коммиты.

**git reflog** показывает историю ВСЕХ действий (даже удаленных коммитов).

**Использование:**

```bash
# Просмотр reflog
git reflog

# Вывод:
# abc123 HEAD@{0}: commit: Add feature
# def456 HEAD@{1}: checkout: moving from main to feature
# ghi789 HEAD@{2}: reset: moving to HEAD~1
# jkl012 HEAD@{3}: commit: Lost commit
```

**Восстановление потерянного коммита:**

```bash
# Найдите hash потерянного коммита
git reflog
# jkl012 HEAD@{3}: commit: Lost commit

# Создайте ветку на этом коммите
git branch recovery jkl012

# Или сразу checkout
git checkout jkl012

# Или cherry-pick
git cherry-pick jkl012
```

**Восстановление удаленной ветки:**

```bash
# Случайно удалили ветку
git branch -D feature-branch

# Найдите последний коммит ветки в reflog
git reflog | grep feature-branch
# abc123 HEAD@{5}: checkout: moving from feature-branch to main

# Восстановите ветку
git branch feature-branch abc123
```

**Очистка reflog (осторожно!):**

```bash
# Reflog хранится 90 дней по умолчанию
# Ручная очистка:
git reflog expire --expire=now --all
git gc --prune=now
```

---

## Типичные ошибки (краткий список)

| Ошибка | Решение |
|--------|---------|
| Authentication failed | Используйте PAT или SSH вместо пароля |
| Merge conflict | Редактируйте маркеры `<<<<<<`, `=======`, `>>>>>>>`, затем `git add && git commit` |
| Commit в main вместо ветки | `git branch feature && git reset --hard HEAD~1 && git checkout feature` |
| Push файлов >100 MB | `git rm --cached file && .gitignore` или Git LFS |
| Пути Windows в Git Bash | `D:\path` -> `/d/path` |
| Закоммитили node_modules | `git rm -r --cached node_modules/ && .gitignore` |
| Detached HEAD | `git checkout main` или `git checkout -b new-branch` |
| Защита main от push | GitHub Settings -> Branches -> Branch protection rules |

> Подробные решения с примерами: см. `references/troubleshooting.md`

---

## Дополнительные ресурсы

- **Документация:** https://git-scm.com/doc | https://docs.github.com
- **Интерактив:** https://learngitbranching.js.org | https://skills.github.com
- **Книга:** https://git-scm.com/book/ru/v2 (Pro Git, бесплатная)
- **.gitignore:** https://www.toptal.com/developers/gitignore | https://github.com/github/gitignore
- **GUI:** GitHub Desktop, GitKraken, Git Extensions

---

## Таблица references

| Файл | Описание |
|------|----------|
| `references/git-commands-cheatsheet.md` | Полная шпаргалка команд Git |
| `references/pat-authentication.md` | PAT аутентификация (пошагово) |
| `references/ssh-setup-windows.md` | SSH ключи на Windows |
| `references/branches-guide.md` | Ветки, merge, rebase, конфликты |
| `references/github-workflows.md` | GitHub Actions workflows |
| `references/troubleshooting.md` | Решение типичных проблем |
| `references/glossary.md` | Глоссарий терминов |
| `references/faq.md` | Часто задаваемые вопросы |

---

**Версия:** 1.1 | **Дата:** 2026-02-17 | **Лицензия:** MIT