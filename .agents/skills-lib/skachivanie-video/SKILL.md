---
name: skachivanie-video
description: "Скилл для скачивания видео, аудио, плейлистов и субтитров с YouTube и 1700+ сайтов через yt-dlp. Используется когда пользователь просит скачать видео, извлечь аудио, скачать плейлист, субтитры или отправляет ссылку на видеоплатформу."
---
# Скачивание видео/аудио через yt-dlp

## Quick Start (быстрый старт)

Минимум для начала работы — 4 самые частые команды:

```bash
# Скачать видео (лучшее качество)
yt-dlp -P "D:/Downloads/YouTube/" "URL"

# Скачать видео в MP4 1080p
yt-dlp -f "bv*[ext=mp4][height<=1080]+ba[ext=m4a]/b[ext=mp4]" --merge-output-format mp4 -P "D:/Downloads/YouTube/" "URL"

# Извлечь аудио в MP3
yt-dlp -x --audio-format mp3 --audio-quality 0 -P "D:/Downloads/YouTube/" "URL"

# Скачать плейлист
yt-dlp -P "D:/Downloads/YouTube/" -o "%(playlist)s/%(playlist_index)02d - %(title)s.%(ext)s" "PLAYLIST_URL"
```

> **Путь сохранения: `D:/Downloads/YouTube/` — ВСЕГДА.**

---

## ⚡ Особенности этой системы (Windows — читай первым)

Эта машина настроена специфично. Всегда использовать именно эти значения:

| Параметр | Значение |
|----------|---------|
| **Папка сохранения** | `D:/Downloads/YouTube/` |
| **Конфиг yt-dlp** | `%APPDATA%\yt-dlp\config` (уже настроен) |
| **yt-dlp версия** | 2026.02.04 |
| **FFmpeg версия** | 8.0.1 (в PATH) |
| **deno runtime** | Настроен — обрабатывает YouTube JS challenges |

### Git Bash: трансформация путей

При запуске yt-dlp **из Git Bash** Windows-пути надо трансформировать:
- `D:\` → `/d/`
- `C:\` → `/c/`
- `\` → `/`

```bash
# В Git Bash — ПРАВИЛЬНО:
yt-dlp -P "/d/Downloads/YouTube/" "URL"

# В CMD / PowerShell — ПРАВИЛЬНО:
yt-dlp -P "D:/Downloads/YouTube/" "URL"
```

### deno runtime и YouTube JS challenges

Если YouTube не скачивается с ошибкой "sign in" или "failed to extract":

```bash
# Шаг 1: обновить yt-dlp (решает 90% случаев)
yt-dlp -U

# Шаг 2: deno уже настроен в конфиге — просто запустить заново
# Если не помогло — явно указать player_client:
yt-dlp --extractor-args "youtube:player_client=web,ios" -P "D:/Downloads/YouTube/" "URL"
```

### Конфигурационный файл (уже настроен)

**Путь:** `%APPDATA%\yt-dlp\config`

Текущее содержимое конфига автоматически применяет:
- Путь `-P D:/Downloads/YouTube/` (не нужно указывать каждый раз)
- deno runtime для YouTube JS challenges
- Антибан паузы `--sleep-interval 3`

---

## 1. Окружение и версии

### Текущая конфигурация

| Компонент | Версия | Примечание |
|-----------|--------|------------|
| yt-dlp | 2026.02.04 | Обновлять регулярно: `yt-dlp -U` |
| FFmpeg | 8.0.1 | Обязателен для 1080p+ и извлечения аудио |
| deno | Настроен | Runtime для YouTube JS challenges |

### Конфигурационный файл yt-dlp

**Путь:** `%APPDATA%\yt-dlp\config`

Содержит настройки по умолчанию: путь `D:/Downloads/YouTube/` и deno runtime для обработки YouTube JS challenges. Благодаря конфигу не нужно каждый раз указывать `-P`.

### Путь сохранения (ОБЯЗАТЕЛЬНО)

**Папка для скачивания: `D:/Downloads/YouTube/` — все видео сохраняются сюда.**

```bash
# Базовый шаблон вывода — ВСЕГДА использовать
-P "D:/Downloads/YouTube/" -o "%(title)s.%(ext)s"
```

### Установка и обновление yt-dlp

```bash
# Через pip
pip install -U yt-dlp

