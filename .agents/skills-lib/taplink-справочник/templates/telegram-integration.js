/**
 * ============================================================
 * ШАБЛОН: Telegram Bot для приёма заявок с Taplink
 * ============================================================
 *
 * КАК ИСПОЛЬЗОВАТЬ:
 * 1. Создайте бота через @BotFather в Telegram:
 *    - Отправьте /newbot
 *    - Задайте имя и username
 *    - Скопируйте токен (BOT_TOKEN)
 *
 * 2. Узнайте CHAT_ID вашего чата/группы:
 *    - Добавьте бота в группу
 *    - Отправьте сообщение в группу
 *    - Откройте: https://api.telegram.org/botYOUR_TOKEN/getUpdates
 *    - Найдите "chat":{"id": XXXXXXX}
 *    (или используйте @getmyid_bot / @userinfobot)
 *
 * 3. Установите зависимости:
 *    npm init -y
 *    npm install express axios dotenv
 *
 * 4. Создайте файл .env:
 *    TAPLINK_SECRET=ваша_секретная_фраза
 *    TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
 *    TELEGRAM_CHAT_ID=-100123456789
 *    PORT=3000
 *
 * 5. Запустите:
 *    node telegram-integration.js
 *
 * 6. В Taplink: Настройки -> Модули -> Webhooks
 *    - URL: https://ваш-сервер.com/webhook/taplink
 *    - Secret Phrase: та же, что в .env
 *
 * ФУНКЦИИ:
 * - Приём данных от Taplink webhook (leads.created, payments.created)
 * - Форматированное сообщение в Telegram (имя, телефон, экскурсия, дата)
 * - Inline-кнопки: Подтвердить / Отклонить / Позвонить
 * - Обработка callback_query (нажатие кнопок)
 * - Обновление статуса заявки в сообщении
 *
 * ДЕПЛОЙ: Railway, Render, VPS
 * ============================================================
 */

require('dotenv').config();
const express = require('express');
const crypto = require('crypto');
const axios = require('axios');

const app = express();

// ============================================================
// КОНФИГУРАЦИЯ
// ============================================================
const CONFIG = {
  TAPLINK_SECRET: process.env.TAPLINK_SECRET || 'YOUR_TAPLINK_SECRET_PHRASE',
  TELEGRAM_BOT_TOKEN: process.env.TELEGRAM_BOT_TOKEN || 'YOUR_BOT_TOKEN',
  TELEGRAM_CHAT_ID: process.env.TELEGRAM_CHAT_ID || 'YOUR_CHAT_ID',
  PORT: process.env.PORT || 3000,
  // URL вашего сервера (нужен для настройки Telegram webhook)
  SERVER_URL: process.env.SERVER_URL || 'https://your-server.com',
};

const TELEGRAM_API = `https://api.telegram.org/bot${CONFIG.TELEGRAM_BOT_TOKEN}`;

// ============================================================
// MIDDLEWARE
// ============================================================
// Сырое тело для маршрута Taplink (нужно для HMAC)
app.use('/webhook/taplink', express.raw({ type: 'application/json' }));
// JSON для маршрута Telegram callback
app.use('/webhook/telegram', express.json());

// ============================================================
// TELEGRAM BOT API: Вспомогательные функции
// ============================================================

/**
 * Отправляет сообщение в Telegram с inline-кнопками.
 *
 * @param {string} text - Текст сообщения (HTML)
 * @param {object} replyMarkup - Объект inline_keyboard
 * @returns {Promise<object>} Ответ Telegram API
 */
async function sendTelegramMessage(text, replyMarkup = null) {
  const payload = {
    chat_id: CONFIG.TELEGRAM_CHAT_ID,
    text: text,
    parse_mode: 'HTML',
  };

  if (replyMarkup) {
    payload.reply_markup = JSON.stringify(replyMarkup);
  }

  try {
    const res = await axios.post(`${TELEGRAM_API}/sendMessage`, payload);
    return res.data;
  } catch (err) {
    console.error('[Telegram] Ошибка sendMessage:', err.response?.data || err.message);
    throw err;
  }
}

/**
 * Редактирует текст существующего сообщения в Telegram.
 * Используется для обновления статуса заявки.
 *
 * @param {string} chatId - ID чата
 * @param {number} messageId - ID сообщения для редактирования
 * @param {string} text - Новый текст
 * @param {object} replyMarkup - Новые кнопки (или null для удаления)
 */
