# Deployment Comparison: Drop vs GitHub vs CLI

Детальное сравнение методов деплоя на Netlify.

---

## Краткое сравнение

| Характеристика | Drop Deploy | GitHub Integration | Netlify CLI |
|----------------|-------------|-------------------|-------------|
| **Скорость первого деплоя** | ⚡ 10 секунд | 🐢 5 минут | 🟡 2 минуты |
| **Автообновления** | ❌ | ✅ | ⚠️ Вручную |
| **Password protection** | ❌ | ✅ | ✅ |
| **Deploy previews** | ❌ | ✅ | ✅ (draft) |
| **Rollback** | ❌ | ✅ | ✅ |
| **Environment variables** | ❌ | ✅ | ✅ |
| **Build automation** | ❌ | ✅ | ⚠️ Скриптом |
| **Team collaboration** | ❌ | ✅ | ✅ |
| **Serverless Functions** | ❌ | ✅ | ✅ |
| **Custom domains** | ✅ | ✅ | ✅ |
| **Analytics** | ✅ | ✅ | ✅ |
| **Requires Git** | ❌ | ✅ | ❌ |
| **Requires Account** | ⚠️ Для постоянства | ✅ | ✅ |

---

## Drop Deploy

### Описание

Drag & drop папки с билдом в веб-интерфейс Netlify.

### Процесс

```
1. Собрать проект локально (npm run build)
2. Открыть https://app.netlify.com
3. Перетащить папку build/ на сайт
4. Получить ссылку через 10-30 секунд
```

### Плюсы

✅ **Моментальный деплой**
- Не нужно настраивать Git
- Не нужно настраивать Build Settings
- Результат за считанные секунды

✅ **Простота**
- Нулевая кривая обучения
- Визуально понятно
- Отлично для демо

✅ **Не требует Git**
- Работает с любыми файлами
- Можно деплоить из ZIP архива
- Подходит для legacy проектов

✅ **Быстрое прототипирование**
- Показать клиенту за 1 минуту
- Тестирование идей
- Быстрая итерация

---

### Минусы

❌ **Нет автоматизации**
- Каждое обновление - вручную
- Нужно помнить пересобрать проект
- Легко забыть задеплоить

❌ **Нет истории изменений**
- Нельзя откатиться к предыдущей версии
- Нет Deploy Previews
- Нет логов билда (билд локальный)

❌ **Нет Password Protection**
- Только публичные сайты
- Или временная защита паролем (на 24ч без аккаунта)
- Нельзя ограничить доступ

❌ **Нет Environment Variables**
- Переменные должны быть в `.env` локально
- Риск закоммитить секреты
- Нельзя менять без пересборки

❌ **Нет Functions**
- Только статические файлы
- Нет serverless backend
- Нужны внешние API

❌ **Командная работа сложнее**
- Кто последний задеплоил?
- Какие изменения были?
- Кто отвечает за обновления?

---

### Когда использовать

✅ **Идеально для:**
- Быстрого прототипа
- Демо для клиента
- Тестирования идеи
- Одноразовых landing pages
- Проектов без Git

❌ **НЕ подходит для:**
- Production сайтов
- Проектов с частыми обновлениями
- Командной разработки
- Проектов с секретами
- Сайтов с Functions

---

## GitHub Integration

### Описание

Автоматический деплой из Git репозитория при каждом push.

### Процесс

```
1. Push код в GitHub
2. Netlify → New site from Git
3. Выбрать репозиторий
4. Настроить Build Settings
5. Netlify автоматически собирает и деплоит
```

### Плюсы

✅ **Полная автоматизация**
- Push → автоматический билд → деплой
- Не нужно помнить деплоить
- CI/CD из коробки

✅ **Deploy Previews**
- Каждый Pull Request → отдельный preview URL
- Проверка изменений до мержа
- Команда видит изменения до продакшена

✅ **История и Rollback**
- Каждый коммит = отдельный деплой
- Можно откатиться к любой версии одним кликом
- Полные логи билдов

