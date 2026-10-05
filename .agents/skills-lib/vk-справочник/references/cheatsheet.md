# VK Платформа: Cheatsheet (Шпаргалка)

Быстрый справочник по всем методам VK API для работы с платформой.

---

## Базовый запрос

```
POST https://api.vk.com/method/{METHOD}
  access_token=TOKEN
  v=5.199
  ...params
```

---

## Аутентификация

| Токен | Rate Limit | Получение |
|-------|-----------|-----------|
| Community | 3 req/sec | Настройки -> Работа с API |
| User | 5 req/sec | OAuth Implicit Flow |
| Standalone | 20 req/sec | OAuth Authorization Code |
| Service | 20 req/sec | Настройки приложения |

**OAuth URL:**
```
https://oauth.vk.com/authorize?client_id=APP_ID&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=wall,photos,video,groups,market,stories,ads,stats,offline&response_type=token&v=5.199
```

---

## Стена (wall.*)

| Метод | Описание | Ключевые параметры |
|-------|----------|--------------------|
| `wall.post` | Создать запись | owner_id, message, attachments, publish_date |
| `wall.edit` | Редактировать | owner_id, post_id, message |
| `wall.delete` | Удалить | owner_id, post_id |
| `wall.get` | Получить записи | owner_id, count, offset, filter |
| `wall.getById` | По ID | posts (формат: {owner}_{id}) |
| `wall.pin` | Закрепить | owner_id, post_id |
| `wall.unpin` | Открепить | owner_id, post_id |
| `wall.repost` | Репост | object (wall{owner}_{id}) |
| `wall.createComment` | Комментарий | owner_id, post_id, message |
| `wall.getComments` | Комментарии | owner_id, post_id, count |
| `wall.deleteComment` | Удалить коммент | owner_id, comment_id |

**Быстрый пост:**
```python
vk.wall.post(owner_id=-GROUP, from_group=1, message='Text', attachments='photo-X_Y')
```

---

## Фото (photos.*)

| Метод | Описание |
|-------|----------|
| `photos.getWallUploadServer` | Upload URL для фото стены |
| `photos.saveWallPhoto` | Сохранить загруженное фото |
| `photos.get` | Получить фото альбома |

**Быстрая загрузка:**
```python
upload = vk_api.VkUpload(vk_session)
photo = upload.photo_wall(photos='file.jpg', group_id=GROUP)
att = f"photo{photo[0]['owner_id']}_{photo[0]['id']}"
```

---

## Видео (video.*)

| Метод | Описание |
|-------|----------|
| `video.save` | Получить upload URL (+ video_id) |
| `video.get` | Получить видео (проверка processing) |
| `video.delete` | Удалить видео |
| `video.edit` | Редактировать |
| `video.startStreaming` | Начать трансляцию (Live) |

**Загрузка видео:**
```python
data = vk.video.save(name='Title', group_id=GROUP)
requests.post(data['upload_url'], files={'video_file': open('file.mp4','rb')})
att = f"video{data['owner_id']}_{data['video_id']}"
```

**Загрузка клипа:**
```python
data = vk.video.save(name='Clip', group_id=GROUP, is_clip=1)
requests.post(data['upload_url'], files={'video_file': open('clip.mp4','rb')})
```

---

## Stories (stories.*)

| Метод | Описание |
|-------|----------|
| `stories.getPhotoUploadServer` | Upload URL для фото-истории |
| `stories.getVideoUploadServer` | Upload URL для видео-истории |
| `stories.save` | Сохранить историю |
| `stories.get` | Получить истории |
| `stories.delete` | Удалить историю |

**Публикация с ссылкой:**
```python
server = vk.stories.getPhotoUploadServer(
    add_to_news=1, group_id=GROUP,
    link_text='book', link_url='https://site.com'
)
resp = requests.post(server['upload_url'], files={'file': open('story.jpg','rb')})
vk.stories.save(upload_results=resp.text)
```

**link_text значения:** `more`, `book`, `order`, `enroll`, `fill`, `signup`, `buy`, `ticket`, `write`, `open`, `learn_more`, `view`, `go_to`, `contact`, `watch`, `play`, `install`

---

## Market (market.*)

