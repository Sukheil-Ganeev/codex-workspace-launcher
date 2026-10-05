# Yandex SpeechKit - Production Examples

6 полных рабочих примеров интеграции Yandex SpeechKit для туристического бизнеса в ОАЭ.

## Обзор примеров

### 1. WhatsApp Voice Transcriber
**Путь:** `whatsapp-voice-transcriber/`

Обработка голосовых сообщений из экспорта WhatsApp чатов.

**Возможности:**
- Поддержка .opus, .ogg, .m4a, .mp3
- Обработка длинных аудио (>30 сек)
- Пакетная обработка
- Экспорт в JSON/CSV/TXT
- Подсчет стоимости

**Кейс использования:**
Клиент отправил 15 голосовых в WhatsApp группу ночью → утром экспортируете чат → скрипт обрабатывает все → получаете JSON с транскрипциями.

**Команда:**
```bash
cd whatsapp-voice-transcriber
pip install -r requirements.txt
python main.py --input whatsapp_export/ --output results.json
```

---

### 2. Telegram Bot Integration
**Путь:** `telegram-bot-integration/`

Production-ready Telegram бот для автоматической транскрипции голосовых.

**Возможности:**
- Polling и Webhook режимы
- SQLite база данных
- Статистика пользователей
- Админ панель
- Docker-ready

**Кейс использования:**
3 турагента отправляют по 20 голосовых в день → бот автоматически транскрибирует → вы читаете текст и быстро отвечаете.

**Команда:**
```bash
cd telegram-bot-integration
pip install -r requirements.txt
python main.py
```

**Docker:**
```bash
docker-compose up -d
```

---

### 3. Make.com Webhook
**Путь:** `make-com-webhook/`

FastAPI webhook сервер для интеграции с Make.com сценариями.

**Возможности:**
- REST API endpoint
- Обработка аудио по URL
- JSON response
- CORS support

**Кейс использования:**
WhatsApp Business API → Make.com → ваш webhook → транскрипция → Google Sheets → уведомление менеджеру.

**Команда:**
```bash
cd make-com-webhook
pip install -r requirements.txt
python main.py
```

**API:**
```bash
POST http://localhost:8000/transcribe
{
  "audio_url": "https://example.com/voice.ogg",
  "language": "ru-RU"
}
```

---

### 4. Batch Audio Processor
**Путь:** `batch-audio-processor/`

CLI инструмент для массовой обработки аудио файлов.

**Возможности:**
- Progress bar (tqdm)
- CSV/JSON экспорт
- Параллельная обработка
- Статистика (время, стоимость)
- Фильтрация по keywords

**Кейс использования:**
У вас папка с 100 голосовыми из разных источников → запускаете скрипт → получаете CSV таблицу со всеми транскрипциями.

**Команда:**
```bash
cd batch-audio-processor
pip install -r requirements.txt
python main.py --input audio_folder/ --output results.csv --format csv
```

---

### 5. Hybrid SpeechKit + Whisper
**Путь:** `hybrid-speechkit-whisper/`

Гибридный подход: SpeechKit для русского, Whisper для остальных языков.

**Возможности:**
- Автоопределение языка
- Fallback логика
- Сравнение качества
- Выбор лучшего движка

**Кейс использования:**
Смешанные клиенты (русские, англоговорящие, арабы) → скрипт автоматически выбирает лучший движок для каждого языка.

**Команда:**
```bash
cd hybrid-speechkit-whisper
pip install -r requirements.txt
python main.py --input audio.ogg --auto-detect
```

---

### 6. Multi-Language Detector
**Путь:** `multi-language-detector/`

Автоопределение языка аудио с транскрипцией на всех поддерживаемых языках.

**Возможности:**
- Параллельная транскрипция на 4 языках
- Confidence scoring
- Автоматический выбор лучшего результата
- Поддержка: русский, английский, арабский, турецкий

**Кейс использования:**
Неизвестно на каком языке говорит клиент → скрипт транскрибирует на всех языках параллельно → выбирает лучший результат.

**Команда:**
```bash
cd multi-language-detector
pip install -r requirements.txt
python main.py --input voice.ogg --verbose
```

---

## Быстрый старт

### 1. Получите API ключи

