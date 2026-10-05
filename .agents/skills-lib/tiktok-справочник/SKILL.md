---
name: tiktok-справочник
description: "Production-ready руководство по TikTok для туристического бизнеса ОАЭ. Content Posting API, аналитика, TikTok Shop, Promote, тренды. Используй когда нужно работать с TikTok контентом и маркетингом."
---
# TikTok — Справочник платформы

## 1. Обзор

**TikTok** — глобальная платформа коротких видео от ByteDance (Китай, 2016). Международная версия Douyin.

### Ключевые факты

| Параметр | Значение |
|----------|----------|
| Владелец | ByteDance Ltd. |
| Запуск | Сентябрь 2016 (Douyin), Сентябрь 2017 (TikTok) |
| MAU | 1.5+ млрд (2025) |
| Основной контент | Короткие видео (15 сек — 60 мин) |
| Алгоритм | For You Page (FYP) — персонализированная лента |
| Монетизация | TikTok Ads, TikTok Shop, Creator Fund, LIVE Gifts |
| Девпортал | https://developers.tiktok.com/ |
| Бизнес-портал | https://ads.tiktok.com/ |
| Creative Center | https://ads.tiktok.com/business/creativecenter/ |

### Экосистема продуктов

- **TikTok App** — основное приложение (iOS, Android, Web)
- **TikTok for Business** — рекламная платформа
- **TikTok Shop** — e-commerce внутри TikTok
- **TikTok Studio** — аналитика и управление контентом
- **TikTok LIVE** — прямые трансляции
- **CapCut** — видеоредактор от ByteDance (интеграция с TikTok)
- **TikTok Creative Center** — тренды, шаблоны, AI-инструменты

### Отличие от других платформ

TikTok **НЕ имеет Bot API** в классическом смысле (как Telegram, VK, WhatsApp). Вместо этого предлагает:
- Content Posting API — публикация контента
- Login Kit — авторизация пользователей
- Research API — аналитика и исследования
- Embed API — встраивание видео на сайты
- Business API — управление рекламой

---

## 2. Аутентификация

### 2.1. Регистрация приложения

1. Зарегистрироваться на https://developers.tiktok.com/
2. Создать приложение (App) в Developer Portal
3. Получить `client_key` и `client_secret`
4. Настроить Redirect URI
5. Выбрать нужные Scopes (разрешения)

### 2.2. Login Kit (OAuth 2.0 + PKCE)

Login Kit — основной способ авторизации пользователей. Поддерживает OAuth 2.0 с PKCE.

**Платформы:**
- Web (redirect-based)
- iOS / Android (TikTok OpenSDK)
- Desktop (QR-код авторизация)
- QR Code (POST `https://open.tiktokapis.com/v2/oauth/get_qrcode/`)

**Флоу авторизации (Web):**

```
1. Приложение → редирект на TikTok Authorization Server
   GET https://www.tiktok.com/v2/auth/authorize/
   ?client_key={client_key}
   &scope={scopes}
   &response_type=code
   &redirect_uri={redirect_uri}
   &state={csrf_token}
   &code_challenge={code_challenge}
   &code_challenge_method=S256

2. Пользователь авторизуется → TikTok редиректит обратно
   {redirect_uri}?code={auth_code}&state={csrf_token}

3. Обмен code на access_token
   POST https://open.tiktokapis.com/v2/oauth/token/
   Body: client_key, client_secret, code, grant_type=authorization_code,
         redirect_uri, code_verifier
```

**Токены:**
| Тип | Срок жизни | Обновление |
|-----|-----------|------------|
| access_token | 24 часа | Через refresh_token |
| refresh_token | 365 дней | Автоматически при обновлении access_token |

### 2.3. Server-to-Server Auth

Для серверных интеграций без участия пользователя (например, TikTok Ads API):

```
POST https://open.tiktokapis.com/v2/oauth/token/
Content-Type: application/x-www-form-urlencoded

client_key={client_key}
&client_secret={client_secret}
&grant_type=client_credentials
```

### 2.4. Scopes (разрешения)