async function editTelegramMessage(chatId, messageId, text, replyMarkup = null) {
  const payload = {
    chat_id: chatId,
    message_id: messageId,
    text: text,
    parse_mode: 'HTML',
  };

  if (replyMarkup) {
    payload.reply_markup = JSON.stringify(replyMarkup);
  }

  try {
    await axios.post(`${TELEGRAM_API}/editMessageText`, payload);
  } catch (err) {
    console.error('[Telegram] Ошибка editMessageText:', err.response?.data || err.message);
  }
}

/**
 * Отвечает на callback_query (убирает "часики" на кнопке).
 *
 * @param {string} callbackQueryId - ID callback
 * @param {string} text - Текст всплывающего уведомления
 */
async function answerCallbackQuery(callbackQueryId, text = '') {
  try {
    await axios.post(`${TELEGRAM_API}/answerCallbackQuery`, {
      callback_query_id: callbackQueryId,
      text: text,
    });
  } catch (err) {
    console.error('[Telegram] Ошибка answerCallbackQuery:', err.response?.data || err.message);
  }
}

// ============================================================
// ПРОВЕРКА ПОДПИСИ TAPLINK
// ============================================================
function verifyTaplinkSignature(rawBody, receivedSignature) {
  if (!receivedSignature) return false;
  const calculated = crypto
    .createHmac('sha1', CONFIG.TAPLINK_SECRET)
    .update(rawBody)
    .digest('hex');
  try {
    return crypto.timingSafeEqual(
      Buffer.from(calculated, 'utf8'),
      Buffer.from(receivedSignature, 'utf8')
    );
  } catch {
    return false;
  }
}

// ============================================================
// ИЗВЛЕЧЕНИЕ ПОЛЕЙ ИЗ RECORDS
// ============================================================

/**
 * Ищет значение поля в массиве records по заголовку или типу.
 *
 * @param {Array} records - Массив records из вебхука Taplink
 * @param {string} titleOrType - Название поля (title) или тип (type: 1=Phone, 2=Email, 3=Text)
 * @returns {string} Значение поля или пустая строка
 */
function extractField(records, titleOrType) {
  if (!records || !Array.isArray(records)) return '';

  // Сначала ищем по title (регистронезависимо)
  const byTitle = records.find(
    (r) => r.title && r.title.toLowerCase().includes(titleOrType.toLowerCase())
  );
  if (byTitle) return byTitle.value || '';

  // Затем по type
  const byType = records.find((r) => r.type === titleOrType);
  if (byType) return byType.value || '';

  return '';
}

// ============================================================
// ФОРМАТИРОВАНИЕ СООБЩЕНИЙ
// ============================================================

/**
 * Формирует сообщение о новой заявке с inline-кнопками.
 *
 * @param {object} data - Данные из вебхука Taplink
 * @returns {{ text: string, keyboard: object }} Текст и клавиатура
 */
