# Шаблон: Настройка вебхуков Битрикс24

ДАННЫЕ АКТУАЛЬНЫ НА: 2026-02-16

## Назначение

Настройка входящих и исходящих вебхуков для интеграции Битрикс24 с внешними системами. Включает примеры payload, curl-запросы и типовые сценарии для турагентства.

---

## Пошаговая инструкция

### Часть 1. Входящий вебхук (вызов API из внешних систем)

#### Что это

Входящий вебхук позволяет вызывать REST API Битрикс24 без OAuth-авторизации. Вы получаете уникальный URL с токеном, через который можно создавать лиды, сделки, обновлять данные.

#### Создание входящего вебхука

1. Перейдите: **Настройки > Интеграция > REST API > Входящий вебхук**
2. Нажмите **"Добавить вебхук"**
3. Укажите **название**: например, "Интеграция сайта" или "Telegram бот"
4. Выберите **права доступа** (отметьте нужные):

| Право | Описание | Когда нужно |
|-------|----------|-------------|
| CRM | Работа с лидами, сделками, контактами | Почти всегда |
| Задачи | Создание и управление задачами | Автоматизация задач |
| Пользователи | Получение данных о сотрудниках | Для распределения задач |
| Контакт-центр | Работа с Open Channels | Мессенджеры |
| Диск | Работа с файлами | Загрузка документов |

5. Нажмите **"Сохранить"**
6. Скопируйте сгенерированный **URL вебхука**

#### Формат URL

```
https://ваш-домен.bitrix24.ru/rest/{user_id}/{token}/
```

**Пример:**
```
https://mycompany.bitrix24.ru/rest/1/abc123def456/
```

**ВАЖНО:** Храните токен в безопасности. Любой, у кого есть URL, может вызывать API от имени пользователя.

---

### Часть 2. Исходящий вебхук (Битрикс24 уведомляет вашу систему)

#### Что это

Исходящий вебхук отправляет HTTP POST-запрос на ваш сервер при наступлении события в Битрикс24 (создание сделки, обновление лида и т.д.).

#### Создание исходящего вебхука

1. Перейдите: **Настройки > Интеграция > REST API > Исходящий вебхук**
2. Нажмите **"Добавить вебхук"**
3. Заполните поля:

| Поле | Пример | Описание |
|------|--------|----------|
| URL обработчика | `https://myserver.com/bitrix-webhook` | HTTPS обязателен |
| Событие | ONCRMDEALADD | Какое событие отслеживать |
| Токен приложения | Автоматически | Для проверки подлинности запроса |

4. Нажмите **"Сохранить"**

#### Основные события

| Событие | Описание | Сценарий для туризма |
|---------|----------|---------------------|
| `ONCRMLEADADD` | Создан новый лид | Уведомить Telegram-бот о новой заявке |
| `ONCRMLEADUPDATE` | Обновлен лид | Отследить смену стадии |
| `ONCRMDEALADD` | Создана новая сделка | Записать в Google Sheets |
| `ONCRMDEALUPDATE` | Обновлена сделка | Проверить стадию оплаты |
| `ONCRMCONTACTADD` | Создан контакт | Добавить в рассылку |
| `ONCRMDEALDELETE` | Удалена сделка | Логирование |
| `ONTASKADD` | Создана задача | Уведомить исполнителя |
| `ONTASKUPDATE` | Обновлена задача | Проверить статус задачи |

---

## Примеры

### Примеры curl-запросов (входящий вебхук)

#### Создать лид

```bash
curl -X POST "https://mycompany.bitrix24.ru/rest/1/abc123/crm.lead.add.json" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "TITLE": "Заявка: Desert Safari",
      "NAME": "Иван",
      "LAST_NAME": "Петров",
      "PHONE": [{"VALUE": "+79001234567", "VALUE_TYPE": "MOBILE"}],
      "SOURCE_ID": "WHATSAPP",
      "COMMENTS": "4 гостя, 15 марта, нужен трансфер"
    }
  }'
```

#### Создать сделку

```bash
curl -X POST "https://mycompany.bitrix24.ru/rest/1/abc123/crm.deal.add.json" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "TITLE": "Desert Safari - Петров",
      "CATEGORY_ID": 1,
      "STAGE_ID": "NEW",
      "OPPORTUNITY": 120,
      "CURRENCY_ID": "USD",
      "CONTACT_ID": 45,
      "ASSIGNED_BY_ID": 1,
      "UF_CRM_TOUR_DATE": "2026-03-15",
      "UF_CRM_GUESTS": 4,
      "UF_CRM_HOTEL": "JBR Hilton",
      "UF_CRM_LANGUAGE": "Русский",
      "UF_CRM_TRANSFER": 1,
      "UF_CRM_PAYMENT_TYPE": "Cash USD"
    }
  }'
```

#### Получить список сделок (с фильтром)

```bash
curl -X POST "https://mycompany.bitrix24.ru/rest/1/abc123/crm.deal.list.json" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "STAGE_ID": "NEW",
      ">=OPPORTUNITY": 100
    },
    "select": ["ID", "TITLE", "OPPORTUNITY", "STAGE_ID", "CONTACT_ID"],
    "order": {"DATE_CREATE": "DESC"}
  }'
```

