# MASTER-КОНТЕКСТ — Операционная система продаж билетов и мероприятий

**Версия:** 1.0  
**Дата сборки:** 2 сентября 2026  
**Основа:** 10 переписок Марселя с ChatGPT, около 65 000 строк.  
**Назначение:** единый контекст проекта для AI и рабочий регламент для человека.

---

## 1. Что это за бизнес

Марсель работает с билетами и event-продуктами как посредник/организатор для партнёров, агентов и их клиентов. Типовые продукты:

- обычные билеты на концерты и спорт;
- premium/VIP/VVIP места;
- hospitality, lounges, suites, boxes, tables;
- Formula 1 / MotoGP / UFC / футбол / теннис;
- многодневные программы вроде Dakar;
- пакеты ticket + hotel / transport / experiences;
- групповые запросы, где нужно много мест рядом;
- рекламные прайс-листы для партнёров.

Главная ценность бизнеса — не просто найти ссылку, а **найти реальный продукт, проверить риски, посчитать полную себестоимость, упаковать понятное предложение и сопровождать покупку/передачу**.

## 2. Две аудитории — два разных ответа

### 2.1. Внешний блок: партнёр/клиент

Он должен содержать только то, что человек может использовать для продажи или принятия решения:

- событие, дата, время, площадка;
- доступные категории и точное количество;
- sector/row/seats, если они подтверждены;
- seats together, если это гарантируется;
- подтверждённые inclusions;
- конечная цена продажи;
- возраст;
- важные правила входа;
- предупреждение о live availability.

Он **не должен** содержать закупку, прибыль, supplier, внутренний резерв, путь поиска, внутренние сомнения и ссылки на закупочный канал, если Марсель не попросил обратное.

### 2.2. Внутренний блок: только для Марселя

Он содержит:

- источник и прямую ссылку;
- статус источника: official / authorised / supplier / secondary;
- номинал и all-in checkout;
- fee breakdown;
- currency and working rate;
- bank/FX reserve;
- full cost;
- selling price;
- profit per ticket / order / actual percentage;
- delivery, transfer, real-name, lead-booker;
- refund/cancellation;
- риск и что ещё подтвердить.

## 3. Обязательный рабочий процесс для любого нового запроса

### Шаг 1 — нормализовать запрос

Зафиксировать:

1. точное событие;
2. город/страну;
3. дату и сессию;
4. количество гостей;
5. взрослые/дети и возраст;
6. seats together;
7. нужную категорию/сектор/ряд;
8. бюджет;
9. нужен ли VIP/hospitality;
10. готовность купить сейчас или запрос на рекламу.

### Шаг 2 — проверить историю проекта

До веб-поиска найти старую работу по событию:

- какие варианты уже отправлялись;
- какая цена была названа;
- какая закупка была тогда;
- какая формула прибыли использовалась;
- какие источники были исключены;
- что клиент отклонил/выбрал;
- статус: в работе / ждём / отправлено / закрыто.

Если текущая full cost позволяет — сохранить старую продажную цену.

### Шаг 3 — проверить сам факт события

Проверить exact name, date, venue, session/day, start time and current status. Не смешивать похожие события: UFC Shanghai и Shanghai Masters; final и semifinal; Day и Night; concert-only и F1 ticket + concert.

### Шаг 4 — пройти лестницу источников

1. organizer;
2. venue;
3. official ticket operator;
4. official hospitality/experiences;
5. authorised partners;
6. known suppliers;
7. StubHub / Viagogo / Ticombo / other secondary;
8. aggregators — только для рынка, не как автоматическая закупка.

### Шаг 5 — собрать всю продуктовую линейку

Не ограничиваться одним дешёвым билетом. Проверить:

- GA/standing;
- standard seated;
- premium seated;
- VIP/VVIP;
- lounge/loge/club;
- hospitality;
- suites/boxes/tables;
- paddock/pit lane/team packages;
- ticket + hotel / transport / experiences;
- child/family/special bundles.

Добавлять продукт можно только при подтверждённом event-specific inventory.

### Шаг 6 — проверить механику билета

- PDF / mobile / app / dynamic QR / physical / box office;
- когда билет или QR станет доступен;
- transfer available? when?;
- name change?;
- lead booker required?;
- real-name and passport/ID;
- face verification;
- original card/ID requirements;
- delivery deadline;
- refund/exchange.

