# Telegram Ad Bot — Бот для автоматической продажи рекламы

## Описание

Production-ready Telegram бот для автоматизации продажи рекламы. Клиенты заказывают рекламу 24/7, оплачивают через Stripe, получают инвойс автоматически.

## Функции

- Меню с пакетами (Bronze, Silver, Gold, Platinum)
- Просмотр статистики канала
- Оформление заказа (выбор пакета)
- Оплата через Stripe (карты всех стран)
- Автоматический PDF инвойс
- Уведомление админа о новом заказе
- Добавление заказа в CRM (Notion)

## Tech Stack

- Node.js 18+
- Telegraf (Telegram Bot framework)
- Stripe API (payment processing)
- PDFKit (генерация PDF инвойсов)
- Notion API (CRM интеграция)
- PostgreSQL (база заказов, опционально)

## Установка

```bash
npm install telegraf stripe pdfkit @notionhq/client
```

## Конфигурация (.env)

```
TELEGRAM_BOT_TOKEN=your_bot_token_from_@BotFather
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
NOTION_API_KEY=secret_xxxxx
NOTION_DATABASE_ID=xxxxx
ADMIN_TELEGRAM_ID=123456789
```

## Структура

```
telegram-ad-bot/
├── bot.js                  # Главный файл бота
├── handlers/
│   ├── menu.js             # Обработка меню
│   ├── order.js            # Оформление заказа
│   └── payment.js          # Оплата и webhook
├── services/
│   ├── stripe.js           # Stripe интеграция
│   ├── invoice.js          # Генерация PDF инвойсов
│   └── notion.js           # Notion CRM интеграция
├── package.json
├── .env.example
└── README.md
```

## Пример кода (bot.js)

```javascript
const { Telegraf, Markup } = require('telegraf');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);

// Команда /start
bot.start((ctx) => {
  ctx.reply(
    'Добро пожаловать в AdBot!\n\n' +
    'Выберите действие:',
    Markup.keyboard([
      ['📦 Пакеты', '📊 Статистика'],
      ['🛒 Заказать рекламу', '💬 Связаться с админом']
    ]).resize()
  );
});

// Показать пакеты
bot.hears('📦 Пакеты', (ctx) => {
  ctx.reply(
    '**Пакеты размещения:**\n\n' +
    '🥉 **Bronze** (7,000₽)\n' +
    '- 1 пост в Telegram\n\n' +
    '🥈 **Silver** (12,000₽)\n' +
    '- 3 поста (Telegram + Instagram + Story)\n\n' +
    '🥇 **Gold** (25,000₽)\n' +
    '- 5 постов + 3 Stories + закреп (7 дней)\n\n' +
    '💎 **Platinum** (80,000₽/месяц)\n' +
    '- Месячное партнёрство (16 постов + YouTube)',
    { parse_mode: 'Markdown' }
  );
});

// Показать статистику
bot.hears('📊 Статистика', (ctx) => {
  ctx.reply(
    '**Статистика канала:**\n\n' +
    '👥 Подписчики: 10,000\n' +
    '📈 Охват: 4,000-5,000\n' +
    '💬 ERR: 6.5%\n' +
    '🌍 География: Россия 60%, ОАЭ 20%, Казахстан 10%\n' +
    '🎯 Возраст: 25-45 лет (80%)',
    { parse_mode: 'Markdown' }
  );
});

// Заказать рекламу
bot.hears('🛒 Заказать рекламу', (ctx) => {
  ctx.reply(
    'Выберите пакет:',
    Markup.inlineKeyboard([
      [Markup.button.callback('🥉 Bronze (7,000₽)', 'order_bronze')],
      [Markup.button.callback('🥈 Silver (12,000₽)', 'order_silver')],
      [Markup.button.callback('🥇 Gold (25,000₽)', 'order_gold')],
      [Markup.button.callback('💎 Platinum (80,000₽)', 'order_platinum')]
    ])
  );
});

// Обработка выбора пакета
bot.action(/order_(.+)/, async (ctx) => {
  const package = ctx.match[1];
  const prices = {
    bronze: 7000,
    silver: 12000,
    gold: 25000,
    platinum: 80000
  };

  const price = prices[package];

  // Создать Stripe Checkout сессию
  const session = await stripe.checkout.sessions.create({
    payment_method_types: ['card'],
    line_items: [{
      price_data: {
        currency: 'rub',
        product_data: {
          name: `Пакет ${package.toUpperCase()}`,
        },
        unit_amount: price * 100, // Stripe uses cents
      },
      quantity: 1,
    }],
    mode: 'payment',
    success_url: 'https://yourdomain.com/success',
    cancel_url: 'https://yourdomain.com/cancel',
    metadata: {
      telegram_user_id: ctx.from.id,
      telegram_username: ctx.from.username,
      package: package
    }
  });

  ctx.reply(
    `Пакет: ${package.toUpperCase()}\n` +
    `Цена: ${price}₽\n\n` +
    `Для оплаты перейдите по ссылке:\n${session.url}`,
    { parse_mode: 'Markdown' }
  );
});

// Webhook для подтверждения оплаты
// (Настроить отдельный Express сервер для получения webhook от Stripe)

bot.launch();
console.log('Bot started');
```