# Или скачать yt-dlp.exe из GitHub releases
# https://github.com/yt-dlp/yt-dlp/releases/latest

# Обновление
yt-dlp -U
```

### FFmpeg (КРИТИЧЕСКИ ВАЖНО)

FFmpeg **обязателен** для:
- Слияния video+audio потоков (YouTube хранит их раздельно для 1080p+)
- Извлечения аудио (`-x`)
- Конвертации форматов
- Встраивания субтитров и обложек

**Без FFmpeg максимальное качество в одном файле = 720p!**

```bash
# Проверить наличие
ffmpeg -version

# Windows: скачать с https://www.gyan.dev/ffmpeg/builds/
# Извлечь ffmpeg.exe в папку yt-dlp или добавить в PATH

# Если ffmpeg не в PATH, указать вручную:
--ffmpeg-location "C:/путь/к/ffmpeg.exe"
```

### Проверка установки

```bash
yt-dlp --version    # Ожидание: 2026.02.04+
ffmpeg -version     # Ожидание: 8.0.1+
```

---

## 2. Основные команды

### Скачать видео (лучшее качество)

```bash
yt-dlp -P "D:/Downloads/YouTube/" "URL"
```

### Скачать видео в MP4 (1080p, совместимый формат)

```bash
yt-dlp -f "bv*[ext=mp4][height<=1080]+ba[ext=m4a]/b[ext=mp4]" --merge-output-format mp4 -P "D:/Downloads/YouTube/" "URL"
```

### Скачать только аудио (MP3)

```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 -P "D:/Downloads/YouTube/" "URL"
```

### Скачать плейлист

```bash
yt-dlp -P "D:/Downloads/YouTube/" -o "%(playlist)s/%(playlist_index)02d - %(title)s.%(ext)s" "PLAYLIST_URL"
```

### Скачать субтитры

```bash
yt-dlp --write-subs --sub-lang ru,en -P "D:/Downloads/YouTube/" "URL"
```

### Скачать видео + встроить субтитры + обложку + метаданные

```bash
yt-dlp -f "bv*[ext=mp4]+ba[ext=m4a]" --merge-output-format mp4 --embed-subs --sub-lang ru,en --embed-thumbnail --embed-metadata -P "D:/Downloads/YouTube/" "URL"
```

---

## 3. Выбор формата (-f)

### Основные селекторы

| Селектор | Описание |
|----------|----------|
| `best` | Лучший одиночный файл (video+audio) |
| `worst` | Худшее качество |
| `bestvideo` / `bv` / `bv*` | Лучшее видео (bv* включает комбинированные) |
| `bestaudio` / `ba` | Лучшее аудио |
| `bv*+ba` | Лучшее видео + лучшее аудио (слияние через FFmpeg) |

### Просмотр доступных форматов

```bash
yt-dlp -F "URL"
```

### Фильтрация по свойствам

```bash
# По разрешению
-f "bv*[height=1080]+ba"          # Строго 1080p
-f "bv*[height<=720]+ba"          # До 720p включительно
-f "bv*[height>=1080]+ba"         # 1080p и выше

# По расширению
-f "bv*[ext=mp4]+ba[ext=m4a]"     # Только MP4+M4A
-f "best[ext!=webm]"              # Исключить WebM

# По кодеку
-f "bv*[vcodec=h264]+ba[acodec=aac]"  # H.264 + AAC
-f "bv*[vcodec=vp9]+ba[acodec=opus]"  # VP9 + Opus

# По fps
-f "bv*[fps=60]+ba"               # 60fps видео

# По размеру файла
-f "best[filesize<100M]"          # До 100 МБ

