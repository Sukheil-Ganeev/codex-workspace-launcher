---
name: facebook-справочник
description: "Production-ready руководство по Facebook как платформе для туристического бизнеса ОАЭ. Graph API, страницы, группы, Reels, события, Marketplace, Shops. Используй когда нужно работать с Facebook контентом (НЕ Messenger боты)."
---
# Facebook — Справочник платформы

> Messenger боты: см. **meta-messenger-bot-справочник**

Справочник охватывает Facebook как платформу контента, коммерции и аналитики. Messenger Platform API, чат-боты, webhooks и автоматизация переписки — в отдельном справочнике.

---

## 1. Обзор платформы

### Facebook Graph API

Graph API — единая HTTP-точка входа ко всем данным Facebook: страницы, посты, фото, видео, события, группы, каталоги, аналитика.

**Базовый URL:**
```
https://graph.facebook.com/v22.0/{endpoint}
```

**Версионирование:**
- Текущая стабильная: **v22.0** (2025)
- Предыдущая: v21.0 (октябрь 2024)
- Политика: версии старше 2 лет деактивируются. С сентября 2025 запросы к версиям ниже v22.0 отклоняются
- Каждая новая версия выходит раз в ~4 месяца

**Ключевые изменения v22.0:**
- Страничные рекомендации (Page Recommendations) deprecated
- Обязательные поля для country override в каталогах (price, sale_price, status, availability — только в country feeds)
- Метрика "Views" заменяет "Impressions" (унификация с Instagram)

### Meta Business Suite

Бесплатная панель управления Facebook + Instagram:
- Единый инбокс (Facebook, Instagram, Messenger)
- Планирование и публикация контента (посты, Stories, Reels)
- Аналитика (reach, engagement, audience demographics)
- Управление рекламой (базовое; расширенное — в Ads Manager)
- Ролевая система: Admin, Editor, Analyst, Moderator
- Drag-and-drop календарь контента с рекомендациями по времени публикации

### Архитектура экосистемы

```
Meta Business Suite (UI)
├── Facebook Page Management
├── Instagram Account Management
├── Messenger Inbox
├── Content Planner
├── Insights Dashboard
└── Ads Manager (linked)

Graph API v22.0 (программный доступ)
├── Pages API
├── Posts / Photos / Videos
├── Reels Publishing API
├── Stories API
├── Events API
├── Groups API
├── Commerce / Catalog API
├── Insights API
├── Comments / Moderation
└── Ads API (Marketing API)
```

---

## 2. Аутентификация

### Типы токенов

| Токен | Срок жизни | Назначение |
|-------|-----------|------------|
| **User Access Token** | ~1 час | Действия от имени пользователя |
| **Long-Lived User Token** | ~60 дней | Продлённый User Token |
| **Page Access Token** | Бессрочный* | Действия от имени страницы |
| **App Access Token** | Бессрочный | Server-to-server, публичные данные |
| **System User Token** | Бессрочный | Business Manager автоматизация |

*Page Access Token, полученный из Long-Lived User Token, не истекает.

### Получение Page Access Token

```
1. Создать App в developers.facebook.com
2. Получить User Access Token (Facebook Login, scope: pages_manage_posts, pages_read_engagement)
3. Обменять на Long-Lived Token:
   GET /oauth/access_token?grant_type=fb_exchange_token
     &client_id={app_id}
     &client_secret={app_secret}
     &fb_exchange_token={short_lived_token}
4. Получить Page Token:
   GET /me/accounts?access_token={long_lived_user_token}
```

### Ключевые разрешения (Permissions)

**Контент:**
- `pages_manage_posts` — публикация постов, фото, видео
- `pages_read_engagement` — чтение реакций, комментариев
- `pages_read_user_content` — чтение пользовательского контента на странице
- `pages_manage_metadata` — управление настройками страницы

**Аналитика:**
- `pages_show_list` — список страниц пользователя
- `read_insights` — доступ к Insights API

**Модерация:**
- `pages_manage_engagement` — управление комментариями, реакциями
- `pages_messaging` — Messenger (см. Messenger-справочник)

**Коммерция:**
- `catalog_management` — управление каталогом товаров
- `commerce_account_manage_orders` — управление заказами

**Реклама:**
- `ads_management` — управление рекламными кампаниями
- `ads_read` — чтение данных о рекламе

---

## 3. Страницы (Pages API)

### Создание и настройка страницы

Страницы создаются через UI (facebook.com/pages/create). API используется для управления уже созданной страницей.

