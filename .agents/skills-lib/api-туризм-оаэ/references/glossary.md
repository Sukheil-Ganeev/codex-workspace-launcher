# Глоссарий API терминов

## A

**API (Application Programming Interface)**
Интерфейс для взаимодействия между программами. Позволяет одной программе использовать функции другой.

**API Key**
Уникальный идентификатор для аутентификации при вызове API. Обычно длинная строка символов.

**Access Token**
Токен доступа, подтверждающий права на использование API. Часто имеет срок действия.

**Authentication**
Процесс подтверждения личности (кто вы). Например, через API key или JWT.

**Authorization**
Процесс проверки прав доступа (что вам разрешено делать).

## B

**Bearer Token**
Тип токена, передаваемый в header `Authorization: Bearer <token>`. Часто используется с JWT.

**Body**
Тело HTTP запроса, содержащее данные (обычно JSON).

**Base URL**
Базовый адрес API, например `https://api.stripe.com/v1`.

## C

**Callback URL**
URL, на который сервис отправляет уведомления (webhooks).

**CORS (Cross-Origin Resource Sharing)**
Механизм безопасности браузера, ограничивающий запросы к другим доменам.

**cURL**
Командная утилита для отправки HTTP запросов.

**Client**
Программа, которая отправляет запросы к API (ваше приложение).

## E

**Endpoint**
Конкретный URL для доступа к ресурсу API. Например: `https://api.com/tours`.

**Error Code**
Код ошибки в ответе API. Например: `INVALID_API_KEY`.

## G

**GraphQL**
Язык запросов для API, позволяющий запрашивать только нужные поля.

## H

**Header**
Мета-информация HTTP запроса: авторизация, тип контента, и т.д.

**HTTP (HyperText Transfer Protocol)**
Протокол передачи данных в интернете. API используют HTTP/HTTPS.

**HTTPS**
Защищённая версия HTTP с шифрованием.

**HMAC (Hash-based Message Authentication Code)**
Алгоритм для проверки подлинности сообщения. Используется в webhook signatures.

## I

**Idempotency**
Свойство операции давать одинаковый результат при повторном выполнении. Важно для retry логики.

**Idempotency Key**
Уникальный ключ для предотвращения дублирования операций при retry.

## J

**JSON (JavaScript Object Notation)**
Формат данных для API. Пример: `{"name": "Tour", "price": 100}`

**JWT (JSON Web Token)**
Стандарт токенов для аутентификации. Содержит закодированную информацию о пользователе.

## M

**Mutation**
В GraphQL: операция изменения данных (создание, обновление, удаление).

## O

**OAuth 2.0**
Протокол авторизации для доступа к данным пользователя через третью сторону.

## P

**Pagination**
Разбиение больших списков на страницы. Параметры: `limit`, `offset` или `cursor`.

**Payload**
Данные, передаваемые в запросе или ответе API.

**POST**
HTTP метод для создания нового ресурса.

**PUT**
HTTP метод для полного обновления ресурса.

**PATCH**
HTTP метод для частичного обновления ресурса.

## Q

**Query**
В GraphQL: операция получения данных.

**Query Parameters**
Параметры в URL после `?`. Например: `?city=dubai&date=2026-03-15`

## R

**Rate Limit**
Ограничение количества запросов за период времени. Превышение возвращает 429.

**Request**
HTTP запрос к API.

**Response**
Ответ API на запрос.

**REST (Representational State Transfer)**
Архитектурный стиль API. Использует HTTP методы и URL для работы с ресурсами.

**Retry**
Повторная попытка запроса после ошибки.

## S

**SDK (Software Development Kit)**
Библиотека для работы с API на конкретном языке. Например: `stripe-python`.

**Server**
Программа, которая обрабатывает запросы API.

**Signature**
Криптографическая подпись для проверки подлинности webhook.

**Status Code**
Числовой код результата HTTP запроса (200, 404, 500 и т.д.).

## T

**Token**
Строка для аутентификации. Может быть API key, JWT, access token.

**Timeout**
Максимальное время ожидания ответа от API.

## U

**URL (Uniform Resource Locator)**
Адрес ресурса в интернете.

## W

**Webhook**
HTTP callback — сервис отправляет POST запрос на ваш URL при событии.

**WebSocket**
Протокол двусторонней связи в реальном времени.

## Примеры использования

```
Request: POST https://api.stripe.com/v1/charges
          │         │                    │
          │         │                    └── Endpoint
          │         └── Base URL
          └── HTTP Method

Headers:
  Authorization: Bearer sk_test_xxx  ← Bearer Token
  Content-Type: application/json     ← Тип данных

Body (Payload):
  {"amount": 1000, "currency": "aed"}  ← JSON

Response:
  Status: 201 Created  ← Status Code
  Body: {"id": "ch_xxx", "status": "succeeded"}  ← Payload
```
