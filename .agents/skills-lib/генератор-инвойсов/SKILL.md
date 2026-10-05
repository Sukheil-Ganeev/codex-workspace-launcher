---
name: генератор-инвойсов
description: "Генерация инвойсов для Marsel Luxury Car Rental и Sokol Car Rental. Используй этот скилл когда нужно создать новый инвойс на основе данных клиента, списка услуг и условий оплаты. Поддерживает туры, трансферы, яхты, билеты, аренду авто и кейтеринг."
---
# ГЕНЕРАЦИЯ ИНВОЙСОВ MARSEL / SOKOL

## QUICK START

Для создания инвойса нужны минимум:

1. **Номер и дата** — `#26-001`, `Jan 22, 2026`
2. **Бренд** — `marsel` или `sokol`
3. **Клиент** — имя (CAPS), телефон
4. **Услуги** — минимум одна с описанием и ценой

```yaml
invoice:
  number: "#26-001"
  date: "Jan 22, 2026"
brand: "marsel"
client:
  name: "IVANOV IVAN"
  phone: "+7 999 123 4567"
services:
  - description: "PRIVATE TOUR IN DUBAI (for 2 persons) 28 JANUARY"
    price_excl_vat: 238.10
```

**VAT рассчитывается автоматически:** 5% от цены без НДС.

---

## СТРУКТУРА ВХОДНЫХ ДАННЫХ

### Полная схема

```yaml
invoice:
  number: "#YY-XXX"              # Обязательно. Формат: #ГОД-НОМЕР
  date: "Mon DD, YYYY"           # Обязательно. Формат: Jan 22, 2026

brand: "marsel"                  # marsel | sokol

client:
  name: "ИМЯ КЛИЕНТА"            # Обязательно. CAPS для физлиц
  phone: "+7 XXX XXX XXXX"       # Обязательно. Международный формат
  address: ""                    # Опционально. UAE / полный адрес / прочерк
  trn: ""                        # Опционально. Только для B2B в ОАЭ

services:                        # Минимум 1 услуга
  - type: "PRIVATE_TOUR"         # Тип (для валидации)
    description: "ОПИСАНИЕ"      # Обязательно. CAPS, на английском
    date: "28 JANUARY"           # Дата услуги
    time: "START AT 10:00 AM"    # Время (опционально)
    quantity: 1                  # Количество единиц
    price_excl_vat: 238.10       # Цена без VAT

payment:
  pos_terminal: false            # true если оплата картой
  pos_commission: 4              # Процент комиссии (3.5 или 4)

bank_details:
  use_default: true              # true = актуальные реквизиты

currency:
  primary: "USD"                 # USD | AED
  show_aed_conversion: true      # Показать итоги в AED
  usd_to_aed_rate: 3.65          # Курс конвертации
```

### Обязательные поля

| Поле | Описание |
|------|----------|
| `invoice.number` | Формат #YY-XXX или #YY-XXXX |
| `invoice.date` | Формат Mon DD, YYYY |
| `brand` | marsel или sokol |
| `client.name` | CAPS для физлиц |
| `client.phone` | С кодом страны |
| `services[].description` | CAPS, английский |
| `services[].price_excl_vat` | Число с 2 знаками |

### Опциональные поля

| Поле | Когда использовать |
|------|-------------------|
| `client.address` | Для корпоративных клиентов |
| `client.trn` | Для B2B клиентов в ОАЭ |
| `payment.pos_terminal` | При оплате картой |
| `currency.show_aed_conversion` | Для цен в USD |

---

## ТИПЫ УСЛУГ

### Туры и экскурсии

```
PRIVATE [ТИП] TOUR [МЕСТО] (for [N] persons) [ДАТА], START AT [ВРЕМЯ]
```

**Примеры:**
- `PRIVATE TOUR IN DUBAI (for 2 persons) 28 JANUARY, START AT 10:00 AM`
- `PRIVATE JEEP SAFARI TOUR (for 4 persons) 30 JANUARY`
- `PRIVATE MODERN TOUR IN ABU DHABI (for 3 persons) 1 FEBRUARY`

### Трансферы

```
TRANSFER ON [МАРКА АВТО] FROM [ТОЧКА A] TO [ТОЧКА B]
```

**Примеры:**
- `MEETING AT THE AIRPORT AND TRANSFER TO THE HOTEL BY LEXUS ES350`
- `TRANSFER ON MERCEDES V-CLASS FROM DXB AIRPORT TO ATLANTIS THE PALM`

**Марки авто:** LEXUS ES350, MERCEDES V-CLASS, MERCEDES S-CLASS, TOYOTA HIACE

