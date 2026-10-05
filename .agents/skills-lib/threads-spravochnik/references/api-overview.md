# Threads API - Обзор эндпоинтов и методов

Полная документация по всем доступным API эндпоинтам Threads.

---

## Базовый URL

```
https://graph.threads.net/v1.0/
```

**Аутентификация:** Bearer Token (OAuth 2.0 через Instagram)

---

## Основные эндпоинты

### 1. Управление контентом

#### POST /threads
**Назначение:** Создание нового поста (текст, изображение, карусель)

**Параметры:**
- `text` (string) - текст поста (до 500 символов)
- `image_url` (string) - URL изображения (опционально)
- `media_type` (string) - тип медиа: `TEXT`, `IMAGE`, `CAROUSEL`
- `auto_publish_text` (boolean) - автопубликация текста (новинка 2025)
- `children` (array) - для каруселей (массив media IDs)

**Пример (текст с авто-публикацией):**
```bash
curl -X POST "https://graph.threads.net/v1.0/THREADS_USER_ID/threads" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Visiting Dubai? Check out our top 5 desert safari tours! 🏜️ #Dubai",
    "auto_publish_text": true
  }'
```

**Ответ:**
```json
{
  "id": "18123456789012345"
}
```

**Пример (изображение, двухшаговый процесс):**
```bash
# Шаг 1: Создать медиа-контейнер
curl -X POST "https://graph.threads.net/v1.0/THREADS_USER_ID/threads" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d "image_url=https://example.com/burj-khalifa.jpg" \
  -d "text=Iconic Burj Khalifa at sunset 🌆" \
  -d "media_type=IMAGE"

# Ответ: {"id": "CREATION_ID"}

# Шаг 2: Опубликовать (см. POST /threads/{id}/publish)
```

---

#### POST /threads/{id}/publish
**Назначение:** Публикация созданного draft (для медиа-постов)

**Параметры:**
- `creation_id` (string) - ID из предыдущего шага

**Пример:**
```bash
curl -X POST "https://graph.threads.net/v1.0/THREADS_USER_ID/media_publish" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d "creation_id=CREATION_ID"
```

**Ответ:**
```json
{
  "id": "18987654321098765"
}
```

**Важно:** Используется только для медиа-постов. Текстовые посты с `auto_publish_text: true` публикуются сразу.

---

#### GET /threads/{id}
**Назначение:** Получение информации о конкретном посте

**Параметры:**
- `fields` (string) - список полей через запятую

**Доступные поля:**
- `id` - ID поста
- `text` - текст поста
- `media_type` - тип медиа
- `media_url` - URL медиа (если есть)
- `permalink` - постоянная ссылка
- `timestamp` - дата/время публикации
- `username` - автор поста
- `is_quote_post` - является ли цитатой

**Пример:**
```bash
curl -X GET \
  "https://graph.threads.net/v1.0/THREAD_ID?fields=id,text,media_url,permalink,timestamp" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**Ответ:**
```json
{
  "id": "18123456789012345",
  "text": "Amazing desert safari experience! 🏜️",
  "media_url": "https://...",
  "permalink": "https://threads.net/@username/post/...",
  "timestamp": "2026-02-05T14:30:00+0000"
}
```

---

#### DELETE /threads/{id}
**Назначение:** Удаление поста

**Пример:**
```bash
curl -X DELETE "https://graph.threads.net/v1.0/THREAD_ID" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**Ответ:**
```json
{
  "success": true
}
```

---

### 2. Управление профилем

#### GET /me
**Назначение:** Получение информации о текущем пользователе

**Параметры:**
- `fields` (string) - список полей

**Доступные поля:**
- `id` - Threads User ID
- `username` - имя пользователя
- `threads_profile_picture_url` - аватар
- `threads_biography` - биография

**Пример:**
```bash
curl -X GET \
  "https://graph.threads.net/v1.0/me?fields=id,username,threads_biography" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**Ответ:**
```json
{
  "id": "17841400123456789",
  "username": "dubai_tours_official",
  "threads_biography": "Best Dubai tours & excursions 🏜️ DM for bookings"
}
```

---

#### GET /{threads_user_id}/threads
**Назначение:** Получение списка постов пользователя

**Параметры:**
- `fields` (string) - поля для каждого поста
- `limit` (integer) - количество постов (по умолчанию 25, макс 100)
- `since` (timestamp) - посты после этой даты
- `until` (timestamp) - посты до этой даты

**Пример:**
```bash
curl -X GET \
  "https://graph.threads.net/v1.0/THREADS_USER_ID/threads?fields=id,text,timestamp&limit=10" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**Ответ:**
