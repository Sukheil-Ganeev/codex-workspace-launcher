# FAQ: Netlify Deployment

Часто задаваемые вопросы о деплое на Netlify.

---

## Основы Netlify

### Что такое Netlify?

Netlify — это платформа для хостинга статических сайтов и JAMstack приложений с автоматическим деплоем, CDN, serverless functions и встроенным CI/CD.

**Основные возможности:**
- ✅ Автоматический деплой из Git
- ✅ Глобальный CDN
- ✅ Бесплатный HTTPS
- ✅ Serverless Functions
- ✅ Form handling
- ✅ Deploy previews для pull requests

**Что можно деплоить:**
- Статические сайты (HTML/CSS/JS)
- SPA (React, Vue, Angular)
- SSG (Next.js, Gatsby, Hugo, Astro)
- JAMstack приложения

---

### Сколько стоит Netlify?

**Free tier включает:**
- 300 build минут/месяц
- 100 GB bandwidth
- Unlimited сайтов
- Базовые функции

**Платные планы:**
- Pro: $19/месяц (больше bandwidth, build минут)
- Business: $99/месяц (команды, расширенные функции)

Для большинства проектов бесплатного плана хватает.

---

### Нужно ли создавать аккаунт для деплоя?

**Зависит от метода:**
- Drop Deploy: Можно без аккаунта (сайт живёт 24 часа)
- GitHub Integration: Требуется аккаунт
- Netlify CLI: Требуется аккаунт

**Рекомендация:** Создайте аккаунт для постоянного хостинга.

### 3. Почему мой Drop деплой требует password?

❌ **Проблема:** Drop Deploy (без аккаунта) автоматически защищён паролем
✅ **Решение:** Используй GitHub Integration или CLI — они дают публичный доступ

