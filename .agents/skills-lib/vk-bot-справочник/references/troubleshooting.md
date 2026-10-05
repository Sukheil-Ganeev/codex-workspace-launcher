# VK Bot API: Troubleshooting (15 проблем)

## 1. Бот не получает сообщения

**Симптомы:** Бот запущен, но `longpoll.listen()` не выдает событий.

**Решение:**
1. Проверить: Настройки сообщества -> Сообщения -> **Включено**
2. Проверить: Работа с API -> Long Poll API -> **Включено**
3. Проверить: Типы событий -> `message_new` **отмечен**
4. Проверить: Версия API = **5.199** (не ниже 5.131)
5. Убедиться, что используется **Community Token**, а не User Token

```python
# Диагностика: проверить настройки Long Poll
settings = vk.groups.getLongPollSettings(group_id=GROUP_ID)
print(settings)  # Должен показать enabled events
```

## 2. Ошибка "Too many requests per second" (код 6)

**Симптомы:** `ApiError: [6] Too many requests per second`

**Решение:**
```python
import time

def safe_call(method, **kwargs):
    while True:
        try:
            return method(**kwargs)
        except vk_api.exceptions.ApiError as e:
            if e.code == 6:
                time.sleep(0.5)
                continue
            raise
```

Или используйте `execute` для пакетных операций (25 вызовов за 1 запрос).

## 3. Ошибка "Permission to perform this action is denied" (код 7)

**Симптомы:** `ApiError: [7] Permission to perform this action is denied`

**Решение:**
1. Проверить права токена: Работа с API -> Ключи доступа
2. Пересоздать токен с нужными правами (messages, photos, docs)
3. Для `messages.send` нужно право **messages**
4. Для загрузки фото нужно право **photos**

## 4. Ошибка "Can't send messages for users from blacklist" (код 901)

**Симптомы:** Бот не может отправить сообщение конкретному пользователю.

**Причина:** Пользователь заблокировал сообщество или добавил в черный список.

**Решение:**
```python
try:
    vk.messages.send(user_id=uid, message="Текст", random_id=0)
except vk_api.exceptions.ApiError as e:
    if e.code == 901:
        # Пользователь заблокировал — удалить из рассылки
        remove_from_mailing(uid)
```

## 5. Ошибка "Can't send messages to this user due to their privacy settings" (код 902)

**Симптомы:** Бот не может инициировать диалог.

**Причина:** Пользователь не разрешил сообщения от сообщества.

**Решение:**
- Бот может писать **только пользователям, которые первыми написали** боту или нажали "Разрешить сообщения"
- Отслеживайте `message_allow` / `message_deny`
- Нельзя отправить первым — это ограничение VK

## 6. Callback API: "URL-address not working"

**Симптомы:** VK не может подтвердить URL сервера.

**Проверьте:**
1. URL доступен из интернета (не localhost)
2. HTTPS с валидным сертификатом (не self-signed)
3. Сервер возвращает confirmation string (строку, не JSON)
4. Сервер отвечает за **5 секунд** (лимит VK)
5. Content-Type: `text/plain`

```python
# Правильный confirmation
@app.route('/callback', methods=['POST'])
def callback():
    data = request.get_json()
    if data['type'] == 'confirmation':
        return 'abc123def'  # Строка, не JSON!
    return 'ok'
```

## 7. Callback API: "Response waiting time has been exceeded"

**Симптомы:** VK отправляет повторные запросы, бот обрабатывает дубли.

**Причина:** Сервер отвечает дольше 5 секунд.

**Решение:**
1. Вернуть `"ok"` **немедленно**, до обработки
2. Обработку делать в фоновом потоке/задаче

```python
from threading import Thread

@app.route('/callback', methods=['POST'])
def callback():
    data = request.get_json()
    if data['type'] == 'confirmation':
        return CONFIRMATION

    # Фоновая обработка
    Thread(target=process_event, args=(data,)).start()

    return 'ok'  # Мгновенный ответ!
```

## 8. Long Poll: соединение постоянно обрывается

**Симптомы:** `ConnectionError`, `ReadTimeout` каждые несколько минут.

**Решение:**
```python
import time

while True:
    try:
        for event in longpoll.listen():
            handle_event(event)
    except Exception as e:
        print(f"Long Poll error: {e}")
        time.sleep(3)  # Пауза перед reconnect
```

Или используйте vkbottle — встроенный reconnect:
```python
bot = Bot("TOKEN")
bot.run_forever()  # Автоматический reconnect
```

## 9. Клавиатура не отображается

