---
name: limo-order-manager
description: "Управление лимузинными заказами — генерация бланков, подбор партнёра, калькулятор цен, бронирование, CRM. Используй когда нужно создать заказ на трансфер, выбрать партнёра, рассчитать цену, найти клиента, подготовить бронь/booking для поставщика (TJ, Raja), забронировать машину."
---
# Лимузинный менеджер заказов

## Триггеры
- "заказ на трансфер", "трансфер", "лимузин"
- "бланк заказа", "VIP transfer"
- "бронь", "забронируй", "бронирование", "booking", "подготовь бронь"
- "напиши бронь для поставщика", "бронь для TJ", "бронь для Raja"
- "какой партнёр", "выбери партнёра"
- "цена трансфера", "сколько стоит трансфер"
- "найди клиента", "профиль клиента"

## Данные
- **Корень:** `D:/MARSEL_BUSINESS/`
- **Партнёры:** `01_partners/limousine/`
- **Клиенты:** `02_clients/` (55 профилей)
- **Заказы:** `03_orders/` (113 заказов)
- **Маржа:** `04_finance/margins/by_route.json`
- **KPI:** `05_analytics/kpi/partner_scorecard.json`
- **SOP:** `06_operations/sop/`

## Партнёры

### Раджа Зарьяб (Funsho Signature Limousine)
- **Сегмент:** Эконом-бизнес
- **Флот:** Lexus ES350 (3), GMC Yukon (2), V-Class (1), S-Class (по запросу)
- **НЕТ:** Escalade, Sprinter, Maybach
- **НЕ обслуживает:** Sharjah Airport, RAK
- **Часы:** 08:00-22:00
- **Score:** 7.2/10

### TJ Faisal (Tee Jay Limousine)
- **Сегмент:** Премиум-VIP
- **Флот:** V-Class (5), S-Class (3), Escalade (2), Sprinter (2), GMC (2), Lexus (2), BMW (1), Maybach (по запросу)
- **Покрытие:** Все эмираты включая Sharjah/RAK
- **Часы:** 24/7 (OPS team)
- **Score:** 8.4/10

## B2B Прайс-лист (AED)

### Трансферы (1 way)
| Маршрут | Lexus (Раджа) | V-Class | GMC | S-Class | Escalade (TJ) |
|---|---|---|---|---|---|
| DXB <-> Dubai Hotel | 150-180 | 300 | 300 | 400-500 | 600 |
| DXB <-> Abu Dhabi | 350-400 | 700 | 700 | 900 | — |
| DXB <-> Fujairah | 400-500 | 800 | — | — | — |
| DXB <-> RAK | 350 | 600 | — | — | — |
| DXB <-> Sharjah | 200 | 400 | — | — | — |
| Al Maktoum <-> Dubai | 250 | — | — | — | — |

### Почасовая (с водителем)
| Модель | 5ч | 8ч | 10ч | Extra час |
|---|---|---|---|---|
| Lexus (Раджа) | — | — | 800 | 80 |
| GMC (Раджа) | 700 | 1,000 | 1,300 | 150 |
| V-Class | — | — | 1,300-1,400 | 100 |
| S-Class | — | — | 2,000-2,500 | — |
| Escalade (TJ) | — | — | 1,800-2,200 | — |
| Sprinter (TJ) | — | — | 1,000-1,800 | — |
| Maybach (TJ) | — | — | 3,500-4,500 | — |

## Правила маржи
- **Минимум:** 20% (для удержания VIP)
- **Целевая:** 30-35%
- **Пик (нояб-фев):** +15%
- **Новый год:** +50%

## Матрица выбора партнёра

| Условие | Партнёр |
|---|---|
| Lexus / GMC, стандарт | **Раджа** (дешевле) |
| V-Class стандарт | **Раджа** первый |
| V-Class для VIP | **TJ** (надёжнее) |
| S-Class | Оба (цены равны) |
| Escalade | **Только TJ** |
| Sprinter (группа) | **Только TJ** |
| Maybach | **Только TJ** |
| Sharjah / RAK | **Только TJ** |
| Срочно (< 2ч) | **TJ** (24/7) |
| Ночной | **TJ** (24/7) |

## Команды

### /limo-order — Создать заказ
Формат: `/limo-order [дата] [время] [маршрут], [авто], [pax] чел, [имя] [телефон], [рейс]`

Пример:
```
/limo-order 20.11.2025 14:30 DXB T1 -> W Mina Seyahi, V-Class, 3 чел, Staravoitau Aleksandr +375297180410, SU 520
```

Действия:
1. Определить партнёра по матрице
2. Рассчитать B2B и клиентскую цену
3. Сгенерировать VIP Transfer Blank
4. Создать JSON заказа в 03_orders/
5. Обновить профиль клиента (или создать новый)

### /limo-price — Калькулятор цены
Формат: `/limo-price [маршрут] [авто]`

Пример: `/limo-price DXB -> Abu Dhabi, V-Class`

Вывод:
```
Маршрут: DXB -> Abu Dhabi Hotel
Авто: Mercedes V-Class
Партнёр: Раджа или TJ (оба доступны)
B2B цена: 700 AED
Клиентская цена:
  - Минимум: 950 AED (маржа 26%)
  - Рекомендуемая: 1,050 AED (маржа 33%)
  - Максимум: 1,300 AED (маржа 46%)
Пиковый сезон (+15%): 1,200 AED
```

### /limo-partner — Подбор партнёра
Формат: `/limo-partner [авто] [маршрут] [тип клиента]`

### /limo-client — Поиск клиента
Формат: `/limo-client [имя или телефон]`

Действия:
1. Поиск в D:/MARSEL_BUSINESS/02_clients/profiles/
2. Показать профиль: имя, страна, tier, историю заказов
3. Если не найден — предложить создать

### /limo-report — Отчёт
Формат: `/limo-report [период]`

Примеры:
- `/limo-report 2025-11` — месячный
- `/limo-report partner raja` — по партнёру
- `/limo-report client CLI-0001` — по клиенту

## Формат VIP Transfer Blank

```
*VIP TRANSFER ORDER*

*ORDER ID:* {{order_id}}
*ORDER DATE:* {{date}}

*MEETING TIME:* {{time}}
*FLIGHT NUMBER:* {{flight}}

*MEETING POINT:* {{pickup}}
*DROP OFF POINT:* {{dropoff}}

*TRANSPORT MODEL:* {{vehicle}}
*NUMBER OF PEOPLE:* {{pax}}

*FULL NAME:* {{name}}
*Contact Number:* {{phone}}

*ORDER AMOUNT:* {{amount}} AED
*PAYMENT:* {{payment_method}}
```

## Сезонность
- **Пик:** Ноябрь (index 100), Февраль (90), Декабрь (80)
- **Мертвый сезон:** Июнь (10), Июль (5), Август (8)
- Готовить мощности к ноябрю с сентября!

## Связанные файлы
- SOP: `D:/MARSEL_BUSINESS/06_operations/sop/order_processing.md`
- Чек-лист: `D:/MARSEL_BUSINESS/06_operations/checklists/new_order_checklist.md`
- Маржа: `D:/MARSEL_BUSINESS/04_finance/margins/by_route.json`
- KPI: `D:/MARSEL_BUSINESS/05_analytics/kpi/partner_scorecard.json`
