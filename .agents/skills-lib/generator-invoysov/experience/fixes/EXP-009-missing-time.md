---
id: EXP-009
date: 2026-01-22
type: fix
severity: high
tags: [время, яхты, туры, начало, окончание]
---

## Проблема

Для услуг, требующих времени (яхты, туры), не указано время начала/окончания.

## Контекст

**Неправильно:**
```
YACHT RENTING IN DUBAI: MAJESTY 48 FT NEW (5 HOURS)
← Нет конкретного времени

PRIVATE TOUR IN DUBAI (for 2 persons) 28 JANUARY
← Нет времени начала
```

## Решение

**Яхты:**
```
YACHT RENTING IN DUBAI: MAJESTY 48 FT NEW (5 HOURS). RENTAL TIME FROM 15:30 TO 20:30.
RENT AN INFINITY CATAMARAN 60 FEET FROM 17:00 TO 22:00
```

**Туры:**
```
PRIVATE TOUR IN DUBAI (for 2 persons) 28 JANUARY, START AT 10:00 AM
PRIVATE DUBAI MODERN TOUR FROM 09:00 TO 16:00
```

## Урок

Форматы времени:
- Яхты: **FROM HH:MM TO HH:MM** или **(N HOURS). RENTAL TIME FROM HH:MM TO HH:MM**
- Туры: **START AT HH:MM AM/PM** или **FROM HH:MM TO HH:MM**
