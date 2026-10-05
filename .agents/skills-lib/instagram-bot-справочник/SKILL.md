---
name: instagram-bot-справочник
description: "Production-ready руководство по Instagram Messenger API для DM-автоматизации. Бот-справочник для туристического бизнеса ОАЭ. Ice Breakers, Quick Replies, Private Replies, Generic Template. Используй когда нужно автоматизировать Instagram DM."
---

# Instagram Messenger API — Справочник DM-автоматизации

## Обзор

Instagram **не имеет** классического Bot API как Telegram. Вместо этого Meta предоставляет **Messenger API for Instagram** — часть Meta Platform для автоматизации DM (Direct Messages). Через него можно создавать автоответы, обрабатывать входящие сообщения, отправлять интерактивные элементы (кнопки, карточки, быстрые ответы) и строить полноценные чат-боты.

### Что можно автоматизировать

- Автоответы на входящие DM (текст, медиа, кнопки)
- Ice Breakers — приветственные вопросы при первом обращении
- Persistent Menu — постоянное меню в диалоге
- Quick Replies — быстрые ответы-кнопки
- Generic Template — карточки с изображением и кнопками
- Private Replies — автоответ в DM на комментарий к посту
- Story Mentions — обработка упоминаний в Stories
- Передача диалога живому оператору (Human Agent Handover)

### Критические ограничения

- **Нельзя писать первым** — бот отвечает только на входящие сообщения/действия пользователя
- **Нельзя делать массовые рассылки** — нет broadcast API
- **24-часовое окно** — можно отвечать только в течение 24 часов после последнего сообщения пользователя
- **Human Agent Tag** — продлевает окно до 7 дней, но только для живого оператора
- **200 API вызовов/час** на аккаунт (снижено с 5,000 в 2025)
- **Только Business/Creator аккаунты** — Personal не поддерживается

---

## Quick Start: Первый автоответ за 30 минут

### Шаг 1: Подготовка Meta App

1. Перейдите: https://developers.facebook.com/apps
2. Создайте приложение типа **Business**
3. Добавьте продукт **Messenger** (он же используется для Instagram)
4. Добавьте продукт **Webhooks**

### Шаг 2: Подключение Instagram

1. Instagram Settings → Account → Switch to Professional Account (Business)
2. Привяжите к Facebook Page
3. В Meta App Dashboard → Messenger → Settings → добавьте вашу Facebook Page
4. Сгенерируйте **Page Access Token**

### Шаг 3: Permissions (App Review)

Для production нужно пройти App Review и получить:

| Permission | Назначение | Доступ |
|-----------|-----------|--------|
| `instagram_basic` | Профиль и медиа | Сразу |
| `instagram_manage_messages` | Чтение/отправка DM | App Review |
| `instagram_manage_comments` | Управление комментариями | App Review |
| `pages_messaging` | Отправка сообщений через Page | App Review |

**Время рассмотрения:** 3-7 рабочих дней.

### Шаг 4: Webhook (Получение сообщений)

Настройте URL для получения событий от Meta:

```javascript
// Node.js + Express — верификация webhook
const express = require('express');
const app = express();

const VERIFY_TOKEN = 'my_secret_token_123';

// GET — верификация от Meta
app.get('/webhook', (req, res) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  if (mode === 'subscribe' && token === VERIFY_TOKEN) {
    console.log('Webhook verified');
    res.status(200).send(challenge);
  } else {
    res.sendStatus(403);
  }
});

// POST — входящие сообщения
app.post('/webhook', express.json(), (req, res) => {
  const body = req.body;

  if (body.object === 'instagram') {
    body.entry.forEach(entry => {
      entry.messaging.forEach(event => {
        if (event.message) {
          handleMessage(event);
        } else if (event.postback) {
          handlePostback(event);
        }
      });
    });
    res.status(200).send('EVENT_RECEIVED');
  } else {
    res.sendStatus(404);
  }
});

app.listen(3000);
```

### Шаг 5: Отправка ответа

```javascript
const axios = require('axios');

const PAGE_ACCESS_TOKEN = process.env.PAGE_ACCESS_TOKEN;

async function handleMessage(event) {
  const senderId = event.sender.id;
  const messageText = event.message.text;

  // Простой автоответ
  await sendMessage(senderId, {
    text: 'Спасибо за сообщение! Чем могу помочь?'
  });
}

async function sendMessage(recipientId, message) {
  await axios.post(
    'https://graph.facebook.com/v21.0/me/messages',
    {
      recipient: { id: recipientId },
      message: message
    },
    {
      params: { access_token: PAGE_ACCESS_TOKEN }
    }
  );
}
```

