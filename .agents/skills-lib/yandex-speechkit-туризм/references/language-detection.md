# Language Detection — Автоопределение языка

> Определение языка голосового сообщения для выбора правильной модели

---

## Проблема

Yandex SpeechKit **НЕ** определяет язык автоматически. Нужно указывать `lang` параметр при каждом запросе.

**Контекст туризма ОАЭ:**
- 70% клиентов из СНГ (русский язык)
- 20% международные туристы (английский)
- 10% местные/арабские (арабский, турецкий)

**Без определения языка:**
```python
# Клиент говорит по-английски, но мы пытаемся ru-RU
text = transcribe("audio.ogg", lang="ru-RU")
# → Результат: искаженный текст или ошибка
```

---

## Решение 1: Попытка нескольких языков

### Концепция

Транскрибируем аудио с несколькими языками, выбираем лучший результат по эвристикам качества.

### Базовая реализация

```python
def transcribe_auto_detect(audio_path: str) -> dict:
    """
    Транскрипция с автоопределением языка.

    Пробует русский, английский, арабский.
    Выбирает результат с максимальной уверенностью.

    Args:
        audio_path: Путь к аудиофайлу

    Returns:
        dict: {
            "language": "ru-RU",
            "text": "распознанный текст",
            "confidence": 0.85
        }
    """
    languages = ["ru-RU", "en-US", "ar-AE"]
    results = []

    for lang in languages:
        try:
            text = transcribe_direct(audio_path, lang)

            if text.strip():
                confidence = estimate_confidence(text, lang)
                results.append({
                    "language": lang,
                    "text": text,
                    "confidence": confidence
                })
        except Exception as e:
            print(f"Ошибка для {lang}: {e}")
            continue

    # Выбираем лучший результат
    if results:
        best = max(results, key=lambda x: x["confidence"])
        return best

    # Fallback если все языки провалились
    return {
        "language": "unknown",
        "text": "",
        "confidence": 0.0
    }


def transcribe_direct(audio_path: str, lang: str) -> str:
    """Прямая транскрипция (из speechkit-basics.md)."""
    import requests
    import os

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
```

---

## Эвристики определения качества

### Основные метрики

```python
def estimate_confidence(text: str, lang: str) -> float:
    """
    Эвристическая оценка качества распознавания.

    Факторы:
    - Длина текста (больше слов = лучше)
    - Отсутствие маркеров ошибок
    - Словарная проверка (типичные слова языка)

    Args:
        text: Распознанный текст
        lang: Язык распознавания

    Returns:
        float: Confidence score (0.0 - 1.0)
    """
    if not text:
        return 0.0

    score = 0.0

    # 1. Длина текста (макс 0.4)
    word_count = len(text.split())
    length_score = min(word_count / 20, 0.4)  # 20 слов = отлично
    score += length_score

    # 2. Отсутствие ошибок (макс 0.3)
    error_markers = ["[неразборчиво]", "???", "...", "[unknown]"]
    has_errors = any(marker in text for marker in error_markers)
    error_score = 0.0 if has_errors else 0.3
    score += error_score

    # 3. Словарная проверка (макс 0.3)
    dictionary_score = check_language_dictionary(text, lang)
    score += dictionary_score

    return round(min(score, 1.0), 2)


def check_language_dictionary(text: str, lang: str) -> float:
    """
    Проверка типичных слов языка.

    Returns:
        float: Score 0.0 - 0.3
    """
    # Словари типичных слов
    dictionaries = {
        "ru-RU": [
            # Приветствия
            "здравствуйте", "привет", "добрый", "день", "вечер",
            # Туризм
            "хочу", "забронировать", "сафари", "экскурсия", "тур",
            "человек", "взрослых", "детей", "цена", "стоимость",
            "когда", "где", "как", "можно", "нужно",
            # Локации
            "дубай", "абу-даби", "отель", "аэропорт", "марина"
        ],
        "en-US": [
            # Greetings
            "hello", "hi", "good", "morning", "evening",
            # Tourism
            "want", "book", "safari", "tour", "excursion",
            "people", "adults", "children", "price", "cost",
            "when", "where", "how", "can", "need",
            # Locations
            "dubai", "abu", "dhabi", "hotel", "airport"
        ],
        "ar-AE": [
            "مرحبا", "السلام", "صباح", "مساء",
            "أريد", "حجز", "سفاري", "جولة", "رحلة",
            "سعر", "تكلفة", "متى", "أين", "كيف"
        ]
    }

    dictionary = dictionaries.get(lang, [])
    if not dictionary:
        return 0.15  # Neutral score

    # Подсчет совпадений
    text_lower = text.lower()
    matches = sum(1 for word in dictionary if word in text_lower)

    # Нормализация (10 совпадений = максимум)
    score = min(matches / 10, 1.0) * 0.3

    return score
```

