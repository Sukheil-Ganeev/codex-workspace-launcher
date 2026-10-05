---
name: instagram-spravochnik
description: "Production-ready руководство по Instagram как платформе для туристического бизнеса ОАЭ. Публикации, Reels, Stories, Shopping, Insights, хэштеги. Используй когда нужно работать с Instagram контентом (НЕ DM/боты)."
---
> **DM-боты и автоматизация:** см. `meta-messenger-bot-справочник` — Messenger API for Instagram, Ice Breakers, Persistent Menu, Webhooks, автоматизация ответов

# Instagram Graph API — Платформа для туристического бизнеса ОАЭ

## 1. Обзор API

### Что такое Instagram Graph API

Instagram Graph API — официальный API от Meta для управления Instagram Business и Creator аккаунтами. Позволяет программно публиковать контент (фото, видео, карусели, Reels, Stories), получать аналитику, управлять комментариями, работать с хэштегами и тегировать товары.

### Типы аккаунтов

| Тип | API доступ | Возможности |
|-----|-----------|-------------|
| **Business** | Полный | Публикации, Insights, Shopping, комментарии |
| **Creator** | Полный | Публикации, Insights, комментарии (без Shopping) |
| **Personal** | Нет | Basic Display API закрыт с декабря 2024 |

**Конвертация в Business:**
1. Instagram → Settings → Account → Switch to Professional Account
2. Выберите категорию: Tourism / Travel Agency
3. Привяжите Facebook Page (обязательно)

### Два типа API-доступа (с 2025)

1. **Instagram API with Instagram Login** — упрощённая авторизация через Instagram (без Facebook Page). Ограниченные permissions: `instagram_basic`, `instagram_content_publish`, `instagram_manage_comments`, `instagram_manage_insights`.

2. **Instagram API with Facebook Login** — полный доступ через Facebook OAuth. Все permissions, включая Shopping и расширенные Insights.

### Версионирование

**Текущая версия:** v22.0 (2026). Рекомендуется использовать последнюю стабильную версию.

**Важные изменения:**
- v21.0 (октябрь 2024) — депрекация video_views, email_contacts, profile_views
- v22.0 (2025-2026) — новая метрика `views` вместо старых plays/impressions, депрекация plays, clips_replays_count, impressions
- Basic Display API полностью закрыт (декабрь 2024)

**Базовый URL:**
```
https://graph.facebook.com/v22.0/
```

---

## 2. Аутентификация

### Что нужно

1. **Facebook App** — создайте на developers.facebook.com/apps
2. **Facebook Page** — привязанная к Instagram Business аккаунту
3. **Access Token** с необходимыми permissions
4. **Instagram Business Account ID** — получается через API

### Получение токена (тестирование)

1. Откройте Graph API Explorer: developers.facebook.com/tools/explorer/
2. Выберите приложение → Get Page Access Token
3. Добавьте permissions: `instagram_basic`, `instagram_content_publish`, `instagram_manage_insights`
4. Generate Access Token → скопируйте

### Получение токена (production — OAuth 2.0)

```
https://www.facebook.com/v22.0/dialog/oauth?
  client_id={APP_ID}&
  redirect_uri={REDIRECT_URI}&
  scope=instagram_basic,instagram_content_publish,instagram_manage_comments,instagram_manage_insights&
  response_type=code
```

Обмен кода на токен:
```bash
curl -X GET "https://graph.facebook.com/v22.0/oauth/access_token?\
client_id={APP_ID}&redirect_uri={REDIRECT_URI}&\
client_secret={APP_SECRET}&code={CODE}"
```

### Long-Lived Token (60 дней)

```bash
curl -X GET "https://graph.facebook.com/v22.0/oauth/access_token?\
grant_type=fb_exchange_token&client_id={APP_ID}&\
client_secret={APP_SECRET}&fb_exchange_token={SHORT_TOKEN}"
```

**Автообновление:** настройте cron каждые 50 дней для обмена токена.

### Получение Instagram Account ID

