# 12 туристических кейсов для ОАЭ

## Кейс 1: Booking API

**Стек:** PostgreSQL + API Gateway + Cloud Functions
**Время:** 6 часов
**Стоимость:** ~9,000₽/месяц

```javascript
// booking-function.js
const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

module.exports.handler = async (event) => {
    const { httpMethod, body, pathParameters } = event;

    // POST /bookings - создать бронирование
    if (httpMethod === 'POST') {
        const booking = JSON.parse(body);

        const result = await pool.query(`
            INSERT INTO bookings (tour_id, customer_name, customer_email, booking_date, participants, total_amount)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
        `, [booking.tourId, booking.customerName, booking.customerEmail, booking.bookingDate, booking.participants, booking.totalAmount]);

        return { statusCode: 201, body: JSON.stringify(result.rows[0]) };
    }

    // GET /bookings/:id
    if (httpMethod === 'GET' && pathParameters?.id) {
        const result = await pool.query('SELECT * FROM bookings WHERE id = $1', [pathParameters.id]);
        return { statusCode: 200, body: JSON.stringify(result.rows[0]) };
    }

    return { statusCode: 404 };
};
```

---

## Кейс 2: Photo Storage с CDN

**Стек:** Object Storage + CDN + Cloud Function (resize)
**Время:** 4 часа
**Стоимость:** ~1,500₽/месяц

```python
# resize-photo.py
from PIL import Image
import boto3
import io

s3 = boto3.client('s3', endpoint_url='https://storage.yandexcloud.net')

def handler(event, context):
    bucket = event['messages'][0]['details']['bucket_id']
    key = event['messages'][0]['details']['object_id']

    # Download
    obj = s3.get_object(Bucket=bucket, Key=key)
    image = Image.open(io.BytesIO(obj['Body'].read()))

    # Resize
    sizes = {'thumbnail': (300, 300), 'medium': (800, 800), 'large': (1920, 1920)}

    for size_name, dimensions in sizes.items():
        resized = image.copy()
        resized.thumbnail(dimensions)

        buffer = io.BytesIO()
        resized.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)

        new_key = key.replace('original/', f'{size_name}/')
        s3.upload_fileobj(buffer, bucket, new_key)

    return {'statusCode': 200}
```

---

## Кейс 3: AI Telegram бот

**Стек:** Cloud Function + YandexGPT + PostgreSQL
**Время:** 8 часов
**Стоимость:** ~1,000₽/месяц

```javascript
// telegram-bot.js
const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');

const bot = new TelegramBot(process.env.BOT_TOKEN);

module.exports.handler = async (event) => {
    const update = JSON.parse(event.body);

    if (update.message?.text) {
        const chatId = update.message.chat.id;
        const text = update.message.text;

        // Получить туры из БД
        const tours = await getTours();
        const context = tours.map(t => `${t.name}: ${t.description}, ${t.price} AED`).join('\n');

        // YandexGPT
        const response = await axios.post(
            'https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
            {
                modelUri: 'gpt://b1g.../yandexgpt/latest',
                messages: [
                    { role: 'system', content: `Ты консультант туристического агентства в Дубае.\nДоступные туры:\n${context}` },
                    { role: 'user', content: text }
                ]
            },
            { headers: { 'Authorization': `Bearer ${process.env.YC_IAM_TOKEN}` } }
        );

        const answer = response.data.result.alternatives[0].message.content;
        await bot.sendMessage(chatId, answer);
    }

    return { statusCode: 200 };
};
```

---

## Кейс 4: Voice Transcription

**Стек:** Cloud Function + SpeechKit
**Время:** 4 часа
**Стоимость:** ~500₽/месяц

```javascript
// voice-transcription.js
bot.on('voice', async (msg) => {
    const chatId = msg.chat.id;
    const fileId = msg.voice.file_id;

    // Download voice
    const fileUrl = await bot.getFileLink(fileId);
    const audioResponse = await axios.get(fileUrl, { responseType: 'arraybuffer' });

    // Transcribe
    const text = await transcribeAudio(audioResponse.data);

    // Reply
    bot.sendMessage(chatId, `Вы сказали: ${text}`);
});

async function transcribeAudio(audioData) {
    const response = await axios.post(
        'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize',
        audioData,
        {
            headers: {
                'Authorization': `Bearer ${process.env.YC_IAM_TOKEN}`,
                'Content-Type': 'audio/ogg'
            },
            params: { lang: 'ru-RU' }
        }
    );

    return response.data.result;
}
```

---

## Кейс 5: Multi-currency Payments

**Стек:** YDB + Cloud Functions
**Время:** 6 часов
**Стоимость:** ~200₽/месяц

