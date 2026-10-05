# Cheatsheet — Facebook Graph API v22.0

## Базовый URL
```
https://graph.facebook.com/v22.0/
```

---

## Токены

| Действие | Запрос |
|----------|--------|
| Short→Long-Lived | `GET /oauth/access_token?grant_type=fb_exchange_token&client_id={app}&client_secret={secret}&fb_exchange_token={token}` |
| Получить Page Token | `GET /me/accounts?access_token={long_lived_user_token}` |
| Проверить токен | `GET /debug_token?input_token={token}&access_token={app_token}` |
| App Token | `GET /oauth/access_token?client_id={app}&client_secret={secret}&grant_type=client_credentials` |

---

## Страница (Page)

| Действие | Запрос |
|----------|--------|
| Информация | `GET /{page_id}?fields=id,name,about,fan_count,website,phone,location,cover` |
| Обновить | `POST /{page_id}?about=...&website=...` |
| Добавить CTA | `POST /{page_id}/call_to_actions?type=BOOK_NOW&value={"link":"..."}` |
| Роли | `POST /{page_id}/roles?user={id}&role=EDITOR` |

---

## Публикации

| Действие | Запрос |
|----------|--------|
| Текстовый пост | `POST /{page_id}/feed?message=...` |
| Пост + ссылка | `POST /{page_id}/feed?message=...&link=...` |
| Одно фото | `POST /{page_id}/photos?url=...&caption=...` |
| Фото (upload) | `POST /{page_id}/photos` (multipart, source=file) |
| Несколько фото | 1) `POST /{page_id}/photos?published=false` x N 2) `POST /{page_id}/feed?attached_media=[...]` |
| Видео (URL) | `POST /{page_id}/videos?file_url=...&title=...&description=...` |
| Запланировать | `POST /{page_id}/feed?message=...&published=false&scheduled_publish_time={unix}` |
| Гео-таргет | `POST /{page_id}/feed?message=...&targeting={"geo_locations":{"countries":["RU"]}}` |
| Получить посты | `GET /{page_id}/feed?fields=message,created_time,type&limit=25` |
| Удалить пост | `DELETE /{post_id}` |

---

## Reels (3 шага)

```
1. START:   POST /{page_id}/video_reels?upload_phase=start
             → {"video_id": "123"}

2. TRANSFER: POST /{video_id}?upload_phase=transfer&file_url=...
             (или binary upload)

3. FINISH:  POST /{page_id}/video_reels?upload_phase=finish
             &video_id=123&title=...&description=...
```

**Требования:** 9:16, мин. 540p, 23+ fps, 4-90 сек, MP4/MOV/MKV/WMV

---

## Stories

| Действие | Запрос |
|----------|--------|
| Фото Story | 1) `POST /{page_id}/photos?published=false&source=file` 2) `POST /{page_id}/photo_stories?photo_id={id}` |
| Видео Story | 1) Upload video 2) `POST /{page_id}/video_stories?video_id={id}` |
| Аналитика | `GET /{story_id}/insights?metric=story_impressions,story_exits,story_replies` |

---

## События (Events)

| Действие | Запрос |
|----------|--------|
| Создать | `POST /{page_id}/events?name=...&start_time=...&description=...` |
| Получить | `GET /{event_id}?fields=name,start_time,attending_count,interested_count` |
| Список | `GET /{page_id}/events?time_filter=upcoming` |
| RSVP | `POST /{event_id}/attending` (user token) |
| Обновить | `POST /{event_id}?description=...` |
| Удалить | `DELETE /{event_id}` |

---

## Группы

| Действие | Запрос |
|----------|--------|
| Пост в группу | `POST /{group_id}/feed?message=...` |
| Получить посты | `GET /{group_id}/feed?fields=message,from,created_time` |
| Участники | `GET /{group_id}/members?fields=id,name,administrator` |
| Удалить участника | `POST /{group_id}/removed_members?member={user_id}` |

