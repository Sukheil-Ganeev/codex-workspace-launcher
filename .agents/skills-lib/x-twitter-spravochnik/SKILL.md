---
name: x-twitter-spravochnik
description: "Production-ready руководство по X (Twitter) как платформе для туристического бизнеса ОАЭ. API v2, посты, медиа, аналитика, Spaces, Premium, реклама. Используй когда нужно работать с X/Twitter контентом (НЕ боты)."
---
# X (Twitter) — Платформенный справочник

> Справочник по X (бывший Twitter) — микроблоговая платформа с 600M+ пользователей.
> Охватывает API v2, посты, медиа, поиск, Spaces, Premium, рекламу и аналитику.
> Для туристического бизнеса в ОАЭ (Дубай) с аудиторией СНГ и международной.
> Актуальность: февраль 2026.

> Боты и автоматизация: см. x-twitter-bot-справочник

---

## 1. Обзор платформы

**X (ex-Twitter)** — глобальная микроблоговая платформа реального времени. Основана в 2006, переименована в X в июле 2023 (Elon Musk). Базовый URL: `x.com` (twitter.com редиректит).

### Ключевые характеристики

| Параметр | Значение |
|----------|----------|
| Пользователей | 600M+ (MAU), 250M+ (DAU) |
| Основной контент | Текст (до 280 символов free / 25K Premium) |
| API | v2 (основной), v1.1 (legacy, частично sunset) |
| Базовый URL API | `https://api.x.com/2/` |
| Developer Portal | `https://developer.x.com/` |

### Тарифы API (февраль 2026)

С ноября 2025 X запустил **pay-per-use** модель (кредиты). Старые фиксированные тарифы пока работают параллельно:

| Тариф | Цена | Чтение постов | Запись постов | Примечание |
|-------|------|---------------|---------------|------------|
| Free | $0 | Нет (write-only) | 1 500/мес | Только публикация |
| Basic | $200/мес | 10 000/мес | 50 000/мес | Основной для малого бизнеса |
| Pro | $5 000/мес | 1 000 000/мес | 300 000/мес | Full-archive search |
| Enterprise | Индивидуально | Без лимитов | Без лимитов | Dedicated support |
| Pay-per-use | По кредитам | По факту | По факту | Новая модель с 2026 |

**Pay-per-use:** покупаете кредиты заранее, баланс списывается за каждый вызов API. Разные эндпоинты — разная стоимость. При переходе с Free дают $10 ваучер.

---

## 2. Аутентификация

X API поддерживает три метода авторизации.

### OAuth 2.0 Authorization Code Flow с PKCE (рекомендуемый)

Для действий от имени пользователя. PKCE-совместимый (Proof Key for Code Exchange).

**Эндпоинты:**
- Авторизация: `https://x.com/i/oauth2/authorize`
- Токен: `https://api.x.com/2/oauth2/token`
- Отзыв: `https://api.x.com/2/oauth2/revoke`

**Параметры запроса токена:**
- `code` — код авторизации
- `grant_type` — `authorization_code`
- `client_id` — ID приложения
- `redirect_uri` — URI перенаправления
- `code_verifier` — PKCE верификатор

**Время жизни токенов:**
- Access token: 2 часа
- Refresh token: бессрочный (при scope `offline.access`)

**Scopes:** `tweet.read`, `tweet.write`, `users.read`, `bookmark.read`, `bookmark.write`, `list.read`, `list.write`, `space.read`, `like.read`, `like.write`, `follows.read`, `follows.write`, `offline.access`

### App-only (Bearer Token)

Для чтения публичных данных без контекста пользователя:

```
Authorization: Bearer YOUR_BEARER_TOKEN
```

Получение: `POST https://api.x.com/oauth2/token` с `grant_type=client_credentials`

### OAuth 1.0a (legacy)

Используется для Media Upload API (v1.1). Требует `consumer_key`, `consumer_secret`, `access_token`, `access_token_secret`. HMAC-SHA1 подпись.

---

## 3. Посты (Tweets)

### Создание поста

