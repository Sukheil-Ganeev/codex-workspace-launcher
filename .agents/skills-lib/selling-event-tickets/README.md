# selling-event-tickets

Внутренний AI-skill Марселя для исследования, закупки, проверки, расчёта и упаковки билетов и event-продуктов.

## Что умеет

- восстанавливает предыдущие предложения и локальные правила прибыли;
- ищет обычные билеты, VIP/VVIP, hospitality, suites, boxes, paddock и многодневные пакеты;
- проверяет seats together, transfer, dynamic QR, real-name, lead booker и возраст;
- считает полную себестоимость до прибыли;
- выдаёт чистый WhatsApp TXT партнёру и отдельный внутренний расчёт;
- не раскрывает закупочную цепочку партнёрам;
- содержит playbooks, шаблоны, тесты и два CLI-инструмента.

## Быстрая проверка

```bash
python tests/run_tests.py
python scripts/check_skill.py
```

## Пример запуска калькулятора

```bash
python scripts/calculate_offer.py \
  --base 1100 \
  --source-per-usd 3.65 \
  --bank-reserve-percent 5 \
  --markup-percent 60 \
  --round-up-usd 5 \
  --quantity 2
```

## Конфиденциальность

Skill предназначен для внутренней работы. Не отправляйте партнёрам каталог `references`, исходную базу знаний, внутренние расчёты или закупочные ссылки.
