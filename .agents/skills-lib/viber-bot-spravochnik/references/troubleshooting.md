# Viber Bot API — Troubleshooting

## Webhook не работает

### Симптом: Бот не получает сообщения от пользователей

**Проверка 1: Webhook установлен?**
```bash
curl -X POST https://chatapi.viber.com/pa/get_account_info \
  -H "X-Viber-Auth-Token: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```
Проверьте поле `webhook` в ответе.

**Проверка 2: SSL-сертификат**
- Viber требует **доверенный CA-signed** сертификат
- Self-signed НЕ принимается
- Решение: Let's Encrypt (бесплатно) или Cloudflare

**Проверка 3: Сервер отвечает HTTP 200**
- Viber ожидает ответ 200 на каждый callback
- Если сервер отвечает 500/404 — Viber прекратит отправку
- Добавьте `return Response(status=200)` в конце обработчика

**Проверка 4: URL доступен извне**
```bash
curl -I https://your-server.com/viber/webhook
```

### Симптом: set_webhook возвращает ошибку

| Код ошибки | Причина | Решение |
|------------|---------|---------|
| 1 | URL недоступен | Проверьте HTTPS и доступность |
| 2 | Невалидный токен | Проверьте X-Viber-Auth-Token |
| 3 | Некорректный URL | URL должен начинаться с https:// |
| 4 | Невалидный сертификат | Используйте CA-signed сертификат |

---

## Сообщения не доставляются

### Симптом: send_message возвращает ошибку

| status | status_message | Причина | Решение |
|--------|---------------|---------|---------|
| 0 | ok | Успех | — |
| 1 | invalidUrl | Невалидный URL | Проверьте URL в media/thumbnail |
| 2 | invalidAuthToken | Неверный токен | Обновите токен |
| 3 | badData | Некорректные данные | Проверьте JSON-структуру |
| 4 | missingData | Пропущены обязательные поля | Добавьте receiver, type |
| 5 | receiverNotRegistered | Получатель не в Viber | Пользователь удалил Viber |
| 6 | receiverNotSubscribed | Не подписчик | Можно отправить только через conversation_started |
| 7 | publicAccountBlocked | Бот заблокирован | Пользователь заблокировал бота |
| 8 | publicAccountNotFound | Бот не найден | Проверьте токен |
| 9 | publicAccountSuspended | Бот приостановлен | Обратитесь в Viber support |
| 10 | webhookNotSet | Webhook не установлен | Вызовите set_webhook |
| 11 | receiverNoSuitableDevice | Устройство не поддерживает | Отправьте текстовое сообщение |
| 12 | tooManyRequests | Превышен rate limit | Снизьте частоту запросов |

### Симптом: Сообщение отправлено (status=0), но пользователь не видит

1. Проверьте `delivered` и `seen` callbacks
2. Если `failed` callback — устройство недоступно
3. Пользователь мог заблокировать бота (status 7 при следующей отправке)

---

## Rich Media не отображается

### Симптом: Пользователь видит alt_text вместо карусели

**Причина:** Устаревшая версия Viber (Rich Media требует 6.7+)

**Решение:**
- Укажите `min_api_version: 7`
- Добавьте `alt_text` с текстовой альтернативой
- Для старых устройств отправляйте обычный текст с keyboard

### Симптом: Кнопки в Rich Media не работают

**Проверка:**
- `location-picker` и `share-phone` НЕ работают в Rich Media
- Используйте только `reply`, `open-url`, `none`
- Проверьте, что `ActionBody` не пустой для `reply` и `open-url`

### Симптом: Изображения не загружаются в Rich Media

- URL должен быть доступен публично (не localhost)
- Поддерживаемые форматы: JPEG, PNG
- Рекомендуемый размер: 480x360 px для карточек

---

## Клавиатура не отображается

### Симптом: Сообщение приходит без кнопок

