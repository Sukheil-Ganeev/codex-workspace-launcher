# Типичные ошибки при генерации инвойсов

**Версия:** 1.0
**Дата:** 22 января 2026

---

## Ошибка 1: Неправильный формат даты

### Проблема
Дата инвойса указана в неверном формате - используется русский или европейский формат вместо американского.

### Пример неправильно
```
Invoice Date: 22.01.2026
Invoice Date: 22 января 2026
Invoice Date: 2026-01-22
```

### Пример правильно
```
Invoice Date: Jan 22, 2026
Invoice Date: January 22, 2026
```

### Как избежать
Всегда используй формат **Mon DD, YYYY** (сокращённый месяц) или **Month DD, YYYY** (полный месяц). Месяц пишется по-английски, после числа ставится запятая.

---

## Ошибка 2: Ошибка в расчёте VAT

### Проблема
VAT рассчитан неправильно - использована неверная ставка, неправильная база для расчёта или ошибка округления.

### Пример неправильно
```
Amount (Excl. VAT): 1000 AED
VAT 5%, Amount: 52.50 AED       ← Неверный расчёт (5.25%)
Amount (Incl. VAT): 1052.50 AED

Amount (Excl. VAT): 1000 AED
VAT 5%, Amount: 50 AED
Amount (Incl. VAT): 1100 AED    ← Итог не сходится
```

### Пример правильно
```
Amount (Excl. VAT): 1000 AED
VAT 5%, Amount: 50.00 AED       ← 1000 * 0.05 = 50
Amount (Incl. VAT): 1050.00 AED ← 1000 + 50 = 1050
```

### Как избежать
Формула VAT: `Amount (Excl. VAT) * 0.05`. Округляй до 2 знаков после запятой. Всегда проверяй: `Excl. VAT + VAT = Incl. VAT`.

---

## Ошибка 3: Неправильный формат телефона

### Проблема
Телефон указан без кода страны или в локальном формате.

### Пример неправильно
```
Contact number: 050 588 9068
Contact number: 8 999 990 01 07
Contact number: (050) 588-9068
```

### Пример правильно
```
Contact number: +971 50 588 9068
Contact number: +7 999 990 01 07
Contact number: +971501809438
```

### Как избежать
Всегда указывай международный код страны: +971 (ОАЭ), +7 (Россия/Казахстан), +90 (Турция). Формат пробелов может варьироваться, но код страны обязателен.

---

## Ошибка 4: POS Terminal с неверным процентом

### Проблема
Указан неправильный процент комиссии POS Terminal или комиссия добавлена, когда не нужна.

### Пример неправильно
```
PAYMENT VIA POS TERMINAL + 5%      ← Неверный процент
PAYMENT VIA POS TERMINAL + 3%      ← Слишком мало

# Или добавлена для B2B клиента, который платит переводом:
Bill To: RMCOS TRADING L.L.C
...
PAYMENT VIA POS TERMINAL + 4%      ← Не нужна для юр.лица
```

### Пример правильно
```
# Стандартный клиент (физ.лицо, оплата картой):
PAYMENT VIA POS TERMINAL + 4%

# VIP/корпоративный клиент:
PAYMENT VIA POS TERMINAL + 3.5%

# B2B клиент (юр.лицо) - НЕ добавлять POS Terminal вообще
```

### Как избежать
- Стандартная комиссия: **4%**
- VIP клиенты: **3.5%**
- Для юридических лиц (оплата переводом) - **не добавлять** POS Terminal

---

## Ошибка 5: Смешивание реквизитов Marsel и Sokol

### Проблема
В одном инвойсе используются реквизиты разных компаний - например, логотип Marsel с банковскими реквизитами Sokol.

### Пример неправильно
```
Шапка: Marsel Luxury Car Rental, Licence: 1024110
...
COMPANY BANK ACCOUNT
Company Name: SOKOL CAR RENTAL L.L.C    ← Реквизиты другой компании!
Account No.: 19346595
IBAN: AE070500000000019346595
```

### Пример правильно
```
# Если Marsel:
Шапка: Marsel Luxury Car Rental, Licence: 1024110
...
COMPANY BANK ACCOUNT
COMPANY NAME: MARSEL LUXURY CAR RENTAL
ACCOUNT NO: 28642584
IBAN: 110500000000028642584

# Если Sokol:
Шапка: Sokol Car Rental L.L.C, Licence: 1442819
...
Bank Account Details
Company Name: SOKOL CAR RENTAL L.L.C
Account No.: 19346595
IBAN: AE070500000000019346595
```

