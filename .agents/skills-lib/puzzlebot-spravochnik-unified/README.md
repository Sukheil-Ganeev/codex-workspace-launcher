# puzzlebot-справочник-unified

Объединённый справочник по конструктору Telegram-ботов PuzzleBot. Результат слияния 3 скиллов в единую 3-уровневую структуру.

## Исходные скиллы

| Скилл | Слой | Что содержал |
|-------|------|-------------|
| `puzzlebot-справочник` | docs/ | Платформенный гайд: тарифы, обзор, лимиты, туризм ОАЭ |
| `puzzlebot-конструктор-справочник` | learn/ | Обучающий гайд: 112 видеоуроков, 12 модулей, паттерны, готовые сценарии |
| `puzzlebot-deep-reference` | deep/ | Глубокие данные: 30 видео-файлов, 45 транскриптов, 10 OCR, community knowledge |

## Структура

```
puzzlebot-справочник-unified/
├── SKILL.md                              # Routing-файл (~3500 слов, навигация по 3 слоям)
├── README.md                             # Этот файл
├── references/
│   ├── docs/                             # Уровень 1: Платформенный справочник (4 файла)
│   │   ├── platform-guide.md             # Полный гайд по платформе
│   │   ├── faq.md                        # FAQ платформы
│   │   ├── troubleshooting.md            # Решение проблем
│   │   └── cheatsheet.md                 # Шпаргалка
│   │
│   ├── learn/                            # Уровень 2: Обучающий справочник (17 файлов)
│   │   ├── full-guide.md                 # Полный гайд по конструктору (112 уроков)
│   │   ├── video-index.md                # Индекс видеоуроков
│   │   ├── faq.md                        # FAQ конструктора
│   │   ├── troubleshooting.md            # Решение проблем конструктора
│   │   ├── cheatsheet.md                 # Шпаргалка конструктора
│   │   └── modules/                      # 12 тематических модулей
│   │       ├── 01-basics.md              # Основы
│   │       ├── 02-forms.md               # Формы ввода
│   │       ├── 03-buttons-menu.md        # Кнопки и меню
│   │       ├── 04-variables.md           # Переменные и формулы
│   │       ├── 05-scenarios.md           # Сценарии
│   │       ├── 06-payments.md            # Оплата
│   │       ├── 07-integrations.md        # Интеграции
│   │       ├── 08-mini-apps.md           # Мини-приложения
│   │       ├── 09-groups.md              # Группы и каналы
│   │       ├── 10-broadcasts.md          # Рассылки
│   │       ├── 11-posting.md             # Постинг
│   │       └── 12-gamification.md        # Геймификация
│   │
│   ├── deep/                             # Уровень 3: Глубокий справочник (89 файлов)
│   │   ├── videos/                       # 30 видео-справочников
│   │   │   ├── 01-basics-deep-part1.md
│   │   │   ├── 01-basics-deep-part2.md
│   │   │   ├── 02-forms-deep.md
│   │   │   ├── 03-buttons-menu-deep.md
│   │   │   ├── 04-variables-deep-part1.md ... part3
│   │   │   ├── 05-scenarios-deep-part1.md ... part2
│   │   │   ├── 06-payments-deep-part1.md ... part4
│   │   │   ├── 07-integrations-deep-part1.md ... part4
│   │   │   ├── 08-mini-apps-deep-part1.md ... part3
│   │   │   ├── 09-groups-deep-part1.md ... part3
│   │   │   ├── 10-broadcasts-deep.md
│   │   │   ├── 11-posting-deep.md
│   │   │   ├── 12-gamification-deep-part1.md ... part2
│   │   │   └── 13-special-topics-deep-part1.md ... part3
│   │   ├── transcripts/                  # 45 транскриптов
│   │   │   ├── transcripts-basics-part1.md ... part3
│   │   │   ├── transcripts-forms-part1.md ... part2
│   │   │   ├── transcripts-variables-part1.md ... part4
│   │   │   ├── transcripts-scenarios-part1.md ... part10
│   │   │   ├── transcripts-payments-part1.md ... part5
│   │   │   ├── transcripts-integrations-part1.md ... part4
│   │   │   ├── transcripts-miniapps-part1.md ... part4
│   │   │   ├── transcripts-groups-part1.md ... part5
│   │   │   └── transcripts-other-part1.md ... part6
│   │   ├── ocr/                          # 10 OCR-снимков интерфейса
│   │   │   ├── ocr-constructor.md
│   │   │   ├── ocr-variables.md
│   │   │   ├── ocr-payments.md
│   │   │   ├── ocr-scenarios.md
│   │   │   ├── ocr-shop.md
│   │   │   ├── ocr-miniapps.md
│   │   │   ├── ocr-posting.md
│   │   │   ├── ocr-moderation.md
│   │   │   ├── ocr-settings.md
│   │   │   └── ocr-entrance.md
│   │   ├── ocr-interface-map.md          # Карта интерфейса по OCR
│   │   ├── community-knowledge-full-part1a.md  # Community (часть 1a)
│   │   ├── community-knowledge-full-part1b.md  # Community (часть 1b)
│   │   └── community-knowledge-full-part2.md   # Community (часть 2)
│   │
│   └── _qa/                              # Результаты QA-проверок
│
└── experience/                           # Накопленный опыт (11 уроков)
    └── _index.md                         # Критические уроки (читать при активации)
```

## Статистика

| Метрика | Значение |
|---------|----------|
| Всего файлов в references/ | ~110 |
| Видеоуроков покрыто | 112 |
| Сообщений сообщества | 68,659 |
| Q&A пар | 8,712 |
| OCR кадров | 3,859 |
| Период данных | 2024-03 -- 2026-02 |

## Принцип работы

SKILL.md содержит ТОЛЬКО routing (навигацию) -- он не дублирует контент. Вся полезная информация хранится в файлах references/.

**Каскадная стратегия поиска:**

1. **docs/** -- для быстрых ответов, обзоров, лимитов, FAQ
2. **learn/** -- для практических инструкций, паттернов, настройки функций
3. **deep/** -- для точных деталей интерфейса, полных видео-инструкций, контекста из сообщества

## Темы (15 направлений)

1. Основы и Quick Start
2. Блоки и команды
3. Кнопки и клавиатуры
4. Формы ввода
5. Переменные и формулы
6. Условия и логика
7. Сценарии и автоматизация
8. Оплата и платежи
9. Магазин
10. Рассылки и постинг
11. Интеграции (Google Sheets, NocoDB, API, AI)
12. Мини-приложения
13. Группы, каналы, модерация
14. Геймификация и баллы
15. Спецтемы (диалоги, лид-магнит, капча, админка)
