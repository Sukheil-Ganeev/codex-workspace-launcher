# Python шаблоны для Yandex SpeechKit

Production-ready Python скрипты для транскрипции аудио в туристическом бизнесе.

## Доступные шаблоны

### 1. basic-transcription.py
**Базовая транскрипция через Sync API**

- Поддержка OGG Opus, MP3, WAV
- Error handling
- Docstrings на русском
- CLI интерфейс

**Использование:**
```bash
python basic-transcription.py audio.ogg
```

**Требования:**
```bash
pip install requests python-dotenv
```

**Когда использовать:**
- Короткие голосовые (до 30 сек)
- Простая разовая транскрипция
- Быстрое тестирование

---

### 2. long-audio-handler.py
**Обработчик длинных аудио файлов**

- Автоопределение длины (ffprobe)
- Деление на части по 29 сек
- Транскрипция каждой части
- Склеивание результата
- Cleanup временных файлов

**Использование:**
```bash
python long-audio-handler.py long_recording.mp3
```

**Требования:**
```bash
pip install ffmpeg-python tqdm requests python-dotenv
# + установленный ffmpeg в системе
```

**Когда использовать:**
- Аудио длиннее 30 секунд
- Долгие записи разговоров
- Лекции, презентации

---

### 3. batch-processing.py
**Пакетная обработка множества файлов**

- Рекурсивный поиск в папках
- Параллельная обработка (asyncio)
- Progress bar (tqdm)
- Экспорт в JSON/CSV
- Статистика обработки

**Использование:**
```bash
# JSON экспорт
python batch-processing.py /path/to/audio/folder

# CSV экспорт
python batch-processing.py /path/to/folder --format csv

# Кастомный вывод
python batch-processing.py /path/to/folder -o results.json -w 10
```

**Требования:**
```bash
pip install requests python-dotenv asyncio tqdm
```

**Когда использовать:**
- Обработка архива голосовых
- Массовая транскрипция
- Автоматизация рутинных задач

---

### 4. webhook-handler.py
**Webhook сервер (Flask)**

- REST API endpoints
- Signature verification
- Make.com / Zapier integration
- Health check endpoint

**Endpoints:**
- `POST /transcribe` - Загрузка файла
- `POST /transcribe-url` - Транскрипция по URL
- `GET /health` - Проверка сервиса

**Использование:**
```bash
# Разработка
python webhook-handler.py

# Продакшн
gunicorn -w 4 -b 0.0.0.0:5000 webhook-handler:app
```

**Требования:**
```bash
pip install flask requests python-dotenv
```

**Когда использовать:**
- Интеграция с Make.com
- Автоматизация через Zapier/n8n
- API для фронтенда

**Пример запроса (curl):**
```bash
curl -X POST http://localhost:5000/transcribe \
  -F "audio=@voice.ogg" \
  -F "language=ru-RU"
```

---

### 5. telegram-integration.py
**Telegram бот с транскрипцией**

- Обработка голосовых сообщений
- Команды (/start, /help, /stats)
- Статистика пользователя
- Логирование

**Использование:**
```bash
# 1. Создать бота через @BotFather
# 2. Добавить TELEGRAM_BOT_TOKEN в .env
python telegram-integration.py
```

**Требования:**
```bash
pip install python-telegram-bot requests python-dotenv
```

**Когда использовать:**
- Telegram бот для клиентов
- Автоответчик с транскрипцией
- Внутренний инструмент компании

---

### 6. whatsapp-parser.py
**Парсер WhatsApp экспорта**

- Парсинг _chat.txt
- Извлечение аудио (PTT-*.opus)
- Транскрипция каждого
- Замена в тексте чата
- Статистика

**Использование:**
```bash
python whatsapp-parser.py "WhatsApp Chat with Client"
```

**Требования:**
```bash
pip install requests python-dotenv
```

**Когда использовать:**
- Обработка истории чатов
- Анализ диалогов с клиентами
- Создание текстовых отчетов

**Структура экспорта:**
```
WhatsApp Chat with Name/
├── _chat.txt
├── PTT-20240115-WA0001.opus
├── PTT-20240115-WA0002.opus
└── ...
```

---

### 7. error-handler.py
**Надежная обработка ошибок**

- Retry с exponential backoff
- Circuit breaker pattern
- Fallback на OpenAI Whisper
- Детальное логирование
- Статистика провайдеров

**Использование:**
```python
from error_handler import RobustTranscriber

transcriber = RobustTranscriber(enable_fallback=True)
result = transcriber.transcribe("audio.ogg")

if result['success']:
    print(result['text'])
    print(f"Provider: {result['provider']}")  # yandex или whisper
```

