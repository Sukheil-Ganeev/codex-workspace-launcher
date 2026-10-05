# X (Twitter) API v2 — Шпаргалка

## Быстрый старт

```bash
# Bearer Token (App-only)
curl -H "Authorization: Bearer $BEARER_TOKEN" \
  "https://api.x.com/2/tweets/1234567890"

# OAuth 2.0 User Context
curl -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from API!"}' \
  "https://api.x.com/2/tweets"
```

---

## Базовый URL

```
https://api.x.com/2/
```

---

## Посты (Tweets)

| Действие | Метод | Эндпоинт |
|----------|-------|----------|
| Создать пост | POST | `/2/tweets` |
| Удалить пост | DELETE | `/2/tweets/:id` |
| Получить пост | GET | `/2/tweets/:id` |
| Пакет постов | GET | `/2/tweets?ids=1,2,3` |
| Таймлайн юзера | GET | `/2/users/:id/tweets` |
| Упоминания | GET | `/2/users/:id/mentions` |
| Лайкнуть | POST | `/2/users/:id/likes` |
| Убрать лайк | DELETE | `/2/users/:id/likes/:tweet_id` |
| Ретвит | POST | `/2/users/:id/retweets` |
| Убрать ретвит | DELETE | `/2/users/:id/retweets/:tweet_id` |

### Создание поста

```json
{
  "text": "Текст поста",
  "media": {"media_ids": ["ID"]},
  "reply": {"in_reply_to_tweet_id": "ID"},
  "quote_tweet_id": "ID",
  "poll": {"options": ["A","B"], "duration_minutes": 60}
}
```

### Полезные tweet.fields

```
tweet.fields=author_id,created_at,public_metrics,entities,attachments,conversation_id,lang,source
```

---

## Пользователи (Users)

| Действие | Метод | Эндпоинт |
|----------|-------|----------|
| По ID | GET | `/2/users/:id` |
| По username | GET | `/2/users/by/username/:username` |
| Подписчики | GET | `/2/users/:id/followers` |
| Подписки | GET | `/2/users/:id/following` |
| Подписаться | POST | `/2/users/:id/following` |
| Отписаться | DELETE | `/2/users/:id/following/:target_id` |
| Заблокировать | POST | `/2/users/:id/blocking` |
| Разблокировать | DELETE | `/2/users/:id/blocking/:target_id` |
| Замьютить | POST | `/2/users/:id/muting` |
| Размьютить | DELETE | `/2/users/:id/muting/:target_id` |

### Полезные user.fields

```
user.fields=created_at,description,location,profile_image_url,public_metrics,verified,verified_type
```

---

## Поиск (Search)

| Тариф | Эндпоинт |
|-------|----------|
| Free/Basic | `/2/tweets/search/recent` (7 дней) |
| Pro+ | `/2/tweets/search/all` (полный архив) |

### Операторы поиска

```
# Базовые
keyword                  — по слову
"exact phrase"           — точная фраза
word1 OR word2           — ИЛИ
-exclude                 — исключить
#hashtag                 — по хэштегу
@mention                 — по упоминанию

# Фильтры автора
from:username            — от пользователя
to:username              — ответы пользователю

# Фильтры контента
has:media                — с медиа
has:images               — с фото
has:videos               — с видео
has:links                — со ссылками
has:hashtags             — с хэштегами
has:mentions             — с упоминаниями

# Фильтры даты
since:2025-01-01         — с даты
until:2025-12-31         — до даты

# Фильтры типа
is:retweet / -is:retweet — ретвиты
is:reply / -is:reply     — ответы
is:quote / -is:quote     — цитирования

# Локация и язык
lang:ru                  — по языку
place:"Dubai"            — по месту
place_country:AE         — по стране

# Тред
conversation_id:123      — весь тред
```

### Пример комплексного запроса

```
"desert safari" (Dubai OR "Abu Dhabi") has:media -is:retweet lang:en since:2025-01-01
```

---

## Медиа (Media Upload)

```bash
# Фото (простая загрузка)
curl -X POST "https://api.x.com/2/media/upload" \
  -H "Authorization: OAuth ..." \
  -F "media=@photo.jpg"

# Видео (chunked upload)
# 1. INIT
curl -X POST "https://upload.twitter.com/1.1/media/upload.json" \
  -d "command=INIT&total_bytes=SIZE&media_type=video/mp4"

# 2. APPEND (для каждого чанка)
curl -X POST "https://upload.twitter.com/1.1/media/upload.json" \
  -F "command=APPEND" -F "media_id=ID" -F "segment_index=0" -F "media=@chunk"

# 3. FINALIZE
curl -X POST "https://upload.twitter.com/1.1/media/upload.json" \
  -d "command=FINALIZE&media_id=ID"
```

### Лимиты медиа

| Тип | Размер | Формат | Кол-во |
|-----|--------|--------|--------|
| Фото | 5 МБ | JPEG, PNG, WebP | До 4 |
| GIF | 15 МБ | GIF | 1 |
| Видео | 512 МБ | MP4 (H.264) | 1 |

---

## Списки (Lists)

| Действие | Метод | Эндпоинт |
|----------|-------|----------|
| Создать | POST | `/2/lists` |
| Обновить | PUT | `/2/lists/:id` |
| Удалить | DELETE | `/2/lists/:id` |
| Мои списки | GET | `/2/users/:id/owned_lists` |
| Добавить участника | POST | `/2/lists/:id/members` |
| Убрать участника | DELETE | `/2/lists/:id/members/:user_id` |
| Посты списка | GET | `/2/lists/:id/tweets` |

