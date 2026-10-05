// Главный файл автопостинга в Threads
// Автор: Claude Code Agent
// Дата: 05 февраля 2026

const cron = require('node-cron');
const fs = require('fs').promises;
const path = require('path');
const config = require('./config');
const ThreadsPostCreator = require('../../templates/post-creator');
const logger = require('./utils/logger');

class AutoPoster {
  constructor() {
    this.poster = new ThreadsPostCreator(
      config.threadsApi.accessToken,
      config.threadsApi.igUserId
    );
    this.contentPath = path.join(__dirname, config.paths.content);
    this.scheduledJobs = [];
  }

  // Загрузка контента из JSON
  async loadContent() {
    try {
      const data = await fs.readFile(this.contentPath, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      logger.error('Failed to load content:', error);
      return [];
    }
  }

  // Сохранение контента (обновление статуса posted)
  async saveContent(content) {
    try {
      await fs.writeFile(
        this.contentPath,
        JSON.stringify(content, null, 2),
        'utf8'
      );
    } catch (error) {
      logger.error('Failed to save content:', error);
    }
  }

  // Публикация поста с retry логикой
  async publishPost(post, attempt = 1) {
    const { id, text, imageUrl } = post;

    logger.info(`Publishing post ${id} (attempt ${attempt})...`);

    try {
      let result;

      if (imageUrl) {
        result = await this.poster.publishImage(imageUrl, text);
      } else {
        result = await this.poster.publishText(text);
      }

      if (result.success) {
        logger.info(`✅ Post ${id} published successfully! Post ID: ${result.postId}`);
        return result;
      } else {
        throw new Error(result.error || 'Unknown error');
      }

    } catch (error) {
      logger.error(`❌ Failed to publish post ${id}:`, error.message);

      // Retry logic
      if (attempt < config.retry.maxAttempts) {
        const delay = config.retry.delay * Math.pow(config.retry.backoffMultiplier, attempt - 1);
        logger.info(`Retrying in ${delay / 1000} seconds...`);
        await this.delay(delay);
        return this.publishPost(post, attempt + 1);
      } else {
        logger.error(`Max retry attempts reached for post ${id}`);
        throw error;
      }
    }
  }

  // Utility: задержка
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Планирование постов по расписанию
  async schedulePosts() {
    const content = await this.loadContent();

    logger.info(`Loaded ${content.length} posts from content file`);

    for (const post of content) {
      if (post.posted) {
        logger.info(`Post ${post.id} already posted, skipping`);
        continue;
      }

      if (!post.schedule) {
        logger.warn(`Post ${post.id} has no schedule, skipping`);
        continue;
      }

      // Валидация cron расписания
      if (!cron.validate(post.schedule)) {
        logger.error(`Invalid schedule for post ${post.id}: ${post.schedule}`);
        continue;
      }

      // Создание cron job для каждого поста
      const job = cron.schedule(post.schedule, async () => {
        logger.info(`Scheduled time reached for post ${post.id}`);

        try {
          await this.publishPost(post);

          // Обновление статуса в JSON
          post.posted = true;
          post.publishedAt = new Date().toISOString();
          await this.saveContent(content);

        } catch (error) {
          logger.error(`Failed to publish scheduled post ${post.id}:`, error);
        }
      }, {
        timezone: config.schedule.timezone
      });

      this.scheduledJobs.push({ postId: post.id, job });
      logger.info(`📅 Scheduled post ${post.id} with cron: ${post.schedule}`);
    }

    logger.info(`✅ All posts scheduled successfully! Total: ${this.scheduledJobs.length}`);
  }

  // Запуск автопостинга
  async start() {
    logger.info('🚀 Starting Threads Auto Poster...');
    logger.info(`Timezone: ${config.schedule.timezone}`);

    // Проверка credentials
    if (!config.threadsApi.accessToken || !config.threadsApi.igUserId) {
      logger.error('Missing ACCESS_TOKEN or IG_USER_ID in .env file');
      process.exit(1);
    }

    // Проверка наличия контента
    try {
      await fs.access(this.contentPath);
    } catch {
      logger.error(`Content file not found: ${this.contentPath}`);
      process.exit(1);
    }

    // Планирование постов
    await this.schedulePosts();

    logger.info('✅ Auto Poster is running. Press Ctrl+C to stop.');
  }

  // Остановка автопостинга
  stop() {
    logger.info('Stopping Auto Poster...');

    for (const { postId, job } of this.scheduledJobs) {
      job.stop();
      logger.info(`Stopped job for post ${postId}`);
    }

    logger.info('✅ Auto Poster stopped');
  }
}

// ============================================
// Запуск приложения
// ============================================

const autoPoster = new AutoPoster();

// Graceful shutdown
process.on('SIGINT', () => {
  logger.info('\nReceived SIGINT signal');
  autoPoster.stop();
  process.exit(0);
});

process.on('SIGTERM', () => {
  logger.info('\nReceived SIGTERM signal');
  autoPoster.stop();
  process.exit(0);
});

// Запуск
autoPoster.start().catch(error => {
  logger.error('Fatal error:', error);
  process.exit(1);
});