## Stripe Webhook (payment.js)

```javascript
const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const app = express();

app.post('/webhook', express.raw({type: 'application/json'}), async (req, res) => {
  const sig = req.headers['stripe-signature'];

  let event;
  try {
    event = stripe.webhooks.constructEvent(req.body, sig, process.env.STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;

    // Получить данные заказа
    const userId = session.metadata.telegram_user_id;
    const package = session.metadata.package;

    // Сгенерировать инвойс
    await generateInvoice(session);

    // Отправить инвойс клиенту
    await bot.telegram.sendDocument(userId, {
      source: 'invoice.pdf',
      filename: `Invoice_${session.id}.pdf`
    });

    // Уведомить админа
    await bot.telegram.sendMessage(
      process.env.ADMIN_TELEGRAM_ID,
      `🎉 Новый заказ!\n\n` +
      `Клиент: @${session.metadata.telegram_username}\n` +
      `Пакет: ${package}\n` +
      `Сумма: ${session.amount_total / 100}₽`
    );

    // Добавить в CRM (Notion)
    await addToNotion(session);
  }

  res.json({received: true});
});

app.listen(3000, () => console.log('Webhook server running on port 3000'));
```

## Генерация инвойса (invoice.js)

```javascript
const PDFDocument = require('pdfkit');
const fs = require('fs');

function generateInvoice(session) {
  const doc = new PDFDocument();
  doc.pipe(fs.createWriteStream('invoice.pdf'));

  doc.fontSize(20).text('INVOICE', 50, 50);
  doc.fontSize(12)
     .text(`Invoice #${session.id}`, 50, 100)
     .text(`Date: ${new Date().toLocaleDateString()}`, 50, 120);

  doc.text(`Bill To:`, 50, 160)
     .text(session.metadata.telegram_username, 50, 180);

  doc.text('Description', 50, 240)
     .text('Amount', 400, 240);

  doc.text(`Пакет ${session.metadata.package.toUpperCase()}`, 50, 260)
     .text(`${session.amount_total / 100} RUB`, 400, 260);

  doc.fontSize(14)
     .text(`Total: ${session.amount_total / 100} RUB`, 400, 300);

  doc.end();
}
```

## Интеграция с Notion CRM (notion.js)

```javascript
const { Client } = require('@notionhq/client');
const notion = new Client({ auth: process.env.NOTION_API_KEY });

async function addToNotion(session) {
  await notion.pages.create({
    parent: { database_id: process.env.NOTION_DATABASE_ID },
    properties: {
      'Клиент': { title: [{ text: { content: session.metadata.telegram_username } }] },
      'Пакет': { select: { name: session.metadata.package } },
      'Сумма': { number: session.amount_total / 100 },
      'Статус': { select: { name: 'Оплачено' } },
      'Дата': { date: { start: new Date().toISOString() } }
    }
  });
}
```

## Запуск

```bash
# Запустить бота
node bot.js

# Запустить webhook сервер (в отдельном терминале)
node payment.js
```

## Тестирование

1. Найти бота в Telegram: @YourAdBot
2. Нажать /start
3. Выбрать "Заказать рекламу"
4. Выбрать пакет
5. Перейти по ссылке Stripe Checkout
6. Оплатить тестовой картой (4242 4242 4242 4242)
7. Получить инвойс в Telegram

## Деплой (Production)

**Heroku:**
```bash
heroku create your-ad-bot
git push heroku main
heroku config:set TELEGRAM_BOT_TOKEN=xxx STRIPE_SECRET_KEY=xxx
```

**Vercel:**
- Бот → Vercel Serverless Function
- Webhook → отдельный endpoint

## Стоимость

- Stripe: 2.9% + $0.30 за транзакцию
- Heroku: бесплатно (до 550 часов/месяц)
- Vercel: бесплатно (до 100GB bandwidth)

## ROI

- Экономия времени: 10+ часов/неделю
- Автоматизация: 24/7 приём заказов
- Окупаемость: первый месяц (при 3+ заказах/месяц)

---

*Последнее обновление: 05 февраля 2026*
