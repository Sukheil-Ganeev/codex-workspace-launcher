# yt-dlp — Шпаргалка по командам

> Путь сохранения по умолчанию: `-P "D:/Downloads/YouTube/"`

---

## Установка и обновление

```bash
pip install -U yt-dlp              # Установка / обновление через pip
yt-dlp -U                          # Обновление бинарника
yt-dlp --update-to nightly         # Переключиться на ночные сборки
yt-dlp --version                   # Текущая версия
ffmpeg -version                    # Проверить FFmpeg
```

---

## Базовое скачивание

```bash
yt-dlp "URL"                                        # Лучшее качество
yt-dlp -P "D:/Downloads/YouTube/" "URL"                     # В нужную папку
yt-dlp -f best "URL"                                # Лучший одиночный файл
yt-dlp -f worst "URL"                               # Худшее качество (экономия)
```

---

## Выбор формата и качества

```bash
# Просмотр форматов
yt-dlp -F "URL"

# Лучшее видео + аудио (слияние, нужен FFmpeg)
yt-dlp -f "bv*+ba" "URL"

# MP4 до 1080p
yt-dlp -f "bv*[ext=mp4][height<=1080]+ba[ext=m4a]" --merge-output-format mp4 "URL"

# Строго 720p
yt-dlp -f "bv*[height=720]+ba" "URL"

# 4K если есть
yt-dlp -f "bv*[height=2160]+ba" "URL"

# 60fps
yt-dlp -f "bv*[fps=60]+ba" "URL"

# Конкретные ID форматов
yt-dlp -f 137+140 "URL"

# Наименьший размер
yt-dlp -S "+size" "URL"

# H.264 + AAC (максимальная совместимость)
yt-dlp -f "bv*[vcodec=h264]+ba[acodec=aac]" --merge-output-format mp4 "URL"

# VP9 + Opus (лучшее соотношение качество/размер)
yt-dlp -f "bv*[vcodec=vp9]+ba[acodec=opus]" "URL"

# С fallback
yt-dlp -f "bv*[height=1080]+ba/bv*[height=720]+ba/best" "URL"
```

---

## Извлечение аудио

```bash
yt-dlp -x --audio-format mp3 "URL"                  # MP3
yt-dlp -x --audio-format mp3 --audio-quality 0 "URL" # MP3 лучшее качество
yt-dlp -x --audio-format aac "URL"                   # AAC
yt-dlp -x --audio-format flac "URL"                  # FLAC (lossless)
yt-dlp -x --audio-format opus "URL"                  # Opus
yt-dlp -x --audio-format wav "URL"                   # WAV
yt-dlp -x --audio-format m4a "URL"                   # M4A
yt-dlp -x --audio-format best "URL"                  # Оригинал без конвертации

# MP3 с обложкой и тегами
yt-dlp -x --audio-format mp3 --audio-quality 0 --embed-thumbnail --embed-metadata "URL"
```

---

## Плейлисты

```bash
yt-dlp "PLAYLIST_URL"                                # Весь плейлист
yt-dlp --playlist-items 1-5 "URL"                    # Первые 5
yt-dlp --playlist-items 10-20 "URL"                  # С 10 по 20
yt-dlp --playlist-items 1,3,7 "URL"                  # Конкретные
yt-dlp -I 1::2 "URL"                                # Каждое второе
yt-dlp --playlist-items -3: "URL"                    # Последние 3
yt-dlp --playlist-reverse "URL"                      # В обратном порядке
yt-dlp --max-downloads 10 "URL"                      # Максимум 10

# Плейлист с нумерацией в папку
yt-dlp -o "%(playlist)s/%(playlist_index)02d - %(title)s.%(ext)s" "URL"

# Архив (не скачивать повторно)
yt-dlp --download-archive archive.txt "URL"

# Антибан (пауза между видео)
yt-dlp --sleep-interval 5 --max-sleep-interval 15 "URL"
```

---

## Субтитры

