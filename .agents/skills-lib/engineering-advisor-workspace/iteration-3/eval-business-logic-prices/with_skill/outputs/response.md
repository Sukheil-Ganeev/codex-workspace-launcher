# Engineering Advisor — Ответ с активным скиллом

## Активация скилла

Engineering Advisor активирован. Загружено 5 критических уроков из опыта (EXP-053, EXP-040, EXP-041, EXP-065, EXP-073). Буду проверять код с учётом накопленных ошибок.

---

## Анализ запроса (до написания кода)

Запрос содержит функцию с бизнес-логикой — **сработал триггер #3:**

```
=== Engineering Advisor ===
WARN (1): Функция calculate_tour_price содержит бизнес-логику с ценами
  -- Триггер #3: price, total, AED, скидка → Recommended
  -- Уровень: Recommended (жёлтый — совет врача)
  -- Тесты обязательны для финансовых расчётов
INFO (1): Параметр group_discount_pct не включён в сигнатуру — нужно уточнить диапазон (0-100 или 0.0-1.0)
INFO (1): Функция принимает tax_rate но в задаче НДС 5% — стоит сделать константой или параметром явно
===========================
```

---

## Уточнение перед кодом (ВАЖНО)

Перед тем как дополнить функцию, нужно решить **2 неоднозначных момента** в условии:

1. **`group_discount_pct` — в каких единицах?**
   - Вариант A: `10` = 10% скидка → формула: `base * (1 - pct/100)`
   - Вариант B: `0.10` = 10% скидка → формула: `base * (1 - pct)`
   - Принимаю **Вариант A** (натуральные проценты — понятнее для человека)

2. **Порядок применения скидки и налога:**
   - Вариант A: скидка → потом налог (налог на итоговую цену)
   - Вариант B: налог → потом скидка (скидка на цену с налогом)
   - Принимаю **Вариант A** (стандартная практика в туризме — НДС начисляется на итоговую сумму)

---

## Реализация функции

```python
def calculate_tour_price(
    base_price_per_night: float,
    nights: int,
    group_discount_pct: float,  # 0-100, например 10 = 10% скидка
    tax_rate: float = 0.05,     # НДС 5% по умолчанию
) -> dict:
    """
    Рассчитывает стоимость тура в AED.

    Параметры:
        base_price_per_night: Базовая цена за ночь (AED)
        nights: Количество ночей
        group_discount_pct: Процент скидки для группы (0-100)
        tax_rate: Ставка налога (по умолчанию 0.05 = 5% НДС)

    Возвращает:
        dict с полным расчётом: subtotal, discount, after_discount, tax, total

    Исключения:
        ValueError: если параметры вне допустимого диапазона
    """
    # Валидация входных данных
    if base_price_per_night <= 0:
        raise ValueError(f"base_price_per_night должна быть > 0, получено: {base_price_per_night}")
    if nights <= 0:
        raise ValueError(f"nights должно быть > 0, получено: {nights}")
    if not (0 <= group_discount_pct <= 100):
        raise ValueError(f"group_discount_pct должен быть 0-100, получено: {group_discount_pct}")
    if not (0 <= tax_rate <= 1):
        raise ValueError(f"tax_rate должен быть 0.0-1.0, получено: {tax_rate}")

    # Расчёт
    subtotal = base_price_per_night * nights
    discount_amount = subtotal * (group_discount_pct / 100)
    after_discount = subtotal - discount_amount
    tax_amount = after_discount * tax_rate
    total = after_discount + tax_amount

    return {
        "subtotal_aed": round(subtotal, 2),
        "discount_pct": group_discount_pct,
        "discount_aed": round(discount_amount, 2),
        "after_discount_aed": round(after_discount, 2),
        "tax_pct": tax_rate * 100,
        "tax_aed": round(tax_amount, 2),
        "total_aed": round(total, 2),
    }
```

---

## Пример вызова

```python
# Тур: 500 AED/ночь, 3 ночи, групповая скидка 10%, НДС 5%
result = calculate_tour_price(
    base_price_per_night=500,
    nights=3,
    group_discount_pct=10,
)
print(result)
# {
#   'subtotal_aed': 1500.0,
#   'discount_pct': 10,
#   'discount_aed': 150.0,
#   'after_discount_aed': 1350.0,
#   'tax_pct': 5.0,
#   'tax_aed': 67.5,
#   'total_aed': 1417.5
# }
```

---

## Рекомендация Engineering Advisor (Триггер #3)

**WARN — Рекомендую добавить тесты перед использованием в продакшне.**

Эта функция считает деньги клиентов. Ошибка в расчёте = репутационный и финансовый ущерб.

Минимальный набор тестов который нужно пройти:

```python
def test_calculate_tour_price():
    # 1. Базовый случай без скидки
    result = calculate_tour_price(500, 3, 0)
    assert result["total_aed"] == 1575.0  # 500*3 + 5% налог

    # 2. Скидка 10%
    result = calculate_tour_price(500, 3, 10)
    assert result["subtotal_aed"] == 1500.0
    assert result["discount_aed"] == 150.0
    assert result["after_discount_aed"] == 1350.0
    assert result["tax_aed"] == 67.5
    assert result["total_aed"] == 1417.5

    # 3. Скидка 100% (полная)
    result = calculate_tour_price(500, 3, 100)
    assert result["total_aed"] == 0.0

    # 4. Граничный случай: 1 ночь
    result = calculate_tour_price(500, 1, 0)
    assert result["total_aed"] == 525.0  # 500 + 5%

    # 5. Валидация: отрицательная цена
    import pytest
    with pytest.raises(ValueError):
        calculate_tour_price(-500, 3, 0)

    # 6. Валидация: скидка > 100%
    with pytest.raises(ValueError):
        calculate_tour_price(500, 3, 150)
```

**Промпт для запуска тестов:** "Запусти тесты calculate_tour_price и покажи реальный вывод pytest"

---

## Что проверено / Что стоит проверить

**Проверено:**
- Функция возвращает детализированный dict с каждым шагом расчёта
- Валидация входных данных с понятными ошибками
- Порядок: subtotal -> discount -> tax -> total (стандартный)
- Округление до 2 знаков после запятой (AED)

**Не проверено (стоит проверить вручную):**
- Поведение с дробными ночами (0.5 ночи) — сейчас допускается
- Многовалютность — если понадобится USD/EUR, функцию нужно расширить
- Интеграция с реальной системой бронирования — нужен тест end-to-end

---

## Engineering Advisor Summary (предварительный)

```
=== Engineering Advisor Summary ===
Триггеры сработали: #3 (бизнес-логика с ценами, Recommended)
BLOCK: 0
WARN: 1 — финансовая функция без тестов
INFO: 2 — неоднозначность единиц параметра, порядок скидка/налог
Опыт применён: EXP-040 (сверка имён полей в return dict)
===================================
```

Хотите записать урок в опыт скилла о паттерне "финансовая функция должна возвращать полный расчёт, не только итог"?
