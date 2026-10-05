---
name: youtube-spravochnik
description: "Production-ready руководство по YouTube Data API v3 для туристического бизнеса ОАЭ. Квоты 10000 units/day, YouTube Shorts поддержка. Триггеры - youtube, ютуб, youtube api, shorts."
version: 1.0
author: Claude Code Agent
date: 2026-02-05
---
# YouTube Data API v3 — Справочник для туристического бизнеса ОАЭ

## Обзор

YouTube Data API v3 — это официальный API от Google для управления YouTube каналами, загрузки видео, управления плейлистами, получения аналитики и многого другого.

### Что можно делать

- ✅ Загрузка видео (до 256 GB, resumable upload)
- ✅ Автоматическое определение YouTube Shorts (<60 секунд, вертикальный формат)
- ✅ Управление плейлистами (создание, редактирование, удаление)
- ✅ Настройка прямых трансляций (live streaming)
- ✅ Получение аналитики через YouTube Analytics API
- ✅ Управление комментариями (чтение, ответы, модерация)
- ✅ Поиск видео (search API)

### Что нельзя делать

- ❌ Обход квот (10,000 units/day — жесткий лимит)
- ❌ Автоматические лайки/подписки без пользовательского действия
- ❌ Массовая загрузка одинакового контента (spam)

---

## Квоты 2026

### Дефолтная квота: 10,000 units/день

**Важно:** Квоты сбрасываются в **полночь по Pacific Time** (PST/PDT).

### Стоимость операций (в единицах квоты)

| Операция | Метод | Стоимость | Примечание |
|----------|-------|-----------|------------|
| **Загрузка видео** | `videos.insert` | 1600 | Макс. 6 видео/день |
| **Обновление видео** | `videos.update` | 50 | Метаданные |
| **Список видео** | `videos.list` | 1 | Получение инфо |
| **Поиск** | `search.list` | 100 | Дорогой запрос! |
| **Комментарии (чтение)** | `comments.list` | 1 | |
| **Комментарии (запись)** | `comments.insert` | 50 | |
| **Плейлисты (чтение)** | `playlists.list` | 1 | |
| **Плейлисты (запись)** | `playlists.insert/update/delete` | 50 | |
| **Прямая трансляция** | `liveBroadcasts.insert` | 50 | |

### Пример расчета квоты

**Сценарий:** Загрузка 1 видео + проверка + добавление в плейлист

```
videos.insert    = 1600 units  (загрузка)
videos.list      = 1 unit      (проверка)
playlists.insert = 50 units    (добавление в плейлист)
-------------------------
ИТОГО:          = 1651 units
```

**Остаток:** 10,000 - 1,651 = 8,349 units (можно еще 5 видео загрузить)

### Увеличение квоты

Если нужно больше 10,000 units/день:

1. Перейдите: https://support.google.com/youtube/contact/yt_api_form
2. Заполните форму обоснования
3. Ожидайте рассмотрения (может занять 2-4 недели)

**Альтернатива:** Используйте несколько Google Cloud проектов (каждый имеет свою квоту 10,000).

---

## YouTube Shorts (2026)

### Автоматическое определение

YouTube **автоматически** определяет Shorts по критериям:

1. **Длительность:** < 60 секунд
2. **Формат:** Вертикальный (aspect ratio 9:16 или близкий)

**Не нужно** специального API endpoint — используйте обычный `videos.insert`.

### Спецификации для Shorts

| Параметр | Требование |
|----------|------------|
| **Длительность** | < 60 секунд (58-59 сек оптимально) |
| **Разрешение** | 1080x1920 (рекомендуется) |
| **Aspect Ratio** | 9:16 (вертикальный) |
| **Формат** | MP4, MOV |
| **Кодек** | H.264, H.265 |
| **Аудио** | AAC, 128 kbps+ |

### Монетизация Shorts (2026)

**RPM (Revenue Per Mille):** $0.01 - $0.07 за 1,000 просмотров

**Расчет:**
- При RPM $0.03: нужно **3.3M просмотров** для $100
- При RPM $0.05: нужно **2M просмотров** для $100

**Вывод:** Shorts — для охвата и роста канала, не для прямой монетизации.

