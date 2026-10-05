# Auto Publish Text - Новинка 2025

Подробное руководство по использованию параметра `auto_publish_text` для одношаговой публикации текстовых постов в Threads.

---

## Что изменилось

### До июля 2025 года (двухшаговый процесс)

Публикация любого контента требовала два API запроса:

```bash
# Шаг 1: Создать draft
POST /threads

# Шаг 2: Опубликовать draft
POST /threads/{id}/publish
```

**Проблемы:**
- 2 API запроса = двойная квота
- Задержка между созданием и публикацией
- Дополнительная обработка ошибок
- Усложнение кода

---

### С июля 2025 года (одношаговая публикация)

Meta представила параметр `auto_publish_text` для **текстовых постов**:

```bash
# Один запрос = создание + публикация
POST /threads?auto_publish_text=true
```

**Преимущества:**
- ✅ 1 API запрос вместо 2
- ✅ Экономия квоты на 50%
- ✅ Мгновенная публикация
- ✅ Упрощение кода
- ✅ Меньше точек отказа

---

## Технические детали

### Синтаксис

```bash
POST https://graph.threads.net/v1.0/{threads_user_id}/threads
```

**Параметры:**
- `text` (string, обязательный) - текст поста
- `auto_publish_text` (boolean, обязательный) - `true` для автопубликации
- `reply_to_id` (string, опционально) - ID поста для ответа

**Важно:** Параметр работает **только для текстовых постов** (без изображений/видео).

---

### Примеры на разных языках

#### Bash (curl)

```bash
curl -X POST "https://graph.threads.net/v1.0/17841400123456789/threads" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Just booked an amazing Dubai tour! 🏜️ Best experience ever. #Dubai #Travel",
    "auto_publish_text": true
  }'
```

**Ответ:**
```json
{
  "id": "18123456789012345"
}
```

---

#### Node.js

```javascript
const axios = require('axios');

const THREADS_API = 'https://graph.threads.net/v1.0';
const ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN';
const USER_ID = 'YOUR_THREADS_USER_ID';

async function publishTextPost(text) {
  try {
    const response = await axios.post(
      `${THREADS_API}/${USER_ID}/threads`,
      {
        text: text,
        auto_publish_text: true
      },
      {
        headers: {
          'Authorization': `Bearer ${ACCESS_TOKEN}`,
          'Content-Type': 'application/json'
        }
      }
    );

    console.log('Post published successfully!');
    console.log('Post ID:', response.data.id);
    return response.data;

  } catch (error) {
    console.error('Error publishing post:', error.response.data);
    throw error;
  }
}

// Использование
publishTextPost('Top 5 things to do in Dubai! 🌟 #DubaiTourism')
  .then(result => console.log('Success:', result))
  .catch(err => console.error('Failed:', err));
```

---

#### Python

```python
import requests

THREADS_API = 'https://graph.threads.net/v1.0'
ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
USER_ID = 'YOUR_THREADS_USER_ID'

def publish_text_post(text):
    url = f'{THREADS_API}/{USER_ID}/threads'
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        'text': text,
        'auto_publish_text': True
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        print(f"Post published successfully!")
        print(f"Post ID: {result['id']}")
        return result

    except requests.exceptions.HTTPError as error:
        print(f"Error publishing post: {error.response.json()}")
        raise

# Использование
publish_text_post('Top 5 things to do in Dubai! 🌟 #DubaiTourism')
```

---

#### PHP

```php
<?php

$threadsApi = 'https://graph.threads.net/v1.0';
$accessToken = 'YOUR_ACCESS_TOKEN';
$userId = 'YOUR_THREADS_USER_ID';

function publishTextPost($text) {
    global $threadsApi, $accessToken, $userId;

    $url = "$threadsApi/$userId/threads";
    $data = [
        'text' => $text,
        'auto_publish_text' => true
    ];

    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Authorization: Bearer ' . $accessToken,
        'Content-Type: application/json'
    ]);

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($httpCode >= 400) {
        echo "Error publishing post: $response\n";
        return null;
    }

    $result = json_decode($response, true);
    echo "Post published successfully!\n";
    echo "Post ID: {$result['id']}\n";
    return $result;
}

// Использование
publishTextPost('Top 5 things to do in Dubai! 🌟 #DubaiTourism');

?>
```