```javascript
// Tracking оплат в AED, USD, RUB, KZT
const payments = {
    bookingId: 123,
    amounts: [
        { currency: 'AED', amount: 250, rate: 1.0 },
        { currency: 'USD', amount: 68, rate: 3.67 },
        { currency: 'RUB', amount: 7500, rate: 0.033 }
    ],
    baseAmount: 250, // AED
    baseCurrency: 'AED'
};

// YDB хранит все валюты и автоматически конвертирует
```

---

## Кейс 6: Analytics Dashboard

**Стек:** ClickHouse + DataLens
**Время:** 8 часов
**Стоимость:** ~17,000₽/месяц

```sql
-- Топ туров по выручке
SELECT
    tour_name,
    COUNT(*) as bookings,
    SUM(amount) as revenue
FROM bookings_analytics
WHERE date >= today() - INTERVAL 30 DAY
GROUP BY tour_name
ORDER BY revenue DESC
LIMIT 10;

-- Конверсия по странам
SELECT
    customer_country,
    COUNT(*) as bookings,
    AVG(amount) as avg_price
FROM bookings_analytics
WHERE date >= today() - INTERVAL 90 DAY
GROUP BY customer_country;
```

---

## Кейс 7: Disaster Recovery

**Стек:** Hystax + automated snapshots
**Время:** 4 часа
**Стоимость:** ~3,000₽/месяц

```bash
# Automated daily snapshots
yc compute snapshot-schedule create \
  --name daily-backup \
  --expression "0 3 * * *" \
  --retention-period 7d
```

---

## Кейс 8: Auto-scaling Web App

**Стек:** Instance Group + Load Balancer
**Время:** 6 часов
**Стоимость:** ~8,000₽/месяц

```yaml
# instance-group.yaml
scale_policy:
  auto_scale:
    min_size: 2
    max_size: 10
    cpu_utilization_target: 70

load_balancer_spec:
  target_group_spec:
    name: web-servers-tg
```

---

## Кейс 9: OCR для документов

**Стек:** Cloud Function + Vision API
**Время:** 4 часа
**Стоимость:** ~300₽/месяц

```python
# passport-ocr.py
def extract_passport_data(image_path):
    text_blocks = recognize_text(image_path)

    # Извлечь поля
    return {
        'name': extract_field(text_blocks, 'name'),
        'passport_number': extract_field(text_blocks, 'passport'),
        'nationality': extract_field(text_blocks, 'nationality')
    }
```

---

## Кейс 10: Real-time Notifications

**Стек:** Message Queue + Cloud Functions
**Время:** 4 часа
**Стоимость:** ~500₽/месяц

```javascript
// Отправка уведомлений при новом бронировании
async function sendNotification(booking) {
    await sqs.sendMessage({
        QueueUrl: QUEUE_URL,
        MessageBody: JSON.stringify({
            type: 'new_booking',
            booking: booking
        })
    });
}
```

---

## Кейс 11: Automated Backups

**Стек:** Cloud Function (timer) + Object Storage
**Время:** 2 часа
**Стоимость:** ~500₽/месяц

```bash
#!/bin/bash
# backup.sh
pg_dump $DATABASE_URL | gzip > backup-$(date +%Y%m%d).sql.gz
aws s3 cp backup-*.sql.gz s3://tourism-backups/ --endpoint-url=https://storage.yandexcloud.net
```

---

## Кейс 12: Full-stack IaC (Terraform)

**Стек:** Terraform
**Время:** 12 часов
**Стоимость:** зависит от ресурсов

```hcl
# main.tf
module "database" {
  source = "./modules/postgresql"
  cluster_name = "tourism-db"
}

module "storage" {
  source = "./modules/s3"
  bucket_name = "tourism-photos"
}

module "functions" {
  source = "./modules/functions"
  function_name = "booking-api"
}
```

---

## Матрица выбора

| Задача | Рекомендованный кейс |
|--------|---------------------|
| REST API | #1 (Booking API) |
| Хранение фото | #2 (Photo Storage) |
| Чат-бот | #3 (AI Telegram) |
| Голосовые сообщения | #4 (Voice Transcription) |
| Мультивалютность | #5 (Multi-currency) |
| Аналитика | #6 (Analytics Dashboard) |
| Backup | #7 (Disaster Recovery) |
| Масштабирование | #8 (Auto-scaling) |
| Обработка документов | #9 (OCR) |
| Push-уведомления | #10 (Notifications) |
| Автоматизация backup | #11 (Automated Backups) |
| Infrastructure as Code | #12 (Terraform) |

---

**См. также:**
- `assets/examples/` - полные примеры кода
- `assets/templates/` - готовые конфигурации
