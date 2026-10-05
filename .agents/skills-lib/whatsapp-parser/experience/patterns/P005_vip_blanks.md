# P005: Парсинг VIP Transfer Blank из чатов

**Дата:** 2026-02-05
**Severity:** HIGH
**Проект:** MARSEL_BUSINESS (лимузинные партнёры)

## Контекст

В лимузинных чатах заказы оформляются через стандартизированный бланк "VIP Transfer Blank", отправляемый текстом в WhatsApp.

## Формат бланка

```
VIP Transfer Blank:
ORDER DATE: 15/11/2022
MEETING TIME: 14:00
TRANSPORT MODEL: Lexus ES 350
FULL NAME: John Smith
CONTACT NUMBER: +971 50 123 4567
PICK UP: Dubai Mall
DROP OFF: Dubai Airport Terminal 3
FLIGHT NUMBER: EK 302
HOURS: 3
RATE: 180 AED
REMARKS: VIP guest, meet & greet
```

## Regex для извлечения

```python
BLANK_START = re.compile(r'VIP\s+Transfer\s+Blank', re.IGNORECASE)

FIELDS = {
    'order_date': re.compile(r'ORDER\s+DATE[:\s]*(.+)', re.IGNORECASE),
    'meeting_time': re.compile(r'MEETING\s+TIME[:\s]*(.+)', re.IGNORECASE),
    'transport': re.compile(r'TRANSPORT\s+MODEL[:\s]*(.+)', re.IGNORECASE),
    'full_name': re.compile(r'FULL\s+NAME[:\s]*(.+)', re.IGNORECASE),
    'contact': re.compile(r'CONTACT\s+NUMBER[:\s]*(.+)', re.IGNORECASE),
    'pickup': re.compile(r'PICK\s*UP[:\s]*(.+)', re.IGNORECASE),
    'dropoff': re.compile(r'DROP\s*OFF[:\s]*(.+)', re.IGNORECASE),
    'flight': re.compile(r'FLIGHT\s+(?:NUMBER|NO|#)[:\s]*(.+)', re.IGNORECASE),
    'hours': re.compile(r'HOURS?[:\s]*(.+)', re.IGNORECASE),
    'rate': re.compile(r'RATE[:\s]*(.+)', re.IGNORECASE),
    'remarks': re.compile(r'REMARKS?[:\s]*(.+)', re.IGNORECASE),
}
```

## Результат

- 113 бланков извлечено из 3 чатов (2021-2025)
- Пик: 2022 год — 46 заказов
- Скрипт: `D:/MARSEL_BUSINESS/08_automation/importers/extract_orders.py`

**Теги:** #заказы #бланк #regex #CRM
