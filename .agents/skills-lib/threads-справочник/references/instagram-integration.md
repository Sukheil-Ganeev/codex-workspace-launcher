# Instagram Integration - OAuth и Token Management

Подробное руководство по интеграции Threads API через Instagram Business/Creator аккаунт.

---

## Архитектура авторизации

Threads API использует **Instagram Graph API** для авторизации:

```
┌─────────────────────────────────────────────────────┐
│  Instagram Business/Creator Account                  │
│  (Требуется обязательно)                            │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  Facebook Page                                       │
│  (Привязана к Instagram)                            │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  Threads Profile                                     │
│  (Связан с Instagram)                               │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  Meta App + Permissions                              │
│  (Facebook Developers)                              │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  Access Token                                        │
│  (60 дней, нужно обновлять)                         │
└─────────────────────────────────────────────────────┘
```

---

## Требования к аккаунту

### Instagram

✅ **Поддерживаются:**
- Instagram Business аккаунт
- Instagram Creator аккаунт

❌ **НЕ поддерживаются:**
- Personal аккаунты
- Аккаунты без привязки к Facebook Page

### Проверка типа аккаунта

1. Открыть Instagram
2. Перейти в Settings → Account
3. Проверить тип: должно быть "Business" или "Creator"

### Конвертация в Business

1. Settings → Account → Switch to Professional Account
2. Выбрать категорию (Tourism, Travel Agency, Tour Guide)
3. Привязать к Facebook Page

---

## Создание Meta App

### Шаг 1: Регистрация в Meta Developers

1. Перейти: https://developers.facebook.com
2. Войти с Facebook аккаунтом
3. Create App → Business (тип приложения)
4. Заполнить:
   - App Display Name: "Dubai Tours API"
   - App Contact Email: your@email.com
5. Create App

### Шаг 2: Добавить продукт Threads

1. В Dashboard → Add Product
2. Найти "Threads" → Set Up
3. Threads API активирован

### Шаг 3: Записать credentials

```
App ID: 1234567890123456
App Secret: abcdef1234567890abcdef1234567890
```

**Важно:** App Secret - конфиденциальная информация. Хранить в .env файле.

---

## OAuth 2.0 Flow

### Метод 1: Authorization Code (рекомендуется)

#### Шаг 1: Получить Authorization Code

```
https://api.instagram.com/oauth/authorize
  ?client_id=YOUR_APP_ID
  &redirect_uri=YOUR_REDIRECT_URI
  &scope=threads_basic,threads_content_publish,threads_manage_insights
  &response_type=code
```

**Параметры:**
- `client_id` - App ID из Meta Developers
- `redirect_uri` - URL для callback (должен быть зарегистрирован в App)
- `scope` - разрешения (см. ниже)
- `response_type` - `code`

**Регистрация redirect_uri:**
1. App Dashboard → Threads → Settings
2. Valid OAuth Redirect URIs → Add: `https://yourdomain.com/callback`
3. Save Changes

**Результат:**
```
https://yourdomain.com/callback?code=AUTHORIZATION_CODE#_
```

---

#### Шаг 2: Обменять code на Short-Lived Token

```bash
curl -X POST https://api.instagram.com/oauth/access_token \
  -F client_id=YOUR_APP_ID \
  -F client_secret=YOUR_APP_SECRET \
  -F grant_type=authorization_code \
  -F redirect_uri=YOUR_REDIRECT_URI \
  -F code=AUTHORIZATION_CODE
```

**Ответ:**
```json
{
  "access_token": "IGQWRNa1...",
  "user_id": 17841400123456789
}
```

**Срок действия:** ~1 час

---

#### Шаг 3: Обменять на Long-Lived Token (60 дней)

```bash
curl -X GET "https://graph.instagram.com/access_token \
  ?grant_type=ig_exchange_token \
  &client_secret=YOUR_APP_SECRET \
  &access_token=SHORT_LIVED_TOKEN"
```

**Ответ:**
```json
{
  "access_token": "IGQWRPZD3...",
  "token_type": "bearer",
  "expires_in": 5183944
}
```

**Срок действия:** 60 дней (без использования) или 90 дней (с регулярным использованием)

---

### Пример (Node.js) - Полный flow