| Scope | Доступ |
|-------|--------|
| user.info.basic | Аватар, display name |
| user.info.profile | Био, ссылки |
| user.info.stats | Подписчики, лайки |
| video.list | Публичные видео |
| video.publish | Публикация видео |
| video.upload | Загрузка видео |
| research.adlib.basic | Research API |
| research.data.basic | Данные исследований |

**Важно:** все scopes требуют явного согласия пользователя. Неаудированные приложения ограничены 5 пользователями и приватным режимом контента.

---

## 3. Content Posting API

Позволяет публиковать видео и фото напрямую в TikTok из вашего приложения.

### 3.1. Direct Post (прямая публикация)

```
POST https://open.tiktokapis.com/v2/post/publish/video/init/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "post_info": {
    "title": "Desert Safari in Dubai! #dubai #safari",
    "privacy_level": "PUBLIC_TO_EVERYONE",
    "disable_duet": false,
    "disable_comment": false,
    "disable_stitch": false,
    "video_cover_timestamp_ms": 1000
  },
  "source_info": {
    "source": "FILE_UPLOAD",
    "video_size": 50000000,
    "chunk_size": 10000000,
    "total_chunk_count": 5
  }
}
```

**Уровни приватности:**
- `PUBLIC_TO_EVERYONE` — видно всем
- `MUTUAL_FOLLOW_FRIENDS` — только взаимные подписчики
- `FOLLOWER_OF_CREATOR` — подписчики автора
- `SELF_ONLY` — только автору

### 3.2. Photo Mode (публикация фото)

```
POST https://open.tiktokapis.com/v2/post/publish/content/init/
Authorization: Bearer {access_token}

{
  "post_info": {
    "title": "Burj Khalifa views",
    "privacy_level": "PUBLIC_TO_EVERYONE"
  },
  "source_info": {
    "source": "FILE_UPLOAD"
  },
  "post_mode": "DIRECT_POST",
  "media_type": "PHOTO"
}
```

### 3.3. Upload (черновик)

Загрузка видео как черновика — пользователь получает уведомление в TikTok и может опубликовать вручную:

```
POST https://open.tiktokapis.com/v2/post/publish/inbox/video/init/
```

### 3.4. Ограничения

| Параметр | Лимит |
|----------|-------|
| Публикаций/день на пользователя | 15 |
| Пользователей для неаудированного приложения | 5 в 24ч |
| Видимость неаудированного контента | Только приватный |
| Максимум фото в Photo Mode | 35 |

**Аудит приложения:** после тестирования необходимо пройти аудит TikTok для снятия ограничений на видимость контента.

---

## 4. Video Management

### 4.1. Статус публикации

```
POST https://open.tiktokapis.com/v2/post/publish/status/fetch/
Authorization: Bearer {access_token}

{
  "publish_id": "{publish_id}"
}
```

**Статусы:** `PROCESSING_UPLOAD`, `PROCESSING_DOWNLOAD`, `PUBLISH_COMPLETE`, `FAILED`

### 4.2. Список видео пользователя

```
POST https://open.tiktokapis.com/v2/video/list/
Authorization: Bearer {access_token}

{
  "max_count": 20
}
```

Ответ содержит: `id`, `title`, `cover_image_url`, `share_url`, `create_time`, `like_count`, `comment_count`, `share_count`, `view_count`, `duration`.

### 4.3. Получение информации о видео

```
POST https://open.tiktokapis.com/v2/video/query/
Authorization: Bearer {access_token}

{
  "filters": {
    "video_ids": ["7123456789012345678"]
  },
  "fields": ["id", "title", "like_count", "view_count", "share_count"]
}
```

---

## 5. User Info

### 5.1. Базовая информация

```
GET https://open.tiktokapis.com/v2/user/info/
?fields=open_id,union_id,avatar_url,display_name
Authorization: Bearer {access_token}
```

### 5.2. Расширенный профиль

```
GET https://open.tiktokapis.com/v2/user/info/
?fields=open_id,display_name,bio_description,profile_deep_link,
        is_verified,follower_count,following_count,likes_count,
        video_count
Authorization: Bearer {access_token}
```