function formatLeadWithButtons(data) {
  const records = data.records || [];

  // Извлекаем ключевые поля
  const name = extractField(records, 'name') || extractField(records, '3') || 'Не указано';
  const phone = extractField(records, 'phone') || extractField(records, '1') || '';
  const email = extractField(records, 'email') || extractField(records, '2') || '';
  const date = extractField(records, 'date') || extractField(records, 'дата') || '';
  const service = extractField(records, 'экскурсия') || extractField(records, 'тип') || extractField(records, 'пакет') || '';
  const guests = extractField(records, 'гост') || extractField(records, 'количество') || '';

  // Формируем текст сообщения
  let text = '';
  text += `<b>Новая заявка с Taplink</b>\n`;
  text += `━━━━━━━━━━━━━━━━━━\n\n`;
  text += `<b>Клиент:</b> ${name}\n`;

  if (phone) text += `<b>Телефон:</b> ${phone}\n`;
  if (email) text += `<b>Email:</b> ${email}\n`;
  if (service) text += `<b>Услуга:</b> ${service}\n`;
  if (date) text += `<b>Дата:</b> ${date}\n`;
  if (guests) text += `<b>Гостей:</b> ${guests}\n`;

  text += `\n<b>Заявка:</b> #${data.lead_number || '?'}\n`;
  text += `<b>Время:</b> ${data.tms_created || 'N/A'}\n`;
  text += `<b>Страница:</b> ${data.page_link || 'N/A'}\n`;

  // Все поля формы (если есть дополнительные)
  if (records.length > 0) {
    text += `\n<b>Все поля формы:</b>\n`;
    records.forEach((r) => {
      text += `  ${r.title}: ${r.value}\n`;
    });
  }

  text += `\n<i>Статус: Новая</i>`;

  // Формируем inline-кнопки
  const cleanPhone = phone.replace(/[^0-9]/g, '');
  const leadId = data.lead_id || data.lead_number || '0';

  const keyboard = {
    inline_keyboard: [
      [
        { text: 'Подтвердить', callback_data: `confirm_${leadId}` },
        { text: 'Отклонить', callback_data: `reject_${leadId}` },
      ],
      // Кнопка "Позвонить" — только если есть телефон
      ...(cleanPhone
        ? [[{ text: `Позвонить ${phone}`, url: `tel:${cleanPhone}` }]]
        : []),
      // Кнопка "WhatsApp" — только если есть телефон
      ...(cleanPhone
        ? [[{ text: 'Написать в WhatsApp', url: `https://wa.me/${cleanPhone}` }]]
        : []),
    ],
  };

  return { text, keyboard };
}

/**
 * Формирует сообщение о новом платеже.
 *
 * @param {object} data - Данные из вебхука Taplink
 * @returns {{ text: string, keyboard: object }} Текст и клавиатура
 */
function formatPaymentWithButtons(data) {
  const records = data.records || [];
  const name = extractField(records, 'name') || extractField(records, '3') || 'Не указано';
  const phone = extractField(records, 'phone') || extractField(records, '1') || '';

  let text = '';
  text += `<b>Новый платёж с Taplink</b>\n`;
  text += `━━━━━━━━━━━━━━━━━━\n\n`;
  text += `<b>Сумма: ${data.budget || '0'} ${data.currency_code || ''}</b>\n`;
  text += `<b>Клиент:</b> ${name}\n`;

  if (phone) text += `<b>Телефон:</b> ${phone}\n`;
  text += `<b>Назначение:</b> ${data.purpose || 'N/A'}\n`;
  text += `<b>Заказ:</b> #${data.order_number || '?'}\n`;
  text += `<b>Время:</b> ${data.tms_modify || 'N/A'}\n`;

  if (records.length > 0) {
    text += `\n<b>Данные клиента:</b>\n`;
    records.forEach((r) => {
      text += `  ${r.title}: ${r.value}\n`;
    });
  }

  const cleanPhone = phone.replace(/[^0-9]/g, '');

  const keyboard = {
    inline_keyboard: [
      ...(cleanPhone
        ? [[{ text: 'Написать в WhatsApp', url: `https://wa.me/${cleanPhone}` }]]
        : []),
    ],
  };

  return { text, keyboard };
}

// ============================================================
// МАРШРУТ: Приём вебхуков от Taplink
// ============================================================
app.post('/webhook/taplink', async (req, res) => {
  const signature = req.headers['taplink-signature'];

  // Проверка подписи
  if (!verifyTaplinkSignature(req.body, signature)) {
    console.error(`[${new Date().toISOString()}] Неверная подпись Taplink`);
    return res.status(403).json({ error: 'Invalid signature' });
  }

  let payload;
  try {
    payload = JSON.parse(req.body.toString());
  } catch (err) {
    console.error(`[${new Date().toISOString()}] Ошибка парсинга JSON:`, err.message);
    return res.status(400).json({ error: 'Invalid JSON' });
  }

  const { action, data } = payload;
  console.log(`[${new Date().toISOString()}] Taplink webhook: ${action}`);

  try {
    let formatted;

    switch (action) {
      case 'leads.created':
        formatted = formatLeadWithButtons(data);
        break;

      case 'payments.created':
        formatted = formatPaymentWithButtons(data);
        break;

      default:
        console.log(`[webhook] Неизвестное событие: ${action}`);
        return res.status(200).json({ ok: true });
    }

    // Отправляем сообщение с кнопками в Telegram
    await sendTelegramMessage(formatted.text, formatted.keyboard);
    console.log(`[Telegram] Сообщение отправлено (${action})`);

    res.status(200).json({ ok: true });
  } catch (error) {
    console.error(`[${new Date().toISOString()}] Ошибка:`, error.message);
    // Возвращаем 200, чтобы Taplink не ретраил
    res.status(200).json({ ok: true, warning: 'processed with errors' });
  }
});