# Комбинация с fallback (через запятую)
-f "bv*[height=1080]+ba/bv*[height=720]+ba/best"
```

### Сортировка по размеру

```bash
-S "+size"    # Самый маленький файл
-S "size"     # Самый большой файл
```

### Конкретный формат по ID

```bash
yt-dlp -F "URL"          # Посмотреть ID форматов
yt-dlp -f 137+140 "URL"  # Скачать конкретные ID
```

### Контейнер вывода

```bash
--merge-output-format mp4    # Объединить в MP4
--merge-output-format mkv    # Объединить в MKV
--remux-video mp4            # Перемуксировать в MP4 (без перекодировки)
--recode-video mp4           # Перекодировать в MP4 (через FFmpeg)
```

---

## 4. Шаблоны вывода (-o)

### Основные переменные

| Переменная | Описание | Пример |
|-----------|----------|--------|
| `%(title)s` | Название видео | My Video Title |
| `%(id)s` | ID видео | dQw4w9WgXcQ |
| `%(ext)s` | Расширение файла | mp4 |
| `%(uploader)s` | Название канала | PewDiePie |
| `%(uploader_id)s` | ID канала | UC-lHJZR3Gqxm24_Vd_AJ5Yw |
| `%(upload_date)s` | Дата загрузки (YYYYMMDD) | 20240315 |
| `%(upload_date>%Y-%m-%d)s` | Дата форматированная | 2024-03-15 |
| `%(duration)s` | Длительность (секунды) | 325 |
| `%(view_count)s` | Просмотры | 1500000 |
| `%(like_count)s` | Лайки | 50000 |
| `%(description)s` | Описание видео | ... |
| `%(resolution)s` | Разрешение | 1920x1080 |
| `%(format_id)s` | ID формата | 137+140 |
| `%(webpage_url)s` | Исходная ссылка | https://... |

### Переменные для плейлистов

| Переменная | Описание |
|-----------|----------|
| `%(playlist)s` | Название плейлиста |
| `%(playlist_id)s` | ID плейлиста |
| `%(playlist_index)s` | Позиция в плейлисте (1, 2, 3...) |
| `%(playlist_count)s` | Всего видео в плейлисте |
| `%(playlist_uploader)s` | Автор плейлиста |

### Примеры шаблонов

```bash
# Простое имя
-o "%(title)s.%(ext)s"

# С датой
-o "%(upload_date>%Y-%m-%d)s - %(title)s.%(ext)s"

# По каналам в папки
-o "%(uploader)s/%(title)s.%(ext)s"

# Плейлист с нумерацией
-o "%(playlist)s/%(playlist_index)02d - %(title)s.%(ext)s"

# Полная организация
-o "%(uploader)s/%(playlist)s/%(playlist_index)02d - %(title)s [%(id)s].%(ext)s"

# Безопасные имена файлов (замена спецсимволов)
-o "%(title|replace,/,-)s.%(ext)s"
--restrict-filenames   # Только ASCII + без пробелов
```

---

## 5. Плейлисты и каналы

### Скачать весь плейлист

```bash
yt-dlp -P "D:/Downloads/YouTube/" -o "%(playlist)s/%(playlist_index)02d - %(title)s.%(ext)s" "PLAYLIST_URL"
```

### Конкретные видео из плейлиста

```bash
# Первые 5
--playlist-items 1-5

# С 10 по 20
--playlist-items 10-20

# Конкретные номера
--playlist-items 1,3,5,7

# Каждое второе видео
-I 1::2

# Последние 3
--playlist-items -3:

# В обратном порядке
--playlist-reverse
```

### Скачать канал целиком

```bash
yt-dlp -P "D:/Downloads/YouTube/" -o "%(uploader)s/%(upload_date>%Y-%m-%d)s - %(title)s.%(ext)s" "https://www.youtube.com/@ChannelName"
```

### Архив скачанных (избежать повторов)

```bash
yt-dlp --download-archive "D:/Downloads/YouTube/yt-archive.txt" --no-overwrites "URL"
```

Файл archive.txt хранит ID скачанных видео. При повторном запуске скачанные пропускаются.

### Ограничение количества

```bash
--max-downloads 10    # Максимум 10 видео
```

### Паузы между скачиваниями (антибан)

```bash
--sleep-interval 5 --max-sleep-interval 15
```

---

## 6. Субтитры

### Просмотр доступных субтитров

```bash
yt-dlp --list-subs "URL"
```

### Скачать субтитры

```bash
# Конкретные языки
--write-subs --sub-lang ru,en

