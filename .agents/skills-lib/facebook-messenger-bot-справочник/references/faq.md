# FAQ — Facebook Messenger Bot

## Основы

### 1. Нужна ли Facebook Page для бота?
Да. Messenger бот привязывается к Facebook Page. Пользователи общаются с ботом через Page, а не напрямую с приложением. Одна Page = один бот.

### 2. Сколько стоит Messenger Platform?
Бесплатно. Meta не берёт плату за Send API, шаблоны и webhook. Платишь только за хостинг своего сервера.

### 3. Чем PSID отличается от Facebook User ID?
PSID (Page-Scoped ID) — уникальный для каждой пары "пользователь + Page". Один человек имеет разные PSID для разных Pages. Нельзя сопоставить PSID между Pages без Account Linking.

### 4. Какая версия Graph API актуальна?
Graph API v22.0 (2025-2026). Meta депрекейтит старые версии каждые 2 года. Используй последнюю стабильную версию. Следи за changelog: developers.facebook.com/docs/graph-api/changelog

### 5. Можно ли отправлять сообщения первым?
Нет. Пользователь должен первым написать боту или нажать кнопку (Get Started, m.me ссылка, Send to Messenger plugin). После этого у тебя 24 часа на свободную переписку.

## Шаблоны и кнопки

### 6. Сколько элементов в Generic Template?
До 10 карточек в карусели. Каждая карточка: заголовок (80 символов), подзаголовок (80), до 3 кнопок, изображение.

### 7. Можно ли комбинировать шаблоны в одном сообщении?
Нет. Одно сообщение = один шаблон. Но можно отправить несколько сообщений подряд (с задержкой через Sender Actions).

### 8. Quick Replies исчезают после нажатия?
Да. Quick Replies одноразовые — после нажатия они пропадают. Для постоянной навигации используй Persistent Menu.

### 9. Какие типы кнопок можно использовать?
- `web_url` — открывает URL (с WebView)
- `postback` — отправляет payload боту
- `phone_number` — звонок
- `account_link` / `account_unlink` — вход/выход через Account Linking

## Правила и политики

### 10. Что такое 24-Hour Messaging Window?
После последнего сообщения пользователя у тебя 24 часа на отправку любых сообщений (включая промо). После 24ч — только Message Tags, OTN или Recurring Notifications.

### 11. Какие Message Tags разрешены?
- `CONFIRMED_EVENT_UPDATE` — обновление подтверждённого события
- `POST_PURCHASE_UPDATE` — обновление после покупки
- `ACCOUNT_UPDATE` — изменения аккаунта
- `HUMAN_AGENT` — ответ живого оператора (7 дней)

Промо-контент через теги запрещён. Нарушение = ограничение Page.

### 12. Чем OTN отличается от Recurring Notifications?
- **OTN** (One-Time Notification) — одно сообщение, одноразовый токен, срок до 1 года
- **Recurring Notifications** — подписка на серию (daily/weekly/monthly), токен обновляется после каждой отправки

### 13. Что случится если нарушить политику?
Meta может: ограничить отправку сообщений, заблокировать API для Page, в крайнем случае — удалить приложение. Всегда соблюдай 24ч окно и не злоупотребляй тегами.

## Технические вопросы

### 14. Как тестировать бота локально?
1. Используй `ngrok` для туннеля: `ngrok http 3000`
2. Укажи ngrok URL в настройках Webhook
3. Пиши боту из личного аккаунта Facebook
4. Для отладки: включи Page в режим разработки (тестовые пользователи)

### 15. Как получить бессрочный Page Access Token?
1. Получи Short-Lived User Token через Graph API Explorer
2. Обменяй на Long-Lived Token (60 дней) через `/oauth/access_token`
3. Запроси Page Token через `/me/accounts` с Long-Lived User Token
4. Этот Page Token будет бессрочным

### 16. Webhook не получает события — что делать?
- Проверь подписку на events (`messages`, `messaging_postbacks`)
- Убедись что сервер отвечает 200 OK на верификацию
- Проверь X-Hub-Signature-256 (если валидация включена)
- Посмотри логи в App Dashboard → Webhooks → Test
- Переподпишись через API: `POST /me/subscribed_apps`

### 17. Как обрабатывать вложения (фото, аудио)?
Вложения приходят в `event.message.attachments[]` с полями `type` и `payload.url`. URL временный (срок жизни ограничен). Скачивай и сохраняй сразу.

### 18. Можно ли отправлять сообщения нескольким пользователям одновременно?
Broadcast API депрекейтнут. Используй Recurring Notifications для подписчиков. Для массовой отправки — отправляй индивидуально через Send API с batch requests (до 50 запросов).

### 19. Как работает Handover Protocol с live chat?
1. Бот = Primary Receiver (получает все сообщения)
2. Live chat (Sprinklr, Zendesk и т.д.) = Secondary Receiver
3. При команде "оператор" бот вызывает `pass_thread_control`
4. Оператор общается через Secondary Receiver
5. После завершения — `take_thread_control` возвращает управление боту

### 20. Какой фреймворк выбрать?
- **Быстрый старт** → pymessenger (Python) или messenger-node (Node.js)
- **Production** → Botpress (visual builder + NLU)
- **Мультиплатформенный** → Bottender (Messenger + Telegram + WhatsApp)
- **Serverless** → Claudia Bot Builder (AWS Lambda)
