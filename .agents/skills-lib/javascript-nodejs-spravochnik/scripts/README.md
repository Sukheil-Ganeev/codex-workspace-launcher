# Scripts Directory

Автоматизационные скрипты для разработки и деплоя Node.js приложений.

## Доступные скрипты

### Development скрипты

#### 1. **lint.js** - ESLint Runner
Проверяет качество кода согласно ESLint правилам.

```bash
npm run lint              # Проверить код
npm run lint -- --fix    # Автоисправить ошибки
npm run lint -- --cache  # С кешированием для скорости
```

**Что делает:**
- Проверяет синтаксис и стиль кода
- Создает .eslintrc.json если не существует
- Поддерживает автоисправление проблем

---

#### 2. **format.js** - Prettier Code Formatter
Форматирует код согласно Prettier стилю.

```bash
npm run format               # Отформатировать весь код
npm run format -- --check   # Проверить без изменений
npm run format -- --tab-width 4  # Другие параметры
```

**Что делает:**
- Единообразное форматирование кода
- Создает .prettierrc если не существует
- Поддерживает проверку без изменений

---

#### 3. **test.js** - Jest Test Runner
Запускает unit и integration тесты.

```bash
npm test                    # Запустить все тесты
npm run test -- --watch    # Watch mode
npm run test -- --coverage # С покрытием кода
npm run test -- --bail     # Остановить на первой ошибке
```

**Что делает:**
- Запускает Jest тестовый фреймворк
- Создает jest.config.js если нет
- Показывает покрытие кода
- Требует >= 70% покрытия для production

---

#### 4. **type-check.js** - Type Checker
Проверяет типы через TypeScript или JSDoc.

```bash
npm run type-check              # Базовая проверка
npm run type-check -- --watch  # Watch mode
npm run type-check -- --emit   # С компиляцией
npm run type-check -- --strict # Строгий режим
```

**Что делает:**
- Проверяет типы через TypeScript
- Поддерживает JSDoc аннотации
- Создает tsconfig.json если не существует
- Может компилировать в dist/

---

#### 5. **dev-server.js** - Development Server
Локальный сервер с hot reload при изменении файлов.

```bash
npm run dev              # На порту 3000
npm run dev -- --port 4000   # На другом порту
npm run dev -- --host 0.0.0.0  # На всех интерфейсах
```

**Что делает:**
- Стартует Express или Node.js сервер
- Автоматически перезагружает при изменениях
- Загружает переменные из .env
- Graceful shutdown на Ctrl+C

---

### Build & Deployment скрипты

#### 6. **build.js** - Production Build
Компилирует и оптимизирует код для production.

```bash
npm run build                  # Обычная сборка
npm run build -- --minify     # С минификацией
npm run build -- --analyze    # Анализ размера
npm run build -- --clean      # Очистить перед сборкой
```

**Что делает:**
1. Type checking
2. Linting
3. Testing
4. Копирование файлов
5. Опциональная минификация
6. Создание dist/
7. Статистика размера

---

#### 7. **migrate.js** - Database Migrations
Управляет миграциями БД (create, run, undo).

```bash
npm run migrate              # Запустить pending миграции
npm run migrate -- undo     # Откатить последнюю
npm run migrate -- create users  # Создать новую
npm run migrate -- status   # Показать статус
```

**Что делает:**
- Создание новых миграций
- Применение pending миграций
- Откат на N шагов назад
- Отслеживание истории в .migration-history.json

**Структура миграции:**
```javascript
module.exports = {
  up: async (db) => {
    // CREATE TABLE, ALTER TABLE, INSERT
  },
  down: async (db) => {
    // DROP TABLE
  }
};
```

---

#### 8. **seed.js** - Database Seeding
Заполняет БД тестовыми/начальными данными.

```bash
npm run seed               # Запустить все seeders
npm run seed -- tours     # Конкретный seeder
npm run seed -- create users  # Создать новый
npm run seed -- --list    # Показать доступные
```

**Что делает:**
- Создание новых seeders
- Выполнение всех или конкретного seeder'а
- Загрузка тестовых данных в БД
- Отслеживание выполненных seeders

---

#### 9. **docs-generator.js** - API Documentation
Генерирует документацию API из кода (Swagger/OpenAPI).

```bash
npm run docs               # Сгенерировать документацию
npm run docs -- --watch   # Watch mode
npm run docs -- --format openapi  # OpenAPI v3
```

