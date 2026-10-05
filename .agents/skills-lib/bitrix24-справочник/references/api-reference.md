ДАННЫЕ АКТУАЛЬНЫ НА: 2026-02-16

# REST API Битрикс24 -- Справочник

---

## Основы

### Доступ к API

Все облачные порталы Битрикс24 имеют REST API. Два способа авторизации:

| Способ | Описание | Для кого |
|--------|----------|----------|
| Входящий вебхук | URL с токеном, без OAuth | Скрипты, простые интеграции |
| OAuth 2.0 | Полноценная авторизация | Приложения из Маркетплейса |

### Базовый URL

```
https://ваш_домен.bitrix24.ru/rest/
```

### Лимиты

| Параметр | Значение |
|----------|----------|
| Запросов в секунду | 2 на портал |
| Пакетный вызов (batch) | до 50 команд за 1 запрос |
| Таймаут | зависит от метода |

---

## Входящие вебхуки

### Создание

Путь: Настройки > Интеграция > REST API > Входящий вебхук.

При создании выберите нужные права (CRM, задачи, пользователи и т.д.).

### Формат URL

```
https://домен.bitrix24.ru/rest/{user_id}/{token}/{метод}.json
```

### Пример вызова (curl)

```bash
# Получить список сделок
curl "https://mycompany.bitrix24.ru/rest/1/abc123/crm.deal.list.json"

# С фильтром
curl "https://mycompany.bitrix24.ru/rest/1/abc123/crm.deal.list.json?filter[STAGE_ID]=NEW&select[]=ID&select[]=TITLE"
```

### Пример вызова (Python)

```python
import requests

WEBHOOK_URL = "https://mycompany.bitrix24.ru/rest/1/abc123/"

# Создать лид
response = requests.post(f"{WEBHOOK_URL}crm.lead.add.json", json={
    "fields": {
        "TITLE": "Заявка на экскурсию Desert Safari",
        "NAME": "Иван",
        "LAST_NAME": "Петров",
        "PHONE": [{"VALUE": "+79001234567", "VALUE_TYPE": "MOBILE"}],
        "SOURCE_ID": "WEB",
        "UF_CRM_TOUR_DATE": "2026-03-15",
        "UF_CRM_GUESTS": 4
    }
})
print(response.json())
```

### Пример вызова (JavaScript)

```javascript
const WEBHOOK_URL = 'https://mycompany.bitrix24.ru/rest/1/abc123/';

// Получить список сделок
fetch(`${WEBHOOK_URL}crm.deal.list.json`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    filter: { 'STAGE_ID': 'NEW' },
    select: ['ID', 'TITLE', 'OPPORTUNITY', 'CONTACT_ID']
  })
})
.then(res => res.json())
.then(data => console.log(data.result));
```

---

## Исходящие вебхуки

### Настройка

Путь: Настройки > Интеграция > REST API > Исходящий вебхук.

Указать: URL обработчика (HTTPS), события для отслеживания.

### Формат payload

Битрикс24 отправляет POST-запрос с данными:

```json
{
  "event": "ONCRMDEALADD",
  "data": {
    "FIELDS": {
      "ID": "123"
    }
  },
  "auth": {
    "access_token": "...",
    "application_token": "..."
  }
}
```

### Основные события

| Событие | Описание |
|---------|----------|
| `ONCRMLEADADD` | Создан новый лид |
| `ONCRMLEADUPDATE` | Обновлен лид |
| `ONCRMDEALADD` | Создана новая сделка |
| `ONCRMDEALUPDATE` | Обновлена сделка |
| `ONCRMCONTACTADD` | Создан контакт |
| `ONCRMDEALDELETE` | Удалена сделка |
| `ONTASKADD` | Создана задача |
| `ONTASKUPDATE` | Обновлена задача |

---

## Основные методы API

### CRM -- Лиды

| Метод | Описание | HTTP |
|-------|----------|------|
| `crm.lead.list` | Список лидов (фильтр, select, order) | GET/POST |
| `crm.lead.get` | Получить лид по ID | GET |
| `crm.lead.add` | Создать лид | POST |
| `crm.lead.update` | Обновить лид | POST |
| `crm.lead.delete` | Удалить лид | POST |
| `crm.lead.fields` | Описание полей лида | GET |

### CRM -- Сделки

| Метод | Описание | HTTP |
|-------|----------|------|
| `crm.deal.list` | Список сделок | GET/POST |
| `crm.deal.get` | Получить сделку по ID | GET |
| `crm.deal.add` | Создать сделку | POST |
| `crm.deal.update` | Обновить сделку | POST |
| `crm.deal.delete` | Удалить сделку | POST |
| `crm.deal.fields` | Описание полей сделки | GET |

### CRM -- Контакты