Зарегистрируйтесь в [Yandex Cloud](https://console.cloud.yandex.ru/):

1. Создайте каталог (Folder)
2. Получите API ключ для SpeechKit
3. Скопируйте Folder ID

### 2. Настройте .env

Каждый пример содержит `.env.example`:

```bash
cd <example-folder>
cp .env.example .env
nano .env
```

Заполните:
```env
YANDEX_API_KEY=PASTE_YANDEX_CLOUD_API_KEY_HERE
YANDEX_FOLDER_ID=b1gxxxxxxxxxxxxxxxxx
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Запустите

```bash
python main.py --help
```

---

## Сравнение примеров

| Пример | Сложность | Кейс | Деплой |
|--------|-----------|------|--------|
| WhatsApp Transcriber | Простая | Экспорт чатов | Локально |
| Telegram Bot | Средняя | Живой бот | VPS/Docker |
| Make.com Webhook | Средняя | Автоматизация | Cloud/Serverless |
| Batch Processor | Простая | Массовая обработка | Локально |
| Hybrid | Сложная | Мультиязычность | Локально/Cloud |
| Multi-Language | Сложная | Определение языка | Локально/Cloud |

---

## Стоимость

Yandex SpeechKit тарифы (февраль 2026):
- Короткие аудио (<30 сек): **0.2₽/мин**
- Длинные аудио (>30 сек): **0.5₽/мин**

**Примеры:**
- 100 голосовых по 30 сек/день = 50 мин = **10₽/день** = 300₽/месяц
- 500 голосовых по 20 сек/день = 167 мин = **33₽/день** = 1000₽/месяц
- 1000 голосовых по 15 сек/день = 250 мин = **50₽/день** = 1500₽/месяц

---

## Поддерживаемые форматы

Все примеры поддерживают:
- ✅ `.opus` (WhatsApp голосовые)
- ✅ `.ogg` (Telegram голосовые)
- ✅ `.m4a` (iPhone голосовые)
- ✅ `.mp3` (универсальный)
- ✅ `.wav` (без сжатия)
- ✅ `.flac` (lossless)

---

## Поддерживаемые языки

- 🇷🇺 Русский (ru-RU) - основной для СНГ
- 🇬🇧 Английский (en-US) - международные клиенты
- 🇦🇪 Арабский (ar-AE) - местные клиенты ОАЭ
- 🇹🇷 Турецкий (tr-TR) - турецкие туристы

---

## Технологии

Все примеры используют:
- **Python 3.8+**
- **Yandex SpeechKit API**
- **requests** для HTTP
- **python-dotenv** для конфигурации

Дополнительно:
- **FastAPI** (webhook)
- **python-telegram-bot** (Telegram)
- **tqdm** (progress bar)
- **OpenAI Whisper** (hybrid)

---

## Production Checklist

Перед деплоем в production:

- [ ] Храните .env в безопасности (не коммитьте в git)
- [ ] Используйте HTTPS для webhook endpoints
- [ ] Настройте rate limiting
- [ ] Мониторьте баланс Yandex Cloud
- [ ] Логируйте все транскрипции
- [ ] Создайте резервные копии базы данных
- [ ] Тестируйте на реальных голосовых из бизнеса
- [ ] Настройте алерты при ошибках

---

## Troubleshooting

### Ошибка API ключа
```
Error: Invalid API key
```
**Решение:** Проверьте `.env`, ключ должен начинаться с `AQVN`.

### FFmpeg не найден
```
Error: FFmpeg not installed
```
**Решение:** Установите FFmpeg и добавьте в PATH.

### Превышен лимит запросов
```
Error: Rate limit exceeded
```
**Решение:** Добавьте паузы между запросами (time.sleep(0.5)).

---

## Поддержка

При проблемах:
1. Проверьте README.md конкретного примера
2. Убедитесь что все зависимости установлены
3. Проверьте баланс Yandex Cloud
4. Проверьте логи (`--verbose` флаг)

---

## Лицензия

MIT License - свободное использование для вашего туристического бизнеса.

---

## Следующие шаги

1. Выберите нужный пример из списка выше
2. Откройте папку и прочитайте README.md
3. Настройте .env с вашими ключами
4. Запустите и тестируйте
5. Адаптируйте под ваш бизнес-процесс

**Успехов в автоматизации вашего туристического бизнеса в ОАЭ!**
