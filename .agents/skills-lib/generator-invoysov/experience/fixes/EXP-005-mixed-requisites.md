---
id: EXP-005
date: 2026-01-22
type: fix
severity: critical
tags: [Marsel, Sokol, реквизиты, банк, смешивание]
---

## Проблема

В одном инвойсе используются реквизиты разных компаний — логотип одной с банковскими реквизитами другой.

## Контекст

**Неправильно:**
```
Шапка: Marsel Luxury Car Rental, Licence: 1024110
...
COMPANY BANK ACCOUNT
Company Name: SOKOL CAR RENTAL L.L.C    ← Реквизиты другой компании!
```

## Решение

Все элементы должны соответствовать одной компании:

**Marsel:**
```
Шапка: Marsel Luxury Car Rental, Licence: 1024110
...
COMPANY NAME: MARSEL LUXURY CAR RENTAL
ACCOUNT NO: 28642584
IBAN: 110500000000028642584
```

**Sokol:**
```
Шапка: Sokol Car Rental L.L.C, Licence: 1442819
...
Company Name: SOKOL CAR RENTAL L.L.C
Account No.: 19346595
IBAN: AE070500000000019346595
```

## Урок

Перед генерацией определи бренд:
- **Marsel**: туры, трансферы, яхты, билеты, краткосрочная аренда
- **Sokol**: долгосрочная аренда авто

Проверить: логотип, Licence, банковские реквизиты, адрес офиса.