```bash
curl "https://graph.facebook.com/v22.0/me/accounts?\
fields=instagram_business_account&access_token={TOKEN}"
```

Ответ: `{"instagram_business_account": {"id": "17841405309211844"}}`

### Permissions (App Review)

| Permission | Что даёт | App Review |
|-----------|---------|-----------|
| `instagram_basic` | Профиль, медиа | Нет (базовый) |
| `instagram_content_publish` | Публикация контента | Да |
| `instagram_manage_comments` | Комментарии | Да |
| `instagram_manage_insights` | Аналитика | Да |
| `instagram_shopping_tag_products` | Product Tagging | Да |
| `pages_read_engagement` | Данные страницы | Да |
| `pages_show_list` | Список страниц | Нет |

Подробнее: `references/faq.md` → App Review

---

## 3. Content Publishing API

### Двухэтапная публикация

Instagram использует двухэтапный процесс:
1. **POST /{ig-user-id}/media** — создание медиа-контейнера (загрузка + метаданные)
2. **POST /{ig-user-id}/media_publish** — публикация в профиле

### Публикация фото

```bash
# Шаг 1: Создать контейнер
curl -X POST "https://graph.facebook.com/v22.0/{IG_USER_ID}/media" \
  -F "image_url=https://example.com/dubai_tour.jpg" \
  -F "caption=Desert Safari в Дубае! #Dubai #DesertSafari" \
  -F "access_token={TOKEN}"
# Ответ: {"id": "17895695668004550"}

# Шаг 2: Опубликовать
curl -X POST "https://graph.facebook.com/v22.0/{IG_USER_ID}/media_publish" \
  -F "creation_id=17895695668004550" \
  -F "access_token={TOKEN}"
```

**Требования к фото:**
- Формат: JPEG, PNG
- Размер: до 8 МБ
- Соотношение сторон: от 4:5 до 1.91:1
- Рекомендуемое: 1080x1080 (квадрат) или 1080x1350 (портрет)

### Публикация видео

```bash
curl -X POST "https://graph.facebook.com/v22.0/{IG_USER_ID}/media" \
  -F "media_type=VIDEO" \
  -F "video_url=https://example.com/tour_video.mp4" \
  -F "caption=Лучшие экскурсии в Дубае" \
  -F "access_token={TOKEN}"
```

**Требования к видео:**
- Формат: MP4, MOV
- Размер: до 100 МБ (Feed), до 1 ГБ (Reels)
- Длительность: 3-60 секунд (Feed), 3-90 секунд (Reels)
- Кодек: H.264
- Разрешение: минимум 540x960

### Публикация карусели (до 10 медиа)

```bash
# Шаг 1: Создать контейнеры для каждого элемента
curl -X POST "https://graph.facebook.com/v22.0/{IG_USER_ID}/media" \
  -F "image_url=https://example.com/photo1.jpg" \
  -F "is_carousel_item=true" \
  -F "access_token={TOKEN}"
# Повторить для каждого элемента (до 10)

# Шаг 2: Создать контейнер карусели
curl -X POST "https://graph.facebook.com/v22.0/{IG_USER_ID}/media" \
  -F "media_type=CAROUSEL" \
  -F "caption=10 мест в Дубае, которые нужно увидеть" \
  -F "children=ID1,ID2,ID3,ID4,ID5" \
  -F "access_token={TOKEN}"

# Шаг 3: Опубликовать
curl -X POST "https://graph.facebook.com/v22.0/{IG_USER_ID}/media_publish" \
  -F "creation_id={CAROUSEL_ID}" \
  -F "access_token={TOKEN}"
```

### Caption и хэштеги

- Максимум 2,200 символов
- Максимум 30 хэштегов (рекомендуется 5-10 для лучшего охвата)
- @ упоминания работают в caption
- Эмодзи поддерживаются

### Лимиты публикаций

- **25 публикаций / 24 часа** через API (на аккаунт)
- **200 API-запросов / час** (скользящее окно)
- Контейнеры истекают через 24 часа, если не опубликованы

