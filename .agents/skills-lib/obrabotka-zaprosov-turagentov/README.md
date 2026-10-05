# Скилл: Обработка запросов турагентов

Полное руководство по обработке запросов от турагентов и клиентов на туристические продукты в ОАЭ.

---

## Быстрый старт

### 5 главных правил:

| Правило | Значение |
|---------|----------|
| Разделители | 15 тире `───────────────` |
| Пробелы | 2 после категории |
| Эмодзи | Только 💰 ➕ ⚠️ |
| Мессенджер | ВСЕГДА уточнять |
| Выдача | Файл .txt, не code block |

---

## Структура скилла

```
обработка-запросов-турагентов/
├── SKILL.md                      # Основной файл (~1000 строк)
├── README.md                     # Этот файл
├── marketplace.json              # Метаданные
│
├── assets/
│   ├── templates/                # 8 шаблонов
│   │   ├── tour-whatsapp.txt
│   │   ├── tour-telegram.txt
│   │   ├── restaurant-whatsapp.txt
│   │   ├── restaurant-telegram.txt
│   │   ├── menu-whatsapp.txt
│   │   ├── menu-telegram.txt
│   │   ├── tickets-whatsapp.txt
│   │   └── tickets-telegram.txt
│   │
│   └── examples/                 # 5 примеров
│       ├── tour-abudhabi-whatsapp.txt
│       ├── tour-safari-telegram.txt
│       ├── restaurant-dhowcruise-whatsapp.txt
│       ├── menu-dhowcruise-whatsapp.txt
│       └── tickets-aquaventure-whatsapp.txt
│
├── references/                   # 4 справочника
│   ├── faq.md
│   ├── troubleshooting.md
│   ├── syntax-reference.md
│   └── cheatsheet.md
│
└── scripts/                      # 3 скрипта
    ├── validate-whatsapp.py
    ├── validate-telegram.py
    └── helpers.py
```

**Итого: 21 файл**

---

## Типы продуктов

| Тип | Группировка цен | Файлов | Особенности |
|-----|-----------------|--------|-------------|
| **Туры** | По эмиратам | 1 | Блок ОПЦИИ |
| **Питание** | По пакетам | 2 | Основное + Меню |
| **Билеты** | По категориям | 1 | Модульная система |

---

## Мессенджеры

| Элемент | WhatsApp | Telegram |
|---------|----------|----------|
| Жирный | `*текст*` | `**текст**` |
| Курсив | `_текст_` | `__текст__` |
| Моноширинный | ` ```текст``` ` | ` `текст` ` |
| Разделитель | 15 тире | 18 тире |

**ВАЖНО:** Если мессенджер не указан — УТОЧНИТЬ!

---

## Использование

### Для Claude Code:

```bash
# Скопировать в папку skills
cp -r обработка-запросов-турагентов ~/.claude/skills/
```

### Для проекта:

```bash
# Скопировать в папку проекта
cp -r обработка-запросов-турагентов .claude/skills/
```

### Валидация файлов:

```bash
# Проверить WhatsApp-карточку
python scripts/validate-whatsapp.py карточка.txt

# Проверить Telegram-карточку
python scripts/validate-telegram.py карточка.txt
```

---

## Дополнительные ресурсы

| Ресурс | Описание |
|--------|----------|
| `assets/templates/` | Шаблоны для заполнения |
| `assets/examples/` | Готовые примеры |
| `references/faq.md` | Частые вопросы |
| `references/troubleshooting.md` | Типичные ошибки |
| `references/syntax-reference.md` | Справка по синтаксису |
| `references/cheatsheet.md` | Шпаргалки для копирования |

---

## Версия

- **Версия:** 2.0.0
- **Дата:** Январь 2026
- **Автор:** Tourism Content Team

---

## Связанные скиллы

- `форматирование-турпродуктов` — детальные правила форматирования карточек
