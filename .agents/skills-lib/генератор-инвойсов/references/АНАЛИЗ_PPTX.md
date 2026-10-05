# Детальный анализ PPTX инвойсов Marsel Luxury Car Rental

**Дата анализа:** Январь 2026
**Количество проанализированных файлов:** 9 штук
**Формат:** PowerPoint (.pptx)

---

## 1. Общая информация о файлах

### 1.1 Структура документов

| Файл | Слайдов | Элементов | Таблиц | Изображений | Бренд |
|------|---------|-----------|--------|-------------|-------|
| INVOICE-26-398-v3.pptx (ЭТАЛОН) | 1 | 41 | 1 (4x6) | 6 | Marsel |
| INVOICE 22-0121.pptx | 1 | 41 | 1 (6x8) | 6 | Marsel |
| INVOICE 22-0129.pptx | 2 | 29+14 | 1 (4x8) | 1+5 | Marsel |
| INVOICE 22-0344.pptx | 1 | 40 | 1 (2x7) | 6 | Marsel |
| INVOICE 22-0552.pptx | 1 | 46 | 1 (2x8) | 8 | Marsel |
| INVOICE 22-0554.pptx | 1 | 42 | 1 (2x5) | 6 | Marsel |
| INVOICE 22-0599.pptx | 1 | 38 | 1 (2x7) | 3 | Marsel |
| INVOICE 22-0802.pptx | 1 | 40 | 1 (6x7) | 6 | Marsel |
| sokolcarrental invoice to Michkov.pptx | 1 | 53 | 1 (11x5) | 8 | Sokol |

### 1.2 Размеры слайда

**Все файлы:** 8.26" x 11.68" (210mm x 297mm = формат A4)

---

## 2. Данные клиента (Bill To)

### 2.1 Форматы имени клиента

| Файл | Bill To | Формат имени |
|------|---------|--------------|
| ЭТАЛОН | MIRZAYEVA NILUFAR | CAPS (Фамилия Имя) |
| 22-0121 | KHOTINSKII IGOR OLEGOVICH | CAPS (Фамилия Имя Отчество) |
| 22-0129 | GREEN CODE + Customer Details | Компания + детали |
| 22-0344 | RMCOS TRADING L.L.C + TRN | Компания (LLC) + TRN |
| 22-0552 | ART OF TRAVEL LLC + Customer Details: Pavel | Компания + контакт |
| 22-0554 | STEALTH ENTERTAINMENT... + TRN | Компания (длинное) + TRN |
| 22-0599 | ALEKSASHIN MAKSIM + Customer Details | CAPS + дубль в деталях |
| 22-0802 | - (пустой шаблон) | Плейсхолдер |
| Sokol | MATVEY MICHKOV ANDREEVICH + Passport No. | CAPS + паспорт |

### 2.2 Паттерны заполнения данных клиента

**Физические лица:**
- Формат: `Bill To: ФАМИЛИЯ ИМЯ [ОТЧЕСТВО]`
- Регистр: **ВСЕ ЗАГЛАВНЫЕ БУКВЫ (CAPS)**
- Дополнительно: `Customer Details:` или `Passport No.:`

**Юридические лица:**
- Формат: `Bill To: НАЗВАНИЕ КОМПАНИИ L.L.C/LLC`
- TRN (Tax Registration Number): `TRN: XXXXXXXXXXXXXXX`
- Customer Details: имя контактного лица

### 2.3 Формат телефона клиента

| Файл | Contact number | Формат |
|------|---------------|--------|
| ЭТАЛОН | +7 701 863 0653 | +X XXX XXX XXXX |
| 22-0121 | + 79679585535 | + XXXXXXXXXXX |
| 22-0129 | +90 530 916 0548 | +XX XXX XXX XXXX |
| 22-0344 | +971501809438 | +XXXXXXXXXXXX |
| 22-0552 | +37126523814 | +XXXXXXXXXXX |
| 22-0554 | +971 50 588 9068 | +XXX XX XXX XXXX |
| 22-0599 | +79270380262 | +XXXXXXXXXXX |
| 22-0802 | - | Плейсхолдер |
| Sokol | +7 910 665 7739 | +X XXX XXX XXXX |

