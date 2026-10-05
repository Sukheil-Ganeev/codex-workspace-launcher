# VK Платформа: Troubleshooting (Решение проблем)

15 типичных проблем при работе с VK API и их решения.

---

## 1. Ошибка 5: "User authorization failed: invalid access_token"

**Причина:** Невалидный или истёкший токен.

**Решение:**
- Community Token не истекает — возможно, был пересоздан/удалён
- User Token с правом `offline` бессрочен — проверьте, не отозвал ли пользователь доступ
- Заново получите токен в настройках сообщества или через OAuth

```python
# Проверка токена
try:
    vk.users.get()
except vk_api.exceptions.ApiError as e:
    if e.code == 5:
        print("Токен невалиден, нужно обновить")
```

---

## 2. Ошибка 6: "Too many requests per second"

**Причина:** Превышен rate limit (3 req/sec для Community Token).

**Решение:**

```python
import time

def safe_call(method, **kwargs):
    for attempt in range(3):
        try:
            return method(**kwargs)
        except vk_api.exceptions.ApiError as e:
            if e.code == 6:
                time.sleep(1)
                continue
            raise
    raise Exception("Rate limit exceeded after 3 retries")
```

Или используйте `execute` для пакетных операций (до 25 вызовов за 1 запрос).

---

## 3. Ошибка 214: "Access to adding post denied"

**Причина:** У токена нет прав на публикацию.

**Решение:**
- Community Token: пересоздать ключ с правом "Управление стеной"
- User Token: запросить scope `wall` при авторизации
- Проверьте, что `from_group=1` при публикации от имени сообщества

---

## 4. Фото не загружается: "Upload error"

**Причина:** Файл слишком большой, неверный формат или битый upload URL.

**Решение:**
- Максимум 50 MB, форматы: JPG, PNG, GIF
- Upload URL одноразовый — используйте сразу после получения
- Оптимизируйте: уменьшите до 2048x2048, quality=85

```python
from PIL import Image

img = Image.open('huge_photo.jpg')
img.thumbnail((2048, 2048))
img.save('optimized.jpg', quality=85)
```

---

## 5. Видео загружено, но "processing" не завершается

**Причина:** Видео на обработке сервером VK (нормально для больших файлов).

**Решение:**
- Подождите 5-15 минут (зависит от размера)
- Проверяйте статус: `vk.video.get(videos=f"{owner_id}_{video_id}")`
- Поле `processing=0` означает готовность
- Максимальный размер: 5 GB, до 1 часа

---

## 6. VK Market: "Access denied" при добавлении товара

**Причина:** Маркет не включён в сообществе или нет прав.

**Решение:**
1. Настройки сообщества -> Разделы -> Товары -> Включить
2. Указать валюту и контактное лицо
3. Токен должен иметь право `market`
4. Для User Token: запросить scope `market` при OAuth

---

## 7. Stories не публикуются: "No access"

**Причина:** Истории доступны только сообществам с 5000+ подписчиков.

**Решение:**
- Если менее 5000 подписчиков — Stories через API недоступны
- Альтернатива: публикуйте Stories вручную через приложение VK
- Наращивайте аудиторию через Clips, Market и рекламу

---

## 8. stats.get возвращает пустые данные

**Причина:** Статистика доступна только для сообществ с 5000+ участников.

**Решение:**
- Для малых сообществ: используйте `wall.get` + считайте лайки/комменты вручную
- Альтернатива: VK рекламный кабинет показывает базовую аналитику для любого сообщества

```python
# Ручной подсчёт engagement
posts = vk.wall.get(owner_id=-12345678, count=10)
for post in posts['items']:
    likes = post.get('likes', {}).get('count', 0)
    comments = post.get('comments', {}).get('count', 0)
    reposts = post.get('reposts', {}).get('count', 0)
    print(f"Post {post['id']}: {likes}L {comments}C {reposts}R")
```

---

## 9. Отложенный пост не публикуется

**Причина:** `publish_date` должен быть Unix timestamp в секундах, минимум через 10 минут.

**Решение:**

```python
from datetime import datetime, timedelta

# Правильно: timestamp в секундах
future = datetime.now() + timedelta(hours=1)
timestamp = int(future.timestamp())  # 1739000000

# Неправильно: миллисекунды
# timestamp = int(future.timestamp() * 1000)  # ОШИБКА!
```

Если пост создан, но не опубликован — проверьте `wall.get` с `filter=postponed`.

---

## 10. Ошибка 100: "One of the parameters specified was missing or invalid"

**Причина:** Пропущен обязательный параметр или неверный формат.

**Решение:**
- Всегда передавайте `v=5.199`
- `owner_id` для сообществ — отрицательный
- `group_id` для upload серверов — положительный
- Проверьте документацию метода: https://dev.vk.com/ru/method

---

## 11. Клавиатура бота не отображается (для интеграции с Market)

**Проблема:** Хотя боты вынесены в отдельный справочник, Market-уведомления могут требовать ответов.

**Решение:** Для уведомлений о заказах Market используйте Callback API событие `market_order_new`, а ответы отправляйте через бот-справочник.

---

## 12. VK Donut: "Donut is not available"

**Причина:** VK Donut не настроен для сообщества.

**Решение:**
1. Настройки -> VK Donut -> Включить
2. Настроить хотя бы один уровень подписки
3. Привязать карту для вывода средств
4. Для API: использовать `donut.isDonor`, `donut.getSubscribers`

---

## 13. Кириллица в запросах curl отображается неправильно

**Причина:** Проблема кодировки UTF-8 в shell.

**Решение:**

```bash
# Используйте URL-encoding
curl -X POST "https://api.vk.com/method/wall.post" \
  --data-urlencode "message=Экскурсия по Дубаю!" \
  -d "owner_id=-12345678" \
  -d "from_group=1" \
  -d "access_token=TOKEN" \
  -d "v=5.199"
```

Или используйте Python/Node.js вместо curl.

---

## 14. execute: "Runtime error occurred during code invocation"

**Причина:** Ошибка в VKScript коде внутри execute.

**Решение:**
- VKScript похож на JavaScript, но это не JS
- Нет `let/const` — только `var`
- Нет `for...of` — только `while` с индексом
- Максимум 25 API вызовов

```python
# Правильный VKScript
code = """
var i = 0;
var results = [];
while (i < 3) {
    results.push(API.wall.post({owner_id: -12345678, from_group: 1, message: "Пост " + i}));
    i = i + 1;
}
return results;
"""
```

---

## 15. API работает, но данные не обновляются в приложении VK

**Причина:** Кэширование VK (CDN кэш для медиа, кэш ленты).

**Решение:**
- Подождите 1-5 минут — кэш обновится автоматически
- Для фото: VK кэширует thumbnails, полноразмерные доступны сразу
- Для видео: обработка занимает время (5-15 мин)
- Для постов: проверьте через API (`wall.get`) — если ответ содержит пост, значит он опубликован

---

## Полезные ссылки

- **Коды ошибок:** https://dev.vk.com/ru/reference/errors
- **Методы API:** https://dev.vk.com/ru/method
- **Сообщество разработчиков:** https://vk.com/apiclub
- **Бот-вопросы:** см. `vk-bot-справочник/references/troubleshooting.md`

---

*Версия: 2.0 | Дата: 2026-02-12*
