# Synthetic full-cycle example

This example is deliberately fictional so that no old event price or policy is reused as current fact.

## Request

Two adjacent seated tickets for “Example Arena Concert”, 10 October, adults, good lower level. A secondary listing shows Section 104, Row K, 2 together at 1,100 AED each. Checkout has no separate seller fee. Marsel instructs 5% reserve and 60% markup, working rate 3.65.

## Internal calculation

```bash
python scripts/calculate_offer.py --base 1100 --source-per-usd 3.65 \
  --bank-reserve-percent 5 --markup-percent 60 --round-up-usd 5 --quantity 2
```

Expected commercial result: 510 USD per ticket; estimated/gross order profit about 387.12 USD. Before offering, verify the exact event/date, seller allocation, delivery, transfer and current checkout.

## Partner TXT shape

```txt
Хамра, добрый день!

По вашему запросу можем предложить билеты на *Example Arena Concert*.

*Дата:* 10 октября
*Место проведения:* Example Arena
*Количество гостей:* 2 взрослых

*Вариант 1 — Lower Level*

*Сектор:* 104
*Ряд:* K
*Расположение:* 2 места рядом
*Стоимость:* *510 USD за билет*

*Возрастные ограничения:* правила мероприятия подтверждаются перед бронированием.

Наличие конкретных мест и окончательную стоимость необходимо повторно подтвердить непосредственно перед оплатой, поскольку доступность может измениться.
```

The partner block contains no procurement source, base cost, reserve or profit.
