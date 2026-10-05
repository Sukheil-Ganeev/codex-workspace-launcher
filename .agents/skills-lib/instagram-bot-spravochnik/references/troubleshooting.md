# Troubleshooting — Instagram Messenger API

## 1. Webhook не получает сообщения

**Симптом:** Настроили webhook, но POST-запросы не приходят.

**Решение:**
- Проверьте, что URL доступен по HTTPS (не HTTP, не self-signed SSL)
- Убедитесь, что GET-верификация прошла успешно (Meta отправляет `hub.challenge`)
- В App Dashboard → Webhooks → подпишитесь на поле `messages` для Instagram
- Проверьте, что приложение в режиме **Live** (не Development)
- Убедитесь, что Instagram-аккаунт привязан к Facebook Page в настройках App

```bash
# Тест webhook доступности
curl -I https://yourdomain.com/webhook
# Должен вернуть 200 OK
```

## 2. Ошибка "(#100) No matching user found"

**Симптом:** При отправке сообщения — ошибка "no matching user".

**Решение:**
- Используйте **Instagram-Scoped User ID (IGSID)**, не Facebook PSID
- IGSID приходит в webhook event как `event.sender.id`
- Нельзя использовать Instagram username или числовой ID аккаунта
- IGSID уникален для каждой пары (ваш аккаунт + пользователь)

## 3. Ошибка "(#10) This message is sent outside of allowed window"

**Симптом:** Попытка отправить сообщение, но получаете ошибку окна.

**Решение:**
- 24-часовое окно истекло — пользователь не писал вам более 24 часов
- Дождитесь нового сообщения от пользователя
- Для живого оператора: используйте тег `HUMAN_AGENT` (продлевает до 7 дней)
- Нельзя отправлять автоматические сообщения с тегом `HUMAN_AGENT`

## 4. Ошибка "(#190) Invalid OAuth access token"

**Симптом:** Токен перестал работать.

**Решение:**
- Short-lived token живёт 1 час — обменяйте на long-lived (60 дней)
- Long-lived token: обновляйте каждые 50-55 дней
- Page Access Token бессрочный, если получен из long-lived User Token
- Проверьте, что не отозвали permissions у приложения

```bash
# Проверка валидности токена
curl "https://graph.facebook.com/v21.0/debug_token?\
input_token=YOUR_TOKEN&\
access_token=APP_ID|APP_SECRET"
```

## 5. Ошибка "(#613) Calls to this api have exceeded the rate limit"

**Симптом:** Превышен лимит API вызовов.

**Решение:**
- Текущий лимит: **200 вызовов/час** на аккаунт (снижен с 5,000 в 2025)
- Подождите 1 час (скользящее окно)
- Внедрите очередь сообщений (Redis Queue, Bull)
- Батчите запросы где возможно
- Мониторьте заголовок `X-App-Usage` в ответах API

## 6. Private Reply не отправляется

**Симптом:** Пытаетесь отправить Private Reply на комментарий — ошибка.

**Решение:**
- Убедитесь, что комментарий не старше 24 часов
- Private Reply можно отправить **только 1 раз** на каждый комментарий
- Проверьте permission `instagram_manage_comments`
- Комментарий должен быть к **вашему** посту
- Не работает для комментариев к Live-трансляциям

## 7. Ice Breakers не отображаются

**Симптом:** Установили Ice Breakers, но пользователи их не видят.

**Решение:**
- Ice Breakers видны только при **первом** открытии диалога (нет истории сообщений)
- Убедитесь, что передаёте `"platform": "instagram"` в запросе
- Максимум 4 вопроса — если указали больше, запрос откажет
- Проверьте через GET:

```bash
curl "https://graph.facebook.com/v21.0/me/messenger_profile?\
fields=ice_breakers&\
platform=instagram&\
access_token=PAGE_ACCESS_TOKEN"
```

## 8. Generic Template не показывает изображения

**Симптом:** Карточки отображаются, но без картинок.

