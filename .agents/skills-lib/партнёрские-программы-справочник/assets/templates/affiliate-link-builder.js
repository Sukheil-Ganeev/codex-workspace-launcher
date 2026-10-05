/**
 * Affiliate Link Builder
 * Генератор партнёрских ссылок с UTM метками
 */

class AffiliateLinkBuilder {
  constructor(config) {
    this.affiliateIds = config.affiliateIds || {};
  }

  /**
   * Построить партнёрскую ссылку Booking.com
   * @param {string} hotelId - ID отеля
   * @param {object} utm - UTM параметры
   * @returns {string}
   */
  buildBookingLink(hotelId, utm = {}) {
    const affiliateId = this.affiliateIds.booking;
    const baseUrl = 'https://www.booking.com/hotel';

    const params = new URLSearchParams({
      aid: affiliateId,
      utm_source: utm.source || 'telegram',
      utm_medium: utm.medium || 'post',
      utm_campaign: utm.campaign || 'default',
      utm_content: utm.content || hotelId
    });

    return `${baseUrl}/${hotelId}.html?${params.toString()}`;
  }

  /**
   * Построить партнёрскую ссылку Aviasales
   * @param {object} utm - UTM параметры
   * @returns {string}
   */
  buildAviasalesLink(utm = {}) {
    const marker = this.affiliateIds.aviasales;
    const baseUrl = 'https://www.aviasales.ru';

    const params = new URLSearchParams({
      marker: marker,
      utm_source: utm.source || 'telegram',
      utm_medium: utm.medium || 'post',
      utm_campaign: utm.campaign || 'default'
    });

    return `${baseUrl}?${params.toString()}`;
  }

  /**
   * Построить партнёрскую ссылку GetYourGuide
   * @param {string} activityId - ID активности
   * @param {object} utm - UTM параметры
   * @returns {string}
   */
  buildGetYourGuideLink(activityId, utm = {}) {
    const partnerId = this.affiliateIds.getyourguide;
    const baseUrl = `https://www.getyourguide.com/activity`;

    const params = new URLSearchParams({
      partner_id: partnerId,
      utm_source: utm.source || 'telegram',
      utm_medium: utm.medium || 'post',
      utm_campaign: utm.campaign || 'default',
      utm_content: utm.content || activityId
    });

    return `${baseUrl}/${activityId}?${params.toString()}`;
  }

  /**
   * Сократить ссылку через Bitly
   * @param {string} longUrl - Длинная ссылка
   * @returns {Promise<string>}
   */
  async shortenWithBitly(longUrl) {
    const bitlyToken = this.affiliateIds.bitly;

    const response = await fetch('https://api-ssl.bitly.com/v4/shorten', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${bitlyToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ long_url: longUrl })
    });

    const data = await response.json();
    return data.link;
  }

  /**
   * Генерировать несколько ссылок для кампании
   * @param {string} campaign - Название кампании
   * @returns {object}
   */
  generateCampaignLinks(campaign) {
    const links = {};

    // Booking: Atlantis The Palm
    links.atlantis = this.buildBookingLink('ae-atlantis-the-palm', {
      source: 'telegram',
      medium: 'post',
      campaign: campaign,
      content: 'atlantis_hotel'
    });

    // GetYourGuide: Desert Safari
    links.desertSafari = this.buildGetYourGuideLink('dubai-desert-safari-123', {
      source: 'telegram',
      medium: 'post',
      campaign: campaign,
      content: 'desert_safari'
    });

    // Aviasales
    links.flights = this.buildAviasalesLink({
      source: 'telegram',
      medium: 'post',
      campaign: campaign
    });

    return links;
  }
}

// Пример использования:

const builder = new AffiliateLinkBuilder({
  affiliateIds: {
    booking: '123456',           // Ваш Booking affiliate ID
    aviasales: 'YOUR_MARKER',    // Ваш Aviasales marker
    getyourguide: 'YOUR_PARTNER_ID', // Ваш GetYourGuide partner ID
    bitly: 'YOUR_BITLY_TOKEN'    // Ваш Bitly токен
  }
});

// Генерация ссылки Booking
const hotelLink = builder.buildBookingLink('ae-atlantis-the-palm', {
  source: 'telegram',
  medium: 'post',
  campaign: 'dubai_march_2026',
  content: 'atlantis_review'
});

console.log('Hotel Link:', hotelLink);

// Генерация всех ссылок для кампании
const campaignLinks = builder.generateCampaignLinks('dubai_march_2026');
console.log('Campaign Links:', campaignLinks);

// Сократить ссылку
(async () => {
  const shortLink = await builder.shortenWithBitly(hotelLink);
  console.log('Short Link:', shortLink);
})();

// Экспорт для Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = AffiliateLinkBuilder;
}