### Яхты и катамараны

```
[YACHT/CATAMARAN] [НАЗВАНИЕ] [РАЗМЕР]FT [FROM HH:MM TO HH:MM]
```

**Примеры:**
- `YACHT MAJESTY 48FT 3 HOURS TRIP (for 6 persons)`
- `RENT INFINITY CATAMARAN 60 FEET FROM 17:00 TO 22:00`

### Билеты и шоу

```
[НАЗВАНИЕ] [КАТЕГОРИЯ] FOR [N] [ADULT/CHILD]
```

**Примеры:**
- `LA PERLE SHOW SILVER CATEGORY FOR 2 ADULT`
- `DUBAI AQUARIUM TICKETS FOR 4 PERSONS`

### Аренда авто (Sokol)

```
[МАРКА МОДЕЛЬ ГОД] RENTAL [ПЕРИОД]
```

**Примеры:**
- `TOYOTA LAND CRUISER 300 RENTAL (20.01.2026 - 19.02.2026)`
- Дополнительно: SECURITY DEPOSIT, SALIK TOLL CHARGES, TRAFFIC FINES

### Кейтеринг

```
[LEVEL UP] CATERING ON THE [ЯХТА]. DATE [ДАТА] TIME [ВРЕМЯ]
```

---

## УСЛОВНАЯ ЛОГИКА

### Выбор бренда

```
ЕСЛИ долгосрочная аренда авто без водителя:
  → brand: sokol
  → Licence: 1442819
  → Account: 19346595

ИНАЧЕ (туры, трансферы, яхты, билеты):
  → brand: marsel
  → Licence: 1024110
  → Account: 28642584
```

### POS Terminal

```
ЕСЛИ payment.pos_terminal = true:
  → Добавить строку: "PAYMENT VIA POS TERMINAL + X%"
  → X = pos_commission (3.5% VIP, 4% стандарт)
  → Комиссия = Total * X / 100
  → Grand Total = Total + Комиссия

ИНАЧЕ:
  → Не добавлять строку POS
```

### TRN (Tax Registration Number)

```
ЕСЛИ client.trn указан:
  → Добавить строку: TRN: XXXXXXXXXXXXXXX
  → Только для юрлиц ОАЭ (15 цифр)

ИНАЧЕ:
  → Не показывать TRN
```

### Конвертация валют

```
ЕСЛИ currency.primary = "USD" И show_aed_conversion = true:
  → Показать: Total in USD: XXX,XX USD
  → Показать: Total in AED (1 USD=3,65 AED): XXX,XX AED

ИНАЧЕ:
  → Показать только одну валюту
```

### Адрес клиента

```
ЕСЛИ юрлицо (есть TRN или L.L.C в имени):
  → client.address = полный юридический адрес

ЕСЛИ физлицо без адреса:
  → client.address = "UAE" или "-"
```

---

## РАСЧЁТЫ

### VAT (НДС)

```
Ставка: 5%
VAT = price_excl_vat * 0.05
amount_incl_vat = price_excl_vat + VAT
Округление: до сотых (2 знака)
```

**Пример:**
- price_excl_vat = 238,10
- VAT = 238,10 × 0,05 = 11,91
- amount_incl_vat = 238,10 + 11,91 = 250,01

### Итоги

```
Total (Excl. VAT) = сумма всех price_excl_vat
Total VAT = сумма всех VAT
Total (Incl. VAT) = Total (Excl. VAT) + Total VAT

ЕСЛИ POS Terminal:
  POS Commission = Total (Incl. VAT) × pos_commission / 100
  Grand Total = Total (Incl. VAT) + POS Commission
```

### Конвертация USD → AED

```
Курс: 1 USD = 3.65 AED
AED = USD × 3.65
```

---

## АЛГОРИТМ ГЕНЕРАЦИИ

### Шаг 1: Валидация входных данных

- [ ] Номер инвойса в формате #YY-XXX
- [ ] Дата в формате Mon DD, YYYY
- [ ] Бренд: marsel или sokol
- [ ] Имя клиента не пустое
- [ ] Телефон с кодом страны
- [ ] Минимум 1 услуга

### Шаг 2: Определение реквизитов

На основе `brand`:
- Логотип
- Licence Number
- Банковские реквизиты
- Адрес офиса

### Шаг 3: Генерация таблицы услуг

