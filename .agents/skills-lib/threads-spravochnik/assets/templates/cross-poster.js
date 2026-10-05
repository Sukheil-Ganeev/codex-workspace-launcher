// Cross-posting для Instagram + Threads
// Публикует контент одновременно на обе платформы
// Автор: Claude Code Agent
// Дата: 05 февраля 2026

const axios = require('axios');

/**
 * CrossPoster - класс для кросс-постинга в Instagram + Threads
 *
 * Возможности:
 * - Одновременная публикация на обе платформы
 * - Адаптация контента для каждой платформы
 * - Instagram: визуал + короткий caption + много хештегов
 * - Threads: детальное описание + меньше хештегов
 * - Error handling с retry логикой
 * - Параллельная публикация для скорости
 */
class CrossPoster {
  /**
   * @param {string} accessToken - Instagram/Threads access token (единый)
   * @param {string} igUserId - Instagram User ID
   */
  constructor(accessToken, igUserId) {
    this.accessToken = accessToken;
    this.igUserId = igUserId;
    this.instagramBaseUrl = 'https://graph.facebook.com/v18.0';
    this.threadsBaseUrl = 'https://graph.threads.net/v1.0';
  }

  /**
   * Форматирование caption для Instagram
   *
   * @param {string} text - Исходный текст
   * @param {Array<string>} hashtags - Массив хештегов
   * @returns {string} Отформатированный caption
   */
  formatCaptionForInstagram(text, hashtags = []) {
    // Instagram любит короткие captions
    let caption = text.length > 150 ? text.substring(0, 147) + '...' : text;

    // Добавление хештегов (5-10 оптимально)
    if (hashtags && hashtags.length > 0) {
      const selectedHashtags = hashtags.slice(0, 10);
      caption += '\n\n' + selectedHashtags.map(tag => `#${tag.replace('#', '')}`).join(' ');
    }

    // Лимит Instagram: 2200 символов
    return caption.slice(0, 2200);
  }

  /**
   * Форматирование текста для Threads
   *
   * @param {string} title - Заголовок
   * @param {string} description - Детальное описание
   * @param {Array<string>} hashtags - Массив хештегов
   * @returns {string} Отформатированный текст
   */
  formatTextForThreads(title, description, hashtags = []) {
    // Threads позволяет более длинные тексты, но с лимитом 500 символов
    let text = title;

    if (description) {
      text += '\n\n' + description;
    }

    // Меньше хештегов для Threads (3-5 оптимально)
    if (hashtags && hashtags.length > 0) {
      const selectedHashtags = hashtags.slice(0, 5);
      text += '\n\n' + selectedHashtags.map(tag => `#${tag.replace('#', '')}`).join(' ');
    }

    // Лимит Threads: 500 символов
    if (text.length > 500) {
      // Умная обрезка: сохраняем заголовок + начало описания + хештеги
      const hashtagsPart = hashtags.slice(0, 5).map(tag => `#${tag.replace('#', '')}`).join(' ');
      const availableLength = 500 - title.length - hashtagsPart.length - 10; // 10 для переносов строк

      if (availableLength > 50) {
        const truncatedDescription = description.substring(0, availableLength - 3) + '...';
        text = `${title}\n\n${truncatedDescription}\n\n${hashtagsPart}`;
      } else {
        // Если не хватает места - только заголовок + хештеги
        text = `${title}\n\n${hashtagsPart}`;
      }
    }

    return text.slice(0, 500);
  }

