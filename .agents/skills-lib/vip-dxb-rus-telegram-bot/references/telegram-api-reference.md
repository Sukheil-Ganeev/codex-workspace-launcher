# Telegram Bot API Quick Reference

## Архитектура

### Webhook vs Long Polling

| Параметр | Long Polling | Webhook |
|----------|--------------|---------|
| Задержка | До 30 сек | Мгновенно |
| Настройка | Простая | Требует HTTPS |
| Масштабирование | Сложнее | Лучше |
| Для | Разработка | Production |

### Когда использовать Webhook
- Production-окружение
- Высокая нагрузка (1000+ msg/sec)
- Serverless (AWS Lambda, Vercel)

## Клавиатуры

### Reply Keyboard
```json
{
  "keyboard": [
    [{"text": "Кнопка 1"}, {"text": "Кнопка 2"}],
    [{"text": "Кнопка 3"}]
  ],
  "resize_keyboard": true,
  "one_time_keyboard": false
}
```

### Inline Keyboard
```json
{
  "inline_keyboard": [
    [
      {"text": "Действие", "callback_data": "action_123"},
      {"text": "Ссылка", "url": "https://example.com"}
    ]
  ]
}
```

### Callback Data Patterns

**Префиксы (рекомендуется):**
```python
callback_data = "like_post_123"
parts = data.split("_")
action = parts[0]  # "like"
entity_id = parts[2]  # "123"
```

## API Лимиты

### Отправка сообщений

| Тип | Лимит |
|-----|-------|
| Глобальный | ~30 req/sec |
| В один чат | 20 msg/min |
| В группу | 20 msg/min |
| Массовая рассылка | 1 msg/sec |

### Размеры файлов

| Тип | Стандартный API | Local Bot API |
|-----|-----------------|---------------|
| Фото | 10 МБ | 10 МБ |
| Документ | 50 МБ | 2 ГБ |
| Видео | 50 МБ | 2 ГБ |

### Длина текста

| Поле | Максимум |
|------|----------|
| Сообщение | 4096 символов |
| Caption | 1024 символа |
| Callback data | 64 байта |
| Deep link | 64 символа |

## Безопасность токена

### Хранение (по приоритету)

1. **Переменные окружения:**
```bash
export BOT_TOKEN="123456789:ABCdef..."
```

2. **.env файл (в .gitignore!):**
```
BOT_TOKEN=123456789:ABCdef...
```

3. **Secrets Manager** (production)

### При утечке токена

1. **НЕМЕДЛЕННО:** Revoke в @BotFather
2. Получить новый токен
3. Обновить везде
4. Аудит логов
5. Проверить webhook

## Обработка Callback

### Обязательно отвечать!
```python
answer_callback_query(callback_id, text="Готово!", show_alert=False)
```

### Редактирование после callback
```python
edit_message_text(chat_id, message_id, "Новый текст", reply_markup=new_keyboard)
```

### Частые ошибки

| Ошибка | Причина | Решение |
|--------|---------|---------|
| QUERY_ID_INVALID | Ответ >30 сек | Отвечать быстрее |
| MESSAGE_NOT_MODIFIED | Текст не изменился | Проверять перед edit |
| MESSAGE_ID_INVALID | Сообщение удалено | Обрабатывать ошибку |

## Rate Limiter (пример)

```python
class RateLimiter:
    def __init__(self, rps=25, per_chat_rpm=20):
        self.rps = rps
        self.per_chat_rpm = per_chat_rpm
        self.global_times = []
        self.chat_times = defaultdict(list)

    def check_global(self) -> bool:
        now = datetime.now()
        self.global_times = [t for t in self.global_times
                           if t > now - timedelta(seconds=1)]
        if len(self.global_times) >= self.rps:
            return False
        self.global_times.append(now)
        return True
```

## Ссылки

- [Bot API Docs](https://core.telegram.org/bots/api)
- [Web Apps](https://core.telegram.org/bots/webapps)
- Справочник: `D:/Downloads/TELEGRAM_БОТЫ_СПРАВОЧНИК/`
