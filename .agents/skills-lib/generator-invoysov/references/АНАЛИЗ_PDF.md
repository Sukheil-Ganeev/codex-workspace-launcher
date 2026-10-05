# Анализ PDF-инвойсов Marsel Luxury Car Rental и Sokol Car Rental

> **Дата анализа:** 22 января 2026
> **Количество проанализированных файлов:** 9 (7 Marsel + 2 Sokol)

---

## Содержание

1. [Общая информация о компаниях](#1-общая-информация-о-компаниях)
2. [Данные клиентов](#2-данные-клиентов)
3. [Типы услуг](#3-типы-услуг)
4. [Структура таблицы цен](#4-структура-таблицы-цен)
5. [POS Terminal](#5-pos-terminal)
6. [Банковские реквизиты](#6-банковские-реквизиты)
7. [Визуальные элементы](#7-визуальные-элементы)
8. [Сводная таблица различий](#8-сводная-таблица-различий)

---

## 1. Общая информация о компаниях

### Marsel Luxury Car Rental

| Параметр | Значение |
|----------|----------|
| **Название (EN)** | Marsel Luxury Car Rental |
| **Название (AR)** | مارسیل لكشير لتأجیا رلسیاتار |
| **Licence Number** | 1024110 |
| **Телефон** | + 971 58 511 0777 (основной) / + 7 999 990-01-07 (альтернативный) |
| **Website** | www.marselluxurycarrental.com |
| **Email** | Info@marselluxurycarrental.com |
| **Instagram** | marsel_carrental / gid_uae |
| **Адрес (старый)** | AL FALAHI BUILDING, 312-931, Al Suq Al Kabeer Plot 184-0, Dubai, UAE, MAKANI NUMBER: 27840 94964 |
| **Адрес (новый)** | DAMAC SMART HEIGHTS BUILDING, OFFICE NUMBER 2109 |

### Sokol Car Rental L.L.C

| Параметр | Значение |
|----------|----------|
| **Название (EN)** | Sokol Car Rental L.L.C |
| **Название (AR)** | سوكول لتأجير السيارات ذ.م.م |
| **Licence Number** | 1442819 |
| **Телефон** | + 971 58 511 0777 |
| **Website** | www.sokol-carrental.com |
| **Email** | Info@sokol-carrental.com |
| **Адрес** | DAMAC SMART HEIGHTS BUILDING, OFFICE NUMBER 2106 |

---

## 2. Данные клиентов

### Таблица клиентов по инвойсам

| Инвойс | Bill To | Customer Details | Формат имени | Address | Contact Number | TRN |
|--------|---------|------------------|--------------|---------|----------------|-----|
| #22-0241 | Bektimir Kazbekov | Bektimir Kazbekov | Mixed Case | UAE | +77775001123 | - |
| #22-299 | Yemelyanov Yevgeniy | Yemelyanov Yevgeniy | Mixed Case | UAE | +77077777788 | - |
| #22-344 | RMCOS TRADING L.L.C | - | CAPS (компания) | AL ABBAS BLDG. 2, OFFICE 136, BANK STREET, BURDUBAI, DUBAI, 117537, DUBAI | +971501809438 | 104042090100003 |
| #22-598 | ALEKSASHIN MAKSIM | ALEKSASHIN MAKSIM | CAPS | UAE | +79270380262 | - |
| #22-644 | Joan Beaufort, Kristina Beaufort | - | Mixed Case (два имени) | - | +7 995 782-85-68 | - |
| #22-655 | Caspian Pipeline Consortium-R | - | Mixed Case (компания) | 7 PAVLOVSKAYA STR. BLDG.1 BUSINESS CENTRE PAVLOVSKY MOSCOW 115093 RUSSIA | +7 964 573 2866 | - |
| #22-701 | Huawei Technologies Kazakhstan Co., LTD | - | Mixed Case (компания) | - | - | - |
| Sokol #22-817 | MATVEY MICHKOV ANDREEVICH | - | CAPS | - | +7 910 665 7739 | - |

### Паттерны заполнения данных клиентов

#### Формат имени
- **Физ. лица (частные клиенты):** Встречается как Mixed Case (`Bektimir Kazbekov`), так и CAPS (`ALEKSASHIN MAKSIM`)
- **Юр. лица:** Обычно Mixed Case (`RMCOS TRADING L.L.C`, `Huawei Technologies Kazakhstan Co., LTD`)
- **Несколько лиц:** Через запятую (`Joan Beaufort, Kristina Beaufort`)

#### Формат телефона
| Страна | Формат | Примеры |
|--------|--------|---------|
| Казахстан | +7XXXXXXXXXX | +77775001123, +77077777788 |
| Россия | +7XXXXXXXXXX или +7 XXX XXX-XX-XX | +79270380262, +7 995 782-85-68 |
| ОАЭ | +971XXXXXXXXX | +971501809438 |

#### Поле Address
- **UAE** — стандартное значение для физ. лиц без адреса
- **-** — используется при отсутствии адреса
- **Полный адрес** — для юр. лиц (компаний)

#### Поле TRN (Tax Registration Number)
- Указывается только для B2B инвойсов
- Формат: 15 цифр (пример: `104042090100003`)
- Прочерк (-) для физ. лиц или отсутствует

#### Дополнительные поля (Sokol)
- **Passport No.** — номер паспорта клиента
- **Delivery to** — адрес доставки автомобиля
- **Vehicle** — модель автомобиля
- **Plate** — номер автомобиля
- **Agreement** — номер договора аренды

---

## 3. Типы услуг

### Полный перечень услуг из инвойсов

#### Трансферы и аренда с водителем

| Инвойс | Описание услуги | Формат даты | Формат времени |
|--------|-----------------|-------------|----------------|
| #22-0241 | MEETING AT THE AIRPORT AND TRANSFER TO THE HOTEL BY LEXUS ES350 CAR | DATE: 04.10.2023 | - |
| #22-0241 | CAR WITH DRIVER FOR 10 HOURS IN A LEXUS ES350 | DATE: 05.10.2023 | - |
| #22-0241 | PICK UP FROM THE HOTEL AND TRANSFER TO THE AIRPORT BY LEXUS ES350 CAR | DATE: 06.10.2023 | - |
| #22-598 | PRIVATE DUBAI MODERN TOUR FROM 09:00 TO 16:00. PICK-UP BY TOYOTA HIACE CAR FROM FZ 974 KZN-DXB (TERMINAL 2) | (в описании) | FROM 09:00 TO 16:00 |
| #22-655 | TRANSFER ON MERCEDES S-CLASS WITH DRIVER | START: 14 OCTOBER | DEPARTURE AT 5:30 AM, ARRIVAL AT 5:30 PM |
| #22-655 | TRANSFER ON MERCEDES V-CLASS WITH DRIVER | START: 14/15 OCTOBER | DEPARTURE AT X:XX AM/PM, ARRIVAL AT X:XX PM |

**Паттерн трансфера (инвойс #22-655):**
```
TRANSFER ON [МАРКА АВТО] WITH DRIVER
START: [ДАТА], DEPARTURE AT [ВРЕМЯ], ARRIVAL AT [ВРЕМЯ],
TOTAL OF [ЧЧ:ММ]. EXTRA [N] HOURS TO BE PAID.
```

#### Шоу и развлечения

| Инвойс | Описание услуги | Формат персон |
|--------|-----------------|---------------|
| #22-299 | LA PERLE SHOW BY DRAGON SILVER CATEGORY FOR 2 ADULT | FOR [N] ADULT |
| #22-299 | LA PERLE SHOW BY DRAGON SILVER CATEGORY FOR 2 CHILD | FOR [N] CHILD |

#### Яхты и катамараны

| Инвойс | Описание услуги | Формат времени |
|--------|-----------------|----------------|
| #22-344 | RENT AN INFINITY CATAMARAN 60 FEET | FROM 17:00 TO 22:00 |

#### Аренда автомобилей

| Инвойс | Описание услуги | Формат периода |
|--------|-----------------|----------------|
| #22-644 | EXTENSION OF THE RENTAL PERIOD FOR ROLLS-ROYCE CULLINAN VIP BLACK BADGE 2023 | Quantity: 1 Day |
| #22-644 | RETURNABLE DEPOSIT (DEPOSIT AMOUNT WILL BE CONSIDERED ONLY 4000 AED, VAT WILL BE PAID TO THE TAX AUTHORITY) | Quantity: 1 Day |

#### Билеты

| Инвойс | Описание услуги | Язык |
|--------|-----------------|------|
| #22-701 | БИЛЕТЫ В АКВАРИУМ ДУБАЙ МОЛЛ С ПОДВОДНЫМ ЗООПАРКОМ И БУХТОЙ ПИНГВИНОВ | Русский |

### Sokol Car Rental — специфические услуги

| # | Описание | Комментарий |
|---|----------|-------------|
| 1 | Outstanding vehicle value not covered by insurance (298,000 - 198,000) | Разница страховки |
| 2 | Non-refundable insurance premium | Страховая премия |
| 3 | GPS equipment cost | Оборудование |
| 4 | PPF protective film cost | Защитная пленка |
| 5 | Rental charges (03 May 2025 - 30 Jul 2025), 88 days x 750 AED/day (Excl. VAT) | Аренда с периодом |
| 6 | VAT 5% on rental charges (Item #5) | НДС отдельной строкой |
| 7 | Traffic fines (see Annex A for breakdown) | Штрафы |
| 8 | Insurance policy excess amount (Total Loss) | Франшиза |
| 9 | Salik toll charges (13 gates) | Дорожные сборы |

### Формат даты в описаниях

| Формат | Пример | Инвойсы |
|--------|--------|---------|
| DATE: DD.MM.YYYY | DATE: 04.10.2023 | #22-0241 |
| FROM HH:MM TO HH:MM | FROM 17:00 TO 22:00 | #22-344 |
| FROM HH:MM TO HH:MM (в тексте) | FROM 09:00 TO 16:00 | #22-598 |
| START: D MONTH | START: 14 OCTOBER | #22-655 |
| (DD MMM YYYY - DD MMM YYYY) | (03 May 2025 - 30 Jul 2025) | Sokol |

### Формат указания персон

| Формат | Пример | Использование |
|--------|--------|---------------|
| FOR [N] ADULT | FOR 2 ADULT | Билеты на шоу |
| FOR [N] CHILD | FOR 2 CHILD | Билеты на шоу |
| [N] (в Quantity) | 4 | Билеты в аквариум |

---

## 4. Структура таблицы цен

### Marsel Luxury Car Rental — стандартные колонки

| Колонка | Описание | Формат |
|---------|----------|--------|
| # | Номер позиции | Число |
| DESCRIPTION | Описание услуги | Текст CAPS |
| Quantity | Количество | Число или "1 Day" |
| Price (Excl. VAT) $ / AED | Цена без НДС | XX,XX $ или XXXX AED |
| Amount (Excl. VAT) $ / AED | Сумма без НДС | XX,XX $ или XXXX AED |
| VAT 5%, Amount, $ / AED | Сумма НДС 5% | XX,XX $ или XXX AED |
| Amount (Incl. VAT), $ / AED | Сумма с НДС | XXX,XX $ или XXXX AED |

### Sokol Car Rental — колонки

| Колонка | Описание | Формат |
|---------|----------|--------|
| # | Номер позиции | Число |
| DESCRIPTION | Описание услуги | Mixed Case |
| Quantity | Количество | Число |
| Unit Price (Excl. VAT) AED | Цена за единицу без НДС | XXX,XXX AED |
| Total Price (Excl. VAT) AED | Итого без НДС | XXX,XXX AED |

### Формат цен

| Валюта | Формат суммы | Примеры |
|--------|--------------|---------|
| USD ($) | XX,XX $ | 90,00 $, 343,00 $, 608,00 $ |
| AED | XXXX AED | 3080 AED, 5456 AED, 16170 AED |
| USD (инв. #22-655) | XX USD / XXX USD | 76 USD, 152 USD |

### Расчёт VAT

- **Ставка:** 5%
- **Расчёт:** Amount (Excl. VAT) * 0.05 = VAT Amount
- **Округление:** До целых или до сотых (зависит от инвойса)

### Формат итогов

| Инвойс | Валюта | Формат Total | Дополнительно |
|--------|--------|--------------|---------------|
| #22-0241 | USD | Total: 572,00 $ | С POS Terminal |
| #22-299 | USD | Total: 359,00 $ | С POS Terminal + Bank |
| #22-344 | AED | Total: 16170 AED | - |
| #22-598 | USD | Total: 640,00 $ | - |
| #22-644 | AED | Total: 9929 AED | - |
| #22-655 | USD/AED | Total in USD: 2230 USD, Total in AED (1 USD=3,65 AED): 8139,50 AED | Конвертация |
| #22-701 | AED | Total: 720 AED | - |
| Sokol | AED | TOTAL AMOUNT: 268,073 AED | + PAID/REMAINING |

### Дополнительные строки в итогах (Sokol)

```
TOTAL AMOUNT:      268,073 AED
PAID AMOUNT:        14,270 AED
REMAINING AMOUNT:  253,803 AED
```

---

## 5. POS Terminal

### Инвойсы с POS Terminal

| Инвойс | Строка | Процент | Сумма комиссии |
|--------|--------|---------|----------------|
| #22-0241 | PAYMENT VIA POS TERMINAL + 4% | 4% | 22,00 $ |
| #22-299 | PAYMENT VIA POS TERMINAL + 4% | 4% | 13,80 $ |
| #22-655 | PAYMENT VIA POS TERMINAL + 3.5% | 3.5% | 75,41 USD |

### Инвойсы БЕЗ POS Terminal

- #22-344 (B2B, оплата на счёт)
- #22-598
- #22-644
- #22-701
- Sokol #22-817

### Формат строки POS Terminal

```
PAYMENT VIA POS TERMINAL + X%    [сумма комиссии]
```

### Выводы по POS Terminal

1. Используется только при оплате картой через терминал
2. Комиссия варьируется: **3.5% или 4%**
3. Строка добавляется между таблицей услуг и Total
4. В B2B инвойсах обычно не используется (оплата банковским переводом)

---

## 6. Банковские реквизиты

### Marsel Luxury Car Rental

```
COMPANY BANK ACCOUNT
ADIB BANK : UAE
COMPANY NAME : MARSEL LUXURY CAR RENTAL
ACCOUNT NO : 19064835
IBAN : 110500000000019064835
CURRENCY : AED
```

**Вариации:**
- Присутствует во всех инвойсах, кроме #22-0241 (который содержит только POS Terminal)
- Формат неизменен во всех инвойсах

### Sokol Car Rental L.L.C

```
Bank Account Details
Bank: ADIB Bank (UAE)
Company Name: SOKOL CAR RENTAL L.L.C
Account No.: 19346595
IBAN: AE070500000000019346595
Currency: AED
```

### Сравнение реквизитов

| Параметр | Marsel | Sokol |
|----------|--------|-------|
| Банк | ADIB BANK | ADIB Bank (UAE) |
| Название компании | MARSEL LUXURY CAR RENTAL | SOKOL CAR RENTAL L.L.C |
| Account No. | 19064835 | 19346595 |
| IBAN | 110500000000019064835 | AE070500000000019346595 |
| Валюта | AED | AED |

**Примечание:** Формат IBAN у Marsel нестандартный (без AE в начале). У Sokol — корректный формат ОАЭ.

---

## 7. Визуальные элементы

### Логотип

| Компания | Расположение | Описание |
|----------|--------------|----------|
| Marsel | Правый верхний угол | Каллиграфический текст "Marsel Luxury" + CAR RENTAL, кольца с флагами ОАЭ |
| Sokol | Правый верхний угол | Красно-серый логотип с буквой S, текст "SOKOL CAR RENTAL" |

### Печать (штамп)

| Компания | Наличие | Описание |
|----------|---------|----------|
| Marsel | Да (в большинстве) | Круглая печать с надписью на арабском по кругу, в центре — "MARSEL LUXURY CAR RENTAL", "DUBAI-UAE", флаги ОАЭ |
| Sokol | Да | Круглая печать с логотипом Sokol в центре, надпись на арабском по кругу |

**Инвойсы без печати:**
- #22-0241 (первый инвойс, возможно черновик)

### Подпись

| Инвойс | Наличие | Описание |
|--------|---------|----------|
| Все Marsel | Да | Рукописная подпись справа от печати |
| Sokol | Да | Рукописная подпись справа от печати |

### Футер (нижний колонтитул)

**Marsel Luxury Car Rental:**
```
[WhatsApp icon] +971 58 511 0777  [Instagram icon] marsel_carrental  [Globe icon] marsel-luxurycarrental.com  [Email icon] info@marsel-luxurycarrental.com
```

**Sokol Car Rental:**
```
[WhatsApp icon] +971585110777  [Instagram icon] -  [Globe icon] www.sokol-carrental.com  [Email icon] Info@sokol-carrental.com
```

### Цветовая схема

| Элемент | Marsel | Sokol |
|---------|--------|-------|
| Шапка | Красная полоса сверху | Красная полоса сверху |
| Заголовок INVOICE | Чёрный bold | Чёрный bold |
| Таблица (заголовки) | Красный фон, белый текст | Красный фон, белый текст |
| Футер | Красная и зелёная полосы (флаг ОАЭ) | Красная и зелёная полосы (флаг ОАЭ) |

---

## 8. Сводная таблица различий

### Различия между инвойсами Marsel

| Параметр | Ранние (2023) | Поздние (2024) |
|----------|---------------|----------------|
| Адрес компании | AL FALAHI BUILDING | DAMAC SMART HEIGHTS |
| Телефон в футере | +971 58 511 0777 | +971 58 511 0777 (без изменений) |
| Телефон в шапке | + 971 58 511 0777 | + 7 999 990-01-07 (в #22-598) |
| Instagram | marsel_carrental | gid_uae (в #22-598) |

### Различия между Marsel и Sokol

| Параметр | Marsel | Sokol |
|----------|--------|-------|
| Licence Number | 1024110 | 1442819 |
| Офис | 2109 | 2106 |
| Формат описания услуг | CAPS | Mixed Case |
| Колонки таблицы | 5 колонок с VAT | 3 колонки (без VAT в таблице) |
| VAT | В каждой строке | Отдельной строкой (#6) |
| Дополнительные поля клиента | - | Passport No., Delivery to, Vehicle, Plate, Agreement |
| Итоги | Total | TOTAL/PAID/REMAINING |
| Вложения | - | Список Attachments |

### Формат номера инвойса

| Компания | Формат | Примеры |
|----------|--------|---------|
| Marsel | #22-XXXX | #22-0241, #22-299, #22-344, #22-598, #22-644, #22-655, #22-701 |
| Sokol | #22-XXX | #22-817 |

### Формат даты инвойса

| Формат | Примеры | Инвойсы |
|--------|---------|---------|
| Month DD, YYYY | October 04, 2023 | #22-0241 |
| Month DD, YYYY | December 17, 2023 | #22-299 |
| Month DD, YYYY | May 21, 2024 | #22-344 |
| Mon DD, YYYY | Oct 14, 2024 | #22-644 |

---

## Приложение A: Полный текст банковских реквизитов

### Marsel Luxury Car Rental

```
COMPANY BANK ACCOUNT
ADIB BANK : UAE
COMPANY NAME : MARSEL LUXURY CAR RENTAL
ACCOUNT NO : 19064835
IBAN : 110500000000019064835
CURRENCY : AED
```

### Sokol Car Rental L.L.C

```
Bank Account Details
Bank: ADIB Bank (UAE)
Company Name: SOKOL CAR RENTAL L.L.C
Account No.: 19346595
IBAN: AE070500000000019346595
Currency: AED
```

---

## Приложение B: Примеры описаний услуг (дословно)

### Трансферы

1. `MEETING AT THE AIRPORT AND TRANSFER TO THE HOTEL BY LEXUS ES350 CAR`
2. `PICK UP FROM THE HOTEL AND TRANSFER TO THE AIRPORT BY LEXUS ES350 CAR`
3. `TRANSFER ON MERCEDES S-CLASS WITH DRIVER`
4. `TRANSFER ON MERCEDES V-CLASS WITH DRIVER`

### Аренда с водителем

1. `CAR WITH DRIVER FOR 10 HOURS IN A LEXUS ES350`
2. `PRIVATE DUBAI MODERN TOUR FROM 09:00 TO 16:00. PICK-UP BY TOYOTA HIACE CAR FROM FZ 974 KZN-DXB (TERMINAL 2)`

### Шоу и билеты

1. `LA PERLE SHOW BY DRAGON SILVER CATEGORY FOR 2 ADULT`
2. `LA PERLE SHOW BY DRAGON SILVER CATEGORY FOR 2 CHILD`
3. `БИЛЕТЫ В АКВАРИУМ ДУБАЙ МОЛЛ С ПОДВОДНЫМ ЗООПАРКОМ И БУХТОЙ ПИНГВИНОВ`

### Яхты

1. `RENT AN INFINITY CATAMARAN 60 FEET FROM 17:00 TO 22:00`

### Аренда автомобилей

1. `EXTENSION OF THE RENTAL PERIOD FOR ROLLS-ROYCE CULLINAN VIP BLACK BADGE 2023`
2. `RETURNABLE DEPOSIT (DEPOSIT AMOUNT WILL BE CONSIDERED ONLY 4000 AED, VAT WILL BE PAID TO THE TAX AUTHORITY)`

---

## Приложение C: Контактная информация по инвойсам

| Инвойс | Телефон компании | Instagram |
|--------|------------------|-----------|
| #22-0241 | + 971 58 511 0777 | marsel_carrental |
| #22-299 | + 971 58 511 0777 | marsel_carrental |
| #22-344 | + 971 58 511 0777 | marsel_carrental |
| #22-598 | + 7 999 990-01-07 | gid_uae |
| #22-644 | + 971 58 511 0777 | marsel_carrental |
| #22-655 | + 971 58 511 0777 | marsel_carrental |
| #22-701 | + 971 58 511 0777 | marsel_carrental |
| Sokol #22-817 | + 971 58 511 0777 | - |

---

*Документ создан автоматически на основе анализа 9 PDF-инвойсов.*
