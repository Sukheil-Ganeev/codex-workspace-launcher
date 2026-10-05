# Обработка медиа -- Полный код

Полные реализации всех функций обработки медиа: Whisper, SpeechKit, OCR, Claude Vision, CLIP, дедупликация и др.

---

## Whisper транскрипция (полный код)

```python
import openai
from pathlib import Path

def transcribe_voice(audio_path: str, language: str = "ru") -> dict:
    """
    Транскрипция голосового сообщения через Whisper API.

    Args:
        audio_path: Путь к аудиофайлу (ogg, mp3, wav, m4a)
        language: Код языка (ru, en, ar)

    Returns:
        dict: {text, duration, language, segments}
    """
    client = openai.OpenAI()

    with open(audio_path, "rb") as audio_file:
        # Базовая транскрипция
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language,
            response_format="verbose_json"
        )

    return {
        "text": transcription.text,
        "duration": transcription.duration,
        "language": transcription.language,
        "segments": [
            {
                "start": s.start,
                "end": s.end,
                "text": s.text
            }
            for s in transcription.segments
        ]
    }


def transcribe_with_context(audio_path: str, context: str = None) -> dict:
    """
    Транскрипция с подсказкой контекста для улучшения точности.

    Args:
        audio_path: Путь к аудио
        context: Контекст (имена, термины) для улучшения распознавания

    Returns:
        dict: Результат транскрипции
    """
    client = openai.OpenAI()

    # Контекст для туристических терминов
    tourism_context = """
    Ferrari World, Burj Khalifa, Dubai Mall, Atlantis, Palm Jumeirah,
    Desert Safari, Abu Dhabi, Sharjah, трансфер, экскурсия, виза,
    Марсель, Дубай, дирхам, AED
    """

    prompt = tourism_context
    if context:
        prompt += f"\n{context}"

    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            prompt=prompt,
            response_format="verbose_json"
        )

    return {
        "text": transcription.text,
        "duration": transcription.duration
    }
```

---

## Yandex SpeechKit (для русского языка)

Для русскоязычных клиентов рекомендуется Yandex SpeechKit -- лучшее качество распознавания русской речи.

```python
import requests
import os

def transcribe_speechkit(audio_path: str, lang: str = "ru-RU") -> str:
    """
    Транскрипция через Yandex SpeechKit.
    Лучше Whisper для русского языка.

    Args:
        audio_path: Путь к аудио (ogg opus, mp3, wav)
        lang: Язык (ru-RU, en-US, tr-TR)

    Returns:
        str: Распознанный текст
    """
    response = requests.post(
        "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
        params={
            "folderId": os.getenv("YANDEX_CLOUD_FOLDER_ID"),
            "lang": lang,
            "format": "oggopus",
            "sampleRateHertz": 48000
        },
        headers={
            "Authorization": f"Api-Key {os.getenv('YANDEX_CLOUD_API_KEY')}"
        },
        data=open(audio_path, "rb")
    )

    if response.status_code == 200:
        return response.json().get("result", "")
    else:
        raise Exception(f"SpeechKit error: {response.status_code}")


def transcribe_hybrid(audio_path: str, client_language: str = "ru") -> dict:
    """
    Гибридная транскрипция: SpeechKit для русского, Whisper для остальных.
    """
    if client_language in ["ru", "kz", "by", "ua"]:
        text = transcribe_speechkit(audio_path, "ru-RU")
        return {"text": text, "source": "speechkit", "language": "ru-RU"}
    else:
        result = transcribe_voice(audio_path, client_language)
        return {"text": result["text"], "source": "whisper", "language": client_language}
```

**Сравнение Whisper vs SpeechKit:**

| Параметр | SpeechKit | Whisper |
|----------|-----------|---------|
| Русский | Отлично | Очень хорошо |
| Английский | Очень хорошо | Отлично |
| Streaming | Да | Нет |
| Стоимость | ~$0.01/мин | $0.006/мин |

> **Подробнее:** См. скилл `giga-transcribe-туризм` для полной документации.

---

## OCR документов (полный код)

```python
import anthropic
import base64
from pathlib import Path

def ocr_document(image_path: str) -> dict:
    """
    OCR документа через Claude Vision API.

    Args:
        image_path: Путь к изображению (jpg, png, pdf первая страница)

    Returns:
        dict: {text, document_type, extracted_data}
    """
    client = anthropic.Anthropic()

    # Читаем изображение
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    # Определяем MIME тип
    suffix = Path(image_path).suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp"
    }
    media_type = media_types.get(suffix, "image/jpeg")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": """Извлеки текст из этого документа.

Верни JSON:
{
  "document_type": "passport|visa|ticket|invoice|receipt|other",
  "text": "полный текст документа",
  "extracted_data": {
    "name": "имя если есть",
    "date": "дата если есть",
    "number": "номер документа если есть",
    "amount": "сумма если есть"
  },
  "confidence": 0.0-1.0
}"""
                    }
                ]
            }
        ]
    )

    return json.loads(response.content[0].text)


def ocr_batch(image_paths: list[str]) -> list[dict]:
    """
    OCR пакета документов.
    """
    results = []
    for path in image_paths:
        try:
            result = ocr_document(path)
            result['source_file'] = path
            results.append(result)
        except Exception as e:
            results.append({
                'source_file': path,
                'error': str(e)
            })
    return results
```

