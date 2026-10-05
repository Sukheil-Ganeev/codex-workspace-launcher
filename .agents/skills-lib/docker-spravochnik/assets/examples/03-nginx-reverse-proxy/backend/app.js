// =============================================================================
// app.js — Backend API бронирования туров ОАЭ
// Express.js + PostgreSQL + Redis | Февраль 2026
// =============================================================================

const express = require('express');

const app = express();
const PORT = process.env.PORT || 3000;
const CURRENCY = process.env.TOURS_CURRENCY || 'AED';
const LANGUAGE = process.env.DEFAULT_LANGUAGE || 'ru';

app.use(express.json());

// --- Каталог туров (в реальном проекте — из PostgreSQL) ---
const tours = [
  { id: 1, name: 'Desert Safari Premium', price: 250, duration: '6 часов', category: 'safari' },
  { id: 2, name: 'Dubai City Tour', price: 180, duration: '4 часа', category: 'city' },
  { id: 3, name: 'Abu Dhabi Full Day', price: 220, duration: '10 часов', category: 'city' },
  { id: 4, name: 'Burj Khalifa At The Top', price: 260, duration: '1.5 часа', category: 'attraction' },
  { id: 5, name: 'Dubai Marina Yacht Cruise', price: 350, duration: '3 часа', category: 'yacht' },
];

// --- Healthcheck ---
app.get('/health', (req, res) => {
  res.json({ status: 'ok', currency: CURRENCY, language: LANGUAGE });
});

// --- Список туров ---
app.get('/api/tours', (req, res) => {
  const { category } = req.query;
  let result = tours;

  if (category) {
    result = tours.filter((t) => t.category === category);
  }

  res.json({
    currency: CURRENCY,
    count: result.length,
    tours: result,
  });
});

// --- Детали тура ---
app.get('/api/tours/:id', (req, res) => {
  const tour = tours.find((t) => t.id === parseInt(req.params.id, 10));

  if (!tour) {
    return res.status(404).json({ error: 'Тур не найден' });
  }

  res.json({ currency: CURRENCY, tour });
});

// --- Создание бронирования ---
app.post('/api/bookings', (req, res) => {
  const { tourId, customerName, customerPhone, date, guests } = req.body;

  if (!tourId || !customerName || !customerPhone) {
    return res.status(400).json({
      error: 'Обязательные поля: tourId, customerName, customerPhone',
    });
  }

  const tour = tours.find((t) => t.id === tourId);
  if (!tour) {
    return res.status(404).json({ error: 'Тур не найден' });
  }

  const booking = {
    id: `BK-${Date.now()}`,
    tour: tour.name,
    price: tour.price * (guests || 1),
    currency: CURRENCY,
    customer: { name: customerName, phone: customerPhone },
    date: date || 'TBD',
    guests: guests || 1,
    status: 'pending',
    createdAt: new Date().toISOString(),
  };

  // В реальном проекте: INSERT INTO bookings ... + Redis кэш
  res.status(201).json(booking);
});

// --- Запуск ---
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Booking API запущен на порту ${PORT} (${CURRENCY}, ${LANGUAGE})`);
});
