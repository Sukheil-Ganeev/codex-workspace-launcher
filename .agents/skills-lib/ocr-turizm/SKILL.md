---
name: ocr-turizm
description: "OCR для туризма ОАЭ — распознавание текста на изображениях (чеки, паспорта, документы). Yandex Vision для русского, Google Vision для арабского/английского. Используй когда нужно извлечь текст из изображения."
---
# OCR для туризма ОАЭ

> Yandex Vision (русский) + Google Vision (арабский/английский)

## Когда использовать

- Чеки и скриншоты оплаты — извлечение суммы, даты, референса
- Паспорта — извлечение данных для виз (MRZ)
- Скриншоты бронирований — подтверждения от поставщиков
- Документы на любом языке (ru/en/ar)

---

## Конфигурация

```bash
# .env файл

# === YANDEX CLOUD VISION ===
# Лучше для русского текста
YANDEX_VISION_API_KEY=PASTE_YANDEX_CLOUD_API_KEY_HERE
YANDEX_CLOUD_FOLDER_ID=b1gvu3q8k1kafqd3sk5f

# === GOOGLE CLOUD VISION ===
# Лучше для арабского и английского
GOOGLE_VISION_API_KEY=PASTE_GOOGLE_API_KEY_HERE
```

---

## Выбор сервиса по языку

| Язык | Сервис | Качество |
|------|--------|----------|
| Русский | Yandex Vision | ⭐⭐⭐⭐⭐ |
| Английский | Google Vision | ⭐⭐⭐⭐⭐ |
| Арабский | Google Vision | ⭐⭐⭐⭐⭐ |
| Рукописный русский | Yandex Vision | ⭐⭐⭐⭐ |

---

## Быстрый старт

```python
import requests
import base64
import os
import re
from pathlib import Path

# === YANDEX VISION OCR ===

def ocr_yandex(image_path: str, languages: list = ["ru", "en"]) -> str:
    """
    Yandex Vision OCR — лучше для русского текста.

    Args:
        image_path: Путь к изображению
        languages: Языки ["ru", "en", "ar"]

    Returns:
        Распознанный текст
    """
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()

    response = requests.post(
        "https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze",
        headers={
            "Authorization": f"Api-Key {os.getenv('YANDEX_VISION_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "folderId": os.getenv("YANDEX_CLOUD_FOLDER_ID"),
            "analyzeSpecs": [{
                "content": image_data,
                "features": [{
                    "type": "TEXT_DETECTION",
                    "textDetectionConfig": {"languageCodes": languages}
                }]
            }]
        }
    )

    if response.status_code != 200:
        raise Exception(f"Yandex Vision error: {response.status_code}")

    # Извлекаем текст
    result = response.json()
    pages = (result
             .get("results", [{}])[0]
             .get("results", [{}])[0]
             .get("textDetection", {})
             .get("pages", []))

    lines = []
    for page in pages:
        for block in page.get("blocks", []):
            for line in block.get("lines", []):
                words = [w.get("text", "") for w in line.get("words", [])]
                lines.append(" ".join(words))

    return "\n".join(lines)


# === GOOGLE VISION OCR ===

def ocr_google(image_path: str, languages: list = ["en", "ar"]) -> str:
    """
    Google Vision OCR — лучше для арабского и английского.

    Args:
        image_path: Путь к изображению
        languages: Подсказка языков

    Returns:
        Распознанный текст
    """
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()

    response = requests.post(
        f"https://vision.googleapis.com/v1/images:annotate?key={os.getenv('GOOGLE_VISION_API_KEY')}",
        json={
            "requests": [{
                "image": {"content": image_data},
                "features": [{"type": "TEXT_DETECTION"}],
                "imageContext": {"languageHints": languages}
            }]
        }
    )

    if response.status_code != 200:
        raise Exception(f"Google Vision error: {response.status_code}")

    result = response.json()
    annotations = result.get("responses", [{}])[0].get("textAnnotations", [])

    if annotations:
        return annotations[0].get("description", "")
    return ""


# === ГИБРИДНЫЙ OCR ===

def ocr_hybrid(image_path: str) -> dict:
    """
    Умный OCR: автоматический выбор сервиса по языку.

    Returns:
        dict: {text, source, language}
    """
    # Сначала Yandex (быстрее для проверки)
    try:
        text_yandex = ocr_yandex(image_path, ["ru", "en"])

        # Считаем долю кириллицы
        cyrillic = len(re.findall(r'[а-яА-ЯёЁ]', text_yandex))
        total = len(text_yandex.replace(" ", "").replace("\n", ""))

        if total > 0 and cyrillic / total > 0.3:
            return {"text": text_yandex, "source": "yandex", "language": "ru"}
    except:
        pass

    # Google для арабского/английского
    try:
        text_google = ocr_google(image_path, ["en", "ar"])

        # Проверяем арабский
        arabic = len(re.findall(r'[\u0600-\u06FF]', text_google))
        total = len(text_google.replace(" ", "").replace("\n", ""))

        lang = "ar" if total > 0 and arabic / total > 0.2 else "en"
        return {"text": text_google, "source": "google", "language": lang}
    except:
        pass

    # Fallback
    if 'text_yandex' in locals() and text_yandex:
        return {"text": text_yandex, "source": "yandex_fallback", "language": "unknown"}

    return {"text": "", "source": "failed", "language": "unknown"}
```