**Получение информации о странице:**
```http
GET /v22.0/{page_id}
  ?fields=id,name,about,category,fan_count,website,phone,
          location,hours,cover,picture
  &access_token={page_token}
```

**Обновление информации:**
```http
POST /v22.0/{page_id}
  ?about=Экскурсии и билеты в парки ОАЭ
  &website=https://example.com
  &phone=+971501234567
  &access_token={page_token}
```

### Настройка CTA (Call-to-Action)

```http
POST /v22.0/{page_id}/call_to_actions
  ?type=BOOK_NOW
  &value={"link": "https://wa.me/971501234567"}
  &access_token={page_token}
```

Типы CTA: `BOOK_NOW`, `CONTACT_US`, `SEND_MESSAGE`, `CALL_NOW`, `SHOP_NOW`, `SIGN_UP`, `LEARN_MORE`, `WATCH_VIDEO`.

### Управление ролями

```http
POST /v22.0/{page_id}/roles
  ?user={user_id}
  &role=EDITOR
  &access_token={page_token}
```

Роли: `ADMIN`, `EDITOR`, `MODERATOR`, `ANALYST`, `ADVERTISER`.

---

## 4. Группы (Groups API)

### Обзор

Facebook Groups — сообщества по интересам. Для туризма — идеальный инструмент для комьюнити: "Экскурсии в Дубае", "Отдых в ОАЭ".

**Ограничения API (с 2018+):**
- Создание групп — только через UI
- Публикация в группы через API — только для приложений, прошедших App Review
- Требуется permission `publish_to_groups`

### Публикация в группу

```http
POST /v22.0/{group_id}/feed
  ?message=Новые экскурсии на февраль! Джип-сафари со скидкой 20%
  &link=https://example.com/safari
  &access_token={user_token}
```

### Получение постов группы

```http
GET /v22.0/{group_id}/feed
  ?fields=message,created_time,from,type,attachments
  &limit=25
  &access_token={user_token}
```

### Управление участниками

```http
GET /v22.0/{group_id}/members
  ?fields=id,name,administrator
  &access_token={user_token}
```

### Модерация группы

```http
DELETE /v22.0/{post_id}
  ?access_token={user_token}

POST /v22.0/{group_id}/removed_members
  ?member={user_id}
  &access_token={admin_token}
```

---

## 5. Публикации (Posts API)

### Текстовый пост

```http
POST /v22.0/{page_id}/feed
  ?message=Desert Safari в Дубае — незабываемое приключение!
  &access_token={page_token}
```

### Пост с фото

```http
POST /v22.0/{page_id}/photos
  ?url=https://example.com/safari.jpg
  &caption=Джип-сафари в пустыне — каждый день в 15:00
  &access_token={page_token}
```

Локальная загрузка:
```http
POST /v22.0/{page_id}/photos
  Content-Type: multipart/form-data
  source={file}
  &caption=Burj Khalifa — вид с 148 этажа
  &access_token={page_token}
```

### Пост с несколькими фото

```
1. Загрузить каждое фото с published=false:
   POST /{page_id}/photos?published=false&source={file}
   → получить {photo_id_1}, {photo_id_2}, ...

2. Создать пост с привязкой:
   POST /{page_id}/feed
     ?message=Наши экскурсии
     &attached_media=[{"media_fbid":"{photo_id_1}"},{"media_fbid":"{photo_id_2}"}]
```

### Пост с видео

```http
POST /v22.0/{page_id}/videos
  ?file_url=https://example.com/tour.mp4
  &title=Обзорная экскурсия по Дубаю
  &description=Все главные достопримечательности за 4 часа
  &access_token={page_token}
```

### Пост с ссылкой

```http
POST /v22.0/{page_id}/feed
  ?message=Забронируйте экскурсию прямо сейчас!
  &link=https://example.com/booking
  &access_token={page_token}
```

### Планирование публикации

```http
POST /v22.0/{page_id}/feed
  ?message=Раннее бронирование — скидка 15%
  &published=false
  &scheduled_publish_time={unix_timestamp}
  &access_token={page_token}
```

`scheduled_publish_time` — Unix timestamp, от 10 минут до 75 дней в будущем.

### Таргетирование поста по гео

```http
POST /v22.0/{page_id}/feed
  ?message=Специальное предложение для гостей из России!
  &targeting={"geo_locations":{"countries":["RU","KZ","UZ"]}}
  &access_token={page_token}
```