| Метод | Описание |
|-------|----------|
| `market.add` | Добавить товар |
| `market.edit` | Редактировать |
| `market.delete` | Удалить |
| `market.get` | Список товаров |
| `market.getById` | Товар по ID |
| `market.search` | Поиск |
| `market.addAlbum` | Создать подборку |
| `market.getAlbums` | Список подборок |
| `market.addToAlbum` | Добавить в подборку |
| `market.getCategories` | Категории |
| `market.getOrders` | Заказы |
| `market.editOrder` | Изменить статус заказа |

**Добавить товар:**
```python
vk.market.add(
    owner_id=-GROUP, name='Desert Safari',
    description='6ч, трансфер, BBQ', price=250, currency=784
)
```

**Статусы заказов:** 0=new, 1=agreed, 2=delivered, 3=cancelled

---

## Donut (donut.*)

| Метод | Описание |
|-------|----------|
| `donut.isDonor` | Проверить донатера |
| `donut.getSubscribers` | Список донатеров |
| `donut.getSubscriptions` | Подписки пользователя |

**Эксклюзивный пост:**
```python
vk.wall.post(owner_id=-GROUP, from_group=1, message='VIP', donut_paid_duration=-1)
```

---

## Группы (groups.*)

| Метод | Описание |
|-------|----------|
| `groups.getById` | Информация о сообществе |
| `groups.edit` | Редактировать настройки |
| `groups.getMembers` | Список участников |
| `groups.ban` | Забанить |
| `groups.unban` | Разбанить |
| `groups.getBanned` | Чёрный список |

**Настройка фильтров:**
```python
vk.groups.edit(group_id=GROUP, obscene_filter=1, obscene_stopwords=1, obscene_words='спам')
```

---

## Статистика (stats.*)

| Метод | Описание | Требование |
|-------|----------|------------|
| `stats.get` | Статистика сообщества | 5000+ участников |
| `stats.getPostReach` | Охват записей | 5000+ участников, последние 300 |

```python
stats = vk.stats.get(group_id=GROUP, date_from='2026-02-01', date_to='2026-02-12')
reach = vk.stats.getPostReach(owner_id=-GROUP, post_ids=[123,456])
```

---

## Реклама (ads.*)

| Метод | Описание |
|-------|----------|
| `ads.createCampaigns` | Создать кампанию |
| `ads.getStatistics` | Статистика кампаний |
| `ads.getAds` | Список объявлений |
| `ads.updateAds` | Обновить объявления |

---

## Статьи (pages.*)

| Метод | Описание |
|-------|----------|
| `pages.save` | Создать/обновить статью |
| `pages.get` | Получить статью |

```python
vk.pages.save(group_id=GROUP, title='Гид по Дубаю', text='<h1>Топ мест</h1>...')
```

---

## Execute (пакетные операции)

До 25 API вызовов за 1 запрос:

```python
code = """
var i = 0; var results = [];
while (i < 5) {
    results.push(API.wall.post({owner_id:-GROUP, from_group:1, message:"Post "+i}));
    i = i + 1;
}
return results;
"""
vk.execute(code=code)
```

**VKScript:** только `var`, только `while`, `API.method()`, `return`.

---

## Формат attachments

```
{type}{owner_id}_{media_id}
```

| Тип | Пример |
|-----|--------|
| photo | `photo-123_456` |
| video | `video-123_789` |
| doc | `doc-123_012` |
| audio | `audio-123_345` |
| poll | `poll-123_678` |
| link | `https://site.com` |

Несколько: через запятую. Максимум: 10.

---

## Валюты для Market (ISO 4217)

| Код | Валюта |
|-----|--------|
| 643 | RUB |
| 784 | AED |
| 840 | USD |
| 978 | EUR |
| 398 | KZT |

---

## Библиотеки

| Язык | Пакет | Установка |
|------|-------|-----------|
| Python | vk_api | `pip install vk_api` |
| Node.js | vk-io | `npm install vk-io` |
| PHP | vk-php-sdk | composer |

---

## Ссылки

- Методы: https://dev.vk.com/ru/method
- Ошибки: https://dev.vk.com/ru/reference/errors
- Версии: https://dev.vk.com/ru/reference/versions
- Mini Apps: https://dev.vk.com/ru/mini-apps/overview
- VK Bridge: https://dev.vk.com/ru/bridge/overview

---

*Версия: 2.0 | Дата: 2026-02-12*