  /**
   * Публикация в Instagram (2-step process)
   *
   * @param {string} imageUrl - URL изображения
   * @param {string} caption - Caption
   * @returns {Promise<Object>} Результат публикации
   */
  async publishToInstagram(imageUrl, caption) {
    try {
      console.log('📸 Publishing to Instagram...');

      // Шаг 1: Создать media container
      const createResponse = await axios.post(
        `${this.instagramBaseUrl}/${this.igUserId}/media`,
        {
          image_url: imageUrl,
          caption: caption
        },
        {
          headers: {
            'Authorization': `Bearer ${this.accessToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const creationId = createResponse.data.id;
      console.log(`Instagram container created: ${creationId}`);

      // Задержка для обработки медиа
      await this.delay(5000);

      // Шаг 2: Опубликовать
      const publishResponse = await axios.post(
        `${this.instagramBaseUrl}/${this.igUserId}/media_publish`,
        {
          creation_id: creationId
        },
        {
          headers: {
            'Authorization': `Bearer ${this.accessToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      console.log('✅ Instagram post published!');

      return {
        success: true,
        platform: 'instagram',
        postId: publishResponse.data.id,
        creationId: creationId
      };

    } catch (error) {
      console.error('❌ Instagram publishing error:', error.response?.data || error.message);
      return {
        success: false,
        platform: 'instagram',
        error: error.response?.data?.error?.message || error.message
      };
    }
  }

  /**
   * Публикация в Threads
   *
   * @param {string} text - Текст поста
   * @param {string} imageUrl - URL изображения (опционально)
   * @returns {Promise<Object>} Результат публикации
   */
  async publishToThreads(text, imageUrl = null) {
    try {
      console.log('🧵 Publishing to Threads...');

      if (imageUrl) {
        // С изображением: 2-step process
        const createResponse = await axios.post(
          `${this.threadsBaseUrl}/${this.igUserId}/threads`,
          {
            media_type: 'IMAGE',
            image_url: imageUrl,
            text: text
          },
          {
            headers: {
              'Authorization': `Bearer ${this.accessToken}`,
              'Content-Type': 'application/json'
            }
          }
        );

        const threadId = createResponse.data.id;
        console.log(`Threads container created: ${threadId}`);

        await this.delay(5000);

        const publishResponse = await axios.post(
          `${this.threadsBaseUrl}/${threadId}/publish`,
          {},
          {
            headers: {
              'Authorization': `Bearer ${this.accessToken}`
            }
          }
        );

        console.log('✅ Threads post published!');

        return {
          success: true,
          platform: 'threads',
          postId: publishResponse.data.id,
          threadId: threadId
        };

      } else {
        // Только текст: auto_publish_text (новинка 2025)
        const response = await axios.post(
          `${this.threadsBaseUrl}/${this.igUserId}/threads`,
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

        console.log('✅ Threads post published!');

        return {
          success: true,
          platform: 'threads',
          postId: response.data.id
        };
      }

    } catch (error) {
      console.error('❌ Threads publishing error:', error.response?.data || error.message);
      return {
        success: false,
        platform: 'threads',
        error: error.response?.data?.error?.message || error.message
      };
    }
  }

  /**
   * Главная функция: публикация на обе платформы одновременно
   *
   * @param {Object} content - Контент для публикации
   * @param {string} content.title - Заголовок
   * @param {string} content.description - Детальное описание
   * @param {string} content.imageUrl - URL изображения
   * @param {Array<string>} content.hashtags - Массив хештегов
   * @returns {Promise<Object>} Результаты публикации
   */
  async crossPost(content) {
    console.log('\n🚀 Starting cross-posting to Instagram + Threads...\n');

    // Валидация
    if (!content.imageUrl) {
      throw new Error('Image URL is required for cross-posting');
    }

    if (!content.title) {
      throw new Error('Title is required');
    }

    // Адаптация контента для каждой платформы
    const instagramCaption = this.formatCaptionForInstagram(
      content.title,
      content.hashtags
    );

    const threadsText = this.formatTextForThreads(
      content.title,
      content.description || '',
      content.hashtags
    );

    console.log('📝 Content adapted for both platforms');
    console.log(`Instagram caption: ${instagramCaption.length} chars`);
    console.log(`Threads text: ${threadsText.length} chars\n`);

    // Параллельная публикация на обе платформы для скорости
    const results = await Promise.allSettled([
      this.publishToInstagram(content.imageUrl, instagramCaption),
      this.publishToThreads(threadsText, content.imageUrl)
    ]);

    // Обработка результатов
    const summary = {
      instagram: results[0].status === 'fulfilled' ? results[0].value : {
        success: false,
        platform: 'instagram',
        error: results[0].reason
      },
      threads: results[1].status === 'fulfilled' ? results[1].value : {
        success: false,
        platform: 'threads',
        error: results[1].reason
      }
    };

    // Итоговый статус
    const successCount = [summary.instagram.success, summary.threads.success].filter(Boolean).length;

    console.log('\n📊 Cross-posting Results:');
    console.log(`✅ Instagram: ${summary.instagram.success ? 'Published' : 'Failed'}`);
    console.log(`✅ Threads: ${summary.threads.success ? 'Published' : 'Failed'}`);
    console.log(`\n🎯 Success rate: ${successCount}/2 platforms\n`);

    return summary;
  }

  /**
   * Публикация только текста в Threads (без Instagram)
   *
   * @param {Object} content - Контент
   * @returns {Promise<Object>} Результат
   */
  async postTextOnly(content) {
    console.log('🧵 Posting text-only to Threads...\n');

    const threadsText = this.formatTextForThreads(
      content.title,
      content.description || '',
      content.hashtags
    );

    return await this.publishToThreads(threadsText, null);
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
}

module.exports = CrossPoster;

// ============================================
// Примеры использования
// ============================================

/*

// 1. Базовый кросс-постинг
const CrossPoster = require('./cross-poster');

const poster = new CrossPoster(
  'YOUR_ACCESS_TOKEN',
  'YOUR_IG_USER_ID'
);

const content = {
  title: 'Experience Dubai Desert Safari 🏜️',
  description: `Just wrapped up an amazing desert safari tour!

What's included:
✅ Dune bashing (30-40 min)
✅ Camel riding
✅ BBQ dinner under the stars
✅ Traditional dance shows

Price: $80/person (all-inclusive)
Pickup from any Dubai hotel

Perfect for families and adventure seekers!`,
  imageUrl: 'https://example.com/desert-safari.jpg',
  hashtags: ['DubaiDesert', 'DesertSafari', 'DubaiTourism', 'UAETravel', 'VisitDubai', 'DubaiLife']
};

poster.crossPost(content)
  .then(results => {
    console.log('Instagram:', results.instagram.success ? 'Success' : 'Failed');
    console.log('Threads:', results.threads.success ? 'Success' : 'Failed');
  })
  .catch(error => {
    console.error('Cross-posting error:', error);
  });


// 2. Публикация только в Threads (текст без изображения)
const textContent = {
  title: 'Top 5 Tips for First-Time Visitors to Dubai',
  description: `Planning your first trip to Dubai? Here are my top tips:

1. Best time to visit: November to March (cooler weather)
2. Dress code: Modest clothing for mosques and malls
3. Transportation: Metro is fast and cheap
4. Currency: AED, but USD widely accepted
5. Don't miss: Desert safari and Burj Khalifa at sunset!

Questions? Ask away!`,
  hashtags: ['DubaiTips', 'DubaiTravel', 'UAEGuide']
};

poster.postTextOnly(textContent)
  .then(result => {
    if (result.success) {
      console.log('Posted to Threads:', result.postId);
    }
  });


// 3. Пример для туристического бизнеса (акция)
const promoContent = {
  title: '🔥 Flash Sale: 20% OFF Desert Safari!',
  description: `24-hour flash sale on our most popular tour!

Regular price: $80/person
TODAY ONLY: $64/person

Includes:
✅ Hotel pickup & drop-off
✅ Dune bashing
✅ Camel riding
✅ Sandboarding
✅ BBQ dinner
✅ Live shows

Book now! Offer ends tonight at midnight.
DM us or click link in bio.`,
  imageUrl: 'https://example.com/desert-safari-promo.jpg',
  hashtags: ['DubaiDeals', 'DesertSafari', 'FlashSale', 'DubaiTourism', 'UAETravel']
};

poster.crossPost(promoContent)
  .then(results => {
    // Уведомление в Telegram команде
    if (results.instagram.success && results.threads.success) {
      console.log('✅ Promo posted successfully on both platforms!');
      // sendTelegramNotification('Promo live on Instagram + Threads');
    }
  });


// 4. Серия постов (контент-план на неделю)
const weeklyContent = [
  {
    day: 'Monday',
    title: 'Start your week with adventure! 🏜️',
    description: 'Desert safari tours available daily...',
    imageUrl: 'https://example.com/monday.jpg',
    hashtags: ['MondayMotivation', 'DubaiDesert']
  },
  {
    day: 'Wednesday',
    title: 'Dubai Marina by night 🌃',
    description: 'Yacht tours every evening...',
    imageUrl: 'https://example.com/wednesday.jpg',
    hashtags: ['DubaiMarina', 'YachtLife']
  },
  // ... остальные дни недели
];

async function postWeeklyContent() {
  for (const content of weeklyContent) {
    console.log(`\nPosting ${content.day} content...`);
    await poster.crossPost(content);
    await new Promise(resolve => setTimeout(resolve, 60000)); // 1 минута между постами
  }
}

// postWeeklyContent();


// 5. Error handling с retry логикой
async function crossPostWithRetry(content, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    const results = await poster.crossPost(content);

    const instagramSuccess = results.instagram.success;
    const threadsSuccess = results.threads.success;

    // Если обе платформы успешны - готово
    if (instagramSuccess && threadsSuccess) {
      return results;
    }

    // Retry только неудавшихся платформ
    console.log(`\nAttempt ${i + 1} - Retrying failed platforms...`);

    if (!instagramSuccess) {
      console.log('Retrying Instagram...');
      const igCaption = poster.formatCaptionForInstagram(content.title, content.hashtags);
      results.instagram = await poster.publishToInstagram(content.imageUrl, igCaption);
    }

    if (!threadsSuccess) {
      console.log('Retrying Threads...');
      const threadsText = poster.formatTextForThreads(
        content.title,
        content.description,
        content.hashtags
      );
      results.threads = await poster.publishToThreads(threadsText, content.imageUrl);
    }

    // Задержка перед следующей попыткой
    if (i < maxRetries - 1) {
      await new Promise(resolve => setTimeout(resolve, 10000)); // 10 секунд
    }
  }

  throw new Error('Failed to cross-post after max retries');
}


// 6. Интеграция с планировщиком (cron)
const cron = require('node-cron');

// Ежедневная публикация в 14:00 (оптимальное время для ОАЭ)
cron.schedule('0 14 * * *', async () => {
  const dailyContent = {
    title: 'Good afternoon Dubai! ☀️',
    description: 'Check out our daily tour specials...',
    imageUrl: 'https://example.com/daily.jpg',
    hashtags: ['DubaiTourism', 'DailyDeals']
  };

  try {
    const results = await poster.crossPost(dailyContent);
    console.log('Daily post published:', results);
  } catch (error) {
    console.error('Daily post failed:', error);
    // Уведомить команду
  }
});


// 7. Webhook триггер (от формы бронирования)
const express = require('express');
const app = express();

app.post('/webhook/booking-confirmed', async (req, res) => {
  const booking = req.body;

  const confirmationPost = {
    title: '🎉 New booking just confirmed!',
    description: `Tour: ${booking.tour}
Customer: ${booking.customer_name}
Date: ${booking.date}

We're excited to host you!
Thank you for choosing us! ❤️`,
    imageUrl: booking.tour_image_url,
    hashtags: ['DubaiBooking', 'HappyCustomers', 'ThankYou']
  };

  try {
    await poster.crossPost(confirmationPost);
    res.json({ success: true, message: 'Posted to Instagram + Threads' });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.listen(3000, () => {
  console.log('Webhook server running on port 3000');
});

*/
