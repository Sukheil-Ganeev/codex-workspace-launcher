---
name: vk-справочник
description: "Production-ready руководство по VK как платформе для туристического бизнеса ОАЭ. Сообщества, Clips, Market, Donut, Stories, реклама, аналитика. Используй когда нужно работать с VK контентом (НЕ боты)."
---
# VK: Полное руководство по платформе для туристического бизнеса

> **Боты сообществ:** см. `vk-bot-справочник` — Long Poll, Callback API, клавиатуры, рассылки, messages.send

## Содержание

1. [Обзор API](#обзор-api)
2. [Аутентификация](#аутентификация)
3. [Сообщества](#сообщества)
4. [Стена и контент](#стена-и-контент)
5. [VK Clips](#vk-clips)
6. [VK Stories](#vk-stories)
7. [VK Market](#vk-market)
8. [VK Donut](#vk-donut)
9. [VK Articles](#vk-articles)
10. [VK Live](#vk-live)
11. [VK Реклама](#vk-реклама)
12. [Аналитика](#аналитика)
13. [VK Mini Apps](#vk-mini-apps)
14. [Модерация](#модерация)
15. [Примеры для туризма ОАЭ](#примеры-для-туризма-оаэ)
16. [Rate Limits](#rate-limits)

---

## Обзор API

### Базовые сведения

**VK API** — REST API социальной сети ВКонтакте. Позволяет автоматизировать управление сообществами, публикацию контента, работу с товарами, рекламой и аналитикой.

**Endpoint:** `https://api.vk.com/method/METHOD_NAME`

**Методы:** GET, POST (рекомендуется POST)

**Текущая версия (2026):** v5.199

**Обязательные параметры каждого запроса:**

| Параметр | Описание | Пример |
|----------|----------|--------|
| `access_token` | Токен доступа | `vk1.a.AbCdEf...` |
| `v` | Версия API | `5.199` |

**Структура ответа:**

```json
// Успех
{"response": { ... }}

// Ошибка
{"error": {"error_code": 5, "error_msg": "User authorization failed"}}
```

**Коды ошибок:**

| Код | Описание | Решение |
|-----|----------|---------|
| 5 | Невалидный токен | Получить новый токен |
| 6 | Too many requests | Добавить паузы, использовать execute |
| 14 | Требуется капча | Обработать (редко для API) |
| 100 | Неверные параметры | Проверить параметры |
| 214 | Нет доступа к публикации | Проверить права токена |

### VK ID / Open API

**VK ID** — единая система авторизации VK (ранее VK Connect). Используется для входа пользователей через VK на внешних сайтах.

**Применение для туризма:** кнопка "Войти через VK" на сайте бронирования.

```html
<script src="https://unpkg.com/@vkid/sdk/dist-sdk/umd/index.js"></script>
<script>
  VKIDSDK.Config.init({app: YOUR_APP_ID, redirectUrl: 'https://yoursite.com/callback'});
  const oneTap = new VKIDSDK.OneTap();
  oneTap.render({container: document.getElementById('vk-login')});
</script>
```

---

## Аутентификация

### Типы токенов

| Тип | Rate Limit | Применение | Получение |
|-----|-----------|------------|-----------|
| **Community Token** | 3 req/sec | Одно сообщество | Настройки -> Работа с API |
| **User Token** | 5 req/sec | От имени пользователя | OAuth 2.0 |
| **Standalone Token** | 20 req/sec | Несколько сообществ | OAuth Implicit Flow |
| **Service Token** | 20 req/sec | Публичные данные | Настройки приложения |

### Community Token (рекомендуется для бизнеса)

Самый простой способ — токен сообщества:

1. Настройки сообщества -> **Работа с API** -> **Создать ключ**
2. Выбрать права: управление, посты, фото, видео
3. Скопировать токен

**Формат:** `vk1.a.AbCdEfGhIjKlMnOpQrStUvWxYz...`

Токен не истекает (пока не удалите вручную).

### OAuth 2.0 (User Token)

Для работы от имени пользователя — Implicit Flow:

```
https://oauth.vk.com/authorize?
  client_id=YOUR_APP_ID
  &display=page
  &redirect_uri=https://oauth.vk.com/blank.html
  &scope=wall,photos,video,groups,market,stories,offline
  &response_type=token
  &v=5.199
```

**Scope (права):**

| Право | Описание |
|-------|----------|
| `wall` | Публикации на стене |
| `photos` | Фотографии |
| `video` | Видео |
| `groups` | Управление сообществами |
| `market` | Товары (Market) |
| `stories` | Истории |
| `ads` | Реклама |
| `stats` | Статистика |
| `offline` | Бессрочный токен |

### Безопасность токенов

- Хранить в `.env`, не в коде
- Использовать HTTPS
- Не публиковать в Git

```python
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('VK_COMMUNITY_TOKEN')
```

---

## Сообщества

### Типы сообществ

| Тип | Описание | Для туризма |
|-----|----------|-------------|
| **Группа** (group) | Обсуждения, общение участников | Клуб путешественников |
| **Публичная страница** (public) | Новости, контент от лица бренда | Основная страница бизнеса |
| **Мероприятие** (event) | Разовые события | Групповые туры, мероприятия |

**Рекомендация:** Публичная страница — для туристического бизнеса.

### Управление через API

**Получить информацию:**

```python
info = vk.groups.getById(group_id='your_group', fields='members_count,description,market')
```

**Изменить настройки:**

```python
vk.groups.edit(
    group_id=12345678,
    description='Экскурсии в Дубае и ОАЭ. Лучшие цены!',
    website='https://yoursite.com',
    wall=2,          # 0-выкл, 1-откр, 2-огранич, 3-закрыт
    topics=1,        # обсуждения
    photos=1,        # фотоальбомы
    video=1,         # видеозаписи
    market=1         # товары
)
```

**Управление участниками:**

```python
# Получить список участников
members = vk.groups.getMembers(group_id=12345678, count=100)

# Забанить пользователя
vk.groups.ban(group_id=12345678, owner_id=USER_ID, reason=0, comment='Спам')

# Разбанить
vk.groups.unban(group_id=12345678, owner_id=USER_ID)
```

---

## Стена и контент

### wall.post — публикация записи

```python
import vk_api

vk_session = vk_api.VkApi(token='YOUR_TOKEN')
vk = vk_session.get_api()

response = vk.wall.post(
    owner_id=-12345678,          # ID сообщества (отрицательный!)
    from_group=1,                # от имени сообщества
    message='Desert Safari в Дубае!',
    attachments='photo-123_456'  # медиа (опционально)
)
print(f"post_id: {response['post_id']}")
```

**Параметры wall.post:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `owner_id` | int | ID стены (отрицательный для группы) |
| `from_group` | int | 1 = от имени сообщества |
| `message` | string | Текст (до 16384 символов) |
| `attachments` | string | Медиа через запятую |
| `publish_date` | int | Unix timestamp (отложенный пост) |
| `copyright` | string | Ссылка на источник |

### Загрузка медиа

**3-шаговый процесс для фото:**

```python
upload = vk_api.VkUpload(vk_session)

# Загрузка фото (все 3 шага автоматически)
photo = upload.photo_wall(photos='dubai.jpg', group_id=12345678)
attachment = f"photo{photo[0]['owner_id']}_{photo[0]['id']}"

# Публикация
vk.wall.post(owner_id=-12345678, from_group=1, message='Дубай!', attachments=attachment)
```

**Загрузка видео:**

```python
import requests

video_data = vk.video.save(
    name='Desert Safari Dubai',
    description='Экскурсия по пустыне',
    group_id=12345678
)

with open('safari.mp4', 'rb') as f:
    requests.post(video_data['upload_url'], files={'video_file': f})

attachment = f"video{video_data['owner_id']}_{video_data['video_id']}"
```

**Формат attachments:** `{type}{owner_id}_{media_id}` — через запятую до 10 шт.

### Отложенные публикации

```python
from datetime import datetime, timedelta

publish_time = datetime.now() + timedelta(hours=2)

vk.wall.post(
    owner_id=-12345678,
    from_group=1,
    message='Вечерний тур Dubai Marina!',
    publish_date=int(publish_time.timestamp())
)
```

**Ограничения:** от 10 минут до 1 года вперёд.

### Другие методы стены

| Метод | Описание |
|-------|----------|
| `wall.get` | Получить записи (count, offset) |
| `wall.edit` | Редактировать запись |
| `wall.delete` | Удалить запись |
| `wall.pin` | Закрепить запись |
| `wall.unpin` | Открепить запись |
| `wall.repost` | Репост записи |
| `wall.createComment` | Добавить комментарий |
| `wall.getComments` | Получить комментарии |

---

## VK Clips

### Обзор

**VK Clips** — платформа коротких вертикальных видео (аналог Reels/TikTok). Среднесуточные просмотры — 2.7 млрд (Q3 2025).

**Характеристики:**

- Длительность: до 3 минут (ранее 90 сек)
- Формат: вертикальный (9:16)
- Разрешение: до 1080p, 60 FPS
- Встроенный редактор: маски, фильтры, музыка, тренды

### Создание через API

Клипы загружаются через `video.save` с параметром `is_clip=1`:

```python
clip_data = vk.video.save(
    name='Desert Safari Highlights',
    description='Лучшие моменты сафари в Дубае',
    group_id=12345678,
    is_clip=1,           # Это клип
    wallpost=0
)

with open('clip_vertical.mp4', 'rb') as f:
    requests.post(clip_data['upload_url'], files={'video_file': f})
```

### Рекомендации для туризма

- **Контент:** 15-60 секунд — достопримечательности, экскурсии, закаты
- **Формат:** вертикальный 9:16, яркая обложка
- **Хештеги:** #Dubai #ОАЭ #Экскурсии #DesertSafari #VKClips
- **Тренды:** использовать раздел "Тренды" для подбора музыки и хештегов
- **Частота:** 3-5 клипов в неделю
- **Промо:** можно создавать клипы из длинных видео в пару кликов

---

## VK Stories

### Обзор

**VK Stories** — исчезающие публикации (24 часа). Доступны для сообществ с 5000+ подписчиков.

### Публикация через API

**Фото-история:**

```python
# 1. Получить upload server
server = vk.stories.getPhotoUploadServer(
    add_to_news=1,
    group_id=12345678
)

# 2. Загрузить фото
with open('story_photo.jpg', 'rb') as f:
    response = requests.post(server['upload_url'], files={'file': f})

# 3. Сохранить
result = vk.stories.save(upload_results=response.text)
```

**Видео-история:**

```python
server = vk.stories.getVideoUploadServer(
    add_to_news=1,
    group_id=12345678
)

with open('story_video.mp4', 'rb') as f:
    response = requests.post(server['upload_url'], files={'video_file': f})

result = vk.stories.save(upload_results=response.text)
```

### Параметры историй

| Параметр | Описание |
|----------|----------|
| `add_to_news` | 1 = показать в ленте новостей |
| `link_text` | Текст кнопки (more/book/buy/...) |
| `link_url` | URL при свайпе вверх |
| `group_id` | ID сообщества |

**Ссылка в истории** (свайп вверх):

```python
server = vk.stories.getPhotoUploadServer(
    add_to_news=1,
    group_id=12345678,
    link_text='book',
    link_url='https://yoursite.com/booking'
)
```

### Рекомендации

- Фото: 1080x1920 px (9:16)
- Видео: до 15 сек, вертикальное
- Свайп-ссылка для бронирований
- Ежедневные истории для вовлечённости

---

## VK Market

### Обзор

**VK Market** — встроенный магазин товаров и услуг в сообществе. Позволяет продавать экскурсии, билеты и туры прямо из VK.

**Новинки 2025:** формат "Shops" — карточки товаров в клипах, историях и постах с прямой покупкой.

### Подключение Market

1. Настройки сообщества -> **Разделы** -> **Товары** -> Включить
2. Указать: валюту, контактное лицо, описание магазина
3. Или через API: `groups.edit(group_id=ID, market=1)`

### Управление товарами через API

**Добавить товар:**

```python
item = vk.market.add(
    owner_id=-12345678,
    name='Desert Safari Dubai',
    description='6-часовая экскурсия по пустыне. Трансфер, джипы, ужин BBQ, шоу.',
    category_id=1001,         # Категория "Туризм и отдых"
    price=250,                # Цена
    currency=784,             # AED (ISO 4217)
    main_photo_id=PHOTO_ID,   # ID загруженного фото
    url='https://yoursite.com/desert-safari'
)
print(f"market_item_id: {item['market_item_id']}")
```

**Редактировать товар:**

```python
vk.market.edit(
    owner_id=-12345678,
    item_id=123,
    price=220,                # Новая цена
    deleted=0
)
```

**Подборки (альбомы):**

```python
# Создать подборку
album = vk.market.addAlbum(
    owner_id=-12345678,
    title='Экскурсии по Дубаю',
    photo_id=PHOTO_ID
)

# Добавить товар в подборку
vk.market.addToAlbum(
    owner_id=-12345678,
    item_id=123,
    album_ids=album['market_album_id']
)
```

### Основные методы Market

| Метод | Описание |
|-------|----------|
| `market.add` | Добавить товар |
| `market.edit` | Редактировать товар |
| `market.delete` | Удалить товар |
| `market.get` | Получить список товаров |
| `market.getById` | Получить товар по ID |
| `market.search` | Поиск товаров |
| `market.addAlbum` | Создать подборку |
| `market.getAlbums` | Получить подборки |
| `market.getCategories` | Категории товаров |
| `market.getOrders` | Заказы (корзина) |

### Заказы и корзина

```python
# Получить заказы
orders = vk.market.getOrders(owner_id=-12345678, count=50)

# Изменить статус заказа
vk.market.editOrder(
    owner_id=-12345678,
    order_id=789,
    status=2  # 0=new, 1=agreed, 2=delivered, 3=cancelled
)
```

---

## VK Donut

### Обзор

**VK Donut** — сервис платных подписок. Подписчики платят ежемесячно за эксклюзивный контент. Доход авторов за 2025: 2.23 млрд руб.

**Модель:** Подписка от 50 до 2000 руб/мес (автор устанавливает сам).

**Комиссия:** 5% + 2.3% за вывод + 25 руб.

### Подключение

1. Настройки сообщества -> **VK Donut** -> Включить
2. Настроить уровни подписки и их привилегии
3. Описать что получают донатеры

### Привилегии подписчиков

- Доступ к эксклюзивным постам
- Ранний просмотр публикаций
- Спецзначок у аватарки
- Доступ к закрытому чату
- Доступ к эксклюзивным комментариям

### API для Donut

```python
# Проверить, является ли пользователь донатером
is_donor = vk.donut.isDonor(owner_id=-12345678, user_id=USER_ID)

# Получить список донатеров
donors = vk.donut.getSubscribers(owner_id=-12345678, count=100)

# Получить подписки пользователя
subs = vk.donut.getSubscriptions(count=10)
```

### Эксклюзивные посты для донатеров

```python
vk.wall.post(
    owner_id=-12345678,
    from_group=1,
    message='Секретные маршруты Дубая, которых нет в путеводителях!',
    donut_paid_duration=-1  # -1 = только для донатеров навсегда
)
```

### Идеи для туризма

- **Уровень 1 (50 руб):** закулисье экскурсий, лайфхаки
- **Уровень 2 (200 руб):** персональные рекомендации, скидки 5%
- **Уровень 3 (500 руб):** VIP-чат с менеджером, скидки 15%, приоритетное бронирование

---

## VK Articles

### Обзор

**VK Articles** — редактор лонгридов (статей) внутри ВКонтакте. Поддерживает форматирование, фото, видео, цитаты. Статьи индексируются поисковиками.

### Создание через API

Статьи используют wiki-разметку и метод `pages.save`:

```python
# Создать/обновить статью
page = vk.pages.save(
    group_id=12345678,
    title='Гид по Дубаю: 10 мест, которые нужно посетить',
    text='<h1>Топ-10 мест Дубая</h1><p>Burj Khalifa, Dubai Mall...</p>'
)
```

**Получить статью:**

```python
article = vk.pages.get(
    owner_id=-12345678,
    page_id=PAGE_ID
)
```

### Рекомендации

- SEO: статьи индексируются Яндексом и Google
- Длинные гиды по экскурсиям и достопримечательностям
- Прикрепляйте к постам как attachment

---

## VK Live

### Обзор

**VK Live** — прямые трансляции из сообщества. Подходят для виртуальных туров и Q&A сессий.

### Создание трансляции через API

```python
# Создать трансляцию
stream = vk.video.startStreaming(
    group_id=12345678,
    name='Прямой эфир из Дубая!',
    description='Показываем достопримечательности в реальном времени'
)
# Ответ содержит RTMP URL и stream key
```

Альтернативно — через `video.save` с параметром `is_private=0` и OBS/Streamlabs.

### Идеи для туризма

- Виртуальные туры по достопримечательностям
- Q&A "спроси о Дубае"
- Трансляции с экскурсий (Desert Safari, Yacht Tour)

---

## VK Реклама

### Рекламные записи из сообщества

Для продвижения постов используется VK Ads (ранее Target VK).

**Создание кампании через API:**

```python
vk.ads.createCampaigns(
    account_id=AD_ACCOUNT_ID,
    data='[{"type":"promoted_posts","name":"Desert Safari Promo","day_limit":"1000","all_limit":"10000"}]'
)
```

### Таргетинг для туризма

| Параметр | Значение |
|----------|----------|
| **География** | Россия, СНГ (Казахстан, Узбекистан) |
| **Возраст** | 25-45 лет |
| **Интересы** | Путешествия, туризм, ОАЭ |
| **Ретаргетинг** | Посетители сообщества |

### Новые форматы (2025)

- **Реклама в Stories** — видео до 30 сек или изображения в историях ВК
- **Carousel** — несколько карточек с товарами/экскурсиями
- **Collages** — формат из нескольких изображений
- **Shops** — карточки товаров с кнопкой покупки в клипах и видео

### Бюджет

- **CPM:** 50-150 руб (1000 показов)
- **CPC:** 5-20 руб (клик)
- **Стартовый бюджет:** 5,000-10,000 руб/мес

### Получение статистики рекламы

```python
stats = vk.ads.getStatistics(
    account_id=AD_ACCOUNT_ID,
    ids_type='campaign',
    ids='123,456',
    period='day',
    date_from='2026-02-01',
    date_to='2026-02-12'
)
```

---

## Аналитика

### stats.get — статистика сообщества

Доступна для сообществ с 5000+ участников.

```python
stats = vk.stats.get(
    group_id=12345678,
    date_from='2026-02-01',
    date_to='2026-02-12'
)
```

**Возвращаемые данные:**

- `visitors` — уникальные посетители и просмотры
- `reach` — охват (подписчики + виральный + рекламный)
- `activity` — лайки, комментарии, репосты, подписки

### stats.getPostReach — статистика записей

Доступна для последних 300 записей в сообществах с 5000+ участников.

```python
post_stats = vk.stats.getPostReach(
    owner_id=-12345678,
    post_ids=[123, 456, 789]
)
```

**Метрики:**

| Метрика | Описание |
|---------|----------|
| `reach_subscribers` | Охват подписчиков |
| `reach_viral` | Виральный охват |
| `reach_ads` | Рекламный охват |
| `reach_total` | Общий охват |
| `links` | Клики по ссылкам |
| `to_group` | Переходы в сообщество |
| `join_group` | Вступления |
| `report` | Жалобы |
| `hide` | Скрытия |

### Метрики для отслеживания (туризм)

1. **Охват** — сколько людей видят контент
2. **Вовлечённость** — лайки + комменты + репосты / охват
3. **Переходы** — клики на ссылки бронирования
4. **Рост подписчиков** — динамика по неделям
5. **Конверсия Market** — просмотры товаров -> заказы

---

## VK Mini Apps

### Обзор

**VK Mini Apps** — встроенные веб-приложения внутри VK (аналог Telegram Web Apps). Технологии: HTML/CSS/JS + VK Bridge.

**Для туризма:** каталог экскурсий, бронирование, оплата (VK Pay), электронные билеты.

### VK Bridge API

```javascript
import vkBridge from '@vkontakte/vk-bridge';

// Инициализация
vkBridge.send('VKWebAppInit');

// Данные пользователя
const user = await vkBridge.send('VKWebAppGetUserInfo');

// Оплата VK Pay
await vkBridge.send('VKWebAppOpenPayForm', {
    app_id: APP_ID,
    action: 'pay-to-group',
    params: {group_id: GROUP_ID, amount: 250, description: 'Desert Safari'}
});

// Поделиться на стену
await vkBridge.send('VKWebAppShowWallPostBox', {
    message: 'Забронировал Desert Safari!'
});
```

### Основные методы VK Bridge

| Метод | Описание |
|-------|----------|
| `VKWebAppInit` | Инициализация |
| `VKWebAppGetUserInfo` | Данные пользователя |
| `VKWebAppOpenPayForm` | Оплата VK Pay |
| `VKWebAppShare` | Поделиться |
| `VKWebAppShowWallPostBox` | Пост на стену |
| `VKWebAppGetGeodata` | Геолокация |

### Документация

- https://dev.vk.com/ru/mini-apps/overview
- https://dev.vk.com/ru/bridge/overview

---

## Модерация

### Управление участниками

```python
# Получить участников
members = vk.groups.getMembers(group_id=12345678, count=100, filter='managers')

# Забанить
vk.groups.ban(
    group_id=12345678,
    owner_id=USER_ID,
    reason=1,           # 0=другое, 1=спам, 2=оскорбление, 3=нецензур
    comment='Спам',
    comment_visible=1   # Видимый комментарий
)

# Получить чёрный список
banned = vk.groups.getBanned(group_id=12345678, count=100)
```

### Фильтры контента

```python
vk.groups.edit(
    group_id=12345678,
    obscene_filter=1,     # Фильтр нецензурной лексики
    obscene_stopwords=1,  # Стоп-слова
    obscene_words='спам,реклама,конкурент'
)
```

### Модерация комментариев

```python
# Удалить комментарий
vk.wall.deleteComment(owner_id=-12345678, comment_id=COMMENT_ID)

# Ответить на комментарий
vk.wall.createComment(
    owner_id=-12345678,
    post_id=POST_ID,
    message='Спасибо за отзыв! Рады, что понравилось.'
)
```

---

## Примеры для туризма ОАЭ

### Контент-план для сообщества

| День | Тип | Контент |
|------|-----|---------|
| Пн | Пост + фото | Анонс экскурсий на неделю |
| Вт | Клип 30 сек | Достопримечательность дня |
| Ср | История + свайп | Акция/спецпредложение |
| Чт | Статья | Гид "Топ-5 мест в Дубае" |
| Пт | Клип 60 сек | Закулисье экскурсии |
| Сб | Пост + карусель | Отзывы клиентов |
| Вс | Live трансляция | Q&A "Спроси о Дубае" |

### Автопостинг ежедневных экскурсий

```python
import vk_api
import schedule
import time

vk_session = vk_api.VkApi(token='YOUR_TOKEN')
vk = vk_session.get_api()

def post_morning():
    from datetime import datetime
    today = datetime.now().strftime('%d.%m.%Y')
    vk.wall.post(
        owner_id=-12345678,
        from_group=1,
        message=f'Экскурсии на {today}:\n\nDesert Safari - 250 AED\nCity Tour - 150 AED\nYacht Marina - 300 AED\n\nБронь: +971 50 XXX XXXX'
    )

schedule.every().day.at("09:00").do(post_morning)
while True:
    schedule.run_pending()
    time.sleep(60)
```

### Market с экскурсиями

```python
# Добавить экскурсию как товар
tours = [
    {'name': 'Desert Safari', 'price': 250, 'desc': 'Джипы, ужин BBQ, шоу. 15:00-21:00'},
    {'name': 'Dubai City Tour', 'price': 150, 'desc': 'Burj Khalifa, Dubai Mall. 09:00-13:00'},
    {'name': 'Yacht Marina', 'price': 300, 'desc': 'Яхта, напитки, закуски. 17:00-20:00'},
    {'name': 'Abu Dhabi Tour', 'price': 200, 'desc': 'Sheikh Zayed, Louvre. Весь день'},
]

for tour in tours:
    vk.market.add(
        owner_id=-12345678,
        name=tour['name'],
        description=tour['desc'],
        price=tour['price'],
        currency=784  # AED
    )
```

### Clips-стратегия

1. **До экскурсии:** 15 сек тизер с музыкой (хештег тренда)
2. **Во время:** 30-60 сек highlights (джипы, закаты, яхты)
3. **После:** 15 сек отзыв клиента + CTA "бронируй в описании"

---

## Rate Limits

### Ограничения по типу токена

| Тип | Rate Limit | Примечание |
|-----|-----------|------------|
| Community Token | 3 req/sec | На одно сообщество |
| User Token | 5 req/sec | На пользователя |
| Standalone App | 20 req/sec | На приложение |

### Метод execute — до 25 вызовов за раз

```python
code = """
var posts = [];
var i = 0;
var messages = ["Пост 1", "Пост 2", "Пост 3"];
while (i < messages.length) {
    posts.push(API.wall.post({owner_id: -12345678, from_group: 1, message: messages[i]}));
    i = i + 1;
}
return posts;
"""
response = vk.execute(code=code)
```

### Обработка ошибок

```python
import time

def safe_api_call(method, **kwargs):
    for attempt in range(3):
        try:
            return method(**kwargs)
        except vk_api.exceptions.ApiError as e:
            if e.code == 6:  # Too many requests
                time.sleep(1)
                continue
            raise
    raise Exception("Max retries exceeded")
```

---

## Ссылки

**Официальная документация:**
- Методы API: https://dev.vk.com/ru/method
- VK для разработчиков: https://vk.com/dev
- VK Bridge: https://dev.vk.com/ru/bridge/overview
- Mini Apps: https://dev.vk.com/ru/mini-apps/overview
- VK Pay: https://dev.vk.com/ru/pay/overview
- Сообщество: https://vk.com/apiclub

**Библиотеки:**
- Python: `pip install vk_api` — https://github.com/python273/vk_api
- Node.js: `npm install vk-io` — https://github.com/negezor/vk-io
- PHP: https://github.com/VKCOM/vk-php-sdk

**Подробные руководства:** см. `references/` — faq.md, troubleshooting.md, cheatsheet.md

**Связанные справочники:**
- `vk-bot-справочник` — боты, Long Poll, Callback API, рассылки
- `vk-video-справочник` — работа с VK Video API

---

**Версия:** 2.0
**Дата обновления:** 2026-02-12
**Автор:** Claude Code Agent для Сухейль (Туризм в Дубае/ОАЭ)

---

## Ресурсы скилла

| Файл | Описание |
|------|----------|
| references/faq.md | Часто задаваемые вопросы |
| references/troubleshooting.md | Решение проблем |
| references/cheatsheet.md | Шпаргалка |