**Вывод:** Формат телефона **не стандартизирован** - используются разные форматы в зависимости от страны.

### 2.4 Адрес клиента

| Тип | Примеры |
|-----|---------|
| Краткий | `Address: UAE`, `Address: Latvia` |
| Полный | `AL ABBAS BLDG. 2, OFFICE 136, BANK STREET, BURDUBAI, DUBAI, 117537, DUBAI` |
| Пустой | `Address: -` |

---

## 3. Типы услуг (ОПИСАНИЕ в таблице)

### 3.1 Полный список найденных услуг

#### Туры и экскурсии

| Файл | Описание услуги | Формат даты/времени |
|------|-----------------|---------------------|
| ЭТАЛОН | PRIVATE TOUR IN DUBAI (for 2 persons) 28 JANUARY, START AT 10:00 AM | DD MONTH, START AT HH:MM AM/PM |
| ЭТАЛОН | PRIVATE TOUR IN DUBAI - CONTINUATION (for 2 persons) 29 JANUARY, START AT 10:00 AM | DD MONTH, START AT HH:MM AM/PM |
| ЭТАЛОН | PRIVATE JEEP SAFARI TOUR (for 2 persons) 30 JANUARY | DD MONTH |
| ЭТАЛОН | PRIVATE TOUR IN ABU DHABI (for 2 persons) 1 FEBRUARY, START AT 9:00 AM | D MONTH, START AT H:MM AM |
| 22-0599 | PRIVATE DUBAI MODERN TOUR FROM 09:00 TO 16:00. PICK-UP BY TOYOTA HIACE CAR FROM FZ 974 KZN-DXB (TERMINAL 2) | FROM HH:MM TO HH:MM |

#### Яхты

| Файл | Описание услуги |
|------|-----------------|
| 22-0121 | YACHT HEIGAN 90 FEET |
| 22-0129 | YACHT RENTING IN DUBAI: MAJESTY 48 FT NEW (5 HOURS). RENTAL TIME FROM 15:30 TO 20:30. |
| 22-0344 | RENT AN INFINITY CATAMARAN 60 FEET FROM 17:00 TO 22:00 |
| 22-0554 | STEALTH YACHT BOOKING ON 8 NOVEMBER 15:30-20:30 TRIP COMMISSION 3937 AED |

#### Трансферы

| Файл | Описание услуги |
|------|-----------------|
| 22-0129 | TRANSFER RT FROM RIXOS THE PALM DUBAI HOTEL & SUITES (ADDRESS: THE PALM JUMEIRAH...) TO THE PORT (ADDRESS DUBAI MARINA HARBOUR) DATE 16.02.23 TIME 15:00 BY MERCEDES V CLASS AND BACK TRANSFER AT 20:30 - 2 CARS. |

#### Кейтеринг

| Файл | Описание услуги |
|------|-----------------|
| 22-0121 | LEVEL UP CATERING |
| 22-0129 | CATERING ON THE YACHT MAJESTY 48 FT NEW. DATE 16.02.23 TIME - FROM 15:30 till 20:30, NUMBER OF PEOPLE - 7 PERSON. (+ подробное MENU) |

#### Прочие услуги

| Файл | Описание услуги |
|------|-----------------|
| 22-0121 | PROFESSIONAL DJ |
| 22-0121 | JET SKI ( Water ATV 1800CC ) |
| 22-0552 | DUBAI PRIVATE HORSE RIDING ON THE BEACH FOR 2 HOURS |

### 3.2 Формат указания количества персон

- `(for 2 persons)` - в ЭТАЛОНЕ
- `NUMBER OF PEOPLE - 7 PERSON` - в кейтеринге
- `2 Rides` - в колонке Quantity

### 3.3 Формат даты в описаниях

| Формат | Пример | Файлы |
|--------|--------|-------|
| DD MONTH | 28 JANUARY, 30 JANUARY | ЭТАЛОН |
| D MONTH | 1 FEBRUARY | ЭТАЛОН |
| DD.MM.YY | 16.02.23 | 22-0129 |
| D MONTH | 8 NOVEMBER | 22-0554 |