// ============================================================
// МАРШРУТ: Обработка callback_query от Telegram (нажатие кнопок)
// ============================================================
app.post('/webhook/telegram', async (req, res) => {
  const update = req.body;

  // Обрабатываем только callback_query (нажатие inline-кнопок)
  if (!update.callback_query) {
    return res.status(200).json({ ok: true });
  }

  const callbackQuery = update.callback_query;
  const callbackData = callbackQuery.data;
  const chatId = callbackQuery.message.chat.id;
  const messageId = callbackQuery.message.message_id;
  const originalText = callbackQuery.message.text;
  const operatorName = callbackQuery.from.first_name || 'Оператор';

  console.log(`[Telegram] Callback: ${callbackData} от ${operatorName}`);

  try {
    // Определяем действие по callback_data
    if (callbackData.startsWith('confirm_')) {
      const leadId = callbackData.replace('confirm_', '');

      // Обновляем сообщение — меняем статус на "Подтверждена"
      const updatedText = originalText.replace(
        'Статус: Новая',
        `Статус: Подтверждена (${operatorName})`
      );

      await editTelegramMessage(chatId, messageId, updatedText, null);
      await answerCallbackQuery(callbackQuery.id, `Заявка #${leadId} подтверждена!`);

      console.log(`[Lead #${leadId}] Подтверждена оператором ${operatorName}`);

    } else if (callbackData.startsWith('reject_')) {
      const leadId = callbackData.replace('reject_', '');

      // Обновляем сообщение — меняем статус на "Отклонена"
      const updatedText = originalText.replace(
        'Статус: Новая',
        `Статус: Отклонена (${operatorName})`
      );

      await editTelegramMessage(chatId, messageId, updatedText, null);
      await answerCallbackQuery(callbackQuery.id, `Заявка #${leadId} отклонена`);

      console.log(`[Lead #${leadId}] Отклонена оператором ${operatorName}`);

    } else {
      await answerCallbackQuery(callbackQuery.id, 'Неизвестное действие');
    }
  } catch (error) {
    console.error('[Telegram] Ошибка обработки callback:', error.message);
    await answerCallbackQuery(callbackQuery.id, 'Ошибка обработки');
  }

  res.status(200).json({ ok: true });
});

// ============================================================
// МАРШРУТ: Настройка Telegram Webhook (вызвать один раз)
// ============================================================
/**
 * GET /setup-telegram-webhook
 * Регистрирует URL вашего сервера для получения обновлений Telegram.
 * Вызовите один раз после деплоя:
 *   curl https://ваш-сервер.com/setup-telegram-webhook
 */
app.get('/setup-telegram-webhook', async (req, res) => {
  const webhookUrl = `${CONFIG.SERVER_URL}/webhook/telegram`;

  try {
    const response = await axios.post(`${TELEGRAM_API}/setWebhook`, {
      url: webhookUrl,
      allowed_updates: ['callback_query'],
    });

    console.log('[Telegram] Webhook установлен:', webhookUrl);
    res.json({
      ok: true,
      webhook_url: webhookUrl,
      telegram_response: response.data,
    });
  } catch (err) {
    console.error('[Telegram] Ошибка установки webhook:', err.response?.data || err.message);
    res.status(500).json({ error: err.response?.data || err.message });
  }
});

// ============================================================
// МАРШРУТ: Health check
// ============================================================
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'taplink-telegram-integration',
    timestamp: new Date().toISOString(),
  });
});

// ============================================================
// ЗАПУСК СЕРВЕРА
// ============================================================
app.listen(CONFIG.PORT, () => {
  console.log(`\n========================================`);
  console.log(`  Taplink -> Telegram Integration`);
  console.log(`  Порт: ${CONFIG.PORT}`);
  console.log(`  Taplink webhook: POST /webhook/taplink`);
  console.log(`  Telegram webhook: POST /webhook/telegram`);
  console.log(`  Настройка TG: GET /setup-telegram-webhook`);
  console.log(`========================================\n`);
});
