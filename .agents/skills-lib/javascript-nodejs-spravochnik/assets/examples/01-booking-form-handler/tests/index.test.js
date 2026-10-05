/**
 * Booking Form Handler - Tests
 */

const request = require('supertest');
const app = require('../index');

describe('Booking API', () => {
  describe('POST /api/bookings', () => {
    it('should create a new booking with valid data', async () => {
      const bookingData = {
        customerName: 'Ahmed Al-Mansouri',
        email: 'ahmed@example.com',
        phone: '+971501234567',
        tourType: 'desert-safari',
        date: '2026-03-15',
        adults: 2,
        children: 1
      };

      const res = await request(app)
        .post('/api/bookings')
        .send(bookingData);

      expect(res.statusCode).toBe(201);
      expect(res.body.status).toBe('success');
      expect(res.body.data).toHaveProperty('id');
      expect(res.body.data).toHaveProperty('confirmationCode');
      expect(res.body.data.status).toBe('confirmed');
    });

    it('should reject booking with invalid email', async () => {
      const bookingData = {
        customerName: 'Ahmed Al-Mansouri',
        email: 'invalid-email',
        phone: '+971501234567',
        tourType: 'desert-safari',
        date: '2026-03-15',
        adults: 2
      };

      const res = await request(app)
        .post('/api/bookings')
        .send(bookingData);

      expect(res.statusCode).toBe(400);
      expect(res.body.status).toBe('error');
      expect(res.body.details).toBeDefined();
    });

    it('should reject booking without required fields', async () => {
      const bookingData = {
        customerName: 'Ahmed',
        email: 'ahmed@example.com'
        // missing other required fields
      };

      const res = await request(app)
        .post('/api/bookings')
        .send(bookingData);

      expect(res.statusCode).toBe(400);
      expect(res.body.status).toBe('error');
    });

    it('should reject invalid tour type', async () => {
      const bookingData = {
        customerName: 'Ahmed Al-Mansouri',
        email: 'ahmed@example.com',
        phone: '+971501234567',
        tourType: 'invalid-tour',
        date: '2026-03-15',
        adults: 2
      };

      const res = await request(app)
        .post('/api/bookings')
        .send(bookingData);

      expect(res.statusCode).toBe(400);
    });
  });

  describe('GET /api/bookings/:id', () => {
    it('should return 404 for non-existent booking', async () => {
      const res = await request(app)
        .get('/api/bookings/non-existent-id');

      expect(res.statusCode).toBe(404);
      expect(res.body.status).toBe('error');
    });
  });

  describe('PUT /api/bookings/:id', () => {
    it('should reject invalid status', async () => {
      const res = await request(app)
        .put('/api/bookings/some-id')
        .send({ status: 'invalid-status' });

      expect(res.statusCode).toBe(400);
      expect(res.body.status).toBe('error');
    });
  });

  describe('GET /health', () => {
    it('should return health status', async () => {
      const res = await request(app)
        .get('/health');

      expect(res.statusCode).toBe(200);
      expect(res.body.status).toBe('ok');
      expect(res.body).toHaveProperty('timestamp');
    });
  });
});
