# Публикация контента в Threads API

Детальное руководство по публикации текстовых постов и изображений через Threads API.

---

## Типы контента

Threads API поддерживает:

1. **Текстовые посты** (до 500 символов)
2. **Изображения** (соотношение сторон 9:16 до 1.91:1)
3. **Карусели** (до 20 изображений)
4. **Посты с ссылками** (автоматический превью)

**Не поддерживаются (пока):**
- Видео
- GIF анимации
- Опросы (polls)

---

## Текстовые посты

### Метод 1: Auto-publish (рекомендуется с 2025)

**Одношаговая публикация текста:**

```bash
curl -X POST "https://graph.threads.net/v1.0/THREADS_USER_ID/threads" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Top 5 things to do in Dubai:\n1. Burj Khalifa\n2. Desert Safari\n3. Dubai Marina\n4. Gold Souk\n5. Palm Jumeirah\n\n#Dubai #Travel",
    "auto_publish_text": true
  }'
```

**Ответ:**
```json
{
  "id": "18123456789012345"
}
```

**Преимущества:**
- Один запрос = публикация
- Экономия API квоты
- Мгновенная публикация

**Ограничения:**
- Только для текста (без медиа)
- Нельзя запланировать на будущее

---

### Метод 2: Draft + Publish (устаревший)

```bash
# Шаг 1: Создать draft
curl -X POST "https://graph.threads.net/v1.0/THREADS_USER_ID/threads" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d "text=My text post"

# Ответ: {"id": "CREATION_ID"}

# Шаг 2: Опубликовать
curl -X POST "https://graph.threads.net/v1.0/THREADS_USER_ID/media_publish" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d "creation_id=CREATION_ID"
```

**Когда использовать:** Если нужна задержка между созданием и публикацией (планировщик).

---

## Форматирование текста

### Длина текста

- **Минимум:** 1 символ
- **Максимум:** 500 символов
- **Оптимально:** 300-400 символов (лучшая вовлеченность)

**Подсчет символов:**
```javascript
// Node.js
const text = "Dubai tours 🏜️ #tourism";
const length = [...text].length; // Правильный подсчет с эмодзи
console.log(length); // 24
```

### Переносы строк

Поддерживаются:
```bash
curl -X POST "..." \
  -d '{
    "text": "Line 1\nLine 2\nLine 3",
    "auto_publish_text": true
  }'
```

### Эмодзи

Полная поддержка Unicode эмодзи:
```bash
"text": "🏜️ Desert Safari\n⛵ Yacht Tours\n🕌 Mosque Visit\n🏙️ City Tours"
```

**Рекомендация:** 2-3 эмодзи на пост для визуального разнообразия.

---

## Хештеги и упоминания

### Хештеги

```bash
"text": "Best Dubai tours! #Dubai #Tourism #UAE #Travel #DesertSafari"
```