### Важные ограничения

- Нельзя комбинировать фото и видео в одном посте
- API позволяет публиковать только на Pages (не на личные профили)
- Максимум фото в мультифото-посте: 10
- Видео: макс. размер 10 GB, длительность до 240 минут

---

## 6. Facebook Reels

### Обзор

Reels — короткие вертикальные видео (до 90 сек). Публикация через Reels Publishing API.

**Требования к видео:**
- Формат: MP4, MOV, MKV, WMV
- Соотношение сторон: 9:16
- Минимальное разрешение: 540x960 (540p)
- Частота кадров: минимум 23 fps
- Длительность: 4–90 секунд

### Процесс публикации (3 шага)

**Шаг 1: Инициализация**
```http
POST /v22.0/{page_id}/video_reels
  ?upload_phase=start
  &access_token={page_token}

→ Response: {"video_id": "123456789"}
```

**Шаг 2: Загрузка видео**
```http
POST /v22.0/{video_id}
  ?upload_phase=transfer
  &file_url=https://cdn.example.com/reel.mp4
  &access_token={page_token}
```

Или бинарная загрузка:
```http
POST /v22.0/{video_id}
  ?upload_phase=transfer
  Content-Type: application/octet-stream
  Body: {binary_video_data}
```

**Шаг 3: Публикация**
```http
POST /v22.0/{page_id}/video_reels
  ?upload_phase=finish
  &video_id={video_id}
  &title=Закат в пустыне — Desert Safari
  &description=Бронируйте сафари: wa.me/971501234567
  &access_token={page_token}
```

### Аналитика Reels

Доступные метрики (через Insights API):
- `post_video_views` — просмотры
- `post_video_view_time` — общее время просмотра
- `blue_reels_play_count` — воспроизведения Reels
- `post_video_avg_time_watched` — среднее время просмотра
- Reels replays (новая метрика 2025)

---

## 7. Stories

### Публикация фото-Story

```http
POST /v22.0/{page_id}/photo_stories
  ?photo_id={uploaded_photo_id}
  &access_token={page_token}
```

Предварительно загрузить фото:
```http
POST /v22.0/{page_id}/photos
  ?published=false
  &source={file}
  &access_token={page_token}
→ {"id": "{photo_id}"}
```

### Публикация видео-Story

```http
POST /v22.0/{page_id}/video_stories
  ?video_id={uploaded_video_id}
  &access_token={page_token}
```

### Характеристики

- Формат: вертикальный 9:16 (1080x1920)
- Видео: до 60 секунд
- Срок жизни: 24 часа
- Фото: JPG, PNG
- Стикеры и интерактивные элементы — только через UI, не через API

### Аналитика Stories

```http
GET /v22.0/{story_id}/insights
  ?metric=story_impressions,story_exits,story_replies,story_taps_forward,story_taps_back
  &access_token={page_token}
```

---

## 8. События (Events API)

### Создание события

```http
POST /v22.0/{page_id}/events
  ?name=Desert Safari — Групповая экскурсия
  &description=Джип-сафари с BBQ ужином в пустыне. Включено: пикап из отеля, сэндбординг, катание на верблюдах.
  &start_time=2026-03-15T15:00:00+0400
  &end_time=2026-03-15T21:00:00+0400
  &place={"name":"Dubai Desert Conservation Reserve","location":{"latitude":24.87,"longitude":55.67}}
  &access_token={page_token}
```

### Получение события

```http
GET /v22.0/{event_id}
  ?fields=name,description,start_time,end_time,place,attending_count,interested_count,cover
  &access_token={page_token}
```

### RSVP (от имени пользователя)

```http
POST /v22.0/{event_id}/attending
  ?access_token={user_token}
```

Статусы: `/attending` (пойду), `/maybe` (возможно), `/declined` (не пойду).

### Обновление события

```http
POST /v22.0/{event_id}
  ?description=Обновлённое описание с новыми деталями
  &access_token={page_token}
```

### Удаление события

```http
DELETE /v22.0/{event_id}
  ?access_token={page_token}
```

### Получение списка событий страницы

```http
GET /v22.0/{page_id}/events
  ?fields=name,start_time,attending_count,interested_count
  &time_filter=upcoming
  &access_token={page_token}
```

---

## 9. Facebook Shops & Commerce

### Обзор

Facebook Shops — витрина товаров/услуг прямо на странице. Управляется через Commerce Manager.