**Готово!** Бот отвечает на входящие DM.

---

## Архитектура

### Messenger API for Instagram vs Facebook Messenger

Instagram DM-боты работают через **тот же Messenger Platform**, что и Facebook Messenger боты. Основные отличия:

| Аспект | Facebook Messenger | Instagram DM |
|--------|-------------------|--------------|
| Webhook object | `page` | `instagram` |
| Первое сообщение от бота | Допускается (через m.me) | **Запрещено** |
| Массовые рассылки | Sponsored Messages | **Нет** |
| Persistent Menu | До 3 уровней | 1 уровень |
| Generic Template | До 10 карточек | До 10 карточек |
| Messaging Window | 24 часа | 24 часа |
| Human Agent Tag | 7 дней | 7 дней |

### Поток данных

```
Пользователь пишет DM
        ↓
Meta Webhook → POST /webhook (ваш сервер)
        ↓
Обработка event.messaging[].message
        ↓
Ответ через POST /me/messages (Graph API)
        ↓
Пользователь получает ответ в DM
```

### Типы Webhook-событий

Подпишитесь на эти поля в настройках Webhook:

| Поле | Описание |
|------|----------|
| `messages` | Текстовые сообщения, медиа, вложения |
| `messaging_postbacks` | Нажатия на кнопки (postback) |
| `messaging_referrals` | Переходы по IG.me ссылкам |
| `message_reactions` | Реакции на сообщения |
| `messaging_seen` | Прочтение сообщения |

---

## Аутентификация

### Получение Page Access Token

```bash
# 1. Получите User Access Token через Graph API Explorer
# https://developers.facebook.com/tools/explorer/

# 2. Обменяйте на Long-Lived Token (60 дней)
curl -X GET "https://graph.facebook.com/v21.0/oauth/access_token?\
grant_type=fb_exchange_token&\
client_id=APP_ID&\
client_secret=APP_SECRET&\
fb_exchange_token=SHORT_LIVED_TOKEN"

# 3. Получите Page Access Token
curl -X GET "https://graph.facebook.com/v21.0/me/accounts?\
access_token=LONG_LIVED_USER_TOKEN"
# → id страницы + access_token (бессрочный, если User Token long-lived)
```

### Instagram Business Account ID

```bash
curl -X GET "https://graph.facebook.com/v21.0/PAGE_ID?\
fields=instagram_business_account&\
access_token=PAGE_ACCESS_TOKEN"

# Ответ:
# { "instagram_business_account": { "id": "17841405309211844" } }
```

Этот ID используется для Ice Breakers, Persistent Menu и других настроек.

---

## Отправка сообщений

### Текст

```bash
curl -X POST "https://graph.facebook.com/v21.0/me/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": { "id": "USER_IGSID" },
    "message": { "text": "Добро пожаловать! Чем помочь?" }
  }' \
  --data-urlencode "access_token=PAGE_ACCESS_TOKEN"
```

### Изображение

```json
{
  "recipient": { "id": "USER_IGSID" },
  "message": {
    "attachment": {
      "type": "image",
      "payload": {
        "url": "https://example.com/desert_safari.jpg"
      }
    }
  }
}
```

### Поддерживаемые типы вложений

| Тип | Формат | Макс. размер |
|-----|--------|-------------|
| `image` | JPEG, PNG, GIF | 8 MB |
| `video` | MP4 | 25 MB |
| `audio` | AAC, MP4, WAV | 25 MB |
| `file` | PDF и др. | 25 MB |

**Стикеры:** Instagram не поддерживает отправку стикеров через API (только получение).

---

## Интерактивные элементы

### Quick Replies (быстрые ответы)

Кнопки под сообщением, которые исчезают после нажатия. Максимум 13 штук.

```json
{
  "recipient": { "id": "USER_IGSID" },
  "message": {
    "text": "Что вас интересует?",
    "quick_replies": [
      {
        "content_type": "text",
        "title": "Экскурсии",
        "payload": "EXCURSIONS"
      },
      {
        "content_type": "text",
        "title": "Трансферы",
        "payload": "TRANSFERS"
      },
      {
        "content_type": "text",
        "title": "Яхты",
        "payload": "YACHTS"
      },
      {
        "content_type": "text",
        "title": "Аренда авто",
        "payload": "CAR_RENTAL"
      }
    ]
  }
}
```

