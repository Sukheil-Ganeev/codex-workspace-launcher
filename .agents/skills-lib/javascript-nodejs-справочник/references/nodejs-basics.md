# Node.js Basics

Node.js — это среда выполнения JavaScript на стороне сервера, построенная на V8 движке Chrome. Этот справочник охватывает фундаментальные концепции, необходимые для эффективной разработки с Node.js.

---

## 1. Node.js Runtime и Event Loop

### Что такое Node.js Runtime?

Node.js Runtime состоит из:
- **V8 Engine** — JavaScript движок от Google для выполнения кода
- **libuv** — асинхронная библиотека ввода-вывода
- **Встроенные модули** — fs, http, path и другие

### Event Loop (Цикл событий)

Event Loop — сердце асинхронности Node.js. Он работает в одном потоке и постоянно проверяет очередь задач:

```javascript
// Event Loop выполняет задачи в таком порядке:
// 1. Synchronous code
// 2. Microtasks (Promise.then(), process.nextTick())
// 3. Timers (setTimeout, setInterval)
// 4. I/O operations
// 5. setImmediate()

console.log('Start'); // Синхронный код

setTimeout(() => {
  console.log('Timer callback'); // Выполнится 3-й
}, 0);

Promise.resolve().then(() => {
  console.log('Promise callback'); // Выполнится 2-й
});

console.log('End'); // Синхронный код (1-й)

// Вывод:
// Start
// End
// Promise callback
// Timer callback
```

### process.nextTick() vs setImmediate()

```javascript
setImmediate(() => console.log('setImmediate'));
process.nextTick(() => console.log('nextTick'));

// Вывод:
// nextTick
// setImmediate

// nextTick имеет ВЫШЕ приоритет и выполняется раньше
```

---

## 2. NPM и package.json

### package.json структура

```json
{
  "name": "my-app",
  "version": "1.0.0",
  "description": "My awesome app",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js",
    "test": "jest",
    "build": "webpack"
  },
  "dependencies": {
    "express": "^4.18.0",
    "dotenv": "^16.0.0"
  },
  "devDependencies": {
    "nodemon": "^2.0.0",
    "jest": "^27.0.0"
  },
  "engines": {
    "node": ">=14.0.0",
    "npm": ">=6.0.0"
  }
}
```

### Версионирование (Semantic Versioning)

```
^4.18.0  → может быть 4.x.x (minor обновления допустимы)
~4.18.0  → может быть 4.18.x (только patch обновления)
4.18.0   → только точная версия
```

### Основные команды

```bash
npm init                    # Создать package.json
npm install                 # Установить все зависимости
npm install express         # Установить пакет
npm install -g nodemon      # Глобально установить
npm uninstall express       # Удалить пакет
npm update                  # Обновить все пакеты
npm list                    # Список установленных пакетов
npm audit                   # Проверить уязвимости
npm audit fix              # Исправить уязвимости
```

---

## 3. Core Modules (Встроенные модули)

### File System (fs) — Работа с файлами

```javascript
const fs = require('fs');
const path = require('path');

// Синхронное чтение (БЛОКИРУЕТ выполнение)
const data = fs.readFileSync('file.txt', 'utf-8');
console.log(data);

// Асинхронное чтение (РЕКОМЕНДУЕТСЯ)
fs.readFile('file.txt', 'utf-8', (err, data) => {
  if (err) {
    console.error('Ошибка:', err);
    return;
  }
  console.log(data);
});

// Асинхронное чтение с Promise (современный подход)
const fs_promises = require('fs').promises;

async function readFile() {
  try {
    const data = await fs_promises.readFile('file.txt', 'utf-8');
    console.log(data);
  } catch (err) {
    console.error('Ошибка:', err);
  }
}

// Запись файла
fs.writeFile('output.txt', 'Hello World', (err) => {
  if (err) throw err;
  console.log('Файл создан!');
});

// Добавление к файлу
fs.appendFile('log.txt', 'New log entry\n', (err) => {
  if (err) throw err;
});

// Проверка существования файла
fs.existsSync('file.txt') ? console.log('Файл существует') : console.log('Не найден');

// Удаление файла
fs.unlink('file.txt', (err) => {
  if (err) throw err;
  console.log('Файл удален');
});

// Список файлов в папке
fs.readdirSync('./') // Синхронно
fs.readdir('./', (err, files) => {
  if (err) throw err;
  console.log(files);
}); // Асинхронно
```

### Path — Работа с путями

