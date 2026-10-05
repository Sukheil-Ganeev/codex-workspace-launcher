# Testing & Deployment

Практический справочник по тестированию и развёртыванию Node.js приложений. Покрывает модульное тестирование, интеграционные тесты, CI/CD и Docker.

---

## 1. Jest Setup и Unit Tests

Jest — стандартный фреймворк для тестирования JavaScript/Node.js приложений.

### Установка и базовая конфигурация

```bash
npm install --save-dev jest @types/jest
npx jest --init  # Автогенерация jest.config.js
```

**jest.config.js:**
```javascript
module.exports = {
  testEnvironment: 'node',
  coveragePathIgnorePatterns: ['/node_modules/'],
  testMatch: ['**/__tests__/**/*.js', '**/?(*.)+(spec|test).js'],
  collectCoverageFrom: [
    'src/**/*.js',
    '!src/index.js',
    '!src/**/*.config.js'
  ]
};
```

### Простой unit тест

**src/calculator.js:**
```javascript
function add(a, b) {
  if (typeof a !== 'number' || typeof b !== 'number') {
    throw new Error('Both arguments must be numbers');
  }
  return a + b;
}

function subtract(a, b) {
  return a - b;
}

module.exports = { add, subtract };
```

**src/__tests__/calculator.test.js:**
```javascript
const { add, subtract } = require('../calculator');

describe('Calculator', () => {
  describe('add function', () => {
    test('should add two positive numbers', () => {
      expect(add(2, 3)).toBe(5);
    });

    test('should handle negative numbers', () => {
      expect(add(-2, 3)).toBe(1);
    });

    test('should throw error for non-numeric input', () => {
      expect(() => add('2', 3)).toThrow('Both arguments must be numbers');
    });
  });

  describe('subtract function', () => {
    test('should subtract two numbers', () => {
      expect(subtract(5, 3)).toBe(2);
    });
  });
});
```

**Запуск тестов:**
```bash
npm test                    # Запустить все тесты
npm test -- --watch        # Режим наблюдения
npm test -- --coverage     # С отчётом покрытия
npm test -- calculator     # Конкретный файл
```

### Mocking и fixtures

```javascript
describe('User Service', () => {
  const mockDatabase = {
    findUser: jest.fn(),
    saveUser: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();  // Очистить моки перед каждым тестом
  });

  test('should find user by ID', () => {
    const mockUser = { id: 1, name: 'John' };
    mockDatabase.findUser.mockResolvedValue(mockUser);

    mockDatabase.findUser(1).then(user => {
      expect(user.name).toBe('John');
      expect(mockDatabase.findUser).toHaveBeenCalledWith(1);
    });
  });

  test('should handle database error', () => {
    mockDatabase.findUser.mockRejectedValue(new Error('DB Error'));

    expect(mockDatabase.findUser(1)).rejects.toThrow('DB Error');
  });
});
```

---

## 2. Integration Tests

Интеграционные тесты проверяют взаимодействие между компонентами.

**src/services/bookingService.js:**
```javascript
class BookingService {
  constructor(database, emailService) {
    this.db = database;
    this.email = emailService;
  }

  async createBooking(bookingData) {
    // Валидация
    if (!bookingData.userId || !bookingData.touristId) {
      throw new Error('Missing required fields');
    }

    // Сохранение в БД
    const booking = await this.db.saveBooking(bookingData);

    // Отправка email
    await this.email.sendConfirmation(booking.userId, booking.id);

    return booking;
  }

  async cancelBooking(bookingId) {
    const booking = await this.db.findBooking(bookingId);

    if (!booking) {
      throw new Error('Booking not found');
    }

    await this.db.updateBooking(bookingId, { status: 'cancelled' });
    await this.email.sendCancellation(booking.userId, bookingId);

    return { success: true };
  }
}

module.exports = BookingService;
```

**src/__tests__/bookingService.integration.test.js:**
```javascript
const BookingService = require('../services/bookingService');

describe('BookingService Integration Tests', () => {
  let bookingService;
  let mockDB;
  let mockEmailService;

  beforeEach(() => {
    mockDB = {
      saveBooking: jest.fn(),
      findBooking: jest.fn(),
      updateBooking: jest.fn()
    };

    mockEmailService = {
      sendConfirmation: jest.fn().mockResolvedValue(true),
      sendCancellation: jest.fn().mockResolvedValue(true)
    };

    bookingService = new BookingService(mockDB, mockEmailService);
  });

  test('should create booking and send confirmation email', async () => {
    const bookingData = {
      userId: 'user123',
      touristId: 'dubai-tour-001',
      date: '2026-03-15'
    };

    const savedBooking = { id: 'booking001', ...bookingData };
    mockDB.saveBooking.mockResolvedValue(savedBooking);

    const result = await bookingService.createBooking(bookingData);

    expect(mockDB.saveBooking).toHaveBeenCalledWith(bookingData);
    expect(mockEmailService.sendConfirmation).toHaveBeenCalledWith(
      'user123',
      'booking001'
    );
    expect(result.id).toBe('booking001');
  });

  test('should cancel booking and notify user', async () => {
    mockDB.findBooking.mockResolvedValue({
      id: 'booking001',
      userId: 'user123'
    });

    const result = await bookingService.cancelBooking('booking001');

    expect(mockDB.updateBooking).toHaveBeenCalledWith(
      'booking001',
      { status: 'cancelled' }
    );
    expect(mockEmailService.sendCancellation).toHaveBeenCalledWith(
      'user123',
      'booking001'
    );
    expect(result.success).toBe(true);
  });

  test('should throw error on missing booking', async () => {
    mockDB.findBooking.mockResolvedValue(null);

    await expect(bookingService.cancelBooking('invalid-id'))
      .rejects
      .toThrow('Booking not found');
  });
});
```

