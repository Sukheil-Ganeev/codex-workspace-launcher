# Express API — Полный справочник

Express.js — это минималистичный веб-фреймворк для Node.js, идеален для создания RESTful API. Этот справочник охватывает все основные концепции с примерами для туристического бизнеса (туры, бронирования, загрузка изображений).

---

## 1. Express Setup и Basic Server

### Установка и инициализация

```bash
npm init -y
npm install express
```

### Базовый сервер

```javascript
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware для парсинга JSON
app.use(express.json());

// Базовый маршрут
app.get('/', (req, res) => {
  res.json({ message: 'Tour API Server Running' });
});

// Запуск сервера
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
```

### Использование переменных окружения

```javascript
require('dotenv').config();
const app = express();

const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || 'development';

app.use(express.json());

app.get('/config', (req, res) => {
  res.json({
    environment: NODE_ENV,
    port: PORT,
    apiVersion: process.env.API_VERSION
  });
});

app.listen(PORT);
```

**Файл .env:**
```
PORT=3000
NODE_ENV=development
API_VERSION=1.0.0
DB_CONNECTION=mongodb://localhost:27017/tours
JWT_SECRET=your_secret_key
```

---

## 2. Routing (GET, POST, PUT, DELETE)

### GET — Получение данных

```javascript
// Получить все туры
app.get('/api/tours', (req, res) => {
  const tours = [
    { id: 1, name: 'Desert Safari', price: 150, duration: 4 },
    { id: 2, name: 'City Tour', price: 100, duration: 3 },
    { id: 3, name: 'Beach Day', price: 120, duration: 6 }
  ];
  res.json(tours);
});

// Получить тур по ID
app.get('/api/tours/:id', (req, res) => {
  const { id } = req.params;
  const tour = { id, name: 'Desert Safari', price: 150, duration: 4 };

  if (!tour) {
    return res.status(404).json({ error: 'Tour not found' });
  }

  res.json(tour);
});

// Query параметры (фильтрация)
app.get('/api/tours/search', (req, res) => {
  const { minPrice, maxPrice, duration } = req.query;

  let tours = [
    { id: 1, name: 'Desert Safari', price: 150, duration: 4 },
    { id: 2, name: 'City Tour', price: 100, duration: 3 },
    { id: 3, name: 'Beach Day', price: 120, duration: 6 }
  ];

  if (minPrice) {
    tours = tours.filter(t => t.price >= parseInt(minPrice));
  }
  if (maxPrice) {
    tours = tours.filter(t => t.price <= parseInt(maxPrice));
  }

  res.json(tours);
});
```

### POST — Создание данных

```javascript
// Создать новый тур
app.post('/api/tours', (req, res) => {
  const { name, price, duration, description, location } = req.body;

  // Валидация
  if (!name || !price || !duration) {
    return res.status(400).json({
      error: 'Missing required fields: name, price, duration'
    });
  }

  const newTour = {
    id: Date.now(),
    name,
    price,
    duration,
    description,
    location,
    createdAt: new Date()
  };

  // Сохранить в БД (здесь просто возвращаем)
  res.status(201).json({
    message: 'Tour created successfully',
    tour: newTour
  });
});

// Пример запроса:
// POST /api/tours
// {
//   "name": "Yacht Cruise",
//   "price": 200,
//   "duration": 5,
//   "description": "Luxury yacht cruise in Dubai",
//   "location": "Marina, Dubai"
// }
```

### PUT — Обновление данных

```javascript
// Обновить тур
app.put('/api/tours/:id', (req, res) => {
  const { id } = req.params;
  const { name, price, duration, description } = req.body;

  // Проверка ID
  if (!id || isNaN(id)) {
    return res.status(400).json({ error: 'Invalid tour ID' });
  }

  const updatedTour = {
    id: parseInt(id),
    name: name || 'Desert Safari',
    price: price || 150,
    duration: duration || 4,
    description: description || 'Amazing desert experience',
    updatedAt: new Date()
  };

  res.json({
    message: 'Tour updated successfully',
    tour: updatedTour
  });
});

// Пример запроса:
// PUT /api/tours/1
// {
//   "name": "Desert Safari Deluxe",
//   "price": 200
// }
```