```javascript
const express = require('express');
const axios = require('axios');

const app = express();
const APP_ID = 'YOUR_APP_ID';
const APP_SECRET = 'YOUR_APP_SECRET';
const REDIRECT_URI = 'http://localhost:3000/callback';

// Шаг 1: Перенаправить пользователя на авторизацию
app.get('/auth', (req, res) => {
  const authUrl = `https://api.instagram.com/oauth/authorize?client_id=${APP_ID}&redirect_uri=${REDIRECT_URI}&scope=threads_basic,threads_content_publish,threads_manage_insights&response_type=code`;
  res.redirect(authUrl);
});

// Шаг 2: Получить код и обменять на токен
app.get('/callback', async (req, res) => {
  const { code } = req.query;

  try {
    // Получить short-lived token
    const shortTokenResponse = await axios.post(
      'https://api.instagram.com/oauth/access_token',
      new URLSearchParams({
        client_id: APP_ID,
        client_secret: APP_SECRET,
        grant_type: 'authorization_code',
        redirect_uri: REDIRECT_URI,
        code: code
      })
    );

    const shortToken = shortTokenResponse.data.access_token;

    // Обменять на long-lived token
    const longTokenResponse = await axios.get(
      `https://graph.instagram.com/access_token?grant_type=ig_exchange_token&client_secret=${APP_SECRET}&access_token=${shortToken}`
    );

    const longToken = longTokenResponse.data.access_token;
    const expiresIn = longTokenResponse.data.expires_in;

    res.json({
      success: true,
      access_token: longToken,
      expires_in: expiresIn,
      expires_in_days: Math.floor(expiresIn / 86400)
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.response?.data || error.message
    });
  }
});

app.listen(3000, () => {
  console.log('OAuth server running on http://localhost:3000');
  console.log('Start authorization: http://localhost:3000/auth');
});
```

---

## Разрешения (Permissions/Scopes)

### Базовые разрешения

| Permission | Описание | Требует App Review |
|-----------|----------|-------------------|
| `threads_basic` | Базовый доступ к профилю | Да |
| `threads_content_publish` | Публикация контента | Да |
| `threads_manage_insights` | Аналитика и метрики | Да |
| `threads_manage_replies` | Управление ответами | Да |
| `threads_read_replies` | Чтение ответов | Да |

**App Review:** Обязателен для production использования. Без review доступны только тестовые пользователи (до 5 аккаунтов).

---

## App Review Process

### Подготовка

1. Завершить интеграцию (рабочий код)
2. Создать демо-видео (screencast)
3. Написать детальное описание use case
4. Подготовить privacy policy URL

### Подача заявки

1. App Dashboard → App Review → Permissions and Features
2. Выбрать нужные permissions
3. Заполнить форму:
   - **Use Case:** "Automated tourism content publishing for Dubai tours"
   - **Detailed Description:** Опишите как используете API
   - **Screencast:** Видео демонстрации функционала (2-3 минуты)
   - **Privacy Policy:** URL вашей политики конфиденциальности
4. Submit for Review

### Время рассмотрения

- Стандартно: 3-7 рабочих дней
- Может быть запрошена дополнительная информация
- После одобрения - полный доступ к API

---

## Token Management

### Обновление Long-Lived Token

**Важно:** Токены действуют 60 дней. Обновляйте каждые 50-55 дней!

```bash
curl -X GET "https://graph.instagram.com/refresh_access_token \
  ?grant_type=ig_refresh_token \
  &access_token=LONG_LIVED_TOKEN"
```

**Ответ:**
```json
{
  "access_token": "NEW_LONG_LIVED_TOKEN",
  "token_type": "bearer",
  "expires_in": 5183944
}
```

### Автоматическое обновление (Node.js)

```javascript
const schedule = require('node-schedule');
const fs = require('fs').promises;

// Обновлять токен каждые 50 дней
const job = schedule.scheduleJob('0 0 */50 * *', async function() {
  try {
    // Прочитать текущий токен
    const currentToken = await fs.readFile('.env.token', 'utf8');

    // Обновить токен
    const response = await axios.get(
      `https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=${currentToken.trim()}`
    );

    const newToken = response.data.access_token;

    // Сохранить новый токен
    await fs.writeFile('.env.token', newToken);

    console.log('[Token Manager] Token refreshed successfully');
    console.log(`[Token Manager] New expiration: ${response.data.expires_in / 86400} days`);

  } catch (error) {
    console.error('[Token Manager] Failed to refresh token:', error.message);
    // Отправить уведомление администратору
  }
});

