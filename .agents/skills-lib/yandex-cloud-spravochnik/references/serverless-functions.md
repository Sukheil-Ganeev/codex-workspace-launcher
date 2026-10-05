# Cloud Functions: Serverless Computing

## Обзор

**Cloud Functions** - serverless платформа для выполнения кода без управления серверами.

**Преимущества:**
- Pay-per-use (платишь за вызовы и compute time)
- Auto-scaling (от 0 до тысяч инстансов)
- Managed infrastructure
- Built-in logging и monitoring
- Free tier: 1M invocations/month

**Когда использовать:**
- API endpoints
- Event-driven обработка (webhooks, triggers)
- Scheduled tasks (cron jobs)
- Обработка файлов (resize images, convert video)

---

## Поддерживаемые runtime

| Runtime | Версии | Use case |
|---------|--------|----------|
| Node.js | 18, 20 | REST API, webhooks, integrations |
| Python | 3.11, 3.12 | Data processing, ML, automation |
| Go | 1.21 | High-performance, low latency |
| Java | 11, 17 | Enterprise apps, Spring Boot |
| .NET Core | 3.1, 6.0 | C# apps, .NET ecosystem |
| PHP | 8.2 | Legacy systems, WordPress |
| Bash | 5.1 | Scripts, automation |

---

## Создание функции

### Node.js example

```javascript
// index.js
module.exports.handler = async (event, context) => {
    const { httpMethod, body, queryStringParameters } = event;

    // GET /tours
    if (httpMethod === 'GET') {
        return {
            statusCode: 200,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tours: [
                    { id: 1, name: 'Desert Safari', price: 250 },
                    { id: 2, name: 'City Tour', price: 150 }
                ]
            })
        };
    }

    // POST /bookings
    if (httpMethod === 'POST') {
        const booking = JSON.parse(body);
        // Save to database...

        return {
            statusCode: 201,
            body: JSON.stringify({ message: 'Booking created', booking })
        };
    }

    return { statusCode: 404, body: 'Not Found' };
};
```

```bash
# Deploy
yc serverless function create --name tourism-api

yc serverless function version create \
  --function-name tourism-api \
  --runtime nodejs18 \
  --entrypoint index.handler \
  --memory 256m \
  --execution-timeout 5s \
  --source-path .
```

### Python example

```python
# index.py
import json
import psycopg2
import os

def handler(event, context):
    # Подключение к БД
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cursor = conn.cursor()

    # Query
    cursor.execute("SELECT * FROM tours WHERE active = true")
    tours = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        'statusCode': 200,
        'body': json.dumps({
            'tours': [
                {'id': row[0], 'name': row[1], 'price': float(row[2])}
                for row in tours
            ]
        })
    }
```

```bash
# requirements.txt
psycopg2-binary==2.9.9

# Deploy
yc serverless function version create \
  --function-name tourism-api \
  --runtime python312 \
  --entrypoint index.handler \
  --memory 256m \
  --execution-timeout 5s \
  --source-path . \
  --environment DATABASE_URL=postgresql://...
```

---

## Triggers (триггеры)

### HTTP Trigger

```bash
# Сделать функцию публичной
yc serverless function allow-unauthenticated-invoke tourism-api

# Получить URL
FUNCTION_URL=$(yc serverless function get tourism-api --format json | jq -r '.http_invoke_url')

# Test
curl $FUNCTION_URL
```

### Timer Trigger (cron)

```bash
# Запускать каждый день в 3:00 UTC
yc serverless trigger create timer \
  --name daily-backup \
  --cron-expression "0 3 * * *" \
  --invoke-function-name backup-function \
  --invoke-function-service-account-id $SA_ID
```

**Cron format:** `минуты часы день месяц день_недели`

Примеры:
- `0 3 * * *` - каждый день в 3:00
- `0 */6 * * *` - каждые 6 часов
- `0 0 * * 0` - каждое воскресенье в полночь

### Message Queue Trigger

```bash
# Создать очередь
yc message-queue queue create tourism-queue

# Trigger для обработки сообщений
yc serverless trigger create message-queue \
  --name process-bookings \
  --queue-id $QUEUE_ID \
  --invoke-function-name process-booking \
  --invoke-function-service-account-id $SA_ID \
  --batch-size 10
```

### Object Storage Trigger

```bash
# Trigger при загрузке файлов в bucket
yc serverless trigger create object-storage \
  --name process-photos \
  --bucket-id tourism-photos \
  --events create-object \
  --invoke-function-name resize-photo \
  --invoke-function-service-account-id $SA_ID
```

