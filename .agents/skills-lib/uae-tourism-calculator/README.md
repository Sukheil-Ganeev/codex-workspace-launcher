# uae-tourism-calculator

## Описание
Валютный калькулятор для туристического бизнеса в ОАЭ. Конвертация AED/USD/RUB/KZT/USDT/Stars с наценкой, расчёт прибыли агента, форматирование для WhatsApp/Telegram, банковские реквизиты для оплаты.

## Структура
```
uae-tourism-calculator/
├── SKILL.md              # Основной файл
├── README.md             # Этот файл
├── references/           # Справочные материалы
│   ├── aed_to_kzt_economics.md
│   ├── aed_to_rub_economics.md
│   ├── aed_to_usd_economics.md
│   ├── common_services.md
│   ├── currency_exchange_economics.md
│   ├── rub_exchange_economics.md
│   ├── telegram_stars_economics.md
│   ├── usdt_exchange_economics.md
│   └── whatsapp_templates.md
├── assets/               # Банковские реквизиты (3 формата)
│   ├── plain/            # Простой текст (8 счетов)
│   ├── telegram/         # Telegram-формат (8 счетов)
│   └── whatsapp/         # WhatsApp-формат (8 счетов)
├── scripts/
│   └── currency_calculator.py
└── experience/           # Накопленный опыт
    ├── _index.md
    ├── fixes/
    ├── improvements/
    ├── patterns/
    └── warnings/
```

## Использование
Скилл активируется автоматически по триггерам в description.
