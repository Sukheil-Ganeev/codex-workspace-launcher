# Instagram Graph API — Шпаргалка

> **DM-боты:** см. `instagram-bot-справочник`
> **Базовый URL:** `https://graph.facebook.com/v22.0/`

---

## Endpoints — Публикация

```bash
# Создать медиа-контейнер (фото)
POST /{ig-user-id}/media
  image_url, caption, access_token

# Создать медиа-контейнер (видео)
POST /{ig-user-id}/media
  media_type=VIDEO, video_url, caption, access_token

# Создать Reel
POST /{ig-user-id}/media
  media_type=REELS, video_url, caption, cover_url, share_to_feed, access_token

# Создать Story
POST /{ig-user-id}/media
  media_type=STORIES, image_url|video_url, access_token

# Элемент карусели
POST /{ig-user-id}/media
  image_url|video_url, is_carousel_item=true, access_token

# Контейнер карусели
POST /{ig-user-id}/media
  media_type=CAROUSEL, children=ID1,ID2,..., caption, access_token

# Опубликовать
POST /{ig-user-id}/media_publish
  creation_id, access_token

# Проверить статус видео
GET /{container-id}?fields=status_code&access_token={TOKEN}
```

---

## Endpoints — Профиль и медиа

```bash
# Информация о профиле
GET /{ig-user-id}?fields=id,username,name,profile_picture_url,followers_count,media_count

# Список постов
GET /{ig-user-id}/media?fields=id,caption,media_type,permalink,timestamp,like_count,comments_count

# Информация о посте
GET /{media-id}?fields=id,caption,media_type,permalink,timestamp,like_count,comments_count

# Stories
GET /{ig-user-id}/stories?fields=id,media_type,timestamp
```

---

## Endpoints — Комментарии

```bash
# Получить комментарии
GET /{media-id}/comments?fields=id,text,username,timestamp,replies

# Ответить на комментарий
POST /{comment-id}/replies
  message, access_token

# Скрыть комментарий
POST /{comment-id}
  hide=true, access_token

# Удалить комментарий
DELETE /{comment-id}?access_token={TOKEN}
```

---

## Endpoints — Insights

```bash
# Метрики аккаунта
GET /{ig-user-id}/insights?metric=reach,accounts_engaged,follows_and_unfollows&period=day

# Демография подписчиков
GET /{ig-user-id}/insights?metric=follower_demographics&metric_type=total_value&period=lifetime&breakdown=country

# Метрики поста/Reel
GET /{media-id}/insights?metric=reach,views,likes,comments,shares,saved,total_interactions

# Метрики Stories
GET /{media-id}/insights?metric=reach,views,replies,follows,shares
```

---

## Endpoints — Хэштеги

```bash
# Поиск хэштега (получить ID)
GET /ig_hashtag_search?q=dubaitourism&user_id={IG_USER_ID}

# Top Media по хэштегу
GET /{hashtag-id}/top_media?user_id={IG_USER_ID}&fields=id,caption,permalink,like_count

# Recent Media по хэштегу
GET /{hashtag-id}/recent_media?user_id={IG_USER_ID}&fields=id,caption,permalink
```

---

## Endpoints — Shopping

```bash
# Получить теги товаров
GET /{media-id}/product_tags

# Добавить теги товаров
POST /{media-id}/product_tags
  updated_tags=[{"product_id":"ID","x":0.5,"y":0.5}]

# Удалить теги
DELETE /{media-id}/product_tags

# Товары каталога
GET /{catalog-id}/products?fields=name,price,image_url
```

---

## Endpoints — Mentions и oEmbed

```bash
# Упоминания
GET /{ig-user-id}/mentioned_media?fields=id,caption,media_type,permalink

# oEmbed (встраивание)
GET /instagram_oembed?url={POST_URL}&access_token={APP_TOKEN}
```

---

## Endpoints — Аутентификация

```bash
# OAuth — получить код
GET https://www.facebook.com/v22.0/dialog/oauth?
  client_id={APP_ID}&redirect_uri={URI}&scope=permissions&response_type=code

# Код → Short-lived Token
GET /oauth/access_token?client_id={APP_ID}&redirect_uri={URI}&client_secret={SECRET}&code={CODE}

# Short → Long-lived Token (60 дней)
GET /oauth/access_token?grant_type=fb_exchange_token&client_id={APP_ID}&client_secret={SECRET}&fb_exchange_token={TOKEN}

# Проверка токена
GET /debug_token?input_token={TOKEN}&access_token={APP_ID}|{APP_SECRET}

# Получить Instagram Account ID
GET /me/accounts?fields=instagram_business_account&access_token={TOKEN}
```

