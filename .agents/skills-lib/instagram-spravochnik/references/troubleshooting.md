# Instagram Graph API — Troubleshooting (15 проблем)

> **DM-боты:** см. `instagram-bot-справочник`

---

## 1. Ошибка (#100) Invalid parameter

**Причина:** Неверный формат данных, отсутствующий обязательный параметр или неверное значение.

**Решение:**
- Проверьте что все обязательные параметры указаны
- `image_url` должен быть публично доступным HTTPS URL
- `media_type` должен быть `VIDEO`, `REELS`, `STORIES` или `CAROUSEL`
- Для карусели `is_carousel_item=true` для каждого элемента
- Проверьте JSON-формат для массивов (collaborators, children)

---

## 2. Ошибка (#190) Invalid OAuth access token

**Причина:** Токен истёк, отозван или невалиден.

**Решение:**
- Short-lived токен живёт ~1 час — обновите через Graph API Explorer
- Long-lived токен живёт 60 дней — обменяйте через `fb_exchange_token`
- Проверьте что токен имеет нужные permissions
- Убедитесь что Facebook App не деактивирован

```bash
# Проверка токена
curl "https://graph.facebook.com/debug_token?\
input_token={TOKEN}&access_token={APP_ID}|{APP_SECRET}"
```

---

## 3. Ошибка (#10) Application does not have permission

**Причина:** Permission не пройден через App Review или не запрошен при авторизации.

**Решение:**
- Проверьте список granted permissions в Graph API Explorer
- Подайте на App Review для нужных permissions
- При генерации токена убедитесь что все permissions отмечены
- Для тестирования добавьте себя как Test User в App Dashboard

---

## 4. Ошибка (#613) Rate limit exceeded

**Причина:** Превышен лимит 200 запросов/час на аккаунт.

**Решение:**
- Подождите 1 час (скользящее окно)
- Оптимизируйте запросы: используйте batch requests
- Кэшируйте данные локально
- Запрашивайте только нужные fields (не запрашивайте всё подряд)

```javascript
// Пример retry с экспоненциальной задержкой
const callWithRetry = async (fn, retries = 3) => {
  try { return await fn(); }
  catch (e) {
    if (e.code === 613 && retries > 0) {
      await new Promise(r => setTimeout(r, 60000 * (4 - retries)));
      return callWithRetry(fn, retries - 1);
    }
    throw e;
  }
};
```

---

## 5. Ошибка (#4) Application request limit reached

**Причина:** Превышен лимит публикаций (25/день) или общий лимит приложения.

**Решение:**
- Публикации: подождите до следующего 24-часового окна
- Распределите публикации равномерно (не все разом)
- Карусель = 1 публикация (используйте карусели для экономии)

---

## 6. Видео не публикуется — статус PROCESSING зависает

**Причина:** Видео не соответствует требованиям или сервер Meta перегружен.

**Решение:**
- Проверьте формат: MP4/MOV, H.264, AAC
- Размер: до 100 МБ (Feed), до 1 ГБ (Reels)
- Длительность: 3-60 сек (Feed), 3-90 сек (Reels)
- Разрешение: минимум 540x960
- URL видео должен быть публично доступен и стабилен (не временная ссылка)
- Проверяйте статус каждые 30 секунд, таймаут 10 минут

```bash
# Проверка статуса
curl "https://graph.facebook.com/v22.0/{CONTAINER_ID}?\
fields=status_code,status&access_token={TOKEN}"
# Ждите status_code=FINISHED
```

---

## 7. Карусель не создаётся — ошибка children

**Причина:** Неверный формат массива children или контейнеры не готовы.

**Решение:**
- Каждый элемент должен быть создан с `is_carousel_item=true`
- Передавайте children как строку с запятыми: `children=ID1,ID2,ID3`
- Минимум 2 элемента, максимум 10
- Все элементы должны быть одного типа (фото) или смешанные (фото+видео)
- Видео-элементы должны иметь status_code=FINISHED

---

## 8. Insights возвращают пустые данные

**Причина:** Недостаточно данных, неверный период или устаревшие метрики.

**Решение:**
- Аккаунт должен иметь минимум 100 подписчиков для демографии
- Используйте правильный `period`: day, week, days_28, lifetime
- Проверьте `since`/`until` формат: UNIX timestamp или YYYY-MM-DD
- С v22 используйте `views` вместо `video_views`/`plays`/`impressions`
- Stories Insights доступны только 72 часа после публикации

---

## 9. Hashtag Search не возвращает результаты

**Причина:** Лимит исчерпан, хэштег запрещён или неверный user_id.

**Решение:**
- Проверьте лимит: 30 уникальных хэштегов за 7 дней
- Некоторые хэштеги запрещены Instagram (нет результатов)
- `user_id` должен быть вашим Instagram Business Account ID
- Permission `instagram_basic` должен быть активен

---

## 10. Product Tags не работают

**Причина:** Shopping не настроен, каталог не подключён или permission отсутствует.

**Решение:**
- Убедитесь что аккаунт Business (не Creator)
- Commerce Manager → каталог создан и товары добавлены
- Каталог подключён к Instagram Shopping
- Instagram Shopping одобрен Meta
- Permission `instagram_shopping_tag_products` пройден через App Review
- `product_id` существует в каталоге

---

## 11. Webhook не получает события

**Причина:** Неверная настройка, SSL-проблемы или подписка не активна.

**Решение:**
- URL должен быть HTTPS с валидным SSL (не self-signed)
- Verify Token должен совпадать с настройками в App Dashboard
- Подпишитесь на нужные fields: `comments`, `mentions`, `story_insights`
- Проверьте что endpoint отвечает 200 OK на GET-верификацию
- Логируйте все входящие запросы для отладки

---

## 12. Collaborative Post — соавтор не получает приглашение

**Причина:** Неверный username, аккаунт не Business/Creator или лимит.

**Решение:**
- Username должен быть точным (без @)
- Соавтор должен иметь Business или Creator аккаунт
- Максимум 3 соавтора
- Соавтор должен одобрить приглашение в приложении Instagram (не через API)
- Проверьте что соавтор не заблокировал ваш аккаунт

---

## 13. oEmbed возвращает ошибку после обновления 2025

**Причина:** Старый oEmbed endpoint закрыт, нужен новый Meta oEmbed Read.

**Решение:**
- Используйте новый endpoint: `GET /v22.0/instagram_oembed`
- Требуется App Access Token (не User Token): `{APP_ID}|{APP_SECRET}`
- App должен быть reviewed и approved
- Только публичный контент (приватные посты не встраиваются)
- Поля `thumbnail_url`, `author_name` больше не возвращаются

---

## 14. Reels — cover_url не применяется

**Причина:** URL недоступен, формат не поддерживается или параметр игнорируется.

**Решение:**
- `cover_url` должен быть публично доступным HTTPS URL
- Формат: JPEG или PNG
- Рекомендуемое разрешение: 1080x1920 (9:16)
- Если `cover_url` не указан, используется `thumb_offset` (мс от начала видео)
- Проверьте что URL доступен без авторизации

---

## 15. Instagram Account ID не находится

**Причина:** Аккаунт не привязан к Facebook Page или Page не привязана к App.

**Решение:**
1. Убедитесь что Instagram аккаунт — Business (не Personal)
2. Проверьте привязку: Instagram Settings → Linked Accounts → Facebook
3. Facebook Page должна быть привязана к вашему Facebook App
4. Запросите pages_show_list permission

```bash
# Получить список Pages и их Instagram аккаунтов
curl "https://graph.facebook.com/v22.0/me/accounts?\
fields=name,instagram_business_account&access_token={TOKEN}"
```
