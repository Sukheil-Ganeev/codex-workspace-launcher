# Оптимальные настройки OBS по сценариям — Полные конфигурации

> Перенесено из SKILL.md (секция 6). Полные конфиги с объяснениями.

---

## 6.1 Скринкасты и туториалы

Главное: читаемый текст, маленький файл, плавная запись.

```
=== OBS Settings ===

Output → Recording:
  Encoder:        NVIDIA NVENC H.264 (или x264 CRF)
  Rate Control:   CQP (NVENC) / CRF (x264)
  CQP/CRF:       20
  Preset:         P5 Quality (NVENC) / veryfast (x264)
  Profile:        high

Video:
  Base:           1920×1080
  Output:         1920×1080
  FPS:            30

Audio:
  Sample Rate:    48 kHz
  Encoder:        AAC
  Bitrate:        160 kbps

Recording Format:  MKV
```

**Ожидаемый размер:** ~30-50 МБ/минута

**Почему 30 FPS:** для скринкастов 60 FPS не нужен — текст и UI не требуют
плавности. 30 FPS экономит 40-50% размера файла.

**Почему CQP/CRF 20:** оптимальный баланс. Текст в IDE/браузере остаётся чётким.
Если нужно ещё лучше — 18. Если файл слишком большой — 22.

**Советы для скринкастов:**
- Увеличьте шрифт в IDE/терминале до 14-16pt перед записью
- Используйте тёмную тему (меньше шума → меньше размер файла)
- Закройте уведомления и лишние окна
- Включите подсветку курсора (Settings → Accessibility или плагин)

---

## 6.2 Геймплей

Главное: плавность, качество при быстром движении, минимальная нагрузка на CPU.

```
=== OBS Settings ===

Output → Recording:
  Encoder:        NVIDIA NVENC H.264
  Rate Control:   CQP
  CQP:            18
  Preset:         P5 Quality
  Profile:        high
  B-Frames:       2
  Look-ahead:     On

Video:
  Base:           1920×1080
  Output:         1920×1080
  FPS:            60

Audio:
  Sample Rate:    48 kHz
  Encoder:        AAC
  Bitrate:        192 kbps

Recording Format:  MKV
```

**Ожидаемый размер:** ~80-120 МБ/минута

**Почему 60 FPS:** игры выигрывают от плавности. 60 FPS делает быстрые
сцены смотрибельными.

**Почему CQP 18:** быстрое движение в играх требует больше бит для сохранения
чёткости. CQP 18 гарантирует качество в экшн-сценах.

**Советы для геймплея:**
- NVENC обязателен — x264 отнимет FPS у игры
- Используй Game Capture, не Display Capture (эффективнее)
- Включи Instant Replay в OBS (Settings → General → Replay Buffer)
- Для 4K-игр: записывай в 1080p (Output downscale) — YouTube всё равно пережмёт

---

## 6.3 Стриминг (Twitch / YouTube)

Главное: стабильный битрейт, совместимость с платформой, низкая задержка.

**Twitch:**

```
Output → Streaming:
  Encoder:        NVIDIA NVENC H.264
  Rate Control:   CBR
  Bitrate:        6000 kbps (Twitch Partner)
                  4500 kbps (Twitch Affiliate)
                  3500 kbps (стандарт)
  Keyframe:       2 (обязательно для Twitch)
  Preset:         P5 Quality (NVENC) / veryfast (x264)
  Profile:        high (или main)
  B-Frames:       2

Video:
  Base:           1920×1080
  Output:         1920×1080 (при 6000 kbps) или 1280×720 (при 3500 kbps)
  FPS:            60 (или 30 при низком битрейте)

Audio:
  Encoder:        AAC
  Bitrate:        160 kbps
```

**YouTube Live:**

```
Bitrate:        6000-9000 kbps (YouTube более лоялен к высокому битрейту)
Keyframe:       2
Остальное:      как для Twitch
```

**Одновременная запись и стрим:**

```
Output → Recording:
  Используй отдельные настройки (Output Mode: Advanced)
  Encoder:      NVENC CQP 20 (для записи)
  Format:       MKV

Output → Streaming:
  Encoder:      NVENC CBR 6000 (для стрима)
```

На RTX картах два NVENC-чипа — можно кодировать стрим и запись параллельно.

---

## 6.4 Запись для монтажа (Production Quality)

Главное: максимальное качество, гибкость в постобработке.

```
=== OBS Settings ===

Output → Recording:
  Encoder:        x264 (для максимального контроля)
  Rate Control:   CRF
  CRF:            16
  Preset:         faster (или fast, если CPU позволяет)
  Profile:        high

Video:
  Base:           2560×1440 (или разрешение монитора)
  Output:         2560×1440
  FPS:            30 (или 60 для динамичного контента)

Audio:
  Sample Rate:    48 kHz
  Encoder:        PCM (несжатый) или FLAC
  Или AAC 320 kbps если PCM слишком большой

Recording Format:  MKV
```

**Ожидаемый размер:** ~150-300 МБ/минута (с PCM аудио — ещё больше)

**Почему CRF 16:** минимальные потери, максимум деталей для цветокоррекции
и кропа при монтаже.

**Почему x264:** при CRF 16 даёт лучшее качество на бит, чем NVENC.
Для продакшн-записи качество важнее нагрузки на CPU.

**Почему PCM:** несжатый звук для монтажа — без артефактов при
многократной обработке.

**Советы:**
- Записывай в 1440p, даже если финальный продукт 1080p — запас для кропа и zoom
- Разделяй аудиодорожки (микрофон, desktop, музыка — отдельно)
- Используй MKV → Remux в MOV для Final Cut / MP4 для Premiere