**YouTube Partner Program:**
- Требования: 1,000 подписчиков + 4,000 часов просмотра (или 10M просмотров Shorts за 90 дней)

---

## Quick Start: Загрузка первого видео за 20 минут

### Шаг 1: Создание Google Cloud проекта

1. Перейдите: https://console.cloud.google.com/
2. Создайте новый проект: **"My Tourism YouTube API"**
3. Активируйте **YouTube Data API v3**:
   - APIs & Services → Enable APIs and Services
   - Найдите "YouTube Data API v3" → Enable

### Шаг 2: Создание OAuth 2.0 credentials

1. APIs & Services → **Credentials**
2. **Create Credentials** → **OAuth client ID**
3. Выберите тип: **Desktop app** (для тестирования) или **Web application** (для production)
4. Скачайте `client_secret.json`

### Шаг 3: Авторизация и получение токена

**Python пример** (с Google API Python Client):

```python
import google_auth_oauthlib.flow

# OAuth flow
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/youtube.upload']
)

credentials = flow.run_local_server(port=0)
# Сохраните credentials для последующего использования
```

### Шаг 4: Загрузка видео

```python
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Создаем YouTube API клиент
youtube = build('youtube', 'v3', credentials=credentials)

# Метаданные видео
body = {
    'snippet': {
        'title': 'Dubai Desert Safari - Amazing Experience',
        'description': 'Experience the ultimate desert adventure in Dubai!',
        'tags': ['Dubai', 'Desert Safari', 'UAE', 'Tourism'],
        'categoryId': '19'  # Travel & Events
    },
    'status': {
        'privacyStatus': 'public'  # public, private, unlisted
    }
}

# Загрузка файла
media = MediaFileUpload('desert_safari.mp4', chunksize=-1, resumable=True)

request = youtube.videos().insert(
    part='snippet,status',
    body=body,
    media_body=media
)

response = request.execute()
print(f"Видео загружено: https://youtube.com/watch?v={response['id']}")
```

**Готово!** Ваше первое видео на YouTube через API.

---

## Архитектура API

### Базовый URL

```
https://www.googleapis.com/youtube/v3/
```

### Аутентификация

**Два метода:**

1. **API Key** — для публичных операций (поиск, просмотр):
   ```
   GET https://www.googleapis.com/youtube/v3/videos?id=VIDEO_ID&key=YOUR_API_KEY
   ```

2. **OAuth 2.0** — для операций с аккаунтом (загрузка, удаление):
   ```
   Authorization: Bearer ACCESS_TOKEN
   ```

### Основные endpoints

- `POST /videos` — загрузка видео
- `GET /videos` — информация о видео
- `PUT /videos` — обновление метаданных
- `DELETE /videos` — удаление видео
- `GET /search` — поиск видео
- `POST /playlists` — создание плейлиста
- `POST /liveBroadcasts` — настройка прямой трансляции
- `GET /channels` — информация о канале

---

## Resumable Upload (для больших файлов)

### Зачем нужен

Для файлов **> 5 MB** используйте **resumable upload protocol**:
- Возможность возобновить загрузку при обрыве соединения
- Загрузка частями (chunks)
- Прогресс-бар для пользователя

### Python пример

```python
from googleapiclient.http import MediaFileUpload

# Resumable upload (chunks по 10 MB)
media = MediaFileUpload(
    'large_video.mp4',
    chunksize=10*1024*1024,  # 10 MB
    resumable=True
)

request = youtube.videos().insert(
    part='snippet,status',
    body=body,
    media_body=media
)

response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f"Загружено {int(status.progress() * 100)}%")

print(f"Загрузка завершена: {response['id']}")
```

---

## Кейсы для туризма ОАЭ

### Кейс 1: Автозагрузка туристических видео

**Сценарий:** Каждый день загружать новое видео с туром.

**Стек:**
- Python + YouTube Data API v3
- Cron для планирования
- База данных с видео (JSON/MongoDB)

**Workflow:**
```
Cron (ежедневно 10:00) → Выбрать видео дня из БД
                       → Сгенерировать title/description (YandexGPT)
                       → Загрузить через YouTube API
                       → Добавить в плейлист "Tours 2026"
                       → Лог результата
```

