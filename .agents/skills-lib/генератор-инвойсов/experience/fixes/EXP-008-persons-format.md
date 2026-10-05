---
id: EXP-008
date: 2026-01-22
type: fix
severity: medium
tags: [персоны, количество, формат, for-persons]
---

## Проблема

Количество персон не указано или указано в неверном формате.

## Контекст

**Неправильно:**
```
PRIVATE TOUR IN DUBAI 28 JANUARY, START AT 10:00 AM
← Нет количества персон

PRIVATE TOUR IN DUBAI (2 persons) 28 JANUARY
← Нет "for"

PRIVATE TOUR IN DUBAI (for two persons) 28 JANUARY
← Текстом вместо цифры
```

## Решение

Формат: **(for N persons)**

**Правильно:**
```
PRIVATE TOUR IN DUBAI (for 2 persons) 28 JANUARY, START AT 10:00 AM
PRIVATE JEEP SAFARI TOUR (for 4 persons) 30 JANUARY
PRIVATE TOUR IN ABU DHABI (for 2 persons) 1 FEBRUARY, START AT 9:00 AM
```

## Урок

Всегда указывай количество цифрой, используй "for" и "persons".
