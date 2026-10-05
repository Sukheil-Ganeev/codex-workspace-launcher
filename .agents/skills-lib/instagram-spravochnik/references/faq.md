# Instagram Graph API — FAQ (15 вопросов)

> **DM-боты:** см. `instagram-bot-справочник`

---

## 1. Какой тип аккаунта нужен для API?

**Business** или **Creator**. Personal аккаунты не поддерживаются — Basic Display API закрыт с декабря 2024. Конвертация: Instagram → Settings → Account → Switch to Professional Account → выберите категорию Tourism/Travel Agency → привяжите Facebook Page.

---

## 2. Чем отличается Instagram Login от Facebook Login?

**Instagram API with Instagram Login** — упрощённая авторизация напрямую через Instagram. Доступны базовые permissions: `instagram_basic`, `instagram_content_publish`, `instagram_manage_comments`, `instagram_manage_insights`. Не требует Facebook Page.

**Instagram API with Facebook Login** — полный доступ через Facebook OAuth. Все permissions, включая Shopping, расширенные Insights, Mentioned Media. Требует Facebook Page.

Для полноценного бизнес-использования рекомендуется Facebook Login.

---

## 3. Как пройти App Review?

1. Facebook App Dashboard → App Review → Permissions and Features
2. Запросите нужные permissions (instagram_content_publish, instagram_manage_insights и др.)
3. Заполните форму: описание использования, скриншоты интерфейса, видео (опционально)
4. Отправьте на рассмотрение
5. Ожидание: 3-7 рабочих дней

**Советы:** опишите конкретный бизнес-кейс (автопостинг туров), приложите реальные скриншоты, покажите как используется каждый permission.

---

## 4. Как долго живёт Access Token?

- **Short-lived:** ~1 час (из Graph API Explorer)
- **Long-lived:** 60 дней (обмен через `fb_exchange_token`)
- При регулярном использовании long-lived token обновляется автоматически
- Рекомендация: настройте cron-обновление каждые 50 дней

---

## 5. Сколько постов можно опубликовать через API?

**25 публикаций за 24 часа** на один Instagram аккаунт. Это скользящее окно. Карусель считается как 1 публикация (не по количеству медиа). Reels и Stories тоже входят в лимит 25/день.

---

## 6. Какой формат нужен для Reels?

- **Формат:** MP4, MOV
- **Разрешение:** минимум 540x960, рекомендуется 1080x1920
- **Соотношение:** 9:16 (вертикально)
- **Длительность:** 3-90 секунд
- **Размер:** до 1 ГБ
- **Кодек:** H.264 видео, AAC аудио
- **FPS:** 24-60

---

## 7. Можно ли добавить стикеры в Stories через API?

**Нет.** API не поддерживает интерактивные стикеры (опросы, вопросы, слайдеры, обратный отсчёт), музыку, AR-фильтры и link-стикеры. Через API можно опубликовать только фото или видео Story без интерактивных элементов.

---

## 8. Как настроить Instagram Shopping через API?

1. Создайте каталог в Commerce Manager (business.facebook.com/commerce)
2. Добавьте товары (вручную, Data Feed, или Shopify/WooCommerce)
3. Подключите каталог к Instagram Shopping
4. Пройдите App Review для permission `instagram_shopping_tag_products`
5. Тегируйте товары через endpoint `POST /{media-id}/product_tags`

**Требования:** Business аккаунт (не Creator), страна из списка поддерживаемых (ОАЭ — да).

---

## 9. Какие метрики Insights доступны в v22?

**Аккаунт:** reach, accounts_engaged, follows_and_unfollows, profile_views, follower_demographics (country, city, age, gender).

**Медиа:** reach, views, likes, comments, shares, saved, follows, profile_visits, total_interactions.

**Reels дополнительно:** skip_rate (процент пропусков в первые 3 секунды).

**Stories:** reach, views, replies, follows, profile_visits, shares.

**Депрекированы:** video_views, plays, impressions, email_contacts, phone_call_clicks.

---

## 10. Сколько хэштегов можно искать через API?

**30 уникальных хэштегов за 7 дней** на один Instagram аккаунт. Каждый поисковый запрос расходует 1 слот из 30. Результаты: до 50 медиа (Top) и 50 медиа (Recent) на каждый хэштег.

---

## 11. Как работают Collaborative Posts через API?

При создании контейнера добавьте параметр `collaborators` — массив username (до 3 соавторов):
```bash
-F "collaborators=[\"partner_username\"]"
```
Соавтор получит приглашение в приложении Instagram и должен одобрить его вручную. После одобрения пост появится в обоих профилях.

---

## 12. Есть ли API для Broadcast Channels?

**Нет (на февраль 2026).** Broadcast Channels управляются только вручную через приложение Instagram. Нет endpoints для создания, публикации или аналитики каналов через API.

---

## 13. Как работает oEmbed после 2025?

Старый oEmbed закрыт в апреле 2025. Новый endpoint — Meta oEmbed Read:
```
GET /v22.0/instagram_oembed?url={POST_URL}&access_token={APP_TOKEN}
```
Требуется App Access Token и approved app. Поля `thumbnail_url`, `author_name` удалены — генерируйте превью самостоятельно.

---

## 14. Можно ли запланировать публикацию на будущее?

API не имеет встроенного параметра `publish_at`. Планирование реализуется внешними средствами:
- **Cron/scheduler** — ваш сервер вызывает API в нужное время
- **Make.com / n8n** — no-code планировщик
- Контейнеры хранятся 24 часа — создайте заранее, опубликуйте по расписанию

---

## 15. Какая версия API актуальна в 2026?

**v22.0** — текущая стабильная версия. Базовый URL: `https://graph.facebook.com/v22.0/`. Важные изменения: метрика `views` заменяет `plays`/`impressions`, новая метрика `skip_rate` для Reels, обновлённые объекты IG User / IG Media / IG Comment.