---

## Permissions

| Permission | Описание | App Review |
|-----------|---------|-----------|
| `instagram_basic` | Профиль, медиа | Нет |
| `instagram_content_publish` | Публикация | Да |
| `instagram_manage_comments` | Комментарии | Да |
| `instagram_manage_insights` | Аналитика | Да |
| `instagram_shopping_tag_products` | Shopping теги | Да |
| `pages_read_engagement` | Данные Page | Да |
| `pages_show_list` | Список Pages | Нет |

---

## Метрики Insights (v22)

### Аккаунт (period: day/week/days_28)

| Метрика | Описание |
|---------|---------|
| `reach` | Уникальный охват |
| `accounts_engaged` | Аккаунты с взаимодействием |
| `follows_and_unfollows` | Подписки/отписки |
| `profile_views` | Просмотры профиля |
| `follower_demographics` | Демография (breakdown: country/city/age/gender) |

### Медиа

| Метрика | Photo | Video | Carousel | Reel | Story |
|---------|-------|-------|----------|------|-------|
| `reach` | + | + | + | + | + |
| `views` | + | + | + | + | + |
| `likes` | + | + | + | + | - |
| `comments` | + | + | + | + | - |
| `shares` | + | + | + | + | + |
| `saved` | + | + | + | + | - |
| `follows` | + | + | + | + | + |
| `total_interactions` | + | + | + | + | + |
| `replies` | - | - | - | - | + |
| `skip_rate` | - | - | - | + | - |

---

## Rate Limits

| Ресурс | Лимит |
|--------|------|
| API запросы | 200/час (на аккаунт) |
| Публикации | 25/24 часа |
| Hashtag Search | 30 уникальных/7 дней |
| Контейнеры | Истекают через 24 часа |

---

## Требования к медиа

### Фото
- Формат: JPEG, PNG
- Размер: до 8 МБ
- Соотношение: 4:5 — 1.91:1
- Рекомендуемое: 1080x1080 или 1080x1350

### Видео (Feed)
- Формат: MP4, MOV
- Кодек: H.264, AAC
- Размер: до 100 МБ
- Длительность: 3-60 сек
- Разрешение: мин. 540x960

### Reels
- Формат: MP4, MOV
- Кодек: H.264, AAC
- Размер: до 1 ГБ
- Длительность: 3-90 сек
- Соотношение: 9:16
- Разрешение: рекомендуется 1080x1920
- FPS: 24-60

### Stories
- Фото: JPEG/PNG, до 8 МБ
- Видео: MP4/MOV, до 100 МБ, до 60 сек
- Соотношение: 9:16
- Без стикеров через API

---

## Хэштеги для туризма ОАЭ

```
# Высокочастотные
#Dubai #UAE #Travel #Vacation #Tourism

# Среднечастотные
#DubaiTourism #VisitDubai #DubaiLife #AbuDhabi #DubaiTrip

# Низкочастотные
#DesertSafari #DhowCruise #DubaiExcursions #BurjKhalifa #DubaiFrame

# Нишевые
#DubaiLocalGuide #DubaiDealz #UAETourGuide

# Рекомендация: 3 высоко + 3 средне + 3 низко + 1 нишевый = 10
```

---

## Коды ошибок

| Код | Описание | Решение |
|-----|---------|---------|
| #100 | Invalid parameter | Проверьте параметры |
| #190 | Invalid access token | Обновите токен |
| #10 | No permission | App Review |
| #613 | Rate limit | Ждите 1 час |
| #4 | App limit | Ждите 24 часа |
| #368 | Temporarily blocked | Снизьте активность |

---

## Quick Reference: Публикация за 3 шага

```bash
# 1. Контейнер
curl -X POST "https://graph.facebook.com/v22.0/{IG_USER_ID}/media" \
  -F "image_url=https://example.com/photo.jpg" \
  -F "caption=Текст поста #Dubai" \
  -F "access_token={TOKEN}"

# 2. (для видео) Проверить статус
curl "https://graph.facebook.com/v22.0/{CONTAINER_ID}?fields=status_code&access_token={TOKEN}"

# 3. Опубликовать
curl -X POST "https://graph.facebook.com/v22.0/{IG_USER_ID}/media_publish" \
  -F "creation_id={CONTAINER_ID}" \
  -F "access_token={TOKEN}"
```
