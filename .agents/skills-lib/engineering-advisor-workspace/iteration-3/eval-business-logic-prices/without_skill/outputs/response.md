# Ответ: расчёт стоимости тура

Вот дополненная функция:

```python
def calculate_tour_price(base_price_per_night, nights, group_discount_pct):
    """
    Рассчитывает итоговую стоимость тура в AED.

    Параметры:
        base_price_per_night (float): Базовая цена за ночь в AED
        nights (int): Количество ночей
        group_discount_pct (float): Процент скидки для группы (например, 10 для 10%)

    Возвращает:
        dict: Детализация расчёта и итоговая сумма в AED
    """
    VAT_RATE = 0.05  # НДС 5%

    # 1. Базовая стоимость
    subtotal = base_price_per_night * nights

    # 2. Скидка для группы
    discount_amount = subtotal * (group_discount_pct / 100)
    after_discount = subtotal - discount_amount

    # 3. НДС 5%
    vat_amount = after_discount * VAT_RATE

    # 4. Итог
    total = after_discount + vat_amount

    return {
        "base_price_per_night": base_price_per_night,
        "nights": nights,
        "subtotal": round(subtotal, 2),
        "group_discount_pct": group_discount_pct,
        "discount_amount": round(discount_amount, 2),
        "after_discount": round(after_discount, 2),
        "vat_amount": round(vat_amount, 2),
        "total_aed": round(total, 2),
    }
```

## Пример вызова

```python
result = calculate_tour_price(
    base_price_per_night=500,  # 500 AED за ночь
    nights=4,
    group_discount_pct=10      # скидка 10% для группы
)

print(f"Базовая стоимость:  {result['subtotal']} AED")
print(f"Скидка ({result['group_discount_pct']}%):      -{result['discount_amount']} AED")
print(f"После скидки:       {result['after_discount']} AED")
print(f"НДС (5%):           +{result['vat_amount']} AED")
print(f"ИТОГО:              {result['total_aed']} AED")
```

**Вывод:**

```
Базовая стоимость:  2000.0 AED
Скидка (10%):      -200.0 AED
После скидки:       1800.0 AED
НДС (5%):           +90.0 AED
ИТОГО:              1890.0 AED
```

## Логика расчёта

1. `subtotal = 500 × 4 = 2000 AED` — базовая стоимость
2. `discount = 2000 × 10% = 200 AED` — групповая скидка
3. `after_discount = 2000 - 200 = 1800 AED`
4. `vat = 1800 × 5% = 90 AED` — НДС начисляется **после** скидки
5. `total = 1800 + 90 = 1890 AED`

> Важно: НДС начисляется на сумму **после скидки**, а не на полную стоимость — это стандартная практика в ОАЭ.
