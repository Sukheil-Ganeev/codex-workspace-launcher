// Serverless Function: Telegram Webhook Handler
// Путь: netlify/functions/webhook.js
// URL: https://your-site.netlify.app/.netlify/functions/webhook

// ВАЖНО: Установите environment variables в Netlify:
// BOT_TOKEN - токен вашего Telegram бота

exports.handler = async (event, context) => {
  // Проверка метода запроса
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method Not Allowed' })
    };
  }

  try {
    // Парсим тело запроса от Telegram
    const body = JSON.parse(event.body);

    // Извлекаем данные сообщения
    const message = body.message;
    const chatId = message.chat.id;
    const text = message.text;

    console.log('Получено сообщение:', text, 'от', chatId);

    // Пример: простой эхо-бот
    if (text) {
      const botToken = process.env.BOT_TOKEN;
      const telegramApiUrl = `https://api.telegram.org/bot${botToken}/sendMessage`;

      // Отправляем ответ пользователю
      const response = await fetch(telegramApiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          text: `Вы написали: ${text}`
        })
      });

      const result = await response.json();
      console.log('Ответ отправлен:', result);
    }

    // Возвращаем успех Telegram
    return {
      statusCode: 200,
      body: JSON.stringify({ ok: true })
    };

  } catch (error) {
    console.error('Ошибка обработки webhook:', error);

    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'Internal Server Error',
        message: error.message
      })
    };
  }
};

// ============================================
// КАК ИСПОЛЬЗОВАТЬ:
// ============================================

// 1. Создайте бота через @BotFather в Telegram
// 2. Получите токен бота
// 3. Добавьте BOT_TOKEN в Netlify Environment Variables
// 4. Задеплойте сайт на Netlify
// 5. Установите webhook командой:
//    curl -F "url=https://your-site.netlify.app/.netlify/functions/webhook" \
//         https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook

// ============================================
// РАСШИРЕНИЯ:
// ============================================

// - Добавьте обработку команд (/start, /help)
// - Сохраняйте данные в базу (Google Sheets, Airtable)
// - Интегрируйте с CRM
// - Отправляйте уведомления администратору