---

## 4. Reels

### Публикация Reels через API

```bash
# Шаг 1: Создать контейнер
curl -X POST "https://graph.facebook.com/v22.0/{IG_USER_ID}/media" \
  -F "media_type=REELS" \
  -F "video_url=https://example.com/reel_safari.mp4" \
  -F "caption=Desert Safari Experience! #DubaiReels" \
  -F "share_to_feed=true" \
  -F "cover_url=https://example.com/cover.jpg" \
  -F "access_token={TOKEN}"

# Шаг 2: Проверить статус (видео обрабатывается)
curl "https://graph.facebook.com/v22.0/{CONTAINER_ID}?\
fields=status_code&access_token={TOKEN}"
# Ждать status_code=FINISHED

# Шаг 3: Опубликовать
curl -X POST "https://graph.facebook.com/v22.0/{IG_USER_ID}/media_publish" \
  -F "creation_id={CONTAINER_ID}" \
  -F "access_token={TOKEN}"
```

### Параметры Reels

| Параметр | Описание |
|---------|---------|
| `media_type` | `REELS` (обязательно) |
| `video_url` | URL видеофайла (публично доступный) |
| `caption` | Подпись (до 2200 символов) |
| `cover_url` | URL изображения обложки |
| `share_to_feed` | `true` — показывать в Feed (по умолчанию true) |
| `thumb_offset` | Смещение для генерации обложки из видео (мс) |
| `audio_name` | Название аудиотрека (если есть) |
| `collaborators` | Массив username для совместных публикаций |

### Требования к Reels

- **Формат:** MP4, MOV
- **Разрешение:** минимум 540x960 (рекомендуется 1080x1920)
- **Соотношение:** 9:16 (вертикально)
- **Длительность:** 3-90 секунд
- **Размер:** до 1 ГБ
- **FPS:** 24-60
- **Кодек:** H.264, AAC аудио

### Аналитика Reels (v22)

- `views` — количество просмотров (заменяет plays)
- `likes`, `comments`, `shares`, `saves`
- `reach` — уникальный охват
- `skip_rate` — процент пропусков в первые 3 секунды (новая метрика 2025)

---

## 5. Stories

### Публикация Stories через API

```bash
# Фото-Story
curl -X POST "https://graph.facebook.com/v22.0/{IG_USER_ID}/media" \
  -F "image_url=https://example.com/story_photo.jpg" \
  -F "media_type=STORIES" \
  -F "access_token={TOKEN}"

# Видео-Story
curl -X POST "https://graph.facebook.com/v22.0/{IG_USER_ID}/media" \
  -F "video_url=https://example.com/story_video.mp4" \
  -F "media_type=STORIES" \
  -F "access_token={TOKEN}"

# Публикация
curl -X POST "https://graph.facebook.com/v22.0/{IG_USER_ID}/media_publish" \
  -F "creation_id={CONTAINER_ID}" \
  -F "access_token={TOKEN}"
```

### Ограничения Stories через API

- **Нет поддержки интерактивных стикеров** (опросы, вопросы, слайдеры, обратный отсчёт)
- **Нет музыки** через API
- **Нет AR-фильтров**
- **Нет link-стикеров** (swipe up / link sticker) — только вручную
- Stories живут 24 часа (как обычно)
- Только для Business аккаунтов (не все Creator)

### Аналитика Stories

```bash
curl "https://graph.facebook.com/v22.0/{STORY_MEDIA_ID}/insights?\
metric=reach,views,replies,follows,profile_visits,shares&\
access_token={TOKEN}"
```

Метрики Stories (v22):
- `reach` — уникальный охват
- `views` — просмотры
- `replies` — ответы
- `follows` — подписки из Story
- `profile_visits` — переходы в профиль
- `shares` — репосты

**Важно:** данные Insights для Stories доступны только пока Story активна (24 часа) + 48 часов после.

---

## 6. Instagram Shopping

### Требования

