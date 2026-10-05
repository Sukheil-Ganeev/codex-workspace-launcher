# Meta Messenger Bot — FAQ

## Общие вопросы

### Q: Можно ли одним ботом обслуживать и Instagram, и Facebook?
Да. Один Meta App + один webhook обрабатывает оба канала. Различие: `body.object === 'instagram'` vs `body.object === 'page'`. Один Page Access Token работает для обоих.

### Q: Какую версию Graph API использовать?
**v22.0** (актуальна 2025-2026). Базовый URL: `https://graph.facebook.com/v22.0/`.

### Q: Нужен ли App Review?
Для тестирования — нет (работает с аккаунтами разработчиков). Для production — да, нужно пройти App Review и получить permissions (`instagram_manage_messages`, `pages_messaging`). Срок: 3-7 рабочих дней.

### Q: Чем отличается PSID от IGSID?
**PSID** (Page-Scoped ID) — уникальный ID пользователя для Facebook Page. **IGSID** — аналог для Instagram. Разные Pages/аккаунты видят разные ID одного человека. **ASID** (App-Scoped ID) — ID в контексте приложения.

## Instagram-специфичные

### Q: Может ли бот написать пользователю первым в Instagram?
**Нет.** Бот может только отвечать на: входящее DM, нажатие Ice Breaker, комментарий (Private Reply), Story mention. Это фундаментальное ограничение Instagram.

### Q: Как работает 24-часовое окно в Instagram?
После последнего сообщения пользователя у бота есть 24 часа на ответ. После — отправка запрещена. **Human Agent Tag** продлевает окно до 7 дней, но только для живого оператора (не автоматических сообщений).

### Q: Можно ли делать рассылки в Instagram DM?
**Нет.** Instagram не имеет broadcast/newsletter API. Нет Sponsored Messages. Единственный способ — отвечать на действия пользователей.

### Q: Сколько API вызовов в час для Instagram?
**200 вызовов/час** на аккаунт (снижено с 5,000 в 2025). Ошибка 613 = rate limit.

### Q: Можно ли отправлять стикеры через Instagram API?
Нет. Можно только **получать** стикеры от пользователей, отправлять через API нельзя.

### Q: Что такое Private Replies?
Когда пользователь комментирует ваш пост, бот может отправить ему DM. Ограничения: 1 reply на комментарий, 24ч на отправку, не для Live-комментариев.

### Q: Persistent Menu в Instagram — сколько уровней?
**1 уровень**, до **20 пунктов**. В отличие от Facebook (3 уровня, 3 пункта/уровень). При настройке добавить `"platform": "instagram"`.

## Facebook-специфичные

### Q: Чем отличается One-Time Notification от Recurring?
**OTN** — одноразовое сообщение вне 24ч окна, токен до 1 года, пользователь даёт согласие один раз. **Recurring** — периодические уведомления (daily/weekly/monthly), пользователь подписывается, токен обновляется после каждого использования.

### Q: Как настроить wit.ai NLP?
App Dashboard -> Messenger Settings -> Built-in NLP -> включить. После этого каждое webhook-сообщение будет содержать `message.nlp` с intents и entities.

### Q: Что такое Handover Protocol?
Механизм передачи диалога между приложениями. **Primary Receiver** (бот) получает все сообщения. Через `pass_thread_control` передаёт оператору (**Secondary Receiver**). Оператор возвращает через `take_thread_control`.

### Q: Какие Message Tags доступны?
4 типа для отправки вне 24ч окна: `CONFIRMED_EVENT_UPDATE`, `POST_PURCHASE_UPDATE`, `ACCOUNT_UPDATE`, `HUMAN_AGENT`. Нарушение политики тегов ведёт к ограничению Page.

### Q: Receipt Template поддерживает AED?
Да. В поле `currency` указать `"AED"`. Полностью поддерживается для туризма ОАЭ.