```javascript
const path = require('path');

// Объединение путей
path.join('src', 'views', 'index.html'); // src/views/index.html

// Разбор пути
const filePath = '/home/user/project/file.js';
path.dirname(filePath);   // /home/user/project
path.basename(filePath);  // file.js
path.extname(filePath);   // .js

// Получить абсолютный путь
path.resolve('file.txt'); // /current/working/directory/file.txt

// Разнормализованные пути
path.normalize('src//views///index.html'); // src/views/index.html
```

### HTTP — Создание веб-сервера

```javascript
const http = require('http');

const server = http.createServer((req, res) => {
  // req — запрос клиента
  // res — ответ сервера

  res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' });

  if (req.url === '/') {
    res.end('Главная страница');
  } else if (req.url === '/about') {
    res.end('О сайте');
  } else {
    res.writeHead(404);
    res.end('Страница не найдена');
  }
});

server.listen(3000, () => {
  console.log('Сервер запущен на http://localhost:3000');
});
```

### Crypto — Криптография и хеширование

```javascript
const crypto = require('crypto');

// Хеширование пароля (SHA256)
function hashPassword(password) {
  return crypto.createHash('sha256').update(password).digest('hex');
}

console.log(hashPassword('mypassword'));
// Вывод: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

// PBKDF2 — более безопасный способ
const iterations = 100000;
const salt = crypto.randomBytes(32);
const hash = crypto.pbkdf2Sync('mypassword', salt, iterations, 64, 'sha256');

// Генерация случайных данных
crypto.randomBytes(32).toString('hex'); // 64-символная строка

// Создание подписи
const algorithm = 'sha256';
const hmac = crypto.createHmac(algorithm, 'secret-key');
hmac.update('Hello World');
console.log(hmac.digest('hex'));

// Шифрование и дешифрование (AES-256)
function encrypt(text, key) {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', Buffer.alloc(32, key), iv);
  let encrypted = cipher.update(text);
  encrypted = Buffer.concat([encrypted, cipher.final()]);
  return iv.toString('hex') + ':' + encrypted.toString('hex');
}

function decrypt(text, key) {
  const parts = text.split(':');
  const iv = Buffer.from(parts[0], 'hex');
  const encryptedText = Buffer.from(parts[1], 'hex');
  const decipher = crypto.createDecipheriv('aes-256-cbc', Buffer.alloc(32, key), iv);
  let decrypted = decipher.update(encryptedText);
  decrypted = Buffer.concat([decrypted, decipher.final()]);
  return decrypted.toString();
}
```

---

## 4. Environment Variables (Переменные окружения)

### process.env

```javascript
// Получение переменной окружения
const dbHost = process.env.DB_HOST;
const dbPort = process.env.DB_PORT || 5432; // со значением по умолчанию

// Все переменные окружения
console.log(process.env);
```

### .env файл с dotenv

```bash
# .env файл
DB_HOST=localhost
DB_PORT=5432
DB_USER=admin
DB_PASSWORD=secret123
API_KEY=abc123xyz
NODE_ENV=development
```

```javascript
// app.js
require('dotenv').config(); // ОБЯЗАТЕЛЬНО в начале файла!

const dbHost = process.env.DB_HOST;
const dbPort = process.env.DB_PORT;
const apiKey = process.env.API_KEY;

console.log(`Подключение к БД: ${dbHost}:${dbPort}`);
```

### .gitignore

```
node_modules/
.env
.env.local
.env.*.local
dist/
build/
.DS_Store
*.log
```

---

## 5. Process Management (Управление процессом)

### Основные свойства process

```javascript
// Текущая рабочая директория
process.cwd();

// ID процесса
console.log(process.pid);

// Версия Node.js
console.log(process.version);

// Аргументы командной строки
console.log(process.argv); // ['node', 'script.js', 'arg1', 'arg2']

// Операционная система
console.log(process.platform); // 'linux', 'win32', 'darwin'

// Количество ядер CPU
const os = require('os');
console.log(os.cpus().length);
```

### Обработка ошибок и выхода

```javascript
// Обработка необработанных ошибок
process.on('uncaughtException', (err) => {
  console.error('Необработанная ошибка:', err);
  process.exit(1); // Выход с кодом ошибки
});

// Обработка отклоненного Promise
process.on('unhandledRejection', (reason, promise) => {
  console.error('Отклоненное Promise:', reason);
});

// Обработка SIGTERM (корректное завершение)
process.on('SIGTERM', () => {
  console.log('Получен сигнал SIGTERM, завершаю...');
  process.exit(0);
});

// Выход из процесса
process.exit(0); // 0 = успешный выход
process.exit(1); // 1 = ошибка
```