1. **Business аккаунт** (Creator не поддерживается для Shopping)
2. **Commerce Manager** с настроенным каталогом
3. **Facebook Shop** — утверждённый Meta
4. **Permission:** `instagram_shopping_tag_products`
5. Страна из списка поддерживаемых (ОАЭ поддерживается)

### Настройка каталога

1. Commerce Manager (business.facebook.com/commerce) → Create Catalog
2. Тип: E-commerce
3. Добавьте товары (вручную, через Data Feed, или Shopify/WooCommerce)
4. Подключите каталог к Instagram: Commerce Manager → Settings → Instagram Shopping

### Product Tagging через API

```bash
# Получить товары каталога
curl "https://graph.facebook.com/v22.0/{CATALOG_ID}/products?\
fields=name,price,image_url&access_token={TOKEN}"

# Тегировать товар в существующем посте
curl -X POST "https://graph.facebook.com/v22.0/{MEDIA_ID}/product_tags" \
  -F 'updated_tags=[{"product_id":"PRODUCT_ID","x":0.5,"y":0.5}]' \
  -F "access_token={TOKEN}"

# Получить теги товаров
curl "https://graph.facebook.com/v22.0/{MEDIA_ID}/product_tags?\
access_token={TOKEN}"

# Удалить теги
curl -X DELETE "https://graph.facebook.com/v22.0/{MEDIA_ID}/product_tags?\
access_token={TOKEN}"
```

### Shopping в Reels

С 2025 Shopping поддерживается в Reels — тегируйте товары прямо в видео. По данным Meta, Shopping Reels дают +22% engagement по сравнению со статичными постами.

### Для туризма ОАЭ

- Тегируйте билеты на экскурсии (Desert Safari, Burj Khalifa, Dhow Cruise)
- Пакетные предложения (тур + трансфер + ужин)
- Каталог: создайте товары-экскурсии с ценой в AED

---

## 7. Insights API

### Метрики аккаунта

```bash
curl "https://graph.facebook.com/v22.0/{IG_USER_ID}/insights?\
metric=reach,accounts_engaged,follows_and_unfollows,profile_views&\
period=day&since=2026-02-01&until=2026-02-12&\
access_token={TOKEN}"
```

**Доступные метрики аккаунта (v22):**

| Метрика | Описание | Период |
|---------|---------|--------|
| `reach` | Уникальный охват | day, week, days_28 |
| `accounts_engaged` | Аккаунты с взаимодействием | day, week, days_28 |
| `follows_and_unfollows` | Подписки/отписки | day |
| `profile_views` | Просмотры профиля | day |

**Демография аудитории:**
```bash
curl "https://graph.facebook.com/v22.0/{IG_USER_ID}/insights?\
metric=follower_demographics&\
metric_type=total_value&\
period=lifetime&\
breakdown=country&\
access_token={TOKEN}"
```

Доступные breakdown: `country`, `city`, `age`, `gender`

### Метрики медиа (постов)

```bash
curl "https://graph.facebook.com/v22.0/{MEDIA_ID}/insights?\
metric=reach,views,likes,comments,shares,saved,\
total_interactions,follows,profile_visits&\
access_token={TOKEN}"
```

**Метрики медиа (v22):**

| Метрика | Фото | Видео | Carousel | Reel | Story |
|---------|------|-------|----------|------|-------|
| `reach` | + | + | + | + | + |
| `views` | + | + | + | + | + |
| `likes` | + | + | + | + | - |
| `comments` | + | + | + | + | - |
| `shares` | + | + | + | + | + |
| `saved` | + | + | + | + | - |
| `follows` | + | + | + | + | + |
| `profile_visits` | + | + | + | + | + |
| `total_interactions` | + | + | + | + | + |
| `replies` | - | - | - | - | + |
| `skip_rate` | - | - | - | + | - |

### Депрекации v21-v22 (важно)