1. Проверьте `min_api_version >= 3` (для клавиатур)
2. Структура `keyboard` должна содержать `"Type": "keyboard"`
3. Массив `Buttons` не должен быть пустым
4. Сумма Columns во всех кнопках одной строки <= 6

### Симптом: Текст на кнопках некорректно отображается

- HTML-теги должны быть валидными
- Поддерживаются: `<b>`, `<i>`, `<u>`, `<s>`, `<font>`, `<br>`
- Атрибут color в `<font>`: `<font color="#FFFFFF">Text</font>`
- Кавычки в JSON экранируйте: `\"` внутри строки

---

## tracking_data проблемы

### Симптом: tracking_data приходит пустым

1. Проверьте, что вы отправляете `tracking_data` в исходном сообщении
2. После `subscribed` события tracking_data сбрасывается
3. Максимум 4000 символов — если превышен, данные обрезаются

### Симптом: JSON в tracking_data невалидный

- Используйте `json.dumps()` при отправке
- При получении — `json.loads()` с try/except
- Не используйте одинарные кавычки — только двойные (JSON стандарт)

---

## Broadcast проблемы

### Симптом: broadcast_message возвращает ошибку "tooManyRequests"

**Причина:** Превышен rate limit (500 req / 10 sec)

**Решение:**
```python
import time

def broadcast_with_throttle(subscribers, message, batch_size=300):
    for i in range(0, len(subscribers), batch_size):
        batch = subscribers[i:i+batch_size]
        send_broadcast(batch, message)
        time.sleep(0.05)  # 50ms между запросами
```

### Симптом: Часть подписчиков не получает рассылку

1. Проверьте `failed_list` в ответе broadcast_message
2. Удалённые/заблокировавшие бота пользователи — в failed_list
3. Очистите локальную БД от невалидных ID

---

## Conversation Started не срабатывает

### Симптом: Бот не получает conversation_started

1. Проверьте `event_types` в set_webhook — должен включать `"conversation_started"`
2. Событие приходит **только при первом открытии** чата
3. После subscribe/unsubscribe цикла — приходит **повторно**

### Симптом: context из deep link не приходит

1. Deep links работают только на **Android и iOS** (НЕ Desktop)
2. Формат: `viber://pa?chatURI=YOUR_URI&context=YOUR_CONTEXT`
3. Некоторые браузеры не поддерживают deep links — тестируйте из Viber

---

## Локальная разработка

### ngrok (рекомендуется)

```bash
# Установка
npm install -g ngrok
# Или скачать с ngrok.com

# Запуск
ngrok http 8080

# Получите URL вида: https://abc123.ngrok.io
# Используйте как webhook URL
```

### Cloudflare Tunnel

```bash
# Установка
winget install cloudflare.cloudflared

# Запуск
cloudflared tunnel --url http://localhost:8080

# Получите URL вида: https://xxx.trycloudflare.com
```

### Отладка callbacks

```python
@app.route('/viber/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    # Логирование всех callbacks
    import logging
    logging.info(f"Event: {data.get('event')}")
    logging.info(f"Full data: {json.dumps(data, indent=2, ensure_ascii=False)}")

    # ... обработка
    return Response(status=200)
```

---

## Коды ошибок API (полная таблица)

| status | Описание |
|--------|----------|
| 0 | Успех (ok) |
| 1 | Невалидный URL |
| 2 | Невалидный auth token |
| 3 | Некорректные данные (bad data) |
| 4 | Пропущены обязательные данные |
| 5 | Получатель не зарегистрирован в Viber |
| 6 | Получатель не подписан на бота |
| 7 | Бот заблокирован получателем |
| 8 | Бот не найден |
| 9 | Бот приостановлен |
| 10 | Webhook не установлен |
| 11 | Устройство получателя не поддерживает тип сообщения |
| 12 | Превышен rate limit |
| 13 | Домен API недоступен |
| 14 | Устройство получателя не поддерживает min_api_version |
