# Scripts - Скрипты автоматизации Vercel

Набор Bash и Node.js скриптов для автоматизации работы с Vercel.

## Доступные скрипты

### 1. setup-vercel.sh

**Назначение:** Автоматическая установка и первоначальная настройка Vercel CLI

**Использование:**
```bash
cd path/to/your/project
bash ~/.claude/skills/vercel-деплой/scripts/setup-vercel.sh
```

**Что делает:**
1. Проверяет установку Node.js
2. Предлагает выбор пакетного менеджера (npm/pnpm/yarn)
3. Устанавливает или проверяет Vercel CLI
4. Выполняет `vercel login` (авторизация)
5. Предлагает настроить текущий проект (`vercel link`)
6. Интерактивно создает `vercel.json` из шаблонов

**Интерактивные опции:**
- Выбор пакетного менеджера (npm, pnpm, yarn)
- Переустановка Vercel CLI (если уже установлен)
- Перелогин (если уже залогинен)
- Выбор шаблона vercel.json:
  - Статичный сайт (static)
  - Статичный сайт + API
  - Next.js
  - SPA (React/Vue)
  - Пропустить создание

---

### 2. deploy-workflow.sh

**Назначение:** Упрощённый и безопасный workflow деплоя с проверками

**Использование:**
```bash
# Preview деплой (по умолчанию)
bash ~/.claude/skills/vercel-деплой/scripts/deploy-workflow.sh preview

# Production деплой
bash ~/.claude/skills/vercel-деплой/scripts/deploy-workflow.sh production
```

**Что делает:**

**Pre-deploy проверки:**
1. Проверяет установку Vercel CLI
2. Проверяет авторизацию в Vercel
3. Валидирует `vercel.json` (если существует)
4. Проверяет наличие `.vercelignore` или `.gitignore`

**Деплой:**
5. Запрашивает подтверждение (для production)
6. Выполняет `vercel` или `vercel --prod`
7. Логирует процесс в `deploy.log`
8. Показывает время деплоя

**Post-deploy:**
9. Выводит Deployment URL
10. Показывает информацию о деплое
11. Предлагает опции:
    - Открыть в браузере
    - Посмотреть логи
    - Скопировать URL в буфер обмена
    - Завершить

---

### 3. validate-config.js

**Назначение:** Валидация и анализ `vercel.json` конфигурации

**Использование:**
```bash
# Проверить vercel.json в текущей директории
node ~/.claude/skills/vercel-деплой/scripts/validate-config.js

# Проверить конкретный файл
node ~/.claude/skills/vercel-деплой/scripts/validate-config.js path/to/vercel.json
```

**Что проверяет:**

**Синтаксис:**
- Валидный JSON
- Правильная структура

**Обязательные поля:**
- Наличие `version`
- Правильное значение `version` (рекомендуется 2)

**Структура builds:**
- `builds` - массив
- Каждый build имеет `src` и `use`
- Проверка известных билдеров (@vercel/static, @vercel/node и др.)

**Структура routes/rewrites/redirects:**
- `rewrites` - массив с `source` и `destination`
- `redirects` - массив с `source`, `destination`, `permanent`
- `routes` - deprecated предупреждение

**Структура headers:**
- `headers` - массив
- Каждый header имеет `source` и `headers`

**Безопасность:**
- Предупреждение о `env` переменных в конфиге
- Предупреждение о секретах

**Deprecated поля:**
- `regions`, `features`, `routes`, `cleanUrls`

**Оптимизация:**
- Рекомендации по размеру конфига
- Советы по Zero Config
- Проверка наличия `.vercelignore`

---

## Совместное использование

### Полный workflow новых проектов

```bash
# 1. Установка и настройка
bash ~/.claude/skills/vercel-деплой/scripts/setup-vercel.sh

# 2. Разработка...
# (ваш код здесь)

# 3. Валидация конфига
node ~/.claude/skills/vercel-деплой/scripts/validate-config.js

# 4. Preview деплой
bash ~/.claude/skills/vercel-деплой/scripts/deploy-workflow.sh preview

# 5. Тестирование preview...

# 6. Production деплой
bash ~/.claude/skills/vercel-деплой/scripts/deploy-workflow.sh production
```

### Интеграция в package.json

```json
{
  "scripts": {
    "vercel:setup": "bash ~/.claude/skills/vercel-деплой/scripts/setup-vercel.sh",
    "vercel:validate": "node ~/.claude/skills/vercel-деплой/scripts/validate-config.js",
    "vercel:preview": "bash ~/.claude/skills/vercel-деплой/scripts/deploy-workflow.sh preview",
    "vercel:deploy": "bash ~/.claude/skills/vercel-деплой/scripts/deploy-workflow.sh production"
  }
}
```

## Требования

### Все скрипты
- Git Bash (Windows) или Bash 4+ (Linux/Mac)
- Node.js 14+

### setup-vercel.sh
- Доступ к npm/pnpm/yarn
- Интернет соединение

### deploy-workflow.sh
- Vercel CLI установлен
- Авторизация в Vercel выполнена

### validate-config.js
- Node.js с поддержкой ES modules

## Troubleshooting

**Проблема:** `command not found: vercel`

**Решение:**
```bash
# Установить Vercel CLI
npm install -g vercel

# Или запустить setup-vercel.sh
bash ~/.claude/skills/vercel-деплой/scripts/setup-vercel.sh
```

---

**Проблема:** Скрипт не запускается (Windows)

**Решение:**
```bash
# Использовать Git Bash, не PowerShell или CMD
# Или явно указать bash:
bash ~/.claude/skills/vercel-деплой/scripts/setup-vercel.sh
```

---

**Проблема:** Permission denied

**Решение:**
```bash
# Сделать скрипты исполняемыми
chmod +x ~/.claude/skills/vercel-деплой/scripts/*.sh
chmod +x ~/.claude/skills/vercel-деплой/scripts/*.js
```

## Полезные ссылки

- [Vercel CLI Documentation](https://vercel.com/docs/cli)
- [vercel.json Reference](https://vercel.com/docs/project-configuration)
- [Bash Scripting Guide](https://www.gnu.org/software/bash/manual/)
- [Node.js Documentation](https://nodejs.org/docs/)
