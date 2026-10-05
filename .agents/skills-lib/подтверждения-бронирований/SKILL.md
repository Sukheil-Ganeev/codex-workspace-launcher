---
name: подтверждения-бронирований
description: "Преобразование табличных данных подтверждений бронирования (из изображений или текста) в красиво оформленные сообщения WhatsApp/Telegram для клиентов. Используй при обработке подтверждений экскурсий/туров, особенно когда видишь таблицы с полями номер брони, дата, название тура, время пикапа, отель, имя гостя."
---
# Booking Confirmation Formatter

## Overview

Format booking confirmations from tabular data into professional WhatsApp/Telegram messages for clients. Extract details from booking tables (images or text) and create structured, friendly confirmations with all necessary information and contextual reminders.

---

## РАЗДЕЛ 0: ВЫБОР ПЛАТФОРМЫ

> **ОБЯЗАТЕЛЬНО:** Если в задаче НЕ указано, для какого мессенджера готовится текст:
> «Под какой мессенджер форматируем: WhatsApp или Telegram?»

---

## Workflow: 4 Simple Steps

### Step 1: Extract Data

Extract the following fields from the booking confirmation table:

**Required fields:**
- Booking # (номер бронирования)
- Date (дата экскурсии)
- Offer (название экскурсии)
- Pick Up Time (время подачи транспорта)
- Hotel (название отеля + телефон если есть)
- Guest Name (имя гостя)
- Tel (телефон гостя)
- Adults (количество взрослых)
- Children (количество детей)

**Optional fields:**
- Region (район отеля)
- Room (номер комнаты)
- Agency (агентство)
- Agent (агент)
- Agent Phone (телефон агента)

If the booking data is in an image, use vision capabilities to extract the information. If any critical field is missing or unclear, note it and request clarification.

### Step 2: Apply Template

Use the template below with extracted data. Add contextual reminders based on excursion type (see references/excursion_types.md for details).

### Step 3: Validate & Check

**CRITICAL: Triple-check the text for errors:**

Run through the quality checklist:
- All required fields included
- Correct separator (15 dashes WhatsApp / 18 dashes Telegram)
- Male voice: "подготовил", "забронировал"
- Proper formatting applied (WhatsApp vs Telegram)
- Contextual reminders match excursion type
- Name uses polite form if Russian (e.g., Мария, not Mariia)
- **NO grammatical errors**
- **NO spelling mistakes**
- **NO typos**
- **Proper punctuation**
- **Correct Russian language**

### Step 4: Output

**ВСЕГДА сохранять результат в MD файл:**

1. Сохранить файл в `D:/Downloads/` с именем: `Бронь_[НОМЕР]_[ИМЯ_ГОСТЯ].md`
2. Структура файла:
   - Заголовок: `# Подтверждение брони #[НОМЕР]`
   - Дата создания и мессенджер
   - Блок `## Сообщение (скопировать):` — готовый текст для копирования
   - Блок `## Данные брони (для себя)` — таблица со всеми полями включая агентство, агента, телефон агента
3. После сохранения вывести текст подтверждения также в чат
4. Сообщить: «Файл сохранён: `D:/Downloads/Бронь_[НОМЕР]_[ИМЯ].md` — текст готов для WhatsApp/Telegram!»

---

## ШАБЛОН WHATSAPP

**Синтаксис:** `*жирный*`, `_курсив_`
**Разделитель:** 15 тире `───────────────`
**Эмодзи:** Только ключевые (📅 🏨 ⏰ 💰 ⚠️)