✅ **Environment Variables**
- Безопасное хранение секретов
- Разные переменные для разных веток
- Обновление без пересборки (только redeploy)

✅ **Serverless Functions**
- Backend логика прямо в проекте
- Скрытие API ключей
- Полноценный API

✅ **Password Protection**
- Закрыть сайт паролем
- JWT token authentication
- Netlify Identity для user management

✅ **Командная работа**
- Git flow = deploy flow
- Code review через PR
- Deploy notifications в Slack/Discord

✅ **Branch Deploys**
- `production` → production URL
- `staging` → staging URL
- `feature-x` → preview URL
- Разные ENV для разных веток

---

### Минусы

❌ **Требует Git**
- Нужно знать Git
- Нужен GitHub/GitLab/Bitbucket аккаунт
- Может быть overkill для простых проектов

❌ **Настройка требует времени**
- Первичная настройка 5-10 минут
- Нужно правильно настроить Build Settings
- Возможны ошибки конфигурации

❌ **Билд на серверах Netlify**
- Зависит от скорости серверов
- Ограничения Free tier (300 минут/месяц)
- Нельзя билдить локально и проверить

❌ **Обучение команды**
- Все должны понимать Git workflow
- Нужны правила работы с ветками
- Может быть сложно для junior devs

---

### Когда использовать

✅ **Идеально для:**
- Production сайтов
- Проектов с частыми обновлениями
- Командной разработки
- Проектов с секретами
- CI/CD пайплайнов
- Проектов с Functions
- Любых серьёзных проектов

❌ **Избыточно для:**
- Одноразовых landing pages
- Быстрых прототипов
- Проектов без Git
- Когда нужен результат "прямо сейчас"

---

## Netlify CLI

### Описание

Деплой из командной строки через `netlify-cli` пакет.

### Процесс

```bash
# Установка
npm install -g netlify-cli

# Авторизация
netlify login

# Деплой
netlify deploy --prod --dir=build
```

### Плюсы

✅ **Гибкость**
- Деплой из любой директории
- Деплой без Git
- Автоматизация через скрипты

✅ **Локальная разработка**
- `netlify dev` - полная эмуляция Netlify
- Тестирование Functions локально
- Тестирование redirects локально

✅ **Draft Deploys**
- Предпросмотр перед production
- Уникальный URL для проверки
- Безопасное тестирование

✅ **CI/CD интеграция**
- GitHub Actions
- GitLab CI
- Jenkins, CircleCI, etc

✅ **Automation**
- Bash скрипты
- npm scripts
- Cron jobs

✅ **Environment Variables management**
```bash
netlify env:set API_KEY "value"
netlify env:list
```

✅ **Functions management**
```bash
netlify functions:create
netlify functions:log
netlify dev  # Functions работают локально
```

---

### Минусы

❌ **Требует установку**
- Node.js + npm
- netlify-cli пакет
- Нужна авторизация

❌ **Нет автоматических деплоев**
- Нужно вручную запускать команду
- Или настраивать CI/CD
- Легко забыть задеплоить

❌ **Требует технических знаний**
- Командная строка
- Environment variables
- Bash/PowerShell скрипты

❌ **Deploy Previews вручную**
- Не автоматические при PR
- Нужно делать draft deploy
- Делиться ссылкой вручную

---

### Когда использовать

✅ **Идеально для:**
- Локальной разработки с Functions
- CI/CD пайплайнов
- Автоматизации деплоев
- Тестирования перед продакшеном
- Деплоя из нестандартных источников
- Скриптовой автоматизации

❌ **Избыточно для:**
- Проектов уже подключённых к Git
- Разработчиков без опыта CLI
- Простых статических сайтов
- Когда нужна простота

---

## Комбинированный подход

Многие команды используют **несколько методов одновременно**:

### Вариант 1: GitHub + CLI

```
Production: GitHub Integration (автоматический деплой)
Development: netlify dev (локальная разработка)
Testing: netlify deploy (draft deploy для QA)
```

**Workflow:**
1. Разработка: `netlify dev`
2. Тестирование: `netlify deploy` → draft URL для проверки
3. Production: `git push` → автоматический деплой