---

## 3. API Testing (Supertest)

Supertest позволяет тестировать Express/HTTP API.

**Установка:**
```bash
npm install --save-dev supertest
```

**src/app.js:**
```javascript
const express = require('express');
const app = express();

app.use(express.json());

// In-memory booking storage (для примера)
const bookings = new Map();

// Create booking
app.post('/api/bookings', (req, res) => {
  const { touristId, userId, date, people } = req.body;

  if (!touristId || !userId || !date) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const bookingId = 'booking_' + Date.now();
  const booking = {
    id: bookingId,
    touristId,
    userId,
    date,
    people: people || 1,
    status: 'confirmed'
  };

  bookings.set(bookingId, booking);
  res.status(201).json(booking);
});

// Get booking
app.get('/api/bookings/:id', (req, res) => {
  const booking = bookings.get(req.params.id);

  if (!booking) {
    return res.status(404).json({ error: 'Booking not found' });
  }

  res.json(booking);
});

// Cancel booking
app.patch('/api/bookings/:id', (req, res) => {
  const booking = bookings.get(req.params.id);

  if (!booking) {
    return res.status(404).json({ error: 'Booking not found' });
  }

  booking.status = 'cancelled';
  res.json(booking);
});

module.exports = app;
```

**src/__tests__/api.test.js:**
```javascript
const request = require('supertest');
const app = require('../app');

describe('Booking API', () => {
  describe('POST /api/bookings', () => {
    test('should create booking with valid data', async () => {
      const response = await request(app)
        .post('/api/bookings')
        .send({
          touristId: 'dubai-tour-001',
          userId: 'user123',
          date: '2026-03-15',
          people: 2
        })
        .expect(201);

      expect(response.body).toHaveProperty('id');
      expect(response.body.status).toBe('confirmed');
      expect(response.body.people).toBe(2);
    });

    test('should return 400 for missing required fields', async () => {
      const response = await request(app)
        .post('/api/bookings')
        .send({
          userId: 'user123'
          // Missing touristId and date
        })
        .expect(400);

      expect(response.body.error).toBe('Missing required fields');
    });
  });

  describe('GET /api/bookings/:id', () => {
    test('should retrieve booking', async () => {
      // Создаём бронирование
      const createResponse = await request(app)
        .post('/api/bookings')
        .send({
          touristId: 'dubai-tour-001',
          userId: 'user123',
          date: '2026-03-15'
        });

      const bookingId = createResponse.body.id;

      // Получаем его
      const response = await request(app)
        .get(`/api/bookings/${bookingId}`)
        .expect(200);

      expect(response.body.id).toBe(bookingId);
      expect(response.body.status).toBe('confirmed');
    });

    test('should return 404 for non-existent booking', async () => {
      await request(app)
        .get('/api/bookings/non-existent-id')
        .expect(404);
    });
  });

  describe('PATCH /api/bookings/:id', () => {
    test('should cancel booking', async () => {
      const createResponse = await request(app)
        .post('/api/bookings')
        .send({
          touristId: 'dubai-tour-001',
          userId: 'user123',
          date: '2026-03-15'
        });

      const bookingId = createResponse.body.id;

      const response = await request(app)
        .patch(`/api/bookings/${bookingId}`)
        .expect(200);

      expect(response.body.status).toBe('cancelled');
    });
  });
});
```

---

## 4. Test Coverage

Test coverage показывает, какой процент кода покрыт тестами.

**Запуск с отчётом:**
```bash
npm test -- --coverage --collectCoverageFrom="src/**/*.js"
```

**Пример вывода:**
```
File                    | % Stmts | % Branch | % Funcs | % Lines |
------------------------|---------| ---------|---------|---------|
All files               |   92.5  |   85.2   |   95.0  |   90.1  |
 src/app.js             |   100   |   85.0   |   100   |   100   |
 src/calculator.js      |   100   |   100    |   100   |   100   |
 src/services/booking.. |    85   |   80.0   |    90   |   85    |
```

**Пороги покрытия в jest.config.js:**
```javascript
module.exports = {
  collectCoverageFrom: ['src/**/*.js'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    },
    './src/critical.js': {
      branches: 100,
      functions: 100,
      lines: 100,
      statements: 100
    }
  }
};
```

