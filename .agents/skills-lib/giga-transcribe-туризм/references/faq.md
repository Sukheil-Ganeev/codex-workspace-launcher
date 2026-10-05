# FAQ — Yandex SpeechKit для туризма ОАЭ

> Часто задаваемые вопросы по транскрипции голосовых сообщений

---

## Основы API

### Q1: Какие форматы аудио поддерживаются?

**Поддерживаемые форматы:**
- **OGG Opus** (параметр `oggopus`) — WhatsApp, Telegram голосовые
- **MP3** (параметр `mp3`) — универсальный формат
- **WAV/LPCM** (параметр `lpcm`) — без сжатия, высокое качество
- **M4A** — через конвертацию в OGG/MP3

**Рекомендация:** Для WhatsApp/Telegram используйте OGG Opus напрямую (не нужна конвертация).

---

### Q2: Какой максимальный размер и длина файла?

**Синхронный API (Sync):**
- Размер: до 1 МБ
- Длительность: до 30 секунд
- **Критично:** 56% WhatsApp голосовых >30 сек, требуют специальной обработки

**Асинхронный API (Async):**
- Размер: до 1 ГБ
- Длительность: до 4 часов
- Формат: аудио должно быть в Cloud Storage (S3, Yandex Object Storage)

**Решение для длинных файлов:** См. `references/long-audio-handling.md`

---

### Q3: Как получить API ключ?