```
POST https://api.x.com/2/tweets
Authorization: Bearer или OAuth 2.0 User Context
Content-Type: application/json

{
  "text": "Добро пожаловать в Дубай! Desert Safari от $45 #Dubai #UAE"
}
```

### Лимиты текста

| Тип аккаунта | Лимит символов |
|--------------|----------------|
| Free | 280 |
| Premium | 4 000 |
| Premium+ | 25 000 |

### Создание треда

```json
// Первый пост
POST /2/tweets
{"text": "Топ-5 достопримечательностей Дубая - тред"}

// Следующие посты (reply to previous)
POST /2/tweets
{
  "text": "1. Burj Khalifa — 828м, самое высокое здание мира",
  "reply": {"in_reply_to_tweet_id": "ID_ПЕРВОГО_ПОСТА"}
}
```

### Цитирование (Quote Tweet)

```json
POST /2/tweets
{
  "text": "Потрясающий обзор!",
  "quote_tweet_id": "TARGET_TWEET_ID"
}
```

### Удаление поста

```
DELETE https://api.x.com/2/tweets/:id
```

### Scheduling (планирование)

Нативное планирование доступно через веб-интерфейс X и X Pro (TweetDeck). Через API — используйте `scheduled_at` (ISO 8601) при создании Draft Tweet.

### Ключевые эндпоинты постов

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/2/tweets` | Создать пост |
| DELETE | `/2/tweets/:id` | Удалить пост |
| GET | `/2/tweets/:id` | Получить пост |
| GET | `/2/tweets` | Получить несколько постов (до 100 ID) |
| GET | `/2/users/:id/tweets` | Таймлайн пользователя |
| GET | `/2/users/:id/mentions` | Упоминания пользователя |
| POST | `/2/users/:id/likes` | Лайкнуть пост |
| DELETE | `/2/users/:id/likes/:tweet_id` | Убрать лайк |
| POST | `/2/users/:id/retweets` | Ретвитнуть |
| DELETE | `/2/users/:id/retweets/:tweet_id` | Убрать ретвит |

---

## 4. Медиа

### Загрузка медиа

Медиа загружается отдельно, затем привязывается к посту через `media.media_ids`.

**Новый эндпоинт (v2, с января 2025):**
```
POST https://api.x.com/2/media/upload
```

**Legacy (v1.1, sunset июнь 2025):**
```
POST https://upload.twitter.com/1.1/media/upload.json
```

### Лимиты вложений

- До 4 фото в одном посте
- 1 видео ИЛИ 1 GIF на пост
- Нельзя смешивать фото с видео/GIF

### Спецификации медиа

| Тип | Формат | Макс. размер | Разрешение |
|-----|--------|--------------|------------|
| Фото | JPEG, PNG, WebP | 5 МБ | До 4096x4096 |
| GIF | GIF | 15 МБ | До 1280x1080 |
| Видео | MP4 (H.264) | 512 МБ | 720p (free) / 1080p (Premium) |

**Видео детали:**
- Аудио: AAC Low Complexity
- Длительность: до 2 мин 20 сек (free), до 60 мин (Premium+)
- Aspect ratio: 1:2.39 до 2.39:1
- Frame rate: до 60 fps

### Chunked Upload (для видео и GIF)

Для файлов >5 МБ используется chunked upload:
1. `INIT` — инициализация с `media_type` и `total_bytes`
2. `APPEND` — загрузка чанков (до 5 МБ каждый)
3. `FINALIZE` — финализация
4. `STATUS` — проверка обработки (для видео)

### Alt Text (описание для доступности)

```json
POST /2/tweets
{
  "text": "Закат в пустыне",
  "media": {
    "media_ids": ["MEDIA_ID"],
    "alt_text": "Оранжевый закат над дюнами пустыни Руб-эль-Хали"
  }
}
```

---

## 5. Пользователи

### Получение профиля

```
GET https://api.x.com/2/users/:id
GET https://api.x.com/2/users/by/username/:username
```

**Поля пользователя:** `id`, `name`, `username`, `created_at`, `description`, `location`, `profile_image_url`, `public_metrics`, `verified`, `verified_type`

### Подписчики и подписки

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/2/users/:id/followers` | Подписчики |
| GET | `/2/users/:id/following` | Подписки |
| POST | `/2/users/:id/following` | Подписаться |
| DELETE | `/2/users/:id/following/:target_id` | Отписаться |