**Настройка:**
1. Commerce Manager: commerce.facebook.com
2. Создать каталог (Catalog)
3. Привязать к Page
4. Настроить Checkout (on-Facebook или external link)

### Product Catalog API

**Создание каталога:**
```http
POST /v22.0/{business_id}/owned_product_catalogs
  ?name=Экскурсии ОАЭ
  &access_token={token}
```

**Добавление товара:**
```http
POST /v22.0/{catalog_id}/products
  ?retailer_id=safari-001
  &name=Desert Safari Premium
  &description=VIP джип-сафари с приватным BBQ
  &availability=in stock
  &condition=new
  &price=350
  &currency=AED
  &url=https://example.com/safari-premium
  &image_url=https://example.com/safari.jpg
  &brand=Dubai Tours
  &access_token={token}
```

**Batch-загрузка через Data Feed:**
- CSV/TSV/XML файл с товарами
- Автоматический fetch по расписанию (URL фида)
- Или разовая загрузка через Commerce Manager UI

### Обязательные поля товара

| Поле | Описание |
|------|----------|
| `id` / `retailer_id` | Уникальный ID товара |
| `name` / `title` | Название (макс. 200 символов) |
| `description` | Описание |
| `availability` | `in stock`, `out of stock`, `preorder` |
| `price` | Цена + валюта |
| `image_url` | Главное фото (мин. 500x500) |
| `url` | Ссылка на товар |

### Категории для туризма

- Travel & Tourism
- Tours & Experiences
- Tickets & Events
- Transportation Services

### Facebook Shops для туристического бизнеса

Shops отлично подходит для каталога экскурсий:
- Каждая экскурсия = товар (Safari, City Tour, Yacht Charter)
- Цена в AED
- Checkout external — переход в WhatsApp/сайт для бронирования
- Collections — группировка (По эмиратам, По типу, VIP)

---

## 10. Facebook Marketplace

### Обзор

Marketplace — площадка для локальных объявлений. 1.1+ млрд пользователей в 228+ странах.

**Ограничения API:**
- Нет открытого API для листинга в Marketplace для всех
- Marketplace Approval API — только для одобренных партнёров (крупные интеграторы)
- Листинги создаются вручную или через Commerce Manager (для магазинов)

### Создание листинга (через UI)

1. Marketplace > Create New Listing
2. Категория: Item for Sale / Vehicle / Property / Service
3. Фото (до 10), название, цена, описание, местоположение
4. Публикация → виден пользователям в радиусе

### Для турбизнеса

Marketplace ограниченно полезен:
- Можно листить "Services" (экскурсии, трансферы)
- Локальная аудитория Дубая видит объявления
- Нет полноценной API-автоматизации
- Лучше использовать Shops (на странице) + Ads для масштаба

---

## 11. Insights API (Аналитика)

### Метрики страницы

```http
GET /v22.0/{page_id}/insights
  ?metric=page_views_total,page_fan_adds,page_engaged_users,page_post_engagements,page_consumptions
  &period=day
  &since=2026-02-01
  &until=2026-02-12
  &access_token={page_token}
```

### Ключевые метрики (2025+)

**Страница:**
| Метрика | Описание |
|---------|----------|
| `page_views_total` | Просмотры страницы |
| `page_fan_adds` | Новые подписчики |
| `page_engaged_users` | Уникальные пользователи с engagement |
| `page_post_engagements` | Реакции, комментарии, шеры |
| `page_consumptions` | Клики на контент |

**Изменения 2025:**
- `page_impressions` → **deprecated** (ноябрь 2025), заменён на **Views**
- `page_fans` → **deprecated**, заменён на `page_follows`
- Новые метрики: Reels replays, Total reels plays

**Посты:**
```http
GET /v22.0/{post_id}/insights
  ?metric=post_engaged_users,post_clicks,post_reactions_by_type_total
  &access_token={page_token}
```

| Метрика | Описание |
|---------|----------|
| `post_engaged_users` | Уникальные пользователи |
| `post_clicks` | Клики (ссылка, фото, "ещё") |
| `post_reactions_by_type_total` | Реакции по типам |
| `post_video_views` | Просмотры видео (3+ сек) |
| `post_video_avg_time_watched` | Среднее время просмотра |

**Периоды:** `day`, `week`, `days_28`, `month`, `lifetime`.

### Аналитика аудитории

```http
GET /v22.0/{page_id}/insights
  ?metric=page_fans_city,page_fans_country,page_fans_gender_age,page_fans_locale
  &period=day
  &access_token={page_token}
```