### Generic Template (карточки)

Горизонтальный скролл карточек с изображением, заголовком, подзаголовком и кнопками. До 10 карточек.

```json
{
  "recipient": { "id": "USER_IGSID" },
  "message": {
    "attachment": {
      "type": "template",
      "payload": {
        "template_type": "generic",
        "elements": [
          {
            "title": "Пустынное сафари",
            "subtitle": "Дюны, верблюды, BBQ ужин — 200 AED/чел",
            "image_url": "https://example.com/safari.jpg",
            "buttons": [
              {
                "type": "web_url",
                "url": "https://example.com/book/safari",
                "title": "Забронировать"
              },
              {
                "type": "postback",
                "title": "Подробнее",
                "payload": "SAFARI_DETAILS"
              }
            ]
          },
          {
            "title": "Морская прогулка на яхте",
            "subtitle": "Dubai Marina, 2-4 часа — от 800 AED",
            "image_url": "https://example.com/yacht.jpg",
            "buttons": [
              {
                "type": "web_url",
                "url": "https://example.com/book/yacht",
                "title": "Забронировать"
              },
              {
                "type": "postback",
                "title": "Подробнее",
                "payload": "YACHT_DETAILS"
              }
            ]
          }
        ]
      }
    }
  }
}
```

### Кнопки

Два типа:

| Тип | Действие | Использование |
|-----|----------|---------------|
| `web_url` | Открывает ссылку | Бронирование, каталог |
| `postback` | Отправляет payload боту | Навигация по меню |

### Ice Breakers

Приветственные вопросы, которые видит пользователь при первом открытии DM с вашим аккаунтом. Максимум **4 вопроса**.

```bash
# Установка Ice Breakers
curl -X POST "https://graph.facebook.com/v21.0/me/messenger_profile" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "instagram",
    "ice_breakers": [
      {
        "question": "Какие экскурсии есть?",
        "payload": "ICE_EXCURSIONS"
      },
      {
        "question": "Цены на трансферы",
        "payload": "ICE_TRANSFERS"
      },
      {
        "question": "Аренда яхты",
        "payload": "ICE_YACHTS"
      },
      {
        "question": "Связаться с менеджером",
        "payload": "ICE_HUMAN"
      }
    ]
  }' \
  --data-urlencode "access_token=PAGE_ACCESS_TOKEN"
```

Обработка нажатия:

```javascript
function handlePostback(event) {
  const payload = event.postback.payload;

  switch (payload) {
    case 'ICE_EXCURSIONS':
      sendExcursionsCatalog(event.sender.id);
      break;
    case 'ICE_TRANSFERS':
      sendTransferPrices(event.sender.id);
      break;
    case 'ICE_YACHTS':
      sendYachtOptions(event.sender.id);
      break;
    case 'ICE_HUMAN':
      handoverToHuman(event.sender.id);
      break;
  }
}
```

### Persistent Menu

Постоянное меню, доступное в любой момент диалога (иконка меню внизу чата). Максимум **20 пунктов** на одном уровне.

```bash
curl -X POST "https://graph.facebook.com/v21.0/me/messenger_profile" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "instagram",
    "persistent_menu": [
      {
        "locale": "default",
        "call_to_actions": [
          {
            "type": "postback",
            "title": "Каталог экскурсий",
            "payload": "MENU_EXCURSIONS"
          },
          {
            "type": "postback",
            "title": "Наши цены",
            "payload": "MENU_PRICES"
          },
          {
            "type": "web_url",
            "title": "Наш сайт",
            "url": "https://example.com"
          },
          {
            "type": "postback",
            "title": "Связаться с менеджером",
            "payload": "MENU_HUMAN"
          }
        ]
      }
    ]
  }' \
  --data-urlencode "access_token=PAGE_ACCESS_TOKEN"
```

---

## Private Replies (автоответ на комментарий в DM)

Когда пользователь оставляет комментарий к вашему посту, можно автоматически отправить ему DM. Это мощный инструмент для конвертации комментаторов в клиентов.

### Как работает