---

## Закладки (Bookmarks)

| Действие | Метод | Эндпоинт |
|----------|-------|----------|
| Получить | GET | `/2/users/:id/bookmarks` |
| Добавить | POST | `/2/users/:id/bookmarks` |
| Убрать | DELETE | `/2/users/:id/bookmarks/:tweet_id` |

---

## Spaces

| Действие | Метод | Эндпоинт |
|----------|-------|----------|
| По ID | GET | `/2/spaces/:id` |
| Пакет | GET | `/2/spaces?ids=1,2` |
| По создателям | GET | `/2/spaces/by/creator_ids` |
| Поиск | GET | `/2/spaces/search?query=Dubai` |

---

## Embed / oEmbed

```bash
# oEmbed API
curl "https://publish.x.com/oembed?url=https://x.com/user/status/123&theme=dark"

# HTML виджет
<a class="twitter-timeline" href="https://x.com/visitdubai">@visitdubai</a>
<script async src="https://platform.x.com/widgets.js"></script>

# Intent URLs
https://x.com/intent/tweet?text=Hello&url=https://example.com
https://x.com/intent/follow?screen_name=visitdubai
https://x.com/intent/like?tweet_id=123456
```

---

## OAuth 2.0 PKCE

```bash
# 1. Авторизация (браузер)
https://x.com/i/oauth2/authorize?
  response_type=code&
  client_id=CLIENT_ID&
  redirect_uri=REDIRECT&
  scope=tweet.read+tweet.write+users.read+offline.access&
  state=STATE&
  code_challenge=CHALLENGE&
  code_challenge_method=S256

# 2. Обмен кода на токен
curl -X POST "https://api.x.com/2/oauth2/token" \
  -d "code=AUTH_CODE&grant_type=authorization_code&client_id=CLIENT_ID&redirect_uri=REDIRECT&code_verifier=VERIFIER"

# 3. Обновление токена
curl -X POST "https://api.x.com/2/oauth2/token" \
  -d "refresh_token=REFRESH&grant_type=refresh_token&client_id=CLIENT_ID"

# 4. Отзыв токена
curl -X POST "https://api.x.com/2/oauth2/revoke" \
  -d "token=TOKEN&client_id=CLIENT_ID"
```

### Scopes

```
tweet.read    tweet.write    users.read
like.read     like.write     follows.read    follows.write
bookmark.read bookmark.write list.read       list.write
space.read    offline.access
```

---

## Rate Limits (основные)

| Эндпоинт | Free | Basic | Pro |
|----------|------|-------|-----|
| POST /2/tweets | 17/24h | 100/24h | 100/15min |
| GET /2/tweets/:id | 15/15min | 15/15min | 300/15min |
| GET search/recent | 10/15min | 60/15min | 300/15min |
| GET /2/users/:id | 25/24h | 25/15min | 300/15min |
| GET followers | 1/24h | 15/15min | 180/15min |

### Заголовки ответа

```
x-rate-limit-limit: 300
x-rate-limit-remaining: 298
x-rate-limit-reset: 1706745600   # Unix timestamp
```

---

## Тарифы API

| Тариф | Цена | Чтение | Запись |
|-------|------|--------|-------|
| Free | $0 | 0 (write-only) | 1 500/мес |
| Basic | $200/мес | 10 000/мес | 50 000/мес |
| Pro | $5 000/мес | 1 000 000/мес | 300 000/мес |
| Pay-per-use | По кредитам | По факту | По факту |

---

## X Premium (подписки)

| Тариф | Цена | Галочка | Символы | Реклама |
|-------|------|---------|---------|---------|
| Basic | $3/мес | Нет | 280 | Стандарт |
| Premium | $8/мес | Синяя | 4 000 | -50% |
| Premium+ | $16-40/мес | Синяя | 25 000 | Нет |
| Verified Org | $200+/мес | Золотая | 25 000 | Нет |

---

## Хэштеги для Дубая/ОАЭ

```
#Dubai #UAE #MyDubai #VisitDubai #AbuDhabi
#DubaiTourism #DesertSafari #BurjKhalifa #DubaiTravel
#ExploreUAE #DubaiLuxury #DubaiYacht #DubaiDeals
#Дубай #ОАЭ #ОтдыхвДубае #ТурыДубай
```

---

## Коды ошибок

| Код | Значение | Что делать |
|-----|----------|------------|
| 400 | Bad Request | Проверить JSON/параметры |
| 401 | Unauthorized | Обновить/проверить токен |
| 403 | Forbidden | Проверить тариф/scopes |
| 404 | Not Found | Проверить ID/endpoint |
| 429 | Rate Limited | Подождать reset, backoff |
| 500 | Server Error | Повторить позже |
| 503 | Service Unavailable | X перегружен, повторить |

---

## Полезные ссылки

- Developer Portal: https://developer.x.com/
- API Docs: https://developer.x.com/en/docs/twitter-api
- Ads Manager: https://ads.x.com/
- Analytics: https://analytics.x.com/
- Embed Tool: https://publish.x.com/
- Status: https://status.x.com/
- Forum: https://devcommunity.x.com/
