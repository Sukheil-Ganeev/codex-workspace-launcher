# WhatsApp Voice Transcriber

Обработка голосовых сообщений из экспорта WhatsApp чатов для туристического бизнеса.

## Описание

Этот инструмент автоматически обрабатывает голосовые сообщения из экспортированных WhatsApp чатов (включая файлы `.opus`), транскрибирует их через Yandex SpeechKit и сохраняет результаты в JSON.

### Основные возможности

- Поддержка `.opus`, `.ogg`, `.m4a`, `.mp3` форматов
- Автоматическая конвертация в нужный формат
- Обработка длинных аудио (>30 сек) через Streaming API
- Пакетная обработка всех голосовых из экспорта
- Экспорт с метаданными (дата, отправитель, длительность)
- Подсчет стоимости транскрипции

### Реальный кейс

**Ситуация:** Клиент отправил 15 голосовых в WhatsApp группу с вопросами про экскурсии, пока вы спали.

**Решение:** Экспортируйте чат, запустите скрипт — получите все транскрипции в JSON для быстрого ответа.

## Установка

### 1. Установите зависимости

```bash
cd C:/Users/londo/.claude/skills/giga-transcribe-туризм/assets/examples/whatsapp-voice-transcriber
pip install -r requirements.txt
```

### 2. Установите FFmpeg (для конвертации .opus)

**Windows:**
```bash
# Скачайте с https://ffmpeg.org/download.html
# Или через Chocolatey:
choco install ffmpeg
```

**Linux/Mac:**
```bash
sudo apt install ffmpeg  # Debian/Ubuntu
brew install ffmpeg      # macOS
```

### 3. Настройте .env

Скопируйте `.env.example` в `.env` и добавьте ваши ключи:

```bash
cp .env.example .env
```

Заполните:
```env
YANDEX_API_KEY=PASTE_YANDEX_CLOUD_API_KEY_HERE
YANDEX_FOLDER_ID=b1gxxxxxxxxxxxxxxxxx
```

## Использование

### Экспорт чата из WhatsApp

1. Откройте чат в WhatsApp
2. Меню (⋮) → Еще → Экспортировать чат
3. Выберите "С медиафайлами"
4. Сохраните в папку `whatsapp_export/`

### Запуск обработки

```bash
# Обработать все голосовые из экспорта
python main.py --input whatsapp_export/

# Указать конкретные файлы
python main.py --input whatsapp_export/PTT-20240215-WA0001.opus whatsapp_export/PTT-20240215-WA0002.opus

# Сохранить результат в конкретный файл
python main.py --input whatsapp_export/ --output results.json

# Включить детальные логи
python main.py --input whatsapp_export/ --verbose
```

### Формат вывода

Результат сохраняется в `transcriptions.json`:

```json
{
  "total_files": 5,
  "successful": 5,
  "failed": 0,
  "total_duration_seconds": 127.5,
  "estimated_cost_rubles": 0.64,
  "transcriptions": [
    {
      "file": "PTT-20240215-WA0001.opus",
      "sender": "Client Name",
      "timestamp": "2024-02-15 14:30:22",
      "duration_seconds": 18.5,
      "text": "Привет, хотел узнать сколько стоит экскурсия в Абу-Даби на целый день?",
      "confidence": 0.95,
      "language": "ru-RU",
      "status": "success"
    }
  ]
}
```

## Примеры использования

### Python API

```python
from whatsapp_transcriber import WhatsAppTranscriber

# Инициализация
transcriber = WhatsAppTranscriber(
    api_key="your_api_key",
    folder_id="your_folder_id"
)

# Обработка одного файла
result = transcriber.transcribe_file("voice.opus")
print(result['text'])

# Пакетная обработка
results = transcriber.transcribe_folder("whatsapp_export/")
print(f"Обработано: {results['successful']}/{results['total_files']}")
```

### Интеграция с бизнес-процессом

```python
# Фильтрация по ключевым словам
results = transcriber.transcribe_folder("whatsapp_export/")
for item in results['transcriptions']:
    if any(word in item['text'].lower() for word in ['экскурсия', 'билет', 'яхта']):
        print(f"Запрос: {item['text']}")
        print(f"Клиент: {item['sender']}")
        print(f"Время: {item['timestamp']}")
```

## Обработка ошибок

Скрипт автоматически обрабатывает:

- **Неподдерживаемый формат** → конвертация через FFmpeg
- **Слишком длинное аудио** → переключение на Streaming API
- **Сетевые ошибки** → повтор с exponential backoff
- **Плохое качество** → пометка низкого confidence

## Стоимость

Yandex SpeechKit тарифы (февраль 2026):
- Короткие аудио (<30 сек): 0.2₽/мин
- Длинные аудио (>30 сек): 0.5₽/мин

Пример:
- 10 голосовых по 15 сек = 2.5 мин = 0.5₽
- 10 голосовых по 60 сек = 10 мин = 5₽

## Troubleshooting

### FFmpeg не найден

```
Error: FFmpeg not installed
```

**Решение:** Установите FFmpeg и добавьте в PATH.

### Ошибка API ключа

```
Error: Invalid API key
```

**Решение:** Проверьте `.env` файл, убедитесь что ключ начинается с `AQVN`.

### Файлы не найдены

```
Warning: No audio files found
```

**Решение:** Убедитесь что экспортировали чат "С медиафайлами".

## Структура проекта

```
whatsapp-voice-transcriber/
├── main.py                 # Основной скрипт
├── whatsapp_transcriber.py # Класс транскрибера
├── requirements.txt        # Зависимости
├── .env.example           # Пример конфигурации
├── README.md              # Документация
└── tests/
    └── test_transcriber.py # Тесты
```

## Поддержка

При проблемах проверьте:
1. Версию Python (требуется 3.8+)
2. Наличие FFmpeg в PATH
3. Корректность API ключей в .env
4. Формат входных файлов

## Лицензия

MIT License - свободное использование для вашего бизнеса.
