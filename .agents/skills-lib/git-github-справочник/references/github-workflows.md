# GitHub Workflows (GitHub Actions)

Готовые примеры автоматизации с GitHub Actions для типичных задач.

---

## Содержание

1. [Основы GitHub Actions](#основы-github-actions)
2. [Автотесты Node.js](#автотесты-nodejs)
3. [Автотесты Python](#автотесты-python)
4. [Деплой на Netlify](#деплой-на-netlify)
5. [Деплой на Vercel](#деплой-на-vercel)
6. [Линтинг при Pull Request](#линтинг-при-pull-request)
7. [Автоматизация релизов](#автоматизация-релизов)
8. [Автоматический merge](#автоматический-merge)
9. [Проверка зависимостей](#проверка-зависимостей)
10. [Кастомные workflows](#кастомные-workflows)

---

## Основы GitHub Actions

### Структура workflow файла

**Расположение:** `.github/workflows/название.yml`

**Основные компоненты:**
```yaml
name: Название workflow
on: [push, pull_request]  # Триггеры
jobs:
  job-name:
    runs-on: ubuntu-latest  # ОС для выполнения
    steps:
      - name: Шаг 1
        uses: actions/checkout@v4  # Использование action
      - name: Шаг 2
        run: npm install  # Выполнение команды
```

### Триггеры (on:)

```yaml
# При push
on: push

# При push в конкретную ветку
on:
  push:
    branches:
      - main
      - develop

# При Pull Request
on: pull_request

# При создании тега
on:
  push:
    tags:
      - v*

# По расписанию (cron)
on:
  schedule:
    - cron: '0 0 * * *'  # Каждый день в полночь

# Вручную
on: workflow_dispatch

# Комбинация триггеров
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
```

### Переменные окружения

```yaml
env:
  NODE_VERSION: '18'
  DATABASE_URL: ${{ secrets.DATABASE_URL }}

jobs:
  build:
    env:
      API_KEY: ${{ secrets.API_KEY }}
    steps:
      - name: Use variables
        run: echo $NODE_VERSION
```

### Secrets

**Добавление secrets:**
1. Репозиторий → Settings → Secrets and variables → Actions
2. New repository secret
3. Имя: `API_KEY`, Значение: `your-secret-value`

**Использование:**
```yaml
env:
  API_KEY: ${{ secrets.API_KEY }}
```

---

## Автотесты Node.js

### Базовый workflow для Node.js

**Файл:** `.github/workflows/nodejs-test.yml`

```yaml
name: Node.js CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [16, 18, 20]

    steps:
      - name: Checkout код
        uses: actions/checkout@v4

      - name: Установка Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Установка зависимостей
        run: npm ci

      - name: Запуск линтера
        run: npm run lint

      - name: Запуск тестов
        run: npm test

      - name: Проверка сборки
        run: npm run build
```

### С покрытием кода (Coverage)

```yaml
name: Node.js CI with Coverage

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests with coverage
        run: npm run test:coverage

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
          flags: unittests
          name: codecov-umbrella
```

### React приложение (с Vite)

```yaml
name: React CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run ESLint
        run: npm run lint

      - name: Run tests
        run: npm test -- --run

      - name: Build project
        run: npm run build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: dist
          path: dist/
```

---

## Автотесты Python

### Базовый workflow для Python

**Файл:** `.github/workflows/python-test.yml`

```yaml
name: Python CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest flake8 black

      - name: Lint with flake8
        run: flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

      - name: Check formatting with black
        run: black --check .

      - name: Run tests
        run: pytest
```

### Django приложение

```yaml
name: Django CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest-django

      - name: Run migrations
        env:
          DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
        run: python manage.py migrate

      - name: Run tests
        env:
          DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
        run: pytest
```

### FastAPI приложение

```yaml
name: FastAPI CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install poetry
          poetry install

      - name: Run linter
        run: poetry run ruff check .

      - name: Run type checker
        run: poetry run mypy .

      - name: Run tests
        run: poetry run pytest --cov=app tests/
```

---

## Деплой на Netlify

### Автоматический деплой на Netlify

**Файл:** `.github/workflows/deploy-netlify.yml`

```yaml
name: Deploy to Netlify

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build project
        run: npm run build
        env:
          VITE_API_URL: ${{ secrets.VITE_API_URL }}

      - name: Deploy to Netlify
        uses: nwtgck/actions-netlify@v2
        with:
          publish-dir: './dist'
          production-branch: main
          github-token: ${{ secrets.GITHUB_TOKEN }}
          deploy-message: "Deploy from GitHub Actions"
          enable-pull-request-comment: true
          enable-commit-comment: true
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

**Настройка secrets:**
1. Получите `NETLIFY_AUTH_TOKEN`: Netlify → User Settings → Applications → Personal access tokens
2. Получите `NETLIFY_SITE_ID`: Netlify → Site Settings → Site information → API ID
3. Добавьте оба значения в GitHub Secrets

### Preview деплой для Pull Requests

```yaml
name: Preview Deploy

on:
  pull_request:
    branches: [ main ]

jobs:
  preview:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install and build
        run: |
          npm ci
          npm run build

      - name: Deploy preview to Netlify
        uses: nwtgck/actions-netlify@v2
        with:
          publish-dir: './dist'
          production-deploy: false
          github-token: ${{ secrets.GITHUB_TOKEN }}
          deploy-message: "Preview deploy for PR #${{ github.event.number }}"
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

---

## Деплой на Vercel

### Автоматический деплой на Vercel

**Файл:** `.github/workflows/deploy-vercel.yml`

```yaml
name: Deploy to Vercel

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install Vercel CLI
        run: npm install --global vercel@latest

      - name: Pull Vercel Environment
        run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}

      - name: Build Project
        run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}

      - name: Deploy to Vercel
        run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
```

**Настройка secrets:**
1. Получите `VERCEL_TOKEN`: Vercel → Account Settings → Tokens
2. Добавьте токен в GitHub Secrets

### Next.js на Vercel

```yaml
name: Deploy Next.js to Vercel

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Build Next.js
        run: npm run build
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.NEXT_PUBLIC_API_URL }}

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

---

## Линтинг при Pull Request

### ESLint для JavaScript/TypeScript

**Файл:** `.github/workflows/lint-pr.yml`

```yaml
name: Lint Pull Request

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  lint:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run ESLint
        run: npm run lint

      - name: Check formatting (Prettier)
        run: npm run format:check

      - name: Run TypeScript check
        run: npx tsc --noEmit
```

### С комментариями в PR

```yaml
name: Lint with PR Comments

on:
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run ESLint
        run: npm run lint -- --format=json --output-file=eslint-report.json
        continue-on-error: true

      - name: Annotate code with ESLint results
        uses: ataylorme/eslint-annotate-action@v2
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          report-json: eslint-report.json
```

### Python линтинг (Ruff + Black)

```yaml
name: Python Lint

on:
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install linters
        run: |
          pip install ruff black mypy

      - name: Run Ruff
        run: ruff check .

      - name: Check formatting with Black
        run: black --check .

      - name: Run type checker
        run: mypy .
```

---

## Автоматизация релизов

### Создание релиза при теге

**Файл:** `.github/workflows/release.yml`

```yaml
name: Create Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Build project
        run: npm run build

      - name: Create ZIP archive
        run: zip -r dist.zip dist/

      - name: Extract version from tag
        id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist.zip
          body: |
            Release ${{ steps.version.outputs.VERSION }}

            Изменения:
            - Обновлена функциональность
            - Исправлены баги
          draft: false
          prerelease: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Автогенерация changelog

```yaml
name: Release with Changelog

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Generate changelog
        id: changelog
        uses: metcalfc/changelog-generator@v4.1.0
        with:
          myToken: ${{ secrets.GITHUB_TOKEN }}

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          body: ${{ steps.changelog.outputs.changelog }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Semantic Release (автоматическая версионность)

```yaml
name: Semantic Release

on:
  push:
    branches: [ main ]

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Build
        run: npm run build

      - name: Semantic Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
        run: npx semantic-release
```

**Настройка:** Создайте файл `.releaserc.json`:
```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    "@semantic-release/npm",
    "@semantic-release/github",
    "@semantic-release/git"
  ]
}
```

---

## Автоматический merge

### Auto-merge для Dependabot PR

**Файл:** `.github/workflows/auto-merge-dependabot.yml`

```yaml
name: Auto-merge Dependabot PRs

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  auto-merge:
    runs-on: ubuntu-latest
    if: github.actor == 'dependabot[bot]'

    steps:
      - name: Dependabot metadata
        id: metadata
        uses: dependabot/fetch-metadata@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}

      - name: Enable auto-merge for minor updates
        if: steps.metadata.outputs.update-type == 'version-update:semver-minor' || steps.metadata.outputs.update-type == 'version-update:semver-patch'
        run: gh pr merge --auto --squash "$PR_URL"
        env:
          PR_URL: ${{ github.event.pull_request.html_url }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Проверка зависимостей

### Аудит безопасности npm

**Файл:** `.github/workflows/security-audit.yml`

```yaml
name: Security Audit

on:
  schedule:
    - cron: '0 0 * * 1'  # Каждый понедельник
  workflow_dispatch:

jobs:
  audit:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Run npm audit
        run: npm audit --audit-level=moderate

      - name: Check for outdated packages
        run: npm outdated || true
```

### Dependabot configuration

**Файл:** `.github/dependabot.yml`

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "suheil"
    assignees:
      - "suheil"
    labels:
      - "dependencies"
    commit-message:
      prefix: "chore"
      include: "scope"
```

---

## Кастомные workflows

### Автоматическое закрытие stale issues

**Файл:** `.github/workflows/stale.yml`

```yaml
name: Close Stale Issues

on:
  schedule:
    - cron: '0 0 * * *'  # Каждый день

jobs:
  stale:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/stale@v8
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          stale-issue-message: 'Этот issue неактивен 30 дней и будет закрыт через 7 дней.'
          close-issue-message: 'Issue закрыт из-за отсутствия активности.'
          days-before-stale: 30
          days-before-close: 7
          stale-issue-label: 'stale'
          exempt-issue-labels: 'pinned,security'
```

### Приветствие новых contributors

**Файл:** `.github/workflows/greetings.yml`

```yaml
name: Greetings

on: [pull_request_target, issues]

jobs:
  greeting:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/first-interaction@v1
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          issue-message: 'Спасибо за ваш первый issue! Мы скоро ответим.'
          pr-message: 'Спасибо за ваш первый PR! Мы проверим его в ближайшее время.'
```

### Автоматическое присвоение labels

**Файл:** `.github/workflows/labeler.yml`

```yaml
name: Auto Labeler

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  label:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/labeler@v4
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
```

**Конфигурация:** `.github/labeler.yml`
```yaml
'frontend':
  - 'src/**/*.js'
  - 'src/**/*.jsx'
  - 'src/**/*.tsx'

'backend':
  - 'api/**/*'
  - 'server/**/*'

'documentation':
  - 'docs/**/*'
  - '**/*.md'

'tests':
  - 'tests/**/*'
  - '**/*.test.js'
  - '**/*.spec.js'
```

---

## Полезные tips

### Кэширование для ускорения

```yaml
- name: Cache node modules
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

### Матричные builds

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    node: [16, 18, 20]
runs-on: ${{ matrix.os }}
```

### Условное выполнение

```yaml
- name: Deploy to production
  if: github.ref == 'refs/heads/main'
  run: npm run deploy
```

### Переиспользование workflows

**Reusable workflow:** `.github/workflows/reusable-tests.yml`
```yaml
name: Reusable Tests

on:
  workflow_call:
    inputs:
      node-version:
        required: true
        type: string

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
      - run: npm ci
      - run: npm test
```

**Использование:**
```yaml
name: Main CI

on: [push, pull_request]

jobs:
  test-node-18:
    uses: ./.github/workflows/reusable-tests.yml
    with:
      node-version: '18'
```

---

## Заключение

GitHub Actions — мощный инструмент автоматизации. Эти примеры покрывают большинство типичных сценариев.

✅ **Рекомендации:**
- Начните с простых workflows (тесты, линтинг)
- Постепенно добавляйте деплой и автоматизацию
- Используйте secrets для конфиденциальных данных
- Кэшируйте зависимости для ускорения
- Проверяйте workflows локально с [act](https://github.com/nektos/act)

⚠️ **Важно:** GitHub Actions бесплатны для публичных репозиториев и имеют лимиты для приватных (2000 минут/месяц на бесплатном плане).