---

## Сравнение: старый vs новый способ

### Старый способ (двухшаговый)

```javascript
// Шаг 1: Создать draft
const createResponse = await axios.post(
  `${THREADS_API}/${USER_ID}/threads`,
  { text: 'My post' },
  { headers: { 'Authorization': `Bearer ${TOKEN}` } }
);

const creationId = createResponse.data.id;

// Шаг 2: Опубликовать
const publishResponse = await axios.post(
  `${THREADS_API}/${USER_ID}/media_publish`,
  { creation_id: creationId },
  { headers: { 'Authorization': `Bearer ${TOKEN}` } }
);

console.log('Published:', publishResponse.data.id);
```

**Метрики:**
- API запросы: 2
- Время выполнения: ~1-2 секунды
- Точки отказа: 2 (любой запрос может упасть)

---

### Новый способ (одношаговый)

```javascript
// Один запрос = создание + публикация
const response = await axios.post(
  `${THREADS_API}/${USER_ID}/threads`,
  {
    text: 'My post',
    auto_publish_text: true
  },
  {
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'Content-Type': 'application/json'
    }
  }
);

console.log('Published:', response.data.id);
```

**Метрики:**
- API запросы: 1
- Время выполнения: ~0.5-1 секунда
- Точки отказа: 1

**Экономия:** 50% API квоты + быстрее + проще код

---

## Ограничения auto_publish_text

### Работает только для текста

✅ **Поддерживается:**
- Чистый текст
- Текст с эмодзи
- Текст с хештегами
- Текст с упоминаниями (@username)
- Текст с URL (автоматический превью)
- Ответы на другие посты (reply_to_id)

❌ **НЕ поддерживается:**
- Изображения (image_url)
- Карусели (media_type: CAROUSEL)
- Видео (пока нет API для видео в Threads)

---

### Пример с изображением (двухшаговый процесс все еще нужен)

```javascript
// Для медиа-постов используйте старый способ

// Шаг 1: Создать медиа-контейнер
const createResponse = await axios.post(
  `${THREADS_API}/${USER_ID}/threads`,
  {
    image_url: 'https://example.com/image.jpg',
    media_type: 'IMAGE',
    text: 'My caption'
  },
  { headers: { 'Authorization': `Bearer ${TOKEN}` } }
);

// Шаг 2: Ждать обработки
await waitForProcessing(createResponse.data.id);

// Шаг 3: Опубликовать
const publishResponse = await axios.post(
  `${THREADS_API}/${USER_ID}/media_publish`,
  { creation_id: createResponse.data.id },
  { headers: { 'Authorization': `Bearer ${TOKEN}` } }
);
```

---

## Практические примеры для туризма ОАЭ

### Пример 1: Ежедневный совет

```javascript
// Автоматическая ежедневная публикация совета
const dailyTips = [
  '🌡️ Best time to visit Dubai: November-March (22-30°C)',
  '💰 Book summer tours for 50% discount!',
  '🕌 Dress modestly when visiting mosques',
  '🚕 Use Careem/Uber for affordable transport',
  '☀️ Apply sunscreen every 2 hours in summer'
];

const today = new Date().getDay();
const tip = dailyTips[today % dailyTips.length];

await publishTextPost(`Daily Dubai Tip:\n\n${tip}\n\n#DubaiTips #Travel`);
```

---

### Пример 2: Быстрый анонс акции

```javascript
async function announcePromotion(tourName, discount, validUntil) {
  const text = `
🎉 SPECIAL OFFER 🎉

${tourName}
${discount}% OFF!

Valid until: ${validUntil}

Book now: link in bio

#DubaiTours #Promotion #Travel
  `.trim();

  return await publishTextPost(text);
}