### Q: Можно ли локализовать Persistent Menu?
Да. Указать `"locale": "ru_RU"` для русской версии, `"locale": "default"` для остальных. Поддерживается и для Greeting text с переменными `{{user_first_name}}`.

## Деплой и безопасность

### Q: Обязательно ли проверять X-Hub-Signature-256?
**Да.** Без проверки злоумышленник может отправлять поддельные webhook-запросы. Используй `crypto.timingSafeEqual()` для защиты от timing attacks.

### Q: Webhook не получает событий — что делать?
1. Проверь, что подписка на events активна (messages, messaging_postbacks)
2. Проверь, что сервер отвечает 200 OK за <5 секунд
3. Проверь VERIFY_TOKEN
4. Проверь HTTPS (Meta не отправляет на HTTP)
5. Посмотри Webhooks -> Test в App Dashboard

### Q: Какой хостинг выбрать?
- **Начало:** Railway ($5/мес), ngrok (для тестов)
- **Production:** VPS (DigitalOcean/Hetzner, $5-10/мес) + Nginx + PM2 + Let's Encrypt
- **Serverless:** AWS Lambda + API Gateway (оплата за вызовы)

### Q: Как тестировать webhook локально?
`ngrok http 3000` — создаёт временный HTTPS-туннель. Указать полученный URL в App Dashboard -> Webhooks. Помни: ngrok URL меняется при перезапуске (платный план = фиксированный домен).

## Production Implementation

### Q: Можно ли использовать одну БД для Telegram + Instagram + WhatsApp + Facebook ботов?
**Да.** Используй SQLite с `PRAGMA journal_mode=WAL` при init(). Каждая платформа получает уникальный user_id: Telegram (positive), VK (+10B), Instagram (-1..-999), WhatsApp (-1000..-1999), Facebook (-2000..-2999). Все методы бронирования и лояльности работают без изменений.

### Q: Обязательно ли `messaging_type` для Facebook Messenger?
**Да.** Каждый вызов Send API (кроме Sender Actions) ОБЯЗАН включать `messaging_type`. Без него API вернёт 400 ошибку. Значение по умолчанию — `RESPONSE` (ответ на сообщение в рамках 24ч). Для Instagram `messaging_type` не требуется.

### Q: Зачем нужны Sender Actions?
Sender Actions (`mark_seen`, `typing_on`, `typing_off`) значительно улучшают UX: пользователь видит, что бот "прочитал" и "печатает". Отправляй `mark_seen` при каждом входящем сообщении, `typing_on` перед длинными операциями (запрос к БД, построение карусели).

### Q: Get Started кнопка не отображается — что делать?
Get Started не появляется автоматически. Настрой через POST `/me/messenger_profile` с payload `{"get_started": {"payload": "GET_STARTED"}}`. После настройки при первом открытии чата пользователь увидит кнопку "Get Started", которая отправит postback с указанным payload.

### Q: Как отличить бронирования из разных платформ?
Используй уникальные `form_type`: Telegram = `GT`, Instagram = `IG_GT`, WhatsApp = `WA_GT`, Facebook = `FB_GT`. Плюс synthetic user_id из разных диапазонов.

### Q: Как уведомить менеджера о бронировании из Facebook?
Через прямой HTTP POST к Telegram Bot API (без aiogram): `httpx.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={...})`. Этот паттерн используется для всех non-Telegram ботов (Instagram, WhatsApp, Facebook).

### Q: Какой порт использовать для Facebook Messenger webhook?
Рекомендуемая конвенция: Instagram = 8081, WhatsApp = 8082, Facebook = 8083, Mini App = 8080. Все через ngrok для разработки.

### Q: PSID одинаковый для всех Pages?
**Нет.** PSID (Page-Scoped ID) уникален для каждой пары пользователь + Page. Один и тот же человек имеет разные PSID для разных Pages. Не путай с ASID (App-Scoped ID).