**Лучшие практики:**
- 3-5 хештегов на пост
- Релевантные хештеги (не спам)
- Сочетание популярных (#Dubai) и нишевых (#DubaiDesertSafari)

### Упоминания (@username)

```bash
"text": "Thanks @traveler_john for the amazing review! 🙏"
```

**Работает автоматически:** API распознает @username и создает ссылку.

---

## Публикация изображений

### Требования к изображениям

| Параметр | Значение |
|----------|----------|
| **Форматы** | JPEG, PNG |
| **Макс. размер** | 8 MB |
| **Мин. разрешение** | 320px (ширина) |
| **Макс. разрешение** | 1440px (ширина) |
| **Соотношение сторон** | От 9:16 (вертикальное) до 1.91:1 (горизонтальное) |

**Рекомендуемые размеры:**
- Квадрат: 1080x1080px
- Портрет: 1080x1350px
- Ландшафт: 1080x566px

---

### Двухшаговый процесс

#### Шаг 1: Создать медиа-контейнер

```bash
curl -X POST "https://graph.threads.net/v1.0/THREADS_USER_ID/threads" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d "image_url=https://example.com/dubai-burj-khalifa.jpg" \
  -d "media_type=IMAGE" \
  -d "text=Iconic Burj Khalifa at sunset 🌆 #Dubai"
```

**Параметры:**
- `image_url` (string) - **публичный** URL изображения (доступен по HTTPS)
- `media_type` (string) - `IMAGE`
- `text` (string, опционально) - подпись к изображению

**Ответ:**
```json
{
  "id": "18098765432109876"
}
```

**Важно:** URL должен быть:
- Публично доступен (без авторизации)
- HTTPS (не HTTP)
- Прямая ссылка на изображение (не HTML страницу)

---

#### Шаг 2: Опубликовать медиа-контейнер

**Подождать завершения обработки (5-30 секунд):**

```bash
# Проверить статус
curl -X GET "https://graph.threads.net/v1.0/CREATION_ID?fields=status_code" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**Возможные статусы:**
- `IN_PROGRESS` - обрабатывается
- `FINISHED` - готово к публикации
- `ERROR` - ошибка обработки

**Опубликовать:**
```bash
curl -X POST "https://graph.threads.net/v1.0/THREADS_USER_ID/media_publish" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d "creation_id=18098765432109876"
```

**Ответ:**
```json
{
  "id": "18123456789012345"
}
```

---

### Пример с ожиданием (Node.js)

```javascript
const axios = require('axios');

const THREADS_API = 'https://graph.threads.net/v1.0';
const ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN';
const USER_ID = 'YOUR_THREADS_USER_ID';

async function publishImagePost(imageUrl, caption) {
  // Шаг 1: Создать медиа-контейнер
  const createResponse = await axios.post(
    `${THREADS_API}/${USER_ID}/threads`,
    {
      image_url: imageUrl,
      media_type: 'IMAGE',
      text: caption
    },
    {
      headers: { 'Authorization': `Bearer ${ACCESS_TOKEN}` }
    }
  );

  const creationId = createResponse.data.id;
  console.log('Media container created:', creationId);

  // Шаг 2: Ждать завершения обработки
  let status = 'IN_PROGRESS';
  while (status === 'IN_PROGRESS') {
    await new Promise(resolve => setTimeout(resolve, 5000)); // Ждать 5 секунд

    const statusResponse = await axios.get(
      `${THREADS_API}/${creationId}?fields=status_code`,
      {
        headers: { 'Authorization': `Bearer ${ACCESS_TOKEN}` }
      }
    );

    status = statusResponse.data.status_code;
    console.log('Status:', status);
  }

  if (status !== 'FINISHED') {
    throw new Error(`Media processing failed: ${status}`);
  }

  // Шаг 3: Опубликовать
  const publishResponse = await axios.post(
    `${THREADS_API}/${USER_ID}/media_publish`,
    { creation_id: creationId },
    {
      headers: { 'Authorization': `Bearer ${ACCESS_TOKEN}` }
    }
  );

  return publishResponse.data;
}

// Использование
publishImagePost(
  'https://example.com/burj-khalifa.jpg',
  'Iconic Burj Khalifa at sunset 🌆 #Dubai'
)
  .then(result => console.log('Published:', result.id))
  .catch(error => console.error('Error:', error.message));
```

---

### Пример на Python

```python
import requests
import time

THREADS_API = 'https://graph.threads.net/v1.0'
ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
USER_ID = 'YOUR_THREADS_USER_ID'

def publish_image_post(image_url, caption):
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}

    # Шаг 1: Создать медиа-контейнер
    create_url = f'{THREADS_API}/{USER_ID}/threads'
    create_data = {
        'image_url': image_url,
        'media_type': 'IMAGE',
        'text': caption
    }
    create_response = requests.post(create_url, data=create_data, headers=headers)
    create_response.raise_for_status()
    creation_id = create_response.json()['id']
    print(f'Media container created: {creation_id}')

    # Шаг 2: Ждать завершения обработки
    status = 'IN_PROGRESS'
    while status == 'IN_PROGRESS':
        time.sleep(5)  # Ждать 5 секунд

        status_url = f'{THREADS_API}/{creation_id}?fields=status_code'
        status_response = requests.get(status_url, headers=headers)
        status_response.raise_for_status()
        status = status_response.json()['status_code']
        print(f'Status: {status}')

    if status != 'FINISHED':
        raise Exception(f'Media processing failed: {status}')

    # Шаг 3: Опубликовать
    publish_url = f'{THREADS_API}/{USER_ID}/media_publish'
    publish_data = {'creation_id': creation_id}
    publish_response = requests.post(publish_url, data=publish_data, headers=headers)
    publish_response.raise_for_status()

    return publish_response.json()