# Автосгенерированные (YouTube)
--write-auto-subs --sub-lang ru

# Все доступные языки
--write-subs --all-subs

# Конвертировать формат
--write-subs --sub-lang en --convert-subs srt
```

### Встроить субтитры в видео

```bash
--embed-subs --sub-lang ru,en    # Встроить как дорожку (MP4/MKV)
```

### Скачать ТОЛЬКО субтитры (без видео)

```bash
yt-dlp --write-subs --sub-lang ru --skip-download "URL"
```

---

## 7. Извлечение аудио

### Основные команды

```bash
# MP3 лучшего качества
yt-dlp -x --audio-format mp3 --audio-quality 0 -P "D:/Downloads/YouTube/" "URL"

# AAC
yt-dlp -x --audio-format aac -P "D:/Downloads/YouTube/" "URL"

# FLAC (без потерь)
yt-dlp -x --audio-format flac -P "D:/Downloads/YouTube/" "URL"

# Opus (эффективный)
yt-dlp -x --audio-format opus -P "D:/Downloads/YouTube/" "URL"

# WAV (без сжатия)
yt-dlp -x --audio-format wav -P "D:/Downloads/YouTube/" "URL"

# Оригинальный формат (без конвертации)
yt-dlp -x --audio-format best -P "D:/Downloads/YouTube/" "URL"
```

### Качество аудио (--audio-quality)

| Значение | Описание |
|----------|----------|
| 0 | Лучшее качество (~320kbps для MP3) |
| 5 | Среднее (~128kbps) |
| 10 | Худшее |

```bash
# MP3 320kbps
yt-dlp -x --audio-format mp3 --audio-quality 0 "URL"

# MP3 с обложкой и метаданными
yt-dlp -x --audio-format mp3 --audio-quality 0 --embed-thumbnail --embed-metadata -P "D:/Downloads/YouTube/" "URL"
```

### Поддерживаемые форматы

mp3, aac, flac, m4a, opus, vorbis, wav

---

## 8. Пост-обработка (FFmpeg)

### Встраивание метаданных

```bash
--embed-metadata       # Название, описание, дата и т.д.
--embed-thumbnail      # Обложка как постер/album art
--embed-chapters       # Главы видео (если есть)
--embed-subs           # Субтитры как дорожка
--embed-info-json      # Полная JSON-информация
```

### Обложки

```bash
--write-thumbnail      # Скачать обложку как отдельный файл
--all-thumbnails       # Все варианты обложек
--embed-thumbnail      # Встроить в файл
```

### Конвертация форматов

```bash
--remux-video mp4      # Перемуксировать (быстро, без перекодировки)
--recode-video mp4     # Перекодировать (медленно, меняет кодек)
```

### Разделение по главам

```bash
yt-dlp --split-chapters -o "%(title)s - %(chapter)s.%(ext)s" -P "D:/Downloads/YouTube/" "URL"
```

### Скачать конкретный отрезок времени

```bash
yt-dlp --download-sections "*00:01:00-00:05:00" -P "D:/Downloads/YouTube/" "URL"
```

### SponsorBlock (удаление рекламных вставок)

```bash
--sponsorblock-remove all           # Удалить все спонсорские вставки
--sponsorblock-remove sponsor,intro # Только спонсоры и интро
--sponsorblock-mark all             # Пометить как главы (не удалять)
```

### Передача аргументов ffmpeg напрямую

```bash
--postprocessor-args "ffmpeg:-ac 2"    # Стерео
```

---

## 9. Аутентификация и cookies

### Cookies из браузера (рекомендуется)

```bash
# Chrome
--cookies-from-browser chrome

