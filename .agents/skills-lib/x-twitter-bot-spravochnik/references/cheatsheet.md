# Cheatsheet — X (Twitter) Bot API v2

## Endpoints

### Посты (Tweets)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/2/tweets` | Создать пост |
| DELETE | `/2/tweets/:id` | Удалить пост |
| GET | `/2/tweets/:id` | Получить пост по ID |
| GET | `/2/tweets` | Получить посты по массиву ID |
| GET | `/2/users/:id/tweets` | Таймлайн пользователя |
| GET | `/2/users/:id/mentions` | Упоминания пользователя |

### Поиск (Search)

| Метод | Endpoint | Tier | Описание |
|-------|----------|------|----------|
| GET | `/2/tweets/search/recent` | Basic+ | Поиск за 7 дней |
| GET | `/2/tweets/search/all` | Pro+ | Full-archive поиск |
| GET | `/2/tweets/counts/recent` | Basic+ | Счётчик за 7 дней |
| GET | `/2/tweets/counts/all` | Pro+ | Счётчик full-archive |

### Filtered Stream

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/2/tweets/search/stream` | Подключение к стриму |
| GET | `/2/tweets/search/stream/rules` | Получить правила |
| POST | `/2/tweets/search/stream/rules` | Добавить/удалить правила |

### Лайки

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/2/users/:id/likes` | Лайкнуть пост |
| DELETE | `/2/users/:id/likes/:tweet_id` | Убрать лайк |
| GET | `/2/users/:id/liked_tweets` | Лайкнутые посты |

### Ретвиты

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/2/users/:id/retweets` | Ретвитнуть |
| DELETE | `/2/users/:id/retweets/:tweet_id` | Убрать ретвит |

### Подписки (Follows)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/2/users/:id/following` | Подписаться |
| DELETE | `/2/users/:id/following/:target_id` | Отписаться |
| GET | `/2/users/:id/followers` | Подписчики |
| GET | `/2/users/:id/following` | Подписки |

### DM (Direct Messages)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/2/dm_conversations/with/:id/messages` | Отправить DM |
| POST | `/2/dm_conversations` | Создать групповой DM |
| GET | `/2/dm_events` | Получить DM-события |
| GET | `/2/dm_conversations/:id/dm_events` | События конкретного DM |

### Пользователи

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/2/users/me` | Текущий пользователь |
| GET | `/2/users/:id` | По ID |
| GET | `/2/users/by/username/:username` | По username |

### Медиа

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/2/media/upload` | Загрузить медиа (v2) |

---

## Операторы Filtered Stream и Search

### Standalone (можно использовать отдельно)

| Оператор | Пример | Описание |
|----------|--------|----------|
| keyword | `dubai tour` | Содержит слова |
| "exact" | `"desert safari"` | Точная фраза |
| # | `#Dubai` | Хэштег |
| @ | `@botname` | Упоминание |
| from: | `from:visitdubai` | От пользователя |
| to: | `to:botname` | К пользователю |
| url: | `url:"booking.com"` | Содержит URL |
| lang: | `lang:ru` | Язык |
| is:retweet | `-is:retweet` | (Не) ретвит |
| is:reply | `-is:reply` | (Не) ответ |
| is:quote | `is:quote` | Цитата |
| has:media | `has:media` | С медиа |
| has:images | `has:images` | С изображением |
| has:video_link | `has:video_link` | С видео |
| has:links | `has:links` | Со ссылкой |
| has:mentions | `has:mentions` | С упоминанием |
| has:hashtags | `has:hashtags` | С хэштегом |
| has:geo | `has:geo` | С геолокацией |

### Conjunction-required (только с другими операторами)

| Оператор | Пример | Описание |
|----------|--------|----------|
| place_country: | `place_country:AE` | Код страны |
| place: | `place:"Dubai"` | Город |
| conversation_id: | `conversation_id:123` | В треде |
| context: | `context:46.123` | Контекстная аннотация |
| entity: | `entity:"Burj Khalifa"` | Именованная сущность |

### Логика

| Оператор | Пример | Описание |
|----------|--------|----------|
| AND | `dubai tour` (пробел) | Оба слова |
| OR | `dubai OR abu_dhabi` | Любое из слов |
| NOT | `-is:retweet` | Исключить |
| () | `(#Dubai OR #UAE) tour` | Группировка |

