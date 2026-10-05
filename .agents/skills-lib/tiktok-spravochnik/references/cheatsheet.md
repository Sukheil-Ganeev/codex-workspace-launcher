# TikTok Cheatsheet — Шпаргалка

## Базовые URL

| Сервис | URL |
|--------|-----|
| API Base | `https://open.tiktokapis.com/v2/` |
| Auth | `https://www.tiktok.com/v2/auth/authorize/` |
| Token | `https://open.tiktokapis.com/v2/oauth/token/` |
| Business API | `https://business-api.tiktok.com/open_api/v1.3/` |
| oEmbed | `https://www.tiktok.com/oembed` |
| Embed JS | `https://www.tiktok.com/embed.js` |

## Авторизация (OAuth 2.0 + PKCE)

```
# 1. Редирект на авторизацию
GET https://www.tiktok.com/v2/auth/authorize/
  ?client_key={key}&scope=user.info.basic,video.publish
  &response_type=code&redirect_uri={uri}
  &state={csrf}&code_challenge={challenge}
  &code_challenge_method=S256

# 2. Обмен code -> token
POST https://open.tiktokapis.com/v2/oauth/token/
  client_key={key}&client_secret={secret}
  &code={code}&grant_type=authorization_code
  &redirect_uri={uri}&code_verifier={verifier}

# 3. Обновление токена
POST https://open.tiktokapis.com/v2/oauth/token/
  client_key={key}&client_secret={secret}
  &grant_type=refresh_token&refresh_token={token}
```

**Токены:** access = 24ч, refresh = 365 дней

## Content Posting

```
# Прямая публикация видео
POST /v2/post/publish/video/init/
Authorization: Bearer {token}
{
  "post_info": {
    "title": "...",
    "privacy_level": "PUBLIC_TO_EVERYONE"
  },
  "source_info": {
    "source": "FILE_UPLOAD",
    "video_size": 50000000,
    "chunk_size": 10000000,
    "total_chunk_count": 5
  }
}

# Публикация фото
POST /v2/post/publish/content/init/
{ "media_type": "PHOTO", "post_mode": "DIRECT_POST" }

# Черновик (inbox)
POST /v2/post/publish/inbox/video/init/

# Статус публикации
POST /v2/post/publish/status/fetch/
{ "publish_id": "{id}" }
```

**Лимиты:** 15 постов/день/юзер, 6 req/min/token

## User Info

```
GET /v2/user/info/?fields=open_id,display_name,avatar_url,
  bio_description,follower_count,likes_count,video_count
Authorization: Bearer {token}
```

## Video Management

```
# Список видео
POST /v2/video/list/
{ "max_count": 20 }

# Информация о видео
POST /v2/video/query/
{
  "filters": { "video_ids": ["123"] },
  "fields": ["id","title","like_count","view_count"]
}
```

## oEmbed (без авторизации)

```
GET https://www.tiktok.com/oembed?url=https://www.tiktok.com/@user/video/123
```

## Research API

```
# Поиск видео
POST /v2/research/video/query/
{
  "query": {"and": [
    {"field_name": "keyword", "field_values": ["dubai"]},
    {"field_name": "region_code", "field_values": ["AE"]}
  ]},
  "start_date": "20250101",
  "end_date": "20250201",
  "max_count": 100
}

# Хэштеги
POST /v2/research/hashtag/query/
```

**Лимиты:** 1000 req/день, 100K записей/день

## Ads Manager API

```
# Создание кампании
POST https://business-api.tiktok.com/open_api/v1.3/campaign/create/
{
  "advertiser_id": "123",
  "campaign_name": "...",
  "objective_type": "TRAFFIC",
  "budget_mode": "BUDGET_MODE_DAY",
  "budget": 5000
}
```

**Мин. бюджеты:** Campaign $50/день, Ad Group $20/день

## Видео спецификации

| Параметр | Значение |
|----------|----------|
| Разрешение | 1080x1920 (рекомендовано) |
| Аспект | 9:16 вертикальное |
| Форматы | MP4, MOV (H.264 + AAC) |
| Размер | до 500 МБ (web) |
| Длительность | 3 сек — 60 мин |
| Photo Mode | до 35 фото |

## Рекламные форматы

| Формат | Длительность | Особенности |
|--------|-------------|-------------|
| In-Feed | 5-60 сек | В ленте FYP, рекомендовано 21-34 сек |
| TopView | 5-60 сек | При открытии приложения, full screen |
| Brand Takeover | 3-5 сек | 1 рекламодатель/день |
| Spark Ads | любая | Буст органического контента |
| Branded Hashtag | 9-60 сек intro | Челлендж + лендинг |
| Branded Effects | — | AR-фильтры бренда |
| Carousel | — | До 10 изображений |

## Promote (быстрый буст)

| Параметр | Значение |
|----------|----------|
| Мин. бюджет | $3/день |
| Макс. длительность | 7 дней |
| Цели | Views, Followers, Profile Views, Messages, Website |
| Таргетинг | Авто или ручной (пол, возраст, интересы, локация) |

## Scopes

| Scope | Описание |
|-------|----------|
| user.info.basic | Аватар, имя |
| user.info.profile | Био, ссылки |
| user.info.stats | Подписчики, лайки |
| video.list | Список видео |
| video.publish | Публикация |
| video.upload | Загрузка |
| research.data.basic | Research API |

## Rate Limits

| Эндпоинт | Лимит |
|----------|-------|
| /video/list/ | 600 req/min |
| Content Posting | 6 req/min/token |
| Research API | 1000 req/day |
| Research записи | 100K/day |
| Followers API | 20K calls/day |

Квоты сбрасываются в 12:00 UTC.

## Хэштеги для туризма ОАЭ

**Массовые:** #Dubai #UAE #VisitDubai #MyDubai #AbuDhabi
**Нишевые:** #DubaiSafari #DesertSafari #BurjKhalifa #DubaiMarina #PalmJumeirah
**Активности:** #DubaiYacht #DubaiCars #LuxuryDubai #DubaiFood
**РУ:** #Дубай #ОАЭ #ЭкскурсииДубай #ОтдыхДубай

**Формула:** 1 массовый + 1-2 нишевых + 2-3 микро-нишевых + 1 брендовый

## Аналитика — ключевые метрики

| Метрика | Хороший показатель |
|---------|-------------------|
| Avg Watch Time | 15-20 сек+ |
| Full Video Views | 30%+ |
| Engagement Rate | 5-10% |
| Like Rate | 3-5% |
| Comment Rate | 0.5-1% |
| Share Rate | 0.5-1% |

## Embed HTML

```html
<blockquote class="tiktok-embed"
  cite="https://www.tiktok.com/@user/video/123"
  data-video-id="123"
  style="max-width:605px;min-width:325px;">
  <section></section>
</blockquote>
<script async src="https://www.tiktok.com/embed.js"></script>
```

## Privacy Levels (для публикаций)

| Значение | Доступ |
|----------|--------|
| PUBLIC_TO_EVERYONE | Все |
| MUTUAL_FOLLOW_FRIENDS | Взаимные подписчики |
| FOLLOWER_OF_CREATOR | Подписчики |
| SELF_ONLY | Только автор |

## Коды ошибок

| Код | Описание |
|-----|----------|
| 10003 | Invalid redirect_uri |
| 10005 | Rate limit exceeded |
| 10006 | Daily post limit exceeded |
| 10008 | Access token expired |
| 10010 | Daily quota exceeded |
