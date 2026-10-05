/**
 * ============================================================
 * ШАБЛОН: Node.js (Express) сервер для приёма вебхуков Taplink
 * ============================================================
 *
 * КАК ИСПОЛЬЗОВАТЬ:
 * 1. Установите зависимости:
 *    npm init -y
 *    npm install express axios dotenv
 *
 * 2. Создайте файл .env рядом с этим скриптом:
 *    TAPLINK_SECRET=ваша_секретная_фраза_из_taplink
 *    TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
 *    TELEGRAM_CHAT_ID=-100123456789
 *    PORT=3000
 *
 * 3. Запустите сервер:
 *    node webhook-handler.js
 *
 * 4. В Taplink: Настройки -> Модули -> Webhooks
 *    - URL: https://ваш-сервер.com/webhook/taplink
 *    - Secret Phrase: та же, что в .env
 *    - События: New lead, New payment
 *
 * ТРЕБОВАНИЯ: Node.js 18+, тариф Business в Taplink
 * ДЕПЛОЙ: Railway, Render, VPS, или любой хостинг с Node.js
 * ============================================================
 */

require('dotenv').config();
const express = require('express');
const crypto = require('crypto');
const axios = require('axios');

const app = express();

// ============================================================
// КОНФИГУРАЦИЯ — замените значениями из .env или напрямую
// ============================================================
const CONFIG = {
  // Секретная фраза из настроек вебхука Taplink
  TAPLINK_SECRET: process.env.TAPLINK_SECRET || 'YOUR_TAPLINK_SECRET_PHRASE',

  // Telegram Bot API токен (получить у @BotFather)
  TELEGRAM_BOT_TOKEN: process.env.TELEGRAM_BOT_TOKEN || 'YOUR_BOT_TOKEN',

  // ID чата/группы для уведомлений (узнать через @userinfobot или @getmyid_bot)
  TELEGRAM_CHAT_ID: process.env.TELEGRAM_CHAT_ID || 'YOUR_CHAT_ID',

  // Порт сервера
  PORT: process.env.PORT || 3000,
};

// ============================================================
// MIDDLEWARE: Получаем сырое тело запроса для проверки подписи
// ============================================================
// ВАЖНО: express.raw() нужен именно для маршрута вебхука,
// чтобы получить Buffer для вычисления HMAC
app.use('/webhook/taplink', express.raw({ type: 'application/json' }));

// Для остальных маршрутов — обычный JSON парсинг
app.use(express.json());

// ============================================================
// ФУНКЦИЯ: Проверка HMAC-SHA1 подписи Taplink
// ============================================================
/**
 * Верифицирует подпись вебхука Taplink.
 * Taplink отправляет заголовок taplink-signature с HMAC-SHA1 хешем.
 *
 * @param {Buffer} rawBody - Сырое тело запроса
 * @param {string} receivedSignature - Подпись из заголовка taplink-signature
 * @returns {boolean} true если подпись верна
 */
function verifyTaplinkSignature(rawBody, receivedSignature) {
  if (!receivedSignature) return false;

  const calculatedSignature = crypto
    .createHmac('sha1', CONFIG.TAPLINK_SECRET)
    .update(rawBody)
    .digest('hex');

  try {
    // timingSafeEqual предотвращает timing-атаки
    return crypto.timingSafeEqual(
      Buffer.from(calculatedSignature, 'utf8'),
      Buffer.from(receivedSignature, 'utf8')
    );
  } catch (err) {
    // Если длины строк не совпадают — подпись неверна
    return false;
  }
}

// ============================================================
// ФУНКЦИЯ: Отправка сообщения в Telegram
// ============================================================
/**
 * Отправляет текстовое сообщение через Telegram Bot API.
 *
 * @param {string} text - Текст сообщения (поддерживает HTML-разметку)
 * @param {object} [options] - Дополнительные параметры (reply_markup и т.д.)
 * @returns {Promise<object>} Ответ Telegram API
 */
async function sendTelegramMessage(text, options = {}) {
  const url = `https://api.telegram.org/bot${CONFIG.TELEGRAM_BOT_TOKEN}/sendMessage`;

  const payload = {
    chat_id: CONFIG.TELEGRAM_CHAT_ID,
    text: text,
    parse_mode: 'HTML',
    ...options,
  };

  try {
    const response = await axios.post(url, payload);
    return response.data;
  } catch (error) {
    console.error('[Telegram] Ошибка отправки:', error.response?.data || error.message);
    throw error;
  }
}

// ============================================================
// ФУНКЦИЯ: Форматирование новой заявки (leads.created)
// ============================================================
/**
 * Преобразует данные заявки Taplink в форматированное Telegram-сообщение.
 *
 * @param {object} data - Объект data из вебхука Taplink
 * @returns {string} HTML-форматированный текст для Telegram
 */
