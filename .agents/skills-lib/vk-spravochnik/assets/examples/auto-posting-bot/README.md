# Auto-Posting Bot для VK

Автоматическая публикация туров из JSON файла в VK-сообщество по расписанию.

## Возможности

- ✅ Чтение данных туров из JSON
- ✅ Автоматическая загрузка фото
- ✅ Публикация по расписанию (schedule)
- ✅ Логирование всех операций
- ✅ Обработка ошибок и retry

## Установка

```bash
# Клонировать директорию
cd auto-posting-bot

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл
cp .env.example .env

# Отредактировать .env (добавить VK_TOKEN и GROUP_ID)
nano .env
```

## Настройка

### 1. Получить VK Access Token

1. Перейти: https://vk.com/editapp?id=YOUR_APP_ID (замените YOUR_APP_ID)
2. Настройки → Токены доступа
3. Создать токен с правами:
   - Управление сообществом
   - Управление постами
   - Фотографии
4. Скопировать токен в .env файл

### 2. Настроить tours_data.json

Отредактировать `tours_data.json` - добавить ваши туры:

```json
{
  "tours": [
    {
      "name": "Desert Safari",
      "description": "Джип-сафари по пустыне...",
      "price": "$80/чел",
      "photo": "https://example.com/safari.jpg",
      "schedule": "10:00"
    }
  ]
}
```

### 3. Настроить config.py

Отредактировать `config.py` - время публикаций, часовой пояс, etc.

## Запуск

### Ручной запуск

```bash
python main.py
```

### Запуск по расписанию (Linux/Mac)

```bash
# Cron: каждый день в 10:00
0 10 * * * /usr/bin/python3 /path/to/auto-posting-bot/main.py >> /var/log/vk_autopost.log 2>&1
```

### Запуск по расписанию (Windows)

Создать задачу в Task Scheduler:

```powershell
schtasks /create /tn "VK AutoPost" /tr "python C:\path\to\auto-posting-bot\main.py" /sc daily /st 10:00
```

## Структура проекта

```
auto-posting-bot/
├── README.md              # Эта документация
├── main.py               # Основной скрипт
├── config.py             # Конфигурация
├── requirements.txt      # Python зависимости
├── .env.example          # Шаблон .env файла
├── tours_data.json       # База туров
└── logs/                 # Логи (создается автоматически)
    └── autopost.log
```

## Примеры использования

### Публикация одного тура

```python
from main import post_tour
import json

with open('tours_data.json') as f:
    data = json.load(f)
    tour = data['tours'][0]

post_tour(tour)
```

### Публикация всех туров

```bash
python main.py --all
```

### Тестовый режим (без публикации)

```bash
python main.py --dry-run
```

## Логирование

Все операции логируются в `logs/autopost.log`:

```
2026-02-05 10:00:01 - INFO - Запуск автопостинга...
2026-02-05 10:00:05 - INFO - Опубликован пост 123: Desert Safari
2026-02-05 10:00:10 - INFO - Опубликован пост 124: Burj Khalifa
2026-02-05 10:00:15 - INFO - Автопостинг завершён: 2/2 успешно
```

## Troubleshooting

### Ошибка: "VK API Error 5: User authorization failed"

**Решение:** Проверьте правильность VK_TOKEN в .env файле.

### Ошибка: "VK API Error 6: Too many requests"

**Решение:** Уменьшите частоту публикаций в config.py или добавьте паузы.

### Ошибка: "Error downloading photo"

**Решение:** Проверьте URL фотографий в tours_data.json (должны быть публично доступны).

## Дополнительно

### Интеграция с Google Sheets

Вместо JSON можно читать данные из Google Sheets:

```bash
pip install gspread oauth2client
```

См. комментарии в `main.py` для примера интеграции.

### Webhook уведомления

Добавить уведомления в Telegram/Discord при публикации:

```python
# В main.py после успешной публикации
import requests
requests.post('https://api.telegram.org/botTOKEN/sendMessage', json={
    'chat_id': YOUR_CHAT_ID,
    'text': f'✅ Опубликован пост: {tour_name}'
})
```

## Лицензия

MIT License - свободное использование для коммерческих целей.

## Поддержка

Вопросы и предложения: info@dubaitours.com
