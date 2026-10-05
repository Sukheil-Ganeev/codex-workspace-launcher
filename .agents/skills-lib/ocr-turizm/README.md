# OCR для туризма ОАЭ

Скилл для распознавания текста на изображениях: Yandex Vision (русский) + Google Vision (арабский/английский).

## Структура

```
ocr-туризм/
├── SKILL.md              # Основная документация
├── README.md             # Это файл
└── references/
    ├── faq.md            # Часто задаваемые вопросы
    ├── troubleshooting.md # Решение проблем
    └── cheatsheet.md     # Шпаргалка
```

## Быстрый старт

```python
from ocr_tourism import ocr_hybrid
result = ocr_hybrid("receipt.jpg")
print(result["text"])
```

## Связанные скиллы
- yandex-speechkit-туризм — транскрипция голосовых
- whatsapp-парсер — парсинг чатов с OCR
