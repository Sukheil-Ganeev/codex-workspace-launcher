# оптимизатор-маршрутов

## Описание
Оптимизация туристических маршрутов по ОАЭ с использованием Google Maps MCP. Расчёт расстояний и времени в пути с учётом пробок, планирование дневных маршрутов, поддержка авто и общественного транспорта (метро, автобусы, трамвай).

## Структура
```
оптимизатор-маршрутов/
├── SKILL.md              # Основной файл
├── README.md             # Этот файл
├── references/           # Справочные материалы
│   ├── faq.md
│   ├── cheatsheet.md
│   ├── база-оаэ.md
│   ├── критические-правила.md
│   ├── нормализация-названий.md
│   └── транспорт/        # Детальные справочники транспорта
│       ├── дубай-метро-трамвай.md
│       ├── дубай-автобусы.md
│       ├── дубай-водный.md
│       ├── абу-даби.md
│       ├── аэропорты.md
│       ├── межгородской.md
│       ├── северные-эмираты.md
│       ├── etihad-rail.md
│       ├── авто-vs-транспорт.md
│       ├── оплата-проездные.md
│       ├── правила-советы.md
│       ├── станции-достопримечательности.md
│       ├── шаттлы-последняя-миля.md
│       └── будущий-транспорт.md
├── assets/
│   ├── examples/         # Готовые примеры маршрутов (6 шт)
│   │   ├── example-dubai-1day.md
│   │   ├── example-dubai-abudhabi.md
│   │   ├── example-dubai-transit.md
│   │   ├── example-incomplete-data.md
│   │   ├── example-overload.md
│   │   └── example-seasonal.md
│   └── templates/        # Шаблоны вывода (10 шт)
│       ├── template-whatsapp.txt
│       ├── template-telegram.txt
│       ├── template-ai-chat.txt
│       ├── template-transit.txt
│       ├── template-transit-whatsapp.txt
│       ├── template-transit-telegram.txt
│       ├── template-airport-transfer.txt
│       ├── template-comparison.txt
│       ├── template-mixed-route.txt
│       └── template-clarification.txt
├── diagrams/             # Схемы транспортных сетей
│   ├── dubai-metro-map.md
│   ├── dubai-tram-connections.md
│   ├── etihad-rail-map.md
│   ├── intercity-network.md
│   ├── nol-zones.md
│   └── transit-decision-tree.md
└── experience/           # Накопленный опыт
    ├── _index.md
    ├── fixes/
    ├── improvements/
    ├── patterns/
    └── warnings/
```

## Использование
Скилл активируется автоматически по триггерам в description.