**Симптомы:** Бот отправляет сообщение, но кнопки не видны.

**Проверьте:**
1. `keyboard` передается как **JSON строка**, не dict
2. Максимум кнопок не превышен (10 строк reply / 6 строк inline)
3. Для inline: `"inline": true` в JSON

```python
# Правильно
vk.messages.send(
    user_id=uid,
    message="Текст",
    keyboard=keyboard.get_keyboard(),  # Строка JSON
    random_id=0
)

# Убрать клавиатуру
empty_kb = VkKeyboard()
vk.messages.send(
    user_id=uid,
    message="Клавиатура скрыта",
    keyboard=empty_kb.get_empty_keyboard(),
    random_id=0
)
```

## 10. Карусель не отображается

**Симптомы:** Пользователь видит только текст, без карусели.

**Причины:**
1. Клиент не поддерживает карусели (старое приложение)
2. Неправильная структура JSON
3. `photo_id` некорректный

**Решение:**
```python
# Проверить поддержку перед отправкой
if event.object.client_info.get('carousel'):
    # Отправить карусель
    vk.messages.send(user_id=uid, template=carousel_json, random_id=0)
else:
    # Фоллбэк — текстовый список
    vk.messages.send(user_id=uid, message=text_list, random_id=0)
```

## 11. Загрузка фото возвращает ошибку

**Симптомы:** `photos.saveMessagesPhoto` возвращает ошибку.

**Проверьте:**
1. Файл < 50 МБ, формат JPG/PNG/GIF
2. upload_url используется **один раз** (генерируйте новый для каждого файла)
3. Параметр `files` в POST: `{'photo': ('image.jpg', file_bytes, 'image/jpeg')}`

```python
import requests

upload = vk.photos.getMessagesUploadServer(peer_id=uid)
# upload_url одноразовый!

with open('photo.jpg', 'rb') as f:
    response = requests.post(upload['upload_url'], files={'photo': f}).json()

# Проверить response
if not response.get('photo') or response['photo'] == '[]':
    print("Загрузка не удалась — проверьте формат файла")
else:
    saved = vk.photos.saveMessagesPhoto(**response)[0]
```

## 12. Дублирование обработки сообщений

**Симптомы:** Бот отвечает 2-3 раза на одно сообщение.

**Причины:**
- Callback API: сервер не вернул "ok" вовремя — VK повторил
- Long Poll: запущены несколько экземпляров бота

**Решение:**
```python
# Дедупликация через event_id (Callback API)
processed_events = set()

def process_event(data):
    event_id = data.get('event_id')
    if event_id in processed_events:
        return  # Дубль
    processed_events.add(event_id)
    # Обработка...

    # Очистка старых event_id (каждые 1000)
    if len(processed_events) > 1000:
        processed_events.clear()
```

## 13. Ошибка "Captcha needed" (код 14)

**Симптомы:** `ApiError: [14] Captcha needed`

**Причина:** VK считает активность подозрительной (обычно при массовых операциях).

**Решение:**
1. Уменьшить частоту запросов
2. Использовать `execute` вместо множества одиночных вызовов
3. Для бота сообщества капча появляется крайне редко (это больше проблема user-ботов)
4. Если появляется регулярно — связаться с поддержкой VK

## 14. random_id: ошибка "This message is already sent"

**Симптомы:** Повторная отправка с тем же `random_id` не отправляется.

**Решение:**
```python
import random

# Вариант 1: random_id=0 (VK генерирует сам)
vk.messages.send(user_id=uid, message="Текст", random_id=0)

# Вариант 2: случайное число
vk.messages.send(user_id=uid, message="Текст", random_id=random.getrandbits(64))
```

## 15. Бот работает локально, но не работает на сервере

**Симптомы:** На dev-машине все ок, на сервере — тишина или ошибки.

**Чеклист:**
1. Python/Node.js та же версия что и локально
2. Все зависимости установлены (`pip install -r requirements.txt`)
3. Токен передан через env variable (не хардкод)
4. Firewall не блокирует исходящие запросы к `api.vk.com:443`
5. DNS резолвит `api.vk.com`
6. Для Callback API: порт 443/80 открыт для входящих
7. systemd/pm2 запускает с правильным user/workdir

```bash
# Тест соединения с VK API
curl -s "https://api.vk.com/method/groups.getById?group_id=1&access_token=TOKEN&v=5.199"

# Проверить логи systemd
journalctl -u vkbot -f
```

---

*Часть VK Bot API справочника | Версия 1.0 | 2026-02-12*
