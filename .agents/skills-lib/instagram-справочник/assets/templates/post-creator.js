// Instagram Post Creator Helper
// Node.js helper для создания постов через Instagram Graph API
// Версия: 1.0 (2026-02-05)

const axios = require('axios');
require('dotenv').config();

class InstagramPostCreator {
  constructor() {
    this.baseURL = 'https://graph.facebook.com/v18.0';
    this.token = process.env.INSTAGRAM_ACCESS_TOKEN;
    this.accountId = process.env.INSTAGRAM_ACCOUNT_ID;
  }

  /**
   * Публикация фото
   * @param {string} imageUrl - URL изображения (публично доступный)
   * @param {string} caption - Описание поста
   * @returns {Promise<Object>} - Результат публикации
   */
  async postPhoto(imageUrl, caption) {
    try {
      // Шаг 1: Создание медиа-контейнера
      const containerResponse = await axios.post(
        `${this.baseURL}/${this.accountId}/media`,
        {
          image_url: imageUrl,
          caption: caption,
          access_token: this.token
        }
      );

      const creationId = containerResponse.data.id;
      console.log(`Медиа-контейнер создан: ${creationId}`);

      // Небольшая пауза перед публикацией
      await this.sleep(2000);

      // Шаг 2: Публикация
      const publishResponse = await axios.post(
        `${this.baseURL}/${this.accountId}/media_publish`,
        {
          creation_id: creationId,
          access_token: this.token
        }
      );

      const postId = publishResponse.data.id;
      console.log(`Пост опубликован: ${postId}`);

      return {
        success: true,
        postId: postId,
        message: 'Пост успешно опубликован'
      };

    } catch (error) {
      console.error('Ошибка при публикации:', error.response?.data || error.message);
      return {
        success: false,
        error: error.response?.data || error.message
      };
    }
  }

  /**
   * Публикация карусели (несколько фото)
   * @param {Array<string>} imageUrls - Массив URL изображений
   * @param {string} caption - Описание карусели
   * @returns {Promise<Object>}
   */
  async postCarousel(imageUrls, caption) {
    try {
      // Шаг 1: Создание медиа-контейнеров для каждого изображения
      const mediaIds = [];

      for (const imageUrl of imageUrls) {
        const response = await axios.post(
          `${this.baseURL}/${this.accountId}/media`,
          {
            image_url: imageUrl,
            is_carousel_item: true,
            access_token: this.token
          }
        );
        mediaIds.push(response.data.id);
        await this.sleep(1000); // Пауза между запросами
      }

      console.log(`Медиа-контейнеры созданы: ${mediaIds.join(', ')}`);

      // Шаг 2: Создание карусельного контейнера
      const carouselResponse = await axios.post(
        `${this.baseURL}/${this.accountId}/media`,
        {
          media_type: 'CAROUSEL',
          caption: caption,
          children: mediaIds.join(','),
          access_token: this.token
        }
      );

      const carouselId = carouselResponse.data.id;
      await this.sleep(2000);

      // Шаг 3: Публикация карусели
      const publishResponse = await axios.post(
        `${this.baseURL}/${this.accountId}/media_publish`,
        {
          creation_id: carouselId,
          access_token: this.token
        }
      );

      const postId = publishResponse.data.id;
      console.log(`Карусель опубликована: ${postId}`);

      return {
        success: true,
        postId: postId,
        message: 'Карусель успешно опубликована'
      };

    } catch (error) {
      console.error('Ошибка при публикации карусели:', error.response?.data || error.message);
      return {
        success: false,
        error: error.response?.data || error.message
      };
    }
  }

  /**
   * Вспомогательная функция для паузы
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Экспорт
module.exports = InstagramPostCreator;

// Пример использования:
/*
const InstagramPostCreator = require('./post-creator');

const poster = new InstagramPostCreator();

// Публикация одного фото
poster.postPhoto(
  'https://example.com/dubai_tour.jpg',
  'Невероятное пустынное сафари в Дубае! 🏜️🐪\n\n' +
  'Experience the thrill of desert adventure!\n\n' +
  '📞 Book: +971 50 123 4567\n' +
  '💰 AED 200/person\n\n' +
  '#DubaiTourism #DesertSafari #UAETravel #دبي'
).then(result => {
  console.log(result);
});

// Публикация карусели
poster.postCarousel(
  [
    'https://example.com/photo1.jpg',
    'https://example.com/photo2.jpg',
    'https://example.com/photo3.jpg'
  ],
  'Топ-3 достопримечательности Дубая! 🇦🇪\n\n' +
  'Swipe to see all highlights!\n\n' +
  '#Dubai #Tourism #BurjKhalifa #DubaiMall'
).then(result => {
  console.log(result);
});
*/