console.log('Token refresh scheduler started (every 50 days)');
```

### Проверка срока действия токена

```javascript
async function checkTokenExpiration(token) {
  try {
    const response = await axios.get(
      `https://graph.instagram.com/me?fields=id,username&access_token=${token}`
    );

    // Если токен валиден
    return {
      valid: true,
      user: response.data
    };

  } catch (error) {
    // Если токен истек или невалиден
    if (error.response?.data?.error?.code === 190) {
      return {
        valid: false,
        error: 'Token expired or invalid'
      };
    }

    throw error;
  }
}
```

---

## Best Practices

### 1. Безопасное хранение токенов

**НЕ делайте так:**
```javascript
// ❌ Хардкод токена в коде
const ACCESS_TOKEN = 'IGQWRPZD3...';
```

**Делайте так:**
```javascript
// ✅ Переменные окружения
require('dotenv').config();
const ACCESS_TOKEN = process.env.THREADS_ACCESS_TOKEN;
```

**.env файл:**
```
THREADS_ACCESS_TOKEN=IGQWRPZD3...
THREADS_USER_ID=17841400123456789
```

**.gitignore:**
```
.env
.env.token
```

---

### 2. Мониторинг токенов

```javascript
// Проверять токен перед каждым API запросом
async function publishWithTokenCheck(text) {
  // Проверка токена
  const tokenStatus = await checkTokenExpiration(ACCESS_TOKEN);

  if (!tokenStatus.valid) {
    console.error('Token invalid - please refresh');
    // Автоматическое обновление или уведомление
    throw new Error('Invalid access token');
  }

  // Публикация
  return await publishTextPost(text);
}
```

---

### 3. Обработка ошибок авторизации

```javascript
async function apiRequest(endpoint, data) {
  try {
    return await axios.post(endpoint, data, {
      headers: { 'Authorization': `Bearer ${ACCESS_TOKEN}` }
    });
  } catch (error) {
    const errorCode = error.response?.data?.error?.code;

    switch (errorCode) {
      case 190: // Invalid token
        console.error('Token expired - needs refresh');
        // Trigger token refresh
        break;

      case 102: // Session expired
        console.error('Session expired - re-authenticate');
        // Redirect to OAuth flow
        break;

      case 200: // Permission denied
        console.error('Permission denied - check App Review status');
        break;

      default:
        console.error('API error:', error.response?.data);
    }

    throw error;
  }
}
```

---

## Получение Threads User ID

После получения access token, нужен Threads User ID для API запросов:

```bash
curl -X GET \
  "https://graph.instagram.com/me?fields=threads_profile&access_token=YOUR_ACCESS_TOKEN"
```

**Ответ:**
```json
{
  "id": "17841400123456789",
  "threads_profile": {
    "id": "17841400123456789"
  }
}
```

**Node.js:**
```javascript
async function getThreadsUserId(accessToken) {
  const response = await axios.get(
    `https://graph.instagram.com/me?fields=threads_profile&access_token=${accessToken}`
  );
  return response.data.threads_profile.id;
}
```

---

## Troubleshooting

### Ошибка: "The access token does not belong to application"

**Причина:** Токен был получен для другого приложения

**Решение:**
1. Использовать правильный App ID и App Secret
2. Повторить OAuth flow для текущего приложения

---

### Ошибка: "User does not have a threads profile"

**Причина:** Instagram аккаунт не связан с Threads

**Решение:**
1. Скачать Threads app (iOS/Android)
2. Войти с тем же Instagram аккаунтом
3. Создать Threads профиль

---

### Ошибка: "This endpoint requires a valid threads_basic permission"

**Причина:** App не прошел App Review

**Решение:**
1. Добавить тестовых пользователей в App Dashboard
2. Или подать App Review заявку для production

---

## Полезные ссылки

- [Instagram Graph API - Getting Started](https://developers.facebook.com/docs/instagram-api/getting-started)
- [Threads API Authentication](https://developers.facebook.com/docs/threads/get-started)
- [App Review Guidelines](https://developers.facebook.com/docs/app-review)
- [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)

---

**Обновлено:** 05 февраля 2026
**Версия:** 1.0.0