---

## 12. Facebook Ads (обзор)

> Детальное руководство по рекламе: см. **рекламные-платформы-справочник**

### Ads API (Marketing API)

**Структура рекламного аккаунта:**
```
Ad Account
└── Campaign (цель: Traffic, Conversions, Reach...)
    └── Ad Set (таргетинг, бюджет, расписание)
        └── Ad (креатив: изображение/видео + текст)
```

### Форматы рекламы

| Формат | Описание | Туризм |
|--------|----------|--------|
| Image Ad | Одно изображение | Фото экскурсии |
| Video Ad | Видео до 240 мин | Обзор тура |
| Carousel | 2-10 карточек | Каталог экскурсий |
| Collection | Обложка + товары | Shops интеграция |
| Reels Ad | Между Reels | Вертикальное видео |
| Stories Ad | Полноэкранный | Атмосферное фото/видео |
| Lead Ad | Форма сбора контактов | Бронирование |

### Таргетинг для туризма ОАЭ

```json
{
  "targeting": {
    "geo_locations": {
      "countries": ["RU", "KZ", "UZ", "BY", "UA"],
      "cities": [{"key": "dubai"}]
    },
    "age_min": 25,
    "age_max": 55,
    "interests": [
      {"id": "6003384741631", "name": "Travel"},
      {"id": "6003012882849", "name": "Tourism"},
      {"id": "6003349442636", "name": "Dubai"}
    ],
    "behaviors": [
      {"id": "6002714895372", "name": "Frequent travelers"}
    ]
  }
}
```

### Базовые операции

**Создание кампании:**
```http
POST /v22.0/act_{ad_account_id}/campaigns
  ?name=Dubai Tours — Россия
  &objective=OUTCOME_TRAFFIC
  &status=PAUSED
  &special_ad_categories=[]
  &access_token={token}
```

**Бустинг поста (простой способ):**
```http
POST /v22.0/{post_id}/promotions
  ?budget=5000
  &currency=AED
  &duration=7
  &targeting={"geo_locations":{"countries":["RU"]}}
  &access_token={page_token}
```

---

## 13. Модерация

### Получение комментариев

```http
GET /v22.0/{post_id}/comments
  ?fields=id,message,from,created_time,like_count,is_hidden
  &limit=50
  &access_token={page_token}
```

### Ответ на комментарий

```http
POST /v22.0/{comment_id}/comments
  ?message=Спасибо за отзыв! Напишите нам в WhatsApp для бронирования.
  &access_token={page_token}
```

### Скрытие комментария

```http
POST /v22.0/{comment_id}
  ?is_hidden=true
  &access_token={page_token}
```

### Удаление комментария

```http
DELETE /v22.0/{comment_id}
  ?access_token={page_token}
```

### Бан пользователя со страницы

```http
POST /v22.0/{page_id}/blocked
  ?user[]={user_id}
  &access_token={page_token}
```

### Автомодерация (Page Settings)

Настраивается через Meta Business Suite:
- **Keyword Blocklist** — автоматическое скрытие комментариев с запрещёнными словами
- **Profanity Filter** — блокировка нецензурной лексики (Medium/Strong)
- **AI-модерация** — Meta автоматически скрывает спам

### Webhooks для комментариев

Подписка на `feed` field объекта `page`:
```json
{
  "object": "page",
  "callback_url": "https://example.com/webhook",
  "fields": ["feed"],
  "verify_token": "my_verify_token"
}
```

Получение уведомлений при новых комментариях для real-time модерации.

---

## 14. Примеры для туризма ОАЭ

### Стратегия страницы турагентства

**Название:** Dubai Tours & Excursions — Экскурсии Дубай
**Категория:** Tour Agency / Travel Company
**CTA:** Book Now → WhatsApp

**Контент-план (типы постов):**

| День | Тип | Пример |
|------|-----|--------|
| Пн | Carousel | ТОП-5 экскурсий недели + цены |
| Вт | Reel | 30-сек видео с экскурсии |
| Ср | Event | Анонс групповой экскурсии на выходные |
| Чт | Фото + отзыв | Фото клиента + цитата |
| Пт | Story | За кулисами: подготовка к сафари |
| Сб | Video | 2-мин обзор экскурсии |
| Вс | Пост-ссылка | Блог: "Что посетить в Абу-Даби" |

### Каталог экскурсий в Shops