1. Пользователь комментирует пост (например: "Сколько стоит?")
2. Webhook получает событие `comments`
3. Бот отправляет Private Reply в DM пользователя
4. Пользователь видит DM от вас

### Реализация

```javascript
// Webhook получает комментарий
app.post('/webhook', (req, res) => {
  const body = req.body;

  if (body.object === 'instagram') {
    body.entry.forEach(entry => {
      if (entry.changes) {
        entry.changes.forEach(change => {
          if (change.field === 'comments') {
            handleComment(change.value);
          }
        });
      }
    });
  }
  res.status(200).send('OK');
});

// Отправка Private Reply
async function handleComment(comment) {
  const commentId = comment.id;
  const commentText = comment.text.toLowerCase();

  // Реагируем на ключевые слова
  if (commentText.includes('цена') || commentText.includes('price')
      || commentText.includes('сколько')) {
    await axios.post(
      `https://graph.facebook.com/v21.0/${commentId}/private_replies`,
      {
        message: 'Спасибо за интерес! Вот наши актуальные цены на экскурсии...'
      },
      { params: { access_token: PAGE_ACCESS_TOKEN } }
    );
  }
}
```

### Ограничения Private Replies

- **1 Private Reply на комментарий** — нельзя отправить повторно
- **Только для комментариев к вашим постам** — не для чужих
- **24-часовое окно** — ответ должен быть отправлен в течение 24 часов после комментария
- **Не работает для Live-комментариев**

---

## Story Mentions & Replies

### Когда пользователь упоминает вас в Stories

Webhook получает событие, когда кто-то упоминает ваш аккаунт (@mention) в своей Story.

```javascript
// Обработка story mention
function handleStoryMention(event) {
  const senderId = event.sender.id;
  const storyUrl = event.message?.attachments?.[0]?.payload?.url;

  // Отправляем благодарность
  sendMessage(senderId, {
    text: 'Спасибо, что упомянули нас в Stories! ' +
          'В качестве благодарности — скидка 10% на следующую экскурсию. ' +
          'Промокод: STORY10'
  });
}
```

### Когда пользователь отвечает на вашу Story

Ответы на Stories приходят как обычные сообщения с вложением типа `story_mention`.

```javascript
app.post('/webhook', (req, res) => {
  const body = req.body;
  body.entry?.forEach(entry => {
    entry.messaging?.forEach(event => {
      if (event.message?.reply_to?.story) {
        // Это ответ на нашу Story
        handleStoryReply(event);
      } else if (event.message) {
        handleMessage(event);
      }
    });
  });
  res.status(200).send('OK');
});
```

---

## Human Agent Handover

Передача диалога от бота живому оператору. Meta использует систему **Conversation Routing** (заменила старый Handover Protocol).

### Реализация через Quick Reply

```javascript
// Предложить переключение на оператора
async function offerHumanAgent(recipientId) {
  await sendMessage(recipientId, {
    text: 'Хотите поговорить с менеджером?',
    quick_replies: [
      {
        content_type: "text",
        title: "Да, подключите менеджера",
        payload: "HUMAN_AGENT"
      },
      {
        content_type: "text",
        title: "Нет, бот помогает",
        payload: "CONTINUE_BOT"
      }
    ]
  });
}

// Обработка выбора
function handleQuickReply(event) {
  const payload = event.message.quick_reply.payload;

  if (payload === 'HUMAN_AGENT') {
    // Передаём в Instagram Inbox (Meta Business Suite)
    // Отправляем с тегом HUMAN_AGENT для продления окна до 7 дней
    sendMessage(event.sender.id, {
      text: 'Менеджер скоро подключится! Среднее время ответа — 5 минут.'
    });

    // Уведомляем команду (Telegram, email, webhook)
    notifyTeam({
      customer: event.sender.id,
      lastMessage: event.message.text,
      channel: 'instagram'
    });
  }
}
```

### Human Agent Tag

Тег `HUMAN_AGENT` продлевает окно сообщений с 24 часов до **7 дней**. Важно: он предназначен **только для живого оператора**, не для автоматических сообщений.

```json
{
  "recipient": { "id": "USER_IGSID" },
  "message": { "text": "Менеджер на связи. Чем помочь?" },
  "messaging_type": "MESSAGE_TAG",
  "tag": "HUMAN_AGENT"
}
```

---

## Состояния диалога (FSM)

Для сложных сценариев используйте конечный автомат состояний (Finite State Machine).

### Пример: бронирование экскурсии

```javascript
// Хранение состояний (Redis, БД или in-memory)
const sessions = new Map();