---

## Специализированные функции для туризма

### Извлечение данных из чека оплаты

```python
def extract_payment_info(image_path: str) -> dict:
    """
    Извлечь данные из скриншота чека/перевода.

    Returns:
        dict: {amount, currency, date, reference, raw_text}
    """
    result = ocr_hybrid(image_path)
    text = result["text"]

    info = {
        "raw_text": text,
        "amount": None,
        "currency": None,
        "date": None,
        "reference": None,
        "ocr_source": result["source"]
    }

    # Сумма и валюта
    patterns = [
        r'(\d{1,3}(?:[,.\s]\d{3})*(?:[.,]\d{2})?)\s*(AED|USD|RUB|EUR|руб|дирхам)',
        r'(AED|USD|EUR)\s*(\d{1,3}(?:[,.\s]\d{3})*(?:[.,]\d{2})?)',
        r'Amount[:\s]*(\d+(?:[.,]\d{2})?)\s*(AED|USD)?',
        r'Сумма[:\s]*(\d+(?:[.,]\d{2})?)\s*(руб|RUB)?',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            g = match.groups()
            if g[0].replace(",", "").replace(".", "").replace(" ", "").isdigit():
                info["amount"] = float(g[0].replace(",", "").replace(" ", ""))
                info["currency"] = g[1] if len(g) > 1 else None
            else:
                info["currency"] = g[0]
                info["amount"] = float(g[1].replace(",", "").replace(" ", "")) if len(g) > 1 else None
            break

    # Дата
    date_patterns = [
        r'(\d{2}[./]\d{2}[./]\d{4})',
        r'(\d{4}-\d{2}-\d{2})',
        r'(\d{2}\s+\w+\s+\d{4})',
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            info["date"] = match.group(1)
            break

    # Референс
    ref_patterns = [
        r'(?:Ref|Reference|Transaction|№)[:\s#]*([A-Z0-9]{6,})',
    ]
    for pattern in ref_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info["reference"] = match.group(1)
            break

    return info
```

### Извлечение данных из паспорта (MRZ)

```python
def extract_passport_mrz(image_path: str) -> dict:
    """
    Извлечь данные из MRZ зоны паспорта.

    Returns:
        dict: {surname, given_names, passport_no, nationality, birth_date, expiry_date}
    """
    text = ocr_google(image_path, ["en"])  # MRZ всегда латиница

    info = {
        "raw_text": text,
        "surname": None,
        "given_names": None,
        "passport_no": None,
        "nationality": None,
        "birth_date": None,
        "expiry_date": None
    }

    # Ищем MRZ строки
    lines = text.upper().split("\n")
    mrz = [l.replace(" ", "") for l in lines if len(l) >= 30 and l.count("<") >= 3]

    if len(mrz) >= 2:
        line1, line2 = mrz[0], mrz[1]

        # Имена из первой строки
        if line1.startswith("P"):
            names = line1[5:44].split("<<")
            if len(names) >= 2:
                info["surname"] = names[0].replace("<", " ").strip()
                info["given_names"] = names[1].replace("<", " ").strip()

        # Данные из второй строки
        if len(line2) >= 28:
            info["passport_no"] = line2[0:9].replace("<", "")
            info["nationality"] = line2[10:13]
            info["birth_date"] = _parse_mrz_date(line2[13:19])
            info["expiry_date"] = _parse_mrz_date(line2[21:27])

    return info

def _parse_mrz_date(d: str) -> str:
    """YYMMDD -> DD.MM.YYYY"""
    if len(d) != 6: return None
    yy = int(d[:2])
    year = 2000 + yy if yy < 50 else 1900 + yy
    return f"{d[4:6]}.{d[2:4]}.{year}"
```

