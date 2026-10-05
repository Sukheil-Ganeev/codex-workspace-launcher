/**
 * Создание базы данных Notion для CRM туристического бизнеса ОАЭ
 * 
 * Требования:
 *   npm install @notionhq/client
 *   Переменные окружения: NOTION_TOKEN, NOTION_PARENT_PAGE_ID
 * 
 * Использование:
 *   NOTION_TOKEN=ntn_*** NOTION_PARENT_PAGE_ID=abc123 node create-database.js
 */

const { Client } = require("@notionhq/client");

const notion = new Client({ auth: process.env.NOTION_TOKEN });
const parentPageId = process.env.NOTION_PARENT_PAGE_ID;

async function createBookingsDatabase() {
  const response = await notion.databases.create({
    parent: { type: "page_id", page_id: parentPageId },
    title: [{ type: "text", text: { content: "Bookings" } }],
    icon: { type: "emoji", emoji: "📋" },
    properties: {
      // Title (обязательное)
      "Booking Name": {
        title: {},
      },
      // Статус бронирования
      "Status": {
        select: {
          options: [
            { name: "Inquiry", color: "gray" },
            { name: "Confirmed", color: "blue" },
            { name: "Paid", color: "green" },
            { name: "Completed", color: "purple" },
            { name: "Cancelled", color: "red" },
          ],
        },
      },
      // Дата экскурсии/услуги
      "Date": {
        date: {},
      },
      // Количество гостей
      "Pax": {
        number: { format: "number" },
      },
      // Цена в AED
      "Price AED": {
        number: { format: "number" },
      },
      // Себестоимость
      "Cost Price": {
        number: { format: "number" },
      },
      // Прибыль (формула)
      "Profit": {
        formula: {
          expression: 'prop("Price AED") - prop("Cost Price")',
        },
      },
      // Валюта клиента
      "Client Currency": {
        select: {
          options: [
            { name: "AED", color: "green" },
            { name: "USD", color: "blue" },
            { name: "RUB", color: "red" },
            { name: "KZT", color: "yellow" },
            { name: "Crypto", color: "purple" },
          ],
        },
      },
      // Способ оплаты
      "Payment Method": {
        select: {
          options: [
            { name: "Cash AED", color: "green" },
            { name: "Cash USD", color: "blue" },
            { name: "Sber RUB", color: "red" },
            { name: "Kaspi KZT", color: "yellow" },
            { name: "Crypto", color: "purple" },
            { name: "Bank Transfer", color: "gray" },
          ],
        },
      },
      // Категория услуги
      "Category": {
        select: {
          options: [
            { name: "Excursion", color: "orange" },
            { name: "Park Ticket", color: "blue" },
            { name: "Yacht", color: "purple" },
            { name: "Car Rental", color: "green" },
            { name: "Transfer", color: "gray" },
            { name: "MVU", color: "yellow" },
          ],
        },
      },
      // Место подачи
      "Pickup Location": {
        rich_text: {},
      },
      // Телефон клиента
      "Phone": {
        phone_number: {},
      },
      // Ответственный
      "Agent": {
        people: {},
      },
    },
  });

  console.log("Database created:", response.id);
  console.log("URL:", response.url);
  return response;
}

createBookingsDatabase().catch(console.error);