---

## Оптимизация: приоритет по профилю клиента

### Концепция

Если знаем страну/язык клиента из CRM — пробуем его первым.

```python
def transcribe_with_profile(audio_path: str, client_country: str = None) -> dict:
    """
    Транскрипция с учетом профиля клиента.

    Args:
        audio_path: Путь к аудио
        client_country: Страна клиента (RU, KZ, US, AE, TR)

    Returns:
        dict: Результат распознавания
    """
    # Определяем приоритетные языки по стране
    language_priority = {
        "RU": ["ru-RU", "en-US"],  # Россия — сначала русский
        "KZ": ["ru-RU", "en-US"],  # Казахстан — русский
        "BY": ["ru-RU", "en-US"],  # Беларусь — русский
        "UA": ["ru-RU", "en-US"],  # Украина — русский
        "US": ["en-US", "ru-RU"],  # США — английский
        "GB": ["en-US", "ru-RU"],  # Великобритания
        "AE": ["ar-AE", "en-US", "ru-RU"],  # ОАЭ — арабский
        "TR": ["tr-TR", "en-US", "ru-RU"],  # Турция — турецкий
    }

    # Получаем приоритет или дефолтный
    languages = language_priority.get(
        client_country,
        ["ru-RU", "en-US", "ar-AE"]  # По умолчанию для СНГ
    )

    # Пробуем в порядке приоритета
    results = []

    for lang in languages:
        try:
            text = transcribe_direct(audio_path, lang)

            if text.strip():
                confidence = estimate_confidence(text, lang)
                results.append({
                    "language": lang,
                    "text": text,
                    "confidence": confidence
                })

                # Если уверенность >0.7 — прерываем (найден язык)
                if confidence > 0.7:
                    break

        except Exception:
            continue

    # Возвращаем лучший результат
    if results:
        best = max(results, key=lambda x: x["confidence"])
        return best

    return {"language": "unknown", "text": "", "confidence": 0.0}
```

---

## Решение 2: Определение по первым секундам

### Концепция

Обрабатываем только первые 5 секунд для определения языка, затем полное аудио с правильным языком.

**Экономия:** 2 запроса вместо 3 (60% экономия на длинных аудио).

```python
import subprocess

def transcribe_with_sample_detection(audio_path: str) -> dict:
    """
    Определение языка по первым 5 секундам.

    Алгоритм:
    1. Вырезать первые 5 сек
    2. Определить язык (попытка ru/en/ar)
    3. Транскрибировать полное аудио с найденным языком

    Args:
        audio_path: Путь к полному аудио

    Returns:
        dict: Результат с полным текстом
    """
    # Шаг 1: Вырезать первые 5 сек
    sample_path = f"{audio_path}_sample.ogg"

    subprocess.run([
        'ffmpeg', '-i', audio_path,
        '-t', '5',  # Первые 5 секунд
        '-c', 'copy',
        sample_path, '-y'
    ], capture_output=True, check=True)

    try:
        # Шаг 2: Определить язык
        lang_result = transcribe_auto_detect(sample_path)
        detected_lang = lang_result["language"]

        # Шаг 3: Полная транскрипция
        full_text = transcribe_any_audio(audio_path, detected_lang)

        return {
            "language": detected_lang,
            "text": full_text,
            "confidence": lang_result["confidence"]
        }

    finally:
        # Cleanup
        if os.path.exists(sample_path):
            os.remove(sample_path)
```

### Производительность

| Метод | Запросов | Время (60 сек аудио) |
|-------|----------|---------------------|
| Полное определение | 3 языка × 3 части = 9 | ~7 сек |
| Sample detection | 3 + 3 = 6 | ~5 сек |
| Экономия | 33% | 29% |

---

## Решение 3: Fallback cascade

### Концепция

Используем каскад: пытаемся самый вероятный язык, при низкой уверенности — пробуем остальные.

