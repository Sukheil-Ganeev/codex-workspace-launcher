# Troubleshooting — Facebook Messenger Bot

## 1. Webhook не проходит верификацию

**Симптом:** Meta показывает ошибку при сохранении Callback URL.

**Причины и решения:**
- Сервер не отвечает на GET-запрос с `hub.challenge` → проверь route `/webhook` для метода GET
- `hub.verify_token` не совпадает → сравни токен в коде и в Meta Dashboard
- URL не HTTPS → используй ngrok для разработки или SSL-сертификат
- Сервер не доступен извне → проверь firewall, порт, ngrok
- Ответ не 200 → должен возвращать `hub.challenge` как plain text с кодом 200

```javascript
// Правильно
res.status(200).send(req.query['hub.challenge']);

// Неправильно — JSON вместо plain text
res.json({ challenge: req.query['hub.challenge'] });
```

## 2. Webhook верифицирован, но сообщения не приходят

**Причины:**
- Не подписан на events → `POST /me/subscribed_apps` с полем `subscribed_fields`
- Page не привязана к App → проверь в App Dashboard → Messenger Settings
- Bot в режиме Development → только администраторы/тестеры могут писать
- Token протух → перегенерируй Page Access Token

**Диагностика:**
```bash
# Проверить подписку
curl "https://graph.facebook.com/v22.0/{PAGE_ID}/subscribed_apps?access_token={TOKEN}"
```

## 3. Ошибка 190: Invalid OAuth Token

**Причины:**
- Токен истёк (Short-Lived = 1 час, Long-Lived User = 60 дней)
- Permissions отозваны
- App Secret изменился

**Решение:**
1. Перегенерируй токен в App Dashboard → Messenger Settings
2. Для production: используй бессрочный Page Token (FAQ #15)
3. Настрой мониторинг: логируй ошибки 190 и автоматически уведомляй

## 4. Ошибка 10: Permission Denied

**Причины:**
- Не запрошен `pages_messaging` permission
- App не прошёл App Review для публичного использования
- Page ограничена Meta

**Решение:**
- Проверь permissions: App Dashboard → App Review → Permissions
- Для production: подай на App Review с демо-видео и описанием use case
- Для разработки: добавь себя как тестера в App Roles

## 5. Сообщение не доставлено (error 551)

**Причины:**
- 24-часовое окно истекло
- Пользователь заблокировал Page
- Неверный PSID

**Решение:**
```json
// Ошибка
{
  "error": {
    "message": "(#551) This person isn't available right now.",
    "code": 551
  }
}
```
- Проверь что PSID корректный
- Используй Message Tags если вне 24ч окна
- Если пользователь заблокировал — ничего не сделать, удали из активных

## 6. Rate Limit Exceeded (error 4)

**Симптом:** `(#4) Application request limit reached`

**Решение:**
- Добавь exponential backoff: 1с → 2с → 4с → 8с
- Используй Batch API (до 50 запросов за раз)
- Кэшируй данные профилей пользователей
- Проверь лимит: 200 * количество подписчиков в час

```javascript
async function sendWithRetry(payload, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      return await callSendAPI(payload);
    } catch (err) {
      if (err.code === 4 && i < retries - 1) {
        await sleep(Math.pow(2, i) * 1000);
        continue;
      }
      throw err;
    }
  }
}
```

## 7. Template отображается как текст / не рендерится

**Причины:**
- Неверная структура JSON (опечатка в `template_type`)
- Превышен лимит элементов (Generic: max 10, Buttons: max 3)
- URL картинки недоступен или не HTTPS
- Заголовок превышает 80 символов

**Решение:**
- Валидируй JSON через Send API Debug tool
- Все URL изображений должны быть HTTPS
- Тестируй каждый template отдельно

## 8. Persistent Menu не появляется

**Причины:**
- Кэш Messenger (обновляется с задержкой до 24ч)
- Неверная структура JSON
- Более 3 items на уровне

**Решение:**
1. Удали старое меню: `DELETE /me/messenger_profile` с `{"fields": ["persistent_menu"]}`
2. Подожди 5 минут
3. Установи заново
4. Очисти кэш: удали беседу и начни заново

## 9. Get Started кнопка не работает

**Причины:**
- Не настроен payload
- Пользователь уже общался с ботом ранее (Get Started показывается только новым)

**Решение:**
- Удали беседу в Messenger, начни заново
- Проверь обработку `event.postback.payload === 'GET_STARTED'`
- Убедись что Greeting настроен

## 10. X-Hub-Signature-256 не совпадает

**Причины:**
- Используется SHA1 вместо SHA256
- `rawBody` отличается от парсированного body
- App Secret неверный

**Решение:**
```javascript
// Express: сохрани raw body ДО парсинга
app.use(express.json({
  verify: (req, res, buf) => {
    req.rawBody = buf;
  }
}));
```

## 11. Handover Protocol: pass_thread_control не работает

**Причины:**
- App не назначен как Primary Receiver
- `target_app_id` неверный
- Secondary Receiver не подписан на `messaging_handovers`

**Решение:**
1. App Dashboard → Messenger Settings → Handover Protocol
2. Назначь Primary и Secondary Receiver
3. Оба приложения должны быть подписаны на `messaging_handovers`

## 12. One-Time Notification: токен не приходит

**Причины:**
- Не подписан на `messaging_optins` event
- Пользователь отклонил запрос
- Template неверно сформирован

**Решение:**
- Подпиши webhook на `messaging_optins`
- Проверь `event.optin.type === 'one_time_notif_req'`
- Убедись что `payload` и `title` заполнены в запросе

## 13. Recurring Notifications: ошибка при отправке

**Причины:**
- Токен уже использован (нужно взять новый из ответа)
- Пользователь отписался
- Частота отправки превышена

**Решение:**
- После каждой отправки сохраняй новый `notification_messages_token` из ответа
- Проверяй статус подписки перед отправкой
- Не превышай выбранную частоту (daily/weekly/monthly)

## 14. Дубликаты сообщений от webhook

**Причины:**
- Сервер отвечает медленнее 5 секунд → Meta повторяет запрос
- Нет дедупликации по `message.mid`

**Решение:**
```javascript
const processedMessages = new Set(); // В production: Redis

app.post('/webhook', (req, res) => {
  res.status(200).send('EVENT_RECEIVED'); // Отвечай мгновенно!

  const event = req.body.entry[0].messaging[0];
  const mid = event.message?.mid;

  if (mid && processedMessages.has(mid)) return;
  if (mid) processedMessages.add(mid);

  processEvent(event).catch(console.error);
});
```

## 15. Бот не работает в Production (после App Review)

**Причины:**
- Permissions не одобрены для public use
- Webhook URL изменился
- Токен привязан к dev-окружению

**Чек-лист для production:**
- [ ] App Review пройден (`pages_messaging` одобрен)
- [ ] Page Token бессрочный
- [ ] Webhook URL стабильный (не ngrok)
- [ ] SSL-сертификат валидный
- [ ] X-Hub-Signature-256 проверяется
- [ ] Логирование ошибок настроено
- [ ] Rate limit handling с retry
- [ ] Дедупликация по mid
- [ ] Мониторинг uptime webhook