# Использование
result = publish_image_post(
    'https://example.com/burj-khalifa.jpg',
    'Iconic Burj Khalifa at sunset 🌆 #Dubai'
)
print(f"Published: {result['id']}")
```

---

## Карусели (несколько изображений)

### Процесс создания карусели

1. Создать медиа-контейнеры для каждого изображения
2. Дождаться обработки всех изображений
3. Создать карусель с массивом children IDs
4. Опубликовать карусель

### Пример (Node.js)

```javascript
async function publishCarousel(images, caption) {
  // Шаг 1: Создать медиа-контейнеры для каждого изображения
  const childrenIds = [];

  for (const imageUrl of images) {
    const response = await axios.post(
      `${THREADS_API}/${USER_ID}/threads`,
      {
        image_url: imageUrl,
        media_type: 'IMAGE',
        is_carousel_item: true
      },
      {
        headers: { 'Authorization': `Bearer ${ACCESS_TOKEN}` }
      }
    );
    childrenIds.push(response.data.id);
  }

  console.log('Children IDs:', childrenIds);

  // Шаг 2: Ждать обработки всех изображений
  for (const childId of childrenIds) {
    let status = 'IN_PROGRESS';
    while (status === 'IN_PROGRESS') {
      await new Promise(resolve => setTimeout(resolve, 5000));

      const statusResponse = await axios.get(
        `${THREADS_API}/${childId}?fields=status_code`,
        {
          headers: { 'Authorization': `Bearer ${ACCESS_TOKEN}` }
        }
      );
      status = statusResponse.data.status_code;
    }
  }

  // Шаг 3: Создать карусель
  const carouselResponse = await axios.post(
    `${THREADS_API}/${USER_ID}/threads`,
    {
      media_type: 'CAROUSEL',
      children: childrenIds,
      text: caption
    },
    {
      headers: { 'Authorization': `Bearer ${ACCESS_TOKEN}` }
    }
  );

  const carouselId = carouselResponse.data.id;

  // Шаг 4: Опубликовать
  const publishResponse = await axios.post(
    `${THREADS_API}/${USER_ID}/media_publish`,
    { creation_id: carouselId },
    {
      headers: { 'Authorization': `Bearer ${ACCESS_TOKEN}` }
    }
  );

  return publishResponse.data;
}

// Использование
const images = [
  'https://example.com/image1.jpg',
  'https://example.com/image2.jpg',
  'https://example.com/image3.jpg'
];

publishCarousel(images, 'Top 3 Dubai landmarks! 🏙️ #Dubai')
  .then(result => console.log('Carousel published:', result.id))
  .catch(error => console.error('Error:', error.message));
```

---

## Посты с ссылками

### Автоматический превью

Threads автоматически создает preview card для URL в тексте:

```bash
curl -X POST "https://graph.threads.net/v1.0/THREADS_USER_ID/threads" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Check out our latest tours: https://example.com/dubai-tours\n\nBook now and save 20%! 🎉",
    "auto_publish_text": true
  }'
```

**Результат:** Threads автоматически извлечет Open Graph метаданные (title, description, image) и создаст красивую карточку предпросмотра.

**Требования к сайту:**
```html
<meta property="og:title" content="Dubai Tours - Best Excursions" />
<meta property="og:description" content="Explore Dubai with our guided tours" />
<meta property="og:image" content="https://example.com/preview.jpg" />
```

---

## Обработка ошибок

### Типичные ошибки

**1. Изображение недоступно**
```json
{
  "error": {
    "message": "Image URL is not accessible",
    "code": 100
  }
}
```
**Решение:** Убедитесь, что URL:
- Публично доступен
- Использует HTTPS
- Возвращает image/jpeg или image/png MIME type

**2. Неподдерживаемое соотношение сторон**
```json
{
  "error": {
    "message": "Invalid aspect ratio",
    "code": 100
  }
}
```
**Решение:** Обрезать/изменить размер изображения до 9:16 - 1.91:1

**3. Превышен лимит символов**
```json
{
  "error": {
    "message": "Text exceeds maximum length of 500 characters",
    "code": 100
  }
}
```
**Решение:** Сократить текст до 500 символов

---

## Планирование публикаций

Threads API **не поддерживает** нативное планирование. Решения:

### Вариант 1: Собственный планировщик (Node.js)

```javascript
const schedule = require('node-schedule');