**Удалены:**
- `video_views` → используйте `views`
- `plays`, `clips_replays_count` → используйте `views`
- `impressions` (медиа и аккаунт) → используйте `reach` + `views`
- `email_contacts`, `phone_call_clicks`, `text_message_clicks`, `website_clicks`

---

## 8. Хэштеги

### Hashtag Search API

```bash
# Шаг 1: Найти ID хэштега
curl "https://graph.facebook.com/v22.0/ig_hashtag_search?\
q=dubaitourism&user_id={IG_USER_ID}&access_token={TOKEN}"
# Ответ: {"data": [{"id": "17843853986015181"}]}

# Шаг 2: Получить Top Media
curl "https://graph.facebook.com/v22.0/{HASHTAG_ID}/top_media?\
user_id={IG_USER_ID}&\
fields=id,caption,media_type,permalink,like_count,comments_count&\
access_token={TOKEN}"

# Шаг 3: Получить Recent Media
curl "https://graph.facebook.com/v22.0/{HASHTAG_ID}/recent_media?\
user_id={IG_USER_ID}&\
fields=id,caption,media_type,permalink&\
access_token={TOKEN}"
```

### Лимиты хэштегов

- **30 уникальных хэштегов за 7 дней** (поиск через API)
- **200 запросов/час** (общий лимит API)
- Нельзя искать запрещённые хэштеги
- Результаты: до 50 медиа (Top) и 50 медиа (Recent)

### Стратегия хэштегов для туризма ОАЭ

**Высокочастотные (миллионы):** #Dubai, #UAE, #Travel, #Vacation
**Среднечастотные (100K-1M):** #DubaiTourism, #VisitDubai, #DubaiLife, #AbuDhabi
**Низкочастотные (10K-100K):** #DesertSafari, #DubaiTrip, #DubaiExcursions, #DhowCruise
**Нишевые (<10K):** #DubaiLocalGuide, #DubaiDealz, #UAETourGuide

**Рекомендация:** 3 высоко + 3 средне + 3 низко + 1 нишевый = 10 хэштегов

---

## 9. Mentions и комментарии

### Mentioned Media API

Когда кто-то упоминает ваш аккаунт в посте:

```bash
# Получить медиа с упоминаниями
curl "https://graph.facebook.com/v22.0/{IG_USER_ID}/mentioned_media?\
fields=id,caption,media_type,permalink,timestamp&\
access_token={TOKEN}"
```

### Управление комментариями

```bash
# Получить комментарии к посту
curl "https://graph.facebook.com/v22.0/{MEDIA_ID}/comments?\
fields=id,text,username,timestamp,replies&\
access_token={TOKEN}"

# Ответить на комментарий
curl -X POST "https://graph.facebook.com/v22.0/{COMMENT_ID}/replies" \
  -F "message=Спасибо за отзыв! Напишите нам в DM для бронирования" \
  -F "access_token={TOKEN}"

# Скрыть комментарий
curl -X POST "https://graph.facebook.com/v22.0/{COMMENT_ID}" \
  -F "hide=true" \
  -F "access_token={TOKEN}"

# Удалить комментарий
curl -X DELETE "https://graph.facebook.com/v22.0/{COMMENT_ID}?\
access_token={TOKEN}"
```

### Автомодерация

Настройте Webhook на событие `comments` и обрабатывайте в реальном времени:
- Фильтр по ключевым словам (спам, конкуренты)
- AI-классификация (Claude/YandexGPT)
- Автоответ на типовые вопросы (цены, расписание)

---

## 10. Broadcast Channels

### Что это

Broadcast Channels — односторонний канал связи с подписчиками (как Telegram-канал). Создатель публикует, подписчики читают. Появились в 2023, активно развиваются.

### API поддержка (2026)

**На данный момент нет полноценного API** для Broadcast Channels. Публикация возможна только вручную через приложение Instagram.

### Использование для туризма

- Анонсы горящих туров ("Desert Safari сегодня -30%!")
- Ежедневные предложения
- Эксклюзивные скидки для подписчиков канала
- Опросы (встроенная функция) для выбора экскурсий