### Как избежать
Перед генерацией определи бренд. Все элементы (логотип, Licence, банковские реквизиты, офис) должны соответствовать одной компании:
- **Marsel**: туры, трансферы, яхты, билеты, краткосрочная аренда
- **Sokol**: долгосрочная аренда авто

---

## Ошибка 6: Неверный формат номера инвойса

### Проблема
Номер инвойса не соответствует стандартному формату #YY-XXX.

### Пример неправильно
```
Invoice #: 398
Invoice: 2026-398
Invoice #: INV-26-398
Invoice #: 26398
```

### Пример правильно
```
Invoice #: #26-398
Invoice #: #26-0121
Invoice #: #22-1234
```

### Как избежать
Формат: **#YY-XXX** или **#YY-XXXX**, где:
- YY = последние 2 цифры года (26 для 2026)
- XXX/XXXX = порядковый номер (3-4 цифры)
- Символ # обязателен в начале

---

## Ошибка 7: Забыли конвертацию USD/AED

### Проблема
Для клиентов из СНГ цены указаны только в одной валюте без конвертации.

### Пример неправильно
```
# Клиент из России, цены в USD:
Total: 2230 USD
← Нет конвертации в AED
```

### Пример правильно
```
# Клиент из России, цены в USD:
Total in USD: 2230 USD
Total in AED (1 USD=3,65 AED): 8139,50 AED
```

### Как избежать
Для клиентов из СНГ (Россия, Казахстан, Украина):
- Показывай цены в USD
- Добавляй конвертацию в AED
- Курс: **1 USD = 3.65 AED** (константа)

---

## Ошибка 8: Неправильное количество персон в описании

### Проблема
Количество персон не указано или указано в неверном формате.

### Пример неправильно
```
PRIVATE TOUR IN DUBAI 28 JANUARY, START AT 10:00 AM
← Нет количества персон

PRIVATE TOUR IN DUBAI (2 persons) 28 JANUARY
← Нет "for"

PRIVATE TOUR IN DUBAI (for two persons) 28 JANUARY
← Текстом вместо цифры
```

### Пример правильно
```
PRIVATE TOUR IN DUBAI (for 2 persons) 28 JANUARY, START AT 10:00 AM
PRIVATE JEEP SAFARI TOUR (for 4 persons) 30 JANUARY
PRIVATE TOUR IN ABU DHABI (for 2 persons) 1 FEBRUARY, START AT 9:00 AM
```

### Как избежать
Формат: **(for N persons)** - всегда указывай количество цифрой, используй "for" и "persons".

---

## Ошибка 9: Отсутствие времени для яхт/туров

### Проблема
Для услуг, требующих времени (яхты, туры), не указано время начала/окончания.

### Пример неправильно
```
YACHT RENTING IN DUBAI: MAJESTY 48 FT NEW (5 HOURS)
← Нет конкретного времени

PRIVATE TOUR IN DUBAI (for 2 persons) 28 JANUARY
← Нет времени начала
```

### Пример правильно
```
YACHT RENTING IN DUBAI: MAJESTY 48 FT NEW (5 HOURS). RENTAL TIME FROM 15:30 TO 20:30.
RENT AN INFINITY CATAMARAN 60 FEET FROM 17:00 TO 22:00

PRIVATE TOUR IN DUBAI (for 2 persons) 28 JANUARY, START AT 10:00 AM
PRIVATE DUBAI MODERN TOUR FROM 09:00 TO 16:00
```

### Как избежать
Всегда указывай время:
- Яхты: **FROM HH:MM TO HH:MM** или **(N HOURS). RENTAL TIME FROM HH:MM TO HH:MM**
- Туры: **START AT HH:MM AM/PM** или **FROM HH:MM TO HH:MM**

---

## Ошибка 10: Неверный адрес офиса (старый vs новый)

### Проблема
Использован устаревший адрес офиса для новых инвойсов.

### Пример неправильно
```
# Инвойс 2026 года с СТАРЫМ адресом:
Address: AL FALAHI BUILDING, 312-931, Al Suq Al Kabeer Plot 184-0, Dubai, UAE
```

### Пример правильно
```
# Инвойс 2024-2026 года:
# Marsel:
Address: DAMAC SMART HEIGHTS BUILDING, OFFICE NUMBER 2109

# Sokol:
Address: DAMAC SMART HEIGHTS BUILDING, OFFICE NUMBER 2106
```

### Как избежать
- **2024-2026**: DAMAC SMART HEIGHTS BUILDING
  - Marsel: офис **2109**
  - Sokol: офис **2106**
- До 2024: AL FALAHI BUILDING (только для архивных документов)

---

*Документ создан на основе анализа типичных ошибок при генерации инвойсов Marsel/Sokol*
