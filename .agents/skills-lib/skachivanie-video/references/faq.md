# yt-dlp — Часто задаваемые вопросы (FAQ)

---

## Общие вопросы

### Q1: Что такое yt-dlp?

yt-dlp — бесплатный консольный инструмент для скачивания видео и аудио с YouTube и 1700+ других сайтов. Это форк youtube-dl с активной разработкой, новыми функциями и быстрыми исправлениями.

**Поддерживаемые платформы:** YouTube, TikTok, Instagram, Twitter/X, Reddit, Facebook, Twitch, Vimeo, VK, Dailymotion, Bilibili, Rutube, OK.ru, SoundCloud, Bandcamp и ещё 1700+ сайтов.

---

### Q2: Чем yt-dlp отличается от youtube-dl?

| Функция | youtube-dl | yt-dlp |
|---------|-----------|--------|
| Активная разработка | Практически заброшен | Активная |
| Скорость загрузки | Медленная | Быстрая (параллельные фрагменты) |
| SponsorBlock | Нет | Да |
| Cookies из браузера | Нет | Да (`--cookies-from-browser`) |
| Разделение по главам | Нет | Да (`--split-chapters`) |
| Скачивание фрагментов | Нет | Да (`--download-sections`) |
| Обновления | Редкие | Ежедневные (nightly) |

---

### Q3: Зачем нужен FFmpeg?

FFmpeg **обязателен** для:
1. **Слияния video + audio** — YouTube хранит видео и аудио раздельно для качества 1080p и выше. Без FFmpeg максимум 720p в одном файле.
2. **Извлечения аудио** (`-x`) — конвертация в MP3, AAC, FLAC и т.д.
3. **Конвертации форматов** — перемуксирование и перекодирование
4. **Встраивания субтитров** — `--embed-subs`
5. **Встраивания обложек** — `--embed-thumbnail`
6. **Удаления спонсорских вставок** — `--sponsorblock-remove`

**Без FFmpeg = серьёзные ограничения.** Установи обязательно.

---

### Q4: Как обновить yt-dlp?

```bash
# Бинарник
yt-dlp -U

# Через pip
pip install -U yt-dlp

# Переключиться на nightly (самые свежие фиксы)
yt-dlp --update-to nightly
```

**Обновляй регулярно!** Сайты часто меняют API, и старые версии перестают работать.

---

### Q5: Куда сохраняются файлы?

По умолчанию — в текущую рабочую директорию. Для наших настроек ВСЕГДА используй:

```bash
-P "D:/Downloads/YouTube/"
```

Или настрой в конфиге `%APPDATA%\yt-dlp\config.txt`:
```
-P D:/Downloads/YouTube/
```

---

## Качество и форматы

### Q6: Как скачать видео в максимальном качестве?

```bash
# Автоматически лучшее (по умолчанию)
yt-dlp "URL"

# Явно: лучшее видео + лучшее аудио в MP4
yt-dlp -f "bv*[ext=mp4]+ba[ext=m4a]" --merge-output-format mp4 -P "D:/Downloads/YouTube/" "URL"
```

---

### Q7: Как скачать в конкретном разрешении (720p, 1080p, 4K)?

```bash
# Строго 1080p
yt-dlp -f "bv*[height=1080]+ba" -P "D:/Downloads/YouTube/" "URL"

# До 720p (включительно)
yt-dlp -f "bv*[height<=720]+ba" -P "D:/Downloads/YouTube/" "URL"

# 4K
yt-dlp -f "bv*[height=2160]+ba" -P "D:/Downloads/YouTube/" "URL"

# Если нужного разрешения нет — fallback
yt-dlp -f "bv*[height=1080]+ba/bv*[height=720]+ba/best" -P "D:/Downloads/YouTube/" "URL"
```

---

### Q8: Как узнать доступные форматы?

```bash
yt-dlp -F "URL"
```

Покажет таблицу всех доступных потоков с ID, разрешением, кодеком, размером и типом (video-only, audio-only, combined).

---

### Q9: Почему максимальное качество = 720p без FFmpeg?

YouTube хранит HD+ видео (1080p, 1440p, 4K) как **раздельные** потоки: видео отдельно, аудио отдельно. Для их объединения нужен FFmpeg. Без него yt-dlp может скачать только готовый комбинированный файл, а у YouTube максимальный combined формат = 720p.

**Решение:** Установить FFmpeg и добавить в PATH.

---

## Аудио

### Q10: Как извлечь аудио из видео?

```bash
# MP3 лучшего качества
yt-dlp -x --audio-format mp3 --audio-quality 0 -P "D:/Downloads/YouTube/" "URL"

# С обложкой и тегами
yt-dlp -x --audio-format mp3 --audio-quality 0 --embed-thumbnail --embed-metadata -P "D:/Downloads/YouTube/" "URL"
```

---

### Q11: Какой аудио-формат лучше?

| Формат | Тип | Размер | Качество | Совместимость |
|--------|-----|--------|----------|---------------|
| FLAC | Lossless | Большой | Максимальное | Средняя |
| WAV | Lossless | Очень большой | Максимальное | Высокая |
| MP3 | Lossy | Средний | Хорошее (320kbps) | Максимальная |
| AAC/M4A | Lossy | Средний | Хорошее | Высокая |
| Opus | Lossy | Маленький | Отличное | Средняя |
| Vorbis | Lossy | Маленький | Хорошее | Средняя |

**Рекомендации:**
- Для музыки на телефон/плеер: **MP3** (--audio-quality 0)
- Для архива: **FLAC**
- Для минимального размера: **Opus**

---

## Плейлисты и каналы

### Q12: Как скачать весь плейлист?

```bash
yt-dlp -o "%(playlist)s/%(playlist_index)02d - %(title)s.%(ext)s" -P "D:/Downloads/YouTube/" "PLAYLIST_URL"
```