// Использование
announcePromotion('Desert Safari', 20, 'Feb 15, 2026');
```

---

### Пример 3: Автоответ на отзывы

```javascript
async function thankCustomer(customerName, tourName) {
  const text = `
⭐ Thank you ${customerName}!

We're thrilled you enjoyed our ${tourName}! 🙏

Your feedback means the world to us.

#CustomerLove #DubaiTours
  `.trim();

  return await publishTextPost(text);
}

// Использование (триггер от CRM или webhook)
thankCustomer('@sarah_travels', 'Desert Safari');
```

---

## Обработка ошибок

### Типичные ошибки

**1. Превышен лимит символов (500)**

```javascript
async function publishTextPost(text) {
  // Проверка длины перед отправкой
  if ([...text].length > 500) {
    throw new Error(`Text too long: ${[...text].length} characters (max 500)`);
  }

  // ... публикация
}
```

**2. Невалидный токен**

```javascript
try {
  await publishTextPost('My text');
} catch (error) {
  if (error.response?.data?.error?.code === 190) {
    console.error('Invalid token - please refresh access token');
    // Автоматическое обновление токена
    await refreshAccessToken();
    // Повтор публикации
    await publishTextPost('My text');
  }
}
```

**3. Rate limit exceeded**

```javascript
async function publishWithRetry(text, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await publishTextPost(text);
    } catch (error) {
      if (error.response?.data?.error?.code === 4) {
        // Rate limit - ждем с exponential backoff
        const delay = Math.pow(2, i) * 60000; // 1min, 2min, 4min
        console.log(`Rate limit hit. Waiting ${delay / 1000}s...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      } else {
        throw error;
      }
    }
  }
  throw new Error('Max retries exceeded');
}
```

---

## Best Practices

### 1. Валидация перед публикацией

```javascript
function validateTextPost(text) {
  const errors = [];

  // Проверка длины
  const length = [...text].length;
  if (length === 0) {
    errors.push('Text cannot be empty');
  }
  if (length > 500) {
    errors.push(`Text too long: ${length}/500 characters`);
  }

  // Проверка на спам-хештеги
  const hashtagCount = (text.match(/#/g) || []).length;
  if (hashtagCount > 10) {
    errors.push(`Too many hashtags: ${hashtagCount} (recommended max 10)`);
  }

  // Проверка на дублирующиеся хештеги
  const hashtags = text.match(/#\w+/g) || [];
  const uniqueHashtags = new Set(hashtags.map(h => h.toLowerCase()));
  if (hashtags.length !== uniqueHashtags.size) {
    errors.push('Duplicate hashtags found');
  }

  return {
    valid: errors.length === 0,
    errors: errors,
    warnings: []
  };
}

// Использование
const validation = validateTextPost(myText);
if (!validation.valid) {
  console.error('Validation failed:', validation.errors);
} else {
  await publishTextPost(myText);
}
```

---

### 2. Кэширование последних постов (избежать дубликатов)

```javascript
const recentPosts = new Set();

async function publishUniquePost(text) {
  // Проверка на дубликат
  const textHash = require('crypto')
    .createHash('md5')
    .update(text)
    .digest('hex');

  if (recentPosts.has(textHash)) {
    throw new Error('This post was recently published');
  }

  // Публикация
  const result = await publishTextPost(text);

  // Добавить в кэш (хранить последние 100)
  recentPosts.add(textHash);
  if (recentPosts.size > 100) {
    const firstItem = recentPosts.values().next().value;
    recentPosts.delete(firstItem);
  }

  return result;
}
```

---

### 3. Логирование и мониторинг

```javascript
async function publishTextPostWithLogging(text) {
  const startTime = Date.now();

  try {
    const result = await publishTextPost(text);

    // Логирование успешной публикации
    console.log({
      timestamp: new Date().toISOString(),
      action: 'publish_text',
      status: 'success',
      post_id: result.id,
      text_length: [...text].length,
      duration_ms: Date.now() - startTime
    });

    return result;

  } catch (error) {
    // Логирование ошибки
    console.error({
      timestamp: new Date().toISOString(),
      action: 'publish_text',
      status: 'error',
      error_code: error.response?.data?.error?.code,
      error_message: error.response?.data?.error?.message,
      text_preview: text.substring(0, 50),
      duration_ms: Date.now() - startTime
    });

    throw error;
  }
}
```

---

## Интеграция с планировщиком

### Пример: Публикация по расписанию

```javascript
const schedule = require('node-schedule');

// Запланировать посты на неделю
const scheduledPosts = [
  { time: '2026-02-06 09:00', text: 'Monday tip: Best beaches in Dubai 🏖️' },
  { time: '2026-02-07 14:00', text: 'Tuesday special: 20% off yacht tours! ⛵' },
  { time: '2026-02-08 20:00', text: 'Wednesday wisdom: Top 5 restaurants 🍽️' }
];

scheduledPosts.forEach(post => {
  schedule.scheduleJob(post.time, async function() {
    try {
      await publishTextPost(post.text);
      console.log(`Published scheduled post: ${post.text.substring(0, 30)}...`);
    } catch (error) {
      console.error('Scheduled post failed:', error.message);
    }
  });
});

console.log(`Scheduled ${scheduledPosts.length} posts`);
```

---

## Миграция с двухшагового процесса

### Было (старый код)

```javascript
async function oldPublish(text) {
  const create = await axios.post(`${API}/${USER_ID}/threads`, { text });
  const publish = await axios.post(`${API}/${USER_ID}/media_publish`, {
    creation_id: create.data.id
  });
  return publish.data;
}
```

### Стало (новый код)

```javascript
async function newPublish(text) {
  const response = await axios.post(
    `${API}/${USER_ID}/threads`,
    { text, auto_publish_text: true },
    { headers: { 'Content-Type': 'application/json' } }
  );
  return response.data;
}
```

**Изменения:**
- Убрали второй запрос
- Добавили `auto_publish_text: true`
- Добавили `Content-Type: application/json` заголовок
- 50% меньше кода!

---

## Часто задаваемые вопросы

### Q: Можно ли использовать для изображений?
**A:** Нет, `auto_publish_text` работает только для текстовых постов. Для изображений используйте двухшаговый процесс.

### Q: Работает ли с ответами (replies)?
**A:** Да! Добавьте `reply_to_id` параметр:
```javascript
{
  text: 'Thank you!',
  auto_publish_text: true,
  reply_to_id: 'THREAD_ID'
}
```

### Q: Можно ли запланировать публикацию на будущее?
**A:** API не поддерживает нативное планирование. Используйте собственный планировщик (cron, node-schedule) или Make.com.

### Q: Как откатить публикацию?
**A:** Используйте DELETE endpoint:
```bash
curl -X DELETE "https://graph.threads.net/v1.0/THREAD_ID" \
  -H "Authorization: Bearer TOKEN"
```

### Q: Отличается ли ID в ответе от старого способа?
**A:** Нет, формат ID идентичен. Это обычный Thread ID, который можно использовать для получения insights, удаления и т.д.

---

## Полезные ссылки

- [Threads API Release Notes (July 2025)](https://developers.facebook.com/docs/threads/release-notes)
- [Auto Publish Parameter Documentation](https://developers.facebook.com/docs/threads/posts#auto-publish)
- [Migration Guide](https://developers.facebook.com/docs/threads/migration/auto-publish)

---

**Обновлено:** 05 февраля 2026
**Версия:** 1.0.0
**Статус:** Производственная функция (stable)