#### Обновить стадию сделки

```bash
curl -X POST "https://mycompany.bitrix24.ru/rest/1/abc123/crm.deal.update.json" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 123,
    "fields": {
      "STAGE_ID": "PREPARATION",
      "UF_CRM_PAYMENT_STATUS": "Полностью"
    }
  }'
```

#### Получить контакт

```bash
curl "https://mycompany.bitrix24.ru/rest/1/abc123/crm.contact.get.json?id=45"
```

#### Пакетный запрос (batch) -- до 50 команд

```bash
curl -X POST "https://mycompany.bitrix24.ru/rest/1/abc123/batch.json" \
  -H "Content-Type: application/json" \
  -d '{
    "halt": 0,
    "cmd": {
      "deals_new": "crm.deal.list?filter[STAGE_ID]=NEW&select[]=ID&select[]=TITLE",
      "deals_paid": "crm.deal.list?filter[STAGE_ID]=WON&select[]=ID&select[]=OPPORTUNITY",
      "contacts_count": "crm.contact.list?select[]=ID"
    }
  }'
```

### Пример payload исходящего вебхука

При создании новой сделки (`ONCRMDEALADD`), Битрикс24 отправит POST-запрос:

```json
{
  "event": "ONCRMDEALADD",
  "data": {
    "FIELDS": {
      "ID": "456"
    }
  },
  "ts": "1708099200",
  "auth": {
    "access_token": "xxxxxxxxx",
    "expires_in": "3600",
    "scope": "crm",
    "domain": "mycompany.bitrix24.ru",
    "server_endpoint": "https://oauth.bitrix.info/rest/",
    "status": "L",
    "client_endpoint": "https://mycompany.bitrix24.ru/rest/",
    "member_id": "xxxxxxxx",
    "application_token": "your_app_token"
  }
}
```

**Обратите внимание:** payload содержит только ID. Чтобы получить все данные, сделайте обратный запрос `crm.deal.get` с полученным ID.

### Пример обработчика (Node.js)

```javascript
const express = require('express');
const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const WEBHOOK_URL = 'https://mycompany.bitrix24.ru/rest/1/abc123/';

app.post('/bitrix-webhook', async (req, res) => {
  const { event, data } = req.body;

  if (event === 'ONCRMDEALADD') {
    const dealId = data.FIELDS.ID;

    // Получить полные данные сделки
    const response = await fetch(
      `${WEBHOOK_URL}crm.deal.get.json?id=${dealId}`
    );
    const deal = await response.json();

    console.log('Новая сделка:', deal.result.TITLE);
    console.log('Сумма:', deal.result.OPPORTUNITY, deal.result.CURRENCY_ID);

    // Здесь можно: отправить в Telegram, записать в Google Sheets и т.д.
  }

  res.status(200).send('OK');
});

app.listen(3000, () => console.log('Webhook handler running on port 3000'));
```

### Пример обработчика (Python / Flask)

```python
from flask import Flask, request
import requests

app = Flask(__name__)
WEBHOOK_URL = "https://mycompany.bitrix24.ru/rest/1/abc123/"

@app.route('/bitrix-webhook', methods=['POST'])
def handle_webhook():
    event = request.form.get('event')
    deal_id = request.form.get('data[FIELDS][ID]')

    if event == 'ONCRMDEALADD':
        # Получить данные сделки
        response = requests.get(f"{WEBHOOK_URL}crm.deal.get.json?id={deal_id}")
        deal = response.json()['result']

        print(f"Новая сделка: {deal['TITLE']}")
        print(f"Сумма: {deal['OPPORTUNITY']} {deal['CURRENCY_ID']}")

    return 'OK', 200

if __name__ == '__main__':
    app.run(port=3000)
```

---

## Коды ошибок

| Код | Описание | Решение |
|-----|----------|---------|
| 200 | Успех | -- |
| 400 | Неверный запрос | Проверить параметры |
| 401 | Не авторизован | Проверить токен вебхука |
| 403 | Нет прав | Добавить нужные права в настройках вебхука |
| 404 | Метод не найден | Проверить название метода (опечатка?) |
| 429 | Слишком много запросов | Лимит: 2 запроса/сек. Используйте batch |
| 500 | Ошибка сервера | Повторить запрос через 5-10 секунд |

---

## Лимиты API

| Параметр | Значение |
|----------|----------|
| Запросов в секунду | 2 на портал |
| Команд в batch | до 50 за 1 запрос |
| Таймаут | Зависит от метода |

**Совет:** Используйте `batch` для массовых операций. Один batch-запрос с 50 командами считается за 1 запрос.

---

## Чек-лист

- [ ] Входящий вебхук создан (Настройки > Интеграция > REST API)
- [ ] Права доступа выбраны (CRM, задачи, пользователи)
- [ ] URL вебхука сохранен в безопасном месте
- [ ] Тестовый запрос crm.deal.list выполнен успешно
- [ ] Исходящий вебхук создан (если нужны уведомления)
- [ ] URL обработчика доступен по HTTPS
- [ ] Обработчик проверен на тестовом событии
- [ ] Токен вебхука НЕ хранится в открытом коде (используйте переменные окружения)
