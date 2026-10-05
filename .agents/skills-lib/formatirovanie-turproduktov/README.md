# Skill: форматирование-турпродуктов

Полное руководство по форматированию текстов туристических продуктов для WhatsApp и Telegram.

## Структура

```
форматирование-турпродуктов/
├── SKILL.md                    # Основные инструкции
├── marketplace.json            # Метаданные для публикации
├── README.md                   # Этот файл
├── assets/
│   ├── templates/              # Шаблоны для заполнения
│   │   ├── tour-whatsapp.txt
│   │   ├── tour-telegram.txt
│   │   ├── restaurant-whatsapp.txt
│   │   ├── restaurant-telegram.txt
│   │   ├── menu-whatsapp.txt
│   │   └── menu-telegram.txt
│   └── examples/               # Готовые примеры
│       ├── tour-abudhabi-whatsapp.txt
│       ├── tour-safaripark-telegram.txt
│       ├── restaurant-babshams-whatsapp.txt
│       └── menu-babshams-whatsapp.txt
├── references/                 # Справочная документация
│   ├── faq.md                  # Часто задаваемые вопросы
│   ├── troubleshooting.md      # Типичные ошибки
│   ├── syntax-reference.md     # Справка по синтаксису
│   └── cheatsheet.md           # Шпаргалки
└── scripts/                    # Скрипты валидации
    ├── validate-whatsapp.py
    ├── validate-telegram.py
    └── helpers.py
```

## Использование

### Шаблоны
Копируй шаблон из `assets/templates/` и заполняй данными.

### Примеры
Смотри готовые примеры в `assets/examples/` для понимания формата.

### Валидация
```bash
python scripts/validate-whatsapp.py your_file.txt
python scripts/validate-telegram.py your_file.txt
```

### Справка
- `references/faq.md` — ответы на частые вопросы
- `references/troubleshooting.md` — решение типичных ошибок
- `references/cheatsheet.md` — быстрые шпаргалки
