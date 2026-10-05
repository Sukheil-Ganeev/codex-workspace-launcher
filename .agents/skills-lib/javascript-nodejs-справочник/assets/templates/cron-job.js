/**
 * Cron Job Template
 *
 * Production-ready scheduled tasks с:
 * - node-cron для расписания
 * - Логирование выполнения
 * - Error handling & retry
 * - Graceful shutdown
 *
 * @example
 * npm install node-cron dotenv
 */

const cron = require('node-cron');
const { promises: fs } = require('fs');

// ==================== CRON JOBS REGISTRY ====================

const jobs = new Map();

/**
 * Зарегистрировать cron job
 *
 * @param {string} name - Название задачи
 * @param {string} schedule - Cron выражение (см. примеры ниже)
 * @param {Function} handler - Асинхронная функция-обработчик
 * @param {Object} options - { runOnInit, timezone }
 *
 * @example
 * // Каждый день в 3:00 AM
 * registerJob('daily-backup', '0 3 * * *', backupDatabase);
 *
 * // Каждые 15 минут
 * registerJob('sync-data', '*/15 * * * *', syncData);
 *
 * // Каждый понедельник в 9:00 AM
 * registerJob('weekly-report', '0 9 * * 1', sendWeeklyReport);
 */
function registerJob(name, schedule, handler, options = {}) {
  try {
    const { runOnInit = false, timezone } = options;

    const job = cron.schedule(
      schedule,
      async () => {
        console.log(`[Cron] Running job: ${name}`);
        const startTime = Date.now();

        try {
          await handler();
          const duration = Date.now() - startTime;
          console.log(`[Cron] Completed: ${name} (${duration}ms)`);
        } catch (error) {
          console.error(`[Cron] Error in ${name}:`, error.message);
          // TODO: Отправить уведомление об ошибке
        }
      },
      { scheduled: true, timezone }
    );

    // Запустить сразу при инициализации
    if (runOnInit) {
      console.log(`[Cron] Running on init: ${name}`);
      handler().catch((error) => {
        console.error(`[Cron] Init error in ${name}:`, error.message);
      });
    }

    jobs.set(name, job);
    console.log(`[Cron] Registered: ${name} (${schedule})`);

    return job;
  } catch (error) {
    console.error(`[Cron] Registration error for ${name}:`, error.message);
    throw error;
  }
}

// ==================== BUSINESS LOGIC JOBS ====================

/**
 * Синхронизация данных с внешним API
 */
async function syncDataWithAPI() {
  // TODO: Реализовать логику синхронизации
  console.log('[Job] Syncing data with API...');

  // const response = await fetch('https://api.example.com/data');
  // const data = await response.json();
  // await updateDatabase(data);

  return {
    success: true,
    recordsProcessed: 0,
  };
}

/**
 * Отправить email отчеты
 */
async function sendDailyReports() {
  console.log('[Job] Sending daily reports...');

  // TODO: Реализовать логику отправки отчетов
  // const bookings = await getBookingsSummary();
  // await sendEmail({
  //   to: 'admin@example.com',
  //   subject: 'Daily Bookings Report',
  //   html: generateReportHTML(bookings)
  // });

  return {
    success: true,
    emailsSent: 1,
  };
}

/**
 * Очистить временные файлы
 */
async function cleanupTempFiles() {
  console.log('[Job] Cleaning up temporary files...');

  const uploadDir = process.env.UPLOAD_DIR || './uploads';
  const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 дней
  const now = Date.now();

  try {
    const files = await fs.readdir(uploadDir);
    let deletedCount = 0;

    for (const file of files) {
      const filepath = `${uploadDir}/${file}`;
      const stats = await fs.stat(filepath);

      if (now - stats.mtimeMs > maxAge) {
        await fs.unlink(filepath);
        deletedCount++;
      }
    }

    console.log(`[Job] Deleted ${deletedCount} old files`);
    return { success: true, deletedCount };
  } catch (error) {
    console.error('[Job] Cleanup error:', error.message);
    throw error;
  }
}

/**
 * Архивировать старые данные
 */
async function archiveOldData() {
  console.log('[Job] Archiving old data...');

  // TODO: Архивировать данные старше определенного срока
  // const cutoffDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000); // 30 дней
  // const oldBookings = await Booking.find({ createdAt: { $lt: cutoffDate } });
  // await archiveToStorage(oldBookings);

  return {
    success: true,
    recordsArchived: 0,
  };
}

/**
 * Отправить reminder уведомления
 */
