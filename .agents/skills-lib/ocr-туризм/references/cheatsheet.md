# Шпаргалка — OCR туризм

## Переменные окружения
```bash
# Yandex Vision (русский)
YANDEX_VISION_API_KEY=PASTE_YANDEX_CLOUD_API_KEY_HERE
YANDEX_CLOUD_FOLDER_ID=b1gvu3q8k1kafqd3sk5f

# Google Vision (арабский/английский)
GOOGLE_VISION_API_KEY=PASTE_GOOGLE_API_KEY_HERE
```

## Функции

| Функция | Назначение |
|---------|------------|
| `ocr_yandex()` | Русский текст |
| `ocr_google()` | Арабский/английский |
| `ocr_hybrid()` | Автовыбор сервиса |
| `extract_payment_info()` | Данные из чека |
| `extract_passport_mrz()` | Данные паспорта |

## Пример: чек оплаты
```python
info = extract_payment_info("receipt.jpg")
print(f"Сумма: {info['amount']} {info['currency']}")
print(f"Дата: {info['date']}")
```

## Пример: паспорт
```python
passport = extract_passport_mrz("passport.jpg")
print(f"Имя: {passport['given_names']} {passport['surname']}")
print(f"Номер: {passport['passport_no']}")
```

## Выбор сервиса по языку
| Язык | Сервис | Функция |
|------|--------|---------|
| Русский | Yandex | `ocr_yandex(img, ["ru"])` |
| Английский | Google | `ocr_google(img, ["en"])` |
| Арабский | Google | `ocr_google(img, ["ar"])` |
| Авто | Гибрид | `ocr_hybrid(img)` |
