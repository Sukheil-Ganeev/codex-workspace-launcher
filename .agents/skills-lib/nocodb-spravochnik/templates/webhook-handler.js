/**
 * NocoDB Webhooks v3 -- Express.js обработчик
 * ============================================
 * Использование:
 *   1. npm install express
 *   2. Заполнить настройки (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
 *   3. node webhook-handler.js
 *   4. В NocoDB: Settings -> Webhooks -> URL: http://your-server:3000/webhook/nocodb
 *
 * Обрабатывает события: record.after.insert, record.after.update, record.after.delete
 * Отправляет уведомления в Telegram.
 */

const express = require('express');
const app = express();

// --- Настройки (ОБЯЗАТЕЛЬНО заполнить) ---
const PORT = process.env.PORT || 3000;
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || 'YOUR_BOT_TOKEN_HERE';  // Получить у @BotFather
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID || 'YOUR_CHAT_ID_HERE';        // ID чата/группы

// Опциональный секрет для верификации webhooks (если настроен в NocoDB)
const WEBHOOK_SECRET = process.env.NOCODB_WEBHOOK_SECRET || '';

// --- Middleware ---
app.use(express.json({ limit: '10mb' }));

// =============================================================================
// Отправка сообщения в Telegram
// =============================================================================

/**
 * Отправить текстовое сообщение в Telegram.
 * @param {string} text - Текст сообщения (поддерживает HTML)
 */
async function sendTelegram(text) {
  const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: TELEGRAM_CHAT_ID,
        text: text,
        parse_mode: 'HTML',
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      console.error(`Telegram API ошибка: ${response.status} ${error}`);
    }
  } catch (err) {
    console.error('Ошибка отправки в Telegram:', err.message);
  }
}

// =============================================================================
// Форматирование сообщений для разных событий
// =============================================================================

/**
 * Форматировать сообщение о новой записи.
 * @param {object} data - Данные из webhook payload
 * @returns {string} HTML-текст для Telegram
 */
function formatInsertMessage(data) {
  const tableName = data.table_name || 'Таблица';
  const rows = data.rows || [];

  if (rows.length === 0) return null;

  // Берем первую запись для отображения
  const row = rows[0];
  const title = row['Название'] || row['Title'] || row['ФИО'] || row['Компания'] || `ID: ${row.Id}`;

  let message = `<b>Новая запись в "${tableName}"</b>\n\n`;
  message += `<b>${title}</b>\n`;

  // Показываем ключевые поля (пропускаем служебные)
  const skipFields = ['Id', 'CreatedAt', 'UpdatedAt', 'nc_order'];
  for (const [key, value] of Object.entries(row)) {
    if (skipFields.includes(key) || value === null || value === '') continue;
    if (typeof value === 'object') continue; // Пропускаем вложенные объекты (links)
    message += `${key}: ${value}\n`;
  }

  if (rows.length > 1) {
    message += `\n<i>...и ещё ${rows.length - 1} запись(ей)</i>`;
  }

  return message;
}

/**
 * Форматировать сообщение об обновлении записи.
 * @param {object} data - Данные из webhook payload
 * @returns {string} HTML-текст для Telegram
 */
function formatUpdateMessage(data) {
  const tableName = data.table_name || 'Таблица';
  const rows = data.rows || [];
  const previousRows = data.previous_rows || [];

  if (rows.length === 0) return null;

  const row = rows[0];
  const prevRow = previousRows[0] || {};
  const title = row['Название'] || row['Title'] || row['ФИО'] || `ID: ${row.Id}`;

  let message = `<b>Обновление в "${tableName}"</b>\n\n`;
  message += `<b>${title}</b>\n`;

  // Показываем изменившиеся поля
  const skipFields = ['Id', 'UpdatedAt', 'nc_order'];
  let hasChanges = false;

  for (const [key, newValue] of Object.entries(row)) {
    if (skipFields.includes(key)) continue;
    if (typeof newValue === 'object') continue;

    const oldValue = prevRow[key];
    if (oldValue !== undefined && oldValue !== newValue) {
      message += `${key}: <s>${oldValue}</s> -> <b>${newValue}</b>\n`;
      hasChanges = true;
    }
  }

  if (!hasChanges) {
    message += '<i>Детали изменений недоступны</i>\n';
  }

  return message;
}