### Блокировка и мьют

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/2/users/:id/blocking` | Заблокированные |
| POST | `/2/users/:id/blocking` | Заблокировать |
| DELETE | `/2/users/:id/blocking/:target_id` | Разблокировать |
| GET | `/2/users/:id/muting` | Замьюченные |
| POST | `/2/users/:id/muting` | Замьютить |
| DELETE | `/2/users/:id/muting/:target_id` | Размьютить |

---

## 6. Поиск (Search API)

### Эндпоинты

| Тариф | Эндпоинт | Охват |
|-------|----------|-------|
| Free/Basic | `/2/tweets/search/recent` | Последние 7 дней |
| Pro/Enterprise | `/2/tweets/search/all` | Полный архив (с 2006) |

### Операторы поиска

| Оператор | Пример | Описание |
|----------|--------|----------|
| Ключевое слово | `Dubai safari` | Поиск по тексту (AND по умолчанию) |
| `OR` | `Dubai OR Abu Dhabi` | Логическое ИЛИ |
| `-` | `Dubai -rain` | Исключение |
| `""` | `"desert safari"` | Точная фраза |
| `from:` | `from:visitdubai` | Посты конкретного автора |
| `to:` | `to:username` | Ответы пользователю |
| `has:media` | `Dubai has:media` | Только с медиа |
| `has:images` | `Dubai has:images` | Только с фото |
| `has:videos` | `Dubai has:videos` | Только с видео |
| `has:links` | `Dubai has:links` | Только со ссылками |
| `has:hashtags` | `Dubai has:hashtags` | Только с хештегами |
| `lang:` | `lang:ru` | По языку (ISO 639-1) |
| `since:` | `since:2025-01-01` | С даты |
| `until:` | `until:2025-12-31` | До даты |
| `is:retweet` | `Dubai is:retweet` | Только ретвиты |
| `-is:retweet` | `Dubai -is:retweet` | Без ретвитов |
| `is:reply` | `Dubai is:reply` | Только ответы |
| `place:` | `place:"Dubai"` | По геолокации |
| `conversation_id:` | `conversation_id:123` | Тред целиком |

### Пример комплексного запроса

```
"desert safari" (Dubai OR "Abu Dhabi") has:media -is:retweet lang:en since:2025-01-01
```

---

## 7. X Spaces (Аудиокомнаты)

X Spaces — функция live-аудио, аналог Clubhouse.

### Характеристики

| Параметр | Значение |
|----------|----------|
| Макс. слушателей | Без ограничений (тысячи) |
| Макс. спикеров | 13 (1 хост + 2 со-хоста + 10 спикеров) |
| Планирование | До 30 дней вперёд, до 10 Spaces |
| Доступ | Premium+ или 600+ подписчиков |
| Платформы | iOS, Android, Desktop |

### API Spaces

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/2/spaces/:id` | Получить Space по ID |
| GET | `/2/spaces` | Получить несколько Spaces |
| GET | `/2/spaces/by/creator_ids` | Spaces по создателям |
| GET | `/2/spaces/search` | Поиск Spaces |

**Поля Space:** `id`, `state` (live/scheduled/ended), `title`, `host_ids`, `speaker_ids`, `participant_count`, `scheduled_start`, `started_at`, `ended_at`, `lang`, `is_ticketed`

### Применение для туризма

- **Q&A сессии** — «Спроси о Дубае» с экспертами
- **Виртуальные туры** — аудио-описание маршрутов
- **Партнёрские эфиры** — совместно с отелями, экскурсионными компаниями
- **Сезонные анонсы** — новые предложения на зимний/летний сезон

---

## 8. Списки (Lists)

Списки позволяют группировать пользователей для организованного чтения ленты.

