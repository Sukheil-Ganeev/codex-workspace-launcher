// Пример Telegram webhook endpoint
// Endpoint: https://your-domain.vercel.app/api/webhook

export default async function handler(req, res) {
  // Разрешить только POST запросы
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Получить данные от Telegram
    const update = req.body;
    
    console.log('Получено обновление от Telegram:', JSON.stringify(update, null, 2));

    // Пример обработки текстового сообщения
    if (update.message && update.message.text) {
      const chatId = update.message.chat.id;
      const text = update.message.text;
      
      console.log(`Чат ID: ${chatId}, Текст: ${text}`);
      
      // Здесь можно добавить логику обработки команд
      // Например, отправить ответ через Telegram Bot API
      
      // Для отправки ответа используйте:
      // const TELEGRAM_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
      // await fetch(`https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({
      //     chat_id: chatId,
      //     text: 'Ваш ответ'
      //   })
      // });
    }

    // Telegram требует ответ 200 OK
    return res.status(200).json({ ok: true });
    
  } catch (error) {
    console.error('Ошибка обработки webhook:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
