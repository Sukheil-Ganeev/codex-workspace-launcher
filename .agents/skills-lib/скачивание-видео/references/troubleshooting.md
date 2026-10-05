# yt-dlp — Решение проблем (Troubleshooting)

---

## Критическое правило

> **Первое действие при любой ошибке: обнови yt-dlp!**
> ```bash
> yt-dlp -U
> ```
> 90% проблем решаются обновлением. Сайты постоянно меняют API.

---

## 1. Ошибки установки и запуска

### "yt-dlp: command not found" / "не является внутренней командой"

**Причина:** yt-dlp не в PATH.

**Решение (Windows):**
1. Проверь, где установлен: `where yt-dlp` или `pip show yt-dlp`
2. Добавь путь в переменную окружения PATH:
   - Система -> Дополнительные параметры -> Переменные среды -> Path -> Изменить -> Добавить путь к yt-dlp.exe
3. Или укажи полный путь: `C:\путь\к\yt-dlp.exe "URL"`

**Решение (через pip):**
```bash
pip install -U yt-dlp
# Путь к Scripts добавить в PATH:
# C:\Users\londo\AppData\Local\...\Python313\Scripts\
```

---

### "FFmpeg not found" / "ffmpeg is not installed"

**Причина:** FFmpeg не установлен или не в PATH.

