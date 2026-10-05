// =============================================================================
// bot.js — Telegram-бот бронирования экскурсий и билетов ОАЭ
// Использует grammy (быстрый фреймворк для Telegram Bot API)
// =============================================================================

const { Bot, InlineKeyboard } = require('grammy');

// --- Конфигурация ---
const BOT_TOKEN = process.env.BOT_TOKEN;
const CURRENCY = process.env.TOURS_CURRENCY || 'AED';
const LANGUAGE = process.env.DEFAULT_LANGUAGE || 'ru';

if (!BOT_TOKEN) {
  console.error('BOT_TOKEN не задан. Установи переменную окружения.');
  process.exit(1);
}

// --- Каталог туров (в реальном проекте — из БД) ---
const tours = [
  { id: 1, name: 'Desert Safari Premium', price: 250, duration: '6 часов', emoji: '🏜️' },
  { id: 2, name: 'Dubai City Tour', price: 180, duration: '4 часа', emoji: '🏙️' },
  { id: 3, name: 'Abu Dhabi Full Day', price: 220, duration: '10 часов', emoji: '🕌' },
  { id: 4, name: 'Burj Khalifa At The Top', price: 260, duration: '1.5 часа', emoji: '🏗️' },
  { id: 5, name: 'Dubai Marina Yacht Cruise', price: 350, duration: '3 часа', emoji: '🛥️' },
];

// --- Инициализация бота ---
const bot = new Bot(BOT_TOKEN);

// Команда /start
bot.command('start', async (ctx) => {
  await ctx.reply(
    `Добро пожаловать! 🇦🇪\n\n` +
    `Мы предлагаем экскурсии и билеты по ОАЭ.\n` +
    `Валюта: ${CURRENCY}\n\n` +
    `Команды:\n` +
    `/tours — Список экскурсий\n` +
    `/book <id> — Забронировать тур\n` +
    `/help — Помощь`
  );
});

// Команда /tours — список доступных туров
bot.command('tours', async (ctx) => {
  const list = tours
    .map((t) => `${t.emoji} *${t.name}*\nЦена: ${t.price} ${CURRENCY} | ${t.duration}\nID: \`${t.id}\``)
    .join('\n\n');

  await ctx.reply(`🗺️ *Доступные туры:*\n\n${list}\n\nДля бронирования: /book <id>`, {
    parse_mode: 'Markdown',
  });
});

// Команда /book <id> — бронирование
bot.command('book', async (ctx) => {
  const tourId = parseInt(ctx.match, 10);
  const tour = tours.find((t) => t.id === tourId);

  if (!tour) {
    await ctx.reply('Тур не найден. Используй /tours для списка.');
    return;
  }

  const keyboard = new InlineKeyboard()
    .text('Подтвердить бронь', `confirm_${tour.id}`)
    .text('Отмена', 'cancel');

  await ctx.reply(
    `📋 *Бронирование:*\n\n` +
    `${tour.emoji} ${tour.name}\n` +
    `Цена: ${tour.price} ${CURRENCY}\n` +
    `Длительность: ${tour.duration}\n\n` +
    `Подтвердить?`,
    { parse_mode: 'Markdown', reply_markup: keyboard }
  );
});

// Обработка callback-кнопок
bot.callbackQuery(/^confirm_(\d+)$/, async (ctx) => {
  const tourId = parseInt(ctx.match[1], 10);
  const tour = tours.find((t) => t.id === tourId);
  const bookingId = `BK-${Date.now()}`;

  await ctx.editMessageText(
    `✅ *Бронирование подтверждено!*\n\n` +
    `Тур: ${tour.name}\n` +
    `Цена: ${tour.price} ${CURRENCY}\n` +
    `Номер брони: \`${bookingId}\`\n\n` +
    `Менеджер свяжется с вами в ближайшее время.`,
    { parse_mode: 'Markdown' }
  );
  await ctx.answerCallbackQuery('Бронь подтверждена!');
});

bot.callbackQuery('cancel', async (ctx) => {
  await ctx.editMessageText('Бронирование отменено.');
  await ctx.answerCallbackQuery();
});

// Команда /help
bot.command('help', async (ctx) => {
  await ctx.reply(
    `ℹ️ *Помощь*\n\n` +
    `/start — Главное меню\n` +
    `/tours — Список экскурсий\n` +
    `/book <id> — Забронировать тур\n\n` +
    `Офис: Дубай, Tecom (Barsha Heights)\n` +
    `Метро: Dubai Internet City`,
    { parse_mode: 'Markdown' }
  );
});

// --- Запуск ---
bot.start();
console.log(`Telegram-бот запущен (${LANGUAGE}, ${CURRENCY})`);
