# Справочник типов услуг для инвойсов Marsel/Sokol

**Версия:** 1.0
**Дата:** 22 января 2026
**Назначение:** Детальное описание всех категорий услуг для генерации инвойсов

---

## 1. PRIVATE TOUR (Приватные туры)

### Описание
Индивидуальные экскурсии с личным гидом для группы клиентов. Включают транспорт, сопровождение и посещение достопримечательностей.

### Паттерн описания
```
PRIVATE [ТИП] TOUR [МЕСТО] (for [N] persons) [ДАТА], START AT [ВРЕМЯ]
```

### Варианты паттернов
```
PRIVATE TOUR IN [ГОРОД] (for [N] persons) [DD MONTH], START AT [HH:MM AM/PM]
PRIVATE [ТИП] TOUR (for [N] persons) [DD MONTH]
PRIVATE [ГОРОД] [ТИП] TOUR FROM [HH:MM] TO [HH:MM]
PRIVATE [ГОРОД] [ТИП] TOUR FROM [HH:MM] TO [HH:MM]. PICK-UP BY [АВТО] FROM [МЕСТО]
```

### Примеры из реальных инвойсов
- `PRIVATE TOUR IN DUBAI (for 2 persons) 28 JANUARY, START AT 10:00 AM`
- `PRIVATE JEEP SAFARI TOUR (for 2 persons) 30 JANUARY`
- `PRIVATE TOUR IN ABU DHABI (for 2 persons) 1 FEBRUARY, START AT 9:00 AM`
- `PRIVATE DUBAI MODERN TOUR FROM 09:00 TO 16:00`
- `PRIVATE DUBAI MODERN TOUR FROM 09:00 TO 16:00. PICK-UP BY TOYOTA HIACE CAR FROM FZ 974 KZN-DXB (TERMINAL 2)`

### Поля

| Поле | Обязательно | Формат | Пример |
|------|-------------|--------|--------|
| Тип тура | Да | CAPS, без артиклей | TOUR, JEEP SAFARI TOUR, MODERN TOUR |
| Место | Да | IN + ГОРОД или просто ГОРОД | IN DUBAI, IN ABU DHABI, DUBAI |
| Кол-во персон | Рекомендуется | (for N persons) | (for 2 persons), (for 4 persons) |
| Дата | Да | DD MONTH или D MONTH | 28 JANUARY, 1 FEBRUARY |
| Время начала | Рекомендуется | START AT HH:MM AM/PM | START AT 10:00 AM |
| Время периода | Опционально | FROM HH:MM TO HH:MM | FROM 09:00 TO 16:00 |
| Трансфер | Опционально | PICK-UP BY [АВТО] FROM [МЕСТО] | PICK-UP BY TOYOTA HIACE CAR FROM... |

### Особенности расчёта
- **Цена:** фиксированная за весь тур (не за человека)
- **VAT:** 5% от цены без НДС
- **Количество:** обычно 1 (один тур)
- **Колонка hours:** НЕ используется
- **Колонка Quantity:** НЕ используется (кол-во персон в описании)

### Типы туров
| Тип | Описание |
|-----|----------|
| TOUR | Обзорная экскурсия |
| MODERN TOUR | Современный Дубай |
| JEEP SAFARI TOUR | Джип-сафари в пустыне |
| OLD TOWN TOUR | Исторический район |
| CITY TOUR | Обзорный городской тур |

---

## 2. GROUP TOUR (Групповые экскурсии)

### Описание
Экскурсии в составе сборной группы с общим гидом. Фиксированное расписание, точки сбора.

### Паттерн описания
```
GROUP TOUR [МЕСТО] FOR [N] [ADULT/CHILD] [ДАТА]
[НАЗВАНИЕ ЭКСКУРСИИ] FOR [N] PERSONS [ДАТА]
```

### Варианты паттернов
```
GROUP TOUR TO [МЕСТО] FOR [N] ADULT, [N] CHILD - [DD MONTH]
[НАЗВАНИЕ] EXCURSION FOR [N] PERSONS [DD.MM.YY]
DESERT SAFARI GROUP TOUR FOR [N] PERSONS [DD MONTH]
```