**Шаги:**
1. Откройте [Yandex Cloud Console](https://console.cloud.yandex.com)
2. Перейдите в **Сервисные аккаунты**
3. Выберите существующий или создайте новый
4. Нажмите **"Создать новый ключ"** → **"Создать API-ключ"**
5. Выберите разрешение: `yc.ai.speechkitStt.execute`
6. Скопируйте ключ (показывается только один раз!)

**Пример ключа:**
```
YANDEX_CLOUD_API_KEY=PASTE_YANDEX_CLOUD_API_KEY_HERE
```

---

### Q4: Что такое Folder ID и где его взять?

**Folder ID** — это идентификатор каталога в Yandex Cloud, куда относятся ваши ресурсы.

**Где найти:**
1. [Yandex Cloud Console](https://console.cloud.yandex.com)
2. Выберите каталог (обычно называется "default")
3. В адресной строке: `.../?folder_id=b1gvu3q8k1kafqd3sk5f`
4. Или на странице каталога: "Идентификатор каталога"

**Наш Folder ID:**
```
YANDEX_CLOUD_FOLDER_ID=b1gvu3q8k1kafqd3sk5f
```

---

### Q5: Какие языки поддерживаются?

| Язык | Код | Туристический контекст ОАЭ |
|------|-----|---------------------------|
| Русский | `ru-RU` | **Основной** — 80% клиентов СНГ |
| Английский | `en-US` | Европейцы, арабы (второй язык) |
| Арабский | `ar-AE` | Местные жители, эмираты |
| Турецкий | `tr-TR` | Туристы из Турции |
| Казахский | `kk-KK` | Клиенты из Казахстана |
| Узбекский | `uz-UZ` | Клиенты из Узбекистана |

**Автоопределение языка:** См. `references/language-detection.md`

---

## Использование API

### Q6: Как транскрибировать короткое аудио (<30 сек)?

**Код:**
```python
import requests
import os

response = requests.post(
    "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
    params={
        "folderId": os.getenv("YANDEX_CLOUD_FOLDER_ID"),
        "lang": "ru-RU",
        "format": "oggopus",
        "sampleRateHertz": 48000
    },
    headers={
        "Authorization": f"Api-Key {os.getenv('YANDEX_CLOUD_API_KEY')}"
    },
    data=open("voice.ogg", "rb")
)

text = response.json().get("result", "")
print(text)
```

**Шаблон:** `assets/templates/basic-transcription.py`

---

### Q7: Как обработать длинное аудио (>30 сек)?

**Проблема:** Sync API имеет лимит 30 секунд, но 56% WhatsApp голосовых превышают этот лимит.

**Решение 1 — Деление на части (рекомендуется):**
```python
import subprocess
import math

def transcribe_long_audio(audio_path: str) -> str:
    duration = get_audio_duration(audio_path)

    if duration <= 29:
        return transcribe_direct(audio_path)

    # Делим на части по 29 сек
    num_chunks = math.ceil(duration / 29.0)
    transcripts = []

    for i in range(num_chunks):
        chunk_path = f"{audio_path}_chunk_{i:03d}.ogg"
        subprocess.run([
            'ffmpeg', '-i', audio_path,
            '-ss', str(i * 29),
            '-t', '29',
            '-c', 'copy',  # БЕЗ перекодирования (быстро!)
            chunk_path, '-y'
        ])

        text = transcribe_direct(chunk_path)
        transcripts.append(text)
        os.remove(chunk_path)

    return " ".join(transcripts)
```

**Шаблон:** `assets/templates/long-audio-handler.py`
**Детали:** `references/long-audio-handling.md`

---

### Q8: Как автоматически определить язык?

**Метод:** Попробовать транскрибировать с разными языками, выбрать лучший результат.

```python
def transcribe_auto_detect(audio_path: str) -> dict:
    languages = ["ru-RU", "en-US", "ar-AE"]
    results = []

    for lang in languages:
        try:
            text = transcribe_speechkit(audio_path, lang)
            if text.strip():
                results.append({
                    "language": lang,
                    "text": text,
                    "confidence": estimate_confidence(text, lang)
                })
        except Exception:
            continue

    # Выбираем результат с максимальной уверенностью
    if results:
        return max(results, key=lambda x: x["confidence"])

    return {"language": "unknown", "text": "", "confidence": 0}
```

**Пример:** `assets/examples/multi-language-detector/`

---

### Q9: Как улучшить качество распознавания?

**Рекомендации:**

1. **Качество аудио:**
   - Минимум шума в фоне
   - Чёткая речь (не быстрая)
   - Sample rate 48000 Hz (для Opus)

2. **Выбор правильного языка:**
   - Не угадывайте — лучше автодетект
   - Для туристов СНГ → ru-RU

3. **Модель распознавания:**
   - `general` — универсальная (по умолчанию)
   - `numbers` — для цен, дат
   - `phone` — для номеров телефонов

4. **Пост-обработка:**
   - Коррекция туристических терминов
   - См. секцию "Словарь для улучшения" в SKILL.md

---

### Q10: Сколько стоит транскрипция?

**Цены Yandex SpeechKit:**
| Операция | Цена (руб) | Цена (USD) |
|----------|-----------|-----------|
| Синхронное распознавание | 0.80 руб / 15 сек | ~$0.01 / мин |
| Асинхронное распознавание | 0.48 руб / 15 сек | ~$0.006 / мин |
| Streaming распознавание | 0.96 руб / 15 сек | ~$0.012 / мин |

**Сравнение с Whisper API:**
- Whisper: $0.006/мин (дешевле на 40%)
- Но SpeechKit лучше для русского языка

**Калькулятор:** `scripts/cost-calculator.py`

---

## Интеграции

### Q11: Как интегрировать с WhatsApp?

**Вариант 1 — WhatsApp парсер:**
1. Экспортируйте чат из WhatsApp
2. Используйте `whatsapp-парсер` скилл для извлечения аудио
3. Транскрибируйте через SpeechKit
4. Замените в тексте чата

**Вариант 2 — WhatsApp Business API:**
- Webhook получает голосовые сообщения
- Скачивает аудио
- Транскрибирует
- Отправляет текст обратно

**Шаблон:** `assets/templates/whatsapp-parser.py`
**Пример:** `assets/examples/whatsapp-voice-transcriber/`

---

### Q12: Как интегрировать с Telegram ботом?

**Код:**
```python
from telegram import Update
from telegram.ext import Application, MessageHandler, filters

async def handle_voice(update: Update, context):
    voice = update.message.voice

    # Скачиваем файл
    file = await voice.get_file()
    audio_path = f"temp_{voice.file_id}.ogg"
    await file.download_to_drive(audio_path)

    # Транскрибируем
    text = transcribe_speechkit(audio_path, "ru-RU")

    # Отправляем результат
    await update.message.reply_text(f"Распознано: {text}")

    os.remove(audio_path)

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
app.run_polling()
```

**Пример:** `assets/examples/telegram-bot-integration/`

---

### Q13: Как интегрировать с Make.com?

**Webhook модуль:**
1. Make.com → HTTP Webhook (Custom)
2. URL: `https://your-function.netlify.app/.netlify/functions/transcribe`
3. Method: POST
4. Body: `{"audio_url": "https://..."}`

**Netlify Function:**
```javascript
exports.handler = async (event) => {
  const { audio_url } = JSON.parse(event.body);

  // Скачиваем аудио
  const audioBuffer = await fetch(audio_url).then(r => r.arrayBuffer());

  // Транскрибируем через SpeechKit
  const text = await transcribeSpeechKit(audioBuffer);

  return {
    statusCode: 200,
    body: JSON.stringify({ text })
  };
};
```

**Пример:** `assets/examples/make-com-webhook/`

---

### Q14: Какая разница между Sync, Async и Streaming API?

| Параметр | Sync API | Async API | Streaming API |
|----------|----------|-----------|---------------|
| **Лимит длины** | 30 сек | 4 часа | Неограничено |
| **Размер файла** | 1 МБ | 1 ГБ | N/A (stream) |
| **Латенция** | < 1 сек | 30 сек - 5 мин | Real-time |
| **Результат** | Сразу | Асинхронно (poll) | По мере говорения |
| **Использование** | Короткие голосовые | Длинные аудио | Live транскрипция |
| **Стоимость** | 0.80 руб/15сек | 0.48 руб/15сек | 0.96 руб/15сек |

**Рекомендация для туризма:**
- **WhatsApp/Telegram голосовые** → Sync API + деление на части (если >30 сек)
- **Записи переговоров** → Async API
- **Live support чат** → Streaming API

**Детали:** `references/sync-vs-async.md`

---

## Сравнения

### Q15: SpeechKit vs Whisper — что выбрать?

| Критерий | SpeechKit | Whisper API |
|----------|-----------|-------------|
| **Русский язык** | ⭐⭐⭐⭐⭐ Отлично | ⭐⭐⭐⭐ Очень хорошо |
| **Английский** | ⭐⭐⭐⭐ Очень хорошо | ⭐⭐⭐⭐⭐ Отлично |
| **Арабский** | ⭐⭐⭐ Хорошо | ⭐⭐⭐⭐ Очень хорошо |
| **Streaming** | ✅ Да | ❌ Нет |
| **Max длина** | 30 сек (Sync) | 25 МБ файл |
| **Стоимость** | $0.01/мин | $0.006/мин |
| **Латенция** | < 1 сек | 3-5 сек |
| **Туристические термины (рус)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**Когда использовать SpeechKit:**
- Клиент говорит на русском
- Нужен streaming (real-time)
- Важна скорость отклика

**Когда использовать Whisper:**
- Клиент говорит на английском/арабском
- Нужна мультиязычность
- Важна экономия (на 40% дешевле)

**Гибридный подход:** `assets/examples/hybrid-speechkit-whisper/`

---

### Q16: Локальный Whisper vs API — что быстрее?

| Метод | Скорость | Стоимость | Качество |
|-------|---------|-----------|----------|
| **SpeechKit API** | ⚡ < 1 сек | $ платно | ⭐⭐⭐⭐⭐ |
| **Whisper API** | ⚡ 3-5 сек | $ платно | ⭐⭐⭐⭐⭐ |
| **Whisper локально (CPU)** | 🐌 20-40 сек | 🆓 бесплатно | ⭐⭐⭐⭐⭐ |
| **faster-whisper (GPU)** | ⚡ 2-5 сек | 🆓 бесплатно | ⭐⭐⭐⭐⭐ |

**Рекомендация:**
- **Малый объём (<100 файлов/день)** → API (проще)
- **Большой объём (>1000 файлов/день)** → Локально на GPU (экономия)

---

## Ошибки и решения

### Q17: Ошибка 401 Unauthorized

**Проблема:** Неверный API ключ или не указан Folder ID.

**Решение:**
1. Проверьте API ключ:
   ```bash
   echo $YANDEX_CLOUD_API_KEY
   ```
2. Проверьте Folder ID:
   ```bash
   echo $YANDEX_CLOUD_FOLDER_ID
   ```
3. Убедитесь, что ключ имеет разрешение `yc.ai.speechkitStt.execute`

---

### Q18: Ошибка 429 Rate Limit Exceeded

**Проблема:** Превышен лимит запросов (20 запросов в секунду).

**Решение:**
```python
import time
from functools import wraps

def rate_limit(max_per_second=10):
    min_interval = 1.0 / max_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed

            if left_to_wait > 0:
                time.sleep(left_to_wait)

            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

@rate_limit(max_per_second=10)
def transcribe_with_rate_limit(audio_path):
    return transcribe_speechkit(audio_path)
```

---

### Q19: Ошибка: файл слишком большой (>1 МБ)

**Проблема:** Sync API принимает файлы до 1 МБ.

**Решение 1 — Сжатие:**
```bash
ffmpeg -i input.ogg -c:a libopus -b:a 16k output.ogg
```

**Решение 2 — Async API:**
Загрузите файл в Yandex Object Storage, используйте Async API.

**Решение 3 — Деление на части:**
См. Q7.

---

### Q20: Плохое качество распознавания

**Проблема:** Много ошибок в тексте.

**Возможные причины и решения:**

1. **Неправильный язык:**
   - Используйте автодетект (Q8)
   - Проверьте, соответствует ли язык речи

2. **Плохое качество аудио:**
   - Много шума → используйте noise reduction (ffmpeg)
   - Слишком тихо → нормализуйте громкость

3. **Неправильный формат:**
   - WhatsApp OGG → используйте `format=oggopus`
   - MP3 → используйте `format=mp3`

4. **Специфические термины:**
   - Используйте пост-коррекцию (см. SKILL.md секция "Словарь")

---

## Оптимизация

### Q21: Как ускорить обработку множества файлов?

**Последовательная обработка (медленно):**
```python
for audio in audio_files:
    text = transcribe(audio)  # 1 сек каждый
# Итого: 100 файлов = 100 секунд
```

**Параллельная обработка (быстро):**
```python
import asyncio
import aiohttp

async def transcribe_async(audio):
    async with aiohttp.ClientSession() as session:
        # Async запрос к API
        ...

# Обрабатываем 10 файлов параллельно
results = await asyncio.gather(*[
    transcribe_async(audio) for audio in audio_files
])
# Итого: 100 файлов = ~10 секунд (10× быстрее!)
```

**Шаблон:** `assets/templates/batch-processing.py`

---

### Q22: Как кешировать результаты?

**Зачем:** Избежать повторной транскрипции одного и того же файла.

```python
import hashlib
import json

CACHE_FILE = "transcription_cache.json"

def get_audio_hash(audio_path):
    with open(audio_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def transcribe_with_cache(audio_path):
    audio_hash = get_audio_hash(audio_path)

    # Проверяем кеш
    cache = json.load(open(CACHE_FILE)) if os.path.exists(CACHE_FILE) else {}

    if audio_hash in cache:
        print(f"✓ Взято из кеша: {audio_path}")
        return cache[audio_hash]

    # Транскрибируем
    text = transcribe_speechkit(audio_path)

    # Сохраняем в кеш
    cache[audio_hash] = text
    json.dump(cache, open(CACHE_FILE, "w"))

    return text
```

**Экономия:** До 90% запросов при повторной обработке.

---

### Q23: Как посчитать стоимость транскрипции?

```python
def calculate_cost(audio_duration_seconds, api_type="sync"):
    # Цены за 15 секунд (в рублях)
    prices = {
        "sync": 0.80,
        "async": 0.48,
        "streaming": 0.96
    }

    # Округляем до 15 секунд вверх
    import math
    segments = math.ceil(audio_duration_seconds / 15.0)

    cost_rub = segments * prices[api_type]
    cost_usd = cost_rub / 95  # Курс ~95 руб/USD

    return {
        "duration": audio_duration_seconds,
        "segments": segments,
        "cost_rub": round(cost_rub, 2),
        "cost_usd": round(cost_usd, 4)
    }

# Пример
print(calculate_cost(45, "sync"))
# {'duration': 45, 'segments': 3, 'cost_rub': 2.4, 'cost_usd': 0.0253}
```

**Скрипт:** `scripts/cost-calculator.py`

---

## Туристический контекст

### Q24: Какие термины часто неправильно распознаются?

**Туристические термины ОАЭ:**

| Говорят | SpeechKit слышит | Правильно |
|---------|-----------------|-----------|
| Бурдж Халифа | бурч халифа, бурж халифа | Burj Khalifa |
| Феррари Ворлд | феррари ворлд | Ferrari World |
| Дубай Молл | дубай молл | Dubai Mall |
| Абу-Даби | абудаби | Абу-Даби |
| Сафари | саффари | сафари |
| Дирхам | дирхамы, дирхамов | AED |

**Решение — пост-коррекция:**
```python
def correct_tourism_terms(text: str) -> str:
    corrections = {
        "бурч халифа": "Burj Khalifa",
        "бурж халифа": "Burj Khalifa",
        "феррари ворлд": "Ferrari World",
        "дубай молл": "Dubai Mall",
        "абудаби": "Абу-Даби",
        "саффари": "сафари"
    }

    result = text.lower()
    for wrong, correct in corrections.items():
        result = result.replace(wrong, correct)

    return result
```

---

### Q25: Как обработать голосовые из WhatsApp группы?

**Сценарий:** У вас экспорт группы с агентами, нужно транскрибировать все голосовые.

**Шаги:**
1. Экспортируйте чат из WhatsApp
2. Используйте `whatsapp-парсер` скилл:
   ```python
   from whatsapp_parser import parse_chat, extract_audio

   chat = parse_chat("WhatsApp Chat.txt")
   audio_files = extract_audio(chat, media_folder="_chat/")
   ```

3. Транскрибируйте все аудио:
   ```python
   for audio in audio_files:
       text = transcribe_any_audio(audio.path)
       print(f"{audio.sender} ({audio.date}): {text}")
   ```

**Пример:** `assets/examples/whatsapp-voice-transcriber/`

---

### Q26: Как отправить транскрипцию обратно клиенту?

**Вариант 1 — Telegram:**
```python
await bot.send_message(
    chat_id=client_telegram_id,
    text=f"Распознано ваше голосовое сообщение:\n\n{text}"
)
```

**Вариант 2 — WhatsApp (через Twilio):**
```python
from twilio.rest import Client

client = Client(account_sid, auth_token)
message = client.messages.create(
    from_='whatsapp:+14155238886',
    body=f'Распознано: {text}',
    to=f'whatsapp:{client_phone}'
)
```

**Вариант 3 — Email:**
```python
import smtplib
from email.mime.text import MIMEText

msg = MIMEText(f"Транскрипция вашего голосового:\n\n{text}")
msg['Subject'] = 'Ваше голосовое сообщение'
msg['From'] = 'support@dubai-tours.ae'
msg['To'] = client_email

smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.starttls()
smtp.login(email_user, email_password)
smtp.send_message(msg)
smtp.quit()
```

---

## Связанные скиллы

### Q27: Какие скиллы использовать вместе с giga-transcribe-туризм?

**Workflow транскрипции запросов клиентов:**

```
1. whatsapp-парсер
   ↓ Извлекаем голосовые из WhatsApp экспорта

2. giga-transcribe-туризм (ВЫ ЗДЕСЬ)
   ↓ Транскрибируем в текст

3. обработка-запросов-турагентов
   ↓ Анализируем запрос, определяем тур/дату/кол-во людей

4. создание-карточек-каталога
   ↓ Формируем ответ с предложениями туров

5. vip-dxb-rus-telegram-bot
   ↓ Отправляем ответ клиенту в Telegram
```

**Связанные скиллы:**
- `whatsapp-парсер` — извлечение аудио из чатов
- `обработка-запросов-турагентов` — анализ транскрибированного текста
- `vip-dxb-rus-telegram-bot` — отправка результата
- `туризм-оаэ-автоматизация` — общая автоматизация

---

### Q28: Как записать опыт использования в experience/?

**После исправления ошибки или нахождения улучшения:**

```bash
# 1. Создайте файл в experience/fixes/ или experience/improvements/
cd C:/Users/londo/.claude/skills/giga-transcribe-туризм/experience/

# 2. Исправление ошибки
echo "## Проблема: ffmpeg -c copy не работает с MP3
Решение: использовать -c:a copy только для OGG Opus
Дата: 2026-02-05" > fixes/2026-02-05-ffmpeg-mp3.md

# 3. Обновите _index.md с критическим уроком
```

**См. протокол:** `C:/Users/londo/.claude/skills/_experience-system/EXPERIENCE_PROTOCOL.md`

---

### Q29: Где найти больше примеров кода?

**Расположение ресурсов:**

```
C:/Users/londo/.claude/skills/giga-transcribe-туризм/
├── SKILL.md                    # Главный справочник
├── references/
│   ├── speechkit-basics.md     # Основы API
│   ├── long-audio-handling.md  # Длинные аудио
│   ├── integrations.md         # Интеграции
│   └── ...
├── assets/
│   ├── templates/              # 8 готовых шаблонов
│   │   ├── basic-transcription.py
│   │   ├── long-audio-handler.py
│   │   └── ...
│   └── examples/               # 6 полных примеров
│       ├── whatsapp-voice-transcriber/
│       ├── telegram-bot-integration/
│       └── ...
└── scripts/                    # 6 автоматизационных скриптов
    ├── validate-audio.py
    ├── batch-transcribe.py
    └── ...
```

**Быстрый доступ:**
- Шаблоны для копирования: `assets/templates/`
- Рабочие примеры: `assets/examples/`
- Automation: `scripts/`

---

### Q30: Куда писать вопросы и предложения?

**Обратная связь:**
1. **Experience система:** Запишите в `experience/` папку
2. **GitHub Issues:** (если скилл в репозитории)
3. **Прямой контакт:** Сухейль, VIP Dubai Tours

**Полезные команды:**
```bash
# Показать опыт скилла
ls C:/Users/londo/.claude/skills/giga-transcribe-туризм/experience/

# Записать новый опыт
echo "Ваш урок" > experience/improvements/название.md
```

---

## Дополнительные ресурсы

- **Официальная документация:** https://cloud.yandex.ru/docs/speechkit/
- **API Reference:** https://cloud.yandex.ru/docs/speechkit/stt/api/request-api
- **Примеры от Yandex:** https://github.com/yandex-cloud/docs/tree/master/ru/speechkit
- **Наш SKILL.md:** Главный справочник с деталями
- **Другие справочники:** `javascript-nodejs-справочник`, `html-css-справочник`, `api-туризм-оаэ`

---

**Последнее обновление:** 2026-02-05
**Версия FAQ:** 2.0 Extended Edition
**Скилл:** giga-transcribe-туризм