```
*БРОНЬ ПОДТВЕРЖДЕНА*
───────────────
*[НАЗВАНИЕ_ЭКСКУРСИИ]*
───────────────
*ДЕТАЛИ БРОНИ*
📅 Дата: [ДАТА_ПРОПИСЬЮ]
🏨 Отель: [НАЗВАНИЕ_ОТЕЛЯ], [РАЙОН]
Комната: [НОМЕР]
Гости: [X] взр[, Y дет]
• [ИМЯ_1]
• [ИМЯ_2]
Телефон: [ТЕЛЕФОН]
───────────────
⏰ *ВРЕМЯ ВСТРЕЧИ*
Сбор: [ВРЕМЯ_ОТ]–[ВРЕМЯ_ДО]
_Гид свяжется с вами:_
_• Позвонит по номеру комнаты через ресепшен_
_• Или напишет на WhatsApp_
[Возврат: примерно [ВРЕМЯ]]
───────────────
💰 *СТОИМОСТЬ*
[X] взр × [Y]$ = [ИТОГО]$
[Z] дет × [W]$ = [ИТОГО]$
Итого: [СУММА]$
Оплата: [СПОСОБ]
───────────────
*ЧТО ВКЛЮЧЕНО*
• Трансфер от/до отеля
• [Локация 1]
• [Локация 2]
• Сопровождение на русском языке
───────────────
⚠️ *ВАЖНО*
• Будьте готовы к [ВРЕМЯ] в лобби
• [КОНТЕКСТНЫЕ_НАПОМИНАНИЯ]
• Удобная обувь и одежда
• Возьмите камеру для фото
[• Не забудьте паспорта для детей]
───────────────
_Если будут вопросы — всегда на связи!_
_Желаю отличной экскурсии!_
```

---

## ШАБЛОН TELEGRAM

**Синтаксис:** `**жирный**`, `__курсив__`
**Разделитель:** 18 тире `──────────────────`
**Эмодзи:** Только ключевые (📅 🏨 ⏰ 💰 ⚠️)

```
**БРОНЬ ПОДТВЕРЖДЕНА**
──────────────────
**[НАЗВАНИЕ_ЭКСКУРСИИ]**
──────────────────
**ДЕТАЛИ БРОНИ**
📅 Дата: [ДАТА_ПРОПИСЬЮ]
🏨 Отель: [НАЗВАНИЕ_ОТЕЛЯ], [РАЙОН]
Комната: [НОМЕР]
Гости: [X] взр[, Y дет]
• [ИМЯ_1]
• [ИМЯ_2]
Телефон: [ТЕЛЕФОН]
──────────────────
⏰ **ВРЕМЯ ВСТРЕЧИ**
Сбор: [ВРЕМЯ_ОТ]–[ВРЕМЯ_ДО]
__Гид свяжется с вами:__
__• Позвонит по номеру комнаты через ресепшен__
__• Или напишет в Telegram__
[Возврат: примерно [ВРЕМЯ]]
──────────────────
💰 **СТОИМОСТЬ**
[X] взр × [Y]$ = [ИТОГО]$
[Z] дет × [W]$ = [ИТОГО]$
Итого: [СУММА]$
Оплата: [СПОСОБ]

__Конвертация валют:__
__USD × 3.65 = AED__
__AED × (курс + 3) = RUB__
──────────────────
**ЧТО ВКЛЮЧЕНО**
• Трансфер от/до отеля
• [Локация 1]
• [Локация 2]
• Сопровождение на русском языке
──────────────────
⚠️ **ВАЖНО**
• Будьте готовы к [ВРЕМЯ] в лобби
• [КОНТЕКСТНЫЕ_НАПОМИНАНИЯ]
• Удобная обувь и одежда
• Возьмите камеру для фото
[• Не забудьте паспорта для детей]
──────────────────
__Если будут вопросы — всегда на связи!__
__Желаю отличной экскурсии!__
```

---

## Сравнение WhatsApp vs Telegram

| Элемент | WhatsApp | Telegram |
|---------|----------|----------|
| Жирный | `*текст*` | `**текст**` |
| Курсив | `_текст_` | `__текст__` |
| Разделитель | 15 тире `───────────────` | 18 тире `──────────────────` |
| Категории | ` ```текст``` ` | `**текст**` |

---

## Калькулятор валют

При указании стоимости можно добавить конвертацию:

**Формулы:**
- USD × 3.65 = AED
- AED × (курс + 3) = RUB

**Пример:**
```
Итого: 90$
В дирхамах: 90 × 3.65 = 329 AED
В рублях: 329 × (курс + 3) ≈ [расчет]
```

---

## Contextual Reminders

Add specific reminders based on excursion type. Read `references/excursion_types.md` for complete list.

**Common patterns:**

**Desert Safari:**
```
• Легкая закрытая одежда (защита от солнца и песка)
• Солнцезащитный крем и очки
• НЕ рекомендуется беременным и людям с проблемами спины
```

**Mosque Tour:**
```
• Закрытая одежда ОБЯЗАТЕЛЬНО (длинные рукава, длинные брюки/юбка)
• Платок для женщин
• Носки (обувь снимается при входе)
```

