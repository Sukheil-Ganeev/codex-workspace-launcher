# pdf-мастер

Универсальный навык для **всех** операций с PDF и PPTX файлами.

## Возможности

| Категория | Операции |
|-----------|----------|
| **Создание** | Инвойсы, отчёты, прайсы, сертификаты, визитки (ReportLab, fpdf2, WeasyPrint) |
| **Извлечение** | Текст, таблицы, изображения, метаданные, формы (PyMuPDF, pdfplumber, pikepdf) |
| **Манипуляция** | Слияние, разделение, поворот, обрезка, водяные знаки (pypdf, PyMuPDF) |
| **Конвертация** | HTML→PDF, PPTX→PDF, PDF→изображения, изображения→PDF, PDF→DOCX |
| **OCR** | Распознавание текста в сканах (ocrmypdf + Tesseract) |
| **Безопасность** | Шифрование AES-256, цифровые подписи, редактирование (pikepdf, pyHanko) |
| **Оптимизация** | Сжатие, линеаризация, ремонт повреждённых PDF (pikepdf, PyMuPDF) |
| **PPTX** | Создание, чтение, модификация презентаций (python-pptx) |

## Стек (22 пакета)

pypdf, PyMuPDF, ReportLab, fpdf2, pdfplumber, pikepdf, WeasyPrint, ocrmypdf, pyHanko, img2pdf, PyPDFForm, pypdfium2, pdfminer.six, python-pptx, python-docx, pdf2docx, Pillow, Jinja2, svglib, openpyxl, qrcode, python-barcode

## Структура

```
pdf-мастер/
├── SKILL.md                          # Основные инструкции (242 строки)
├── README.md                         # Этот файл
├── references/
│   ├── library-guide.md              # Детальный справочник 19 библиотек
│   ├── operations-catalog.md         # Каталог операций с кодом
│   ├── code-patterns.md              # 10 готовых рецептов
│   ├── troubleshooting.md            # FAQ, ошибки, fallback
│   └── cheatsheet.md                 # Быстрая шпаргалка
├── scripts/
│   └── check_deps.py                 # Проверка зависимостей
├── assets/templates/                 # HTML-шаблоны (Jinja2)
└── experience/                       # Накопленный опыт
    └── _index.md
```

## Системные зависимости

| Зависимость | Статус | Установка |
|-------------|--------|-----------|
| Tesseract 5.4 | Установлен | — |
| Ghostscript | Не установлен | ghostscript.com |
| GTK3 (Cairo/Pango) | Не установлен | msys2.org |

## Проверка стека

```bash
python C:/Users/londo/.claude/skills/pdf-мастер/scripts/check_deps.py
```