Подробнее: [troubleshooting.md](./troubleshooting.md#password-protection-на-drop-deploy)

### 4. Как получить постоянную ссылку на сайт?

**Три способа:**

1. **Drop Deploy:** Временная ссылка вида `random-name-123abc.netlify.app` (живёт 24 часа без аккаунта)
2. **GitHub Integration:** Постоянная ссылка вида `site-name.netlify.app` (можно изменить в настройках)
3. **Custom Domain:** Свой домен типа `mysite.com` (настраивается в Site Settings → Domain Management)

### 5. Можно ли изменить имя сайта (subdomain)?

✅ **Да:** Site Settings → General → Site details → Change site name

Пример: `ugly-name-123.netlify.app` → `my-project.netlify.app`

⚠️ **Важно:** Старая ссылка перестанет работать!

---

## Методы деплоя

### 6. Какой метод деплоя выбрать?

| Метод | Когда использовать |
|-------|-------------------|
| **Drop Deploy** | Быстрый тест, одноразовый деплой, нет Git |
| **GitHub Integration** | Production, автообновления, командная работа |
| **Netlify CLI** | Локальная разработка, автоматизация, CI/CD |

Подробнее: [deployment-comparison.md](./deployment-comparison.md)

### 7. Как деплоить из приватного GitHub репозитория?

✅ **Работает так же,** как с публичным:

1. Netlify попросит доступ к GitHub
2. Выбери приватный репозиторий
3. Настрой Build Settings

Netlify получает доступ через OAuth, не нужно делать репозиторий публичным.

### 8. Можно ли деплоить не из master/main ветки?

✅ **Да:** Site Settings → Build & Deploy → Deploy contexts

Можно настроить:
- Production branch (например, `production`)
- Deploy Previews для Pull Requests
- Branch deploys (автоматический деплой всех веток)

### 9. Как деплоить SPA (Single Page Application)?

**Критически важно:** Добавь `_redirects` файл в папку с билдом:

```
/*    /index.html   200
```

Это решит проблему 404 при прямых ссылках типа `site.com/about`.

Подробнее: [troubleshooting.md](./troubleshooting.md#404-на-прямых-ссылках-spa)

---

## Build Process

### 10. Что такое Build Command и Publish Directory?

**Build Command** — команда для сборки проекта:
- `npm run build` (для React/Vue)
- `hugo` (для Hugo)
- Пусто (если сайт уже собран)

**Publish Directory** — папка с готовым сайтом:
- `build` (Create React App)
- `dist` (Vue/Vite)
- `public` (Hugo/Gatsby)
- `.` (если HTML в корне)

### 11. Где посмотреть логи сборки?

**Три места:**

1. **Deploy Log:** Deploys → Конкретный деплой → Deploy log
2. **Function Logs:** Functions → Logs (для serverless functions)
3. **Real-time logs:** `netlify dev` в терминале (локально)

### 12. Почему Build падает с ошибкой?

**Топ-5 причин:**

1. ❌ Неправильный Build Command
2. ❌ Неправильный Publish Directory
3. ❌ Отсутствуют зависимости в package.json
4. ❌ Переменные окружения не настроены
5. ❌ Node.js версия не совпадает

Подробнее: [troubleshooting.md](./troubleshooting.md#build-failures)

---

## Environment Variables

### 13. Как добавить environment variables?

**Через UI:**
Site Settings → Build & Deploy → Environment → Environment variables → Add variable

**Через CLI:**
```bash
netlify env:set API_KEY "your-key-value"
```

⚠️ **Важно:** После добавления нужно сделать Redeploy!

### 14. Почему мои ENV переменные не работают?

**Чеклист:**

- ✅ Переменные добавлены в Netlify (не только в `.env` локально)
- ✅ Названия начинаются с `REACT_APP_` (для React) или правильного префикса для фреймворка
- ✅ Сделан Redeploy после добавления переменных
- ✅ Переменные НЕ раскрываются в браузере (для клиентских приложений)

Подробнее: [troubleshooting.md](./troubleshooting.md#environment-variables-не-видны)

### 15. Безопасно ли хранить API ключи в Environment Variables?

**Зависит от типа:**

✅ **Безопасно:** API ключи для Netlify Functions (serverless)
❌ **НЕ безопасно:** API ключи для клиентского кода (браузер видит всё)

**Решение:** Используй Netlify Functions как прокси для секретных API.

Подробнее: [security-guide.md](./security-guide.md)

---

## Домены и HTTPS

### 16. Как подключить свой домен?

1. Site Settings → Domain Management → Add custom domain
2. Введи домен (например, `mysite.com`)
3. Настрой DNS записи у регистратора:
   - **A record:** `75.2.60.5`
   - Или **CNAME:** `your-site.netlify.app`
4. Дождись DNS propagation (до 24 часов)

✅ HTTPS сертификат выдаётся автоматически бесплатно.

### 17. Нужно ли настраивать HTTPS?

❌ **НЕТ!** Netlify автоматически выдаёт бесплатный SSL сертификат (Let's Encrypt).

Работает для:
- ✅ `.netlify.app` поддоменов
- ✅ Кастомных доменов

### 18. Как настроить редирект с www на без www (или наоборот)?

Netlify делает это автоматически! Выбери Primary domain в настройках:

Site Settings → Domain Management → Primary domain → Options

---

## Serverless Functions

### 19. Что такое Netlify Functions?

Serverless функции — это backend код, который запускается по запросу:
- ✅ Не нужен свой сервер
- ✅ Платишь только за использование
- ✅ Автоматический скейлинг

**Пример использования:**
- Отправка email
- Обработка платежей
- Запросы к API с секретными ключами

Подробнее: [advanced-features.md](./advanced-features.md)

### 20. Где размещать Functions?

**По умолчанию:** В папке `netlify/functions/` в корне проекта

**Кастомная папка:** Укажи в `netlify.toml`:
```toml
[build]
  functions = "my-functions"
```

**Структура:**
```
netlify/functions/
├── hello.js          # → /.netlify/functions/hello
└── api/
    └── users.js      # → /.netlify/functions/api/users
```

---

## Оптимизация и производительность

### 21. Как ускорить деплой?

**Топ-5 способов:**

1. Включи кэширование зависимостей (Netlify делает автоматически)
2. Используй `netlify.toml` вместо UI конфигурации
3. Оптимизируй Build Command (убери ненужные шаги)
4. Используй Build Plugins для оптимизации
5. Настрой Deploy Previews только для нужных веток

Подробнее: [troubleshooting.md](./troubleshooting.md#slow-builds)

---

## Полезные ссылки

- 📖 [SKILL.md](../SKILL.md) — Основной гайд
- 🔧 [troubleshooting.md](./troubleshooting.md) — Решение проблем
- 📊 [deployment-comparison.md](./deployment-comparison.md) — Сравнение методов
- 🚀 [advanced-features.md](./advanced-features.md) — Продвинутые возможности
- 🔒 [security-guide.md](./security-guide.md) — Безопасность
