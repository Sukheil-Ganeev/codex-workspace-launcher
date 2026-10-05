---
name: threads-spravochnik
description: "Production-ready руководство по Threads API для туристического бизнеса ОАЭ. auto_publish_text - публикация одним запросом. Триггеры - threads, треды, threads api."
version: 1.0.0
author: Claude Code Agent
created: 2026-02-05
---
# Threads API - Справочник для туристического бизнеса ОАЭ

## Обзор

**Threads** - текстовая социальная платформа Meta, запущенная в июле 2023 года. API открыт для разработчиков с июня 2024 года.

**Статус на 2026 год:**
- Полностью интегрирован с Instagram
- Поддержка автоматизированного постинга
- Доступна аналитика и метрики
- Растущая база пользователей (конкурент Twitter/X)

**Ключевое преимущество:** Возможность кросс-постинга с Instagram через единый OAuth-процесс.

---

## Основные возможности

### 1. Публикация контента

**Поддерживаемые типы:**
- Текстовые посты (до 500 символов)
- Изображения (соотношение сторон 9:16 до 1.91:1)
- Ссылки с превью
- Цитаты и репосты (через API ограничено)

**Формат публикации:**
- Одношаговая публикация текста (новинка 2025)
- Двухшаговая публикация медиа (создание + публикация)

### 2. Управление профилем

**Доступные операции:**
- Получение информации о профиле
- Обновление биографии
- Управление настройками приватности
- Связь с Instagram Business/Creator аккаунтом

### 3. Аналитика

**Метрики постов:**
- Просмотры (views)
- Лайки (likes)
- Комментарии (comments)
- Репосты (reposts)
- Цитирования (quotes)
- Вовлеченность (engagement rate)

**Метрики профиля:**
- Рост подписчиков
- Охват контента
- Активность аудитории

---

## OAuth 2.0 через Instagram

### Важно знать

Threads API использует **Instagram Graph API** для авторизации:

```
Instagram Business/Creator Account
    ↓
Facebook Page (обязательная привязка)
    ↓
Threads Profile
    ↓
API Access Token
```

### Требования к аккаунту

- ✅ Instagram Business или Creator аккаунт
- ✅ Привязка к Facebook Page
- ✅ Threads профиль, связанный с Instagram
- ❌ Personal Instagram аккаунты НЕ поддерживаются

### Разрешения (Permissions)

**Необходимые permissions:**
- `threads_basic` - базовый доступ к профилю
- `threads_content_publish` - публикация контента
- `threads_manage_insights` - доступ к аналитике
- `threads_manage_replies` - управление ответами

### Процесс получения токена

1. Создать Facebook App в Meta Developers
2. Добавить продукт "Threads"
3. Пройти App Review для необходимых permissions
4. Реализовать OAuth flow через Instagram
5. Получить access token (60 дней срок действия)
6. Настроить автообновление токена каждые 50-55 дней

---

## Новинка 2025: auto_publish_text

### До 2025 года (двухшаговый процесс)

```bash
# Шаг 1: Создать draft
curl -X POST "https://graph.threads.net/v1.0/THREADS_USER_ID/threads" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d "text=Amazing desert safari in Dubai! 🏜️"

# Ответ: {"id": "THREAD_ID"}

# Шаг 2: Опубликовать
curl -X POST "https://graph.threads.net/v1.0/THREAD_ID/publish" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

### С 2025 года (одношаговая публикация)

```bash
curl -X POST "https://graph.threads.net/v1.0/THREADS_USER_ID/threads" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Amazing desert safari in Dubai! 🏜️ #DubaiTourism",
    "auto_publish_text": true
  }'
```

**Преимущества:**
- Публикация одним запросом
- Экономия API квоты
- Упрощение кода
- Меньше обработки ошибок

**Ограничение:** Работает только для текстовых постов (без медиа).

---

## Quick Start: Первый пост за 10 минут

### Шаг 1: Получение credentials

1. Перейти: https://developers.facebook.com
2. Создать приложение (тип: Business)
3. Добавить продукт "Threads"
4. Записать App ID и App Secret

### Шаг 2: OAuth авторизация

```javascript
// Node.js пример
const authUrl = `https://api.instagram.com/oauth/authorize?client_id=${APP_ID}&redirect_uri=${REDIRECT_URI}&scope=threads_basic,threads_content_publish&response_type=code`;