function formatLeadMessage(data) {
  // Извлекаем поля из records
  const records = data.records || [];
  const fields = records.map((r) => `  <b>${r.title}:</b> ${r.value}`).join('\n');

  // Ищем конкретные поля для быстрого доступа
  const phone = records.find((r) => r.type === '1')?.value || '';
  const name = records.find((r) => r.type === '3')?.value || records[0]?.value || 'Не указано';

  let message = '';
  message += `<b>Новая заявка с Taplink!</b>\n`;
  message += `━━━━━━━━━━━━━━━━━━\n`;
  message += `Заявка #${data.lead_number || '?'}\n`;
  message += `Страница: ${data.page_link || 'N/A'}\n`;
  message += `Время: ${data.tms_created || 'N/A'}\n\n`;
  message += `<b>Данные клиента:</b>\n`;
  message += fields || '  Нет данных';

  // Если есть телефон — добавляем быструю ссылку на WhatsApp
  if (phone) {
    const cleanPhone = phone.replace(/[^0-9+]/g, '').replace('+', '');
    message += `\n\n<a href="https://wa.me/${cleanPhone}">Написать в WhatsApp</a>`;
  }

  return message;
}

// ============================================================
// ФУНКЦИЯ: Форматирование нового платежа (payments.created)
// ============================================================
/**
 * Преобразует данные платежа Taplink в форматированное Telegram-сообщение.
 *
 * @param {object} data - Объект data из вебхука Taplink
 * @returns {string} HTML-форматированный текст для Telegram
 */
function formatPaymentMessage(data) {
  const records = data.records || [];
  const fields = records.map((r) => `  <b>${r.title}:</b> ${r.value}`).join('\n');

  let message = '';
  message += `<b>Новый платёж с Taplink!</b>\n`;
  message += `━━━━━━━━━━━━━━━━━━\n`;
  message += `Заказ #${data.order_number || '?'}\n`;
  message += `<b>Сумма: ${data.budget || '0'} ${data.currency_code || ''}</b>\n`;
  message += `Назначение: ${data.purpose || 'N/A'}\n`;
  message += `Время: ${data.tms_modify || 'N/A'}\n`;

  if (fields) {
    message += `\n<b>Данные клиента:</b>\n`;
    message += fields;
  }

  return message;
}

// ============================================================
// МАРШРУТ: Приём вебхуков Taplink
// ============================================================
app.post('/webhook/taplink', async (req, res) => {
  const signature = req.headers['taplink-signature'];

  // --- Шаг 1: Проверка подписи ---
  if (!verifyTaplinkSignature(req.body, signature)) {
    console.error(`[${new Date().toISOString()}] Неверная подпись вебхука`);
    return res.status(403).json({ error: 'Invalid signature' });
  }

  // --- Шаг 2: Парсинг данных ---
  let payload;
  try {
    payload = JSON.parse(req.body.toString());
  } catch (err) {
    console.error(`[${new Date().toISOString()}] Ошибка парсинга JSON:`, err.message);
    return res.status(400).json({ error: 'Invalid JSON' });
  }

  const { action, data } = payload;
  console.log(`[${new Date().toISOString()}] Получен вебхук: ${action}`);

  // --- Шаг 3: Обработка по типу события ---
  try {
    let message;

    switch (action) {
      case 'leads.created':
        // Новая заявка с формы
        message = formatLeadMessage(data);
        console.log(`[leads] Заявка #${data.lead_number} от ${data.ip}`);
        break;

      case 'payments.created':
        // Новый платёж
        message = formatPaymentMessage(data);
        console.log(`[payments] Заказ #${data.order_number}, сумма: ${data.budget} ${data.currency_code}`);
        break;

      default:
        // Неизвестный тип события — логируем, но не отправляем в Telegram
        console.log(`[webhook] Неизвестное событие: ${action}`);
        return res.status(200).json({ ok: true, note: 'Unknown action, ignored' });
    }

    // --- Шаг 4: Отправка в Telegram ---
    await sendTelegramMessage(message);
    console.log(`[Telegram] Сообщение отправлено успешно`);

    // Возвращаем 200 OK для Taplink
    res.status(200).json({ ok: true });

  } catch (error) {
    console.error(`[${new Date().toISOString()}] Ошибка обработки:`, error.message);

    // ВАЖНО: Возвращаем 200 даже при ошибке отправки в Telegram,
    // чтобы Taplink не делал повторные попытки (retry).
    // Если нужны ретраи — верните 500.
    res.status(200).json({ ok: true, warning: 'Processed with errors' });
  }
});

// ============================================================
// МАРШРУТ: Проверка работоспособности (health check)
// ============================================================
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'taplink-webhook-handler',
    timestamp: new Date().toISOString(),
  });
});

// ============================================================
// МАРШРУТ: Главная страница (информация)
// ============================================================
app.get('/', (req, res) => {
  res.json({
    service: 'Taplink Webhook Handler',
    webhook_endpoint: '/webhook/taplink',
    health_endpoint: '/health',
    docs: 'https://taplink.at/en/dev/webhooks.html',
  });
});

// ============================================================
// ЗАПУСК СЕРВЕРА
// ============================================================
app.listen(CONFIG.PORT, () => {
  console.log(`\n========================================`);
  console.log(`  Taplink Webhook Handler`);
  console.log(`  Порт: ${CONFIG.PORT}`);
  console.log(`  Эндпоинт: POST /webhook/taplink`);
  console.log(`  Health: GET /health`);
  console.log(`========================================\n`);
});
