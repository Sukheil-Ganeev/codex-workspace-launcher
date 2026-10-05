# Бизнес-кейсы деплоя на Netlify

> Перенесено из SKILL.md — подробные сценарии использования для туристического бизнеса.

---

## Детальное сравнение: Drop vs GitHub vs CLI

| Критерий | Netlify Drop | GitHub Integration | Netlify CLI |
|----------|--------------|-------------------|-------------|
| **Скорость старта** | 30 секунд | 5 минут | 10 минут |
| **Автоматический деплой** | Только ручной | При push в main | Ручной, но из терминала |
| **Версионность** | Нет истории | Git история | Git история |
| **Preview deployments** | Нет | Для PR автоматически | Ручной draft deploy |
| **Rollback** | Нет | Один клик | `netlify rollback` |
| **Environment variables** | Только через UI | Через UI или netlify.toml | Через CLI или UI |
| **Password protection** | Да | Да | Да |
| **Custom domain** | Да | Да | Да |
| **Build процесс** | Нет (только статика) | Да (npm, yarn, etc) | Да |
| **Serverless Functions** | Нет | Да | Да |
| **Локальная разработка** | Нет | Нет (нужен CLI) | `netlify dev` |
| **Бесплатный лимит** | Неограниченно | 300 build минут | 300 build минут |

---

## Кейс 1: Срочный прайс-лист для клиента

- **Ситуация:** Клиент просит прайс на экскурсии прямо сейчас (звонок/WhatsApp)
- **Решение:** Netlify Drop
- **Шаги:**
  1. Открыли локальный HTML прайс
  2. Обновили цены (если нужно)
  3. Drag & drop на https://app.netlify.com/drop
  4. Скопировали URL
  5. Отправили клиенту в WhatsApp

**Время:** 1 минута

## Кейс 2: Корпоративный прайс-лист с автообновлением

- **Ситуация:** Нужен постоянный URL для прайс-листа, который обновляется из Google Sheets
- **Решение:** GitHub Integration + Scheduled Functions
- **Шаги:**
  1. Создали репозиторий `price-list`
  2. Подключили к Netlify
  3. Настроили Serverless Function для фетчинга Google Sheets
  4. Scheduled Function запускается каждые 6 часов
  5. Автоматический деплой при изменениях в коде

**Результат:** https://dxb-tours-price.netlify.app (всегда актуальные цены)

## Кейс 3: Internal dashboard с паролем

- **Ситуация:** Dashboard для команды с бронированиями и комиссиями
- **Решение:** Netlify Drop + Password Protection
- **Шаги:**
  1. Собрали статический HTML dashboard (данные из API)
  2. Drop деплой
  3. Site Settings → Visitor Access → Password: `team2024`
  4. Поделились URL только с командой

**Безопасность:** Никто посторонний не зайдёт

## Кейс 4: Telegram бот с webhooks

- **Ситуация:** Бот для приёма заявок на экскурсии
- **Решение:** GitHub + Netlify Functions
- **Шаги:**
  1. Создали репозиторий `telegram-booking-bot`
  2. Netlify Functions: `/netlify/functions/telegram-webhook.js`
  3. Environment Variables: `TELEGRAM_BOT_TOKEN`, `GOOGLE_SHEETS_API_KEY`
  4. Webhook URL: `https://booking-bot.netlify.app/.netlify/functions/telegram-webhook`
  5. Автоматический деплой при изменениях

**Результат:** Бот работает 24/7, логи в Netlify dashboard

## Кейс 5: A/B тестирование лендинга

- **Ситуация:** Тестируем две версии лендинга (разные заголовки)
- **Решение:** Netlify CLI + Branch deployments
- **Шаги:**
  1. Main branch: текущий лендинг
  2. Feature branch: `feature/new-headline`
  3. `netlify deploy` для draft URL
  4. Показали клиенту оба варианта
  5. Выбрали лучший → merge → автоматический production deploy

## Кейс 6: Быстрый rollback при ошибке

- **Ситуация:** После деплоя обнаружили баг в production
- **Решение:** GitHub Integration (Netlify хранит все деплои)
- **Шаги:**
  1. Netlify Dashboard → Deploys
  2. Нашли последний рабочий деплой
  3. Кликнули "Publish deploy"
  4. Сайт вернулся к предыдущей версии за 5 секунд

**Время восстановления:** < 1 минута

---

## Когда какой метод использовать

### Netlify Drop — для:

**Быстрые демо и тесты:**
- Показать клиенту новый прайс-лист прямо сейчас
- Проверить, как выглядит сайт на мобильных (нужен реальный URL)
- Разовые лендинги (акция закончится через неделю)

**Internal tools с простой структурой:**
- Dashboard с расписанием экскурсий (только для команды)
- Калькулятор цен для менеджеров
- Инструкции для гидов

**С password protection:**
- Internal dashboards (имена, контакты клиентов)
- Финансовый отчёт
- Admin панель

**НЕ использовать для:**
- Production сайтов, которые будут обновляться
- Проектов с build процессом (React, Vue)
- Сайтов с serverless functions

### GitHub Integration — для:

**Production сайтов:**
- Прайс-листы с автообновлением из Google Sheets
- Корпоративные лендинги
- Телеграм боты с webhooks
- Multi-page сайты с навигацией

**Командной работы:**
- Несколько разработчиков работают над одним проектом
- Code review через Pull Requests
- Preview deployments для каждого PR

**Проектов с build процессом:**
- React, Vue, Svelte, Next.js
- TypeScript, SASS, PostCSS
- Автоматическая оптимизация assets

**Проектов с Serverless Functions:**
- Обработка Telegram webhooks
- Интеграция с Google Sheets API
- Email уведомления через SendGrid

### Netlify CLI — для:

**Локальной разработки:**
- `netlify dev` запускает локальный сервер с эмуляцией production
- Тестирование redirects и functions локально

**Preview deployments:**
- `netlify deploy` (без --prod) создаёт draft URL
- Показать клиенту изменения до production деплоя

**Автоматизации:**
- Скрипты для CI/CD (GitHub Actions, GitLab CI)
- Деплой из makefile или package.json scripts

**Debugging:**
- `netlify logs` — просмотр логов functions
- `netlify env:list` — проверка environment variables
- `netlify status` — информация о текущем деплое