### API Lists

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/2/lists` | Создать список |
| PUT | `/2/lists/:id` | Обновить список |
| DELETE | `/2/lists/:id` | Удалить список |
| GET | `/2/lists/:id` | Получить список |
| GET | `/2/users/:id/owned_lists` | Списки пользователя |
| POST | `/2/lists/:id/members` | Добавить участника |
| DELETE | `/2/lists/:id/members/:user_id` | Убрать участника |
| GET | `/2/lists/:id/members` | Участники списка |
| GET | `/2/lists/:id/tweets` | Посты из списка |

### Применение для туризма

- **Конкуренты** — мониторинг постов конкурентов
- **Инфлюенсеры** — список travel-блогеров ОАЭ
- **Партнёры** — отели, авиакомпании, парки
- **СМИ** — туристические медиа и журналисты

---

## 9. Закладки (Bookmarks)

### API Bookmarks

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/2/users/:id/bookmarks` | Получить закладки (до 800) |
| POST | `/2/users/:id/bookmarks` | Добавить в закладки |
| DELETE | `/2/users/:id/bookmarks/:tweet_id` | Убрать из закладок |

**Rate limit:** 180 запросов / 15 мин (GET).

Требуется OAuth 2.0 User Context с scope `bookmark.read` / `bookmark.write`.

---

## 10. X Premium

### Тарифы подписки (2026)

| Тариф | Цена | Верификация | Посты | Реклама | Прочее |
|-------|------|-------------|-------|---------|--------|
| Basic | $3/мес | Нет галочки | 280 символов | Стандартная | Базовые функции |
| Premium | $8/мес | Синяя галочка | 4 000 символов | -50% рекламы | Edit, Grok, монетизация |
| Premium+ | $16/мес* | Синяя галочка | 25 000 символов | Без рекламы | Articles, Radar, макс. Grok |

*Цена Premium+ может варьироваться по регионам ($16-$40).

### Функции Premium

- **Синяя галочка** — верификация, повышение доверия
- **Edit Post** — редактирование постов (30 мин, 5 раз)
- **Длинные посты** — до 4K / 25K символов
- **Grok AI** — встроенный ИИ-ассистент
- **Reader Mode** — удобное чтение тредов
- **Bookmark Folders** — папки для закладок
- **Undo Post** — отмена публикации (до 60 сек)
- **Custom App Icon** — смена иконки приложения

### Влияние на охват

| Тип аккаунта | Средние показы/пост |
|--------------|---------------------|
| Free | ~100 |
| Premium | ~600 (x6) |
| Premium+ | ~1 550 (x15) |

Premium-подписка значительно увеличивает органический охват — в 6-15 раз.

### X Premium для бизнеса (Verified Organizations)

- **Цена:** от $200/мес (базовый), $1 000/мес (полный)
- **Функции:** золотая галочка, аффилированные аккаунты, приоритетная поддержка
- **Применение:** официальная верификация бренда

---

## 11. X Ads (Рекламная платформа)

### Рекламные форматы

| Формат | Описание | Применение |
|--------|----------|------------|
| Promoted Tweets | Обычный пост с продвижением | Охват, вовлечение |
| Promoted Accounts | Рекомендация аккаунта | Рост подписчиков |
| Video Ads | Видео в ленте | Промо экскурсий |
| Carousel Ads | До 6 карточек | Каталог туров |
| Vertical Video | Вертикальное видео (9:16) | Immersive контент |
| Promoted Trends | Трендовый хэштег | Масштабные кампании |

### Таргетинг

- **Демография:** возраст, пол, язык, устройство
- **Геотаргетинг:** страна, регион, город, радиус
- **Интересы:** 350+ категорий (Travel, Luxury, Events...)
- **Поведение:** покупательское поведение, частые путешественники
- **Похожие аудитории (Lookalike):** на основе текущих подписчиков
- **Ключевые слова:** таргетинг по поисковым запросам
- **AI Personas:** ИИ-подобранные аудитории (новое в 2025)
- **Retargeting:** по пикселю сайта, спискам email/телефонов

### Средние затраты (2025-2026)

| Метрика | Среднее значение | Для travel |
|---------|-----------------|------------|
| CPC (клик) | $0.18-$0.74 | $0.50-$1.50 |
| CPM (1000 показов) | $0.86-$3.00 | $2.00-$6.00 |
| CPE (вовлечение) | $0.05-$0.30 | $0.10-$0.25 |
| CTR | 1-3% | 1.5-2.5% |
| Conversion Rate | 1-3% | 1-2% |