```python
def transcribe_cascade(audio_path: str, primary_lang: str = "ru-RU") -> dict:
    """
    Каскадное определение языка.

    1. Пробуем primary_lang
    2. Если confidence < 0.5 — пробуем остальные

    Экономия: ~70% случаев — 1 запрос (для СНГ клиентов)

    Args:
        audio_path: Путь к аудио
        primary_lang: Основной язык (по умолчанию ru-RU)

    Returns:
        dict: Результат распознавания
    """
    # Шаг 1: Пробуем основной язык
    text = transcribe_direct(audio_path, primary_lang)
    confidence = estimate_confidence(text, primary_lang)

    if confidence >= 0.5:
        # Уверены — возвращаем результат
        return {
            "language": primary_lang,
            "text": text,
            "confidence": confidence
        }

    # Шаг 2: Низкая уверенность — пробуем альтернативы
    other_langs = [l for l in ["ru-RU", "en-US", "ar-AE"] if l != primary_lang]
    results = [{
        "language": primary_lang,
        "text": text,
        "confidence": confidence
    }]

    for lang in other_langs:
        try:
            text = transcribe_direct(audio_path, lang)
            conf = estimate_confidence(text, lang)
            results.append({
                "language": lang,
                "text": text,
                "confidence": conf
            })
        except Exception:
            continue

    # Возвращаем лучший
    best = max(results, key=lambda x: x["confidence"])
    return best
```

---

## Туристический контекст: распределение языков

### Статистика по языкам (туризм ОАЭ)

```python
LANGUAGE_STATS = {
    "ru-RU": 0.70,  # 70% клиентов из СНГ
    "en-US": 0.20,  # 20% международные
    "ar-AE": 0.05,  # 5% арабские
    "tr-TR": 0.03,  # 3% турецкие
    "other": 0.02   # 2% остальные
}
```

### Smart detection с приоритетом

```python
def transcribe_smart_tourism(audio_path: str) -> dict:
    """
    Умное определение для туризма ОАЭ.

    Стратегия:
    1. Пробуем ru-RU (70% клиентов)
    2. Если confidence < 0.5 → пробуем en-US
    3. Если confidence < 0.5 → пробуем ar-AE

    Экономия:
    - 70% случаев: 1 запрос
    - 20% случаев: 2 запроса
    - 10% случаев: 3 запроса
    Среднее: 1.4 запроса (вместо 3)

    Returns:
        dict: Результат с языком и текстом
    """
    languages = ["ru-RU", "en-US", "ar-AE"]
    threshold = 0.5

    for i, lang in enumerate(languages):
        text = transcribe_direct(audio_path, lang)
        confidence = estimate_confidence(text, lang)

        print(f"Попытка {i+1}: {lang}, confidence={confidence:.2f}")

        if confidence >= threshold or i == len(languages) - 1:
            # Найден язык ИЛИ последняя попытка
            return {
                "language": lang,
                "text": text,
                "confidence": confidence,
                "attempts": i + 1
            }

    return {"language": "unknown", "text": "", "confidence": 0.0}
```

---

## Интеграция с CRM

### Получение языка из базы клиентов

```python
def get_client_language(phone: str) -> str:
    """
    Получение предпочтительного языка клиента из CRM.

    Args:
        phone: Номер телефона клиента

    Returns:
        str: Язык клиента (ru-RU, en-US, ar-AE)
    """
    # Пример интеграции с Notion/Airtable/SQL
    import requests

    # Notion API пример
    notion_token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("NOTION_CLIENTS_DB")

    response = requests.post(
        f"https://api.notion.com/v1/databases/{database_id}/query",
        headers={
            "Authorization": f"Bearer {notion_token}",
            "Notion-Version": "2022-06-28"
        },
        json={
            "filter": {
                "property": "Phone",
                "phone_number": {"equals": phone}
            }
        }
    )

    if response.ok and response.json()["results"]:
        client = response.json()["results"][0]
        country = client["properties"]["Country"]["select"]["name"]

        # Маппинг страны на язык
        lang_map = {
            "Russia": "ru-RU",
            "Kazakhstan": "ru-RU",
            "USA": "en-US",
            "UK": "en-US",
            "UAE": "ar-AE",
            "Turkey": "tr-TR"
        }

        return lang_map.get(country, "ru-RU")

    return "ru-RU"  # Default для СНГ
```

### Использование с WhatsApp Bot