// Открыть URL → пользователь авторизуется → получить code
// Обменять code на access token
```

### Шаг 3: Первый пост

```bash
# Замените переменные на свои значения
curl -X POST "https://graph.threads.net/v1.0/YOUR_THREADS_USER_ID/threads" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Мой первый пост через Threads API! 🚀",
    "auto_publish_text": true
  }'
```

**Результат:** Пост опубликован на вашем Threads профиле!

---

## Rate Limits (2026)

### Публикация контента

| Операция | Лимит | Период |
|----------|-------|--------|
| **Публикация постов** | 250 постов | 24 часа |
| **Создание draft** | Без ограничений | - |
| **Публикация draft** | 250 публикаций | 24 часа |

### API вызовы

**Зависят от Instagram App лимитов:**
- Базовый уровень: ~200 запросов/час на аккаунт
- Увеличивается с ростом репутации приложения

**Важно:** Threads API использует общую квоту с Instagram Graph API для того же приложения.

### Рекомендации

- Используйте планировщик для распределения постов
- Кэшируйте данные профиля (обновляйте раз в час)
- Обрабатывайте ошибки 429 (Too Many Requests) с exponential backoff
- Мониторьте оставшуюся квоту через заголовки ответов

---

## Применение для туризма ОАЭ

### Кейс 1: Кросс-постинг Instagram + Threads

**Стратегия:**
- **Instagram:** Визуальный контент (фото Burj Khalifa)
- **Threads:** Детальное описание тура с ценами

**Реализация:**
```javascript
// Один запрос → две платформы
async function crossPost(imageUrl, shortCaption, longDescription) {
  // Instagram
  await instagramAPI.createMediaContainer(imageUrl, shortCaption);
  await instagramAPI.publish(containerId);

  // Threads
  await threadsAPI.post({
    text: longDescription,
    auto_publish_text: true
  });
}
```

**Результат:** Максимальный охват с минимальными усилиями.

### Кейс 2: Истории клиентов

**Формат:**
```
"Только что вернулись с пустынного сафари! 🏜️

Что включено:
✅ Трансфер из отеля
✅ Катание на верблюдах
✅ Сэндбординг
✅ Ужин BBQ под звездами
✅ Шоу танца живота

Цена: $80/чел
Бронирование: @your_business

#DubaiTourism #DesertSafari #UAETravel"
```

**Преимущество:** Threads позволяет более длинные тексты (500 символов vs 2200 Instagram), что идеально для описаний услуг.

### Кейс 3: FAQ и советы

**Темы для Threads:**
- Лучшее время для посещения Дубая
- Что взять с собой в пустыню
- Дресс-код для мечети Шейха Зайда
- Как сэкономить на экскурсиях
- Транспорт в Дубае для туристов

**Стратегия:** Еженедельная серия постов с полезными советами → рост вовлеченности и подписчиков.

---

## Ссылки на дополнительную информацию

### Детальная документация (в references/)

1. **api-overview.md** - Полный список endpoints и методов
2. **posting-text-images.md** - Подробное руководство по публикации
3. **auto-publish-2025.md** - Новая функция auto_publish_text
4. **instagram-integration.md** - OAuth flow и token management
5. **cross-posting.md** - Стратегии кросс-постинга
6. **make-integration.md** - Автоматизация через Make.com

### Готовые шаблоны (в assets/templates/)

- **post-creator.js** - Helper для создания постов (Node.js)
- **cross-poster.js** - Кросс-постинг IG + Threads

### Полные примеры (в assets/examples/)

- **auto-posting/** - Система автопостинга с расписанием
- **cross-platform/** - Одновременная публикация на несколько платформ

### Скрипты (в scripts/)

- **setup-threads-api.sh** - Инструкции настройки API
- **post-text.sh** - Публикация текста через curl
- **post-image.sh** - Публикация изображения

---

## Быстрые команды

### Публикация текста

```bash
bash scripts/post-text.sh "Ваш текст" YOUR_USER_ID YOUR_TOKEN
```

### Публикация изображения

```bash
bash scripts/post-image.sh "https://example.com/image.jpg" "Caption" YOUR_USER_ID YOUR_TOKEN
```

### Получение аналитики

```bash
curl -X GET \
  "https://graph.threads.net/v1.0/THREAD_ID/insights?metric=views,likes" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Лучшие практики