### Примеры из реальных инвойсов
- `GROUP TOUR TO ABU DHABI FOR 2 ADULT, 1 CHILD - 15 JANUARY`
- `DESERT SAFARI GROUP TOUR FOR 4 PERSONS 20 JANUARY`
- `DHOW CRUISE DINNER FOR 2 PERSONS 18.01.26`

### Поля

| Поле | Обязательно | Формат | Пример |
|------|-------------|--------|--------|
| Тип | Да | GROUP TOUR или название | GROUP TOUR, DESERT SAFARI |
| Место | Да | TO + МЕСТО | TO ABU DHABI, TO FERRARI WORLD |
| Взрослые | Да | N ADULT | 2 ADULT |
| Дети | Опционально | N CHILD | 1 CHILD |
| Дата | Да | DD MONTH или DD.MM.YY | 15 JANUARY, 18.01.26 |

### Особенности расчёта
- **Цена:** может быть за человека (тогда указывается Quantity)
- **VAT:** 5% от суммы
- **Количество:** количество участников
- **Колонка Quantity:** используется, если цена за человека

### Отличия от PRIVATE TOUR
| Параметр | PRIVATE TOUR | GROUP TOUR |
|----------|--------------|------------|
| Цена | За весь тур | За человека или за группу |
| Расписание | Гибкое | Фиксированное |
| Quantity | Не используется | Может использоваться |
| Персонализация | Высокая | Низкая |

---

## 3. TRANSFER (Трансферы)

### Описание
Перевозка клиентов между точками: аэропорт, отель, порт, достопримечательности. Включает встречу, помощь с багажом.

### Паттерн описания
```
[ТИП ТРАНСФЕРА] BY [МАРКА АВТО]
```

### Варианты паттернов
```
MEETING AT THE AIRPORT AND TRANSFER TO THE HOTEL BY [АВТО]
PICK UP FROM THE HOTEL AND TRANSFER TO THE AIRPORT BY [АВТО]
TRANSFER FROM [ТОЧКА A] TO [ТОЧКА B] BY [АВТО]
TRANSFER RT FROM [ОТЕЛЬ] (ADDRESS: [АДРЕС]) TO [МЕСТО] DATE [DD.MM.YY] TIME [HH:MM] BY [АВТО] AND BACK TRANSFER AT [HH:MM] - [N] CARS
TRANSFER ON [АВТО] WITH DRIVER START: [DD MONTH], DEPARTURE AT [HH:MM], ARRIVAL AT [HH:MM]
```

### Примеры из реальных инвойсов
- `MEETING AT THE AIRPORT AND TRANSFER TO THE HOTEL BY LEXUS ES350 CAR`
- `PICK UP FROM THE HOTEL AND TRANSFER TO THE AIRPORT BY LEXUS ES350 CAR`
- `TRANSFER RT FROM RIXOS THE PALM DUBAI HOTEL & SUITES (ADDRESS: THE PALM JUMEIRAH...) TO THE PORT (ADDRESS DUBAI MARINA HARBOUR) DATE 16.02.23 TIME 15:00 BY MERCEDES V CLASS AND BACK TRANSFER AT 20:30 - 2 CARS.`
- `TRANSFER ON MERCEDES S-CLASS WITH DRIVER START: 14 OCTOBER, DEPARTURE AT 5:30 AM, ARRIVAL AT 5:30 PM`

### Поля

| Поле | Обязательно | Формат | Пример |
|------|-------------|--------|--------|
| Тип трансфера | Да | MEETING/PICK UP/TRANSFER | MEETING AT THE AIRPORT |
| Точка отправления | Да | FROM [МЕСТО] или AT THE [МЕСТО] | FROM THE HOTEL, AT THE AIRPORT |
| Точка назначения | Да | TO THE [МЕСТО] | TO THE HOTEL, TO THE AIRPORT |
| Марка авто | Да | BY [МАРКА МОДЕЛЬ] | BY LEXUS ES350, BY MERCEDES V CLASS |
| Дата | Рекомендуется | DATE DD.MM.YY или DD MONTH | DATE 16.02.23, 14 OCTOBER |
| Время | Рекомендуется | TIME HH:MM или DEPARTURE AT HH:MM | TIME 15:00, DEPARTURE AT 5:30 AM |
| Кол-во машин | Опционально | - N CARS | - 2 CARS |
| Обратный трансфер | Опционально | AND BACK TRANSFER AT HH:MM | AND BACK TRANSFER AT 20:30 |