function getSession(userId) {
  if (!sessions.has(userId)) {
    sessions.set(userId, { state: 'IDLE', data: {} });
  }
  return sessions.get(userId);
}

async function handleMessage(event) {
  const userId = event.sender.id;
  const text = event.message.text;
  const session = getSession(userId);

  switch (session.state) {
    case 'IDLE':
      if (text.match(/экскурси|тур|safari|сафари/i)) {
        session.state = 'CHOOSING_TOUR';
        await sendExcursionsCatalog(userId); // Generic Template
      } else if (text.match(/цен|price|стоим/i)) {
        await sendPriceList(userId);
      } else {
        await sendWelcome(userId); // Quick Replies с категориями
      }
      break;

    case 'CHOOSING_TOUR':
      session.data.tour = text;
      session.state = 'CHOOSING_DATE';
      await sendMessage(userId, {
        text: 'Отличный выбор! На какую дату?'
      });
      break;

    case 'CHOOSING_DATE':
      session.data.date = text;
      session.state = 'CHOOSING_GUESTS';
      await sendMessage(userId, {
        text: 'Сколько гостей?',
        quick_replies: [
          { content_type: 'text', title: '1', payload: 'GUESTS_1' },
          { content_type: 'text', title: '2', payload: 'GUESTS_2' },
          { content_type: 'text', title: '3-4', payload: 'GUESTS_3_4' },
          { content_type: 'text', title: '5+', payload: 'GUESTS_5_PLUS' }
        ]
      });
      break;

    case 'CHOOSING_GUESTS':
      session.data.guests = text;
      session.state = 'CONFIRMING';
      const { tour, date, guests } = session.data;
      await sendMessage(userId, {
        text: `Подтверждаю заявку:\n` +
              `Тур: ${tour}\n` +
              `Дата: ${date}\n` +
              `Гостей: ${guests}\n\n` +
              `Менеджер свяжется для подтверждения.`,
        quick_replies: [
          { content_type: 'text', title: 'Подтвердить', payload: 'CONFIRM' },
          { content_type: 'text', title: 'Изменить', payload: 'RESTART' }
        ]
      });
      break;

    case 'CONFIRMING':
      if (text === 'Подтвердить' || event.message?.quick_reply?.payload === 'CONFIRM') {
        session.state = 'IDLE';
        session.data = {};
        await sendMessage(userId, {
          text: 'Заявка принята! Менеджер свяжется с вами в ближайшее время.'
        });
        notifyTeam(session.data); // Уведомить менеджера
      } else {
        session.state = 'IDLE';
        session.data = {};
        await sendWelcome(userId);
      }
      break;
  }
}
```

---

## Модерация комментариев

### Автоматическое скрытие/удаление

```javascript
// Скрыть комментарий
async function hideComment(commentId) {
  await axios.post(
    `https://graph.facebook.com/v21.0/${commentId}`,
    { hide: true },
    { params: { access_token: PAGE_ACCESS_TOKEN } }
  );
}

// Удалить комментарий
async function deleteComment(commentId) {
  await axios.delete(
    `https://graph.facebook.com/v21.0/${commentId}`,
    { params: { access_token: PAGE_ACCESS_TOKEN } }
  );
}

// Автомодерация: скрыть спам
async function moderateComment(comment) {
  const spamPatterns = [
    /dm me for/i, /check (my|bio)/i, /follow me/i,
    /free followers/i, /click link/i, /bit\.ly/i
  ];

  const isSpam = spamPatterns.some(p => p.test(comment.text));
  if (isSpam) {
    await hideComment(comment.id);
    console.log(`Hidden spam comment: ${comment.id}`);
  }
}
```

---

## Webhook: безопасность

### Верификация подписи X-Hub-Signature-256

Каждый webhook-запрос от Meta содержит заголовок `X-Hub-Signature-256`. Всегда проверяйте его.

```javascript
const crypto = require('crypto');

function verifySignature(req, res, buf) {
  const signature = req.headers['x-hub-signature-256'];
  if (!signature) {
    throw new Error('Missing signature');
  }

  const expected = 'sha256=' + crypto
    .createHmac('sha256', process.env.APP_SECRET)
    .update(buf)
    .digest('hex');

  if (signature !== expected) {
    throw new Error('Invalid signature');
  }
}