---

### Вариант 2: Drop → GitHub миграция

```
1. Начало: Drop Deploy (прототип за 1 минуту)
2. Показали клиенту, всё ОК
3. Создали Git репозиторий
4. Подключили GitHub Integration
5. Удалили старый Drop Deploy сайт
```

**Когда использовать:**
- Быстрая проверка идеи
- Затем переход на production workflow

---

### Вариант 3: CLI для микросервисов

```
Main Site: GitHub Integration
Functions: netlify functions:create + GitHub
Testing: netlify dev локально
```

**Workflow:**
1. Сайт деплоится автоматически из GitHub
2. Functions разрабатываются локально с `netlify dev`
3. Functions тестируются изолированно
4. Push в GitHub → автоматический деплой всего

---

## Decision Tree

```
Нужен деплой прямо сейчас (< 1 мин)?
├─ ДА → Drop Deploy
└─ НЕТ
    │
    Проект будет обновляться?
    ├─ ДА → Используете Git?
    │   ├─ ДА → GitHub Integration
    │   └─ НЕТ → Netlify CLI + скрипты
    └─ НЕТ → Drop Deploy

Есть Functions или секреты?
├─ ДА → GitHub Integration или CLI (НЕ Drop!)
└─ НЕТ → Любой метод подходит

Командная разработка?
├─ ДА → GitHub Integration
└─ НЕТ → Любой метод подходит

Нужна локальная разработка с Functions?
├─ ДА → Netlify CLI (netlify dev)
└─ НЕТ → GitHub Integration достаточно
```

---

## Миграция между методами

### Drop → GitHub

```bash
# 1. Инициализация Git
git init
git add .
git commit -m "Initial commit"

# 2. Создание GitHub репозитория
# Создать на github.com

# 3. Push в GitHub
git remote add origin https://github.com/username/repo.git
git push -u origin main

# 4. Netlify → New site from Git
# Выбрать репозиторий

# 5. Удалить старый Drop Deploy сайт
```

---

### Drop → CLI

```bash
# 1. Установка CLI
npm install -g netlify-cli

# 2. Авторизация
netlify login

# 3. Связать с существующим сайтом
netlify link

# 4. Деплой
netlify deploy --prod
```

---

### GitHub → CLI управление

```bash
# GitHub остаётся для автодеплоя
# CLI используется для:

# Локальная разработка
netlify dev

# Draft deploys для тестирования
netlify deploy

# Environment variables
netlify env:set KEY "value"

# Functions management
netlify functions:create
```

---

## Стоимость и лимиты

| Лимит | Free Tier | Pro ($19/мес) | Business ($99/мес) |
|-------|-----------|---------------|-------------------|
| **Build минуты** | 300/месяц | 1000/месяц | 1500/месяц |
| **Bandwidth** | 100 GB | 400 GB | 1 TB |
| **Concurrent builds** | 1 | 3 | 5 |
| **Function invocations** | 125k/месяц | 2 млн/месяц | 3 млн/месяц |
| **Function runtime** | 10 сек | 26 сек | 26 сек |
| **Deploy notifications** | ❌ | ✅ | ✅ |
| **Password protection** | ✅ | ✅ | ✅ |
| **Team members** | 1 | Unlimited | Unlimited |
| **Support** | Community | Email | Priority |

**Все методы деплоя** доступны на всех планах!

---

## Рекомендации

### Для новичков
👉 Начните с **Drop Deploy** для обучения, затем переходите на **GitHub Integration**.

### Для фрилансеров
👉 **GitHub Integration** для клиентских проектов + **CLI** для локальной разработки.

### Для команд
👉 **GitHub Integration** с PR workflow + **netlify dev** для локальной разработки.

### Для CI/CD
👉 **Netlify CLI** в GitHub Actions/GitLab CI, но можно оставить Netlify автоматический деплой.

### Для экспериментов
👉 **Drop Deploy** для быстрого тестирования идей.

---

Подробности о каждом методе: [SKILL.md](../SKILL.md)
