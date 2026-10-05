---
id: EXP-004
date: 2026-01-22
type: fix
severity: high
tags: [POS, комиссия, процент, карта, B2B]
---

## Проблема

Указан неправильный процент комиссии POS Terminal или комиссия добавлена когда не нужна.

## Контекст

**Неправильно:**
```
PAYMENT VIA POS TERMINAL + 5%      ← Слишком много
PAYMENT VIA POS TERMINAL + 3%      ← Слишком мало

# B2B клиент (юр.лицо), который платит переводом:
Bill To: RMCOS TRADING L.L.C
...
PAYMENT VIA POS TERMINAL + 4%      ← Не нужна!
```

## Решение

**Правильно:**
```
# Стандартный клиент (физ.лицо, оплата картой):
PAYMENT VIA POS TERMINAL + 4%

# VIP/корпоративный клиент:
PAYMENT VIA POS TERMINAL + 3.5%

# B2B клиент (юр.лицо) - НЕ добавлять POS Terminal
```

## Урок

- Стандартная комиссия: **4%**
- VIP клиенты: **3.5%**
- Юридические лица (оплата переводом): **не добавлять** POS Terminal
