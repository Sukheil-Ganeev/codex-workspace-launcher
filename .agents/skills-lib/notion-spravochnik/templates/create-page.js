/**
 * Создание страницы (записи) в базе данных Notion с блоками контента.
 * Пример: создание нового бронирования с описанием.
 * 
 * Требования:
 *   npm install @notionhq/client
 *   Переменные окружения: NOTION_TOKEN, NOTION_BOOKINGS_DB
 * 
 * Использование:
 *   NOTION_TOKEN=ntn_*** NOTION_BOOKINGS_DB=abc123 node create-page.js
 */

const { Client } = require("@notionhq/client");

const notion = new Client({ auth: process.env.NOTION_TOKEN });
const BOOKINGS_DB = process.env.NOTION_BOOKINGS_DB;

async function createBooking({
  name,
  date,
  pax,
  priceAed,
  costPrice,
  category,
  currency = "AED",
  paymentMethod = "Cash AED",
  phone,
  pickup,
}) {
  const page = await notion.pages.create({
    parent: { database_id: BOOKINGS_DB },
    icon: { type: "emoji", emoji: "🎫" },
    properties: {
      "Booking Name": {
        title: [{ text: { content: name } }],
      },
      "Date": {
        date: { start: date },
      },
      "Pax": {
        number: pax,
      },
      "Price AED": {
        number: priceAed,
      },
      "Cost Price": {
        number: costPrice,
      },
      "Category": {
        select: { name: category },
      },
      "Client Currency": {
        select: { name: currency },
      },
      "Payment Method": {
        select: { name: paymentMethod },
      },
      "Status": {
        select: { name: "Confirmed" },
      },
      ...(phone && { "Phone": { phone_number: phone } }),
      ...(pickup && {
        "Pickup Location": {
          rich_text: [{ text: { content: pickup } }],
        },
      }),
    },
    // Контент страницы (блоки)
    children: [
      {
        heading_2: {
          rich_text: [{ text: { content: "Детали бронирования" } }],
        },
      },
      {
        paragraph: {
          rich_text: [
            { text: { content: `Экскурсия: ${name}` } },
          ],
        },
      },
      {
        paragraph: {
          rich_text: [
            { text: { content: `Дата: ${date} | Гостей: ${pax}` } },
          ],
        },
      },
      {
        paragraph: {
          rich_text: [
            { text: { content: `Цена: ${priceAed} AED | Себестоимость: ${costPrice} AED | Прибыль: ${priceAed - costPrice} AED` } },
          ],
        },
      },
      {
        divider: {},
      },
      {
        heading_3: {
          rich_text: [{ text: { content: "Чек-лист" } }],
        },
      },
      {
        to_do: {
          rich_text: [{ text: { content: "Подтвердить бронь у поставщика" } }],
          checked: false,
        },
      },
      {
        to_do: {
          rich_text: [{ text: { content: "Отправить подтверждение клиенту" } }],
          checked: false,
        },
      },
      {
        to_do: {
          rich_text: [{ text: { content: "Получить оплату" } }],
          checked: false,
        },
      },
      {
        to_do: {
          rich_text: [{ text: { content: "Отправить напоминание за день" } }],
          checked: false,
        },
      },
      {
        divider: {},
      },
      {
        callout: {
          rich_text: [
            { text: { content: "Pickup: " } },
            { text: { content: pickup || "Уточнить у клиента" }, annotations: { bold: true } },
          ],
          icon: { type: "emoji", emoji: "📍" },
        },
      },
    ],
  });

  console.log("Booking created:", page.id);
  console.log("URL:", page.url);
  return page;
}

// Пример использования
createBooking({
  name: "Desert Safari Premium",
  date: "2026-02-20",
  pax: 4,
  priceAed: 1200,
  costPrice: 800,
  category: "Excursion",
  currency: "USD",
  paymentMethod: "Cash USD",
  phone: "+971501234567",
  pickup: "JBR Hilton Hotel, lobby, 14:30",
}).catch(console.error);
