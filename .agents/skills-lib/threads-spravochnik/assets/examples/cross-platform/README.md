# Cross-Platform Example: Instagram + Threads Simultaneous Publishing

Одновременная публикация контента в Instagram и Threads с адаптацией для каждой платформы.

## Возможности

- Единая точка входа для публикации
- Автоматическая адаптация контента:
  - Instagram: короткий caption + много хештегов
  - Threads: детальное описание + меньше хештегов
- Error handling для каждой платформы независимо
- REST API endpoints для триггера из внешних систем
- Webhook endpoint для Make.com/Zapier

## Установка

```bash
npm install
```

## Настройка

1. Скопировать `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```

2. Заполнить credentials в `.env`:
   ```
   ACCESS_TOKEN=your_access_token
   IG_USER_ID=your_ig_user_id
   PORT=3000
   WEBHOOK_SECRET=your_webhook_secret
   ```

## Запуск

```bash
# Development
npm run dev

# Production
npm start
```

Сервер запустится на порту 3000 (по умолчанию).

## API Endpoints

### POST /api/cross-post

Публикация контента на обе платформы.

**Request:**
```json
{
  "title": "Your post title",
  "description": "Detailed description",
  "imageUrl": "https://example.com/image.jpg",
  "hashtags": ["Dubai", "Tourism", "UAE"]
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "instagram": {
      "success": true,
      "postId": "123456"
    },
    "threads": {
      "success": true,
      "postId": "789012"
    }
  }
}
```

### POST /api/publish/instagram

Публикация только в Instagram.

### POST /api/publish/threads

Публикация только в Threads.

### POST /webhook

Webhook endpoint для триггера из Make.com.

**Headers:**
```
X-Webhook-Secret: your_webhook_secret
```

**Request:**
```json
{
  "event": "booking_confirmed",
  "data": {
    "customer": "John Doe",
    "tour": "Desert Safari",
    "date": "2026-02-10"
  }
}
```

## Примеры использования

### curl

```bash
# Cross-post to both platforms
curl -X POST http://localhost:3000/api/cross-post \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Desert Safari Dubai 🏜️",
    "description": "Experience amazing adventure!",
    "imageUrl": "https://example.com/safari.jpg",
    "hashtags": ["Dubai", "Safari", "UAE"]
  }'
```

### JavaScript

```javascript
const axios = require('axios');

const content = {
  title: 'Dubai Marina Yacht Tour',
  description: 'Luxury yachting experience...',
  imageUrl: 'https://example.com/yacht.jpg',
  hashtags: ['DubaiMarina', 'Yacht', 'Luxury']
};

axios.post('http://localhost:3000/api/cross-post', content)
  .then(response => {
    console.log('Published:', response.data);
  })
  .catch(error => {
    console.error('Error:', error.response.data);
  });
```

### Python

```python
import requests

content = {
    'title': 'Burj Khalifa Tour',
    'description': 'Visit the tallest building...',
    'imageUrl': 'https://example.com/burj.jpg',
    'hashtags': ['BurjKhalifa', 'Dubai', 'UAE']
}

response = requests.post(
    'http://localhost:3000/api/cross-post',
    json=content
)

print('Published:', response.json())
```

## Интеграция с Make.com

1. Создать Webhook в Make.com scenario
2. Настроить endpoint: `POST http://your-server.com/webhook`
3. Добавить header: `X-Webhook-Secret: your_secret`
4. Payload:
   ```json
   {
     "event": "new_post",
     "data": {
       "title": "{{title}}",
       "description": "{{description}}",
       "imageUrl": "{{imageUrl}}",
       "hashtags": ["tag1", "tag2"]
     }
   }
   ```

## Production Deployment

### PM2

```bash
npm install -g pm2

# Запуск
pm2 start app.js --name cross-platform-api

# Автозапуск
pm2 startup
pm2 save

# Мониторинг
pm2 monit
```

### Docker

```bash
# Build
docker build -t cross-platform-api .

# Run
docker run -d -p 3000:3000 --env-file .env cross-platform-api
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Troubleshooting

### Port already in use
```bash
# Изменить PORT в .env
PORT=3001
```

### Webhook not working
- Проверьте `X-Webhook-Secret` header
- Убедитесь что endpoint публично доступен

### Images not posting
- URL должен быть публичный HTTPS
- Изображение < 8MB
