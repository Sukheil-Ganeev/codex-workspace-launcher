---
id: EXP-010
date: 2026-01-22
type: fix
severity: medium
tags: [адрес, офис, DAMAC, FALAHI, старый]
---

## Проблема

Использован устаревший адрес офиса для новых инвойсов.

## Контекст

**Неправильно (для 2024-2026):**
```
Address: AL FALAHI BUILDING, 312-931, Al Suq Al Kabeer Plot 184-0, Dubai, UAE
```

## Решение

**2024-2026 — DAMAC SMART HEIGHTS BUILDING:**

```
# Marsel:
Address: DAMAC SMART HEIGHTS BUILDING, OFFICE NUMBER 2109

# Sokol:
Address: DAMAC SMART HEIGHTS BUILDING, OFFICE NUMBER 2106
```

## Урок

Адреса:
- **2024-2026**: DAMAC SMART HEIGHTS BUILDING
  - Marsel: офис **2109**
  - Sokol: офис **2106**
- До 2024: AL FALAHI BUILDING (только для архивных документов)
