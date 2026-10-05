# Invoice Generator Skill

Скилл для автоматизации генерации инвойсов Marsel Luxury Car Rental и Sokol Car Rental.

## Возможности

- Генерация инвойсов для двух брендов (Marsel и Sokol)
- Поддержка всех типов услуг: туры, трансферы, яхты, билеты, аренда авто, кейтеринг
- Автоматический расчёт VAT (5%)
- Поддержка POS Terminal (комиссия 3.5% или 4%)
- Конвертация USD/AED
- Валидация входных данных

## Структура

```
invoice-generator/
├── SKILL.md                      # Основной файл скилла
├── README.md                     # Этот файл
├── marketplace.json              # Метаданные
│
├── assets/
│   ├── templates/
│   │   └── INVOICE_TEMPLATE.pptx # Эталонный шаблон
│   │
│   └── examples/                 # Примеры входных данных
│       ├── simple-tour.yaml      # Простой тур
│       ├── corporate-multi.yaml  # Корпоративный клиент
│       ├── pos-terminal.yaml     # С POS Terminal
│       └── sokol-car-rental.yaml # Аренда авто Sokol
│
└── references/                   # Справочники
    ├── АНАЛИЗ_PPTX.md            # Анализ PPTX инвойсов
    ├── АНАЛИЗ_PDF.md             # Анализ PDF инвойсов
    ├── ПРАВИЛА_ГЕНЕРАЦИИ.md      # Правила генерации
    ├── service-types.md          # Типы услуг
    ├── bank-details.md           # Банковские реквизиты
    ├── troubleshooting.md        # Типичные ошибки
    └── checklist.md              # Чеклист проверки
```

## Быстрый старт

1. Подготовьте данные в формате YAML (см. `assets/examples/`)
2. Вызовите скилл с данными
3. Проверьте результат по чеклисту (`references/checklist.md`)

## Минимальные входные данные

```yaml
invoice:
  number: "#26-001"
  date: "Jan 22, 2026"
brand: "marsel"
client:
  name: "IVANOV IVAN"
  phone: "+7 999 123 4567"
services:
  - description: "PRIVATE TOUR IN DUBAI (for 2 persons) 28 JANUARY"
    price_excl_vat: 238.10
```

## Бренды

| Бренд | Использование | Licence |
|-------|---------------|---------|
| marsel | Туры, трансферы, яхты, билеты | 1024110 |
| sokol | Долгосрочная аренда авто | 1442819 |

## Документация

- **SKILL.md** — основные правила и алгоритм
- **references/ПРАВИЛА_ГЕНЕРАЦИИ.md** — детальные правила
- **references/service-types.md** — все типы услуг с примерами
- **references/bank-details.md** — банковские реквизиты
- **references/troubleshooting.md** — решение типичных ошибок
- **references/checklist.md** — чеклист проверки

## Версия

- **Версия:** 1.0
- **Дата:** Январь 2026
- **Основа:** Анализ 18 реальных инвойсов (9 PPTX + 9 PDF)

## Контакты

- Marsel: +971 58 511 0777, www.marsel-luxurycarrental.com
- Sokol: +971 58 511 0777, www.sokol-carrental.com
