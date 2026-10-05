// API endpoint для обработки формы
// Endpoint: https://your-domain.vercel.app/api/submit-form

export default async function handler(req, res) {
  // Разрешить только POST запросы
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { name, email, message } = req.body;
    
    // Валидация данных
    if (!name || !email || !message) {
      return res.status(400).json({ 
        error: 'Все поля обязательны для заполнения' 
      });
    }
    
    // Простая валидация email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({ 
        error: 'Некорректный email адрес' 
      });
    }
    
    // Логирование (в production используйте базу данных)
    console.log('Новое сообщение:', {
      name,
      email,
      message,
      timestamp: new Date().toISOString()
    });
    
    // ВАРИАНТ 1: Отправка в Telegram
    // const TELEGRAM_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
    // const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;
    // 
    // if (TELEGRAM_TOKEN && TELEGRAM_CHAT_ID) {
    //   const telegramMessage = `
    // 🆕 Новое сообщение с сайта
    // 
    // 👤 Имя: ${name}
    // 📧 Email: ${email}
    // 💬 Сообщение: ${message}
    //   `;
    //   
    //   await fetch(`https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`, {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({
    //       chat_id: TELEGRAM_CHAT_ID,
    //       text: telegramMessage
    //     })
    //   });
    // }
    
    // ВАРИАНТ 2: Отправка на email через SendGrid/Mailgun/др.
    // const sgMail = require('@sendgrid/mail');
    // sgMail.setApiKey(process.env.SENDGRID_API_KEY);
    // 
    // await sgMail.send({
    //   to: 'your-email@example.com',
    //   from: 'noreply@yourdomain.com',
    //   subject: `Новое сообщение от ${name}`,
    //   text: message,
    //   html: `<p><strong>Имя:</strong> ${name}</p>
    //          <p><strong>Email:</strong> ${email}</p>
    //          <p><strong>Сообщение:</strong> ${message}</p>`
    // });
    
    // ВАРИАНТ 3: Сохранение в базу данных
    // const { MongoClient } = require('mongodb');
    // const client = new MongoClient(process.env.MONGODB_URI);
    // 
    // await client.connect();
    // const db = client.db('contacts');
    // await db.collection('messages').insertOne({
    //   name,
    //   email,
    //   message,
    //   createdAt: new Date()
    // });
    // await client.close();
    
    return res.status(200).json({ 
      success: true,
      message: 'Сообщение успешно отправлено' 
    });
    
  } catch (error) {
    console.error('Ошибка обработки формы:', error);
    return res.status(500).json({ 
      error: 'Внутренняя ошибка сервера' 
    });
  }
}