Если покрытие ниже пороговых значений, тесты не пройдут.

---

## 5. CI/CD (GitHub Actions)

GitHub Actions автоматизирует запуск тестов при push и pull requests.

**.github/workflows/tests.yml:**
```yaml
name: Run Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]

    steps:
      - uses: actions/checkout@v3

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run tests
        run: npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
          flags: unittests
          name: codecov-umbrella

      - name: Check coverage thresholds
        run: npm test -- --coverage --collectCoverageFrom="src/**/*.js"
```

**package.json:**
```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/**/*.js",
    "build": "node build.js"
  }
}
```

---

## 6. Docker Basics

Docker упаковывает приложение в контейнер для единообразного развёртывания.

**Dockerfile:**
```dockerfile
# Multi-stage build для оптимизации размера образа
FROM node:20-alpine AS builder

WORKDIR /app

# Копируем package files
COPY package*.json ./

# Устанавливаем зависимости (включая dev)
RUN npm ci

# Копируем исходный код
COPY . .

# Запускаем тесты
RUN npm test

# Финальный образ (меньше размером)
FROM node:20-alpine

WORKDIR /app

# Копируем package files
COPY package*.json ./

# Устанавливаем только production зависимости
RUN npm ci --only=production

# Копируем исходный код из builder
COPY --from=builder /app/src ./src

# Expose порт
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Start команда
CMD ["node", "src/index.js"]
```

**.dockerignore:**
```
node_modules
npm-debug.log
.git
.gitignore
README.md
.env
.env.local
coverage
dist
```

**Команды Docker:**
```bash
# Построить образ
docker build -t my-app:1.0 .

# Запустить контейнер
docker run -p 3000:3000 --name my-app-container my-app:1.0

# Проверить логи
docker logs my-app-container

# Остановить контейнер
docker stop my-app-container

# Удалить контейнер
docker rm my-app-container
```

**docker-compose.yml (для локальной разработки):**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: development
      DB_URL: mongodb://mongodb:27017/myapp
    depends_on:
      - mongodb
    volumes:
      - .:/app
      - /app/node_modules
    command: npm run dev

  mongodb:
    image: mongo:6
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

volumes:
  mongodb_data:
```

```bash
docker-compose up    # Запустить все сервисы
docker-compose down  # Остановить
```

---

## 7. Deployment Strategies

### 7.1 Развёртывание на Heroku

**Procfile:**
```
web: node src/index.js
worker: node src/worker.js
```

```bash
# Логин в Heroku
heroku login

# Создать приложение
heroku create my-tourism-app

# Установить переменные окружения
heroku config:set NODE_ENV=production
heroku config:set DB_URL=mongodb+srv://user:pass@cluster.mongodb.net/db

# Deploy
git push heroku main

# Просмотреть логи
heroku logs --tail

# Масштабирование
heroku ps:scale web=2
```

### 7.2 Развёртывание на AWS (EC2 + S3)

**Скрипт развёртывания (deploy.sh):**
```bash
#!/bin/bash
set -e

echo "Building application..."
npm run build

echo "Running tests..."
npm test

echo "Creating artifact..."
tar -czf app-build.tar.gz src/ package*.json

echo "Uploading to S3..."
aws s3 cp app-build.tar.gz s3://my-deployments/builds/

echo "Connecting to EC2..."
ssh -i key.pem ec2-user@your-ec2-instance << 'EOF'
  cd /home/ec2-user/app
  aws s3 cp s3://my-deployments/builds/app-build.tar.gz ./
  tar -xzf app-build.tar.gz
  npm install --production
  npm stop || true
  npm start &
EOF

echo "Deployment complete!"
```

### 7.3 Blue-Green Deployment

```javascript
// Безопасное развёртывание с возможностью откката
const cluster = require('cluster');
const os = require('os');

if (cluster.isMaster) {
  const numCPUs = os.cpus().length;

  // Запустить worker процессы
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }

  // Graceful restart для обновлений
  process.on('SIGUSR2', () => {
    console.log('Graceful restart initiated...');
    for (const id in cluster.workers) {
      cluster.workers[id].kill();
      cluster.fork();  // Новый процесс с обновленным кодом
    }
  });
}

const express = require('express');
const app = express();

app.listen(3000, () => {
  console.log(`Worker ${process.pid} started`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, closing gracefully...');
  process.exit(0);
});
```

---

## Чек-лист для Production

- [ ] Все критические пути покрыты тестами (>80% coverage)
- [ ] CI/CD пайплайн проходит успешно
- [ ] Env переменные настроены и не содержат секретов
- [ ] Docker образ построен и протестирован
- [ ] Логирование настроено (структурированное логирование)
- [ ] Мониторинг и алерты установлены
- [ ] Health check endpoints работают
- [ ] База данных может масштабироваться
- [ ] Graceful shutdown реализован
- [ ] Документация актуальна

---

**Контакты:** По вопросам о тестировании и развёртывании для туристических приложений обращайтесь в наш офис в Дубае, Tecom.