### Распознавание скриншота бронирования

```python
def extract_booking_confirmation(image_path: str) -> dict:
    """
    Извлечь данные из скриншота подтверждения бронирования.

    Returns:
        dict: {confirmation_no, guest_name, hotel, check_in, check_out, room_type}
    """
    result = ocr_hybrid(image_path)
    text = result["text"]

    info = {
        "raw_text": text,
        "confirmation_no": None,
        "guest_name": None,
        "hotel": None,
        "check_in": None,
        "check_out": None,
        "room_type": None
    }

    # Номер подтверждения
    conf_patterns = [
        r'(?:Confirmation|Booking|Reservation)[:\s#]*([A-Z0-9]{6,})',
        r'(?:№|#)\s*([A-Z0-9]{8,})',
    ]
    for p in conf_patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            info["confirmation_no"] = m.group(1)
            break

    # Даты
    dates = re.findall(r'(\d{2}[./]\d{2}[./]\d{4})', text)
    if len(dates) >= 2:
        info["check_in"] = dates[0]
        info["check_out"] = dates[1]
    elif len(dates) == 1:
        info["check_in"] = dates[0]

    return info
```

---

## Стоимость

| Сервис | Цена за 1000 изображений |
|--------|-------------------------|
| Yandex Vision | ~$1.50 |
| Google Vision | ~$1.50 |

---

## Альтернативные методы

Текущее решение использует Yandex Vision + Google Vision. Вот альтернативы на случай если нужно:

| Метод | Когда использовать | Плюсы | Минусы |
|-------|-------------------|-------|--------|
| **Yandex Vision** | Русский текст (основной) | Лучшее качество для кириллицы | Платный (~$1.50/1000) |
| **Google Vision** | Арабский/английский (основной) | Лучшее качество для арабского | Платный (~$1.50/1000) |
| **Tesseract** | Большие объёмы, экономия | Бесплатно, локально | Хуже качество, настройка |
| **EasyOCR** | Python, простота | Бесплатно, GPU ускорение | Среднее качество |
| **PaddleOCR** | Мультиязычность | Бесплатно, хорошее качество | Сложнее настройка |
| **Claude Vision** | Уже используешь Claude | Включено в API, понимает контекст | Дороже для массовой обработки |

### Когда переключиться на альтернативу:

| Ситуация | Рекомендация |
|----------|--------------|
| Бюджет ограничен | Tesseract или EasyOCR |
| Нет интернета | Tesseract локально |
| Нужен полный контроль | Свой сервер с Tesseract |
| Уже используешь Claude | Claude Vision для единичных запросов |
| Большие объёмы (>10K/день) | Tesseract + постобработка |

### Установка альтернатив:

```bash
# Tesseract — УСТАНОВЛЕН: D:\Downloads\tesseract.exe (v5.4.0)
# pytesseract — УСТАНОВЛЕН: pip install pytesseract (v0.3.13)

# EasyOCR
pip install easyocr

# PaddleOCR
pip install paddlepaddle paddleocr
```

### Пример Tesseract:

```python
import pytesseract
from PIL import Image

def ocr_tesseract(image_path: str, lang: str = "rus+eng") -> str:
    """Бесплатный локальный OCR через Tesseract."""
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang=lang)
    return text
```

**Подробнее об альтернативах:** `D:/Downloads/Идеи-парсинга/ИДЕИ_ПАРСИНГ_МЕДИА.md`

---

## Связанные скиллы

| Скилл | Связь |
|-------|-------|
| **yandex-cloud-туризм** | SpeechKit для голосовых |
| **whatsapp-парсер** | Использует OCR для чеков в чатах |

---

## Документация

- Yandex Vision: https://cloud.yandex.ru/docs/vision/
- Google Vision: https://cloud.google.com/vision/docs

---

## Дополнительные ресурсы

| Ресурс | Описание |
|--------|----------|
| [FAQ](references/faq.md) | Часто задаваемые вопросы |
| [Troubleshooting](references/troubleshooting.md) | Решение проблем |
| [Шпаргалка](references/cheatsheet.md) | Быстрая справка по функциям |