### Особенности расчёта
- **Цена:** за трансфер (одно направление) или за RT (туда-обратно)
- **VAT:** 5%
- **Количество:** количество машин или трансферов
- **Колонка Quantity:** используется при нескольких машинах

### Типы трансферов
| Код | Описание | Пример |
|-----|----------|--------|
| AIRPORT-HOTEL | Из аэропорта в отель | MEETING AT THE AIRPORT AND TRANSFER TO THE HOTEL |
| HOTEL-AIRPORT | Из отеля в аэропорт | PICK UP FROM THE HOTEL AND TRANSFER TO THE AIRPORT |
| POINT-TO-POINT | Между точками | TRANSFER FROM [A] TO [B] |
| RT (Round Trip) | Туда и обратно | TRANSFER RT FROM... AND BACK TRANSFER |
| WITH DRIVER | С водителем на день | TRANSFER ON [АВТО] WITH DRIVER |

### Марки автомобилей
| Марка | Класс | Вместимость |
|-------|-------|-------------|
| LEXUS ES350 | Бизнес | 3 пассажира |
| MERCEDES V CLASS | Минивэн | 6-7 пассажиров |
| MERCEDES S-CLASS | Премиум | 3 пассажира |
| TOYOTA HIACE | Микроавтобус | 10-14 пассажиров |

---

## 4. YACHT / CATAMARAN (Морские прогулки)

### Описание
Аренда яхт и катамаранов для морских прогулок в Dubai Marina, Palm Jumeirah и других локациях.

### Паттерн описания
```
[YACHT/RENT] [НАЗВАНИЕ] [РАЗМЕР] [FT/FEET] [FROM HH:MM TO HH:MM]
```

### Варианты паттернов
```
YACHT [НАЗВАНИЕ] [XX] FEET
YACHT RENTING IN DUBAI: [НАЗВАНИЕ] [XX] FT [NEW] ([N] HOURS). RENTAL TIME FROM [HH:MM] TO [HH:MM].
RENT AN [НАЗВАНИЕ] CATAMARAN [XX] FEET FROM [HH:MM] TO [HH:MM]
[НАЗВАНИЕ] YACHT [XX] FT, [DD.MM.YY] [HH:MM]-[HH:MM]
```

### Примеры из реальных инвойсов
- `YACHT HEIGAN 90 FEET`
- `YACHT RENTING IN DUBAI: MAJESTY 48 FT NEW (5 HOURS). RENTAL TIME FROM 15:30 TO 20:30.`
- `RENT AN INFINITY CATAMARAN 60 FEET FROM 17:00 TO 22:00`

### Поля

| Поле | Обязательно | Формат | Пример |
|------|-------------|--------|--------|
| Тип судна | Да | YACHT / CATAMARAN | YACHT, CATAMARAN |
| Название | Да | CAPS | HEIGAN, MAJESTY, INFINITY |
| Размер | Да | XX FEET или XX FT | 90 FEET, 48 FT |
| Модификатор | Опционально | NEW, VIP | NEW |
| Продолжительность | Рекомендуется | (N HOURS) | (5 HOURS) |
| Время аренды | Рекомендуется | FROM HH:MM TO HH:MM | FROM 15:30 TO 20:30 |
| Дата | Опционально | DD.MM.YY | 16.02.23 |

### Особенности расчёта
- **Цена:** за аренду целиком или за час
- **VAT:** 5%
- **Количество:** обычно 1
- **Колонка hours:** может использоваться для почасовой аренды

### Популярные яхты
| Название | Размер | Тип | Вместимость |
|----------|--------|-----|-------------|
| HEIGAN | 90 FT | Yacht | до 30 чел |
| MAJESTY | 48 FT | Yacht | до 15 чел |
| INFINITY | 60 FT | Catamaran | до 25 чел |