**Требования:**
```bash
pip install requests python-dotenv
# + OPENAI_API_KEY для fallback
```

**Когда использовать:**
- Production окружение
- Критичные приложения
- Нужна 99% доступность

---

### 8. cost-optimizer.py
**Оптимизация стоимости**

- Выбор модели по контексту
- Файловый кеш результатов
- SQLite cost tracking
- Отчеты по стоимости
- Статистика по моделям

**Использование:**
```bash
# С контекстом
python cost-optimizer.py audio.ogg tourism

# Посмотреть отчет
python cost-optimizer.py audio.ogg general
```

**Контексты:**
- `tourism` - туризм, экскурсии (модель: general)
- `navigation` - навигация, маршруты (модель: maps)
- `general` - общий (модель: general)
- `research` - эксперименты (модель: general:rc)

**Требования:**
```bash
pip install requests python-dotenv
```

**Когда использовать:**
- Оптимизация бюджета
- Высокая нагрузка
- Нужна аналитика затрат

**Тарификация:**
- Sync API: 15₽ за 1 млн символов
- Кеш: бесплатно

---

## Общая настройка

### 1. Создайте `.env` файл:

```env
# Yandex Cloud
YANDEX_CLOUD_API_KEY=PASTE_YANDEX_CLOUD_API_KEY_HERE
YANDEX_CLOUD_FOLDER_ID=b1gvu3q8k1kafqd3sk5f

# Telegram (опционально)
TELEGRAM_BOT_TOKEN=your_bot_token

# OpenAI для fallback (опционально)
OPENAI_API_KEY=your_openai_key

# Webhook секрет (опционально)
WEBHOOK_SECRET=your_secret_key
```

### 2. Установите зависимости:

```bash
pip install requests python-dotenv
```

### 3. Для специфичных шаблонов:

```bash
# Long audio handler
pip install ffmpeg-python tqdm
sudo apt install ffmpeg  # или brew install ffmpeg

# Batch processing
pip install asyncio tqdm

# Webhook
pip install flask gunicorn

# Telegram
pip install python-telegram-bot
```

---

## Сравнение шаблонов

| Шаблон | Сложность | Длина аудио | Параллель | Интеграции |
|--------|-----------|-------------|-----------|------------|
| basic-transcription | Простая | До 30 сек | Нет | CLI |
| long-audio-handler | Средняя | Любая | Нет | CLI |
| batch-processing | Средняя | До 30 сек | Да | CLI, JSON/CSV |
| webhook-handler | Средняя | До 30 сек | Нет | HTTP API |
| telegram-integration | Средняя | До 30 сек | Нет | Telegram |
| whatsapp-parser | Средняя | До 30 сек | Нет | WhatsApp |
| error-handler | Высокая | До 30 сек | Нет | Python import |
| cost-optimizer | Высокая | До 30 сек | Нет | Python import |

---

## Быстрый старт

### Сценарий 1: Простая транскрипция одного файла
```bash
python basic-transcription.py voice.ogg
```

### Сценарий 2: Длинное аудио (5 минут)
```bash
python long-audio-handler.py recording.mp3
```

### Сценарий 3: Папка с 100 файлами
```bash
python batch-processing.py ./audio_folder -o results.csv --format csv
```

### Сценарий 4: Telegram бот
```bash
python telegram-integration.py
# Отправьте боту голосовое сообщение
```

### Сценарий 5: API сервер для Make.com
```bash
python webhook-handler.py
# Используйте http://localhost:5000/transcribe в Make.com
```

### Сценарий 6: Production с fallback
```python
from error_handler import RobustTranscriber

transcriber = RobustTranscriber(enable_fallback=True)
result = transcriber.transcribe("audio.ogg")
```

### Сценарий 7: Оптимизация затрат
```python
from cost_optimizer import OptimizedTranscriber

transcriber = OptimizedTranscriber(cache_enabled=True, track_costs=True)
result = transcriber.transcribe("audio.ogg", context="tourism")
transcriber.get_cost_report(days=30)
```

---

## Troubleshooting

### Ошибка: "Module not found"
```bash
pip install -r requirements.txt
```

### Ошибка: "API key not configured"
Создайте `.env` файл с ключами.

### Ошибка: "ffmpeg not found"
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Скачать с https://ffmpeg.org/download.html
```

### Ошибка: "File too large"
Используйте `long-audio-handler.py` для больших файлов.

### Ошибка: "Circuit breaker открыт"
Подождите 60 секунд или используйте fallback на Whisper.

---

## Поддержка

Все шаблоны протестированы и готовы к production использованию.

Для вопросов и доработок обращайтесь к документации скилла `yandex-speechkit-туризм`.