**Решение:**
- URL изображения должен быть **публично доступен** (не localhost, не за auth)
- Формат: JPEG или PNG (GIF не поддерживается в Template)
- Размер: до 8 MB
- HTTPS обязателен
- Проверьте, что URL не редиректит (Meta не следует за редиректами)

## 9. Webhook получает дубликаты событий

**Симптом:** Одно и то же сообщение приходит несколько раз.

**Решение:**
- Meta может переотправлять события если ваш сервер не вернул **200 OK** вовремя
- Верните `200` как можно быстрее, обработку делайте асинхронно
- Храните `message_id` в кэше и проверяйте дубликаты:

```javascript
const processedMessages = new Set();

app.post('/webhook', (req, res) => {
  res.status(200).send('OK'); // Отвечаем СРАЗУ

  // Обработка асинхронно
  req.body.entry?.forEach(entry => {
    entry.messaging?.forEach(event => {
      const msgId = event.message?.mid;
      if (msgId && processedMessages.has(msgId)) return;
      if (msgId) processedMessages.add(msgId);
      handleEvent(event);
    });
  });
});
```

## 10. Ошибка "App Not Setup" или "(#200) Requires permission"

**Симптом:** API возвращает ошибку о недостающих permissions.

**Решение:**
- Пройдите **App Review** для `instagram_manage_messages`
- В App Dashboard → App Review → Permissions and Features
- Подготовьте: скриншоты, видео использования, описание
- Время рассмотрения: 3-7 рабочих дней
- Для тестирования: добавьте аккаунт как Test User в App Settings

## 11. Persistent Menu не появляется

**Симптом:** Настроили меню, но иконка не показывается.

**Решение:**
- Persistent Menu может не показываться на старых версиях приложения Instagram
- Передавайте `"platform": "instagram"` в запросе
- Максимум 20 пунктов на одном уровне
- Только 1 уровень вложенности (без подменю, в отличие от FB Messenger)
- После установки подождите 5-10 минут — кэш Meta

## 12. Story Mention webhook не срабатывает

**Симптом:** Пользователь упомянул вас в Story, но webhook молчит.

**Решение:**
- Подпишитесь на поле `messaging` (story_mention приходит как messaging event)
- Проверьте, что аккаунт — Business/Creator (Personal не получает story webhooks)
- Story mentions доступны только 24 часа (как сама Story)
- Убедитесь, что permission `instagram_manage_messages` получен

## 13. Бот отвечает на свои же сообщения (бесконечный цикл)

**Симптом:** Бот получает webhook о своих исходящих сообщениях и отвечает на них.

**Решение:**
- Проверяйте поле `event.message.is_echo`:

```javascript
app.post('/webhook', (req, res) => {
  res.status(200).send('OK');
  req.body.entry?.forEach(entry => {
    entry.messaging?.forEach(event => {
      // Игнорируем эхо своих сообщений
      if (event.message?.is_echo) return;
      if (event.message) handleMessage(event);
    });
  });
});
```

## 14. Ошибка X-Hub-Signature-256 verification failed

**Симптом:** Подпись webhook не проходит проверку.

**Решение:**
- Используйте **App Secret** (не Access Token) для HMAC
- Подпись считается от raw body (до JSON-парсинга)
- Алгоритм: HMAC-SHA256
- Заголовок начинается с `sha256=` — не забудьте это при сравнении

```javascript
const crypto = require('crypto');

function verify(signature, rawBody, appSecret) {
  const expected = 'sha256=' + crypto
    .createHmac('sha256', appSecret)
    .update(rawBody)
    .digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expected)
  );
}
```

## 15. Сообщения отправляются, но пользователь не видит их

**Симптом:** API возвращает 200 OK, но сообщения не доходят.

**Решение:**
- Проверьте, что отправляете на правильный IGSID (из webhook, не выдуманный)
- Пользователь мог заблокировать ваш аккаунт
- Пользователь мог ограничить DM (Settings → Privacy → Messages)
- Если аккаунт приватный — некоторые пользователи не получают DM от бизнесов
- Проверьте, что 24-часовое окно не истекло
- Убедитесь, что `messaging_type` корректный (`RESPONSE` для ответов)
