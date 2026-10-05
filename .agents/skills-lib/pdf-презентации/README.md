# pdf-презентации

Конвертация HTML презентаций в PDF через Playwright.

## Быстрый старт

1. Создать HTML презентацию (через `frontend-design`)
2. Применить технические правила из SKILL.md
3. Конвертировать:

```bash
python scripts/convert-to-pdf.py presentation.html output.pdf
```

## Установка

```bash
pip install playwright
playwright install chromium
```

## Структура

```
pdf-презентации/
├── SKILL.md                    # Основные правила конвертации (13 разделов)
├── README.md                   # Этот файл
├── references/
│   ├── troubleshooting.md      # 14 типичных проблем и решений
│   └── cheatsheet.md           # Шпаргалка (CSS, Playwright, чек-лист)
├── scripts/
│   ├── convert-to-pdf.py       # CLI скрипт конвертации
│   └── image_downloader.py     # Скачивание из Pexels/Unsplash/Pixabay
└── experience/                 # 29 накопленных уроков
    ├── _index.md               # Топ-29 критических уроков
    ├── fixes/                  # Исправленные ошибки (EXP-001..010)
    ├── improvements/           # Улучшения (шрифты, визуальный дизайн)
    ├── patterns/               # Паттерны (hbox→cards, light terminals, zero-dep...)
    └── warnings/               # Что НЕ делать
```

## Справка

- `SKILL.md` — технические правила конвертации
- `references/troubleshooting.md` — типичные проблемы и решения
- `references/cheatsheet.md` — быстрая шпаргалка

## Форматы

| Формат | Размер | Применение |
|--------|--------|------------|
| 16:9 | 1920x1080px | Экраны, проекторы (по умолчанию) |
| 16:9-4k | 3840x2160px | Высокое разрешение |
| 4:3 | 1440x1080px | Старые проекторы |
| a4 | A4 альбомная | Печать |
| a4-portrait | A4 портретная | Документы |

## Связанные скиллы

- `frontend-design` — создание HTML дизайна
- `document-skills:pdf` — работа с готовыми PDF