### Дополнительные услуги (добавляются отдельными строками)
- CATERING ON THE YACHT
- PROFESSIONAL DJ
- JET SKI
- FISHING EQUIPMENT

---

## 5. SHOW / TICKETS (Билеты и шоу)

### Описание
Билеты на шоу, аттракционы, музеи, развлекательные парки. Включает категорию мест и возрастную группу.

### Паттерн описания
```
[НАЗВАНИЕ ШОУ] [КАТЕГОРИЯ] FOR [N] [ADULT/CHILD]
```

### Варианты паттернов
```
[НАЗВАНИЕ] BY [ОРГАНИЗАТОР] [КАТЕГОРИЯ] CATEGORY FOR [N] ADULT
[НАЗВАНИЕ] BY [ОРГАНИЗАТОР] [КАТЕГОРИЯ] CATEGORY FOR [N] CHILD
БИЛЕТЫ В [МЕСТО] С [ОПЦИИ]
[ATTRACTION] TICKETS FOR [N] PERSONS - [ДАТА]
```

### Примеры из реальных инвойсов
- `LA PERLE SHOW BY DRAGON SILVER CATEGORY FOR 2 ADULT`
- `LA PERLE SHOW BY DRAGON SILVER CATEGORY FOR 2 CHILD`
- `БИЛЕТЫ В АКВАРИУМ ДУБАЙ МОЛЛ С ПОДВОДНЫМ ЗООПАРКОМ И БУХТОЙ ПИНГВИНОВ`

### Поля

| Поле | Обязательно | Формат | Пример |
|------|-------------|--------|--------|
| Название | Да | CAPS | LA PERLE SHOW, АКВАРИУМ ДУБАЙ МОЛЛ |
| Организатор | Опционально | BY [NAME] | BY DRAGON |
| Категория | Да для шоу | [CAT] CATEGORY | SILVER CATEGORY, GOLD CATEGORY, VIP |
| Возраст | Да | ADULT / CHILD | FOR 2 ADULT |
| Кол-во | Да | FOR N | FOR 2 |
| Дата | Опционально | DD MONTH или DD.MM.YY | 20 JANUARY |

### Особенности расчёта
- **Цена:** за билет (взрослый/детский)
- **VAT:** 5%
- **Количество:** количество билетов
- **Колонка Quantity:** ИСПОЛЬЗУЕТСЯ (разные строки для взрослых и детей)

### Категории билетов
| Категория | Описание |
|-----------|----------|
| SILVER | Стандарт |
| GOLD | Улучшенные места |
| VIP | Премиум зона |
| PLATINUM | Максимальный комфорт |

### Популярные шоу и аттракционы
| Название | Тип |
|----------|-----|
| LA PERLE SHOW | Шоу |
| AQUAVENTURE | Аквапарк |
| DUBAI AQUARIUM | Аквариум |
| FERRARI WORLD | Парк развлечений |
| GLOBAL VILLAGE | Развлекательный парк |
| DUBAI FRAME | Достопримечательность |

---

## 6. CAR RENTAL (Аренда авто)

### Описание
Аренда автомобилей премиум и люкс класса. Два варианта: с водителем (краткосрочная) и без водителя (долгосрочная).

### Паттерн описания

**С водителем (Marsel):**
```
CAR WITH DRIVER FOR [N] HOURS IN A [МАРКА МОДЕЛЬ]
```

**Без водителя (Sokol):**
```
Rental charges ([DD MMM YYYY] - [DD MMM YYYY]), [N] days x [XXX] AED/day (Excl. VAT)
```

### Варианты паттернов
```
CAR WITH DRIVER FOR [N] HOURS IN A [МАРКА МОДЕЛЬ]
EXTENSION OF THE RENTAL PERIOD FOR [МАРКА МОДЕЛЬ ГОД]
Rental charges ([ДАТА] - [ДАТА]), [N] days x [XXX] AED/day (Excl. VAT)
Outstanding vehicle value
Non-refundable insurance premium
GPS equipment cost
PPF protective film cost
```