### DELETE — Удаление данных

```javascript
// Удалить тур
app.delete('/api/tours/:id', (req, res) => {
  const { id } = req.params;

  if (!id || isNaN(id)) {
    return res.status(400).json({ error: 'Invalid tour ID' });
  }

  // Удаление из БД (имитация)
  res.json({
    message: `Tour ${id} deleted successfully`,
    deletedId: parseInt(id)
  });
});
```

### Router — Группировка маршрутов

```javascript
// routes/tours.js
const router = express.Router();

router.get('/', (req, res) => {
  res.json({ tours: [] });
});

router.post('/', (req, res) => {
  res.status(201).json({ message: 'Tour created' });
});

router.get('/:id', (req, res) => {
  res.json({ id: req.params.id });
});

router.put('/:id', (req, res) => {
  res.json({ message: 'Tour updated' });
});

router.delete('/:id', (req, res) => {
  res.json({ message: 'Tour deleted' });
});

module.exports = router;

// app.js
const tourRoutes = require('./routes/tours');
app.use('/api/tours', tourRoutes);
```

---

## 3. Middleware (встроенное, пользовательское, сторонние)

### Встроенное middleware

```javascript
// Парсинг JSON
app.use(express.json());

// Парсинг URL-encoded данных (формы)
app.use(express.urlencoded({ extended: true }));

// Статические файлы
app.use(express.static('public'));

// Размер лимита для больших файлов
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));
```

### Пользовательское middleware

```javascript
// Логирование всех запросов
app.use((req, res, next) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${req.method} ${req.path}`);
  next();
});

// Middleware для добавления заголовков
app.use((req, res, next) => {
  res.setHeader('X-Powered-By', 'Tour API');
  res.setHeader('X-API-Version', '1.0.0');
  next();
});

// Middleware для проверки аутентификации
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  // Проверка токена (здесь имитация)
  if (token !== 'valid_token_123') {
    return res.status(403).json({ error: 'Invalid token' });
  }

  next();
};

// Использование middleware на конкретных маршрутах
app.get('/api/bookings', authenticateToken, (req, res) => {
  res.json({ bookings: [] });
});

// Middleware для проверки role
const authorizeRole = (roles) => {
  return (req, res, next) => {
    const userRole = req.headers['x-user-role'];

    if (!userRole || !roles.includes(userRole)) {
      return res.status(403).json({
        error: 'Insufficient permissions'
      });
    }

    next();
  };
};

app.delete('/api/tours/:id', authorizeRole(['admin']), (req, res) => {
  res.json({ message: 'Tour deleted' });
});
```

### Сторонние middleware

```javascript
// Установка:
// npm install cors morgan helmet compression

const cors = require('cors');
const morgan = require('morgan');
const helmet = require('helmet');
const compression = require('compression');