| Поле | Описание |
|------|----------|
| open_id | Уникальный ID пользователя для вашего приложения |
| union_id | ID пользователя между приложениями одного разработчика |
| display_name | Отображаемое имя |
| avatar_url | URL аватара |
| bio_description | Описание профиля |
| follower_count | Количество подписчиков |
| likes_count | Общее количество лайков |
| video_count | Количество публичных видео |

---

## 6. TikTok Embed

### 6.1. oEmbed API

Встраивание TikTok видео на сайт через oEmbed (спецификация https://oembed.com/):

```
GET https://www.tiktok.com/oembed?url={video_url}
```

**Пример:**
```
GET https://www.tiktok.com/oembed?url=https://www.tiktok.com/@user/video/7123456789
```

**Ответ:**
```json
{
  "version": "1.0",
  "type": "video",
  "title": "Desert safari Dubai",
  "author_url": "https://www.tiktok.com/@user",
  "author_name": "user",
  "width": 325,
  "height": 738,
  "html": "<blockquote class=\"tiktok-embed\"...>...</blockquote>",
  "thumbnail_url": "https://...",
  "thumbnail_width": 720,
  "thumbnail_height": 1280
}
```

**Аутентификация не требуется** — oEmbed API публичный.

### 6.2. JavaScript SDK для Embed

```html
<blockquote class="tiktok-embed" cite="https://www.tiktok.com/@user/video/123"
  data-video-id="123" style="max-width: 605px; min-width: 325px;">
  <section></section>
</blockquote>
<script async src="https://www.tiktok.com/embed.js"></script>
```

### 6.3. Creator Profile Embed

Встраивание профиля создателя:
```html
<blockquote class="tiktok-embed" cite="https://www.tiktok.com/@username"
  data-unique-id="username" data-embed-type="creator">
  <section></section>
</blockquote>
<script async src="https://www.tiktok.com/embed.js"></script>
```

---

## 7. Research API

Research API предоставляет доступ к публичным данным TikTok для исследований и аналитики.

### 7.1. Доступ

- Требуется отдельная заявка на https://developers.tiktok.com/
- Доступен для академических исследователей, журналистов, организаций
- Ограничен по квотам (1000 запросов/день, 100 000 записей/день)

### 7.2. Поиск видео

```
POST https://open.tiktokapis.com/v2/research/video/query/
Authorization: Bearer {access_token}

{
  "query": {
    "and": [
      {"field_name": "keyword", "field_values": ["dubai safari"]},
      {"field_name": "region_code", "field_values": ["AE"]}
    ]
  },
  "start_date": "20250101",
  "end_date": "20250201",
  "max_count": 100,
  "fields": ["id", "video_description", "create_time", "like_count", "view_count"]
}
```

### 7.3. Хэштеги и тренды

```
POST https://open.tiktokapis.com/v2/research/hashtag/query/
```

Позволяет получить:
- Популярность хэштегов по регионам
- Временные тренды (7/30/120 дней)
- Связанные хэштеги
- Количество видео и просмотров

### 7.4. TikTok Shop Research

```
POST https://open.tiktokapis.com/v2/research/tiktok_shop/query/
```

Данные о товарах, магазинах и продажах в TikTok Shop.

---

## 8. TikTok Shop

E-commerce платформа внутри TikTok. Позволяет продавать товары прямо в видео и LIVE-трансляциях.

### 8.1. Возможности

- **Product Showcase** — витрина товаров в профиле
- **Video Shopping** — карточки товаров в видео
- **LIVE Shopping** — продажа через прямые трансляции
- **Shop Tab** — вкладка магазина в приложении TikTok
- **Affiliate Program** — партнёрка для создателей

### 8.2. Каталог товаров (API)

```
POST https://open.tiktokapis.com/v2/shop/product/
Authorization: Bearer {access_token}

{
  "title": "Dubai Desert Safari VIP Ticket",
  "description": "Private desert safari with BBQ dinner...",
  "category_id": "tourism_experiences",
  "price": {
    "amount": "25000",
    "currency": "AED"
  },
  "images": [{"url": "https://..."}],
  "inventory": {"quantity": 100}
}
```

### 8.3. Управление заказами

- Получение заказов: `GET /v2/shop/orders/`
- Обновление статуса: `POST /v2/shop/orders/{order_id}/ship/`
- Отмена: `POST /v2/shop/orders/{order_id}/cancel/`

### 8.4. Для туризма ОАЭ

TikTok Shop подходит для продажи:
- Билетов на достопримечательности (Burj Khalifa, Dubai Frame, парки)
- Экскурсионных пакетов (Desert Safari, City Tour)
- Ваучеров на яхты и автомобили
- Подарочных сертификатов

**Важно:** TikTok Shop доступен не во всех регионах. Для ОАЭ проверяйте текущую доступность на https://seller.tiktok.com/.

---

## 9. TikTok Promote

Встроенный инструмент продвижения видео прямо из приложения TikTok (без Ads Manager).

### 9.1. Цели продвижения

| Цель | Описание |
|------|----------|
| More Views | Увеличение просмотров видео |
| More Followers | Привлечение подписчиков |
| More Profile Views | Трафик на профиль |
| More Messages | Стимулирование личных сообщений |
| Website Visits | Переходы на сайт |

### 9.2. Таргетинг

- **Автоматический** — TikTok подбирает аудиторию
- **Ручной** — настройка по параметрам:
  - Пол (мужской / женский / все)
  - Возраст (13-17, 18-24, 25-34, 35-44, 45-54, 55+)
  - Интересы (Travel, Food, Luxury, Adventure и др.)
  - Локация (по странам / регионам)

### 9.3. Бюджет и длительность

| Параметр | Значение |
|----------|----------|
| Минимальный бюджет | $3/день |
| Максимальная длительность | 7 дней |
| Оплата | С привязанной карты |
| Promotional Pack | Гарантированный минимум просмотров |

### 9.4. Boost Creator Content

Бизнес-аккаунты могут продвигать контент создателей, с которыми сотрудничают (включая LIVE-трансляции).

---

## 10. TikTok Ads Manager

Полноценная рекламная платформа: https://ads.tiktok.com/

### 10.1. Форматы рекламы

| Формат | Описание | Где показывается |
|--------|----------|------------------|
| **In-Feed Ads** | Видео в ленте For You | FYP, между органическим контентом |
| **TopView** | Полноэкранное видео при открытии приложения | Первое, что видит пользователь (5-60 сек) |
| **Branded Hashtag Challenge** | Спонсированный челлендж с хэштегом | Discover Page + лендинг |
| **Brand Takeover** | 3-5 сек полноэкранная реклама | При открытии приложения (1 рекламодатель/день) |
| **Branded Effects** | AR-фильтры и эффекты бренда | Камера TikTok |
| **Spark Ads** | Продвижение существующего органического контента | FYP |
| **Carousel Ads** | До 10 изображений с прокруткой | Лента |

### 10.2. Спецификации видеорекламы

| Параметр | Требование |
|----------|-----------|
| Разрешение | 720x1280 (рекомендовано 1080x1920) |
| Соотношение сторон | 9:16 (рекомендовано), 16:9, 1:1 |
| Форматы | MP4, MOV, MPEG, 3GP, AVI |
| Размер файла | До 500 МБ |
| Длительность (In-Feed) | 5-60 сек (рекомендовано 21-34 сек) |
| Длительность (TopView) | 5-60 сек |
| Хэштег (Branded) | До 70 символов (рекомендовано до 18) |

### 10.3. Структура кампании

```
Campaign (цель)
  └── Ad Group (таргетинг, бюджет, расписание)
       └── Ad (креатив — видео/изображение + текст)
```

### 10.4. Цели кампаний

- **Awareness:** Reach, Video Views
- **Consideration:** Traffic, App Installs, Lead Generation, Community Interaction
- **Conversion:** Website Conversions, Product Sales (TikTok Shop)

### 10.5. Бюджеты

| Уровень | Минимальный бюджет |
|---------|-------------------|
| Campaign (дневной) | $50 |
| Campaign (lifetime) | $50 |
| Ad Group (дневной) | $20 |

### 10.6. TikTok Ads API

```
POST https://business-api.tiktok.com/open_api/v1.3/campaign/create/
Authorization: Bearer {access_token}

{
  "advertiser_id": "123456",
  "campaign_name": "Dubai Safari Promo",
  "objective_type": "TRAFFIC",
  "budget_mode": "BUDGET_MODE_DAY",
  "budget": 5000
}
```

Документация: https://business-api.tiktok.com/portal/docs

---

## 11. TikTok Creative Center

Бесплатный инструмент для анализа трендов: https://ads.tiktok.com/business/creativecenter/

### 11.1. Разделы

| Раздел | Что содержит |
|--------|-------------|
| **Trending Hashtags** | Популярные хэштеги по регионам и индустриям |
| **Trending Songs** | Трендовые звуки и музыка |
| **Trending Creators** | Топ-создатели контента |
| **Trending Videos** | Вирусные видео |
| **Top Ads** | Лучшая реклама по индустриям |
| **Keyword Insights** | Анализ ключевых слов |

### 11.2. Фильтры

- **Регион:** 50+ стран (включая UAE, Russia, Kazakhstan)
- **Период:** 7 / 30 / 120 дней
- **Индустрия:** 16 категорий (Travel, Food & Beverage, Luxury и др.)
- **Бизнес-использование:** фильтр звуков для коммерческого использования

### 11.3. Symphony AI (2025)

AI-помощник TikTok для создания контента:
- **Symphony Assistant** — генерация скриптов для видео
- **Symphony Creative Studio** — автоматическое создание видео
- **Symphony Ads Manager** — AI-оптимизация рекламных кампаний

---

## 12. Хэштеги и тренды

### 12.1. Стратегия хэштегов (2025-2026)

Алгоритм TikTok 2025+ приоритизирует "Meaningful Engagement" — микро-нишевые хэштеги работают лучше массовых.

**Формула:** 3-5 специфических хэштегов на видео

| Тип | Примеры | Использование |
|-----|---------|---------------|
| Массовые (1B+ views) | #dubai #travel #fyp | 1 на видео (для охвата) |
| Нишевые (10M-1B views) | #dubaisafari #desertdubai | 1-2 на видео |
| Микро-нишевые (<10M views) | #dubaidesertcamp #jeepdubai | 2-3 на видео |
| Брендовые | #YourBrandName | Всегда |

### 12.2. Вирусные механики

- **Challenges** — создание или участие в челленджах
- **Duets** — реакции на популярные видео
- **Stitch** — использование фрагмента чужого видео в своём
- **Trending Sounds** — использование трендовых звуков
- **Transitions** — визуальные переходы (популярны в travel-контенте)

### 12.3. Культурные тренды 2025-2026

Три ключевых тренда (TikTok "What's Next 2025"):
1. **Brand Fusion** — бренды как часть культуры
2. **Identity Osmosis** — аутентичность контента
3. **Creative Catalysts** — AI + человеческий креатив

---

## 13. Аналитика

### 13.1. TikTok Studio (нативная аналитика)

Доступна в приложении TikTok (бизнес/creator-аккаунт) и на desktop.

**Вкладки:**
- **Overview** — общая статистика (просмотры, подписчики, вовлечённость)
- **Content** — детали по каждому видео
- **Followers** — демография аудитории

### 13.2. Метрики видео

| Метрика | Описание | Хороший показатель |
|---------|----------|-------------------|
| Views | Количество просмотров | Зависит от ниши |
| Average Watch Time | Среднее время просмотра | 15-20 сек+ |
| Watched Full Video | % досмотревших до конца | 30%+ |
| Engagement Rate | (Лайки+Коммы+Шеры) / Просмотры | 5-10% |
| Like Rate | Лайки / Просмотры | 3-5% |
| Comment Rate | Комментарии / Просмотры | 0.5-1% |
| Share Rate | Шеры / Просмотры | 0.5-1% |
| Save Rate | Сохранения / Просмотры | Растущая метрика |

### 13.3. Источники трафика

- **For You Page** — рекомендательная лента (основной источник)
- **Following** — лента подписок
- **Search** — поиск TikTok (растёт значимость)
- **Profile** — переходы с профиля
- **Sound** — переходы со страницы звука
- **Hashtag** — переходы со страницы хэштега

### 13.4. Аналитика через API

```
GET https://open.tiktokapis.com/v2/video/list/
?fields=id,title,view_count,like_count,comment_count,share_count,
        create_time,duration
Authorization: Bearer {access_token}
```

### 13.5. Сторонние инструменты аналитики

| Инструмент | Что даёт | Стоимость |
|-----------|----------|-----------|
| Sprout Social | Полная аналитика + расписание | от $249/мес |
| Exolyt | TikTok-специализированная аналитика | от $49/мес |
| Brandwatch | Мониторинг бренда + конкуренты | по запросу |
| Iconosquare | Аналитика + бенчмарки | от $49/мес |
| Socialinsider | Конкурентный анализ | от $99/мес |

---

## 14. Примеры для туризма ОАЭ

### 14.1. Контент-стратегия

Dubai — самый просматриваемый город в TikTok (29.7M+ постов с #Dubai), опережая Лондон, Париж и Нью-Йорк.

**Типы контента для туризма:**

| Формат | Описание | Пример |
|--------|----------|--------|
| POV Tour | "От первого лица" прогулка | "POV: ты на Burj Khalifa At The Top" |
| Before/After | Сравнение (до/после) | "Desert vs City — Dubai в одном дне" |
| Transitions | Визуальные переходы между локациями | "Dubai Marina → Palm Jumeirah" одним движением |
| Day-in-the-Life | День из жизни в Дубае | "День турагента в Дубае" |
| Tips & Hacks | Полезные лайфхаки | "5 вещей в Дубае дешевле, чем ты думаешь" |
| Reels-style | Быстрая нарезка | "48 часов в Дубае за 30 секунд" |
| LIVE | Прямые трансляции с локаций | LIVE с Desert Safari, яхты, шоурума |

### 14.2. Хэштеги для туризма ОАЭ

**Основные:**
`#Dubai` `#UAE` `#VisitDubai` `#MyDubai` `#AbuDhabi` `#DubaiLife`

**Нишевые:**
`#DubaiSafari` `#DesertSafari` `#BurjKhalifa` `#DubaiMarina` `#PalmJumeirah`
`#DubaiMall` `#DubaiFrame` `#DubaiCreek` `#AinDubai` `#MuseumOfTheFuture`

**Активности:**
`#DubaiYacht` `#DubaiCars` `#LuxuryDubai` `#DubaiNightlife`
`#DubaiFood` `#DubaiBeach` `#DubaiShopping`

**На русском (СНГ аудитория):**
`#Дубай` `#ОАЭ` `#ЭкскурсииДубай` `#ОтдыхДубай` `#ДубайТуризм`

### 14.3. Стратегия TikTok Shop для туризма

- **Билеты** — Burj Khalifa, Dubai Frame, Aquaventure, IMG Worlds
- **Пакеты** — Desert Safari VIP, City Tour, Abu Dhabi Day Trip
- **Яхты** — ваучеры на аренду яхт (2ч, 4ч, закат)
- **Авто** — ваучеры на аренду суперкаров
- **Карточки товаров** — прикреплять к каждому видео с соответствующей локацией

### 14.4. Рекламная стратегия

**Бюджетный старт (Promote):**
1. Публикуйте 3-5 видео в неделю
2. Определите видео с лучшей органикой (>1000 views за 24ч)
3. Boost через Promote: $10-20 на 3 дня, цель — More Views
4. Таргетинг: возраст 25-44, интересы Travel + Luxury, локация Russia + CIS

**Масштабирование (Ads Manager):**
1. Spark Ads — продвижение лучших органических видео
2. In-Feed Ads — 21-34 сек, крючок в первые 3 секунды
3. Таргетинг: Custom Audiences + Lookalike Audiences
4. Бюджет: от $50/день на кампанию

### 14.5. Сезонность (ОАЭ)

| Период | Активность | Контент-фокус |
|--------|-----------|---------------|
| Окт-Март | Высокий сезон | Максимум контента, реклама |
| Апр-Май | Средний | Переход, акции "последний шанс" |
| Июн-Сен | Низкий (жара) | Indoor-активности, водные парки, ночные туры |
| Рамадан | Специфический | Ифтар-круизы, ночные экскурсии |
| Ноябрь | Пик | Dubai Shopping Festival, F1, конференции |

---

## 15. Лимиты и требования

### 15.1. API Rate Limits

| Эндпоинт | Лимит |
|----------|-------|
| /v2/video/list/ | 600 запросов/мин |
| Content Posting (публикация) | 6 запросов/мин на access_token |
| Research API | 1000 запросов/день |
| Research API (записи) | 100 000 записей/день |
| Followers/Following API | 20 000 вызовов/день, 2M записей/день |

Квоты сбрасываются в 12:00 UTC. Для повышения лимитов — заявка через TikTok Support.

### 15.2. Требования к видео

| Параметр | Значение |
|----------|----------|
| Рекомендованное разрешение | 1080 x 1920 px |
| Соотношение сторон | 9:16 (вертикальное) |
| Форматы | MP4, MOV (H.264 + AAC) |
| Макс. размер (мобильное) | 287.6 МБ (iOS), 72 МБ (Android) |
| Макс. размер (web/desktop) | 500 МБ |
| Макс. длительность | 60 мин (загрузка), 10 мин (запись в приложении) |
| Мин. длительность | 3 секунды |
| Photo Mode | До 35 фото |

### 15.3. Лимиты аккаунта

| Параметр | Лимит |
|----------|-------|
| Публикаций в день | 15 (через API) |
| Хэштегов на видео | Нет жёсткого лимита (рекомендовано 3-5) |
| Длина описания | 2200 символов |
| Звуки | Доступность зависит от типа аккаунта (personal/business) |

### 15.4. Бизнес-аккаунт vs Creator-аккаунт

| Функция | Creator | Business |
|---------|---------|----------|
| Аналитика | Да | Да |
| Музыкальная библиотека | Полная | Ограничена (только Commercial Sounds) |
| Promote | Да | Да |
| TikTok Shop | Да (Affiliate) | Да (Seller) |
| Creator Fund | Да | Нет |
| LIVE Gifts | Да | Нет |
| Контактная кнопка | Нет | Да (Email, Phone) |

---

## Таблица ресурсов

| Ресурс | URL | Описание |
|--------|-----|----------|
| TikTok for Developers | https://developers.tiktok.com/ | Девелоперский портал, документация |
| TikTok Business Center | https://ads.tiktok.com/ | Рекламный кабинет |
| TikTok Creative Center | https://ads.tiktok.com/business/creativecenter/ | Тренды, звуки, хэштеги |
| TikTok Shop Seller Center | https://seller.tiktok.com/ | Управление магазином |
| Business API Docs | https://business-api.tiktok.com/portal/docs | Документация Ads API |
| Content Posting API | https://developers.tiktok.com/doc/content-posting-api-get-started | Публикация контента |
| Login Kit | https://developers.tiktok.com/doc/login-kit-web | Авторизация OAuth 2.0 |
| Embed API | https://developers.tiktok.com/doc/embed-videos/ | Встраивание видео |
| Research API | https://developers.tiktok.com/doc/research-api-specs-query-videos/ | Исследовательский API |
| Rate Limits | https://developers.tiktok.com/doc/tiktok-api-v2-rate-limit | Лимиты API |
| API Scopes | https://developers.tiktok.com/doc/tiktok-api-scopes | Разрешения |
| TikTok OpenSDK (GitHub) | https://github.com/nicetomeet-you/tiktok-opensdk | Open SDK |
| CapCut | https://www.capcut.com/ | Видеоредактор от ByteDance |
| TikTok Effect House | https://effecthouse.tiktok.com/ | Создание AR-эффектов |
| TikTok "What's Next" Report | https://ads.tiktok.com/business/en/trends | Годовой отчёт по трендам |