### Примеры из реальных инвойсов
- `CAR WITH DRIVER FOR 10 HOURS IN A LEXUS ES350`
- `EXTENSION OF THE RENTAL PERIOD FOR ROLLS-ROYCE CULLINAN VIP BLACK BADGE 2023`
- `Rental charges (03 May 2025 - 30 Jul 2025), 88 days x 750 AED/day (Excl. VAT)`

### Поля (С водителем)

| Поле | Обязательно | Формат | Пример |
|------|-------------|--------|--------|
| Тип | Да | CAR WITH DRIVER | CAR WITH DRIVER |
| Часы | Да | FOR N HOURS | FOR 10 HOURS |
| Авто | Да | IN A [МАРКА МОДЕЛЬ] | IN A LEXUS ES350 |

### Поля (Без водителя - Sokol)

| Поле | Обязательно | Формат | Пример |
|------|-------------|--------|--------|
| Rental charges | Да | Период + дней x цена/день | (03 May 2025 - 30 Jul 2025), 88 days x 750 AED/day |
| Outstanding vehicle value | Условно | Сумма | 268,073 AED |
| Insurance premium | Условно | Сумма | 15,000 AED |
| GPS equipment | Опционально | Сумма | 500 AED |
| PPF film | Опционально | Сумма | 3,000 AED |
| Traffic fines | Условно | Ссылка на Annex | see Annex A for breakdown |
| Salik charges | Условно | Кол-во проездов | (N gates) |

### Особенности расчёта

**Marsel (с водителем):**
- **Цена:** за весь период аренды
- **VAT:** 5%
- **Колонка hours:** ИСПОЛЬЗУЕТСЯ

**Sokol (долгосрочная аренда):**
- **Цена:** days x daily_rate
- **VAT:** 5% от каждой позиции
- **Итоги:** TOTAL AMOUNT, PAID AMOUNT, REMAINING AMOUNT
- **Period:** обязательно указывать

### Структура инвойса Sokol (аренда с инцидентами)

```
1. Rental charges (период), N days x XXX AED/day
2. Outstanding vehicle value (если Total Loss)
3. Insurance policy excess amount
4. Non-refundable insurance premium
5. Traffic fines (see Annex A)
6. Salik toll charges (N gates)
---
TOTAL AMOUNT: XXX AED
PAID AMOUNT: XXX AED
REMAINING AMOUNT: XXX AED
```

---

## 7. CATERING (Кейтеринг и еда)

### Описание
Организация питания на яхтах, мероприятиях, экскурсиях. Может включать детальное меню.

### Паттерн описания
```
[CATERING/LEVEL UP CATERING] ON THE [ЯХТА]. DATE [DD.MM.YY] TIME - FROM [HH:MM] till [HH:MM], NUMBER OF PEOPLE - [N] PERSON.
```

### Варианты паттернов
```
CATERING ON THE YACHT [НАЗВАНИЕ] [XX] FT [NEW]. DATE [DD.MM.YY] TIME - FROM [HH:MM] till [HH:MM], NUMBER OF PEOPLE - [N] PERSON.
LEVEL UP CATERING
CATERING FOR [N] PERSONS
BBQ ON BOARD FOR [N] PERSONS
FOOD AND BEVERAGES
```

### Примеры из реальных инвойсов
- `LEVEL UP CATERING`
- `CATERING ON THE YACHT MAJESTY 48 FT NEW. DATE 16.02.23 TIME - FROM 15:30 till 20:30, NUMBER OF PEOPLE - 7 PERSON.`

### Поля

| Поле | Обязательно | Формат | Пример |
|------|-------------|--------|--------|
| Тип | Да | CATERING / LEVEL UP CATERING / BBQ | CATERING |
| Место | Рекомендуется | ON THE [ЯХТА/МЕСТО] | ON THE YACHT MAJESTY 48 FT |
| Дата | Рекомендуется | DATE DD.MM.YY | DATE 16.02.23 |
| Время | Рекомендуется | FROM HH:MM till HH:MM | FROM 15:30 till 20:30 |
| Кол-во персон | Да | NUMBER OF PEOPLE - N PERSON | NUMBER OF PEOPLE - 7 PERSON |