// Запланировать на определенное время
const job = schedule.scheduleJob('2026-02-06 14:00:00', async function() {
  await publishTextPost('Daily Dubai tips! ☀️ #Dubai');
  console.log('Post published at scheduled time');
});
```

### Вариант 2: Cron (Linux)

```bash
# Добавить в crontab
# Публикация каждый день в 14:00
0 14 * * * /usr/bin/node /path/to/publish-script.js
```

### Вариант 3: Make.com / Zapier

- Создать сценарий с триггером "Schedule"
- Настроить время публикации
- Подключить Threads API через HTTP request

---

## Лучшие практики

### Оптимизация изображений

**Перед загрузкой:**
```javascript
// Node.js с sharp
const sharp = require('sharp');

await sharp('input.jpg')
  .resize(1080, 1080, { fit: 'cover' })
  .jpeg({ quality: 85 })
  .toFile('output.jpg');
```

**Преимущества:**
- Меньше размер файла = быстрее загрузка
- Оптимальное разрешение для Threads
- Улучшение качества отображения

### Тестирование контента

**Проверка перед публикацией:**
```javascript
function validatePost(text, imageUrl = null) {
  const errors = [];

  // Проверка длины текста
  if ([...text].length > 500) {
    errors.push('Text exceeds 500 characters');
  }

  // Проверка URL (если есть изображение)
  if (imageUrl && !imageUrl.startsWith('https://')) {
    errors.push('Image URL must use HTTPS');
  }

  // Проверка на спам-хештеги
  const hashtagCount = (text.match(/#/g) || []).length;
  if (hashtagCount > 10) {
    errors.push('Too many hashtags (max 10 recommended)');
  }

  return errors.length === 0 ? { valid: true } : { valid: false, errors };
}

// Использование
const validation = validatePost(myText, myImageUrl);
if (!validation.valid) {
  console.error('Validation failed:', validation.errors);
} else {
  await publishPost(myText, myImageUrl);
}
```

### A/B тестирование

**Тестирование времени публикации:**
```javascript
const testTimes = [
  { time: '09:00', posts: [], avgEngagement: 0 },
  { time: '14:00', posts: [], avgEngagement: 0 },
  { time: '20:00', posts: [], avgEngagement: 0 }
];

// После месяца публикаций - проанализировать метрики
// Выбрать лучшее время для вашей аудитории
```

---

## Примеры для туризма ОАЭ

### Пример 1: Анонс тура

```bash
curl -X POST "https://graph.threads.net/v1.0/THREADS_USER_ID/threads" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "🏜️ DESERT SAFARI SPECIAL\n\nWhat is included:\n✅ Hotel pickup & drop-off\n✅ Dune bashing\n✅ Camel riding\n✅ BBQ dinner\n✅ Entertainment shows\n\nPrice: $80/person\nBook now: link in bio\n\n#DubaiTourism #DesertSafari #UAETravel",
    "auto_publish_text": true
  }'
```

### Пример 2: Отзыв клиента (с изображением)

```javascript
// Node.js
await publishImagePost(
  'https://cdn.example.com/customer-review.jpg',
  '⭐⭐⭐⭐⭐ "Best tour experience in Dubai!"\n\n- Sarah M., USA\n\nThank you for choosing us! 🙏\n\n#CustomerReview #DubaiTours #Travel'
);
```

### Пример 3: Совет путешественникам

```bash
"🌡️ DUBAI WEATHER TIP\n\nBest months to visit:\n• November - March (22-30°C)\n\nAvoid:\n• June - August (40-45°C)\n\nPro tip: Book summer tours at 50% discount! 💰\n\n#DubaiTravel #TravelTips #UAE"
```

---

## Полезные ссылки

- [Threads API Documentation](https://developers.facebook.com/docs/threads)
- [Image Specifications](https://developers.facebook.com/docs/threads/posts#image-specifications)
- [Character Encoding Best Practices](https://developers.facebook.com/docs/threads/reference/text-formatting)

---

**Обновлено:** 05 февраля 2026
**Версия:** 1.0.0