**Решение:**
1. Скачай с https://www.gyan.dev/ffmpeg/builds/ (Windows, полная сборка)
2. Извлеки `ffmpeg.exe`, `ffprobe.exe` в папку (например `C:\ffmpeg\bin\`)
3. Добавь `C:\ffmpeg\bin\` в PATH
4. Или укажи вручную: `--ffmpeg-location "C:\ffmpeg\bin\ffmpeg.exe"`
5. Проверь: `ffmpeg -version`

---

### "Python version 3.10+ required"

**Причина:** Старая версия Python.

**Решение:**
```bash
python --version   # Проверить
# Установить Python 3.10+ с python.org
pip install -U yt-dlp
```

---

## 2. Ошибки скачивания

### "ERROR: unable to extract" / "Unable to download webpage"

**Причина:** Устаревшая версия yt-dlp или сайт изменил API.

**Решение:**
```bash
# 1. Обновить
yt-dlp -U

# 2. Попробовать nightly (самый свежий код)
yt-dlp --update-to nightly

# 3. Проверить verbose лог
yt-dlp -v "URL"
```

---

### "HTTP Error 403: Forbidden"

**Причины и решения:**

1. **Геоблокировка:**
```bash
yt-dlp --geo-bypass "URL"
yt-dlp --geo-bypass-country US "URL"
yt-dlp --proxy "socks5://host:port" "URL"
```

2. **Нужна аутентификация:**
```bash
yt-dlp --cookies-from-browser chrome "URL"
```

3. **Бан по IP (массовое скачивание):**
```bash
# Добавить паузы
yt-dlp --sleep-interval 10 --max-sleep-interval 30 "URL"

# Использовать прокси
yt-dlp --proxy "http://host:port" "URL"
```

4. **Устаревшая версия:**
```bash
yt-dlp -U
```

---

### "HTTP Error 429: Too Many Requests"

**Причина:** Слишком много запросов за короткое время.

**Решение:**
```bash
# Увеличить паузу между скачиваниями
yt-dlp --sleep-interval 15 --max-sleep-interval 60 "URL"

# Ограничить скорость
yt-dlp --limit-rate 1M "URL"

# Подождать 10-30 минут и повторить
```

---

### "Video unavailable" / "This video is not available"

**Возможные причины:**
- Видео удалено
- Приватное видео (нужен доступ)
- Геоблокировка
- Возрастное ограничение

**Решения:**
```bash
# Геоблокировка
yt-dlp --geo-bypass-country US "URL"

# Возрастное ограничение
yt-dlp --cookies-from-browser chrome "URL"

# Приватное видео (если есть доступ)
yt-dlp --cookies-from-browser chrome "URL"
```

Если видео удалено — скачать невозможно.

---

### "Requested format not available"

**Причина:** Запрашиваемый формат не существует для этого видео.

**Решение:**
```bash
# 1. Посмотреть доступные форматы
yt-dlp -F "URL"

# 2. Использовать fallback
yt-dlp -f "bv*[height=1080]+ba/bv*[height=720]+ba/best" "URL"

# 3. Просто лучшее из доступного
yt-dlp -f best "URL"
```

---

### "Incomplete download" / файл скачан не полностью

**Решение:**
```bash
# Продолжить скачивание
yt-dlp -c "URL"

# Или удалить .part файл и скачать заново
yt-dlp --no-continue "URL"
```

---

### "Sign in to confirm you're not a bot"

**Причина:** YouTube требует аутентификацию (частая проблема 2025-2026).

**Решение:**
```bash
# Обязательно: cookies из браузера, где залогинен YouTube
yt-dlp --cookies-from-browser chrome "URL"

# Если Chrome не работает, попробуй Firefox
yt-dlp --cookies-from-browser firefox "URL"
```

---

## 3. Ошибки форматов и качества

### Видео без звука / аудио без видео

**Причина:** Скачан только один поток (video-only или audio-only).

**Решение:**
```bash
# Явно указать слияние
yt-dlp -f "bv*+ba" --merge-output-format mp4 "URL"
```

**Проверь:** Установлен ли FFmpeg? Без него слияние невозможно.

---

### Качество только 720p, хотя хочу 1080p+

**Причина:** Нет FFmpeg. YouTube хранит 1080p+ как раздельные потоки.

**Решение:**
1. Установить FFmpeg (см. выше)
2. Добавить в PATH
3. Скачать:
```bash
yt-dlp -f "bv*[height=1080]+ba" --merge-output-format mp4 "URL"
```

---

### Файл .webm вместо .mp4

**Причина:** YouTube хранит лучшее качество в WebM/VP9.

**Решение:**
```bash
# Указать MP4 форматы
yt-dlp -f "bv*[ext=mp4]+ba[ext=m4a]" --merge-output-format mp4 "URL"

# Или перемуксировать
yt-dlp --remux-video mp4 "URL"
```

---

### "Merging formats..." зависает или ошибка

**Причина:** Проблемы с FFmpeg.

**Решения:**
```bash
# 1. Проверить FFmpeg
ffmpeg -version

# 2. Указать путь явно
yt-dlp --ffmpeg-location "C:\ffmpeg\bin\" "URL"

# 3. Переустановить FFmpeg (скачать свежую сборку)

# 4. Попробовать MKV вместо MP4
yt-dlp --merge-output-format mkv "URL"
```

---

## 4. Ошибки с cookies

### "Cookies could not be extracted" / cookies не работают

**Возможные причины и решения:**

1. **Браузер открыт** — закрой браузер, попробуй снова
2. **Профиль зашифрован:**
```bash
# Указать конкретный профиль
yt-dlp --cookies-from-browser chrome:Default "URL"
yt-dlp --cookies-from-browser chrome:Profile1 "URL"
```

3. **Браузер обновился** — попробуй другой браузер:
```bash
yt-dlp --cookies-from-browser firefox "URL"
```

4. **Используй файл cookies:**
   - Установи расширение "Get cookies.txt LOCALLY"
   - Экспортируй cookies для нужного сайта
   - `yt-dlp --cookies cookies.txt "URL"`

---

### Cookies из Chrome не работают на Windows

**Причина:** Chrome шифрует cookies, и иногда yt-dlp не может их расшифровать.

**Решения:**
1. Попробуй Firefox: `--cookies-from-browser firefox`
2. Попробуй Edge: `--cookies-from-browser edge`
3. Экспортируй через расширение в файл: `--cookies cookies.txt`
4. Обнови yt-dlp до nightly: `yt-dlp --update-to nightly`

---

## 5. Ошибки с плейлистами

### Скачивается только одно видео из плейлиста

**Причина:** URL указывает на конкретное видео, а не на плейлист.

**Решение:**
```bash
# Убедись, что URL содержит list=
# Правильно: https://youtube.com/playlist?list=PLxxxx
# Неправильно: https://youtube.com/watch?v=xxx (одно видео)

# Если URL содержит и v= и list=, yt-dlp скачает видео
# Чтобы скачать плейлист:
yt-dlp --yes-playlist "URL"
```

---

### "Playlist does not exist"

**Решения:**
```bash
# 1. Проверить URL
# 2. Если приватный плейлист — нужны cookies
yt-dlp --cookies-from-browser chrome "PLAYLIST_URL"

# 3. Если плейлист удалён — невозможно скачать
```

---

### Нумерация плейлиста неправильная

**Решение:**
```bash
# Используй %(playlist_autonumber)s для автонумерации
-o "%(playlist)s/%(playlist_autonumber)03d - %(title)s.%(ext)s"
```

---

## 6. Ошибки сети

### Скачивание очень медленное

**Решения:**
```bash
# 1. Параллельные фрагменты
yt-dlp -N 4 "URL"

# 2. Внешний загрузчик aria2c
yt-dlp --downloader aria2c --downloader-args "-x 16 -k 1M" "URL"

# 3. Проверить: может быть rate limiting от сайта
# Некоторые сайты ограничивают скорость незалогиненным пользователям
yt-dlp --cookies-from-browser chrome "URL"
```

---

### "Connection timed out" / "Network unreachable"

**Решения:**
```bash
# 1. Увеличить таймаут
yt-dlp --socket-timeout 60 "URL"

# 2. Больше попыток
yt-dlp --retries 20 --fragment-retries 20 "URL"

# 3. Использовать прокси
yt-dlp --proxy "socks5://host:port" "URL"

# 4. Принудить IPv4
yt-dlp --force-ipv4 "URL"
```

---

### SSL/TLS ошибки

```bash
# Обойти проверку сертификата (НЕБЕЗОПАСНО, но работает)
yt-dlp --no-check-certificates "URL"

# Лучше: обновить certifi
pip install -U certifi
```

---

## 7. Ошибки с конкретными сайтами

### YouTube: "This video requires payment to watch"

Платное видео скачать нельзя без покупки. Если куплено — используй cookies:
```bash
yt-dlp --cookies-from-browser chrome "URL"
```

---

### Instagram: не скачивается

```bash
# Instagram требует cookies для большинства контента
yt-dlp --cookies-from-browser chrome "URL"

# Убедись, что залогинен в Instagram в этом браузере
```

---

### TikTok: "Unable to download video"

```bash
# 1. Обновить yt-dlp
yt-dlp -U

# 2. Использовать cookies
yt-dlp --cookies-from-browser chrome "URL"

# 3. Проверить URL (убрать лишние параметры)
```

---

### Twitter/X: ошибка скачивания

```bash
# Twitter часто меняет API. Обнови:
yt-dlp -U

# Используй cookies (для залогиненного контента)
yt-dlp --cookies-from-browser chrome "URL"
```

---

### Twitch: VOD не скачивается

```bash
# Subscriber-only VOD — нужны cookies
yt-dlp --cookies-from-browser chrome "URL"

# Клипы обычно работают без cookies
yt-dlp "https://clips.twitch.tv/xxx"
```

---

## 8. Ошибки постобработки

### "embed-thumbnail: mutagen not found"

**Решение:**
```bash
pip install mutagen
```

---

### "--embed-thumbnail" не работает для MP3

**Причина:** Нужен mutagen для MP3.

**Решение:**
```bash
pip install mutagen
yt-dlp -x --audio-format mp3 --embed-thumbnail "URL"
```

---

### SponsorBlock не работает

```bash
# 1. Проверить: доступна ли API
yt-dlp --sponsorblock-remove all -v "URL"

# 2. Обновить yt-dlp
yt-dlp -U

# 3. SponsorBlock работает только для YouTube (не для других сайтов)
```

---

## 9. Диагностика

### Общая диагностика

```bash
# Подробный лог (debug)
yt-dlp -v "URL"

# Проверить версии
yt-dlp --version
ffmpeg -version
python --version

# Симуляция (без скачивания)
yt-dlp -s "URL"

# JSON информация о видео
yt-dlp -j --no-download "URL"
```

### Лог в файл

```bash
yt-dlp -v "URL" 2>&1 | tee debug.log
```

---

## 10. Чек-лист при проблемах

1. **Обнови yt-dlp:** `yt-dlp -U`
2. **Проверь FFmpeg:** `ffmpeg -version`
3. **Попробуй verbose:** `yt-dlp -v "URL"`
4. **Попробуй cookies:** `--cookies-from-browser chrome`
5. **Проверь URL:** скопируй заново, без лишних параметров
6. **Попробуй другой формат:** `yt-dlp -f best "URL"`
7. **Попробуй nightly:** `yt-dlp --update-to nightly`
8. **Проверь интернет:** прокси / VPN / другая сеть
9. **Поищи issue:** https://github.com/yt-dlp/yt-dlp/issues

---

## 11. Типичные сообщения об ошибках (краткая таблица)

| Ошибка | Первое действие |
|--------|----------------|
| `unable to extract` | `yt-dlp -U` |
| `403 Forbidden` | cookies / прокси / обновление |
| `429 Too Many Requests` | подождать + `--sleep-interval` |
| `Video unavailable` | cookies / гео-обход / видео удалено |
| `Requested format not available` | `yt-dlp -F "URL"` посмотреть форматы |
| `FFmpeg not found` | установить FFmpeg, добавить в PATH |
| `Sign in to confirm` | `--cookies-from-browser chrome` |
| `Incomplete download` | `yt-dlp -c "URL"` (продолжить) |
| `Merging error` | проверить FFmpeg / `--merge-output-format mkv` |
| `command not found` | добавить yt-dlp в PATH |
| `mutagen not found` | `pip install mutagen` |
| `SSL error` | `--no-check-certificates` / обновить certifi |
| `Connection timeout` | `--socket-timeout 60 --retries 20` |