### Бюджеты

- **Минимум:** нет формального минимума
- **Тестирование:** $100-$500/мес (рекомендуется)
- **Малый бизнес:** $500-$2 000/мес
- **Средний бизнес:** $2 000-$10 000/мес
- Insertion order (счёт): от $5 000/мес расходов

### Рекламный кабинет

URL: `https://ads.x.com/`

---

## 12. Аналитика

### Tweet Metrics (метрики поста)

Передаются через `tweet.fields=public_metrics,non_public_metrics,organic_metrics`:

| Метрика | Доступность | Описание |
|---------|-------------|----------|
| `impression_count` | non_public | Показы |
| `retweet_count` | public | Ретвиты |
| `reply_count` | public | Ответы |
| `like_count` | public | Лайки |
| `quote_count` | public | Цитирования |
| `bookmark_count` | public | Закладки |
| `url_link_clicks` | non_public | Клики по ссылкам |
| `user_profile_clicks` | non_public | Клики на профиль |

**non_public_metrics** доступны только автору поста через OAuth 2.0 User Context.

### User Metrics

```
GET /2/users/:id?user.fields=public_metrics
```

Возвращает: `followers_count`, `following_count`, `tweet_count`, `listed_count`.

### Engagement Rate (формула)

```
Engagement Rate = (лайки + ретвиты + ответы + цитирования) / показы * 100%
```

Средний ER на X: 0.5-2% (органика), 1-5% (Premium).

### X Analytics Dashboard

Встроенная панель аналитики: `https://analytics.x.com/`
- Доступна всем аккаунтам
- Статистика за 28 дней
- Топ-посты, демография аудитории, тренды

---

## 13. Embed и oEmbed

### oEmbed API

Встраивание постов X на внешние сайты.

**Эндпоинт:**
```
GET https://publish.x.com/oembed?url=https://x.com/user/status/123456
```

**Параметры:**
- `url` — URL поста (обязательный)
- `maxwidth` — максимальная ширина (220-550 px)
- `hide_thread` — скрыть родительский тред (`true`/`false`)
- `hide_media` — скрыть медиа
- `theme` — `light` / `dark`
- `lang` — язык виджета

**Ответ:** HTML-код для встраивания + `widgets.js` скрипт.

### Embedded Timeline

```html
<a class="twitter-timeline" href="https://x.com/visitdubai">
  Posts by @visitdubai
</a>
<script async src="https://platform.x.com/widgets.js" charset="utf-8"></script>
```

### Кнопки X

- Share (поделиться): `https://x.com/intent/tweet?text=...&url=...`
- Follow (подписаться): `https://x.com/intent/follow?screen_name=...`
- Like: `https://x.com/intent/like?tweet_id=...`

---

## 14. Примеры для туризма ОАЭ

### Контент-стратегия

**Типы контента для туристического бизнеса:**

1. **Промо-посты** — акции, скидки, сезонные предложения
2. **Визуальный контент** — фото/видео достопримечательностей
3. **Информационные треды** — гайды, маршруты, лайфхаки
4. **UGC (пользовательский контент)** — репосты отзывов клиентов
5. **Real-time** — погода, события, новости туризма
6. **Polls (опросы)** — вовлечение аудитории

### Хэштеги для Дубая и ОАЭ

**Основные:**
- `#Dubai` — самый популярный, 100M+ постов
- `#UAE` — 57M+ постов
- `#MyDubai` — 20% корреляция с #UAE
- `#VisitDubai` — официальный хэштег туризма
- `#AbuDhabi` — для туров по Абу-Даби

**Нишевые (туризм):**
- `#DubaiTourism` `#DubaiTravel` `#ExploreUAE`
- `#DesertSafari` `#DubaiSafari`
- `#BurjKhalifa` `#DubaiMall` `#PalmJumeirah`
- `#DubaiYacht` `#DubaiLuxury`
- `#DubaiDeals` `#UAEOffers`