/**
 * Форматировать сообщение об удалении записи.
 * @param {object} data - Данные из webhook payload
 * @returns {string} HTML-текст для Telegram
 */
function formatDeleteMessage(data) {
  const tableName = data.table_name || 'Таблица';
  const rows = data.previous_rows || data.rows || [];

  if (rows.length === 0) return null;

  const row = rows[0];
  const title = row['Название'] || row['Title'] || row['ФИО'] || `ID: ${row.Id}`;

  let message = `<b>Удаление из "${tableName}"</b>\n\n`;
  message += `Удалена запись: <b>${title}</b>\n`;

  if (rows.length > 1) {
    message += `<i>Всего удалено: ${rows.length} запись(ей)</i>`;
  }

  return message;
}

// =============================================================================
// Основной endpoint для NocoDB webhooks
// =============================================================================

app.post('/webhook/nocodb', async (req, res) => {
  const payload = req.body;

  // --- Верификация секрета (если настроен) ---
  if (WEBHOOK_SECRET) {
    const headerSecret = req.headers['x-webhook-secret'] || req.headers['x-nocodb-signature'] || '';
    if (headerSecret !== WEBHOOK_SECRET) {
      console.warn('Webhook отклонён: неверный секрет');
      return res.status(401).json({ error: 'Unauthorized' });
    }
  }

  // --- Логирование ---
  console.log(`[${new Date().toISOString()}] Webhook: ${payload.type || 'unknown'}`);

  // --- Определение типа события ---
  const eventType = payload.type || '';
  const data = payload.data || {};
  let message = null;

  switch (eventType) {
    // Webhook v3 формат
    case 'records.after.insert':
      message = formatInsertMessage(data);
      break;

    case 'records.after.update':
      message = formatUpdateMessage(data);
      break;

    case 'records.after.delete':
      message = formatDeleteMessage(data);
      break;

    // Webhook v2 / legacy формат (для совместимости)
    case 'record.after.insert':
      message = formatInsertMessage(data);
      break;

    case 'record.after.update':
      message = formatUpdateMessage(data);
      break;

    case 'record.after.delete':
      message = formatDeleteMessage(data);
      break;

    default:
      console.log(`Неизвестный тип события: ${eventType}`);
      console.log('Payload:', JSON.stringify(payload, null, 2));
  }

  // --- Отправка в Telegram ---
  if (message) {
    await sendTelegram(message);
  }

  // NocoDB ожидает 200 OK
  res.status(200).json({ status: 'ok', event: eventType });
});

// =============================================================================
// Healthcheck endpoint
// =============================================================================

app.get('/health', (req, res) => {
  res.json({ status: 'ok', uptime: process.uptime() });
});

// =============================================================================
// Запуск сервера
// =============================================================================

app.listen(PORT, () => {
  console.log(`NocoDB Webhook Handler запущен на порту ${PORT}`);
  console.log(`Endpoint: POST http://localhost:${PORT}/webhook/nocodb`);
  console.log(`Health:   GET  http://localhost:${PORT}/health`);
  console.log('');
  console.log('Настройка в NocoDB:');
  console.log('  1. Settings -> Webhooks -> Add Webhook');
  console.log(`  2. URL: http://YOUR_SERVER_IP:${PORT}/webhook/nocodb`);
  console.log('  3. Event: выберите нужные триггеры');
  console.log('  4. Method: POST');
  console.log('');

  if (TELEGRAM_BOT_TOKEN.includes('YOUR_')) {
    console.warn('ВНИМАНИЕ: Не настроен TELEGRAM_BOT_TOKEN!');
    console.warn('Получите токен у @BotFather в Telegram.');
  }
  if (TELEGRAM_CHAT_ID.includes('YOUR_')) {
    console.warn('ВНИМАНИЕ: Не настроен TELEGRAM_CHAT_ID!');
    console.warn('Узнайте ID через @userinfobot или @getidsbot.');
  }
});