| Метод | Описание | HTTP |
|-------|----------|------|
| `crm.contact.list` | Список контактов | GET/POST |
| `crm.contact.get` | Получить контакт | GET |
| `crm.contact.add` | Создать контакт | POST |
| `crm.contact.update` | Обновить контакт | POST |
| `crm.contact.delete` | Удалить контакт | POST |

### CRM -- Компании

| Метод | Описание | HTTP |
|-------|----------|------|
| `crm.company.list` | Список компаний | GET/POST |
| `crm.company.get` | Получить компанию | GET |
| `crm.company.add` | Создать компанию | POST |
| `crm.company.update` | Обновить компанию | POST |

### CRM -- Справочники

| Метод | Описание |
|-------|----------|
| `crm.status.list` | Стадии и статусы |
| `crm.category.list` | Воронки сделок |
| `crm.dealcategory.list` | Категории сделок |
| `crm.currency.list` | Валюты |

### CRM -- Смарт-процессы

| Метод | Описание |
|-------|----------|
| `crm.type.list` | Список типов смарт-процессов |
| `crm.item.list` | Элементы смарт-процесса |
| `crm.item.add` | Создать элемент |
| `crm.item.update` | Обновить элемент |

### Задачи

| Метод | Описание |
|-------|----------|
| `tasks.task.list` | Список задач |
| `tasks.task.add` | Создать задачу |
| `tasks.task.update` | Обновить задачу |
| `tasks.task.complete` | Завершить задачу |
| `tasks.task.getFields` | Поля задачи |
| `task.commentitem.add` | Добавить комментарий |

### Пользователи

| Метод | Описание |
|-------|----------|
| `user.get` | Список пользователей |
| `user.current` | Текущий пользователь |
| `department.get` | Список отделов |

### Служебные

| Метод | Описание |
|-------|----------|
| `batch` | Пакетный вызов (до 50 команд) |
| `app.info` | Информация о приложении |
| `scope` | Доступные разрешения |
| `methods` | Список доступных методов |

---

## Пакетные вызовы (batch)

### Формат запроса

```json
POST /rest/1/TOKEN/batch.json

{
  "halt": 0,
  "cmd": {
    "deals": "crm.deal.list?filter[STAGE_ID]=NEW",
    "contacts": "crm.contact.list?select[]=ID&select[]=NAME"
  }
}
```

- `halt: 0` -- продолжать при ошибке, `halt: 1` -- остановиться
- До 50 команд в одном batch-запросе
- Результаты доступны по именам: `result.deals`, `result.contacts`

---

## Коды ошибок

| Код | Описание | Решение |
|-----|----------|---------|
| 200 | Успех | -- |
| 400 | Неверный запрос | Проверить параметры |
| 401 | Не авторизован | Проверить токен |
| 403 | Нет прав | Настроить права вебхука |
| 404 | Метод не найден | Проверить название метода |
| 429 | Слишком много запросов | Использовать batch, добавить задержку |
| 500 | Ошибка сервера | Повторить через время |

---

## Маркетплейс

### Обзор

Каталог приложений для расширения функционала Битрикс24. Установка в 1 клик.

### Категории

- CRM и продажи
- Маркетинг и рассылки
- Телефония и связь
- Аналитика и отчеты
- Документы и склад
- Интеграции (1С, ERP, и др.)

### Подписка "Маркет Плюс"

Расширенный доступ к приложениям. Включает BitrixGPT, расширенные интеграции.

### Создание своего приложения

1. Зарегистрироваться как разработчик на dev.1c-bitrix.ru
2. Создать приложение (OAuth 2.0)
3. Реализовать backend
4. Опубликовать в Маркетплейсе (модерация)

---

## OAuth 2.0

### Процесс авторизации

1. Приложение перенаправляет пользователя на `https://домен.bitrix24.ru/oauth/authorize/?client_id=APP_ID`
2. Пользователь разрешает доступ
3. Битрикс24 перенаправляет на callback URL с `code`
4. Приложение обменивает `code` на `access_token`
5. API-запросы с `access_token`

### Обновление токена

`access_token` имеет ограниченный срок жизни. Используйте `refresh_token` для обновления.

---

## Интеграция с 1С

| Параметр | Значение |
|----------|----------|
| Тип | Двусторонняя синхронизация |
| Данные | Контакты, компании, счета, каталог товаров |
| Облако | Через приложения Маркетплейса |
| Коробка | Встроенная интеграция |

---

## Полезные ссылки

| Ресурс | URL |
|--------|-----|
| REST API документация | https://apidocs.bitrix24.ru/ |
| Dev портал | https://dev.1c-bitrix.ru/ |
| Маркетплейс | https://www.bitrix24.ru/apps/ |
| Примеры кода | https://dev.1c-bitrix.ru/learning/ |