**Water Activities (Yacht, Aquaventure):**
```
• Купальник и сменная одежда
• Полотенце
• Солнцезащитный крем (водостойкий)
```

**Evening Tours:**
```
• Легкая теплая одежда (вечером прохладно)
• Камера для вечерних фотографий
```

---

## Critical Rules

**ALWAYS DO:**
- Start with "*БРОНЬ ПОДТВЕРЖДЕНА*" (no greeting like "Здравствуйте")
- Put excursion name as separate header after first separator
- Use correct separator (15/18 dashes)
- Use only key emoji: 📅 🏨 ⏰ 💰 ⚠️
- List ALL guest names individually with bullet points
- List ALL phone numbers separately
- Explain how guide will contact
- Include return time if known
- Add СТОИМОСТЬ section with calculation
- Add payment method
- Include "ЧТО ВКЛЮЧЕНО" section
- Use "⚠️ *ВАЖНО*" (not "ВАЖНЫЕ НАПОМИНАНИЯ")
- Check references/excursion_types.md for contextual reminders
- Use male voice: "подготовил", "забронировал"
- Convert Russian names to polite form (Mariia → Мария)
- Write dates in readable format: "5 ноября 2025"
- Add contextual reminders based on excursion type

**NEVER DO:**
- Don't start with "Здравствуйте" greeting
- Don't use 15+ different emoji — stick to key ones
- Don't use wrong separator count
- Don't write just "2 гостя" — list names individually
- Don't skip payment information
- Don't forget "ЧТО ВКЛЮЧЕНО" section
- Don't use formal tone — be friendly and professional
- Don't forget passport reminder for children
- Don't write in female voice
- Don't leave dates in numeric format (03.11.2025)
- Don't guess missing information — ask for clarification

---

## Checklist Before Output

**Content:**
- [ ] Starts with "БРОНЬ ПОДТВЕРЖДЕНА" (no greeting)
- [ ] Excursion name as separate header
- [ ] All required fields extracted and included
- [ ] Date in readable format (день месяц год)
- [ ] Only key emoji (📅 🏨 ⏰ 💰 ⚠️)
- [ ] ALL guest names listed individually with bullets
- [ ] ALL phone numbers listed separately
- [ ] Time window properly formatted (XX:XX–XX:XX with en-dash)
- [ ] Guide contact explanation included
- [ ] Return time included if known
- [ ] СТОИМОСТЬ section with calculation
- [ ] Payment method specified
- [ ] ЧТО ВКЛЮЧЕНО section with all locations/services
- [ ] ⚠️ ВАЖНО section
- [ ] Contextual reminders match excursion type
- [ ] Passport reminder for children if applicable

**Formatting:**
- [ ] Correct syntax (WhatsApp: single, Telegram: double)
- [ ] Correct separator count (15 WhatsApp / 18 Telegram)
- [ ] En-dash (–) for time ranges, not hyphen (-)
- [ ] Proper spacing between sections

**Language Quality:**
- [ ] Male voice used ("подготовил", "забронировал")
- [ ] Friendly but professional tone
- [ ] No greeting at start
- [ ] Russian names in proper form (Mariia → Мария)
- [ ] Perfect Russian grammar
- [ ] No typos anywhere

---

## Example: WhatsApp Confirmation

**Input data:**
```
Booking #: 685050
Date: 03.11.2025
Offer: MODERN DUBAI (RUS)
Pick Up Time: 13:30 - 14:00
Hotel: Centara Mirage Beach Resort Dubai
Region: Deira
Room: 275
Guest Name: Pershina Mariia
Tel: +79286295155
Adults: 1
Children: 1
```

**Output (WhatsApp):**