Для каждой услуги:
1. Порядковый номер (#)
2. DESCRIPTION из входных данных
3. Quantity (если указано)
4. Price (Excl. VAT)
5. Amount (Excl. VAT) = Price × Quantity
6. VAT 5% = Amount × 0.05
7. Amount (Incl. VAT) = Amount + VAT

### Шаг 4: Обработка POS Terminal

Если `payment.pos_terminal = true`:
- Добавить строку после услуг
- Рассчитать комиссию

### Шаг 5: Расчёт итогов

- Total (Excl. VAT)
- Total VAT
- Total (Incl. VAT)
- Grand Total (если POS)
- Конвертация в AED (если нужно)

### Шаг 6: Финальная проверка

- [ ] Все суммы сходятся
- [ ] Реквизиты соответствуют бренду
- [ ] Форматирование корректно

---

## ФОРМАТЫ ДАННЫХ

### Даты

| Контекст | Формат | Пример |
|----------|--------|--------|
| Дата инвойса | Mon DD, YYYY | Jan 22, 2026 |
| Дата услуги | DD MONTH | 28 JANUARY |
| Период (Sokol) | DD.MM.YYYY - DD.MM.YYYY | 20.01.2026 - 19.02.2026 |

### Время

| Формат | Пример |
|--------|--------|
| START AT HH:MM AM/PM | START AT 10:00 AM |
| FROM HH:MM TO HH:MM | FROM 14:00 TO 17:00 |

### Цены

| Валюта | Формат |
|--------|--------|
| USD | 238,10 $ или 238.10 USD |
| AED | 870 AED |

**Десятичный разделитель:** запятая (,)

### Телефоны

| Страна | Формат |
|--------|--------|
| Россия | +7 XXX XXX XXXX |
| ОАЭ | +971 XX XXX XXXX |
| Казахстан | +7 7XX XXX XXXX |

---

## СТРУКТУРА ТАБЛИЦЫ

### Колонки (обязательные)

| # | DESCRIPTION | Price (Excl. VAT) | Amount (Excl. VAT) | VAT 5% | Amount (Incl. VAT) |
|---|-------------|-------------------|--------------------|---------|--------------------|

### Колонки (опциональные)

- `hours` — для почасовой аренды
- `Quantity` — для билетов, аренды по дням

### Итоговые строки

```
Total (Excl. VAT):     $XXX,XX
Total VAT:             $XX,XX
Total (Incl. VAT):     $XXX,XX
─────────────────────────────────
PAYMENT VIA POS TERMINAL + 4%: $XX,XX  (если есть)
─────────────────────────────────
GRAND TOTAL:           $XXX,XX
─────────────────────────────────
Total in AED (1 USD=3,65 AED): XXXX AED  (если конвертация)
```

---

## БАНКОВСКИЕ РЕКВИЗИТЫ

### Marsel (АКТУАЛЬНЫЕ)

```
COMPANY BANK ACCOUNT
ADIB BANK : UAE
COMPANY NAME : MARSEL LUXURY CAR RENTAL
ACCOUNT NO : 28642584
IBAN : 110500000000028642584
CURRENCY : AED
```

### Sokol

```
Bank Account Details
Bank: ADIB Bank (UAE)
Company Name: SOKOL CAR RENTAL L.L.C
Account No.: 19346595
IBAN: AE070500000000019346595
Currency: AED
```

> Подробнее: см. `references/bank-details.md`

---

## РЕКВИЗИТЫ КОМПАНИЙ

### Marsel Luxury Car Rental

- Licence: 1024110
- Телефон: +971 58 511 0777
- Сайт: www.marsel-luxurycarrental.com
- Email: Info@marsel-luxurycarrental.com
- Instagram: marsel_carrental
- Офис: DAMAC SMART HEIGHTS, OFFICE 2109

### Sokol Car Rental L.L.C

- Licence: 1442819
- Телефон: +971 58 511 0777
- Сайт: www.sokol-carrental.com
- Email: Info@sokol-carrental.com
- Офис: DAMAC SMART HEIGHTS, OFFICE 2106

---

## ЧЕКЛИСТ ГЕНЕРАЦИИ

### Перед генерацией

- [ ] Определён бренд (marsel/sokol)
- [ ] Есть все обязательные данные
- [ ] Способ оплаты известен (POS?)

### После генерации

- [ ] Номер в формате #YY-XXX
- [ ] Дата в формате Mon DD, YYYY
- [ ] Имя клиента CAPS
- [ ] Все услуги с описанием
- [ ] VAT = 5% корректно
- [ ] Итоги сходятся
- [ ] Реквизиты соответствуют бренду

> Полный чеклист: см. `references/checklist.md`

---

## ОБРАБОТКА ОШИБОК

### Обязательные поля отсутствуют

| Поле | Ошибка | Действие |
|------|--------|----------|
| `invoice.number` | Нет номера инвойса | Запросить номер у пользователя |
| `invoice.date` | Нет даты | Использовать текущую дату |
| `client.name` | Нет имени | Запросить имя |
| `client.phone` | Нет телефона | Запросить телефон |
| `services` | Пустой список | Запросить минимум 1 услугу |

### Неверные форматы

| Проблема | Пример | Исправление |
|----------|--------|-------------|
| Дата без года | "Jan 22" | Добавить текущий год: "Jan 22, 2026" |
| Номер без # | "26-001" | Добавить #: "#26-001" |
| Имя не CAPS | "Ivanov Ivan" | Преобразовать: "IVANOV IVAN" |
| Телефон без кода | "999 123 4567" | Запросить код страны |

### Несовместимые данные

```
ЕСЛИ brand = "sokol" И услуга НЕ аренда авто:
  → Предупредить: "Sokol используется только для аренды авто"
  → Предложить: сменить brand на "marsel"

ЕСЛИ pos_terminal = true И pos_commission не указан:
  → Использовать по умолчанию: 4%

ЕСЛИ TRN указан И формат НЕ 15 цифр:
  → Ошибка: "TRN должен содержать 15 цифр"
```

### Округление VAT

**Правило:** математическое округление до сотых (2 знака).

```
11.905 → 11.91 (округление вверх)
11.904 → 11.90 (округление вниз)
```

> Подробнее об ошибках: см. `references/troubleshooting.md`

---

## ФОРМАТЫ НОМЕРОВ ИНВОЙСОВ

| Бренд | Формат | Пример |
|-------|--------|--------|
| Marsel | #YY-XXX или #YY-XXXX | #26-001, #26-0398 |
| Sokol | #YY-SKL-XXX | #26-SKL-001 |

---

## РЕДАКТИРОВАНИЕ СУЩЕСТВУЮЩИХ ИНВОЙСОВ

### Перед началом — обязательные вопросы

```
1. Цены с VAT или без VAT?
2. Есть ли комиссия (POS terminal, payment link)?
3. Какой процент комиссии?

→ Один вопрос в начале экономит 5 исправлений потом
```

### Workflow редактирования PPTX

```
1. Распаковать: unpack.py invoice.pptx /tmp/edit/
2. Снять inventory: inventory.py → понять структуру текста
3. Снять позиции ВСЕХ элементов с y > 6" (печать, банк, итоги, футер)
4. Найти таблицу в XML: ppt/slides/slide1.xml → <a:tbl>
5. Сделать изменения в XML
6. Сдвинуть нужные элементы (НЕ футер!)
7. Собрать: pack.py /tmp/edit/ invoice_new.pptx
8. Проверить: сравнить футер с оригиналом
```

### Зоны слайда инвойса

```
y = 0-2"     : Шапка (логотип, номер, дата)
y = 2-4"     : Данные клиента и компании
y = 4-6.5"   : Таблица услуг
y = 6.5-8"   : Печать, подпись, банк, итоги ← СДВИГАТЬ при добавлении строк
y = 10-12"   : Футер (соцсети, контакты) ← НИКОГДА НЕ ТРОГАТЬ!
```

### Единицы измерения в PPTX

```
- Позиции в EMU (English Metric Units)
- 914400 EMU = 1 дюйм
- Высота строки таблицы ≈ 480492 EMU (~0.53")
- Для сдвига вниз: new_y = old_y + 480492
```

### Структура таблицы в XML

```xml
<a:tbl>
  <a:tr h="480492">           <!-- строка, h = высота в EMU -->
    <a:tc>                     <!-- ячейка -->
      <a:txBody>
        <a:p>
          <a:r><a:t>ТЕКСТ</a:t></a:r>
        </a:p>
      </a:txBody>
    </a:tc>
    <!-- ещё 5 ячеек для остальных колонок -->
  </a:tr>
  <!-- rowId уникален для каждой строки -->
  <a:extLst><a:ext>
    <a16:rowId val="1621043224"/>
  </a:ext></a:extLst>
</a:tbl>
```

### Добавление строки в таблицу

```
1. Скопировать существующую <a:tr>...</a:tr>
2. Изменить rowId на +1 (например 1621043224 → 1621043225)
3. Заменить содержимое ячеек
4. Вставить после последней строки
5. Сдвинуть элементы ниже таблицы на высоту строки (480492 EMU)
```

### Что сдвигать при добавлении строки

```
СДВИГАТЬ (y между 6.5" и 10"):
  ✓ Печать и подпись (картинки ~6.6-6.8")
  ✓ Банковские реквизиты (текст ~6.9-7.0")
  ✓ Total USD / Total AED (текст ~6.9-7.1")

НЕ СДВИГАТЬ (y > 10"):
  ✗ Иконки соцсетей
  ✗ Текст футера (Instagram, WhatsApp, etc.)
  ✗ Любые элементы с y > 10"
```

### XML-текст разбит на runs

```
ПРОБЛЕМА: "983,51 USD" может быть разбит:
  <a:r><a:t>983,51</a:t></a:r>
  <a:r><a:t>,00</a:t></a:r>      ← остаток от старого текста!
  <a:r><a:t> USD</a:t></a:r>

РЕШЕНИЕ: При замене удалять ЦЕЛЫЕ <a:r>...</a:r> блоки
```

### Порядок расчётов с комиссией

```
1. Цена без VAT = указанная цена
2. VAT = цена × 0.05
3. Цена с VAT = цена + VAT
4. Subtotal = сумма всех цен с VAT
5. Комиссия = Subtotal × 0.035 (ОТ СУММЫ С VAT!)
6. Grand Total = Subtotal + комиссия
7. AED = Grand Total × 3.65
```

### Формат чисел в инвойсе

```
- Десятичный разделитель: ЗАПЯТАЯ (983,51 не 983.51)
- Тысячи: без разделителя
- Валюта после числа: 983,51 USD
- Выравнивание: пробелы перед числом (  983,51 USD)
```

### Комиссии — в таблицу, не в сноски

```
ПРАВИЛЬНО:
  Строка #5 в таблице: "PAYMENT VIA LINK FEE (+3.5%)"

НЕПРАВИЛЬНО:
  Текст под банковскими реквизитами
  Сноска внизу страницы
```

### Описания комиссий — понятные для банка

```
❌ "3,5%" — непонятно от чего
✅ "PAYMENT VIA LINK FEE (+3.5%)" — ясно

❌ "POS" — слишком коротко
✅ "PAYMENT VIA POS TERMINAL (+4%)" — понятно
```

### Чеклист после редактирования

```
□ Таблица: все строки на месте, цены верные
□ Итоги: формат числа корректный (без дублей 983,51,00)
□ Отступ: между таблицей и банком/итогами сохранён
□ Печать/подпись: сдвинуты вместе с итогами
□ Футер: позиции ИДЕНТИЧНЫ оригиналу (сравнить y-координаты)
□ Выравнивание: Total USD и Total AED на одном уровне
```

### Частые ошибки редактирования

| Ошибка | Как избежать |
|--------|--------------|
| Сдвинули футер | Проверять y > 10" — не трогать |
| Забыли печать/подпись | Сдвигать ВСЕ элементы 6.5" < y < 10" |
| Остались "хвосты" (,00 USD) | Удалять целые `<a:r>` блоки |
| Комиссия в сноске | Добавлять строку в таблицу |
| Комиссия от суммы без VAT | Считать от Subtotal (с VAT) |
| Не уточнили: цены с/без VAT | Спрашивать СРАЗУ в начале |

---

## ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

| Ресурс | Описание |
|--------|----------|
| `assets/templates/INVOICE_TEMPLATE.pptx` | Чистый шаблон для заполнения |
| `assets/examples/simple-tour.yaml` | Пример: простой тур |
| `assets/examples/corporate-multi.yaml` | Пример: корпоративный клиент |
| `assets/examples/pos-terminal.yaml` | Пример: с POS Terminal |
| `assets/examples/sokol-car-rental.yaml` | Пример: аренда авто Sokol |
| `references/service-types.md` | Справочник типов услуг |
| `references/bank-details.md` | Справочник банковских реквизитов |
| `references/troubleshooting.md` | Типичные ошибки |
| `references/checklist.md` | Полный чеклист проверки |
| `references/ПРАВИЛА_ГЕНЕРАЦИИ.md` | Детальные правила |

---

---

## НАКОПЛЕННЫЙ ОПЫТ

**Перед началом работы прочитай:** `experience/_index.md`

Содержит 10 критических уроков (мигрировано из troubleshooting.md):
- EXP-002: Расчёт VAT = Amount × 0.05
- EXP-005: НЕ смешивать реквизиты Marsel/Sokol
- EXP-004: POS Terminal: 4% / 3.5% / без для B2B
- EXP-007: USD→AED конвертация для СНГ клиентов
- EXP-009: Время для яхт/туров обязательно

При завершении — скажи "запиши это в опыт" если был полезный урок.

---

*Скилл создан на основе анализа 18 реальных инвойсов*
*Версия: 1.2 | Февраль 2026*
*Добавлено: система experience/, миграция troubleshooting*