# Firefox
--cookies-from-browser firefox

# Edge
--cookies-from-browser edge

# Brave
--cookies-from-browser brave

# С указанием профиля
--cookies-from-browser chrome:Default
--cookies-from-browser chrome:Profile1
```

**Когда нужны cookies:**
- Возрастные ограничения (18+)
- Видео только для подписчиков
- Приватные видео (если есть доступ)
- Членство на канале (Members only)

### Cookies из файла

```bash
--cookies cookies.txt
```

Формат файла: Netscape cookies (экспорт расширением "Get cookies.txt" для браузера).

### Логин/пароль (некоторые сайты)

```bash
-u USERNAME -p PASSWORD
--video-password PASSWORD    # Пароль к конкретному видео
```

---

## 10. Пакетное скачивание

### Из файла со ссылками

```bash
# Создать файл urls.txt (одна ссылка на строку):
# https://youtube.com/watch?v=xxx
# https://youtube.com/watch?v=yyy

yt-dlp -a urls.txt -P "D:/Downloads/YouTube/"
```

### С архивом и продолжением

```bash
yt-dlp -a urls.txt --download-archive "D:/Downloads/YouTube/archive.txt" -P "D:/Downloads/YouTube/" --no-overwrites -i
```

Флаг `-i` (--ignore-errors) пропускает ошибки и продолжает со следующим видео.

---

## 11. Сеть и производительность

### Ограничение скорости

```bash
--limit-rate 2M        # 2 МБ/с
--limit-rate 500K      # 500 КБ/с
```

### Параллельная загрузка фрагментов

```bash
-N 4                   # 4 потока (ускорение DASH/HLS)
```

### Прокси

```bash
--proxy "http://host:port"
--proxy "http://user:pass@host:port"
--proxy "socks5://host:port"
```

### Таймауты и повторы

```bash
--socket-timeout 30    # Таймаут соединения
--retries 10           # Повторы при ошибке
--fragment-retries 10  # Повторы для фрагментов
```

### Внешний загрузчик (aria2c для максимальной скорости)

```bash
--downloader aria2c --downloader-args "-x 16 -k 1M"
```

### Гео-обход

```bash
--geo-bypass                   # Попытка обхода геоблокировки
--geo-bypass-country US        # Имитировать запрос из США
```

---

## 12. Информация без скачивания

```bash
# JSON-информация о видео
yt-dlp -j --no-download "URL"

# Список форматов
yt-dlp -F "URL"

# Получить прямую ссылку
yt-dlp -g "URL"

# Получить название
yt-dlp -e "URL"

# Получить имя файла
yt-dlp --get-filename "URL"

# Список субтитров
yt-dlp --list-subs "URL"

# Симуляция (показать что будет скачано)
yt-dlp -s "URL"
```

---

## 13. Конфигурационный файл

**Актуальный путь:** `%APPDATA%\yt-dlp\config`

> Файл конфига уже настроен. Включает путь по умолчанию `D:/Downloads/YouTube/` и deno runtime для YouTube JS challenges.

Пример расширенного конфига:
```
# Формат и качество
-f bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]
--merge-output-format mp4

# Метаданные
--embed-metadata
--embed-thumbnail
--embed-chapters

# Субтитры
--embed-subs
--sub-lang ru,en

# Вывод
-o %(uploader)s/%(title)s.%(ext)s
-P D:/Downloads/YouTube/

# Антибан
--sleep-interval 3
--max-sleep-interval 10