**Русскоязычные:**
- `#Дубай` `#ОАЭ` `#ЭмиратыТуризм`
- `#ОтдыхвДубае` `#ТурыДубай`

### Расписание публикаций

| Аудитория | Лучшее время (GMT+4 Dubai) | Дни |
|-----------|---------------------------|-----|
| СНГ (RU/KZ) | 10:00-13:00 | Пн-Пт |
| Международная (EN) | 15:00-19:00 | Вт-Чт |
| Выходные | 11:00-14:00 | Сб |

### Пример промо-поста

```
Desert Safari - незабываемые впечатления!

Джип-сафари по дюнам + BBQ ужин + шоу-программа

От $45/чел (группа)
От $150 (индивидуально)

#Dubai #DesertSafari #UAE #DubaiTourism
```

### Пример треда (маршрут)

```
Пост 1: "Идеальный день в Дубае за $100 — тред"
Пост 2: "Утро: Burj Khalifa (At The Top) — $40. Вид на 360 с 124 этажа"
Пост 3: "День: Old Dubai — Abra boat $0.25 + Gold Souk + Spice Souk"
Пост 4: "Вечер: Dubai Fountain Show — БЕСПЛАТНО. Лучшие места у Burj Park"
Пост 5: "Ужин: Al Fahidi — от $15. Аутентичная арабская кухня"
Пост 6: "Бонус: забронируйте через нас — скидка 10% на любой тур! DM"
```

---

## 15. Rate Limits

### По тарифам

| Эндпоинт | Free | Basic | Pro |
|----------|------|-------|-----|
| POST /2/tweets | 17 req/24h | 100 req/24h | 100 req/15min |
| GET /2/tweets/:id | 15 req/15min | 15 req/15min | 300 req/15min |
| GET /2/tweets/search/recent | 10 req/15min | 60 req/15min | 300 req/15min |
| GET /2/users/:id | 25 req/24h | 25 req/15min | 300 req/15min |
| GET /2/users/:id/followers | 1 req/24h | 15 req/15min | 180 req/15min |
| GET /2/users/:id/tweets | 1 req/24h | 15 req/15min | 180 req/15min |
| GET /2/spaces/search | N/A | 15 req/15min | 300 req/15min |
| GET /2/users/:id/bookmarks | N/A | 180 req/15min | 180 req/15min |

**Месячные лимиты (чтение):**
- Free: 0 (write-only)
- Basic: 10 000 постов/мес
- Pro: 1 000 000 постов/мес

### Заголовки Rate Limit

```
x-rate-limit-limit: 300
x-rate-limit-remaining: 298
x-rate-limit-reset: 1706745600
```

### Обработка ошибки 429 (Too Many Requests)

1. Проверить заголовок `x-rate-limit-reset` (Unix timestamp)
2. Подождать до сброса окна
3. Реализовать exponential backoff
4. Кэшировать ответы где возможно

---

## Таблица ресурсов

| Ресурс | URL |
|--------|-----|
| X Developer Portal | https://developer.x.com/ |
| API v2 Документация | https://developer.x.com/en/docs/twitter-api |
| OAuth 2.0 PKCE Guide | https://developer.x.com/en/docs/authentication/oauth-2-0/authorization-code |
| API Rate Limits | https://developer.x.com/en/docs/twitter-api/rate-limits |
| Media Upload Guide | https://developer.x.com/en/docs/twitter-api/v1/media/upload-media/overview |
| Search Operators | https://developer.x.com/en/docs/twitter-api/tweets/search/integrate/build-a-query |
| Spaces API | https://developer.x.com/en/docs/twitter-api/spaces/overview |
| oEmbed API | https://developer.x.com/en/docs/twitter-for-websites/oembed-api |
| X Ads Manager | https://ads.x.com/ |
| X Analytics | https://analytics.x.com/ |
| X Premium Info | https://help.x.com/en/using-x/x-premium |
| Publish (Embed Tool) | https://publish.x.com/ |
| X Status | https://status.x.com/ |
| Developer Forum | https://devcommunity.x.com/ |
| API Pricing | https://developer.x.com/en/products/twitter-api |
