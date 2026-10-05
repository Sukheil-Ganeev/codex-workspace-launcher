# Video Pipeline -- Скачивание, транскрипция, облако

> Справочник по видео-пайплайну VoiceTranscriptionBot
> Путь проекта: `D:/Downloads/VoiceTranscriptionBot/`
> Файлы: `core/video_downloader.py`, `core/video_manager.py`, `core/cloud_storage.py`

---

## Общая архитектура

```
URL видео (YouTube, TikTok, VK, Instagram, etc.)
    |
    v
[video_downloader.get_info()] -- извлечь title, duration, platform
    |
    v
[video_manager.save_download()] -- сохранить запись в SQLite
    |
    v
User выбирает действие: Download / Transcribe / Both
    |
    v
[video_downloader.download()] -- yt-dlp скачивание с качеством/форматом
    |
    v
[video_manager.update_status("ready")]
    |
    v
[Проверка размера файла]
    |
    +-- <= 50 MB --> Отправить напрямую через Telegram/WhatsApp
    |
    +-- > 50 MB --> [cloud_storage.upload()] --> Отправить публичную ссылку
    |                   |
    |                   v
    |               [CloudUploadTracker.save_upload()]
    |
    v
[User подтверждает загрузку] --> expires_at = now + 1 day
    |
    v
[Scheduled cleanup] --> удаление истёкших файлов
```

---

## Video Downloader (yt-dlp wrapper)

**Файл:** `core/video_downloader.py`

### Класс VideoDownloader

Обёртка над yt-dlp для безопасного скачивания видео с 1700+ платформ.

### VideoInfo dataclass

```python
@dataclass
class VideoInfo:
    title: str                     # Название видео
    duration_seconds: int          # Длительность в секундах
    platform: str                  # "youtube" | "tiktok" | "vk" | "instagram" | "other"
    url: str                       # Оригинальный URL
    is_available: bool             # Доступно ли для скачивания
    error_message: str | None      # Текст ошибки (если недоступно)
```

### Получение информации

```python
async def get_info(self, url: str) -> VideoInfo:
    """Извлечь метаданные видео без скачивания."""
```

Таймауты: `socket_timeout=30s`, 1 retry.

### 4 Quality Presets

| Качество | yt-dlp format selector | Описание |
|----------|----------------------|----------|
| `360p` | `bv*[height<=360]+ba/b[height<=360]/best[height<=360]` | Минимальное качество, маленький файл |
| `720p` | `bv*[height<=720]+ba/b[height<=720]/best[height<=720]` | HD, баланс качества и размера |
| `1080p` | `bv*[height<=1080]+ba[ext=m4a]/b[ext=mp4]/best[height<=1080]` | Full HD |
| `best` | `bv*+ba/b` | Лучшее доступное |

### Скачивание

```python
async def download(
    self, url: str,
    output_dir: str,
    quality: str = "720p",
    format: str = "mp4",
) -> str:
    """Скачать видео, вернуть путь к файлу."""
```

Таймауты: `socket_timeout=600s`, 1 retry.

### MP3 извлечение

Для транскрипции извлекается только аудиодорожка:

```python
# format selector
format = "ba/b"

# Postprocessor
postprocessors = [{
    "key": "FFmpegExtractAudio",
    "preferredcodec": "mp3",
    "preferredquality": "192",
}]
```

Результат: MP3 файл 192kbps -> передаётся в `process_voice()`.

### Обработка ошибок

| Ситуация | Сообщение |
|----------|-----------|
| Приватное/требуется авторизация | "Видео приватное или требует авторизации" |
| Недоступно | "Видео недоступно" |
| Геоблокировка | "Видео заблокировано в этом регионе" |
| Таймаут | Retry с backoff |

---

## Video Manager (SQLite tracking)

**Файл:** `core/video_manager.py`

### Таблица video_downloads

