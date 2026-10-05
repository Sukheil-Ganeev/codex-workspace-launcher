# OCR интеграция с парсером WhatsApp

**Источник:** SKILL.md, перенесено для экономии места

---

## Обзор

При парсинге чатов автоматически распознаётся текст на изображениях: чеки, скриншоты оплаты, паспорта клиентов, скриншоты бронирований.

---

## Интеграция с парсером

```python
from pathlib import Path

def process_chat_media_with_ocr(chat_folder: str) -> list:
    """
    Обработать все изображения в чате с OCR.

    Args:
        chat_folder: Папка чата с media/

    Returns:
        list: Найденные данные (чеки, паспорта)
    """
    media_folder = Path(chat_folder) / "media"
    if not media_folder.exists():
        return []

    results = []

    # Обрабатываем изображения
    for img_path in media_folder.glob("*.jpg"):
        filename = img_path.name.lower()

        # Определяем тип по имени файла
        if any(x in filename for x in ["img", "photo", "screen"]):
            # Пробуем как чек
            try:
                from ocr_tourism import extract_payment_info
                payment = extract_payment_info(str(img_path))

                if payment.get("amount"):
                    results.append({
                        "type": "payment",
                        "file": img_path.name,
                        "data": payment
                    })
                    continue
            except:
                pass

            # Пробуем как паспорт
            try:
                from ocr_tourism import extract_passport_mrz
                passport = extract_passport_mrz(str(img_path))

                if passport.get("passport_no"):
                    results.append({
                        "type": "passport",
                        "file": img_path.name,
                        "data": passport
                    })
            except:
                pass

    return results
```

---

## Классификация изображений

```python
def classify_image_type(image_path: str) -> str:
    """
    Определить тип изображения по содержимому.

    Returns:
        str: "receipt", "passport", "booking", "unknown"
    """
    from ocr_tourism import ocr_hybrid

    result = ocr_hybrid(image_path)
    text = result["text"].lower()

    # Признаки чека
    receipt_markers = ["amount", "сумма", "payment", "transfer", "aed", "usd", "rub"]
    if any(m in text for m in receipt_markers):
        return "receipt"

    # Признаки паспорта
    if "<<<" in text or "passport" in text or "p<" in text.replace(" ", ""):
        return "passport"

    # Признаки бронирования
    booking_markers = ["confirmation", "booking", "reservation", "check-in", "check-out"]
    if any(m in text for m in booking_markers):
        return "booking"

    return "unknown"
```

---

## Автоматическая обработка при парсинге

```python
def enhanced_parse_chat(chat_path: str) -> dict:
    """
    Расширенный парсинг чата с OCR.
    """
    # Базовый парсинг
    chat_data = parse_chat(chat_path)  # из основного парсера

    # OCR для медиа
    ocr_results = process_chat_media_with_ocr(chat_path)

    # Добавляем OCR данные
    chat_data["ocr_extracted"] = {
        "payments": [r for r in ocr_results if r["type"] == "payment"],
        "passports": [r for r in ocr_results if r["type"] == "passport"],
        "bookings": [r for r in ocr_results if r["type"] == "booking"]
    }

    # Суммируем оплаты
    total_payments = sum(
        p["data"].get("amount", 0)
        for p in chat_data["ocr_extracted"]["payments"]
        if p["data"].get("amount")
    )
    chat_data["ocr_extracted"]["total_amount"] = total_payments

    return chat_data
```

---

## Использование

```python
# Парсинг одного чата с OCR
chat = enhanced_parse_chat("D:/Downloads/Туризм-ОАЭ-Проект/01-Исходные-данные/WhatsApp-Личный/Марсель Ганеев_971507705321/")

print(f"Найдено чеков: {len(chat['ocr_extracted']['payments'])}")
print(f"Общая сумма: {chat['ocr_extracted']['total_amount']} AED")

# Данные паспортов (для виз)
for passport in chat['ocr_extracted']['passports']:
    print(f"Паспорт: {passport['data']['passport_no']}")
    print(f"Имя: {passport['data']['given_names']} {passport['data']['surname']}")
```

**См. скилл:** `/ocr-туризм` — полная документация по OCR