// CORS - кросс-доменные запросы
app.use(cors({
  origin: ['http://localhost:3000', 'https://yourdomain.com'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Morgan - логирование HTTP запросов
app.use(morgan('combined')); // :remote-addr - :remote-user [:date[clf]] ":method :url HTTP/:http-version" :status :res[content-length]

// Helmet - безопасность (устанавливает заголовки)
app.use(helmet());

// Compression - сжатие ответов
app.use(compression());
```

---

## 4. Request/Response Handling

### Получение данных из request

```javascript
app.post('/api/bookings', (req, res) => {
  // Body (JSON)
  const { tourId, name, email, guests, date } = req.body;

  // Params (из URL)
  const userId = req.params.userId;

  // Query (строка запроса)
  const { promo } = req.query;

  // Headers
  const authToken = req.headers['authorization'];
  const userAgent = req.headers['user-agent'];

  // Cookies
  const sessionId = req.cookies?.sessionId;

  console.log('Body:', req.body);
  console.log('Params:', req.params);
  console.log('Query:', req.query);
  console.log('Headers:', req.headers);

  res.json({ received: { tourId, name, email, guests, date } });
});
```

### Отправка ответов

```javascript
// JSON
app.get('/json', (req, res) => {
  res.json({ status: 'ok', data: [] });
});

// HTML
app.get('/html', (req, res) => {
  res.send('<h1>Tour API</h1><p>Welcome to our tour service</p>');
});

// Текст
app.get('/text', (req, res) => {
  res.type('text/plain').send('Plain text response');
});

// Файл
app.get('/download', (req, res) => {
  res.download('public/tour-guide.pdf', 'tour-guide.pdf');
});

// Редирект
app.get('/old-api', (req, res) => {
  res.redirect(301, '/api/tours');
});

// Со статус кодом и заголовками
app.get('/custom', (req, res) => {
  res
    .status(201)
    .set({
      'Content-Type': 'application/json',
      'X-Custom-Header': 'value'
    })
    .json({ message: 'Created' });
});

// Потоковая передача данных
app.get('/stream', (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.write('{"tours": [');
  res.write('{"id": 1, "name": "Safari"},');
  res.write('{"id": 2, "name": "Beach"}');
  res.write(']}');
  res.end();
});
```

### Валидация данных

```javascript
const validateBooking = (req, res, next) => {
  const { tourId, name, email, guests, date } = req.body;
  const errors = [];

  if (!tourId || isNaN(tourId)) {
    errors.push('Valid tourId is required');
  }
  if (!name || name.trim().length < 2) {
    errors.push('Name must be at least 2 characters');
  }
  if (!email || !email.includes('@')) {
    errors.push('Valid email is required');
  }
  if (!guests || guests < 1 || guests > 50) {
    errors.push('Guests must be between 1 and 50');
  }
  if (!date || new Date(date) < new Date()) {
    errors.push('Date must be in the future');
  }

  if (errors.length > 0) {
    return res.status(400).json({
      error: 'Validation failed',
      details: errors
    });
  }

  next();
};

app.post('/api/bookings', validateBooking, (req, res) => {
  res.json({ message: 'Booking created' });
});
```

---

## 5. Error Handling Middleware

### Обработка ошибок

```javascript
// 404 - маршрут не найден
app.use((req, res) => {
  res.status(404).json({
    error: 'Not found',
    message: `Route ${req.method} ${req.path} does not exist`,
    timestamp: new Date().toISOString()
  });
});

// Глобальная обработка ошибок (должна быть в конце!)
app.use((err, req, res, next) => {
  const status = err.status || err.statusCode || 500;
  const message = err.message || 'Internal server error';

  console.error('Error:', {
    status,
    message,
    path: req.path,
    method: req.method,
    timestamp: new Date().toISOString()
  });

  res.status(status).json({
    error: message,
    status,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
});

// Обработка async ошибок
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

app.get('/api/tours/:id', asyncHandler(async (req, res) => {
  const tour = await fetchTourFromDB(req.params.id);

  if (!tour) {
    const error = new Error('Tour not found');
    error.status = 404;
    throw error;
  }

  res.json(tour);
}));

// Или использовать try-catch
app.post('/api/bookings', async (req, res, next) => {
  try {
    const booking = await saveBooking(req.body);
    res.status(201).json(booking);
  } catch (error) {
    next(error);
  }
});
```

### Кастомные классы ошибок

```javascript
class AppError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

class ValidationError extends AppError {
  constructor(message) {
    super(message, 400);
    this.name = 'ValidationError';
  }
}

class NotFoundError extends AppError {
  constructor(message = 'Resource not found') {
    super(message, 404);
    this.name = 'NotFoundError';
  }
}

class AuthenticationError extends AppError {
  constructor(message = 'Unauthorized') {
    super(message, 401);
    this.name = 'AuthenticationError';
  }
}

// Использование
app.get('/api/tours/:id', (req, res, next) => {
  try {
    if (isNaN(req.params.id)) {
      throw new ValidationError('Tour ID must be a number');
    }

    // ...остальной код
  } catch (error) {
    next(error);
  }
});
```

---

## 6. CORS Configuration

### Базовая конфигурация

```javascript
const cors = require('cors');

// Разрешить все источники
app.use(cors());

// Разрешить конкретные источники
app.use(cors({
  origin: 'https://yourdomain.com',
  credentials: true
}));

// Разрешить несколько источников
app.use(cors({
  origin: (origin, callback) => {
    const whitelist = [
      'http://localhost:3000',
      'https://yourdomain.com',
      'https://admin.yourdomain.com'
    ];

    if (whitelist.includes(origin) || !origin) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  optionsSuccessStatus: 200
}));

// Специфичный маршрут с CORS
app.get('/api/tours', cors(), (req, res) => {
  res.json({ tours: [] });
});

// Без CORS
app.post('/api/internal', (req, res) => {
  res.json({ message: 'Internal only' });
});
```

### Preflight запросы

```javascript
// Express обрабатывает автоматически, но можно явно:
app.options('/api/bookings', cors());

app.post('/api/bookings', (req, res) => {
  res.json({ message: 'Booking created' });
});

// Или для всех маршрутов
app.options('*', cors());
```

---

## 7. File Upload (multer)

### Установка и базовая конфигурация

```bash
npm install multer
```

```javascript
const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Конфигурация хранилища
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = 'uploads/tours';

    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }

    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

// Фильтр файлов
const fileFilter = (req, file, cb) => {
  const allowedMimes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
  const maxSize = 5 * 1024 * 1024; // 5MB

  if (!allowedMimes.includes(file.mimetype)) {
    cb(new Error('Only JPEG, PNG, WebP and GIF images are allowed'));
    return;
  }

  if (file.size > maxSize) {
    cb(new Error('File size must not exceed 5MB'));
    return;
  }

  cb(null, true);
};

// Создание upload instance
const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB
    files: 5 // макс 5 файлов одновременно
  }
});
```

### Загрузка одного файла

```javascript
// Загрузка одного изображения тура
app.post('/api/tours/:id/image', upload.single('image'), (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const imageUrl = `/uploads/tours/${req.file.filename}`;

    // Сохранить URL в БД
    // await updateTourImage(req.params.id, imageUrl);

    res.json({
      message: 'Image uploaded successfully',
      filename: req.file.filename,
      size: req.file.size,
      url: imageUrl
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

### Загрузка нескольких файлов

```javascript
// Загрузка галереи тура
app.post('/api/tours/:id/gallery', upload.array('images', 10), (req, res) => {
  try {
    if (!req.files || req.files.length === 0) {
      return res.status(400).json({ error: 'No files uploaded' });
    }

    const uploadedFiles = req.files.map(file => ({
      filename: file.filename,
      originalName: file.originalname,
      size: file.size,
      url: `/uploads/tours/${file.filename}`,
      uploadedAt: new Date()
    }));

    res.json({
      message: 'Files uploaded successfully',
      count: req.files.length,
      files: uploadedFiles
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

### Загрузка нескольких полей

```javascript
const uploadMultiple = upload.fields([
  { name: 'thumbnail', maxCount: 1 },
  { name: 'gallery', maxCount: 10 }
]);

app.post('/api/tours', uploadMultiple, (req, res) => {
  try {
    const { name, price, duration } = req.body;
    const thumbnail = req.files?.thumbnail?.[0];
    const gallery = req.files?.gallery || [];

    const tourData = {
      name,
      price,
      duration,
      thumbnail: thumbnail ? `/uploads/tours/${thumbnail.filename}` : null,
      gallery: gallery.map(f => ({
        filename: f.filename,
        url: `/uploads/tours/${f.filename}`
      }))
    };

    res.json({
      message: 'Tour created with images',
      tour: tourData
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Пример запроса (FormData):
// const formData = new FormData();
// formData.append('name', 'Desert Safari');
// formData.append('price', '150');
// formData.append('thumbnail', thumbnailFile);
// formData.append('gallery', galleryFile1);
// formData.append('gallery', galleryFile2);
```

### Обработка ошибок upload

```javascript
app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    if (err.code === 'FILE_TOO_LARGE') {
      return res.status(400).json({
        error: 'File too large',
        message: 'Maximum file size is 5MB'
      });
    }
    if (err.code === 'LIMIT_FILE_COUNT') {
      return res.status(400).json({
        error: 'Too many files',
        message: 'Maximum 10 files allowed'
      });
    }
  }

  if (err.message) {
    return res.status(400).json({ error: err.message });
  }

  next(err);
});
```

### Удаление загруженных файлов

```javascript
app.delete('/api/tours/:id/image', (req, res) => {
  try {
    const filename = req.query.filename;

    if (!filename) {
      return res.status(400).json({ error: 'Filename required' });
    }

    const filepath = path.join('uploads/tours', filename);

    if (fs.existsSync(filepath)) {
      fs.unlinkSync(filepath);
      res.json({ message: 'Image deleted successfully' });
    } else {
      res.status(404).json({ error: 'File not found' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

---

## 8. Best Practices

### Структура проекта

```
tour-api/
├── app.js                      # Главный файл приложения
├── server.js                   # Запуск сервера
├── .env                        # Переменные окружения
├── .gitignore
├── package.json
│
├── src/
│   ├── routes/                 # API маршруты
│   │   ├── tours.js
│   │   ├── bookings.js
│   │   ├── users.js
│   │   └── index.js
│   │
│   ├── middleware/             # Кастомные middleware
│   │   ├── auth.js
│   │   ├── validation.js
│   │   ├── errorHandler.js
│   │   └── logger.js
│   │
│   ├── controllers/            # Бизнес логика
│   │   ├── tourController.js
│   │   ├── bookingController.js
│   │   └── userController.js
│   │
│   ├── models/                 # Модели данных (БД)
│   │   ├── Tour.js
│   │   ├── Booking.js
│   │   └── User.js
│   │
│   ├── utils/                  # Утилиты
│   │   ├── validators.js
│   │   ├── formatters.js
│   │   └── logger.js
│   │
│   └── config/                 # Конфигурация
│       ├── database.js
│       ├── multer.js
│       └── cors.js
│
├── uploads/                    # Загруженные файлы
│   └── tours/
│
└── tests/                      # Тесты
    ├── tours.test.js
    └── bookings.test.js
```

### Пример app.js

```javascript
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
require('dotenv').config();

const app = express();

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGIN?.split(',') || '*',
  credentials: true
}));

// Body parsing middleware
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));

// Compression
app.use(compression());

// Static files
app.use(express.static('public'));
app.use('/uploads', express.static('uploads'));

// Logger middleware
app.use((req, res, next) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${req.method} ${req.path}`);
  next();
});

// Routes
const tourRoutes = require('./src/routes/tours');
const bookingRoutes = require('./src/routes/bookings');
const userRoutes = require('./src/routes/users');

app.use('/api/tours', tourRoutes);
app.use('/api/bookings', bookingRoutes);
app.use('/api/users', userRoutes);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not found',
    path: req.path,
    method: req.method
  });
});

// Global error handler
app.use((err, req, res, next) => {
  console.error('Error:', {
    message: err.message,
    status: err.status || 500,
    path: req.path,
    timestamp: new Date().toISOString()
  });

  res.status(err.status || 500).json({
    error: err.message || 'Internal server error',
    status: err.status || 500,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
});

module.exports = app;
```

### Пример server.js

```javascript
const app = require('./app');

const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || 'development';

const server = app.listen(PORT, () => {
  console.log(`
    Server running!
    Environment: ${NODE_ENV}
    Port: ${PORT}
    URL: http://localhost:${PORT}
  `);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
```

### Рекомендации

1. **Используйте Router** для группировки маршрутов
2. **Разделяйте логику**: routes → controllers → services
3. **Валидируйте входные данные** перед обработкой
4. **Используйте статус коды правильно**: 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Error
5. **Логируйте ошибки** для отладки
6. **Используйте переменные окружения** для конфигурации
7. **Реализуйте rate limiting** для API
8. **Используйте HTTPS в production**
9. **Документируйте API** (Swagger/OpenAPI)
10. **Пишите тесты** для критических функций

---

## Дополнительные ресурсы

- [Express.js Official Docs](https://expressjs.com/)
- [Express Best Practices](https://expressjs.com/en/advanced/best-practice-performance.html)
- [REST API Best Practices](https://restfulapi.net/)
- [HTTP Status Codes](https://httpwg.org/specs/rfc7231.html#status.codes)

