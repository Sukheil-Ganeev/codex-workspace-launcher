# Auto-Posting Example: Threads Scheduled Publishing

Автоматическая публикация контента в Threads по расписанию.

## Возможности

- Автопостинг по расписанию (node-cron)
- Поддержка текста и изображений
- Retry логика при ошибках
- Logging всех операций
- Чтение контента из JSON файла

## Установка

```bash
npm install
```

## Настройка

1. Скопировать `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```

2. Заполнить переменные окружения в `.env`:
   ```
   ACCESS_TOKEN=your_threads_access_token
   IG_USER_ID=your_instagram_user_id
   ```

3. Подготовить контент в `content/posts.json`

## Запуск

```bash
# Запуск автопостинга
node main.js

# Тест одного поста
node test-post.js
```

## Структура контента

Файл `content/posts.json`:

```json
[
  {
    "id": "post1",
    "schedule": "0 9 * * *",
    "text": "Good morning Dubai! ☀️",
    "imageUrl": null,
    "posted": false
  },
  {
    "id": "post2",
    "schedule": "0 14 * * *",
    "text": "Desert Safari Adventure 🏜️",
    "imageUrl": "https://example.com/desert.jpg",
    "posted": false
  }
]
```

## Schedule format (cron)

```
* * * * *
│ │ │ │ │
│ │ │ │ └─ День недели (0-7, Sunday = 0 или 7)
│ │ │ └─── Месяц (1-12)
│ │ └───── День месяца (1-31)
│ └─────── Час (0-23)
└───────── Минута (0-59)
```

Примеры:
- `0 9 * * *` - каждый день в 9:00
- `0 14 * * 1-5` - каждый будний день в 14:00
- `0 */4 * * *` - каждые 4 часа
- `0 20 * * 0` - каждое воскресенье в 20:00

## Логирование

Logs сохраняются в `logs/autoposter.log`

## Production deployment

### PM2 (рекомендуется)

```bash
npm install -g pm2

# Запуск
pm2 start main.js --name threads-autoposter

# Автозапуск при перезагрузке
pm2 startup
pm2 save
```

### systemd (Linux)

Создать файл `/etc/systemd/system/threads-autoposter.service`:

```ini
[Unit]
Description=Threads Auto Poster
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/auto-posting
ExecStart=/usr/bin/node main.js
Restart=always

[Install]
WantedBy=multi-user.target
```

Активировать:
```bash
sudo systemctl enable threads-autoposter
sudo systemctl start threads-autoposter
```

## Troubleshooting

### Ошибка: Invalid Access Token
- Проверьте `.env` файл
- Обновите токен (срок 60 дней)

### Посты не публикуются
- Проверьте schedule в `posts.json` (cron format)
- Проверьте логи: `tail -f logs/autoposter.log`

### Image URL errors
- URL должен быть публичный HTTPS
- Изображение должно быть доступно без авторизации
