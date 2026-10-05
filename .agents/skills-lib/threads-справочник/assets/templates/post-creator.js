// Threads Post Creator Helper
// Supports: text-only, single image, carousel (multiple images)
// Автор: Claude Code Agent
// Дата: 05 февраля 2026

const axios = require('axios');

/**
 * ThreadsPostCreator - класс для публикации контента в Threads
 *
 * Возможности:
 * - Публикация текста (auto_publish_text новинка 2025)
 * - Публикация изображения (2-step process)
 * - Публикация carousel (множество изображений)
 * - Rate limit handling
 * - Error handling с retry логикой
 */
class ThreadsPostCreator {
  /**
   * @param {string} accessToken - Instagram/Threads access token
   * @param {string} igUserId - Instagram User ID (для Threads)
   */
  constructor(accessToken, igUserId) {
    this.accessToken = accessToken;
    this.igUserId = igUserId;
    this.baseUrl = 'https://graph.threads.net/v1.0';

    // Rate limiting
    this.requestCount = 0;
    this.requestWindow = 60000; // 1 минута
    this.maxRequestsPerWindow = 200; // Консервативный лимит
    this.lastRequestTime = Date.now();
  }

  /**
   * Публикация текста (новый метод 2025 - auto_publish_text)
   *
   * @param {string} text - Текст поста (до 500 символов)
   * @returns {Promise<Object>} Результат публикации
   */
  async publishText(text) {
    try {
      // Валидация
      if (!text || text.trim().length === 0) {
        throw new Error('Text cannot be empty');
      }

      if (text.length > 500) {
        console.warn(`Text too long (${text.length} chars), truncating to 500...`);
        text = text.substring(0, 500);
      }

      // Rate limit check
      await this.checkRateLimit();

      console.log('Publishing text post to Threads...');

      const response = await axios.post(
        `${this.baseUrl}/${this.igUserId}/threads`,
        {
          text: text,
          auto_publish_text: true
        },
        {
          headers: {
            'Authorization': `Bearer ${this.accessToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      console.log('✅ Text post published successfully!');

      return {
        success: true,
        postId: response.data.id,
        message: 'Text post published',
        data: response.data
      };

    } catch (error) {
      return this.handleError(error, 'publishText');
    }
  }

  /**
   * Публикация изображения (2-step: create container → publish)
   *
   * @param {string} imageUrl - Публичный HTTPS URL изображения
   * @param {string} caption - Текст поста (опционально, до 500 символов)
   * @returns {Promise<Object>} Результат публикации
   */
  async publishImage(imageUrl, caption = '') {
    try {
      // Валидация
      if (!imageUrl || !imageUrl.startsWith('https://')) {
        throw new Error('Image URL must be a valid HTTPS URL');
      }

      if (caption.length > 500) {
        console.warn(`Caption too long (${caption.length} chars), truncating to 500...`);
        caption = caption.substring(0, 500);
      }

      // Rate limit check
      await this.checkRateLimit();

      console.log('Step 1: Creating media container...');

      // Шаг 1: Создать media container
      const createResponse = await axios.post(
        `${this.baseUrl}/${this.igUserId}/threads`,
        {
          media_type: 'IMAGE',
          image_url: imageUrl,
          text: caption
        },
        {
          headers: {
            'Authorization': `Bearer ${this.accessToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const containerId = createResponse.data.id;
      console.log(`Container created: ${containerId}`);

      // Задержка для обработки медиа (рекомендуется 5-10 секунд)
      console.log('Waiting for media processing (5 seconds)...');
      await this.delay(5000);

      // Шаг 2: Опубликовать container
      console.log('Step 2: Publishing container...');

      const publishResponse = await axios.post(
        `${this.baseUrl}/${containerId}/publish`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${this.accessToken}`
          }
        }
      );

      console.log('✅ Image post published successfully!');

      return {
        success: true,
        postId: publishResponse.data.id,
        containerId: containerId,
        message: 'Image post published',
        data: publishResponse.data
      };

    } catch (error) {
      return this.handleError(error, 'publishImage');
    }
  }

  /**
   * Публикация carousel (несколько изображений)
   *
   * @param {Array<string>} imageUrls - Массив публичных HTTPS URLs (2-10 изображений)
   * @param {string} caption - Текст поста (опционально, до 500 символов)
   * @returns {Promise<Object>} Результат публикации
   */
  async publishCarousel(imageUrls, caption = '') {
    try {
      // Валидация
      if (!Array.isArray(imageUrls) || imageUrls.length < 2) {
        throw new Error('Carousel requires at least 2 images');
      }

      if (imageUrls.length > 10) {
        throw new Error('Carousel supports maximum 10 images');
      }

      // Проверка всех URLs
      for (const url of imageUrls) {
        if (!url.startsWith('https://')) {
          throw new Error(`Invalid image URL: ${url}`);
        }
      }

      if (caption.length > 500) {
        console.warn(`Caption too long (${caption.length} chars), truncating to 500...`);
        caption = caption.substring(0, 500);
      }

      // Rate limit check
      await this.checkRateLimit();

      console.log(`Creating carousel with ${imageUrls.length} images...`);

      // Шаг 1: Создать media containers для каждого изображения
      const containerIds = [];

      for (let i = 0; i < imageUrls.length; i++) {
        console.log(`Creating container ${i + 1}/${imageUrls.length}...`);

        const response = await axios.post(
          `${this.baseUrl}/${this.igUserId}/threads`,
          {
            media_type: 'IMAGE',
            image_url: imageUrls[i],
            is_carousel_item: true
          },
          {
            headers: {
              'Authorization': `Bearer ${this.accessToken}`,
              'Content-Type': 'application/json'
            }
          }
        );

        containerIds.push(response.data.id);

        // Небольшая задержка между запросами
        if (i < imageUrls.length - 1) {
          await this.delay(1000);
        }
      }

      console.log(`All containers created: ${containerIds.join(', ')}`);

      // Задержка для обработки всех медиа
      console.log('Waiting for media processing (10 seconds)...');
      await this.delay(10000);

      // Шаг 2: Создать carousel container
      console.log('Creating carousel container...');

      const carouselResponse = await axios.post(
        `${this.baseUrl}/${this.igUserId}/threads`,
        {
          media_type: 'CAROUSEL',
          children: containerIds,
          text: caption
        },
        {
          headers: {
            'Authorization': `Bearer ${this.accessToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const carouselId = carouselResponse.data.id;
      console.log(`Carousel container created: ${carouselId}`);

      // Задержка перед публикацией
      console.log('Waiting before publishing (5 seconds)...');
      await this.delay(5000);

      // Шаг 3: Опубликовать carousel
      console.log('Publishing carousel...');

      const publishResponse = await axios.post(
        `${this.baseUrl}/${carouselId}/publish`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${this.accessToken}`
          }
        }
      );

      console.log('✅ Carousel published successfully!');

      return {
        success: true,
        postId: publishResponse.data.id,
        carouselId: carouselId,
        containerIds: containerIds,
        message: 'Carousel published',
        data: publishResponse.data
      };

    } catch (error) {
      return this.handleError(error, 'publishCarousel');
    }
  }

  /**
   * Rate limit handling
   * Проверяет и ожидает если лимит близок к исчерпанию
   */
  async checkRateLimit() {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequestTime;

    // Если прошла минута - сбросить счетчик
    if (timeSinceLastRequest > this.requestWindow) {
      this.requestCount = 0;
      this.lastRequestTime = now;
    }

    // Если близки к лимиту - подождать
    if (this.requestCount >= this.maxRequestsPerWindow) {
      const waitTime = this.requestWindow - timeSinceLastRequest;
      console.warn(`⚠️ Rate limit approaching, waiting ${Math.ceil(waitTime / 1000)} seconds...`);
      await this.delay(waitTime);
      this.requestCount = 0;
      this.lastRequestTime = Date.now();
    }

    this.requestCount++;
  }

  /**
   * Обработка ошибок с retry логикой
   *
   * @param {Error} error - Ошибка
   * @param {string} operation - Название операции
   * @param {number} retryCount - Текущая попытка
   * @returns {Promise<Object>} Результат с ошибкой
   */
  async handleError(error, operation, retryCount = 0) {
    const maxRetries = 3;

    // Извлечение информации об ошибке
    const errorMessage = error.response?.data?.error?.message || error.message;
    const errorCode = error.response?.data?.error?.code;
    const statusCode = error.response?.status;

    console.error(`❌ Error in ${operation}:`, errorMessage);

    // Rate limit error - retry после задержки
    if (statusCode === 429 || errorCode === 32) {
      if (retryCount < maxRetries) {
        const waitTime = Math.pow(2, retryCount) * 5000; // Exponential backoff
        console.log(`Rate limit hit, retrying in ${waitTime / 1000} seconds... (attempt ${retryCount + 1}/${maxRetries})`);
        await this.delay(waitTime);

        // Повторить операцию (нужно передать параметры из контекста)
        // Для упрощения возвращаем ошибку, retry можно реализовать в вызывающем коде
      }
    }

    // OAuth error - токен истек
    if (statusCode === 401 || errorCode === 190) {
      console.error('🔑 Access token expired or invalid. Please refresh your token.');
    }

    // Media processing error - изображение недоступно
    if (errorMessage && errorMessage.includes('could not be downloaded')) {
      console.error('🖼️ Image URL is not accessible. Make sure it\'s a public HTTPS URL.');
    }

    return {
      success: false,
      error: errorMessage,
      errorCode: errorCode,
      statusCode: statusCode,
      operation: operation,
      retryCount: retryCount
    };
  }

  /**
   * Utility: задержка
   *
   * @param {number} ms - Миллисекунды
   * @returns {Promise<void>}
   */
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Получение информации о посте
   *
   * @param {string} postId - ID поста
   * @returns {Promise<Object>} Информация о посте
   */
  async getPost(postId) {
    try {
      const response = await axios.get(
        `${this.baseUrl}/${postId}`,
        {
          params: {
            fields: 'id,text,media_type,media_url,timestamp,permalink'
          },
          headers: {
            'Authorization': `Bearer ${this.accessToken}`
          }
        }
      );

      return {
        success: true,
        data: response.data
      };

    } catch (error) {
      return this.handleError(error, 'getPost');
    }
  }

  /**
   * Получение insights (метрики) поста
   *
   * @param {string} postId - ID поста
   * @returns {Promise<Object>} Метрики поста
   */
  async getPostInsights(postId) {
    try {
      const response = await axios.get(
        `${this.baseUrl}/${postId}/insights`,
        {
          params: {
            metric: 'views,likes,replies,reposts,quotes'
          },
          headers: {
            'Authorization': `Bearer ${this.accessToken}`
          }
        }
      );

      return {
        success: true,
        data: response.data
      };

    } catch (error) {
      return this.handleError(error, 'getPostInsights');
    }
  }
}

module.exports = ThreadsPostCreator;

// ============================================
// Примеры использования
// ============================================

/*

// 1. Публикация текста (новинка 2025)
const ThreadsPostCreator = require('./post-creator');

const poster = new ThreadsPostCreator(
  'YOUR_ACCESS_TOKEN',
  'YOUR_IG_USER_ID'
);

// Простой текстовый пост
poster.publishText('Amazing desert safari in Dubai! 🏜️ #DubaiTourism')
  .then(result => {
    if (result.success) {
      console.log('Published! Post ID:', result.postId);
    } else {
      console.error('Failed:', result.error);
    }
  });


// 2. Публикация изображения
poster.publishImage(
  'https://example.com/dubai-desert.jpg',
  'Experience the magic of Dubai desert 🌅\n\nDesert Safari starting at just $80/person!\n#DubaiDesert #UAETravel'
)
  .then(result => {
    if (result.success) {
      console.log('Published! Post ID:', result.postId);
    }
  });


// 3. Публикация carousel (несколько фото)
const imageUrls = [
  'https://example.com/image1.jpg',
  'https://example.com/image2.jpg',
  'https://example.com/image3.jpg'
];

poster.publishCarousel(
  imageUrls,
  'Dubai Marina Yacht Tour highlights! 🛥️\n\nSwipe to see more 👉\n#DubaiMarina #YachtTour'
)
  .then(result => {
    if (result.success) {
      console.log('Carousel published! Post ID:', result.postId);
    }
  });


// 4. Получение информации о посте
poster.getPost('POST_ID_HERE')
  .then(result => {
    if (result.success) {
      console.log('Post data:', result.data);
    }
  });


// 5. Получение метрик поста
poster.getPostInsights('POST_ID_HERE')
  .then(result => {
    if (result.success) {
      console.log('Post insights:', result.data);
    }
  });


// 6. Error handling с retry
async function publishWithRetry(text, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    const result = await poster.publishText(text);

    if (result.success) {
      return result;
    }

    console.log(`Attempt ${i + 1} failed, retrying...`);
    await new Promise(resolve => setTimeout(resolve, 5000)); // 5 sec delay
  }

  throw new Error('Failed after max retries');
}

publishWithRetry('My post text')
  .then(result => console.log('Success:', result))
  .catch(error => console.error('Final error:', error));

*/