// Middleware
app.use(express.json({ verify: verifySignature }));
```

---

## Rate Limits

### Текущие лимиты (2026)

| Параметр | Лимит | Примечание |
|---------|-------|------------|
| **API вызовов** | 200/час | На аккаунт (снижено с 5,000 в 2025) |
| **Messaging Window** | 24 часа | После последнего сообщения пользователя |
| **Human Agent Tag** | 7 дней | Только для живого оператора |
| **Private Reply** | 1 на комментарий | В течение 24 часов после комментария |
| **Ice Breakers** | 4 вопроса | На аккаунт |
| **Persistent Menu** | 20 пунктов | 1 уровень |
| **Quick Replies** | 13 кнопок | На сообщение |
| **Generic Template** | 10 карточек | На сообщение |
| **Медиа** | 8/25 MB | Фото 8 MB, видео/аудио/файлы 25 MB |

### Обработка превышения лимитов

```javascript
async function sendWithRateLimit(recipientId, message) {
  try {
    await sendMessage(recipientId, message);
  } catch (error) {
    if (error.response?.data?.error?.code === 613) {
      // Rate limit — ждём и пробуем снова
      console.log('Rate limit hit, queuing message...');
      messageQueue.push({ recipientId, message, retryAt: Date.now() + 3600000 });
    } else {
      throw error;
    }
  }
}
```

---

## Примеры для туризма ОАЭ

### 1. Автоответ на DM "цена?"

```javascript
async function handleMessage(event) {
  const text = event.message.text?.toLowerCase() || '';
  const userId = event.sender.id;

  if (text.match(/цен|price|стоимость|сколько|how much|прайс/i)) {
    await sendMessage(userId, {
      attachment: {
        type: 'template',
        payload: {
          template_type: 'generic',
          elements: [
            {
              title: 'Пустынное сафари — 200 AED',
              subtitle: 'Джип 4x4, верблюды, BBQ ужин, шоу-программа',
              image_url: 'https://example.com/safari.jpg',
              buttons: [
                { type: 'postback', title: 'Забронировать', payload: 'BOOK_SAFARI' }
              ]
            },
            {
              title: 'Burj Khalifa — от 170 AED',
              subtitle: 'Уровни 124-125 или 148 (At The Top SKY)',
              image_url: 'https://example.com/burj.jpg',
              buttons: [
                { type: 'postback', title: 'Выбрать уровень', payload: 'BOOK_BURJ' }
              ]
            },
            {
              title: 'Абу-Даби тур — 200 AED',
              subtitle: 'Grand Mosque, Royal Palace, Yas Island',
              image_url: 'https://example.com/abudhabi.jpg',
              buttons: [
                { type: 'postback', title: 'Забронировать', payload: 'BOOK_ABUDHABI' }
              ]
            }
          ]
        }
      }
    });
  }
}
```

### 2. Ice Breakers для туризма

```json
{
  "platform": "instagram",
  "ice_breakers": [
    { "question": "Экскурсии и билеты", "payload": "ICE_TOURS" },
    { "question": "Трансферы из аэропорта", "payload": "ICE_TRANSFERS" },
    { "question": "Аренда яхты", "payload": "ICE_YACHTS" },
    { "question": "Связаться с менеджером", "payload": "ICE_HUMAN" }
  ]
}
```

### 3. Private Reply — комментарий "сколько?" в DM

```javascript
async function handleComment(comment) {
  const text = comment.text.toLowerCase();

  if (text.match(/скольк|цен|price|how much|стоим/)) {
    await axios.post(
      `https://graph.facebook.com/v21.0/${comment.id}/private_replies`,
      {
        message: 'Привет! Спасибо за интерес.\n\n' +
                 'Вот актуальные цены:\n' +
                 '- Сафари: 200 AED\n' +
                 '- Burj Khalifa: от 170 AED\n' +
                 '- Абу-Даби тур: 200 AED\n\n' +
                 'Напишите, что интересует — подберу лучший вариант!'
      },
      { params: { access_token: PAGE_ACCESS_TOKEN } }
    );
  }
}
```

### 4. Story Mention — благодарность + промокод

```javascript
function handleStoryMention(event) {
  sendMessage(event.sender.id, {
    text: 'Спасибо, что поделились нами в Stories!\n\n' +
          'Дарим скидку 10% на любую экскурсию.\n' +
          'Промокод: STORY10\n\n' +
          'Действует 7 дней. Напишите, если нужна помощь с выбором!'
  });
}
```

---

## Деплой

### Node.js + Express (рекомендуется)

```bash
npm init -y
npm install express axios dotenv
```

Файл `.env`:
```
PAGE_ACCESS_TOKEN=EAA...
APP_SECRET=abc123...
VERIFY_TOKEN=my_custom_verify_token
PORT=3000
```

Для production используйте:
- **Heroku** — бесплатно для начала, `heroku.com`
- **Railway** — от $5/мес, `railway.app`
- **VPS** (DigitalOcean, Hetzner) — $5-10/мес с Nginx + PM2 + Let's Encrypt

### Python + FastAPI

```python
from fastapi import FastAPI, Request, HTTPException
import httpx, hmac, hashlib, os