---

### Q13: Как не скачивать видео повторно?

Используй `--download-archive`:

```bash
yt-dlp --download-archive "D:/Downloads/YouTube/archive.txt" "PLAYLIST_URL"
```

При каждом запуске yt-dlp проверит файл archive.txt и пропустит уже скачанные видео. Идеально для регулярного обновления подписок.

---

### Q14: Как скачать канал целиком?

```bash
yt-dlp --download-archive "D:/Downloads/YouTube/channel-archive.txt" --sleep-interval 5 --max-sleep-interval 15 -o "%(uploader)s/%(upload_date>%Y-%m-%d)s - %(title)s.%(ext)s" -P "D:/Downloads/YouTube/" "https://youtube.com/@ChannelName"
```

**Важно:** используй `--sleep-interval` для больших каналов, иначе YouTube может заблокировать.

---

## Субтитры

### Q15: Как скачать субтитры?

```bash
# Посмотреть доступные
yt-dlp --list-subs "URL"

# Скачать RU + EN
yt-dlp --write-subs --sub-lang ru,en -P "D:/Downloads/YouTube/" "URL"

# Автосгенерированные (YouTube)
yt-dlp --write-auto-subs --sub-lang ru -P "D:/Downloads/YouTube/" "URL"

# Встроить в видео
yt-dlp --embed-subs --sub-lang ru,en -P "D:/Downloads/YouTube/" "URL"

# Только субтитры (без видео)
yt-dlp --write-subs --sub-lang ru --skip-download "URL"
```

---

## Аутентификация

### Q16: Как скачать видео с возрастным ограничением?

```bash
yt-dlp --cookies-from-browser chrome -P "D:/Downloads/YouTube/" "URL"
```

Нужны cookies от аккаунта Google, который подтвердил возраст.

---

### Q17: Как скачать приватное видео?

Если у тебя есть доступ к приватному видео через аккаунт:

```bash
yt-dlp --cookies-from-browser chrome -P "D:/Downloads/YouTube/" "URL"
```

Если нет доступа — скачать невозможно.

---

### Q18: Как экспортировать cookies?

**Способ 1 (рекомендуется):** Напрямую из браузера:
```bash
--cookies-from-browser chrome
--cookies-from-browser firefox
--cookies-from-browser edge
```

**Способ 2:** Расширение браузера "Get cookies.txt LOCALLY" — экспорт в Netscape формат:
```bash
--cookies cookies.txt
```

---

## Пакетная загрузка

### Q19: Как скачать много видео из списка?

1. Создай файл `urls.txt` (одна ссылка на строку)
2. Запусти:

```bash
yt-dlp -a urls.txt -i --download-archive done.txt -P "D:/Downloads/YouTube/"
```

- `-a urls.txt` — читать ссылки из файла
- `-i` — пропускать ошибки
- `--download-archive done.txt` — не повторять скачанные

---

## Разное

### Q20: Как скачать только фрагмент видео?

```bash
# С 1:00 по 5:00
yt-dlp --download-sections "*00:01:00-00:05:00" -P "D:/Downloads/YouTube/" "URL"
```

---

### Q21: Как разделить видео по главам?

```bash
yt-dlp --split-chapters -o "%(title)s - %(chapter)s.%(ext)s" -P "D:/Downloads/YouTube/" "URL"
```

Каждая глава станет отдельным файлом.

---

### Q22: Как убрать рекламные вставки (SponsorBlock)?

```bash
# Удалить все спонсорские вставки
yt-dlp --sponsorblock-remove all -P "D:/Downloads/YouTube/" "URL"

# Только пометить как главы (можно пропустить при просмотре)
yt-dlp --sponsorblock-mark all -P "D:/Downloads/YouTube/" "URL"
```

---

### Q23: Как записать стрим?

```bash
# Текущий стрим
yt-dlp -P "D:/Downloads/YouTube/" "LIVE_URL"

# С начала (YouTube, Twitch)
yt-dlp --live-from-start -P "D:/Downloads/YouTube/" "LIVE_URL"

# HLS стрим (защита от повреждения)
yt-dlp --hls-use-mpegts -P "D:/Downloads/YouTube/" "LIVE_URL"
```

---

### Q24: Можно ли скачивать из VK / Rutube / OK.ru?

Да, yt-dlp поддерживает все три:

```bash
# VK
yt-dlp -P "D:/Downloads/YouTube/" "https://vk.com/video-xxx_xxx"

# Rutube
yt-dlp -P "D:/Downloads/YouTube/" "https://rutube.ru/video/xxx/"

# Одноклассники
yt-dlp -P "D:/Downloads/YouTube/" "https://ok.ru/video/xxx"
```

---

### Q25: Как скачать с Instagram / TikTok?

```bash
# TikTok (обычно без cookies)
yt-dlp -P "D:/Downloads/YouTube/" "https://tiktok.com/@user/video/xxx"

# Instagram (нужны cookies для приватных)
yt-dlp --cookies-from-browser chrome -P "D:/Downloads/YouTube/" "https://instagram.com/reel/xxx/"
```

---

### Q26: Как ускорить загрузку?

```bash
# Параллельные фрагменты (для DASH/HLS)
yt-dlp -N 4 "URL"

# Внешний загрузчик aria2c
yt-dlp --downloader aria2c --downloader-args "-x 16 -k 1M" "URL"
```

---

### Q27: Легально ли скачивать видео?

Скачивание для личного использования в большинстве юрисдикций попадает под fair use. Однако:
- Это нарушает ToS YouTube и некоторых других платформ
- Распространение защищённого контента незаконно
- YouTube не предпринимает действий против обычных пользователей
- Используй ответственно и для личных целей