---

## Commerce / Catalog

| Действие | Запрос |
|----------|--------|
| Создать каталог | `POST /{business_id}/owned_product_catalogs?name=...` |
| Добавить товар | `POST /{catalog_id}/products?retailer_id=...&name=...&price=...&currency=AED&image_url=...&availability=in stock` |
| Обновить товар | `POST /{product_id}?name=...&price=...` |
| Удалить товар | `DELETE /{product_id}` |
| Список товаров | `GET /{catalog_id}/products?fields=name,price,availability,image_url` |

---

## Модерация

| Действие | Запрос |
|----------|--------|
| Комментарии поста | `GET /{post_id}/comments?fields=id,message,from,created_time` |
| Ответить | `POST /{comment_id}/comments?message=...` |
| Скрыть | `POST /{comment_id}?is_hidden=true` |
| Удалить | `DELETE /{comment_id}` |
| Забанить | `POST /{page_id}/blocked?user[]={user_id}` |
| Разбанить | `DELETE /{page_id}/blocked?user={user_id}` |

---

## Insights (Аналитика)

| Действие | Запрос |
|----------|--------|
| Метрики страницы | `GET /{page_id}/insights?metric=page_views_total,page_fan_adds,page_engaged_users&period=day&since=...&until=...` |
| Метрики поста | `GET /{post_id}/insights?metric=post_engaged_users,post_clicks,post_reactions_by_type_total` |
| Аудитория | `GET /{page_id}/insights?metric=page_fans_city,page_fans_country,page_fans_gender_age&period=day` |
| Видео | `GET /{post_id}/insights?metric=post_video_views,post_video_avg_time_watched` |

**Периоды:** `day`, `week`, `days_28`, `month`, `lifetime`

**Deprecated (ноябрь 2025):** `page_impressions` -> Views, `page_fans` -> `page_follows`

---

## Ads (базовое)

| Действие | Запрос |
|----------|--------|
| Создать кампанию | `POST /act_{ad_account}/campaigns?name=...&objective=OUTCOME_TRAFFIC&status=PAUSED` |
| Бустить пост | `POST /{post_id}/promotions?budget=5000&currency=AED&duration=7&targeting={...}` |
| Список кампаний | `GET /act_{ad_account}/campaigns?fields=name,status,objective` |

---

## Batch Requests

```http
POST /v22.0/
  ?batch=[
    {"method":"GET","relative_url":"{page_id}?fields=fan_count"},
    {"method":"GET","relative_url":"{page_id}/posts?limit=5"}
  ]
  &access_token={token}
```

---

## Rate Limits

| Уровень | Лимит | Заголовок |
|---------|-------|-----------|
| App | 200 * users/час | `X-App-Usage` |
| Page | 4,800/24ч | `X-Page-Usage` |
| Публикации | ~25/день (рекомендуемый) | — |

---

## Ключевые Permissions

| Permission | Для чего |
|-----------|----------|
| `pages_manage_posts` | Публикация контента |
| `pages_read_engagement` | Чтение реакций/комментариев |
| `pages_manage_engagement` | Управление комментариями |
| `pages_manage_metadata` | Настройки страницы |
| `read_insights` | Аналитика |
| `publish_to_groups` | Посты в группы |
| `catalog_management` | Каталог товаров |
| `ads_management` | Реклама |
| `pages_messaging` | Messenger (см. messenger-bot) |

---

## Полезные инструменты

| Инструмент | URL |
|-----------|-----|
| Graph API Explorer | developers.facebook.com/tools/explorer/ |
| Access Token Debugger | developers.facebook.com/tools/debug/accesstoken/ |
| Sharing Debugger | developers.facebook.com/tools/debug/ |
| Batch Request Tester | developers.facebook.com/tools/explorer/ (batch mode) |
| Meta Business Suite | business.facebook.com |
| Commerce Manager | commerce.facebook.com |
