# VK Платформа: FAQ (Часто задаваемые вопросы)

15 самых частых вопросов по VK-платформе для туристического бизнеса.

---

## 1. Какой токен использовать для публикации в сообществе?

**Community Token** — самый простой и достаточный. Получается в Настройки -> Работа с API -> Создать ключ. Rate limit: 3 req/sec. Не истекает.

Если нужно работать с несколькими сообществами — **Standalone Token** (20 req/sec), получается через OAuth 2.0.

---

## 2. Как ID сообщества передаётся в API?

**owner_id** для сообществ всегда **отрицательный**: `-12345678`.

**group_id** — всегда **положительный**: `12345678` (для методов photos, video, market).

```python
# wall.post — отрицательный owner_id
vk.wall.post(owner_id=-12345678, from_group=1, message='...')

# market.add — положительный group_id (внутри owner_id отрицательный)
vk.market.add(owner_id=-12345678, name='Tour', price=250)

# photos — положительный group_id
upload_server = vk.photos.getWallUploadServer(group_id=12345678)
```

---

## 3. Как создать отложенный пост?

Передать параметр `publish_date` (Unix timestamp) в `wall.post`:

```python
from datetime import datetime, timedelta
future = datetime.now() + timedelta(hours=2)
vk.wall.post(owner_id=-12345678, from_group=1, message='...', publish_date=int(future.timestamp()))
```

Ограничения: от 10 минут до 1 года вперёд.

---

## 4. Как загрузить фото к посту?

Используйте `vk_api.VkUpload` — он автоматизирует 3-шаговый процесс:

```python
upload = vk_api.VkUpload(vk_session)
photo = upload.photo_wall(photos='dubai.jpg', group_id=12345678)
attachment = f"photo{photo[0]['owner_id']}_{photo[0]['id']}"
vk.wall.post(owner_id=-12345678, from_group=1, message='Дубай!', attachments=attachment)
```

Максимум 10 фото в одном посте.

---

## 5. Как опубликовать VK Clips через API?

Клипы загружаются через `video.save` с параметром `is_clip=1`:

```python
clip = vk.video.save(name='Clip', group_id=12345678, is_clip=1)
requests.post(clip['upload_url'], files={'video_file': open('clip.mp4', 'rb')})
```

Требования: вертикальное видео 9:16, до 3 минут, до 1080p.

---

## 6. Как добавить ссылку свайпом в VK Stories?

При получении upload server передайте `link_text` и `link_url`:

```python
server = vk.stories.getPhotoUploadServer(
    add_to_news=1, group_id=12345678,
    link_text='book',
    link_url='https://yoursite.com/booking'
)
```

Значения `link_text`: `more`, `book`, `order`, `enroll`, `fill`, `signup`, `buy`, `ticket`, `write`, `open`, `learn_more`, `view`, `go_to`, `contact`, `watch`, `play`, `install`.

---

## 7. Как продавать экскурсии через VK Market?

1. Включить Market в настройках сообщества
2. Добавить товары через API:

```python
vk.market.add(
    owner_id=-12345678,
    name='Desert Safari',
    description='6ч, трансфер, джипы, BBQ',
    price=250,
    currency=784  # AED
)
```

3. Создать подборки (альбомы) по типам экскурсий
4. Отслеживать заказы через `market.getOrders`

---

## 8. Как настроить VK Donut для сообщества?

1. Настройки -> VK Donut -> Включить
2. Установить уровни подписки (50-2000 руб/мес)
3. Описать привилегии каждого уровня
4. Публиковать эксклюзивные посты:

```python
vk.wall.post(owner_id=-12345678, from_group=1, message='VIP контент', donut_paid_duration=-1)
```

Комиссия: 5% + 2.3% за вывод.

---

## 9. Можно ли использовать execute для ускорения?

Да. `execute` позволяет выполнить до 25 API-вызовов за 1 запрос:

```python
code = """
var results = [];
results.push(API.wall.post({owner_id:-12345678, from_group:1, message:"Пост 1"}));
results.push(API.wall.post({owner_id:-12345678, from_group:1, message:"Пост 2"}));
return results;
"""
vk.execute(code=code)
```

Полезно для массовых операций (публикация, удаление, статистика).

---

## 10. Как получить аналитику сообщества?

`stats.get` — доступна для сообществ с 5000+ участников:

```python
stats = vk.stats.get(group_id=12345678, date_from='2026-02-01', date_to='2026-02-12')
```

Возвращает: посетители, охват, активность (лайки, комменты, репосты).

Для отдельных постов: `stats.getPostReach` (последние 300 записей).

---

## 11. Какие форматы рекламы доступны в VK?

- **Promoted Posts** — продвижение записей из сообщества
- **Stories Ads** — реклама в историях (до 30 сек видео или фото)
- **Carousel** — карусель с несколькими карточками
- **Collages** — формат из нескольких изображений
- **Shops** — карточки товаров в клипах и видео
- **Ретаргетинг** — показ рекламы посетителям сообщества

---

## 12. Как создать VK Mini App для бронирования?

1. Зарегистрировать приложение: https://vk.com/apps?act=manage
2. Тип: Mini App
3. Разработать HTML/JS приложение с VK Bridge
4. VK Bridge даёт доступ к профилю пользователя, VK Pay, геолокации

```javascript
import vkBridge from '@vkontakte/vk-bridge';
vkBridge.send('VKWebAppInit');
const user = await vkBridge.send('VKWebAppGetUserInfo');
```

---

## 13. Как настроить автоматические фильтры комментариев?

```python
vk.groups.edit(
    group_id=12345678,
    obscene_filter=1,
    obscene_stopwords=1,
    obscene_words='спам,левая реклама,конкурент'
)
```

Также можно настроить пре-модерацию комментариев через настройки сообщества.

---

## 14. Как прикрепить несколько разных медиа к посту?

Через параметр `attachments` — через запятую:

```python
attachments = 'photo-123_456,video-123_789,https://yoursite.com'
vk.wall.post(owner_id=-12345678, from_group=1, message='Микс', attachments=attachments)
```

Максимум 10 медиа-объектов. Можно комбинировать фото, видео, ссылки.

---

## 15. Нужен ли сервер для автопостинга?

**Два подхода:**

1. **С сервером:** Python/Node.js + cron/schedule на VPS — полный контроль
2. **Без сервера:** отложенные посты `publish_date` — создать все посты на неделю заранее
3. **No-code:** Make.com / Zapier — визуальная автоматизация без кода

Рекомендация: для 1-2 постов в день достаточно отложенных постов или Make.com.

---

*Версия: 2.0 | Дата: 2026-02-12*
