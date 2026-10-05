---
name: vk-video-spravochnik
description: "Справочник по VK Video API и альтернативам для туристического бизнеса ОАЭ. VK Video API ограничена, альтернативы - api.video, Cloudflare Stream, Mux, YouTube."
version: "1.0"
author: "Claude Code Agent"
---
# VK Video API: Справочник и альтернативы

## Содержание

1. [Обзор VK Video API](#обзор-vk-video-api)
2. [Доступные методы](#доступные-методы)
3. [Quick Start: Загрузка первого видео](#quick-start-загрузка-первого-видео)
4. [Альтернативы VK Video](#альтернативы-vk-video)
5. [Кейс для туризма ОАЭ](#кейс-для-туризма-оаэ)
6. [Ссылки на references](#ссылки-на-references)

---

## Обзор VK Video API

### Статус документации (2026)

**ВАЖНО:** Официальная документация VK Video API **ограничена** в открытом доступе.

**Что доступно:**

- ✅ Базовая загрузка видео (метод `video.save`)
- ✅ Получение информации о видео (`video.get`)
- ✅ Поиск видео (`video.search`)
- ❌ Live streaming - частично документирован
- ❌ Расширенные возможности - требуют партнёрства с VK

**Рекомендация:** Для серьёзного видеохостинга туристического контента рассмотрите **альтернативные платформы** (см. раздел ниже).

### Почему VK Video API ограничена

**Причины:**

1. **Фокус на VK Play Live** - VK перенёс акцент на стриминговую платформу
2. **Партнёрская модель** - расширенный API доступен только партнёрам
3. **Приоритет контента** - VK продвигает лицензированный контент

**Для туризма это означает:**

- Базовые возможности загрузки работают
- Сложные функции (live, analytics, embed customization) ограничены
- Лучше использовать специализированные видеохостинги

---

## Доступные методы

### video.save - Загрузка видео

**Описание:** Получение upload URL для загрузки видеофайла

**Параметры:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `name` | string | Название видео |
| `description` | string | Описание |
| `group_id` | int | ID сообщества (положительный!) |
| `wallpost` | int | 1 - опубликовать на стене сразу |

**Процесс (2 шага):**

1. `video.save` → получить `upload_url` и `video_id`
2. POST файл на `upload_url`
3. Видео автоматически сохраняется и обрабатывается

**Подробности:** см. `references/upload-process.md`

### video.get - Информация о видео

**Описание:** Получение данных о загруженном видео

**Параметры:**

- `videos` - список видео в формате `{owner_id}_{video_id}`
- `count` - количество видео

**Пример:**

```python
video_info = vk.video.get(
    videos="-12345678_456789012",
    count=1
)

print(video_info['items'][0])
```

**Важные поля:**

- `processing` - 1 = обрабатывается, 0 = готово
- `player` - URL плеера (доступен после обработки)
- `views` - количество просмотров
- `duration` - длительность (секунды)

### video.search - Поиск видео

**Описание:** Поиск видео в VK

**Параметры:**

- `q` - поисковый запрос
- `sort` - сортировка (0 = по релевантности, 1 = по длительности, 2 = по дате)
- `count` - количество результатов (макс 200)

**Пример:**

```python
results = vk.video.search(
    q='Dubai tourism',
    sort=2,  # по дате
    count=20
)

for video in results['items']:
    print(f"{video['title']} - {video['views']} просмотров")
```

---

## Quick Start: Загрузка первого видео

### Шаг 1: Получить upload URL (1 мин)

```python
import vk_api

vk_session = vk_api.VkApi(token='YOUR_COMMUNITY_TOKEN')
vk = vk_session.get_api()

# Получить upload URL
video_data = vk.video.save(
    name='Desert Safari Dubai - Promo',
    description='Экскурсия по пустыне Дубая',
    group_id=12345678  # Положительный ID!
)

print(f"Upload URL: {video_data['upload_url']}")
print(f"Video ID: {video_data['video_id']}")
```

### Шаг 2: Загрузить файл (5 мин)

```python
import requests

upload_url = video_data['upload_url']

# Загрузить видео
with open('desert_safari.mp4', 'rb') as video_file:
    files = {'video_file': video_file}
    response = requests.post(upload_url, files=files)
    print(response.json())
```

**Ответ:**

```json
{
  "size": 15728640,
  "video_id": 456789012
}
```

### Шаг 3: Ждать обработки (5-10 мин)

```python
import time

video_id = video_data['video_id']
owner_id = video_data['owner_id']

# Ждать обработки
print("Ждём обработки видео...")
time.sleep(60)  # Минимум 1 минута

# Проверить статус
video_info = vk.video.get(
    videos=f"{owner_id}_{video_id}",
    count=1
)

if video_info['items'][0].get('processing') == 0:
    print("✅ Видео готово!")
    print(f"Плеер: {video_info['items'][0]['player']}")
else:
    print("⏳ Ещё обрабатывается...")
```

### Шаг 4: Опубликовать на стене (1 мин)

```python
# Attachment string
video_attachment = f"video{owner_id}_{video_id}"

# Публикация
vk.wall.post(
    owner_id=-12345678,  # Отрицательный для групп!
    from_group=1,
    message="🏜️ Desert Safari Dubai - смотрите наше промо-видео!",
    attachments=video_attachment
)

print("✅ Видео опубликовано на стене!")
```

**Готово!** Полный процесс занял ~10-15 минут (включая обработку видео).

---

## Альтернативы VK Video

### Сравнительная таблица

| Платформа | Цена (2026) | API Quality | Live Streaming | Analytics | Recommendation |
|-----------|-------------|-------------|----------------|-----------|----------------|
| **api.video** | €10/месяц (250GB) | ⭐⭐⭐⭐⭐ Excellent | ✅ Да | ✅ Да | ⭐ Best for tourism |
| **Cloudflare Stream** | $1/1000 мин хранение | ⭐⭐⭐⭐⭐ Excellent | ✅ Да | ✅ Да | ⭐ Scalable |
| **Mux** | $0.05/мин хранение | ⭐⭐⭐⭐⭐ Developer-friendly | ✅ Да | ✅ Да | ⭐ Professional |
| **YouTube** | Бесплатно | ⭐⭐⭐⭐ Good (квоты) | ✅ Да | ✅ Да | ⭐ Free option |
| **VK Video** | Бесплатно | ⭐⭐ Limited docs | ❌ Частично | ❌ Базовая | ⚠️ Limited |

### api.video (Рекомендуется для туризма)

**Преимущества:**

- ✅ **Простой API** - отличная документация
- ✅ **Player customization** - брендирование плеера
- ✅ **Live streaming** - прямые трансляции
- ✅ **Analytics** - подробная статистика
- ✅ **Adaptive bitrate** - автоматическая оптимизация качества

**Цены (2026):**

- **Sandbox:** Бесплатно (тестирование)
- **Starter:** €10/месяц (250 GB хранение, 1 TB доставка)
- **Growth:** €50/месяц (1 TB хранение, 5 TB доставка)

**Пример API:**

```python
import requests

API_KEY = 'your_api_video_key'

# Загрузка видео
response = requests.post(
    'https://ws.api.video/videos',
    headers={'Authorization': f'Bearer {API_KEY}'},
    json={
        'title': 'Desert Safari Dubai',
        'description': 'Amazing tour experience',
        'public': True
    }
)

video = response.json()
print(f"Video ID: {video['videoId']}")
print(f"Player URL: {video['assets']['player']}")
```

**Документация:** https://docs.api.video/

### Cloudflare Stream

**Преимущества:**

- ✅ **Cloudflare CDN** - глобальная доставка
- ✅ **Pay-as-you-go** - платите только за использование
- ✅ **No egress fees** - нет платы за трафик из Cloudflare
- ✅ **Live streaming** - поддержка WebRTC

**Цены (2026):**

- **Хранение:** $1 за 1,000 минут/месяц
- **Доставка:** $1 за 1,000 минут просмотра

**Пример:** 100 видео по 5 минут = 500 минут хранение = $0.50/месяц

**Документация:** https://developers.cloudflare.com/stream/

### Mux

**Преимущества:**

- ✅ **Developer-first API** - лучший DX
- ✅ **Video analytics** - детальная аналитика
- ✅ **Thumbnails API** - автоматические превью
- ✅ **Multiple quality levels** - adaptive bitrate

**Цены (2026):**

- **Видео:** $0.05/минута хранение, $0.005/минута доставка
- **Live:** $3/час трансляции

**Пример:** 1000 минут хранения + 10,000 минут просмотра = $50 + $50 = $100/месяц

**Документация:** https://docs.mux.com/

### YouTube (Бесплатная альтернатива)

**Преимущества:**

- ✅ **Бесплатно** - нет платы за хостинг
- ✅ **Огромная аудитория** - SEO и органический трафик
- ✅ **YouTube Data API v3** - управление через API
- ✅ **Shorts** - короткие вертикальные видео

**Недостатки:**

- ❌ **Квоты** - 10,000 единиц/день (макс 6 загрузок)
- ❌ **Реклама** - YouTube может показывать рекламу на ваших видео
- ❌ **Ограничения брендирования** - плеер YouTube (не кастомизируется)

**Применение для туризма:**

- Публичные промо-ролики
- YouTube Shorts для виральности
- SEO (поиск "Dubai tours" → ваши видео)

**Подробнее:** см. скилл `youtube-справочник`

---

## Кейс для туризма ОАЭ

### Задача: Видеохостинг для 50+ промо-роликов экскурсий

**Требования:**

- Загрузка 50 видео (по 2-5 минут каждое)
- Встроенный плеер на сайте
- Аналитика просмотров
- Бюджет: до $50/месяц

### Сравнение решений

#### Вариант 1: api.video (€10/месяц)

**За:**

- ✅ Фиксированная цена (предсказуемо)
- ✅ 250 GB хранение (достаточно для 50+ видео)
- ✅ Отличный API и аналитика

**Против:**

- ❌ Платно (но недорого)

**Итого:** ⭐ **Рекомендуется** для профессионального использования

#### Вариант 2: YouTube (бесплатно)

**За:**

- ✅ Полностью бесплатно
- ✅ SEO и органический трафик
- ✅ Встроенный плеер (iframe)

**Против:**

- ❌ Реклама на видео
- ❌ Ограничения квот (6 загрузок/день)
- ❌ Нет брендирования плеера

**Итого:** ⭐ **Хорошо** для стартапов с нулевым бюджетом

#### Вариант 3: VK Video (бесплатно)

**За:**

- ✅ Бесплатно
- ✅ Интеграция с VK-сообществом

**Против:**

- ❌ Ограниченный API
- ❌ Нет продвинутой аналитики
- ❌ Только русскоязычная аудитория

**Итого:** ⚠️ **Подходит** только для VK-контента (не основной хостинг)

### Рекомендация

**Стратегия:**

1. **Основной хостинг:** api.video (€10/месяц) → встроить плеер на сайт
2. **YouTube:** загружать те же видео для SEO и виральности
3. **VK Video:** дублировать в VK-сообщество для русскоязычной аудитории

**Результат:**

- Профессиональный плеер на сайте (api.video)
- Органический трафик с YouTube
- Охват русскоязычных туристов в VK

**Бюджет:** €10/месяц (только api.video, остальное бесплатно)

---

## Ссылки на references

Подробные руководства в директории `references/`:

1. **[video-api-overview.md](references/video-api-overview.md)** - Доступные методы (video.save, video.get, video.search), limitations 2026

2. **[upload-process.md](references/upload-process.md)** - Процесс загрузки (получение upload URL, загрузка файла, сохранение), примеры curl/Python

3. **[live-streaming.md](references/live-streaming.md)** - Прямые трансляции VK Видео (если доступно в 2026), настройка, limitations

4. **[analytics.md](references/analytics.md)** - Статистика просмотров (video.getStats), метрики (views, reach, engagement)

5. **[alternatives.md](references/alternatives.md)** - Подробное сравнение альтернатив (api.video, Cloudflare Stream, Mux, YouTube) с pricing и примерами

---

## Дополнительные ресурсы

### Примеры кода

- **`assets/examples/video-uploader/`** - Python script для загрузки видео в VK (vk_api library, multi-step upload)

### Скрипты

- **`scripts/upload-video.py`** - Загрузка видео в VK (Python)
- **`scripts/get-video-stats.sh`** - Статистика просмотров (curl, video.getStats)

---

## Контакты и поддержка

**Официальная документация:**
- VK Video API: https://dev.vk.com/ru/method/video
- api.video: https://docs.api.video/
- Cloudflare Stream: https://developers.cloudflare.com/stream/
- Mux: https://docs.mux.com/

**Версия скилла:** 1.0
**Дата обновления:** 2026-02-05
**Автор:** Claude Code Agent для Сухейль (Туризм в Дубае/ОАЭ)

---

*Этот справочник создан на основе актуальных данных VK Video API (2026) из SOCIAL_MEDIA_API_2026_AUTOMATION_GUIDE.md*