Пример: `assets/examples/tour-videos-uploader/`

**Результат:**
- Регулярность: 365 видео/год
- Оптимизация квот: 1,651 units/день (65% остается для других операций)

### Кейс 2: YouTube Shorts для виральности

**Сценарий:** Создание коротких вертикальных видео (<60 сек) из длинных туров.

**Стек:**
- FFmpeg для нарезки видео
- Python для автоматизации
- YouTube API для загрузки

**Workflow:**
```
Длинное видео (10 мин) → FFmpeg (нарезка на 30-сек клипы)
                        → Вертикальный формат (1080x1920)
                        → Загрузка через API (автоопределение Shorts)
```

Пример: `assets/examples/shorts-generator/`

**Эффект:**
- Охват: +300% (Shorts алгоритм более виральный)
- Затраты квот: 1,600 units/Short (6 Shorts/день макс.)
- Стоимость лида: $0.20-0.50 (очень низкая)

### Кейс 3: Прямые трансляции (Live Streaming)

**Сценарий:** Прямая трансляция с экскурсии в реальном времени.

**Стек:**
- OBS Studio для стриминга
- YouTube Live API для настройки
- RTMP сервер

**Применение:**
- "Live сафари по пустыне"
- "Прямой эфир с яхты в Dubai Marina"
- "Виртуальный тур по Burj Khalifa"

Пример: `assets/examples/live-stream-setup/`

---

## Структура справочника

### References (подробные гайды)

1. **data-api-v3.md** — OAuth 2.0, API key, endpoints, quota costs (таблица)
2. **upload-videos.md** — Процесс загрузки, snippet/status, resumable upload, примеры
3. **shorts-optimization.md** — YouTube Shorts best practices, RPM optimization, vertical video
4. **live-streaming.md** — Настройка прямых трансляций (liveBroadcasts, liveStreams)
5. **analytics-api.md** — YouTube Analytics API, метрики (views, watch time, RPM), отчёты
6. **monetization.md** — YouTube Partner Program, AdSense, Shorts Fund, требования
7. **playlists-management.md** — Создание и управление плейлистами (API examples)
8. **make-integration.md** — Автоматизация через Make.com (auto-upload, scheduling)

### Assets

**Templates (helper-скрипты):**
- `video-uploader.py` — Python script с resumable upload
- `shorts-uploader.js` — Node.js для Shorts (vertical video detection)
- `video-metadata-template.json` — Шаблон title/description/tags для туров ОАЭ
- `thumbnail-generator-prompt.txt` — YandexGPT prompt для thumbnail идей

**Examples (полные рабочие примеры):**
- `tour-videos-uploader/` — Автозагрузка видео туров (Python, resumable, README)
- `shorts-generator/` — Создание Shorts из длинных видео (Python, ffmpeg)
- `analytics-dashboard/` — Dashboard с метриками (Node.js, YouTube Analytics API)
- `live-stream-setup/` — Настройка прямых трансляций (Python, OBS integration)

**Scripts (быстрые команды):**
- `setup-youtube-api.sh` — Настройка OAuth credentials (инструкции)
- `upload-video.py` — Загрузка видео (Python)
- `upload-short.py` — Загрузка Short (Python, <60s check)
- `get-analytics.sh` — Получение статистики (curl, Analytics API)

---

## Pricing и стоимость

### YouTube Data API v3

✅ **БЕСПЛАТНО** для использования (нет платы за API запросы)

**Ограничения:**
- Квота: 10,000 units/день
- Лимит загрузки: 6 видео/день (при 1600 units/видео)

### YouTube Analytics API

✅ **БЕСПЛАТНО** (отдельные квоты, не влияют на Data API v3)

### Дополнительные расходы

**Опционально:**
- Хранение: бесплатно (неограниченное на YouTube)
- Bandwidth: бесплатно (YouTube CDN)
- Make.com Pro: ~$16/месяц (автоматизация)
- YandexGPT API: от $0 (бесплатный tier до 100 запросов/день)

**Итого:** $0-20/месяц в зависимости от автоматизации

---

## Best Practices

### 1. Оптимизация квот