### 3.4 Формат времени в описаниях

| Формат | Пример | Файлы |
|--------|--------|-------|
| START AT HH:MM AM/PM | START AT 10:00 AM, START AT 9:00 AM | ЭТАЛОН |
| FROM HH:MM TO HH:MM | FROM 17:00 TO 22:00, FROM 09:00 TO 16:00 | 22-0344, 22-0599 |
| HH:MM-HH:MM | 15:30-20:30 | 22-0554 |
| TIME HH:MM | TIME 15:00 | 22-0129 |

---

## 4. Структура таблицы цен

### 4.1 Колонки таблицы

**ЭТАЛОН (новый формат):**
| # | DESCRIPTION | Price (Excl. VAT) AED | Amount (Excl. VAT) AED | VAT 5%, Amount, AED | Amount (Incl. VAT), AED |
|---|-------------|----------------------|------------------------|---------------------|-------------------------|
| 1 | [услуга] | 238,10 USD | 238,10 USD | 11,90 USD | 250 USD |

**Старый формат (22-0121, 22-0129, 22-0552, 22-0599):**
| # | DESCRIPTION | hours | Quantity | Price (Excl. VAT) $ | Amount (Excl. VAT) $ | VAT 5%, Amount, $ | Amount (Incl. VAT), $ |
|---|-------------|-------|----------|---------------------|----------------------|-------------------|----------------------|

**Упрощённый формат (22-0554):**
| # | DESCRIPTION | Price | VAT | Amount |
|---|-------------|-------|-----|--------|

### 4.2 Формат цен

**ЭТАЛОН (USD с конвертацией в AED):**
```
238,10 USD / 11,90 USD / 250 USD
Total in USD: 1050,00 USD
Total in AED (1 USD=3,65 AED): 3832,50 AED
```

**Старые инвойсы ($ или AED):**
- В долларах: `1 000,00 $`, `602,30 $`, `5212,00 $`
- В дирхамах: `3080 AED`, `16170 AED`, `3937,00 AED`

**Разделители:**
- Десятичный: запятая (,)
- Тысячный: пробел или точка

### 4.3 Расчёт VAT

**Формула:** `VAT = Amount (Excl. VAT) * 0.05`

**Пример из ЭТАЛОНА:**
- Price (Excl. VAT): 238,10 USD
- VAT 5%: 11,90 USD (238,10 * 0.05 = 11.905, округлено)
- Amount (Incl. VAT): 250 USD

**Важно:** В некоторых инвойсах VAT = 0 (не облагается)

---

## 5. POS Terminal

### 5.1 Файлы с POS Terminal

| Файл | Текст | Процент | Сумма |
|------|-------|---------|-------|
| 22-0552 | PAYMENT VIA POS TERMINAL + 4% | 4% | 21,92 $ |

### 5.2 Формат строки POS Terminal

```
PAYMENT VIA POS TERMINAL + 4%
[Сумма комиссии в USD]
[Итого в AED]
```

**Расположение:** Отдельные текстбоксы под таблицей:
- TextBox 13: текст "PAYMENT VIA POS TERMINAL + 4%"
- TextBox 14: сумма комиссии "21,92 $"
- TextBox 17: итого в AED "2180,00 AED"

---

## 6. Банковские реквизиты

### 6.1 Marsel Luxury Car Rental

**Новый формат (ЭТАЛОН, 22-0344, 22-0599, 22-0802):**
```
COMPANY BANK ACCOUNT
ADIB BANK : UAE
COMPANY NAME : MARSEL LUXURY CAR RENTAL
ACCOUNT NO : 28642584 (ЭТАЛОН) / 19064835 (остальные)
IBAN : 110500000000028642584 / 110500000000019064835
CURRENCY : AED
```

**Старый формат (22-0121):**
```
Bank account details:
BANK : TINKOFF ( NEW )
CARD NUMBER : 5280413752588751
FULL NAME : MARSEL GANEEV
```