**Создает:**
- `docs/api-docs.json` - OpenAPI specification
- `docs/index.html` - Swagger UI интерфейс
- `docs/README.md` - Markdown документация

---

### Performance & Security скрипты

#### 10. **profiler.js** - Performance Profiler
Профилирует производительность приложения.

```bash
npm run profile              # 10 сек профилирования
npm run profile -- --duration 30  # 30 секунд
npm run profile -- --memory  # Только память
npm run profile -- --cpu     # Только CPU
```

**Что делает:**
- Мониторинг использования памяти (RSS, Heap)
- Измерение CPU usage
- Анализ утечек памяти
- Сохранение отчета в profile.json

---

#### 11. **security-audit.js** - Security Audit
Проверяет уязвимости и проблемы безопасности.

```bash
npm run security         # Полный аудит
npm run security -- --fix     # Попытаться исправить
npm run security -- --secrets # Только secrets scanning
npm run security -- --env     # Только .env проверка
```

**Проверяет:**
1. npm audit уязвимостей в зависимостях
2. Утечки secrets (.env, API keys)
3. OWASP Top 10 уязвимости
4. Лицензии зависимостей
5. Версию Node.js
6. .gitignore конфигурацию

---

#### 12. **deploy-helper.js** - Deployment Helper
Автоматизирует развертывание на production.

```bash
npm run deploy              # На Netlify
npm run deploy -- --vercel  # На Vercel
npm run deploy -- --railway # На Railway
npm run deploy -- --check   # Только проверка
npm run deploy -- --dry-run # Сухой запуск
npm run deploy -- --rollback  # Откатить предыдущий
```

**Pre-deployment checks:**
- git status
- .env файлы
- Security audit
- Тесты
- Build

**Deployment на:**
- Netlify Functions
- Vercel
- Railway
- Custom servers

---

## Интеграция в package.json

Добавьте в `package.json`:

```json
{
  "scripts": {
    "lint": "node scripts/lint.js",
    "format": "node scripts/format.js",
    "test": "node scripts/test.js",
    "type-check": "node scripts/type-check.js",
    "dev": "node scripts/dev-server.js",
    "build": "node scripts/build.js",
    "migrate": "node scripts/migrate.js",
    "seed": "node scripts/seed.js",
    "docs": "node scripts/docs-generator.js",
    "profile": "node scripts/profiler.js",
    "security": "node scripts/security-audit.js",
    "deploy": "node scripts/deploy-helper.js",
    "pretest": "npm run lint",
    "prebuild": "npm run type-check && npm run test",
    "predeploy": "npm run build"
  }
}
```

---

## Рекомендуемые workflows

### Development workflow
```bash
npm run dev              # Стартую с dev сервером
# Вносю изменения
npm run format           # Форматирую код
npm run lint -- --fix   # Исправляю ошибки
npm test                # Тестирую
```

### Pre-commit workflow
```bash
npm run lint -- --fix   # Исправить ошибки
npm run format          # Форматировать
npm run type-check      # Проверить типы
npm test                # Запустить тесты
```

### Release workflow
```bash
npm run security        # Проверить безопасность
npm run build          # Production build
npm run deploy         # Деплой на production
```

### Database workflow
```bash
npm run migrate        # Применить миграции
npm run seed          # Заполнить данные
```

---

## Environment Variables

Скрипты загружают переменные из:
- `.env`
- `.env.local`
- `.env.production` (для deploy)

Обязательные переменные:
```bash
NODE_ENV=development
PORT=3000
```

---

## Troubleshooting

### "Command not found: npm"
Установите Node.js с https://nodejs.org/

### "ESLint/Prettier not found"
```bash
npm install --save-dev eslint prettier
```

### "Jest/TypeScript not found"
```bash
npm install --save-dev jest typescript
```

### Скрипты работают медленно
```bash
npm run <script> -- --cache  # Используйте cache
```

### Deployment fails
```bash
npm run deploy -- --dry-run      # Сухой запуск
npm run deploy -- --skip-tests   # Пропустить тесты
npm run security                 # Проверить безопасность
```

---

## Примечания

- Все скрипты поддерживают `--help` флаг
- Скрипты создают конфигурации если их нет
- Используют `chalk` для цветных сообщений
- Production-ready с обработкой ошибок
- Exit codes: 0 (успех), 1 (ошибка)

---

**Версия:** 1.0
**Обновлено:** 2026-02-04