```
Collection: Экскурсии по Дубаю
├── Desert Safari Standard — 180 AED
├── Desert Safari VIP — 350 AED
├── City Tour Dubai — 150 AED
├── Burj Khalifa 124+125 — 190 AED
└── Dubai Marina Cruise — 120 AED

Collection: Абу-Даби
├── Abu Dhabi City Tour — 200 AED
├── Ferrari World — 295 AED
└── Yas Waterworld — 260 AED

Collection: VIP Трансферы
├── Airport Transfer (Sedan) — 200 AED
├── Airport Transfer (V-Class) — 350 AED
└── Full Day Chauffeur — 1200 AED
```

### События для привлечения клиентов

Регулярные события:
- "Бесплатная консультация по экскурсиям" — еженедельно
- "Sunset Desert Safari — групповой выезд" — каждую пятницу
- "Yacht Party — New Year" — разовое мероприятие

### Facebook Reels — стратегия

Контент для Reels (9:16, 15-60 сек):
- Timelapse заката в пустыне
- POV: джип-сафари по дюнам
- До/после: пустой яхт vs. вечеринка на борту
- "3 места в Дубае, о которых не знают туристы"
- Отзыв клиента: короткое видео-интервью

### Аудитории для таргетинга

| Аудитория | Гео | Интересы |
|-----------|-----|----------|
| Русскоговорящие туристы | RU, KZ, UZ, BY | Travel, Dubai, UAE |
| Европейские туристы | DE, UK, FR, IT | Luxury travel, Beach holidays |
| Локальные жители | AE (Dubai, Abu Dhabi) | Weekend activities, Entertainment |
| Бизнес-путешественники | Global | Business travel, MICE |

---

## 15. Rate Limits

### Application-Level Rate Limits

Формула: `200 * (количество пользователей приложения)` вызовов в час.

| Пользователей | Лимит/час |
|---------------|-----------|
| 100 | 20,000 |
| 1,000 | 200,000 |
| 10,000 | 2,000,000 |

### Page-Level Rate Limits

- 4,800 вызовов на страницу за 24 часа (для большинства endpoints)
- Публикации: 25 постов в сутки на страницу (рекомендуемый лимит)

### Мониторинг лимитов

Заголовки ответа:
```
X-App-Usage: {"call_count": 25, "total_cputime": 10, "total_time": 15}
X-Page-Usage: {"call_count": 50, "total_cputime": 20, "total_time": 25}
```

Значения в процентах (0-100). При превышении 100 — запросы блокируются.

### Стратегия работы с лимитами

1. Кэшировать данные (не запрашивать повторно)
2. Использовать batch-запросы: `POST /v22.0/?batch=[...]`
3. Запрашивать только нужные fields
4. Подписаться на Webhooks вместо polling
5. Мониторить X-App-Usage и X-Page-Usage

### App Review

Для production-доступа к большинству permissions требуется App Review:

1. Создать приложение в developers.facebook.com
2. Указать платформу, политику конфиденциальности
3. Запросить нужные permissions
4. Предоставить screencast использования
5. Рассмотрение: от нескольких дней до нескольких недель
6. После одобрения — permissions доступны для всех пользователей

**Permissions без App Review (в Development Mode):**
- Работают только для администраторов/тестеров приложения
- Хватает для тестирования и небольших команд

---

## Таблица ресурсов

| Ресурс | URL |
|--------|-----|
| Graph API Explorer | https://developers.facebook.com/tools/explorer/ |
| Graph API Reference | https://developers.facebook.com/docs/graph-api/reference/ |
| Meta Business Suite | https://business.facebook.com/ |
| Commerce Manager | https://commerce.facebook.com/ |
| App Dashboard | https://developers.facebook.com/apps/ |
| Permissions Reference | https://developers.facebook.com/docs/permissions/reference/ |
| Webhooks Docs | https://developers.facebook.com/docs/graph-api/webhooks/ |
| Reels Publishing API | https://developers.facebook.com/docs/video-api/guides/reels-publishing |
| Marketing API | https://developers.facebook.com/docs/marketing-api/ |
| Page Insights Metrics | https://developers.facebook.com/docs/graph-api/reference/page/insights/ |
| Catalog Batch API | https://developers.facebook.com/docs/marketing-api/catalog-batch/ |
| Rate Limiting | https://developers.facebook.com/docs/graph-api/overview/rate-limiting/ |
| App Review Guide | https://developers.facebook.com/docs/app-review/ |
| Meta for Developers Blog | https://developers.facebook.com/blog/ |
| Status Page | https://metastatus.com/ |