```sql
CREATE TABLE video_downloads (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                  TEXT NOT NULL,
    platform                 TEXT NOT NULL,
    url                      TEXT NOT NULL,
    title                    TEXT,
    duration_seconds         INTEGER,
    file_path                TEXT,
    quality                  TEXT,
    format                   TEXT,
    status                   TEXT NOT NULL DEFAULT 'pending',
    action                   TEXT NOT NULL,
    transcription_id         INTEGER,
    downloaded_at            DATETIME,
    expires_at               DATETIME NOT NULL,
    user_confirmed_download  INTEGER DEFAULT 0,
    created_at               DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transcription_id) REFERENCES transcriptions(id)
);
```

**Индексы:**
- `idx_video_downloads_expires` ON `video_downloads(expires_at)`
- `idx_video_downloads_user` ON `video_downloads(user_id)`

### Жизненный цикл статуса

```
pending -> ready -> deleted
```

### Действия (actions)

| Action | Описание |
|--------|----------|
| `ACTION_DOWNLOAD` | Только скачать видео |
| `ACTION_TRANSCRIBE` | Только извлечь аудио и транскрибировать |
| `ACTION_BOTH` | Скачать видео И транскрибировать |

### Smart Deletion Logic

- Файлы имеют `expires_at` (установлен при создании)
- Подтверждение пользователя -> `expires_at = now + 1 day`
- `cleanup_expired()` удаляет файлы после истечения
- `delete_now()` немедленно удаляет файл с диска

### Методы

| Метод | Описание |
|-------|----------|
| `save_download(user_id, platform, url, title, ...)` | Создать запись, returns ID |
| `update_status(download_id, status, file_path?)` | Обновить статус |
| `confirm_downloaded(download_id)` | expires_at = now + 1 day |
| `delete_download(download_id)` | status = 'deleted' |
| `get_expired()` | Истёкшие и не удалённые |
| `get_download(download_id)` | Одна запись по ID |
| `cleanup_expired()` | Удалить файлы с диска, пометить 'deleted' |

---

## Cloud Storage (Google Drive + Yandex Disk)

**Файл:** `core/cloud_storage.py`

### Назначение

Загрузка видеофайлов, превышающих лимит Telegram (50 MB), в облачное хранилище с получением публичной ссылки.

### Yandex Disk (`YandexDiskStorage`)

**API:** `https://cloud-api.yandex.net/v1/disk`
**Auth:** OAuth token (`YANDEX_DISK_TOKEN`)
**Папка:** `VoiceBot_uploads/`

```python
class YandexDiskStorage:
    async def upload(self, file_path: str, file_name: str) -> str:
        """Загрузить файл, вернуть публичную ссылку."""
```

**Поток:**
1. Создать папку (если не существует)
2. Получить URL для загрузки
3. PUT файл на полученный URL
4. Опубликовать файл (publish)
5. Получить публичную ссылку

**Таймауты:** 30s (мета), 600s (загрузка)

**Ошибки:** 507 (диск полон), 403 (нет доступа)

### Google Drive (`GoogleDriveStorage`)

**API:** Google Drive API v3 с resumable uploads
**Auth:** Service account credentials (`GOOGLE_DRIVE_CREDENTIALS`)

```python
class GoogleDriveStorage:
    async def upload(
        self, file_path: str, file_name: str,
        progress_callback=None,
    ) -> str:
        """Загрузить файл чанками, вернуть публичную ссылку."""
```

**Поток:**
1. Получить/обновить access token (service account)
2. Инициировать resumable upload
3. Загрузить файл чанками по 5 MB с progress callback
4. Поделиться файлом публично (anyone -> reader)
5. Вернуть URL: `https://drive.google.com/file/d/{id}/view?usp=sharing`

**Chunked upload:**
- `_CHUNK_SIZE = 5 * 1024 * 1024` (5 MB)
- Каждый чанк отправляется с `Content-Range` заголовком
- Progress callback вызывается после каждого чанка