### Особенности расчёта
- **Цена:** фиксированная за пакет или по меню
- **VAT:** 5%
- **Количество:** обычно 1 (пакет) или по персонам
- **Детализация:** может включать MENU с отдельными позициями

### Уровни кейтеринга
| Уровень | Описание | Включает |
|---------|----------|----------|
| BASIC CATERING | Базовый | Закуски, напитки |
| LEVEL UP CATERING | Улучшенный | Горячее, десерты, премиум напитки |
| BBQ ON BOARD | Барбекю | Мясо, гриль, гарниры |
| PREMIUM CATERING | Премиум | Морепродукты, стейки, шампанское |

---

## 8. VIP SERVICE (VIP услуги)

### Описание
Премиальные услуги: ускоренное прохождение в аэропорту, личный консьерж, VIP-зоны.

### Паттерн описания
```
VIP [ТИП УСЛУГИ] AT [МЕСТО] FOR [N] PERSONS
```

### Варианты паттернов
```
VIP AIRPORT MEET AND ASSIST AT [АЭРОПОРТ] FOR [N] PERSONS
VIP LOUNGE ACCESS AT [МЕСТО] FOR [N] PERSONS
FAST TRACK SERVICE AT [АЭРОПОРТ]
PERSONAL CONCIERGE SERVICE FOR [ПЕРИОД]
VIP TABLE RESERVATION AT [РЕСТОРАН/КЛУБ]
```

### Примеры из реальных инвойсов
- `VIP AIRPORT MEET AND ASSIST AT DXB TERMINAL 3 FOR 4 PERSONS`
- `FAST TRACK IMMIGRATION SERVICE FOR 2 PERSONS`
- `VIP LOUNGE ACCESS FOR 3 HOURS`

### Поля

| Поле | Обязательно | Формат | Пример |
|------|-------------|--------|--------|
| Тип услуги | Да | CAPS | MEET AND ASSIST, LOUNGE ACCESS, FAST TRACK |
| Место | Да | AT [МЕСТО] | AT DXB TERMINAL 3 |
| Кол-во персон | Да | FOR N PERSONS | FOR 4 PERSONS |
| Продолжительность | Опционально | FOR N HOURS | FOR 3 HOURS |
| Дата | Рекомендуется | DD MONTH или DD.MM.YY | 15 JANUARY |

### Особенности расчёта
- **Цена:** за услугу или за человека
- **VAT:** 5%
- **Количество:** количество персон
- **Колонка Quantity:** используется при цене за человека

### Типы VIP услуг
| Услуга | Описание |
|--------|----------|
| MEET AND ASSIST | Встреча и сопровождение в аэропорту |
| FAST TRACK | Ускоренное прохождение контроля |
| LOUNGE ACCESS | Доступ в VIP-зал |
| CONCIERGE | Личный консьерж |
| TABLE RESERVATION | Бронирование VIP-столов |

---

## 9. OTHER (Прочие услуги)

### Описание
Дополнительные услуги, не входящие в основные категории: развлечения, спорт, особые мероприятия.

### Паттерн описания
```
[НАЗВАНИЕ УСЛУГИ] [ДЕТАЛИ]
```

### Примеры из реальных инвойсов
- `PROFESSIONAL DJ`
- `JET SKI ( Water ATV 1800CC )`
- `DUBAI PRIVATE HORSE RIDING ON THE BEACH FOR 2 HOURS`
- `RETURNABLE DEPOSIT (DEPOSIT AMOUNT WILL BE CONSIDERED ONLY 4000 AED, VAT WILL BE PAID TO THE TAX AUTHORITY)`

### Подкатегории

#### 9.1 Развлечения на воде

| Услуга | Паттерн | Пример |
|--------|---------|--------|
| Jet Ski | JET SKI ([МОДЕЛЬ]) | JET SKI ( Water ATV 1800CC ) |
| Flyboard | FLYBOARD SESSION [N] MIN | FLYBOARD SESSION 30 MIN |
| Parasailing | PARASAILING FOR [N] PERSONS | PARASAILING FOR 2 PERSONS |

#### 9.2 Спорт и активности