---

## Environment Variables и Secrets

```bash
# Deploy с environment variables
yc serverless function version create \
  --function-name tourism-api \
  --runtime nodejs18 \
  --entrypoint index.handler \
  --memory 256m \
  --execution-timeout 5s \
  --source-path . \
  --environment DATABASE_URL=postgresql://... \
  --environment API_KEY=secret123 \
  --environment NODE_ENV=production
```

**В коде:**

```javascript
// Node.js
const dbUrl = process.env.DATABASE_URL;
const apiKey = process.env.API_KEY;
```

```python
# Python
import os
db_url = os.environ['DATABASE_URL']
api_key = os.environ['API_KEY']
```

---

## Туристические use cases

### Use Case 1: Telegram бот

```javascript
// telegram-bot.js
const TelegramBot = require('node-telegram-bot-api');

module.exports.handler = async (event) => {
    const bot = new TelegramBot(process.env.BOT_TOKEN);
    const update = JSON.parse(event.body);

    if (update.message) {
        const chatId = update.message.chat.id;
        const text = update.message.text;

        if (text === '/start') {
            await bot.sendMessage(chatId, 'Welcome! Choose a tour:');
        }

        if (text === '/tours') {
            // Fetch from database
            const tours = await getTours();
            const message = tours.map(t => `${t.name} - ${t.price} AED`).join('\n');
            await bot.sendMessage(chatId, message);
        }
    }

    return { statusCode: 200, body: 'OK' };
};
```

### Use Case 2: Photo resize

```python
# resize-photo.py
import boto3
from PIL import Image
import io
import os

s3 = boto3.client('s3', endpoint_url='https://storage.yandexcloud.net')

def handler(event, context):
    # Event от Object Storage trigger
    bucket = event['messages'][0]['details']['bucket_id']
    key = event['messages'][0]['details']['object_id']

    # Download original
    response = s3.get_object(Bucket=bucket, Key=key)
    image = Image.open(io.BytesIO(response['Body'].read()))

    # Resize
    image.thumbnail((800, 800))

    # Upload thumbnail
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=85)
    buffer.seek(0)

    thumbnail_key = key.replace('original/', 'thumbnails/')
    s3.upload_fileobj(buffer, bucket, thumbnail_key)

    return {'statusCode': 200, 'body': f'Resized: {thumbnail_key}'}
```

### Use Case 3: Daily report

```javascript
// daily-report.js (Timer trigger)
const nodemailer = require('nodemailer');
const { Pool } = require('pg');

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

module.exports.handler = async () => {
    // Query bookings
    const result = await pool.query(`
        SELECT COUNT(*), SUM(total_amount)
        FROM bookings
        WHERE booking_date = CURRENT_DATE
    `);

    const [count, revenue] = result.rows[0];

    // Send email
    const transporter = nodemailer.createTransport(process.env.SMTP_URL);

    await transporter.sendMail({
        from: 'reports@tourism.com',
        to: 'manager@tourism.com',
        subject: `Daily Report - ${new Date().toISOString().split('T')[0]}`,
        text: `Bookings: ${count}\nRevenue: ${revenue} AED`
    });

    return { statusCode: 200 };
};
```

---

## Лимиты и ограничения

| Параметр | Значение |
|----------|----------|
| Max memory | 4GB |
| Max execution time | 10 минут |
| Max payload | 3.5MB |
| Max environment variables | 4KB |
| Cold start | ~100-500ms |

---

## Pricing (2026)

**Free tier (каждый месяц):**
- 1,000,000 invocations
- 10 GB-часов compute time

**Paid:**
- Invocations: 1.28₽ за 1M
- Compute: 104₽ за 1 GB-час

**Пример (100k invocations, 256MB, avg 1s):**
- Invocations: 100k × 1.28₽ / 1M = 0.13₽
- Compute: 100k × 1s × 0.25GB / 3600 = 6.94 GB-час × 104₽ = 721₽
- **Итого: ~721₽/месяц**

---

## Best Practices

1. **Переиспользуйте connections** (DB, HTTP clients) вне handler
2. **Используйте environment variables** для конфигурации
3. **Логируйте через console.log** (автоматически в Cloud Logging)
4. **Обрабатывайте ошибки** (иначе function will retry)
5. **Оптимизируйте cold start** (минимизируйте dependencies)

---

**См. также:**
- `api-gateway-guide.md` - API Gateway для маршрутизации
- `assets/examples/ai-chatbot-telegram/` - полный пример Telegram бота