---

## 6. Streams и Buffers

### Buffers — Работа с двоичными данными

```javascript
// Создание Buffer
const buf1 = Buffer.alloc(10); // Выделить 10 байт (заполнены нулями)
const buf2 = Buffer.from('Hello', 'utf-8'); // Из строки

// Запись в Buffer
buf1.write('Hello', 'utf-8');

// Чтение из Buffer
console.log(buf2.toString('utf-8')); // 'Hello'

// Размер
console.log(buf2.length); // 5 (байт)

// Конкатенация
const buf3 = Buffer.concat([buf1, buf2]);
```

### Streams — Потоковая передача данных

```javascript
const fs = require('fs');

// Чтение файла потоком (экономит память)
const readStream = fs.createReadStream('large-file.txt', {
  encoding: 'utf-8',
  highWaterMark: 16 * 1024 // 16KB
});

readStream.on('data', (chunk) => {
  console.log(`Получена порция: ${chunk.length} символов`);
});

readStream.on('end', () => {
  console.log('Файл полностью прочитан');
});

readStream.on('error', (err) => {
  console.error('Ошибка чтения:', err);
});

// Запись потоком
const writeStream = fs.createWriteStream('output.txt');
writeStream.write('Hello World\n');
writeStream.write('Line 2\n');
writeStream.end(); // Завершить запись

writeStream.on('finish', () => {
  console.log('Запись завершена');
});

// Pipe — соединение потоков
fs.createReadStream('input.txt')
  .pipe(fs.createWriteStream('output.txt'));

// Pipe для сжатия файла
const zlib = require('zlib');
fs.createReadStream('input.txt')
  .pipe(zlib.createGzip())
  .pipe(fs.createWriteStream('input.txt.gz'));
```

---

## 7. Best Practices

### Организация проекта

```
project/
├── src/
│   ├── index.js
│   ├── config/
│   │   └── env.js
│   ├── routes/
│   ├── controllers/
│   ├── models/
│   └── utils/
├── tests/
├── .env
├── .env.example
├── .gitignore
├── package.json
└── README.md
```

### Правила разработки

**1. Не блокируйте Event Loop**
```javascript
// ПЛОХО: синхронные операции
fs.readFileSync('large-file.txt');

// ХОРОШО: асинхронные операции
await fs.promises.readFile('large-file.txt');
```

**2. Обработка ошибок**
```javascript
// ПЛОХО: проглатывание ошибок
try {
  await someAsyncFunction();
} catch (err) {
  console.log('Ошибка');
}

// ХОРОШО: логирование и обработка
try {
  await someAsyncFunction();
} catch (err) {
  console.error('Критическая ошибка:', err);
  process.exit(1);
}
```

**3. Используйте async/await**
```javascript
// СТАРЫЙ СТИЛЬ: callback hell
fs.readFile('file1.txt', (err, data1) => {
  fs.readFile('file2.txt', (err, data2) => {
    fs.readFile('file3.txt', (err, data3) => {
      // ...
    });
  });
});

// НОВЫЙ СТИЛЬ: async/await
async function readFiles() {
  try {
    const data1 = await fs.promises.readFile('file1.txt');
    const data2 = await fs.promises.readFile('file2.txt');
    const data3 = await fs.promises.readFile('file3.txt');
  } catch (err) {
    console.error(err);
  }
}
```

**4. Управление памятью**
```javascript
// ПЛОХО: утечка памяти
let largeArray = [];
setInterval(() => {
  largeArray.push(new Array(1000000)); // Растет бесконечно
}, 1000);

// ХОРОШО: очистка
let largeArray = [];
const cleanup = setInterval(() => {
  largeArray = []; // Очистить
}, 60000);

process.on('exit', () => clearInterval(cleanup));
```

**5. Используйте константы**
```javascript
// config/constants.js
module.exports = {
  PORT: process.env.PORT || 3000,
  DB_HOST: process.env.DB_HOST || 'localhost',
  MAX_RETRIES: 3,
  TIMEOUT: 5000
};

// app.js
const { PORT } = require('./config/constants');
```

---

## Заключение

Понимание этих основ критически важно для разработки надежных Node.js приложений. Ключевые моменты:

- Асинхронность и Event Loop — суть Node.js
- Используйте встроенные модули для базовых операций
- Всегда обрабатывайте ошибки
- Оптимизируйте использование памяти
- Следуйте best practices для поддерживаемого кода