```json
{
  "data": [
    {
      "id": "18123456789012345",
      "text": "Check out our new yacht tours! ⛵",
      "timestamp": "2026-02-05T10:00:00+0000"
    },
    {
      "id": "18123456789012344",
      "text": "5 hidden gems in Dubai you must visit 🌟",
      "timestamp": "2026-02-04T14:30:00+0000"
    }
  ],
  "paging": {
    "next": "https://graph.threads.net/v1.0/..."
  }
}
```

---

### 3. Аналитика (Insights)

#### GET /threads/{id}/insights
**Назначение:** Получение метрик конкретного поста

**Параметры:**
- `metric` (string) - список метрик через запятую

**Доступные метрики:**
- `views` - просмотры
- `likes` - лайки
- `replies` - ответы (комментарии)
- `reposts` - репосты
- `quotes` - цитаты

**Пример:**
```bash
curl -X GET \
  "https://graph.threads.net/v1.0/THREAD_ID/insights?metric=views,likes,replies" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**Ответ:**
```json
{
  "data": [
    {
      "name": "views",
      "period": "lifetime",
      "values": [{"value": 2580}],
      "title": "Views",
      "description": "Total number of times the thread was viewed",
      "id": "THREAD_ID/insights/views/lifetime"
    },
    {
      "name": "likes",
      "period": "lifetime",
      "values": [{"value": 184}],
      "title": "Likes",
      "description": "Total number of likes",
      "id": "THREAD_ID/insights/likes/lifetime"
    },
    {
      "name": "replies",
      "period": "lifetime",
      "values": [{"value": 23}],
      "title": "Replies",
      "description": "Total number of replies",
      "id": "THREAD_ID/insights/replies/lifetime"
    }
  ]
}
```

---

#### GET /{threads_user_id}/threads_insights
**Назначение:** Метрики профиля (аггрегированные данные)

**Параметры:**
- `metric` (string) - метрики через запятую
- `since` (timestamp) - начало периода
- `until` (timestamp) - конец периода

**Доступные метрики:**
- `views` - общие просмотры
- `likes` - общие лайки
- `replies` - общие комментарии
- `followers_count` - количество подписчиков (на конец периода)
- `follower_demographics` - демография (возраст, пол, страна)

**Пример:**
```bash
curl -X GET \
  "https://graph.threads.net/v1.0/THREADS_USER_ID/threads_insights?metric=views,likes,followers_count&since=2026-02-01&until=2026-02-05" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

---

### 4. Управление ответами (Replies)

#### GET /threads/{id}/replies
**Назначение:** Получение ответов на пост

**Параметры:**
- `fields` (string) - поля
- `limit` (integer) - количество

**Пример:**
```bash
curl -X GET \
  "https://graph.threads.net/v1.0/THREAD_ID/replies?fields=id,text,username,timestamp&limit=20" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**Ответ:**
```json
{
  "data": [
    {
      "id": "18123456789012346",
      "text": "Great tour! Highly recommend 👍",
      "username": "traveler_jane",
      "timestamp": "2026-02-05T11:15:00+0000"
    }
  ]
}
```

---

#### POST /threads/{id}/replies
**Назначение:** Ответить на пост (создать reply)

**Параметры:**
- `text` (string) - текст ответа
- `reply_to_id` (string) - ID поста, на который отвечаем

**Пример:**
```bash
curl -X POST "https://graph.threads.net/v1.0/THREADS_USER_ID/threads" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d "text=Thank you for your feedback! 🙏" \
  -d "reply_to_id=THREAD_ID"
```

---

## Authentication через Instagram Graph API

### Процесс получения токена

1. **Получить Authorization Code**

```
https://api.instagram.com/oauth/authorize
  ?client_id=YOUR_APP_ID
  &redirect_uri=YOUR_REDIRECT_URI
  &scope=threads_basic,threads_content_publish,threads_manage_insights
  &response_type=code
```

2. **Обменять code на short-lived token**

```bash
curl -X POST https://api.instagram.com/oauth/access_token \
  -F client_id=YOUR_APP_ID \
  -F client_secret=YOUR_APP_SECRET \
  -F grant_type=authorization_code \
  -F redirect_uri=YOUR_REDIRECT_URI \
  -F code=AUTHORIZATION_CODE