# Архив
--download-archive D:/Downloads/YouTube/.yt-dlp-archive.txt
```

---

## 14. Поддерживаемые сайты (1700+)

**Основные:**
- YouTube (видео, плейлисты, каналы, Shorts, Music)
- TikTok
- Instagram (Reels, Stories, IGTV)
- Twitter/X
- Reddit
- Facebook
- Twitch (VOD, клипы, стримы)
- Vimeo
- Dailymotion
- VK (ВКонтакте)
- Bilibili
- Rutube
- OK.ru (Одноклассники)
- SoundCloud
- Bandcamp
- И ещё 1700+ сайтов

Полный список:
```bash
yt-dlp --list-extractors
```

---

## 15. Готовые рецепты

### Максимальное качество (4K MP4 если доступно)

```bash
yt-dlp -f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]" --merge-output-format mp4 --embed-metadata --embed-thumbnail --embed-chapters -P "D:/Downloads/YouTube/" "URL"
```

### Аудио-плейлист (MP3 коллекция)

```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 --embed-thumbnail --embed-metadata -o "%(playlist)s/%(playlist_index)02d - %(title)s.%(ext)s" --download-archive "D:/Downloads/YouTube/music-archive.txt" -P "D:/Downloads/YouTube/" "PLAYLIST_URL"
```

### Скачать с TikTok / Instagram

```bash
# TikTok
yt-dlp -P "D:/Downloads/YouTube/" "https://www.tiktok.com/@user/video/123456"

# Instagram Reel
yt-dlp --cookies-from-browser chrome -P "D:/Downloads/YouTube/" "https://www.instagram.com/reel/xxx/"
```

### YouTube Shorts

```bash
yt-dlp --no-playlist -P "D:/Downloads/YouTube/" "https://youtube.com/shorts/xxx"
```

### Стрим (запись)

```bash
yt-dlp --live-from-start -P "D:/Downloads/YouTube/" "LIVE_URL"
```

### Видео с возрастным ограничением

```bash
yt-dlp --cookies-from-browser chrome -P "D:/Downloads/YouTube/" "URL"
```

---

## 16. Важные замечания

1. **FFmpeg обязателен** для качества выше 720p (YouTube хранит video и audio раздельно для HD+)
2. **Обновляй yt-dlp регулярно** (`yt-dlp -U`) — сайты часто меняют API
3. **Используй `--download-archive`** для плейлистов — избежит повторного скачивания
4. **`--sleep-interval`** при массовом скачивании — защита от бана
5. **Cookies нужны** для приватного/возрастного контента
6. **`-i` (--ignore-errors)** при пакетной загрузке — пропускает битые ссылки
7. **Git Bash пути**: `D:\Downloads\YouTube\` -> `-P "/d/Downloads/YouTube/"` (если запуск из Git Bash)

---

## Краткая памятка

| Задача | Команда |
|--------|---------|
| Скачать видео | `yt-dlp -P "D:/Downloads/YouTube/" "URL"` |
| MP4 1080p | `-f "bv*[ext=mp4][height<=1080]+ba[ext=m4a]" --merge-output-format mp4` |
| Только MP3 | `-x --audio-format mp3 --audio-quality 0` |
| Плейлист | `-o "%(playlist)s/%(playlist_index)02d - %(title)s.%(ext)s"` |
| Субтитры | `--write-subs --sub-lang ru,en` |
| Cookies | `--cookies-from-browser chrome` |
| Обновление | `yt-dlp -U` |
| Список форматов | `yt-dlp -F "URL"` |
| Проблемы | `yt-dlp -v "URL"` (debug лог) |

---

## Дополнительные ресурсы

### Внутренние (references/)

| Файл | Описание | Когда смотреть |
|------|----------|----------------|
| `references/cheatsheet.md` | Шпаргалка — все команды компактно | Быстрая справка по командам |
| `references/faq.md` | 27 вопросов с ответами | Есть вопрос "как сделать X?" |
| `references/troubleshooting.md` | 20+ ошибок с решениями | Ошибка при скачивании |

### Внешние ссылки

- [GitHub yt-dlp](https://github.com/yt-dlp/yt-dlp) — официальный репозиторий
- [FFmpeg](https://www.gyan.dev/ffmpeg/builds/) — скачать для Windows
- [Supported Sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) — полный список сайтов

### Experience (опыт)

Папка `experience/` хранит накопленные уроки работы со скиллом. При активации проверять `experience/_index.md`.