app = FastAPI()
PAGE_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
APP_SECRET = os.getenv("APP_SECRET")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

@app.get("/webhook")
async def verify(hub_mode: str = "", hub_verify_token: str = "",
                 hub_challenge: str = ""):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(403)

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    if body.get("object") != "instagram":
        raise HTTPException(404)

    for entry in body.get("entry", []):
        for event in entry.get("messaging", []):
            if "message" in event:
                await handle_message(event)
    return "OK"

async def handle_message(event):
    user_id = event["sender"]["id"]
    text = event.get("message", {}).get("text", "")

    async with httpx.AsyncClient() as client:
        await client.post(
            "https://graph.facebook.com/v21.0/me/messages",
            params={"access_token": PAGE_TOKEN},
            json={
                "recipient": {"id": user_id},
                "message": {"text": f"Получил: {text}"}
            }
        )
```

---

## Библиотеки и инструменты

| Инструмент | Язык | Назначение |
|-----------|------|-----------|
| `axios` / `node-fetch` | Node.js | HTTP-запросы к Graph API |
| `httpx` / `aiohttp` | Python | Асинхронные HTTP-запросы |
| `bottender` | Node.js | Фреймворк для мессенджер-ботов (FB + IG) |
| `ManyChat` | No-code | Визуальный конструктор ботов (платный) |
| `Chatfuel` | No-code | Альтернативный конструктор |
| `ngrok` | Любой | Туннель для локальной разработки webhook |

---

## Ограничения Instagram (что нельзя)

1. **Нельзя писать первым** — бот может только отвечать на действия пользователя (DM, комментарий, Story mention, Ice Breaker)
2. **Нет массовых рассылок** — нет broadcast/newsletter API
3. **24-часовое окно** — после последнего сообщения пользователя. Вне окна отправка запрещена (кроме Human Agent Tag — 7 дней)
4. **Нет Sponsored Messages** — в отличие от Facebook Messenger
5. **Нет кнопки "Get Started"** — вместо неё Ice Breakers
6. **Personal аккаунты не поддерживаются** — только Business/Creator
7. **1 автоответ на комментарий** — Private Reply отправляется однократно
8. **Нет inline-кнопок в тексте** — только Quick Replies, Template, Persistent Menu
9. **Нет оплаты в чате** — нет платёжных кнопок (в отличие от Telegram)
10. **Стикеры** — можно получать, но нельзя отправлять через API

---

## Версия API

Текущая рекомендуемая: **v21.0** (2025-2026)

Базовый URL:
```
https://graph.facebook.com/v21.0/
```

Changelog: https://developers.facebook.com/docs/instagram-api/changelog

---

## Ресурсы

- Meta Developer Docs: https://developers.facebook.com/docs/instagram-messaging
- Messenger Platform: https://developers.facebook.com/docs/messenger-platform
- Graph API Explorer: https://developers.facebook.com/tools/explorer/
- Webhook Testing: https://developers.facebook.com/tools/debug/
- ngrok (локальная разработка): https://ngrok.com

---

**Версия справочника:** 1.0
**Дата создания:** 12.02.2026
**Автор:** Claude Code Agent
**Для:** Туристический бизнес в ОАЭ (Сухейль)

---

## Ресурсы скилла

| Файл | Описание |
|------|----------|
| references/faq.md | Часто задаваемые вопросы |
| references/troubleshooting.md | Решение проблем |
| references/cheatsheet.md | Шпаргалка |
