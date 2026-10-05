# Hybrid SpeechKit + Whisper

Гибридный подход: Yandex SpeechKit для русского, OpenAI Whisper для остальных языков.

## Описание

Автоматически выбирает лучший движок в зависимости от языка:
- Русский → Yandex SpeechKit (лучшее качество для русского)
- Английский/Арабский/Турецкий → Whisper API

## Использование

```bash
python main.py --input audio.ogg --auto-detect
```

## Конфигурация

```env
YANDEX_API_KEY=xxx
YANDEX_FOLDER_ID=xxx
OPENAI_API_KEY=xxx
```

## Логика выбора

1. Определение языка (langdetect на тексте или auto)
2. Если русский → SpeechKit
3. Иначе → Whisper
4. Сравнение confidence scores
5. Возврат лучшего результата