| Услуга | Паттерн | Пример |
|--------|---------|--------|
| Конные прогулки | [ГОРОД] PRIVATE HORSE RIDING ON THE [МЕСТО] FOR [N] HOURS | DUBAI PRIVATE HORSE RIDING ON THE BEACH FOR 2 HOURS |
| Дайвинг | DIVING EXPERIENCE FOR [N] PERSONS | DIVING EXPERIENCE FOR 2 PERSONS |
| Golf | GOLF SESSION AT [МЕСТО] | GOLF SESSION AT EMIRATES GOLF CLUB |

#### 9.3 Развлечения

| Услуга | Паттерн | Пример |
|--------|---------|--------|
| DJ | PROFESSIONAL DJ | PROFESSIONAL DJ |
| Фотограф | PROFESSIONAL PHOTOGRAPHER [N] HOURS | PROFESSIONAL PHOTOGRAPHER 3 HOURS |
| Музыканты | LIVE MUSIC / LIVE BAND | LIVE BAND FOR 2 HOURS |

#### 9.4 Специальные позиции

| Услуга | Паттерн | Описание |
|--------|---------|----------|
| Депозит | RETURNABLE DEPOSIT ([УСЛОВИЯ]) | Возвратный залог |
| POS комиссия | PAYMENT VIA POS TERMINAL + [X]% | Комиссия за оплату картой |

### Поля

| Поле | Обязательно | Формат | Пример |
|------|-------------|--------|--------|
| Название | Да | CAPS | PROFESSIONAL DJ |
| Детали | Опционально | В скобках или после | ( Water ATV 1800CC ) |
| Продолжительность | Опционально | FOR N HOURS / N MIN | FOR 2 HOURS |
| Кол-во | Опционально | FOR N PERSONS | FOR 2 PERSONS |

### Особенности расчёта
- **Цена:** индивидуально для каждой услуги
- **VAT:** 5% (кроме депозитов - VAT = 0)
- **Депозит:** VAT не применяется, указывается отдельной строкой

---

## 10. СВОДНАЯ ТАБЛИЦА КАТЕГОРИЙ

| Категория | Колонка hours | Колонка Quantity | VAT | Типичная цена |
|-----------|---------------|------------------|-----|---------------|
| PRIVATE TOUR | Нет | Нет | 5% | За тур |
| GROUP TOUR | Нет | Да | 5% | За человека |
| TRANSFER | Нет | Да (при нескольких авто) | 5% | За трансфер |
| YACHT/CATAMARAN | Да (опц.) | Нет | 5% | За аренду |
| SHOW/TICKETS | Нет | Да | 5% | За билет |
| CAR RENTAL (driver) | Да | Нет | 5% | За период |
| CAR RENTAL (Sokol) | Нет | Нет | 5% | Days x rate |
| CATERING | Нет | Да (опц.) | 5% | За пакет |
| VIP SERVICE | Нет | Да | 5% | За услугу |
| OTHER | Да (опц.) | Да (опц.) | 5%* | Индивидуально |

*Депозиты без VAT

---

## 11. ПРАВИЛА ФОРМАТИРОВАНИЯ ОПИСАНИЙ

### Общие правила
1. **Регистр:** ВСЕ CAPS для описания услуг
2. **Язык:** Английский (предпочтительно) или Русский
3. **Даты в описании:** DD MONTH (28 JANUARY) или DD.MM.YY (16.02.23)
4. **Время:** 24-часовой (15:30) или 12-часовой (3:30 PM) формат
5. **Персоны:** (for N persons) или FOR N ADULT/CHILD

### Порядок элементов
```
1. Тип услуги (PRIVATE TOUR, TRANSFER, YACHT...)
2. Детали услуги (место, название, модель)
3. Количество персон
4. Дата
5. Время
6. Дополнительные условия
```

### Пунктуация
- Запятая после даты перед временем: `28 JANUARY, START AT 10:00 AM`
- Точка в конце сложных описаний
- Скобки для уточнений: `(for 2 persons)`, `(5 HOURS)`
- Двоеточие после ADDRESS: `ADDRESS: THE PALM JUMEIRAH`

---

*Справочник создан на основе анализа реальных инвойсов Marsel/Sokol*
*Версия 1.0 - 22 января 2026*
