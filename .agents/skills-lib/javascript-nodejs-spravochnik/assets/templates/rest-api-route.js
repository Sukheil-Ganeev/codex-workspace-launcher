/**
 * REST API Route Template
 *
 * Production-ready шаблон для REST API маршрутов
 * с CRUD операциями, валидацией и обработкой ошибок.
 *
 * @example
 * // В express-server-template.js:
 * const bookingsRouter = require('./rest-api-route');
 * app.use('/api/bookings', bookingsRouter);
 */

const express = require('express');
const router = express.Router();

// TODO: Импортировать модели и middleware
// const { Booking } = require('../models');
// const { authenticate, authorize } = require('../middleware/auth');

// ==================== MIDDLEWARE ====================

/**
 * Валидация ID параметра
 */
router.param('id', (req, res, next, id) => {
  // TODO: Добавить валидацию ID
  if (!id || isNaN(id)) {
    return res.status(400).json({ error: 'Invalid ID format' });
  }
  next();
});

// ==================== GET ROUTES ====================

/**
 * GET /api/resource - Получить все ресурсы
 * @query {number} limit - Количество результатов (default: 10)
 * @query {number} skip - Пропустить записей (default: 0)
 */
router.get('/', async (req, res, next) => {
  try {
    const limit = Math.min(parseInt(req.query.limit) || 10, 100);
    const skip = parseInt(req.query.skip) || 0;

    // TODO: Реализовать получение данных
    // const items = await Booking.find().limit(limit).skip(skip);

    res.json({
      data: [],
      pagination: { limit, skip, total: 0 },
    });
  } catch (error) {
    next(error);
  }
});

/**
 * GET /api/resource/:id - Получить один ресурс
 */
router.get('/:id', async (req, res, next) => {
  try {
    // TODO: Реализовать получение по ID
    // const item = await Booking.findById(req.params.id);

    // if (!item) {
    //   return res.status(404).json({ error: 'Resource not found' });
    // }

    res.json({ data: {} });
  } catch (error) {
    next(error);
  }
});

// ==================== POST ROUTE ====================

/**
 * POST /api/resource - Создать новый ресурс
 * @body {Object} data - Данные ресурса
 */
router.post('/', async (req, res, next) => {
  try {
    // TODO: Добавить валидацию
    if (!req.body || Object.keys(req.body).length === 0) {
      return res.status(400).json({ error: 'Request body is required' });
    }

    // TODO: Создать ресурс
    // const item = await Booking.create(req.body);

    res.status(201).json({
      message: 'Resource created',
      data: {},
    });
  } catch (error) {
    next(error);
  }
});

// ==================== PUT ROUTE ====================

/**
 * PUT /api/resource/:id - Обновить ресурс
 */
router.put('/:id', async (req, res, next) => {
  try {
    if (!req.body || Object.keys(req.body).length === 0) {
      return res.status(400).json({ error: 'Request body is required' });
    }

    // TODO: Обновить ресурс
    // const item = await Booking.findByIdAndUpdate(
    //   req.params.id,
    //   req.body,
    //   { new: true }
    // );

    res.json({
      message: 'Resource updated',
      data: {},
    });
  } catch (error) {
    next(error);
  }
});

// ==================== DELETE ROUTE ====================

/**
 * DELETE /api/resource/:id - Удалить ресурс
 */
router.delete('/:id', async (req, res, next) => {
  try {
    // TODO: Удалить ресурс
    // await Booking.findByIdAndDelete(req.params.id);

    res.json({ message: 'Resource deleted' });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