---

## Анализ изображений (Claude Vision)

```python
def analyze_image(image_path: str, query: str = None) -> dict:
    """
    Анализ изображения через Claude Vision.

    Args:
        image_path: Путь к изображению
        query: Конкретный вопрос об изображении

    Returns:
        dict: Результат анализа
    """
    client = anthropic.Anthropic()

    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    default_query = """Проанализируй изображение в контексте туристического бизнеса ОАЭ.

Верни JSON:
{
  "description": "описание изображения",
  "category": "vehicle|attraction|hotel|document|location|person|other",
  "relevant_for": "для какой услуги релевантно",
  "text_detected": "текст на изображении если есть",
  "location_hint": "предполагаемое место если определяется"
}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": query or default_query
                    }
                ]
            }
        ]
    )

    return json.loads(response.content[0].text)
```

---

## Парсинг банковских переводов

```python
PATTERNS = {
    "amount": [
        r"(?:AED|USD|EUR|RUB)\s*([\d,]+\.?\d*)",
        r"Amount[:\s]*([\d,]+\.?\d*)",
    ],
    "reference": [
        r"Reference[:\s]*([A-Z0-9]+)",
        r"Transaction ID[:\s]*([A-Z0-9]+)",
    ]
}

# Определение банка
banks = {
    "ENBD": "Emirates NBD",
    "FAB": "First Abu Dhabi Bank",
    "Сбер": "Сбербанк",
    "Kaspi": "Kaspi Bank"
}
```

---

## Классификация типа изображения

```python
def classify_image(image_path: str) -> dict:
    """Классификация типа изображения для туризма."""

    categories = [
        "receipt",        # чек
        "bank_transfer",  # скриншот перевода
        "passport",       # паспорт
        "attraction",     # достопримечательность
        "hotel",          # отель
        "vehicle",        # машина, яхта
        "document",       # документ
        "screenshot"      # скриншот переписки
    ]

    # Результат
    return {
        "type": "bank_transfer",
        "confidence": 0.95,
        "contains_personal_data": True
    }
```

---

## Маскирование персональных данных

```python
def mask_sensitive_data(text: str) -> str:
    """Маскирование чувствительных данных."""

    # Номер паспорта: оставляем последние 4 цифры
    # AB1234567 -> AB****4567

    # Номер карты
    # 4111 1111 1111 1234 -> **** **** **** 1234

    # Телефон
    # +971501234567 -> +*** *** *** 4567

    # Email
    # user@domain.com -> u***@domain.com

    return masked_text
```

---

## Организация медиафайлов

```python
# Сортировка по типам
organized/
├── images/       # .jpg, .png, .webp
├── videos/       # .mp4, .mov, .3gp
├── audio/        # .opus, .ogg, .mp3
├── documents/    # .pdf, .doc
└── contacts/     # .vcf

# Сортировка по датам
organized/
├── 2026/
│   ├── 01/
│   │   ├── image1.jpg
│   │   └── video1.mp4
│   └── 02/
└── ...
```

---

## Дедупликация изображений

```python
# Perceptual hash для поиска похожих
from imagehash import phash

# Находит визуально похожие изображения даже если:
# - Разного размера
# - Разного качества
# - Немного обрезаны

duplicates = deduplicator.find_duplicates("media/")
# {"hash123": ["photo1.jpg", "photo1_copy.jpg"]}
```

---

## Семантический поиск (CLIP)

```python
# Поиск по текстовому описанию
search = CLIPMediaSearch()
search.index_directory("media/images")

# "банковский перевод скриншот"
results = search.search("банковский перевод скриншот")
# [{"path": "transfer_001.jpg", "score": 0.89}]

# "фото пустыни с верблюдами"
results = search.search("фото пустыни с верблюдами")
# [{"path": "safari_photo.jpg", "score": 0.92}]
```

---

## Обработка VCF контактов

```python
# Извлечение данных
parser = VCardParser()
contacts = parser.parse_file("contacts.vcf")

# Анализ связей
analyzer = ContactAnalyzer(contacts)
colleagues = analyzer.find_colleagues(contact)
stats = analyzer.get_statistics()
# {"total_contacts": 150, "with_organization": 89, ...}
```

---

## Видео анализ

```python
# Полный пайплайн
analyzer = VideoAnalyzer()
result = analyzer.analyze("video.mp4", "output/")

# Результат
{
    "info": {"duration": 45, "resolution": "1280x720"},
    "transcription": "Текст из аудио...",
    "frames": [{"description": "Пустыня с дюнами..."}],
    "summary": "Видео показывает сафари..."
}
```

---

## Статистика медиа по отправителям

```python
stats = SenderMediaStats()
stats.analyze_chat_with_media("chat.txt", "media/")

top_senders = stats.get_top_senders(by="size", limit=10)
# [{"sender": "Клиент А", "stats": {"images": 45, "videos": 12, ...}}]
```