**Token caching:** Кеширование с 5-минутным буфером до истечения.

**Ошибки:** 507 (хранилище заполнено), 403 (нет доступа)

---

## CloudUploadTracker (SQLite)

### Таблица cloud_uploads

```sql
CREATE TABLE cloud_uploads (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT NOT NULL,
    download_id INTEGER,
    service     TEXT NOT NULL,           -- "google_drive" | "yandex_disk"
    file_id     TEXT NOT NULL,
    file_name   TEXT,
    file_size   INTEGER,
    public_url  TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'active',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at  DATETIME NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Индексы:**
- `idx_cloud_uploads_expires` ON `cloud_uploads(expires_at)`
- `idx_cloud_uploads_user` ON `cloud_uploads(user_id)`

### Управление через CloudUploadTracker

Использует синхронный `sqlite3` (не aiosqlite), тот же файл БД.

---

## Константы

| Константа | Значение | Где |
|-----------|----------|-----|
| `CLOUD_EXPIRES_DAYS` | 2 дня | cloud_storage.py |
| `_CHUNK_SIZE` (Google Drive) | 5 MB | cloud_storage.py |
| Upload timeout | 600s | cloud_storage.py |
| Meta timeout | 30s | cloud_storage.py |
| Download timeout | 600s | video_downloader.py |
| Info timeout | 30s | video_downloader.py |
| MP3 quality | 192 kbps | video_downloader.py |
| Telegram file limit | 50 MB | handlers.py |

---

## Download -> Transcribe -> Summarize Flow

Для действия `ACTION_TRANSCRIBE` или `ACTION_BOTH`:

```
1. video_downloader.download(url, format="mp3") -- извлечь аудио
    |
    v
2. process_voice(mp3_path, user_id, method_prefix="video_")
    |
    v
3. STT: faster-whisper / Groq (result.method = "video_local" или "video_groq")
    |
    v
4. Correction -> Sentiment -> Summarization -> Key Facts -> Category
    |
    v
5. Save to DB (source_type записывается, transcription_id привязывается к video_download)
    |
    v
6. Formatted response отправляется пользователю
```

---

## Поддерживаемые платформы

Детекция через `is_video_url()` и `detect_platform()`:

| Платформа | Значение `platform` |
|-----------|-------------------|
| YouTube | `youtube` |
| TikTok | `tiktok` |
| VK | `vk` |
| Instagram | `instagram` |
| Другие | `other` |

yt-dlp поддерживает 1700+ платформ, так что фактически работает практически с любым видеохостингом.

---

## Scheduled Cleanup

### Video Downloads

- **Когда:** Ежедневно в 03:00 Dubai
- **Что:** `cleanup_video_downloads()` -- удаление файлов с диска после `expires_at`
- **Статус:** Меняется на `deleted`

### Cloud Uploads

- **Когда:** Каждый час
- **Что:** `cleanup_cloud_uploads()`:
  1. `get_expired()` -- найти истёкшие загрузки
  2. Удалить файлы из облака (Google Drive API delete / Yandex Disk delete)
  3. `mark_deleted()` -- пометить в SQLite
- **Срок жизни:** 2 дня (`CLOUD_EXPIRES_DAYS`)

---

## Конфигурация (.env)

| Переменная | Обязательна | Описание |
|------------|-------------|----------|
| `YANDEX_DISK_TOKEN` | Нет | OAuth token для Yandex Disk |
| `GOOGLE_DRIVE_CREDENTIALS` | Нет | Путь к JSON service account Google Drive |
| `TEMP_DIR` | Нет (default `temp/`) | Директория для временных файлов |

Облачные хранилища инициализируются условно:
```python
if config.YANDEX_DISK_TOKEN:
    yandex_disk = YandexDiskStorage(...)
if config.GOOGLE_DRIVE_CREDENTIALS:
    google_drive = GoogleDriveStorage(...)
```