```

3. **Обменять на long-lived token (60 дней)**

```bash
curl -X GET "https://graph.instagram.com/access_token?grant_type=ig_exchange_token&client_secret=YOUR_APP_SECRET&access_token=SHORT_LIVED_TOKEN"
```

4. **Обновить long-lived token (каждые 50-55 дней)**

```bash
curl -X GET "https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=LONG_LIVED_TOKEN"
```

---

## Коды ошибок

### Основные HTTP коды

| Код | Значение | Действие |
|-----|----------|----------|
| 200 | Успешно | - |
| 400 | Неверный запрос | Проверить параметры |
| 401 | Не авторизован | Обновить токен |
| 403 | Доступ запрещен | Проверить permissions |
| 404 | Не найдено | Проверить ID ресурса |
| 429 | Превышен лимит | Подождать, повторить с backoff |
| 500 | Ошибка сервера | Повторить через несколько секунд |

### Типичные ошибки API

**Invalid OAuth 2.0 Access Token**
```json
{
  "error": {
    "message": "Invalid OAuth 2.0 Access Token",
    "type": "OAuthException",
    "code": 190
  }
}
```
**Решение:** Обновить токен через refresh endpoint

**Rate limit exceeded**
```json
{
  "error": {
    "message": "Application request limit reached",
    "type": "OAuthException",
    "code": 4
  }
}
```
**Решение:** Подождать 1 час или до сброса лимита

**Invalid parameter**
```json
{
  "error": {
    "message": "Invalid value for 'text' parameter",
    "type": "InvalidParameterException",
    "code": 100
  }
}
```
**Решение:** Проверить формат и длину параметров

---

## Rate Limits - детальный обзор

### Публикация

- **250 постов / 24 часа** на аккаунт
- Сброс в полночь UTC
- Включает как текстовые, так и медиа-посты

### API запросы

- Зависят от репутации Instagram App
- Базовый уровень: ~200 запросов/час
- Shared quota с Instagram Graph API
- Заголовок `X-App-Usage` показывает текущее использование

**Пример заголовка:**
```
X-App-Usage: {"call_count":45,"total_cputime":25,"total_time":12}
```

### Лучшие практики

1. **Кэширование:**
   - Профильная информация: обновлять раз в час
   - Метрики: обновлять раз в 15 минут

2. **Batch requests:**
   - Группировать запросы insights для нескольких постов

3. **Exponential backoff:**
   ```javascript
   async function retryWithBackoff(fn, maxRetries = 3) {
     for (let i = 0; i < maxRetries; i++) {
       try {
         return await fn();
       } catch (error) {
         if (error.code === 429) {
           const delay = Math.pow(2, i) * 1000; // 1s, 2s, 4s
           await new Promise(resolve => setTimeout(resolve, delay));
         } else {
           throw error;
         }
       }
     }
   }
   ```

---

## Webhooks (в разработке)

**Статус:** Threads API пока не поддерживает webhooks для real-time уведомлений.

**Альтернативы:**
- Polling с интервалом (раз в 5-15 минут)
- Использование сторонних сервисов (Make.com, Zapier)

**Ожидается в 2026:** Поддержка webhooks для уведомлений о:
- Новых комментариях
- Упоминаниях (@mentions)
- Прямых сообщениях (DM)

---

## Примеры на разных языках

### Node.js

```javascript
const axios = require('axios');

const THREADS_API = 'https://graph.threads.net/v1.0';
const ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN';
const USER_ID = 'YOUR_THREADS_USER_ID';

async function publishTextPost(text) {
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
  return response.data;
}

// Использование
publishTextPost('Amazing Dubai experience! 🏜️')
  .then(result => console.log('Posted:', result.id))
  .catch(error => console.error('Error:', error.response.data));
```

### Python

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

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

# Использование
result = publish_text_post('Amazing Dubai experience! 🏜️')
print(f"Posted: {result['id']}")
```

### PHP

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
    curl_close($ch);

    return json_decode($response, true);
}

// Использование
$result = publishTextPost('Amazing Dubai experience! 🏜️');
echo "Posted: " . $result['id'];
?>
```

---

## Полезные ссылки

- [Официальная документация Threads API](https://developers.facebook.com/docs/threads)
- [Postman Collection](https://www.postman.com/meta/threads/collection/dht3nzz/threads-api)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
- [Meta for Developers](https://developers.facebook.com)

---

**Обновлено:** 05 февраля 2026
**Версия:** 1.0.0
