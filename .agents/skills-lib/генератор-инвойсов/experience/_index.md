# Опыт: генератор-инвойсов

> Последнее обновление: 2026-02-03

---

## Критические уроки (топ-5)

1. **[EXP-002]** — VAT = Amount × 0.05, проверяй: Excl + VAT = Incl
2. **[EXP-005]** — НЕ смешивай реквизиты Marsel и Sokol в одном инвойсе!
3. **[EXP-004]** — POS Terminal: 4% стандарт, 3.5% VIP, НЕ для B2B
4. **[EXP-007]** — Для СНГ клиентов: USD + конвертация в AED (курс 3.65)
5. **[EXP-009]** — Яхты/туры требуют время (FROM HH:MM TO HH:MM)

---

## Статистика

- **Всего записей:** 10
- **Fixes:** 10
- **Improvements:** 0
- **Patterns:** 0
- **Warnings:** 0

---

## Fixes (исправленные ошибки)

| ID | Severity | Описание |
|----|----------|----------|
| [EXP-001](fixes/EXP-001-date-format.md) | high | Формат даты: Mon DD, YYYY (американский) |
| [EXP-002](fixes/EXP-002-vat-calculation.md) | critical | Расчёт VAT 5%: Amount × 0.05 |
| [EXP-003](fixes/EXP-003-phone-format.md) | medium | Телефон с кодом страны (+971, +7) |
| [EXP-004](fixes/EXP-004-pos-terminal-percent.md) | high | POS Terminal: 4% / 3.5% / без для B2B |
| [EXP-005](fixes/EXP-005-mixed-requisites.md) | critical | Не смешивать реквизиты Marsel/Sokol |
| [EXP-006](fixes/EXP-006-invoice-number-format.md) | medium | Номер инвойса: #YY-XXX |
| [EXP-007](fixes/EXP-007-usd-aed-conversion.md) | high | USD→AED конвертация для СНГ |
| [EXP-008](fixes/EXP-008-persons-format.md) | medium | Формат: (for N persons) |
| [EXP-009](fixes/EXP-009-missing-time.md) | high | Время для яхт/туров обязательно |
| [EXP-010](fixes/EXP-010-old-office-address.md) | medium | Новый адрес: DAMAC SMART HEIGHTS |

---

## Improvements (улучшения)

| ID | Severity | Описание |
|----|----------|----------|
| — | — | Пока нет записей |

---

## Patterns (паттерны)

| ID | Описание |
|----|----------|
| — | Пока нет записей |

---

## Warnings (что НЕ делать)

| ID | Severity | Описание |
|----|----------|----------|
| — | — | Пока нет записей |

---

## Теги

`дата` `формат` `американский` `VAT` `НДС` `расчёт` `5%` `телефон` `международный` `+971` `+7` `POS` `комиссия` `B2B` `Marsel` `Sokol` `реквизиты` `банк` `номер` `инвойс` `#YY-XXX` `USD` `AED` `конвертация` `СНГ` `персоны` `for-persons` `время` `яхты` `туры` `адрес` `DAMAC`

---

## Legacy

Оригинальный файл сохранён: `references/troubleshooting.md`
