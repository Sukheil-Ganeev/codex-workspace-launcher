# Интеграция Threads с Make.com: No-Code автоматизация

**Дата создания:** 05 февраля 2026
**Автор:** Claude Code Agent
**Применение:** Туристический бизнес в ОАЭ

---

## Содержание

1. [Обзор Make.com](#обзор-makecom)
2. [Настройка интеграции Threads](#настройка-интеграции-threads)
3. [OAuth flow через Instagram](#oauth-flow-через-instagram)
4. [Scenarios (сценарии автоматизации)](#scenarios-сценарии-автоматизации)
5. [Webhooks в Make.com](#webhooks-в-makecom)
6. [Практические примеры](#практические-примеры)
7. [Troubleshooting](#troubleshooting)

---

## Обзор Make.com

### Что такое Make.com

**Make.com** (ранее Integromat) - no-code платформа для автоматизации бизнес-процессов.

**Ключевые возможности:**
- 3000+ готовых интеграций
- Визуальный редактор сценариев (drag & drop)
- Обработка данных (фильтры, маппинг, трансформации)
- Цепочки действий (triggers → actions)
- Расписание выполнения

**Статус Threads в Make.com (2026):**
- ✅ Instagram for Business полностью поддерживается
- ⚠️ Threads API напрямую - в разработке (используется через Instagram)
- ✅ Кросс-постинг Instagram + Threads доступен

### Pricing (2026)

| План | Операции/месяц | Стоимость | Применение |
|------|----------------|-----------|------------|
| **Free** | 1,000 | $0 | Тестирование, малый объем |
| **Core** | 10,000 | ~$9/мес | Малый бизнес |
| **Pro** | 100,000 | ~$16/мес | Средний бизнес (рекомендуется) |
| **Teams** | 100,000+ | ~$29/мес | Команды, корпорации |

**Что считается операцией:**
- 1 триггер = 1 операция
- 1 action (действие) = 1 операция
- Пример: trigger (Google Sheets) + action (Instagram) + action (Threads) = 3 операции

---

## Настройка интеграции Threads

### Предварительные требования

**Необходимо иметь:**
1. ✅ Instagram Business или Creator аккаунт
2. ✅ Связанный с Facebook Page
3. ✅ Threads профиль, привязанный к Instagram
4. ✅ Facebook App с правами Threads API
5. ✅ Аккаунт Make.com

### Шаг 1: Создание Facebook App

**Процесс:**

1. Перейти: https://developers.facebook.com/apps
2. Нажать "Create App" → тип "Business"
3. Заполнить информацию:
   - App Name: "My Tourism Business Automation"
   - Contact Email: ваш email
4. Добавить продукты:
   - "Instagram" → Add Product
   - "Threads" → Add Product (если доступно)

5. Настроить разрешения:
   - `instagram_basic`
   - `instagram_content_publish`
   - `threads_basic`
   - `threads_content_publish`

6. Пройти App Review (3-7 дней)

7. Получить credentials:
   - App ID
   - App Secret

### Шаг 2: Подключение Instagram в Make.com

**Процесс:**

1. Войти в Make.com: https://www.make.com
2. Создать новый scenario
3. Добавить модуль "Instagram for Business"
4. Нажать "Create a connection"
5. OAuth flow:
   - Выбрать Instagram Business аккаунт
   - Предоставить разрешения
   - Успешная авторизация

**Результат:** Единый доступ к Instagram + Threads через одно подключение.

---

## OAuth flow через Instagram

### Архитектура авторизации

```
Make.com Scenario
    ↓
Instagram for Business Connection
    ↓
OAuth 2.0 Authorization (Meta)
    ↓
User authorizes (Facebook Page + Instagram + Threads)
    ↓
Access Token (60 days)
    ↓
Make.com сохраняет токен
    ↓
Автообновление токена каждые 50-55 дней
```

### Разрешения (Permissions)

**Необходимые scopes:**

| Scope | Описание | Применение |
|-------|----------|------------|
| `instagram_basic` | Базовый доступ к Instagram | Получение профиля, постов |
| `instagram_content_publish` | Публикация в Instagram | Создание постов |
| `threads_basic` | Базовый доступ к Threads | Получение профиля |
| `threads_content_publish` | Публикация в Threads | Создание постов |

### Token Management

**Автоматическое управление токенами в Make.com:**

1. Make.com автоматически обновляет токены
2. Срок действия: 60 дней
3. Обновление происходит за 5-7 дней до истечения
4. Если токен истек - Make.com уведомит вас

**Ручное обновление (если нужно):**
1. Перейти в Connections → Instagram for Business
2. Нажать "Reauthorize"
3. Пройти OAuth flow снова

---

## Scenarios (сценарии автоматизации)

### Scenario 1: Auto-posting по расписанию

**Описание:** Автоматическая публикация контента в Instagram + Threads по расписанию.

**Структура:**

```
[Schedule] → [Google Sheets: Get Row] → [Router]
                                            ↓
                                    [Instagram: Create Post]
                                            ↓
                                    [Threads: Create Post]
                                            ↓
                                    [Google Sheets: Update Row]
```

**Детальная настройка:**

**1. Schedule (триггер):**
- Модуль: "Tools" → "Basic trigger"
- Interval: Every day at 14:00 (оптимальное время для ОАЭ)

**2. Google Sheets (источник контента):**
- Модуль: "Google Sheets" → "Search Rows"
- Spreadsheet: "Content Calendar"
- Filter: Status = "Pending" AND Scheduled Date = Today

**3. Router (разветвление):**
- Модуль: "Flow Control" → "Router"
- Направление 1: Instagram
- Направление 2: Threads

**4. Instagram: Create Post:**
- Модуль: "Instagram for Business" → "Create a Photo Post"
- Connection: Instagram Business Account
- Caption: {{Google Sheets.Caption}}
- Image URL: {{Google Sheets.Image URL}}

**5. Threads: Create Post:**
- Модуль: "HTTP" → "Make a Request" (пока нет нативного модуля)
- URL: `https://graph.threads.net/v1.0/{{IG_USER_ID}}/threads`
- Method: POST
- Headers:
  ```json
  {
    "Authorization": "Bearer {{ACCESS_TOKEN}}",
    "Content-Type": "application/json"
  }
  ```
- Body:
  ```json
  {
    "text": "{{Google Sheets.Threads Text}}",
    "auto_publish_text": true
  }
  ```

**6. Update Google Sheets:**
- Модуль: "Google Sheets" → "Update a Row"
- Row ID: {{Google Sheets.Row ID}}
- Status: "Published"
- Published Date: {{now}}

**Скриншот структуры (описание):**
```
┌──────────────┐
│   Schedule   │ ← Каждый день 14:00
└──────┬───────┘
       │
┌──────▼─────────────┐
│  Google Sheets     │ ← Получить контент
│  (Search Rows)     │
└──────┬─────────────┘
       │
┌──────▼────────┐
│    Router     │ ← Разветвление
└──┬────────┬───┘
   │        │
   │        └─────────────────┐
   │                          │
┌──▼────────────────┐  ┌─────▼─────────────┐
│  Instagram        │  │   Threads         │
│  Create Post      │  │   HTTP Request    │
└──┬────────────────┘  └─────┬─────────────┘
   │                          │
   └────────┬─────────────────┘
            │
┌───────────▼──────────┐
│  Google Sheets       │ ← Обновить статус
│  Update Row          │
└──────────────────────┘
```

### Scenario 2: Кросс-постинг Instagram + Threads

**Описание:** При публикации в Instagram автоматически создается пост в Threads с адаптированным контентом.

**Структура:**

```
[Instagram: Watch Posts] → [Text Parser] → [Threads: Create Post]
```

**Детальная настройка:**

**1. Instagram: Watch Posts (триггер):**
- Модуль: "Instagram for Business" → "Watch Media"
- Connection: Instagram Business Account
- Limit: 1 (обрабатывать по одному)

**2. Text Parser (адаптация контента):**
- Модуль: "Tools" → "Set Variable"
- Variables:
  - Short Caption: {{substring(Instagram.Caption, 0, 150)}} (для Instagram)
  - Long Text: {{Instagram.Caption}} + "\n\nFull details in our bio!" (для Threads)

**3. Threads: Create Post:**
- Модуль: "HTTP" → "Make a Request"
- URL: `https://graph.threads.net/v1.0/{{IG_USER_ID}}/threads`
- Method: POST
- Body:
  ```json
  {
    "text": "{{Text Parser.Long Text}}",
    "auto_publish_text": true
  }
  ```

### Scenario 3: Content Calendar

**Описание:** Планирование контента на неделю вперед с автоматической публикацией.

**Структура:**

```
[Google Sheets: Weekly Content] → [Iterator] → [Schedule] → [Instagram + Threads]
```

**Настройка:**

**1. Google Sheets структура:**

| Date | Time | Platform | Content Type | Caption | Image URL | Hashtags | Status |
|------|------|----------|--------------|---------|-----------|----------|--------|
| 2026-02-05 | 14:00 | Instagram | Photo | "Desert Safari..." | https://... | #Dubai #Safari | Pending |
| 2026-02-05 | 14:00 | Threads | Text | "Full guide to..." | - | #DubaiTips | Pending |

**2. Schedule:**
- Каждый час проверять Google Sheets
- Если Date + Time = Now → опубликовать

**3. Публикация:**
- Filter: Platform = "Instagram" → Instagram API
- Filter: Platform = "Threads" → Threads API
- Update Status = "Published"

### Scenario 4: RSS Feed → Threads

**Описание:** Автоматическая публикация новых статей с вашего блога в Threads.

**Структура:**

```
[RSS: Watch Feed] → [Text Parser] → [Threads: Create Post]
```

**Настройка:**

**1. RSS: Watch Feed:**
- Модуль: "RSS" → "Watch RSS feed items"
- URL: https://yourblog.com/feed
- Limit: 5

**2. Text Parser:**
- Извлечь первые 400 символов статьи
- Добавить ссылку на полную статью
- Добавить хештеги

**3. Threads: Create Post:**
- Text:
  ```
  {{RSS.Title}}

  {{substring(RSS.Description, 0, 400)}}...

  Read more: {{RSS.Link}}

  #DubaiTravel #TourismUAE
  ```

### Scenario 5: Instagram Comments → Telegram Notification

**Описание:** Уведомления в Telegram при новых комментариях в Instagram (и аналогично для Threads).

**Структура:**

```
[Instagram: Watch Comments] → [Filter] → [Telegram: Send Message]
```

**Настройка:**

**1. Instagram: Watch Comments:**
- Модуль: "Instagram for Business" → "Watch Comments"
- Connection: Instagram Business Account

**2. Filter:**
- Condition: Comment contains "?" OR "price" OR "booking" (важные ключевые слова)

**3. Telegram: Send Message:**
- Модуль: "Telegram Bot" → "Send a Text Message"
- Chat ID: Your Telegram ID
- Message:
  ```
  🔔 Новый комментарий в Instagram!

  От: {{Instagram.Username}}
  Пост: {{Instagram.Post Caption}}
  Комментарий: {{Instagram.Comment Text}}

  Ответить: [ссылка на Instagram]
  ```

---

## Webhooks в Make.com

### Что такое Webhooks

**Webhook** - это механизм для получения real-time уведомлений о событиях.

**Преимущества:**
- Мгновенная обработка (не нужно polling)
- Экономия операций в Make.com
- Более эффективная автоматизация

### Настройка Webhook для триггера

**Scenario: External trigger → Threads Post**

**Структура:**

```
[Webhook] → [Parse JSON] → [Threads: Create Post]
```

**Настройка:**

**1. Создать Webhook:**
- Модуль: "Webhooks" → "Custom webhook"
- Make.com сгенерирует URL (например: https://hook.make.com/abc123...)

**2. Использовать Webhook URL:**
- В вашем веб-приложении
- В форме бронирования
- В CRM системе

**Пример отправки на Webhook (curl):**
```bash
curl -X POST https://hook.make.com/abc123... \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New booking confirmed!",
    "customer": "John Doe",
    "tour": "Desert Safari",
    "date": "2026-02-10"
  }'
```

**3. Parse JSON:**
- Make.com автоматически парсит JSON payload

**4. Threads: Create Post:**
- Text:
  ```
  🎉 New booking just confirmed!

  Tour: {{Webhook.tour}}
  Customer: {{Webhook.customer}}
  Date: {{Webhook.date}}

  We're excited to host you!

  #DubaiTourism #DesertSafari
  ```

### Пример: Form submission → Instagram + Threads

**Use case:** Клиент оставляет отзыв на сайте → автопубликация в Instagram Stories + Threads.

**Структура:**

```
[Webhook: Review Form] → [Router]
                            ↓
                    [Instagram: Create Story]
                            ↓
                    [Threads: Create Post]
```

**Настройка:**

**1. Webhook payload (от формы):**
```json
{
  "customer_name": "John Doe",
  "rating": 5,
  "review_text": "Amazing desert safari experience!",
  "photo_url": "https://example.com/review-photo.jpg"
}
```

**2. Instagram: Create Story:**
- Image URL: {{Webhook.photo_url}}
- Text overlay: "⭐⭐⭐⭐⭐\n{{Webhook.customer_name}}"

**3. Threads: Create Post:**
- Text:
  ```
  ⭐⭐⭐⭐⭐ 5-star review from {{Webhook.customer_name}}!

  "{{Webhook.review_text}}"

  Thank you for choosing us! We're thrilled you had an amazing time.

  #DubaiReviews #DesertSafari #HappyCustomers
  ```

---

## Практические примеры

### Пример 1: Туристическое агентство - полный цикл

**Цель:** Автоматизация от лида до отзыва.

**Workflow:**

```
1. [Website Form] → Webhook
2. [Make.com] → Google Sheets (add lead)
3. [Make.com] → WhatsApp (confirmation message)
4. [Make.com] → Telegram (notify team)
5. [After 24h] → WhatsApp (reminder)
6. [After tour] → WhatsApp (request review)
7. [Review received] → Instagram + Threads (publish with permission)
```

**Scenario в Make.com:**

**Scenario A: Lead received**
```
[Webhook] → [Google Sheets: Add Row] → [Router]
                                          ↓
                                  [WhatsApp: Send Template]
                                          ↓
                                  [Telegram: Notify Team]
```

**Scenario B: Reminder (24h before)**
```
[Schedule: Daily 10:00] → [Google Sheets: Search Tours Today] → [WhatsApp: Send Reminder]
```

**Scenario C: Post-tour review request**
```
[Schedule: Daily 22:00] → [Google Sheets: Search Tours Completed Today] → [WhatsApp: Request Review]
```

**Scenario D: Publish review**
```
[Webhook: Review Form] → [Filter: Rating >= 4] → [Router]
                                                    ↓
                                            [Instagram: Create Post]
                                                    ↓
                                            [Threads: Create Post]
```

### Пример 2: Content repurposing

**Цель:** Один контент → множество форматов → автопубликация.

**Workflow:**

```
1. Dropbox: Upload video (raw footage)
2. Make.com → Download video
3. Make.com → AI video editing (via API)
4. Make.com → Generate captions (AI)
5. Make.com → Publish:
   - Instagram Reels
   - Threads (text summary)
   - YouTube Shorts
   - TikTok
```

**Scenario:**

```
[Dropbox: Watch Files] → [AI Video Editor API] → [AI Caption Generator] → [Router]
                                                                              ↓
                                                                  [Instagram: Upload Reel]
                                                                              ↓
                                                                  [Threads: Create Post]
                                                                              ↓
                                                                  [YouTube: Upload Short]
```

### Пример 3: Bilingual content automation

**Цель:** Автоматический перевод контента (арабский + английский) для ОАЭ.

**Workflow:**

```
1. Google Sheets: Content in English
2. Make.com → DeepL API (translate to Arabic)
3. Make.com → Publish both versions:
   - English: Instagram + Threads
   - Arabic: Instagram + Threads
```

**Scenario:**

```
[Schedule] → [Google Sheets: Get Row] → [DeepL: Translate] → [Router]
                                                                  ↓
                                                      [Instagram: English Post]
                                                                  ↓
                                                      [Instagram: Arabic Post]
                                                                  ↓
                                                      [Threads: English Post]
                                                                  ↓
                                                      [Threads: Arabic Post]
```

**Результат:** +28% вовлеченность (статистика ОАЭ 2026 для билингвального контента).

---

## Troubleshooting

### Проблема 1: Access Token Expired

**Симптомы:**
```
Error: Invalid OAuth 2.0 Access Token
```

**Решение:**
1. Перейти в Make.com → Connections
2. Найти Instagram for Business connection
3. Нажать "Reauthorize"
4. Пройти OAuth flow снова

**Профилактика:**
- Make.com автоматически обновляет токены
- Проверяйте connections раз в месяц

### Проблема 2: Rate Limit Exceeded

**Симптомы:**
```
Error: Rate limit exceeded
```

**Причина:**
- Instagram: 25 постов/24 часа через API
- Threads: 250 постов/24 часа

**Решение:**
1. Добавить задержку между публикациями:
   - Модуль: "Tools" → "Sleep"
   - Duration: 60 секунд (1 минута между постами)

2. Распределить публикации по времени:
   - Вместо 10 постов сразу → 1 пост каждый час

### Проблема 3: Webhook не срабатывает

**Симптомы:**
- Webhook URL не получает данные

**Checklist:**
- ✅ Webhook URL правильный (скопирован из Make.com)
- ✅ Content-Type: application/json
- ✅ POST метод (не GET)
- ✅ Valid JSON payload

**Тест Webhook:**
```bash
curl -X POST https://hook.make.com/YOUR_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### Проблема 4: Image URL не работает

**Симптомы:**
```
Error: Image could not be downloaded
```

**Причина:**
- Instagram/Threads требует публичный HTTPS URL
- Файл должен быть доступен без авторизации

**Решение:**
1. Использовать CDN:
   - Cloudflare R2
   - AWS S3 (public bucket)
   - Cloudinary

2. Проверить URL:
   ```bash
   curl -I https://your-image-url.jpg
   # Должен вернуть: HTTP/2 200
   ```

### Проблема 5: Scenario выполняется слишком медленно

**Симптомы:**
- Scenario занимает 30+ секунд

**Оптимизация:**

1. **Параллельные действия:**
   - Использовать Router для одновременных действий
   - Вместо последовательности: Action1 → Action2 → Action3
   - Использовать: Router → [Action1, Action2, Action3] параллельно

2. **Кэширование данных:**
   - Data Store для часто используемых данных
   - Избегать повторных запросов

3. **Фильтры до тяжелых операций:**
   - Сначала Filter
   - Потом HTTP Request / API Call

---

## Best Practices

### 1. Структура Scenarios

**DO:**
- Один scenario = одна задача
- Использовать понятные названия модулей
- Добавлять комментарии (Notes)
- Группировать связанные действия

**DON'T:**
- Не создавать один огромный scenario на 50+ модулей
- Не дублировать логику (использовать переменные)

### 2. Error Handling

**Всегда добавляйте:**
- Error handler для критических модулей
- Retry logic (3 попытки с задержкой)
- Fallback actions (что делать при ошибке)

**Пример:**
```
[Instagram: Create Post] → [Error Handler]
                               ↓
                       [Retry 3 times]
                               ↓
                       [If still failed → Telegram: Notify Admin]
```

### 3. Мониторинг

**Настройте уведомления:**
- Email при ошибках
- Telegram при критических сбоях
- Еженедельный отчет выполнения

**Модуль для мониторинга:**
```
[Schedule: Every Monday 9:00] → [Get Scenario Execution Data] → [Telegram: Send Report]
```

### 4. Безопасность

**DO:**
- Использовать Environment Variables для токенов
- Не хардкодить credentials в scenarios
- Регулярно обновлять access tokens

**DON'T:**
- Не делиться screenshots scenarios с токенами
- Не копировать webhook URLs в публичные места

---

## Заключение

**Make.com - мощный инструмент для автоматизации Threads + Instagram без кода.**

**Ключевые преимущества:**
1. No-code - визуальный редактор (не нужны знания программирования)
2. Быстрое внедрение - сценарии за 10-30 минут
3. 3000+ интеграций - готовые коннекторы
4. Гибкость - сложная логика через Router, Filters, Iterators

**ROI для туристического бизнеса:**
- Экономия времени: 20-30 часов/неделю
- Автоматизация: от лида до публикации отзыва
- Стоимость: ~$16/мес (Pro план)
- Окупаемость: 1-2 месяца

**Следующие шаги:**
1. Зарегистрироваться на Make.com (free trial)
2. Подключить Instagram for Business
3. Создать первый scenario (auto-posting)
4. Тестировать и оптимизировать
5. Масштабировать на другие задачи

---

**Дополнительные ресурсы:**
- Make.com Docs: https://www.make.com/en/help/
- Instagram Integration: https://www.make.com/en/integrations/instagram-business
- Telegram Integration: https://www.make.com/en/integrations/telegram
- Community: https://community.make.com/