**Формат 22-0129:**
```
COMPANY BANK ACCOUNT
ADIB BANK: UAE
COMPANY NAME: MARSEL LUXURY CAR RENTAL
ACCOUNT NO: 19064835
IBAN: AE110500000000019064835
SWIFT : ABDIAEADXXX
CURRENCY: AED
```

### 6.2 Sokol Car Rental L.L.C

```
Bank Account Details
Bank: ADIB Bank (UAE)
Company Name: SOKOL CAR RENTAL L.L.C
Account No.: 19346595
IBAN: AE070500000000019346595
Currency: AED
```

### 6.3 Сводка банковских реквизитов

| Параметр | Marsel (новый) | Marsel (ЭТАЛОН) | Sokol |
|----------|---------------|-----------------|-------|
| Банк | ADIB BANK | ADIB BANK | ADIB Bank |
| Компания | MARSEL LUXURY CAR RENTAL | MARSEL LUXURY CAR RENTAL | SOKOL CAR RENTAL L.L.C |
| Account No. | 19064835 | 28642584 | 19346595 |
| IBAN | AE110500000000019064835 | 110500000000028642584 | AE070500000000019346595 |
| SWIFT | ABDIAEADXXX | - | - |
| Currency | AED | AED | AED |

---

## 7. Визуальные элементы

### 7.1 Логотип

| Элемент | Позиция | Размер |
|---------|---------|--------|
| object 8 (маленький логотип) | left: 7.92", top: 0.41" | 0.09" x 0.09" |

### 7.2 Шрифты

**Все файлы используют:**
- Arial
- Segoe UI
- Microsoft Sans Serif

### 7.3 Цвета

| Цвет | HEX | Назначение |
|------|-----|------------|
| Тёмно-серый | #3B3B3B, #3A3A3A, #3C3C3C, #3D3D3D | Основной текст |
| Чёрный | #1F1F1F, #211F1F, #201F1F | Заголовки |
| Белый | #FFFFFF | Фон таблиц |

### 7.4 Печать и подпись

**Изображения в нижней части (футер):**
- object 27/51 - иконка телефона (left: ~0.89", top: ~10.99")
- object 32/56 - иконка места (left: ~1.55", top: ~10.99")
- object 63 - иконка Instagram (left: ~2.47", top: ~10.99")
- object 62 - иконка сайта (left: ~4.08", top: ~10.99")
- object 57 - иконка email (left: ~6.23", top: ~10.99")

**Печать/штамп (в некоторых файлах):**
- Рисунок 19, 20 (22-0552) - печати
- object 65, Рисунок 73 (Sokol) - печати

---

## 8. Офисный адрес компании

### 8.1 Старый адрес (22-0121, 22-0129, 22-0552, 22-0554, 22-0599)

```
AL FALAHI BUILDING, 312-931,
Al Suq Al Kabeer Plot 184-0,
Dubai, United Arab Emirates,
MAKANI NUMBER: 27840 94964
```

### 8.2 Новый адрес (ЭТАЛОН, 22-0344, 22-0802, Sokol)

```
DAMAC SMART HEIGHTS BUILDING, OFFICE NUMBER 2106/2109
```

---

## 9. Формат Invoice Date

| Файл | Invoice Date | Формат |
|------|--------------|--------|
| ЭТАЛОН | Jan 22, 2026 | Mon DD, YYYY |
| 22-0121 | August 01, 2022 | Month DD, YYYY |
| 22-0129 | March 22, 2023 | Month DD, YYYY |
| 22-0344 | May 21, 2024 | Month DD, YYYY |
| 22-0552 | October 31, 2023 | Month DD, YYYY |
| 22-0554 | November 06, 2023 | Month DD, YYYY |
| 22-0599 | December 19, 2023 | Month DD, YYYY |
| 22-0802 | January 23, 2025 | Month DD, YYYY |
| Sokol | May 31, 2025 | Month DD, YYYY |

**Стандартный формат:** `Month DD, YYYY` (полное название месяца)
**ЭТАЛОН использует:** `Mon DD, YYYY` (сокращённый месяц)

---