### Контент

1. **Длина текста:** 300-400 символов оптимально (не максимум 500)
2. **Хештеги:** 3-5 релевантных хештегов
3. **Эмодзи:** 2-3 для визуального разнообразия
4. **Call-to-Action:** Четкий призыв к действию в конце

### Время публикации

**Для аудитории ОАЭ:**
- Утро: 9:00-11:00 (перед работой)
- День: 14:00-15:00 (обеденный перерыв)
- Вечер: 20:00-22:00 (после работы)

**Избегать:** 13:00-14:00 (пятничная молитва), ранние утренние часы (5:00-8:00)

### Частота публикаций

- Минимум: 3-5 постов/неделю
- Оптимально: 1-2 поста/день
- Максимум: 250 постов/день (технический лимит)

### Вовлеченность

- Отвечайте на комментарии в течение 1 часа
- Используйте вопросы в постах
- Создавайте серии постов (часть 1/3)
- Репостите отзывы клиентов (с разрешения)

---

## Troubleshooting

### Ошибка: "Invalid OAuth 2.0 Access Token"

**Причина:** Токен истек (срок 60 дней)

**Решение:**
```bash
# Обновить токен
curl -X GET "https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=YOUR_TOKEN"
```

### Ошибка: "Rate limit exceeded"

**Причина:** Превышен лимит 250 постов/24 часа

**Решение:**
- Подождать до сброса лимита (следующая полночь UTC)
- Использовать планировщик для распределения постов

### Ошибка: "User does not have a threads profile"

**Причина:** Instagram аккаунт не связан с Threads

**Решение:**
1. Создать Threads профиль через мобильное приложение
2. Использовать тот же Instagram аккаунт для авторизации

---

## Сравнение с конкурентами

| Функция | Threads | Instagram | Twitter/X |
|---------|---------|-----------|-----------|
| Лимит символов | 500 | 2200 (caption) | 280 (free) |
| API доступ | ✅ Открыт | ✅ Graph API | ⚠️ Платный |
| Автопостинг | ✅ Да | ✅ Да | ⚠️ Ограничен |
| OAuth через Instagram | ✅ Да | ✅ Да | ❌ Нет |
| Бесплатный API | ✅ Да | ✅ Да | ❌ От $100/мес |

**Вывод:** Threads - оптимальная платформа для текстового контента с бесплатным API и интеграцией с Instagram.

---

## Полезные ссылки

### Официальная документация
- [Threads API Postman Collection](https://www.postman.com/meta/threads/collection/dht3nzz/threads-api)
- [Meta Developers: Threads](https://developers.facebook.com/docs/threads)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)

### Инструменты автоматизации
- [Ayrshare](https://www.ayrshare.com/threads-api-integration-authorization-posting-analytics-with-ayrshare/)
- [Late.dev](https://getlate.dev/threads)
- [Make.com](https://www.make.com/en/integrations/instagram-business)

### Обучающие материалы
- [Developer's Guide to Threads API](https://getlate.dev/blog/threads-api)
- [Threads API Integration Tutorial](https://www.ayrshare.com/threads-api-integration-authorization-posting-analytics-with-ayrshare/)

---

## Дата создания и версия

**Создано:** 05 февраля 2026
**Версия:** 1.0.0
**Автор:** Claude Code Agent
**Обновления:** Следите за изменениями в experience/_index.md

**Актуальность данных:** Февраль 2026 (включая новинки 2025 года)