```bash
yt-dlp --list-subs "URL"                             # Список доступных
yt-dlp --write-subs --sub-lang ru,en "URL"           # Скачать RU + EN
yt-dlp --write-auto-subs --sub-lang ru "URL"         # Автосгенерированные
yt-dlp --write-subs --all-subs "URL"                 # Все языки
yt-dlp --embed-subs --sub-lang ru,en "URL"           # Встроить в видео
yt-dlp --write-subs --convert-subs srt "URL"         # Конвертировать в SRT
yt-dlp --write-subs --sub-lang ru --skip-download "URL"  # Только субтитры
```

---

## Шаблоны имён файлов

```bash
-o "%(title)s.%(ext)s"                               # По названию
-o "%(upload_date>%Y-%m-%d)s - %(title)s.%(ext)s"    # С датой
-o "%(uploader)s/%(title)s.%(ext)s"                  # В папку канала
-o "%(playlist)s/%(playlist_index)02d - %(title)s.%(ext)s"  # Плейлист
-o "%(uploader)s/%(playlist)s/%(playlist_index)02d - %(title)s [%(id)s].%(ext)s"  # Полная
--restrict-filenames                                  # Только ASCII, без пробелов
```

### Переменные

| Переменная | Что это |
|-----------|---------|
| `%(title)s` | Название |
| `%(id)s` | ID видео |
| `%(ext)s` | Расширение |
| `%(uploader)s` | Канал |
| `%(upload_date)s` | Дата (YYYYMMDD) |
| `%(upload_date>%Y-%m-%d)s` | Дата (YYYY-MM-DD) |
| `%(duration)s` | Длительность (сек) |
| `%(view_count)s` | Просмотры |
| `%(playlist)s` | Название плейлиста |
| `%(playlist_index)s` | Номер в плейлисте |
| `%(playlist_count)s` | Всего в плейлисте |
| `%(resolution)s` | Разрешение |
| `%(format_id)s` | ID формата |

---

## Метаданные и постобработка

```bash
--embed-metadata                    # Встроить метаданные
--embed-thumbnail                   # Встроить обложку
--embed-chapters                    # Встроить главы
--embed-subs                        # Встроить субтитры
--embed-info-json                   # Встроить JSON-инфо

--write-thumbnail                   # Скачать обложку отдельно
--all-thumbnails                    # Все варианты обложек

--remux-video mp4                   # Перемуксировать (быстро)
--recode-video mp4                  # Перекодировать (медленно)
--merge-output-format mp4           # Контейнер слияния

--split-chapters                    # Разделить по главам
--download-sections "*01:00-05:00"  # Вырезать фрагмент

# SponsorBlock
--sponsorblock-remove all           # Удалить рекламу
--sponsorblock-mark all             # Пометить главами
```

---

## Аутентификация

```bash
--cookies-from-browser chrome       # Cookies из Chrome
--cookies-from-browser firefox      # Cookies из Firefox
--cookies-from-browser edge         # Cookies из Edge
--cookies-from-browser brave        # Cookies из Brave
--cookies-from-browser chrome:Profile1  # Конкретный профиль

--cookies cookies.txt               # Cookies из файла
-u USERNAME -p PASSWORD             # Логин/пароль
--video-password PASSWORD           # Пароль к видео
```

---

## Сеть

```bash
--limit-rate 2M                     # Лимит скорости (2 МБ/с)
--limit-rate 500K                   # 500 КБ/с
-N 4                                # 4 потока (параллельно)
--proxy "http://host:port"          # HTTP прокси
--proxy "socks5://host:port"        # SOCKS5 прокси
--socket-timeout 30                 # Таймаут (сек)
--retries 10                        # Повторы
--fragment-retries 10               # Повторы фрагментов

# Внешний загрузчик
--downloader aria2c --downloader-args "-x 16 -k 1M"

# Гео-обход
--geo-bypass                        # Общий обход
--geo-bypass-country US             # Имитация из США

# Пауза между скачиваниями
--sleep-interval 5                  # Минимум 5 сек
--max-sleep-interval 15             # Максимум 15 сек
```

---

## Пакетная загрузка

```bash
yt-dlp -a urls.txt                  # Из файла со ссылками
yt-dlp -a urls.txt -i               # Пропускать ошибки
yt-dlp -a urls.txt --download-archive done.txt  # С архивом

# urls.txt формат:
# https://youtube.com/watch?v=xxx
# https://youtube.com/watch?v=yyy
# https://tiktok.com/@user/video/zzz
```