### Шаг 7 — проверить места и рассадку

- category;
- level;
- section;
- row;
- seat numbers;
- quantity together;
- aisle or regular;
- seat assignment now or later;
- category-only sale or exact seat sale.

Не превращать “2 together” в выдуманные seat numbers. Не обещать seats together без подтверждения.

### Шаг 8 — дойти до checkout

Зафиксировать:

- base ticket price;
- tax;
- per-ticket fee;
- per-order fee;
- marketplace/service fee;
- delivery/FedEx;
- payment method surcharge;
- currency;
- final total.

Не оплачивать, если задача только проверить стоимость.

### Шаг 9 — посчитать полную себестоимость

**Full cost = purchase + confirmed fees + taxes + delivery/transfer + payment/FX reserve.**

Для non-AED purchase по умолчанию используется 5% bank/FX reserve, пока нет фактического списания. Для AED purchase 5% автоматически не добавляется.

### Шаг 10 — применить локальное правило прибыли

Не переносить 35/40/50/60% автоматически. Ищется последняя формула именно этого события/клиента/category. Возможны:

- процент от full cost;
- фиксированная прибыль;
- разные правила для low-cost и premium;
- отдельная прибыль посредника;
- комбинированная схема.

Если правила нет — показать Марселю рынок и сценарии.

### Шаг 11 — проверить рынок

Сравнить selling price с official/secondary market. Это не заменяет sourcing, но помогает понять, не слишком ли дешёвая или дорогая наша цена.

### Шаг 12 — подготовить два блока

1. **TXT для партнёра** — чистый, естественный, конечная цена.
2. **Внутренний расчёт** — таблица, ссылки, риск, full cost, profit.

### Шаг 13 — повторная проверка перед оплатой

Перед получением/переводом денег заново проверить выбранный listing/product, quantity, seats, all-in total, transfer and restrictions. Availability live.

## 4. Система расчёта цены и прибыли

### 4.1. Единица расчёта

Сначала определить, что продаётся:

- один билет;
- пара;
- group of 4;
- table;
- sofa;
- box/suite целиком;
- многодневный package per guest.

Нельзя пересчитывать suite per person, если продавец даёт цену за suite, без отдельной просьбы.

### 4.2. Валюта

- партнёрские цены по умолчанию — USD;
- AED/USD working rate — 3.65, если Марсель не дал другой;
- для других валют использовать актуальный курс, но отдельно учитывать card FX;
- не путать SGD, HKD, CNY, QAR, SAR, TRY, GEL, KZT, ARS с USD.

### 4.3. Порядок учёта комиссий и расходов

1. confirmed seller fee;
2. confirmed marketplace fee;
3. confirmed tax;
4. delivery/collection;
5. payment method fee;
6. bank/FX reserve;
7. profit.

Если fee уже all-in — второй раз не добавлять. Если fee не подтверждён — помечать reserve, а не platform commission.

### 4.4. Внутренняя таблица прибыли

Минимальные колонки:

| Product | Base | Confirmed fees | Reserve | Full cost | Selling price | Profit/unit USD | Profit/order USD | Actual % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|

Формула контроля:

`Selling price − Full cost = Actual profit`

## 5. Стандарт сообщения партнёру или клиенту

### 5.1. Формат

- отдельный code block `txt`;
- WhatsApp bold: `*text*`;
- никаких markdown tables в WhatsApp;
- небольшое количество эмодзи;
- варианты разделять `➖➖➖`;
- от дешёвого к дорогому;
- в конце: live availability / reconfirm before payment.

### 5.2. Стандартный блок одного варианта

*Вариант N — CATEGORY*

*Уровень:* ...  
*Сектор:* ...  
*Ряд:* ...  
*Места:* ... *(N мест рядом)*  
*Стоимость:* *... USD за билет*

Короткое правдивое описание обзора/преимущества.

### 5.3. Неизвестные или неподтверждённые детали

Если row/seats неизвестны:

- «Точные ряд и места подтверждаются перед оплатой»;
- «Сейчас продукт продаётся по категории»;
- «Места вместе гарантируются» — только если это действительно гарантировано.

## 6. Конфиденциальность и правдивое позиционирование

Партнёру не показывается supply chain. Supplier также не обязан знать лишние данные о downstream-клиенте. Но нельзя:

- утверждать официальный статус без основания;
- говорить «у нас на руках», если есть только listing;
- обещать 100% fulfillment без verification;
- скрывать критическое real-name/transfer ограничение;
- придумывать inclusions.

Правильная формулировка: «можем предложить», «предварительно доступно», «повторно подтвердим перед оплатой».

## 7. Универсальный контроль рисков

### 7.1. Возрастные ограничения

Всегда проверить:

- minimum age;
- separate ticket age;
- adult accompaniment;
- adult minimum age;
- standing restrictions;
- lounge/hospitality restrictions;
- child not allowed even with adult.

### 7.2. Вторичный рынок и перепродажа

Перед secondary purchase проверить:

- organizer resale warning;
- transfer function;
- lead booker;
- seller proof/allocation;
- ticket-in-hand;
- delivery deadline;
- travel-loss exposure;
- guarantee limitations.

### 7.3. Именные билеты и документы

Если один билет = один ID:

- получить guest data до оплаты;
- покупать сразу на конечного гостя;
- не обещать transfer/name change;
- проверить original ID and facial recognition;
- учесть per-account ticket limit and group seating risk.

### 7.4. Большие группы

Проверить:

- maximum tickets per order;
- exact block;
- adjacent rows;
- group allocation;
- supplier hold;
- invoice/payment deadline;
- split orders;
- cancellation liability.

## 8. Краткая матрица по типам мероприятий

### Formula 1

Линейка: GA → Grandstand → Club → Hospitality → Champions Club → Paddock Club → Team Suite / F1 Garage. Всегда указывать access days, seat/view, concerts, upgrade, F&B, alcohol, parking, paddock/pit lane and age.

### UFC/MMA

Указывать current card, title bouts, venue, start, age, section/row/seats, cage view. Проверять weigh-in separately. Для Азии — real-name, face verification and late seat allocation.

### Концерты и фестивали

Door/opening time, artist/support act, standing/seated, age/height, stage map, dynamic QR, transfer, resale warning. Не обещать setlist; можно дать expected songs как отдельный непредсказуемый блок только при явной маркировке.

### Футбол

Kickoff may be TBC. Reseller categories are not official until mapped. Проверять mobile membership/card, lead booker, away fan restrictions and pair guarantee.

### Теннис

Дата/сессия важнее имени игрока. Различать category и row, Day/Night/All Day, Center Court/Grandstand/Ground Pass, VIP/hospitality.

### MotoGP/MXGP

Различать race-weekend access and hospitality days. GA may be standing/free seating. Проверять child category and paddock experience age.

### Dakar и экспедиционные программы

Это expedition product: route, daily transport, accommodation, camps, meals, viewpoints, bivouac, luggage, room configuration, VAT and cancellation.

### K-pop и азиатские мероприятия

Проверять membership presale, real-name, pickup/app/physical, transfer, age/height, fan benefits and ticket+hotel packages. Не продавать pre-sale promise как inventory.

## 9. Стандарт рекламного пакета

Для рекламируемого продукта подготовить:

1. название и location;
2. exact dates/session structure;
3. short selling description;
4. product ladder from budget to VVIP;
5. clean venue map without procurement prices;
6. age rules;
7. delivery/transfer/real-name;
8. refund/cancellation;
9. hospitality/suites;
10. content/media suggestions;
11. recommendation not to publish fixed price when volatile;
12. internal market comparison and pricing guidance.

## 10. Актуальность источников

Этот MASTER хранит **метод работы**, а не гарантирует актуальность старых событий. Перед использованием обязательно заново проверять:

- availability;
- dates/times;
- line-up/card/order of play;
- ticket policies;
- fees;
- email contacts;
- bank/card conditions;
- exchange rates.

Скриншоты в исходных TXT не вложены: в файлах сохранены только пометки об изображениях и текстовые выводы из них. Поэтому screenshot-derived numbers следует считать историческими, пока они не перепроверены.

## 11. Критерии готового результата

Запрос считается качественно обработанным, когда:

- история проверена;
- event verified;
- official and secondary sources reviewed;
- full product range considered;
- exact unit/quantity defined;
- checkout/all-in known or clearly marked pending;
- age and ticket mechanics checked;
- full cost calculated;
- profit rule confirmed;
- market comparison made;
- partner TXT clean;
- internal block complete;
- pre-payment recheck instruction included.
