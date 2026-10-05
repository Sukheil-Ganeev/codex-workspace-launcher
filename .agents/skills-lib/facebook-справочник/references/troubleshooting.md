# Troubleshooting — Facebook Graph API

## Аутентификация

### Error: "Invalid OAuth access token"
**Причина:** Токен истёк или невалиден.
**Решение:**
1. Проверить срок жизни токена в Graph API Explorer
2. Обменять short-lived на long-lived token
3. Для Page Token — получить заново из long-lived user token
```http
GET /oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id={app_id}
  &client_secret={app_secret}
  &fb_exchange_token={short_lived_token}
```

### Error: "(#200) Requires extended permission: pages_manage_posts"
**Причина:** Приложение не имеет нужного permission.
**Решение:**
1. В Development Mode — добавить permission в App Dashboard → Permissions
2. В Live Mode — пройти App Review для этого permission
3. Убедиться что токен получен с нужным scope

### Error: "User must be an admin of the page"
**Причина:** User Token принадлежит пользователю без роли Admin на странице.
**Решение:**
1. Назначить пользователя Admin/Editor на странице
2. Или использовать Page Access Token вместо User Token

### Токен перестал работать внезапно
**Причины:**
- Пользователь сменил пароль Facebook
- Пользователь отозвал разрешения приложения
- Приложение удалено или заблокировано Meta
- Истёк long-lived token (~60 дней)
**Решение:** Обновить токен, проверить статус приложения в App Dashboard

---

## Публикации

### Error: "(#100) Missing message or attachment"
**Причина:** Пост без контента.
**Решение:** Добавить хотя бы одно из: `message`, `link`, `source` (фото/видео).

### Error: "(#100) The url you supplied is invalid"
**Причина:** Невалидный URL фото/видео.
**Решение:**
1. URL должен быть публично доступен (не за авторизацией)
2. Проверить HTTPS
3. Для локальных файлов использовать multipart upload вместо URL

### Пост не появляется на странице
**Причины:**
1. `published=false` — пост запланирован или скрыт
2. Гео-таргетинг (`targeting`) исключает вашу страну
3. Модерация Meta — пост на ручной проверке
**Решение:** Проверить статус поста через `GET /{post_id}?fields=is_published,scheduled_publish_time`

### Error: "Scheduled publish time is in the past"
**Причина:** `scheduled_publish_time` меньше текущего Unix timestamp.
**Решение:** Минимум текущее время + 10 минут. Используйте UTC.

### Мультифото пост показывает только 1 фото
**Причина:** Фото загружены с `published=true`.
**Решение:** Загружать каждое фото с `published=false`, затем привязать через `attached_media`.

---

## Reels

### Error: "Video upload failed"
**Причины:**
1. Видео не соответствует требованиям (не 9:16, < 540p, < 23 fps)
2. Длительность < 4 сек или > 90 сек
3. Неподдерживаемый кодек
**Решение:**
```bash
# Проверить параметры видео
ffprobe -v quiet -print_format json -show_format -show_streams video.mp4
# Конвертация в нужный формат
ffmpeg -i input.mp4 -vf "scale=1080:1920" -r 30 -c:v libx264 -crf 23 output.mp4
```

### Reel загрузился, но не публикуется
**Причина:** Не вызван 3-й шаг (finish).
**Решение:** После transfer обязательно вызвать:
```http
POST /{page_id}/video_reels
  ?upload_phase=finish
  &video_id={video_id}
```

### Error: "Reel creation is not allowed for this page"
**Причина:** Reels Publishing API требует одобрения (App Review) для permission `pages_manage_posts`.
**Решение:** Пройти App Review или использовать Development Mode.

---

## Insights (Аналитика)

### Error: "(#100) Unsupported get request. Object with ID does not exist"
**Причина:** Метрика deprecated или неверный ID.
**Решение:**
1. Проверить актуальность метрики (многие deprecated в ноябре 2025)
2. `page_impressions` → заменить на Views
3. `page_fans` → заменить на `page_follows`

### Insights возвращают пустые данные
**Причины:**
1. Страница слишком новая (< 100 подписчиков для некоторых метрик)
2. Период `since/until` некорректен
3. Нет данных за запрашиваемый период
**Решение:** Проверить `period` (day/week/days_28) и даты в ISO 8601.

### Error: "(#3001) Invalid query"
**Причина:** Неподдерживаемая комбинация metric + period.
**Решение:** Не все метрики поддерживают все периоды. `page_fans_city` — только `day`. `post_engaged_users` — только `lifetime`.

---

## Rate Limits

### Error: "(#4) Application request limit reached"
**Причина:** Превышен лимит вызовов API.
**Решение:**
1. Проверить `X-App-Usage` header (значение в %)
2. Реализовать exponential backoff
3. Кэшировать данные
4. Использовать batch requests
5. Уменьшить частоту polling, использовать webhooks

### Error: "(#32) Page request limit reached"
**Причина:** Превышен page-level лимит (4,800 вызовов/24ч).
**Решение:**
1. Проверить `X-Page-Usage` header
2. Оптимизировать запросы (запрашивать только нужные fields)
3. Использовать batch requests для нескольких объектов

---

## Commerce / Shops

### Товары не отображаются в Shops
**Причины:**
1. Каталог не привязан к Page
2. Товары на модерации (24-48 часов для новых)
3. Обязательные поля не заполнены
4. Изображения < 500x500
**Решение:** Commerce Manager → Catalog → Diagnostics для деталей.

### Error: "Product cannot be approved"
**Причина:** Товар нарушает Commerce Policies Meta.
**Решение:** Проверить Meta Commerce Policies. Для туризма: услуги допускаются, но формулировка должна быть как "experience/ticket", не "service".

---

## События

### Событие не создаётся
**Причина:** Отсутствует `name` или `start_time`.
**Решение:** Оба поля обязательны. `start_time` в формате ISO 8601 с timezone.

### RSVP не работает
**Причина:** Permission `rsvp_event` не получен.
**Решение:** Добавить permission в App Review. В Development Mode — добавить пользователя как тестера.

---

## Общие проблемы

### App Review отклонён
**Частые причины:**
1. Screencast не демонстрирует реальное использование
2. Политика конфиденциальности отсутствует или неполная
3. Запрошены лишние permissions
**Решение:**
- Запрашивать минимум необходимых permissions
- Подробный screencast с реальным сценарием
- Privacy Policy на отдельной странице сайта

### Webhooks не приходят
**Причины:**
1. URL не проходит verification challenge
2. HTTPS сертификат невалидный
3. Подписка не активирована в App Dashboard
**Решение:**
1. Endpoint должен отвечать на GET с `hub.challenge`
2. Использовать валидный SSL
3. App Dashboard → Webhooks → Subscribe to events