---

## 11. Collaborative Posts

### Что это

Совместные публикации — пост появляется в профилях двух (или более) авторов одновременно. Один и тот же пост, одна аналитика, удвоенный охват.

### Через API

```bash
curl -X POST "https://graph.facebook.com/v22.0/{IG_USER_ID}/media" \
  -F "image_url=https://example.com/collab_tour.jpg" \
  -F "caption=Совместный пост с партнёром!" \
  -F "collaborators=[\"partner_username\"]" \
  -F "access_token={TOKEN}"
```

Параметр `collaborators` — массив username (до 3 соавторов). Соавтор должен одобрить приглашение в приложении Instagram.

### Для туризма ОАЭ

- Коллаборации с отелями: тур + проживание
- С блогерами: обзор экскурсии
- С ресторанами: тур + ужин (Dhow Cruise)
- С прокатом авто (Марсель): тур + VIP-трансфер

---

## 12. Creator Marketplace и Branded Content

### Creator Marketplace

Платформа Meta для поиска и сотрудничества с инфлюенсерами. Бренды находят креаторов, креаторы получают предложения.

### Partnership Ads (Branded Content Ads)

Рекламодатель продвигает контент креатора как рекламу:

```bash
# Получить код партнёрства
curl "https://graph.facebook.com/v22.0/{IG_USER_ID}?\
fields=branded_content_tag_approval&access_token={TOKEN}"
```

### Для туризма

- Найдите travel-блогеров через Creator Marketplace
- Отправьте предложение на обзор экскурсии
- Продвигайте их пост через Partnership Ads
- ROI: в среднем 3-5x для travel-ниши в ОАЭ

---

## 13. oEmbed — встраивание контента

### Что такое

oEmbed позволяет встраивать Instagram посты на сторонних сайтах (блоги, лендинги).

### API (Meta oEmbed Read — с 2025)

Старый oEmbed закрыт в апреле 2025. Новый endpoint:

```bash
curl "https://graph.facebook.com/v22.0/instagram_oembed?\
url=https://www.instagram.com/p/ABC123/&\
access_token={APP_TOKEN}"
```

**Ответ:**
```json
{
  "html": "<blockquote class='instagram-media'...>...</blockquote>",
  "width": 658,
  "provider_name": "Instagram"
}
```

**Изменения 2025:** Поля `thumbnail_url`, `thumbnail_width`, `thumbnail_height`, `author_name` удалены. Генерируйте превью самостоятельно через HTML-метаданные поста.

### Требования

- App Access Token (не User Token)
- Reviewed & approved app
- Только публичный контент

---

## 14. Примеры для туризма ОАЭ

### Автопостинг экскурсий

```
Cron (9:00 GST) → Выбрать тур дня из базы
                → Сгенерировать caption (YandexGPT)
                → Опубликовать фото/карусель через API
                → Тегировать товар (Shopping)
                → Логировать
```

**Пример caption:**
```
Пустынное сафари на джипах — главное приключение в Дубае!

Что входит:
- Езда по дюнам на 4x4
- Катание на верблюдах
- BBQ-ужин в лагере бедуинов
- Шоу-программа: танец живота, тануура

Цена: от 180 AED / чел.
Забронировать: DM или ссылка в шапке профиля

#DesertSafari #Dubai #DubaiTourism #VisitDubai
#ПустынноеСафари #Дубай #Экскурсии #ОАЭ #Туризм #Travel
```

### Reels-стратегия

| Тип Reel | Частота | Хэштеги |
|---------|---------|---------|
| Обзор экскурсии (POV) | 3/неделю | #DubaiReels #TravelReels |
| До/после (пустыня/город) | 1/неделю | #DubaiTransformation |
| Отзыв клиента | 2/неделю | #DubaiReview #TouristReview |
| Закат/рассвет | 1/неделю | #DubaiSunset #GoldenHour |

### Аналитика аудитории

