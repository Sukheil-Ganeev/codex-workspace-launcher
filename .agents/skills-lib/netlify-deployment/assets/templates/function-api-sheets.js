// Serverless Function: Google Sheets API Integration
// Путь: netlify/functions/get-prices.js
// URL: https://your-site.netlify.app/.netlify/functions/get-prices

// ВАЖНО: Установите environment variables в Netlify:
// GOOGLE_API_KEY - API ключ Google
// SHEET_ID - ID Google таблицы

exports.handler = async (event, context) => {
  // CORS headers для браузерных запросов
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Content-Type': 'application/json'
  };

  // Обработка preflight запроса
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  // Проверка метода
  if (event.httpMethod !== 'GET') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method Not Allowed' })
    };
  }

  try {
    const apiKey = process.env.GOOGLE_API_KEY;
    const sheetId = process.env.SHEET_ID;

    // Параметры таблицы
    const range = 'Prices!A1:D100'; // Диапазон ячеек

    // URL Google Sheets API
    const url = `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/${range}?key=${apiKey}`;

    console.log('Запрос к Google Sheets...');

    // Запрос к API
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Google API error: ${response.statusText}`);
    }

    const data = await response.json();

    // Обработка данных (первая строка - заголовки)
    const rows = data.values;
    if (!rows || rows.length === 0) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          success: true,
          data: [],
          message: 'Нет данных в таблице'
        })
      };
    }

    // Преобразуем в массив объектов
    const headers_row = rows[0];
    const items = rows.slice(1).map(row => {
      const item = {};
      headers_row.forEach((header, index) => {
        item[header] = row[index] || '';
      });
      return item;
    });

    console.log(`Получено ${items.length} записей`);

    // Возвращаем данные
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        data: items,
        count: items.length,
        timestamp: new Date().toISOString()
      })
    };

  } catch (error) {
    console.error('Ошибка:', error);

    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        success: false,
        error: 'Internal Server Error',
        message: error.message
      })
    };
  }
};

// ============================================
// КАК НАСТРОИТЬ:
// ============================================

// 1. Создайте Google Sheet с прайс-листом
// 2. Сделайте таблицу публичной (File → Share → Anyone with link can view)
// 3. Получите Sheet ID из URL:
//    https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
// 4. Создайте API ключ в Google Cloud Console:
//    - Включите Google Sheets API
//    - Создайте credentials → API Key
// 5. Добавьте в Netlify Environment Variables:
//    GOOGLE_API_KEY=your_api_key
//    SHEET_ID=your_sheet_id

// ============================================
// ПРИМЕР ИСПОЛЬЗОВАНИЯ В КЛИЕНТЕ:
// ============================================

/*
async function loadPrices() {
  const response = await fetch('/.netlify/functions/get-prices');
  const result = await response.json();

  if (result.success) {
    console.log('Цены загружены:', result.data);
    // Отобразите данные на странице
  }
}
*/
