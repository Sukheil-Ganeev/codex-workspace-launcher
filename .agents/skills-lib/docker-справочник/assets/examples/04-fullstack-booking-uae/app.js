// =============================================================================
// app.js — Booking API для туризма ОАЭ
// Экскурсии, билеты в парки, бронирования | Валюта: AED
// =============================================================================

const express = require("express");
const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;
const CURRENCY = process.env.TOURS_CURRENCY || "AED";
const LANGUAGE = process.env.DEFAULT_LANGUAGE || "ru";

// --- Каталог туров (в production -- из PostgreSQL) ---
const tours = [
  {
    id: 1,
    name: "Desert Safari Premium",
    name_ru: "Джип-сафари Премиум",
    description_ru: "Дюны, барбекю, шоу танца живота, катание на верблюдах. Закат в пустыне.",
    price: 250,
    currency: CURRENCY,
    duration_hours: 6,
    emirate: "Dubai",
    category: "adventure",
    available: true,
  },
  {
    id: 2,
    name: "Dubai City Tour",
    name_ru: "Обзорная экскурсия по Дубаю",
    description_ru: "Бурдж-Халифа, Dubai Mall, Старый город, Рамка Дубая, мечеть Джумейра.",
    price: 180,
    currency: CURRENCY,
    duration_hours: 8,
    emirate: "Dubai",
    category: "sightseeing",
    available: true,
  },
  {
    id: 3,
    name: "Abu Dhabi Full Day",
    name_ru: "Абу-Даби полный день",
    description_ru: "Мечеть Шейха Зайда, Лувр Абу-Даби, набережная Корниш, дворец Каср Аль Ватан.",
    price: 220,
    currency: CURRENCY,
    duration_hours: 10,
    emirate: "Abu Dhabi",
    category: "sightseeing",
    available: true,
  },
  {
    id: 4,
    name: "Burj Khalifa At The Top",
    name_ru: "Бурдж-Халифа — на вершине",
    description_ru: "Билеты на смотровую площадку 124-125 этажи. Потрясающий вид на весь Дубай.",
    price: 260,
    currency: CURRENCY,
    duration_hours: 2,
    emirate: "Dubai",
    category: "attraction",
    available: true,
  },
  {
    id: 5,
    name: "Yacht Cruise Marina",
    name_ru: "Круиз на яхте по Марине",
    description_ru: "2-часовой круиз вдоль Dubai Marina, JBR, Palm Jumeirah. Напитки включены.",
    price: 350,
    currency: CURRENCY,
    duration_hours: 2,
    emirate: "Dubai",
    category: "yacht",
    available: true,
  },
];

// --- Хранилище бронирований (в production -- PostgreSQL) ---
const bookings = [];
let bookingIdCounter = 1000;

// --- Health Check ---
app.get("/health", (req, res) => {
  res.status(200).json({
    status: "ok",
    service: "booking-api-uae",
    timestamp: new Date().toISOString(),
    currency: CURRENCY,
    language: LANGUAGE,
    tours_count: tours.length,
  });
});

// --- Список всех туров ---
app.get("/api/tours", (req, res) => {
  const { category, emirate } = req.query;
  let result = tours.filter((t) => t.available);

  if (category) result = result.filter((t) => t.category === category);
  if (emirate) result = result.filter((t) => t.emirate.toLowerCase() === emirate.toLowerCase());

  res.json({
    total: result.length,
    currency: CURRENCY,
    tours: result,
  });
});

// --- Детали тура ---
app.get("/api/tours/:id", (req, res) => {
  const tour = tours.find((t) => t.id === parseInt(req.params.id));
  if (!tour) {
    return res.status(404).json({ error: "Тур не найден" });
  }
  res.json(tour);
});

// --- Создание бронирования ---
app.post("/api/bookings", (req, res) => {
  const { tour_id, customer_name, customer_phone, guests, date } = req.body;

  // Валидация
  if (!tour_id || !customer_name || !customer_phone || !guests || !date) {
    return res.status(400).json({
      error: "Обязательные поля: tour_id, customer_name, customer_phone, guests, date",
    });
  }

  const tour = tours.find((t) => t.id === tour_id);
  if (!tour) {
    return res.status(404).json({ error: "Тур не найден" });
  }

  const total = tour.price * guests;
  const booking = {
    id: ++bookingIdCounter,
    tour_id,
    tour_name: tour.name_ru,
    customer_name,
    customer_phone,
    guests,
    date,
    price_per_person: tour.price,
    total_price: total,
    currency: CURRENCY,
    status: "confirmed",
    created_at: new Date().toISOString(),
  };

  bookings.push(booking);

  res.status(201).json({
    message: `Бронирование подтверждено! Итого: ${total} ${CURRENCY}`,
    booking,
  });
});

// --- Список бронирований ---
app.get("/api/bookings", (req, res) => {
  res.json({
    total: bookings.length,
    bookings,
  });
});

// --- Запуск сервера ---
app.listen(PORT, "0.0.0.0", () => {
  console.log(`[Booking API] Сервер запущен: http://0.0.0.0:${PORT}`);
  console.log(`[Booking API] Валюта: ${CURRENCY} | Язык: ${LANGUAGE}`);
  console.log(`[Booking API] Туров в каталоге: ${tours.length}`);
});