```bash
# Откуда подписчики
curl "https://graph.facebook.com/v22.0/{IG_USER_ID}/insights?\
metric=follower_demographics&metric_type=total_value&\
period=lifetime&breakdown=country&access_token={TOKEN}"

# Ожидаемый результат для туризма ОАЭ:
# RU ~35%, KZ ~15%, AE ~12%, UZ ~8%, BY ~5%, DE ~4%, UK ~3%
```

### Shopping для билетов

1. Commerce Manager → создайте каталог "Excursions UAE"
2. Добавьте товары: Desert Safari (180 AED), Burj Khalifa (260 AED), Dubai Frame (50 AED)
3. В каждом посте тегируйте соответствующую экскурсию
4. Клиент нажимает → видит цену → переходит на сайт бронирования

### Билингвальный контент

Тренд ОАЭ 2026: +28% вовлеченность при двуязычных постах (EN + AR):
```
Discover the magic of Dubai Desert Safari!
اكتشف سحر رحلة السفاري في دبي!

Book now: DM / Link in bio
احجز الآن: رسالة مباشرة
```

---

## 15. Rate Limits

| Ресурс | Лимит | Окно |
|--------|------|------|
| **API запросы** | 200 / час | Скользящее (на аккаунт) |
| **Публикации** | 25 / 24 часа | Фиксированное |
| **Hashtag Search** | 30 уникальных / 7 дней | Неделя |
| **Контейнеры** | Истекают через 24 часа | - |
| **Insights** | Включены в 200/час | - |

**При превышении:** пауза на 1 час (не бан). Лимиты обновляются каждый час.

**Масштабирование:** 10 аккаунтов = 2,000 запросов/час.

---

## Безопасность

### Токены

- Храните в .env (добавьте в .gitignore)
- Обновляйте каждые 50 дней (Long-Lived Token)
- Ограничьте по IP (Facebook App Settings → Advanced)
- Никогда не передавайте в чатах и не коммитьте в Git

### Webhooks

- Только HTTPS с валидным SSL
- Верификация signature (`sha256` HMAC с App Secret)
- Проверяйте Verify Token при подписке

### Соблюдение ToS

**Запрещено:**
- Автоматические лайки/подписки
- Массовый спам
- Парсинг чужого контента
- Покупка подписчиков

**Последствия:** бан аккаунта, отзыв App Review.

---

## Стоимость

| Компонент | Цена |
|----------|------|
| Instagram Graph API | Бесплатно |
| Make.com (автоматизация) | ~$16/мес |
| VPS для webhook | $5-10/мес |
| YandexGPT (caption) | $0 (бесплатный tier) |
| **Итого** | **$0-30/мес** |

---

## Полезные ссылки

- **Документация:** developers.facebook.com/docs/instagram-api
- **Changelog:** developers.facebook.com/docs/instagram-api/changelog
- **Graph API Explorer:** developers.facebook.com/tools/explorer/
- **Postman Collection:** postman.com/meta/instagram
- **Stack Overflow:** тег `instagram-graph-api`

---

## Структура справочника

### References
- `faq.md` — 15 частых вопросов (App Review, токены, лимиты, Shopping)
- `troubleshooting.md` — 15 типичных проблем и решений
- `cheatsheet.md` — шпаргалка: endpoints, параметры, метрики

---

**Версия:** 2.0
**Дата:** 12.02.2026
**Автор:** Claude Code Agent
**Для:** Туристический бизнес в ОАЭ (Сухейль)

---

## Experience

Этот скилл накапливает опыт в папке `experience/`:
- `_index.md` — критические уроки (читать при активации!)
- `fixes/` — исправленные ошибки
- `improvements/` — найденные улучшения
- `patterns/` — повторяющиеся паттерны
- `warnings/` — что НЕ делать

При завершении работы: если был урок — предложить записать в опыт.

---

## Ресурсы скилла

| Файл | Описание |
|------|----------|
| references/faq.md | Часто задаваемые вопросы |
| references/troubleshooting.md | Решение проблем |
| references/cheatsheet.md | Шпаргалка |
