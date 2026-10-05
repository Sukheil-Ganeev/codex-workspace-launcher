# Cheatsheet — api-design-principles

## HTTP-методы
| Метод | Семантика | Идемпотентность | Тело запроса | Тело ответа |
|-------|-----------|-----------------|--------------|-------------|
| GET | Получить ресурс | Да | Нет | Да |
| POST | Создать ресурс | Нет | Да | Да |
| PUT | Заменить ресурс целиком | Да | Да | Да |
| PATCH | Частичное обновление | Нет | Да | Да |
| DELETE | Удалить ресурс | Да | Нет | Опционально |

## Именование ресурсов REST
| Правильно | Неправильно | Почему |
|-----------|-------------|--------|
| `GET /users` | `GET /getUsers` | Ресурсы — существительные |
| `POST /users` | `POST /createUser` | HTTP-метод = действие |
| `GET /users/123/orders` | `GET /getUserOrders?id=123` | Иерархия через URL |
| `PATCH /users/123` | `POST /updateUser` | Используй правильный метод |
| `/users` (множ. число) | `/user` (ед. число) | Коллекция = множественное |

## HTTP-статусы (быстрый выбор)
| Сценарий | Статус |
|----------|--------|
| Успешный GET | 200 OK |
| Ресурс создан (POST) | 201 Created |
| Успех без тела (DELETE) | 204 No Content |
| Ошибка в данных клиента | 400 Bad Request |
| Нет токена / невалидный | 401 Unauthorized |
| Токен есть, прав нет | 403 Forbidden |
| Ресурс не найден | 404 Not Found |
| Конфликт (дубликат и т.д.) | 409 Conflict |
| Ошибка валидации | 422 Unprocessable Entity |
| Превышен лимит запросов | 429 Too Many Requests |
| Ошибка на сервере | 500 Internal Server Error |

## Паттерны URL
```
# Коллекция
GET    /api/v1/users

# Элемент
GET    /api/v1/users/{id}

# Вложенный ресурс
GET    /api/v1/users/{id}/orders

# Фильтрация
GET    /api/v1/users?status=active&role=admin

# Пагинация (cursor)
GET    /api/v1/users?after=abc123&limit=20

# Поиск
GET    /api/v1/users?q=john

# Sparse fields
GET    /api/v1/users?fields=id,name,email

# Сортировка
GET    /api/v1/users?sort=-created_at,name
```

## GraphQL — базовые паттерны
```graphql
# Query
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    orders(first: 10) {
      edges {
        node { id total }
      }
      pageInfo { hasNextPage endCursor }
    }
  }
}

# Mutation
mutation CreateUser($input: CreateUserInput!) {
  createUser(input: $input) {
    user { id name }
    errors { field message }
  }
}
```

## Заголовки безопасности API
| Заголовок | Значение |
|-----------|----------|
| `Content-Type` | `application/json` |
| `Authorization` | `Bearer <token>` |
| `X-Request-ID` | UUID для трейсинга |
| `X-RateLimit-Limit` | Макс. запросов в окне |
| `X-RateLimit-Remaining` | Оставшиеся запросы |
| `Cache-Control` | `no-store` для приватных данных |

## Версионирование
```
# URL path (рекомендуется для публичных API)
/api/v1/users
/api/v2/users

# Header
Accept: application/vnd.myapi.v1+json

# Query param
/api/users?version=1
```

## Пагинация — форматы ответа
```json
// Cursor-based (рекомендуется)
{
  "data": [...],
  "pagination": {
    "hasNextPage": true,
    "endCursor": "eyJpZCI6MTAwfQ",
    "totalCount": 500
  }
}

// Offset-based
{
  "data": [...],
  "pagination": {
    "offset": 20,
    "limit": 10,
    "total": 500
  }
}
```
