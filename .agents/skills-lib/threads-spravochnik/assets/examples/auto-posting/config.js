// Конфигурация автопостинга
require('dotenv').config();

module.exports = {
  // Threads API
  threadsApi: {
    accessToken: process.env.ACCESS_TOKEN,
    igUserId: process.env.IG_USER_ID,
    baseUrl: 'https://graph.threads.net/v1.0'
  },

  // Расписание
  schedule: {
    timezone: process.env.TZ || 'Asia/Dubai',
    defaultSchedules: {
      morning: '0 9 * * *',     // 9:00 утра каждый день
      afternoon: '0 14 * * *',  // 14:00 днем каждый день
      evening: '0 20 * * *'     // 20:00 вечером каждый день
    }
  },

  // Retry настройки
  retry: {
    maxAttempts: 3,
    delay: 5000,              // 5 секунд
    backoffMultiplier: 2      // Экспоненциальный backoff
  },

  // Пути к файлам
  paths: {
    content: './content/posts.json',
    logs: './logs'
  },

  // Logging
  logging: {
    level: 'info',            // debug | info | warn | error
    toFile: true,
    toConsole: true
  }
};