```
*БРОНЬ ПОДТВЕРЖДЕНА*
───────────────
*ОБЗОРНАЯ ЭКСКУРСИЯ ПО ДУБАЮ*
───────────────
*ДЕТАЛИ БРОНИ*
📅 Дата: 3 ноября 2025
🏨 Отель: Centara Mirage Beach Resort Dubai, Deira
Комната: 275
Гости: 1 взр, 1 реб
• Мария Першина
Телефон: +79286295155
───────────────
⏰ *ВРЕМЯ ВСТРЕЧИ*
Сбор: 13:30–14:00
_Гид свяжется с вами:_
_• Позвонит по номеру комнаты через ресепшен_
_• Или напишет на WhatsApp_
Возврат: примерно 21:30–22:30
───────────────
💰 *СТОИМОСТЬ*
1 взр × 50$ = 50$
1 реб × 40$ = 40$
Итого: 90$
Оплата: на месте при встрече (USD / AED)
───────────────
*ЧТО ВКЛЮЧЕНО*
• Трансфер от/до отеля
• Madinat Jumeirah
• Фотостоп у Burj Al Arab
• Palm Jumeirah → Atlantis
• Dubai Mall и фонтаны у Burj Khalifa
• Сопровождение на русском языке
───────────────
⚠️ *ВАЖНО*
• Будьте готовы к 13:30 в лобби
• Удобная обувь для ходьбы
• Возьмите камеру для фото
• Не забудьте паспорта (для детей обязательно)
───────────────
_Если будут вопросы — всегда на связи!_
_Желаю отличной экскурсии!_
```

---

## Example: Telegram Confirmation

**Output (Telegram):**

```
**БРОНЬ ПОДТВЕРЖДЕНА**
──────────────────
**ОБЗОРНАЯ ЭКСКУРСИЯ ПО ДУБАЮ**
──────────────────
**ДЕТАЛИ БРОНИ**
📅 Дата: 3 ноября 2025
🏨 Отель: Centara Mirage Beach Resort Dubai, Deira
Комната: 275
Гости: 1 взр, 1 реб
• Мария Першина
Телефон: +79286295155
──────────────────
⏰ **ВРЕМЯ ВСТРЕЧИ**
Сбор: 13:30–14:00
__Гид свяжется с вами:__
__• Позвонит по номеру комнаты через ресепшен__
__• Или напишет в Telegram__
Возврат: примерно 21:30–22:30
──────────────────
💰 **СТОИМОСТЬ**
1 взр × 50$ = 50$
1 реб × 40$ = 40$
Итого: 90$
Оплата: на месте при встрече (USD / AED)
──────────────────
**ЧТО ВКЛЮЧЕНО**
• Трансфер от/до отеля
• Madinat Jumeirah
• Фотостоп у Burj Al Arab
• Palm Jumeirah → Atlantis
• Dubai Mall и фонтаны у Burj Khalifa
• Сопровождение на русском языке
──────────────────
⚠️ **ВАЖНО**
• Будьте готовы к 13:30 в лобби
• Удобная обувь для ходьбы
• Возьмите камеру для фото
• Не забудьте паспорта (для детей обязательно)
──────────────────
__Если будут вопросы — всегда на связи!__
__Желаю отличной экскурсии!__
```

---

## Additional Scenarios

**Missing critical information:**
```
Извините, не хватает важной информации:
- [список недостающих полей]

Пожалуйста, уточните эти данные.
```

**Multiple guests (3+ people):**
```
Гости: 3 взр
• Динара Науатова
• Камила Мухамеджанова
• Алдияр Наушаев
```

**Multiple phone numbers:**
```
Телефоны:
+7 775 897 31 05
+7 775 117 96 07
```

**Living at different hotel than pickup:**
```
🏨 Отель встречи: Ramee Dream Hotel Downtown, Business Bay
_(проживают в J ONE apartments, комната 1310)_
```

**VIP/Private tours:**
```
_Это индивидуальная экскурсия — только для вашей группы!_
```

**If price not yet paid:**
```
Оплата: на месте при встрече (USD / AED / наличные)
```

**If price already paid:**
```
Оплата: оплачено
```

---

## Resources

### references/excursion_types.md
Comprehensive guide to different excursion types and their specific requirements.

---

## Краткая памятка

| Вопрос | WhatsApp | Telegram |
|--------|----------|----------|
| Жирный | `*текст*` | `**текст**` |
| Курсив | `_текст_` | `__текст__` |
| Разделитель | 15 тире | 18 тире |
| Ключевые эмодзи | 📅 🏨 ⏰ 💰 ⚠️ | 📅 🏨 ⏰ 💰 ⚠️ |
| Категории | ` ```текст``` ` | `**текст**` |

---

*Booking Confirmation Formatter v2.2*
*Обновлено: Январь 2026 — синхронизировано с эталоном форматирования*