**Проблема:** 10,000 units/день — ограниченный ресурс.

**Решения:**
- Используйте `videos.list` (1 unit) вместо `search.list` (100 units) когда известен video ID
- Кешируйте результаты поиска
- Не используйте `search.list` для проверки наличия видео
- Батчинг: обновляйте метаданные нескольких видео за раз

### 2. Качество видео для туризма

**Рекомендации:**
- Разрешение: минимум 1080p (1920x1080)
- Shorts: 1080x1920 (вертикально)
- Формат: MP4 (H.264 codec)
- Битрейт: 8-12 Mbps (1080p), 5-8 Mbps (720p)
- Аудио: AAC, 128-192 kbps
- Длительность: 8-15 минут (оптимально для алгоритма 2026)

### 3. Метаданные (SEO)

**Title (до 100 символов):**
```
Dubai Desert Safari 2026 - Ultimate Adventure Experience | Dubai Tourism
```

**Description (до 5000 символов):**
```
Experience the ultimate Dubai desert safari adventure! 🏜️

In this video:
✅ Dune bashing in 4x4 vehicles
✅ Camel riding experience
✅ Traditional BBQ dinner
✅ Belly dance show
✅ Henna painting

📞 Book now: +971 50 123 4567
💰 Price: AED 200/person
🌐 Website: example.com

#DubaiTourism #DesertSafari #Dubai2026 #UAETravel
```

**Tags (до 500 символов):**
```
Dubai, Desert Safari, Dubai Tourism, UAE Travel, Dune Bashing, Camel Riding
```

### 4. Thumbnails

**Требования:**
- Разрешение: 1280x720 (минимум)
- Формат: JPG, PNG
- Размер: < 2 MB
- Яркие цвета, крупный текст, эмоции

**Best Practice:** Используйте кастомные thumbnails (не auto-generated).

---

## Безопасность

### 1. Защита OAuth credentials

**НИКОГДА:**
- ❌ Не храните `client_secret.json` в Git
- ❌ Не передавайте Access Token через URL

**ВСЕГДА:**
- ✅ Добавьте `client_secret.json` в `.gitignore`
- ✅ Храните токены в защищенном хранилище
- ✅ Обновляйте Refresh Token регулярно

### 2. Refresh Token

**Важно:** Access Token истекает через 1 час, но Refresh Token **не истекает** (если используется).

```python
# Обновление Access Token
from google.auth.transport.requests import Request

if credentials.expired and credentials.refresh_token:
    credentials.refresh(Request())
    # Сохраните обновленный credentials
```

### 3. Quota Management

**Мониторинг квот:**
```python
# Проверка квоты в Google Cloud Console
# APIs & Services → Dashboard → YouTube Data API v3 → Quotas
```

**Алерты:** Настройте уведомления при достижении 80% квоты.

---

## Поддержка и ресурсы

### Официальная документация
- YouTube Data API v3: https://developers.google.com/youtube/v3/docs
- Quota Calculator: https://developers.google.com/youtube/v3/determine_quota_cost
- Analytics API: https://developers.google.com/youtube-analytics

### Community
- Google Developers Community: https://www.googlecloudcommunity.com/gc/YouTube-API/bd-p/youtube-api
- Stack Overflow: тег `youtube-api`

---

## Следующие шаги

1. Прочитайте `references/data-api-v3.md` для полной настройки OAuth 2.0
2. Изучите `references/upload-videos.md` для различных способов загрузки
3. Попробуйте примеры из `assets/examples/`
4. Настройте автоматизацию через Make.com (`references/make-integration.md`)
5. Интегрируйте YouTube Analytics для отслеживания эффективности

---

**Версия справочника:** 1.0
**Дата создания:** 05.02.2026
**Автор:** Claude Code Agent
**Для:** Туристический бизнес в ОАЭ (Сухейль)

---

## Experience

Этот скилл накапливает опыт в папке `experience/`:
- `_index.md` — критические уроки (читать при активации!)
- `fixes/` — исправленные ошибки
- `improvements/` — найденные улучшения
- `patterns/` — повторяющиеся паттерны
- `warnings/` — что НЕ делать

При завершении работы: если был урок — предложить записать в опыт.