```python
def process_whatsapp_voice(phone: str, audio_url: str) -> str:
    """
    Обработка голосового из WhatsApp с учетом профиля.

    Args:
        phone: Номер отправителя
        audio_url: URL аудиофайла

    Returns:
        str: Транскрибированный текст
    """
    # Скачиваем аудио
    import requests
    audio_path = "/tmp/voice.ogg"
    response = requests.get(audio_url)
    with open(audio_path, "wb") as f:
        f.write(response.content)

    # Получаем язык клиента
    client_lang = get_client_language(phone)

    # Транскрибируем с каскадом
    result = transcribe_cascade(audio_path, primary_lang=client_lang)

    return result["text"]
```

---

## Сравнение подходов

| Подход | Запросов | Точность | Сложность | Рекомендация |
|--------|----------|----------|-----------|--------------|
| **Все языки** | 3 | 🟢 Высокая | 🟢 Просто | Прототипы |
| **Sample detection** | 2-3 | 🟢 Высокая | 🟡 Средне | Batch обработка |
| **Cascade** | 1-3 (avg 1.4) | 🟡 Средняя | 🟢 Просто | **Production** |
| **CRM integration** | 1-2 | 🟢 Высокая | 🔴 Сложно | Enterprise |

**Рекомендация:** Cascade для быстрого старта, CRM integration для масштаба.

---

## Best Practices

### 1. Кеширование результатов

```python
import hashlib
import json

CACHE = {}

def transcribe_cached(audio_path: str) -> dict:
    """Транскрипция с кешированием."""
    # Хеш файла как ключ кеша
    with open(audio_path, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()

    if file_hash in CACHE:
        print(f"Кеш попадание: {file_hash}")
        return CACHE[file_hash]

    # Транскрибируем
    result = transcribe_smart_tourism(audio_path)
    CACHE[file_hash] = result

    return result
```

### 2. Логирование статистики

```python
import json
from datetime import datetime

def log_language_detection(result: dict, audio_path: str):
    """Логирование для анализа точности."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "file": audio_path,
        "detected_lang": result["language"],
        "confidence": result["confidence"],
        "attempts": result.get("attempts", 1)
    }

    with open("language_detection.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

### 3. Fallback на Whisper

```python
def transcribe_with_fallback(audio_path: str) -> dict:
    """Транскрипция с fallback на Whisper API."""
    try:
        # Пытаемся SpeechKit
        result = transcribe_smart_tourism(audio_path)

        if result["confidence"] < 0.3:
            # Низкая уверенность — fallback на Whisper
            text = transcribe_whisper(audio_path)
            return {
                "language": "auto-detected",
                "text": text,
                "source": "whisper_fallback"
            }

        return result

    except Exception as e:
        # Ошибка SpeechKit — Whisper
        text = transcribe_whisper(audio_path)
        return {
            "language": "unknown",
            "text": text,
            "source": "whisper_fallback"
        }


def transcribe_whisper(audio_path: str) -> str:
    """Whisper API транскрипция."""
    import openai

    client = openai.OpenAI()

    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )

    return transcript.text
```

---

## Метрики эффективности

### Оценка качества detection

```python
def evaluate_detection_quality(test_cases: list) -> dict:
    """
    Оценка качества определения языка.

    Args:
        test_cases: [{"audio": "path", "expected_lang": "ru-RU"}, ...]

    Returns:
        dict: Метрики (accuracy, avg_attempts, avg_time)
    """
    correct = 0
    total_attempts = 0
    total_time = 0

    for case in test_cases:
        import time
        start = time.time()

        result = transcribe_smart_tourism(case["audio"])

        elapsed = time.time() - start
        total_time += elapsed
        total_attempts += result.get("attempts", 1)

        if result["language"] == case["expected_lang"]:
            correct += 1

    return {
        "accuracy": correct / len(test_cases),
        "avg_attempts": total_attempts / len(test_cases),
        "avg_time": total_time / len(test_cases)
    }
```

---

## Связанные материалы

| Документ | Описание |
|----------|----------|
| `references/speechkit-basics.md` | Основы API, языки, форматы |
| `references/sync-vs-async.md` | Выбор между Sync и Async API |
| `references/error-handling.md` | Обработка ошибок и retry |
| `references/integrations.md` | Интеграция с WhatsApp, Telegram, CRM |

---

## Официальная документация

- Список языков: https://cloud.yandex.ru/docs/speechkit/stt/models#languages
- Модели распознавания: https://cloud.yandex.ru/docs/speechkit/stt/models
- API Reference: https://cloud.yandex.ru/docs/speechkit/stt/api/request-api