async function sendBookingReminders() {
  console.log('[Job] Sending booking reminders...');

  // TODO: Найти бронирования с датой завтра
  // const tomorrow = new Date();
  // tomorrow.setDate(tomorrow.getDate() + 1);
  // const upcomingBookings = await Booking.find({
  //   tourDate: { $gte: tomorrow, $lt: new Date(tomorrow.getTime() + 24 * 60 * 60 * 1000) }
  // });
  //
  // for (const booking of upcomingBookings) {
  //   await sendEmail({
  //     to: booking.email,
  //     subject: 'Напоминание о вашем туре',
  //     html: `Ваш тур запланирован на ${booking.tourDate.toLocaleDateString('ru-RU')}`
  //   });
  // }

  return {
    success: true,
    remindersSent: 0,
  };
}

/**
 * Database backup
 */
async function backupDatabase() {
  console.log('[Job] Creating database backup...');

  // TODO: Реализовать backup логику
  // const backup = await createDatabaseSnapshot();
  // await uploadToCloudStorage(backup);

  return {
    success: true,
    backupId: `backup-${Date.now()}`,
  };
}

/**
 * Проверить здоровье приложения
 */
async function healthCheck() {
  console.log('[Job] Running health check...');

  const checks = {
    database: await checkDatabase(),
    api: await checkExternalAPI(),
    diskSpace: await checkDiskSpace(),
  };

  const allHealthy = Object.values(checks).every((check) => check.status === 'healthy');

  if (!allHealthy) {
    console.error('[HealthCheck] Issues detected:', checks);
    // TODO: Отправить alert
  }

  return { success: allHealthy, checks };
}

// ==================== HELPER FUNCTIONS ====================

async function checkDatabase() {
  try {
    // TODO: Проверить соединение с БД
    return { status: 'healthy', message: 'DB connected' };
  } catch {
    return { status: 'unhealthy', message: 'DB disconnected' };
  }
}

async function checkExternalAPI() {
  try {
    // TODO: Проверить API endpoint
    return { status: 'healthy', message: 'API responding' };
  } catch {
    return { status: 'unhealthy', message: 'API down' };
  }
}

async function checkDiskSpace() {
  try {
    // TODO: Проверить свободное место на диске
    return { status: 'healthy', message: 'Disk space OK' };
  } catch {
    return { status: 'unhealthy', message: 'Low disk space' };
  }
}

// ==================== INITIALIZATION ====================

/**
 * Инициализировать все cron jobs
 *
 * @example
 * // В main.js или app.js
 * await initializeCronJobs();
 */
async function initializeCronJobs() {
  console.log('[Cron] Initializing scheduled jobs...');

  // Синхронизация каждые 30 минут
  registerJob('sync-api', '*/30 * * * *', syncDataWithAPI);

  // Отправить отчеты в 6:00 AM каждый день
  registerJob('daily-reports', '0 6 * * *', sendDailyReports);

  // Очистить файлы каждый день в 2:00 AM
  registerJob('cleanup-temp', '0 2 * * *', cleanupTempFiles);

  // Архивировать данные в первый день месяца
  registerJob('archive-data', '0 4 1 * *', archiveOldData);

  // Отправить напоминания каждый день в 8:00 AM
  registerJob('send-reminders', '0 8 * * *', sendBookingReminders);

  // Backup БД каждый день в 3:00 AM
  registerJob('db-backup', '0 3 * * *', backupDatabase);

  // Health check каждые 5 минут
  registerJob('health-check', '*/5 * * * *', healthCheck);

  console.log('[Cron] All jobs initialized');
}

/**
 * Остановить все jobs gracefully
 *
 * @example
 * // При завершении приложения
 * process.on('SIGTERM', async () => {
 *   await stopAllJobs();
 *   process.exit(0);
 * });
 */
async function stopAllJobs() {
  console.log('[Cron] Stopping all scheduled jobs...');

  for (const [name, job] of jobs) {
    job.stop();
    console.log(`[Cron] Stopped: ${name}`);
  }

  jobs.clear();
  console.log('[Cron] All jobs stopped');
}

// ==================== EXPORTS ====================

module.exports = {
  registerJob,
  initializeCronJobs,
  stopAllJobs,
  // Individual jobs for testing
  syncDataWithAPI,
  sendDailyReports,
  cleanupTempFiles,
  archiveOldData,
  sendBookingReminders,
  backupDatabase,
  healthCheck,
};

// ==================== CRON EXPRESSION EXAMPLES ====================

/*
Формат: second minute hour day-of-month month day-of-week

┌───────────── second (0 - 59)
│ ┌───────────── minute (0 - 59)
│ │ ┌───────────── hour (0 - 23)
│ │ │ ┌───────────── day of month (1 - 31)
│ │ │ │ ┌───────────── month (1 - 12)
│ │ │ │ │ ┌───────────── day of week (0 - 6) (0 = Sunday)
│ │ │ │ │ │
│ │ │ │ │ │
* * * * * *

Примеры:
- 0 0 * * * - Каждый день в 00:00
- 0 */4 * * * - Каждые 4 часа
- 0 0 * * 0 - Каждый понедельник в 00:00
- 0 0 1 * * - Первый день месяца
- */15 * * * * - Каждые 15 минут
*/
