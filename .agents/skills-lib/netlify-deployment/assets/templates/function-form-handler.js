// Serverless Function: Form Handler with Notifications
// Путь: netlify/functions/submit-form.js
// URL: https://your-site.netlify.app/.netlify/functions/submit-form

// ВАЖНО: Установите environment variables в Netlify:
// TELEGRAM_BOT_TOKEN - токен бота для уведомлений
// TELEGRAM_CHAT_ID - ID чата для уведомлений
// ALLOWED_ORIGINS - разрешённые домены (опционально)

exports.handler = async (event, context) => {
  // CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  // Preflight
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  // Проверка метода
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method Not Allowed' })
    };
  }

  try {
    // Парсим данные формы
    const formData = JSON.parse(event.body);

    // Валидация
    const { name, email, phone, message, tour } = formData;

    if (!name || !phone) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({
          success: false,
          error: 'Имя и телефон обязательны'
        })
      };
    }

    // Простая проверка на спам (honeypot)
    if (formData.website) {
      console.log('Спам обнаружен');
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({ success: true })
      };
    }

    console.log('Новая заявка:', { name, email, phone, tour });

    // Отправка уведомления в Telegram
    const botToken = process.env.TELEGRAM_BOT_TOKEN;
    const chatId = process.env.TELEGRAM_CHAT_ID;

    if (botToken && chatId) {
      const telegramMessage = `
🎫 <b>Новая заявка с сайта!</b>

👤 <b>Имя:</b> ${name}
📧 <b>Email:</b> ${email || 'не указан'}
📱 <b>Телефон:</b> ${phone}
🎯 <b>Тур:</b> ${tour || 'не указан'}

💬 <b>Сообщение:</b>
${message || 'нет сообщения'}

⏰ ${new Date().toLocaleString('ru-RU', { timeZone: 'Asia/Dubai' })} (Dubai time)
      `.trim();

      const telegramUrl = `https://api.telegram.org/bot${botToken}/sendMessage`;

      await fetch(telegramUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          text: telegramMessage,
          parse_mode: 'HTML'
        })
      });

      console.log('Уведомление отправлено в Telegram');
    }

    // Опционально: сохранение в Google Sheets
    // await saveToGoogleSheets(formData);

    // Опционально: отправка email через SendGrid/Mailgun
    // await sendEmail(formData);

    // Успешный ответ
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        message: 'Заявка принята! Мы свяжемся с вами в ближайшее время.'
      })
    };

  } catch (error) {
    console.error('Ошибка обработки формы:', error);

    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        success: false,
        error: 'Ошибка сервера',
        message: error.message
      })
    };
  }
};

// ============================================
// КАК ИСПОЛЬЗОВАТЬ:
// ============================================

// 1. Создайте Telegram бота через @BotFather
// 2. Добавьте бота в группу или получите chat_id через @userinfobot
// 3. Добавьте в Netlify Environment Variables:
//    TELEGRAM_BOT_TOKEN=your_token
//    TELEGRAM_CHAT_ID=your_chat_id
// 4. В HTML форме:
/*
<form id="bookingForm">
  <input type="text" name="name" placeholder="Ваше имя" required>
  <input type="email" name="email" placeholder="Email">
  <input type="tel" name="phone" placeholder="Телефон" required>
  <input type="text" name="tour" placeholder="Какой тур?">
  <textarea name="message" placeholder="Сообщение"></textarea>

  <!-- Honeypot для защиты от спама -->
  <input type="text" name="website" style="display:none;">

  <button type="submit">Отправить заявку</button>
</form>

<script>
document.getElementById('bookingForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const formData = Object.fromEntries(new FormData(e.target));

  const response = await fetch('/.netlify/functions/submit-form', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  });

  const result = await response.json();

  if (result.success) {
    alert(result.message);
    e.target.reset();
  } else {
    alert('Ошибка: ' + result.error);
  }
});
</script>
*/