---

## Информация (без скачивания)

```bash
yt-dlp -F "URL"                     # Список форматов
yt-dlp -j --no-download "URL"       # JSON-информация
yt-dlp -g "URL"                     # Прямая ссылка
yt-dlp -e "URL"                     # Название видео
yt-dlp --get-filename "URL"         # Имя файла
yt-dlp --list-subs "URL"            # Доступные субтитры
yt-dlp -s "URL"                     # Симуляция
yt-dlp --list-extractors            # Все поддерживаемые сайты
yt-dlp -v "URL"                     # Подробный лог (debug)
```

---

## Готовые рецепты

### Видео максимального качества в MP4

```bash
yt-dlp -f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]" --merge-output-format mp4 --embed-metadata --embed-thumbnail --embed-chapters -P "D:/Downloads/YouTube/" "URL"
```

### Аудио-плейлист в MP3

```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 --embed-thumbnail --embed-metadata -o "%(playlist)s/%(playlist_index)02d - %(title)s.%(ext)s" --download-archive "D:/Downloads/YouTube/music-archive.txt" -P "D:/Downloads/YouTube/" "PLAYLIST_URL"
```

### Канал целиком

```bash
yt-dlp --download-archive "D:/Downloads/YouTube/channel-archive.txt" --sleep-interval 5 -o "%(uploader)s/%(upload_date>%Y-%m-%d)s - %(title)s.%(ext)s" -P "D:/Downloads/YouTube/" "https://youtube.com/@ChannelName"
```

### TikTok / Instagram

```bash
yt-dlp -P "D:/Downloads/YouTube/" "https://tiktok.com/@user/video/123"
yt-dlp --cookies-from-browser chrome -P "D:/Downloads/YouTube/" "https://instagram.com/reel/xxx/"
```

### Видео 18+ (с cookies)

```bash
yt-dlp --cookies-from-browser chrome -P "D:/Downloads/YouTube/" "URL"
```

### Стрим (запись с начала)

```bash
yt-dlp --live-from-start -P "D:/Downloads/YouTube/" "LIVE_URL"
```

### Видео по главам (отдельные файлы)

```bash
yt-dlp --split-chapters -o "%(title)s - %(chapter)s.%(ext)s" -P "D:/Downloads/YouTube/" "URL"
```

### Только фрагмент видео

```bash
yt-dlp --download-sections "*00:01:00-00:05:00" -P "D:/Downloads/YouTube/" "URL"
```

---

## Конфигурационный файл

**Windows:** `%APPDATA%\yt-dlp\config.txt`

```
-f bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]
--merge-output-format mp4
--embed-metadata
--embed-thumbnail
--embed-chapters
--embed-subs
--sub-lang ru,en
-o %(uploader)s/%(title)s.%(ext)s
-P D:/Downloads/YouTube/
--sleep-interval 3
--max-sleep-interval 10
--download-archive D:/Downloads/YouTube/.yt-dlp-archive.txt
```

---

## Алиасы для Git Bash / PowerShell

### Git Bash (~/.bashrc)

```bash
alias ydl='yt-dlp -P "/d/Downloads/YouTube/"'
alias ydl-mp4='yt-dlp -f "bv*[ext=mp4]+ba[ext=m4a]" --merge-output-format mp4 -P "/d/Downloads/YouTube/"'
alias ydl-mp3='yt-dlp -x --audio-format mp3 --audio-quality 0 -P "/d/Downloads/YouTube/"'
alias ydl-playlist='yt-dlp -o "%(playlist)s/%(playlist_index)02d - %(title)s.%(ext)s" -P "/d/Downloads/YouTube/"'
```

### PowerShell ($PROFILE)

```powershell
function ydl { yt-dlp -P "D:/Downloads/YouTube/" @args }
function ydl-mp4 { yt-dlp -f "bv*[ext=mp4]+ba[ext=m4a]" --merge-output-format mp4 -P "D:/Downloads/YouTube/" @args }
function ydl-mp3 { yt-dlp -x --audio-format mp3 --audio-quality 0 -P "D:/Downloads/YouTube/" @args }
```
