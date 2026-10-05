# Troubleshooting — Max Bot API

## Проблемы с аутентификацией

### 401 Unauthorized на все запросы
**Причина:** Токен передаётся через query parameter (устарело).
**Решение:** Передавайте токен только в заголовке `Authorization`:
```bash
# НЕПРАВИЛЬНО
curl "https://platform-api.max.ru/me?access_token=YOUR_TOKEN"

# ПРАВИЛЬНО
curl "https://platform-api.max.ru/me" -H "Authorization: YOUR_TOKEN"
```

### Токен перестал работать
**Причины:**
- Токен перегенерирован через @MasterBot (старый аннулирован)
- Бот удалён
**Решение:** Получите новый токен через @MasterBot.

---

## Проблемы с доменом

### Connection refused / DNS error на botapi.max.ru
**Причина:** Старый домен `botapi.max.ru` больше не поддерживается.
**Решение:** Замените на `platform-api.max.ru`:
```
# УСТАРЕЛО
https://botapi.max.ru/me

# АКТУАЛЬНО
https://platform-api.max.ru/me
```

### Connection refused на botapi.tamtam.chat
**Причина:** TamTam-домен может быть отключён/перенаправлен.
**Решение:** Используйте `platform-api.max.ru` — актуальный домен Max.

---

## Проблемы с сообщениями

### 400 Bad Request при отправке сообщения с медиа
**Причина:** Файл ещё не обработан на сервере Max.
**Решение:** Подождите 1-2 секунды после upload и повторите:
```python
import time

# После загрузки файла
upload_token = upload_file(photo_path)
time.sleep(2)  # Дать серверу время на обработку
send_message_with_attachment(chat_id, upload_token)
```

### Сообщение не доставляется (нет ошибки, но пользователь не видит)
**Причины:**
- Неверный `chat_id`
- Бот не в чате с пользователем
- Пользователь заблокировал бота
**Решение:** Проверьте `chat_id` через `GET /chats`. Убедитесь, что пользователь начал диалог с ботом (событие `bot_started`).

### Текст обрезается
**Причина:** Лимит 4000 символов.
**Решение:** Разбейте длинное сообщение на несколько.

---

## Проблемы с клавиатурами

### Клавиатура не отображается
**Причины:**
- Неверная структура JSON (тип `inline_keyboard`)
- Превышен лимит кнопок (макс. 210)
**Решение:** Проверьте структуру:
```json
{
  "type": "inline_keyboard",
  "payload": {
    "buttons": [
      [{"type": "callback", "text": "Кнопка", "payload": "btn1"}]
    ]
  }
}
```

### Callback не приходит при нажатии кнопки
**Причины:**
- Бот не слушает обновления (Long Polling остановлен)
- Фильтр типов событий не включает `message_callback`
**Решение:**
```bash
# Убедитесь что запрашиваете все нужные типы
GET /updates?types=message_created,message_callback&timeout=30
```

### Кнопка link не работает
**Причина:** URL без протокола.
**Решение:** Всегда указывайте полный URL с `https://`:
```json
{"type": "link", "text": "Сайт", "url": "https://example.com"}
```

---

## Проблемы с Webhook

### Webhook не получает обновления
**Причины:**
1. URL не HTTPS
2. Сервер не возвращает 200 OK
3. SSL-сертификат невалидный (кроме самоподписанных)
4. Firewall блокирует входящие от Max
**Решение:**
```bash
# Проверьте подписку
curl -X GET "https://platform-api.max.ru/subscriptions" \
  -H "Authorization: YOUR_TOKEN"

# Переподпишитесь
curl -X POST "https://platform-api.max.ru/subscriptions" \
  -H "Authorization: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-server.com/webhook/max"}'
```

### Webhook и Long Polling конфликтуют
**Причина:** Может быть активен только один режим.
**Решение:** Удалите webhook для возврата к Long Polling:
```bash
curl -X DELETE "https://platform-api.max.ru/subscriptions" \
  -H "Authorization: YOUR_TOKEN"
```

---

## Проблемы с Rate Limits

### 429 Too Many Requests
**Причина:** Превышен лимит 30 RPS.
**Решение:** Реализуйте exponential backoff:
```python
import time

def safe_request(method, url, **kwargs):
    for attempt in range(5):
        resp = requests.request(method, url, **kwargs)
        if resp.status_code == 429:
            wait = 2 ** attempt
            time.sleep(wait)
            continue
        return resp
    raise Exception("Rate limit exceeded after retries")
```

### Массовая рассылка — как не превысить лимит?
**Решение:** Отправляйте с задержкой:
```python
import time

for user in users:
    send_message(user["chat_id"], text)
    time.sleep(0.04)  # ~25 сообщений в секунду (запас от 30 RPS)
```

---

## Проблемы с загрузкой файлов

### Upload URL истёк
**Причина:** Upload URL имеет ограниченное время жизни.
**Решение:** Запрашивайте новый URL непосредственно перед загрузкой, не кешируйте.

### Большой файл не загружается
**Лимиты:**
- Фото: 50 MB
- Видео: 2 GB
- Аудио/файлы: 100 MB
**Решение:** Сжимайте перед отправкой или используйте ссылку.

---

## Общие рекомендации

1. **Логируйте все запросы и ответы** — облегчает отладку
2. **Используйте GET /me** для проверки токена и связности
3. **Храните marker** — для Long Polling, чтобы не получать дубликаты
4. **Обрабатывайте 5xx ошибки** — серверные ошибки Max (повтор через 5 сек)
5. **Тестируйте на реальном устройстве** — некоторые attachment отображаются по-разному на мобильной и десктопной версиях Max