---

## Тарифы (быстрая таблица)

| | Free | Basic $200/мес | Pro $5000/мес |
|---|------|----------------|---------------|
| Write | 500/мес App | 50K/мес | 300K/мес |
| Read | 0 | 10K/мес | 1M/мес |
| Stream rules | 0 | 25 | 1,000 |
| Search | Нет | 7 дней | Full-archive |
| DM | Нет | Да | Да |
| Apps | 1 | 2 | 3 |

---

## Rate Limits (ключевые)

| Endpoint | Free | Basic | Pro |
|----------|------|-------|-----|
| POST tweets | 17/24ч | 100/24ч | 100/24ч |
| GET search/recent | - | 60/15мин | 300/15мин |
| GET mentions | - | 180/15мин | 180/15мин |
| POST likes | 5/24ч | 1000/24ч | 1000/24ч |
| POST retweets | - | 5/15мин | 5/15мин |
| GET dm_events | - | 15/15мин | 15/15мин |
| GET users/me | 25/24ч | 75/15мин | 75/15мин |

---

## OAuth 2.0 Scopes

| Scope | Описание |
|-------|----------|
| `tweet.read` | Чтение постов |
| `tweet.write` | Публикация постов |
| `users.read` | Чтение профилей |
| `dm.read` | Чтение DM |
| `dm.write` | Отправка DM |
| `follows.read` | Чтение подписок |
| `follows.write` | Подписка/отписка |
| `like.read` | Чтение лайков |
| `like.write` | Лайк/анлайк |
| `media.write` | Загрузка медиа |
| `offline.access` | Refresh token |
| `space.read` | Чтение Spaces |
| `mute.read` | Чтение мутов |
| `mute.write` | Мут/анмут |
| `block.read` | Чтение блоков |
| `block.write` | Блок/анблок |
| `bookmark.read` | Чтение закладок |
| `bookmark.write` | Закладки |

---

## Быстрые примеры

### Python (tweepy) — публикация

```python
import tweepy

client = tweepy.Client(
    consumer_key="KEY", consumer_secret="SECRET",
    access_token="TOKEN", access_token_secret="TOKEN_SECRET"
)
client.create_tweet(text="Hello!")
```

### Python (tweepy) — поиск

```python
client = tweepy.Client(bearer_token="BEARER")
tweets = client.search_recent_tweets(
    query="#Dubai -is:retweet lang:en",
    max_results=10,
    tweet_fields=["created_at", "public_metrics"]
)
```

### Python (tweepy) — stream

```python
class MyStream(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        print(tweet.text)

stream = MyStream(bearer_token="BEARER")
stream.add_rules(tweepy.StreamRule("#Dubai tourism"))
stream.filter()
```

### Node.js — публикация

```javascript
const { TwitterApi } = require('twitter-api-v2');
const client = new TwitterApi({
    appKey: 'KEY', appSecret: 'SECRET',
    accessToken: 'TOKEN', accessSecret: 'TOKEN_SECRET'
});
await client.v2.tweet('Hello!');
```

### cURL — публикация

```bash
curl -X POST "https://api.x.com/2/tweets" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from cURL!"}'
```

---

## HTTP-заголовки Rate Limit

| Заголовок | Описание |
|-----------|----------|
| `x-rate-limit-limit` | Макс запросов в окне |
| `x-rate-limit-remaining` | Осталось запросов |
| `x-rate-limit-reset` | Unix timestamp сброса |

---

## Медиа-лимиты

| Тип | Макс размер | Кол-во на пост |
|-----|-------------|----------------|
| Изображение (JPEG/PNG/WEBP) | 5 MB | До 4 |
| GIF | 15 MB | 1 |
| Видео (MP4) | 512 MB, 140 сек | 1 |

---

## Коды ошибок

| Код | Описание | Действие |
|-----|----------|----------|
| 400 | Bad Request | Проверить параметры |
| 401 | Unauthorized | Проверить/обновить токены |
| 403 | Forbidden | Проверить тариф/permissions |
| 404 | Not Found | Проверить endpoint/ID |
| 429 | Rate Limited | Ждать x-rate-limit-reset |
| 500 | Server Error | Retry с backoff |
| 503 | Service Unavailable | Retry позже |