## 10. Номер инвойса

| Файл | Номер | Формат |
|------|-------|--------|
| ЭТАЛОН | #26-398 | #YY-XXX |
| 22-0121 | #22-0121 | #YY-XXXX |
| 22-0129 | #22-0129 | #YY-XXXX |
| 22-0344 | #22-344 | #YY-XXX |
| 22-0552 | #22-0552 | #YY-XXXX |
| 22-0554 | #22-0554 | #YY-XXXX |
| 22-0599 | #22-598 | #YY-XXX |
| 22-0802 | #22-802 | #YY-XXX |
| Sokol | #22-816 | #YY-XXX |

**Вывод:** Формат `#YY-XXXX` или `#YY-XXX` (год-порядковый номер)

---

## 11. Уникальные особенности файлов

### 11.1 22-0121

- Есть поле **Period** (from 01-08-22 to 02-08-22)
- Банк **Tinkoff** (российская карта) вместо ADIB
- **Notes** с ручным расчётом

### 11.2 22-0129

- **2 слайда** (единственный многостраничный)
- Детальное **MENU** кейтеринга с ценами
- Есть поле **Customer Details** отдельно от Bill To

### 11.3 22-0344

- Клиент **юридическое лицо с TRN**
- Цены только в **AED** (не USD)

### 11.4 22-0552

- Есть **POS TERMINAL + 4%**
- Есть **печать и подпись** (Рисунок 19, 20)
- Итого в двух валютах (USD и AED)

### 11.5 22-0554

- Упрощённая таблица (5 колонок)
- Нет колонки Quantity
- Только AED

### 11.6 22-0599

- Дополнительные контакты в футере (gid_uae)
- Телефон в формате Russian (+7)

### 11.7 22-0802

- **Пустой шаблон** (все поля "-")
- Новый офисный адрес

### 11.8 Sokol (Michkov)

- **Другой бренд** (Sokol Car Rental L.L.C)
- **Другой логотип** (Рисунок 71, большой)
- **Паспортные данные** вместо TRN
- Сложная таблица с компенсациями (11 строк)
- **Другие банковские реквизиты**
- **Две печати** (Рисунок 73, object 65)

---

## 12. Сводная таблица различий

| Параметр | ЭТАЛОН | Старые (22-0121...) | Sokol |
|----------|--------|---------------------|-------|
| Офис | DAMAC SMART HEIGHTS | AL FALAHI BUILDING / DAMAC | DAMAC SMART HEIGHTS |
| Банк | ADIB (28642584) | ADIB (19064835) / Tinkoff | ADIB (19346595) |
| Валюта цен | USD (с конвертацией) | USD или AED | AED |
| Колонки таблицы | 6 | 5-8 | 5 |
| Invoice Date | Mon DD, YYYY | Month DD, YYYY | Month DD, YYYY |
| Лицензия | 1024110 | 1024110 | 1442819 |
| Арабский текст | Marsel | Marsel | Sokol |
| Website | marsel-luxurycarrental.com | marsel-luxurycarrental.com | sokol-carrental.com |
| Email | Info@marsel-luxurycarrental.com | Info@marsel-luxurycarrental.com | Info@sokol-carrental.com |

---

## 13. Рекомендации для создания инвойсов

### 13.1 Обязательные элементы

1. **Заголовок** "INVOICE" + номер (#YY-XXX)
2. **Licence Number** (1024110 для Marsel)
3. **Invoice Date** в формате Month DD, YYYY
4. **Bill To** с именем клиента в CAPS
5. **Contact number** клиента
6. **Issued By** + полные реквизиты компании
7. **Таблица услуг** с VAT 5%
8. **Total** в USD и AED
9. **Банковские реквизиты** ADIB
10. **Футер** с иконками и контактами

### 13.2 Стандартные значения

- **Размер слайда:** A4 (8.26" x 11.68")
- **Шрифты:** Arial, Segoe UI
- **Цвет текста:** #3B3B3B
- **VAT:** 5%
- **Курс USD/AED:** 3.65

---

*Документ создан автоматически на основе анализа 9 PPTX файлов*
