# Transit Decision Tree — Авто vs Общественный транспорт
> Дерево решений для выбора оптимального транспорта в Дубае и ОАЭ

```mermaid
flowchart TD
    START(["ЗАПРОС КЛИЕНТА<br/>Как добраться?"]):::start

    %% ===== LEVEL 1: TIME =====
    START --> Q_TIME{"Время суток?"}:::question
    Q_TIME -->|"00:00-05:00<br/>или Вс до 08:00"| TAXI_NIGHT["ТАКСИ / Careem / Uber<br/>Metro закрыто"]:::taxi

    Q_TIME -->|"Рабочие часы<br/>05:00-00:00"| Q_BUDGET{"Бюджет<br/>ограничен?"}:::question

    %% ===== LEVEL 2: BUDGET =====
    Q_BUDGET -->|"ДА"| TRANSIT["METRO + BUS<br/>Daily Cap 14 AED"]:::transit

    Q_BUDGET -->|"НЕТ"| Q_GROUP{"Размер<br/>группы?"}:::question

    %% ===== LEVEL 3: GROUP =====
    Q_GROUP -->|"1-2 человека"| Q_METRO{"Локация на<br/>линии Metro?"}:::question

    Q_GROUP -->|"3-4 человека"| TAXI_GROUP["ТАКСИ<br/>35 AED на всех<br/>= как Metro x4"]:::taxi

    Q_GROUP -->|"5+ человек"| COMBO_GROUP["2 ТАКСИ или<br/>METRO + большое такси"]:::combo

    %% ===== LEVEL 4: METRO ACCESS =====
    Q_METRO -->|"ДА"| Q_BAGGAGE{"Тяжелый<br/>багаж?"}:::question

    Q_METRO -->|"НЕТ<br/>Safari, Miracle Garden,<br/>Global Village..."| Q_COMBO{"Есть Metro<br/>поблизости?"}:::question

    %% ===== LEVEL 5: BAGGAGE =====
    Q_BAGGAGE -->|"НЕТ"| METRO["METRO / TRAM<br/>3-7.5 AED"]:::transit

    Q_BAGGAGE -->|"ДА<br/>Чемоданы,<br/>покупки"| TAXI_COMFORT["ТАКСИ<br/>Комфорт важнее"]:::taxi

    %% ===== LEVEL 5: COMBO =====
    Q_COMBO -->|"ДА"| COMBO_METRO["КОМБО:<br/>Metro до ближайшей<br/>станции + такси<br/>последняя миля"]:::combo

    Q_COMBO -->|"НЕТ"| TAXI_DIRECT["ТАКСИ напрямую<br/>Нет альтернатив"]:::taxi

    %% ===== INTERCITY BRANCH =====
    START --> Q_INTERCITY{"Межгород?"}:::question
    Q_INTERCITY -->|"Dubai-Abu Dhabi"| Q_IC_GROUP{"Группа?"}:::question
    Q_IC_GROUP -->|"1-2 чел"| BUS_AD["E100/E101 АВТОБУС<br/>25 AED, ~2ч<br/>Экономия 225 AED"]:::transit
    Q_IC_GROUP -->|"3+ чел"| TAXI_AD["ТАКСИ<br/>250 AED / группу<br/>~83 AED/чел"]:::taxi

    Q_INTERCITY -->|"Dubai-Sharjah"| BUS_SHJ["E303 АВТОБУС<br/>12 AED, 30-40 мин"]:::transit

    Q_INTERCITY -->|"Другие эмираты"| BUS_OTHER["E-АВТОБУСЫ<br/>22-30 AED<br/>nol Card"]:::transit

    %% ===== EXAMPLES =====
    METRO --> EX1["Airport T3 -> Downtown<br/>3 AED, 27 мин"]:::example
    COMBO_METRO --> EX2["Downtown -> Atlantis<br/>Metro+Tram+такси ~15 AED"]:::example
    TAXI_COMFORT --> EX3["С чемоданами из DXB<br/>70 AED, 20 мин"]:::example

    %% ===== STYLES =====
    classDef start fill:#1A1A2E,stroke:#16213E,color:#FFFFFF,font-weight:bold,stroke-width:3px
    classDef question fill:#2C3E50,stroke:#1A252F,color:#FFFFFF,font-weight:bold
    classDef transit fill:#27AE60,stroke:#1E8449,color:#FFFFFF,font-weight:bold
    classDef taxi fill:#E74C3C,stroke:#C0392B,color:#FFFFFF,font-weight:bold
    classDef combo fill:#F39C12,stroke:#D68910,color:#FFFFFF,font-weight:bold
    classDef example fill:#34495E,stroke:#2C3E50,color:#BDC3C7,font-size:11px
```

## Легенда
- **Темные узлы** — вопросы-решения (время, бюджет, группа, багаж, локация)
- **Зеленые** — общественный транспорт (Metro, Tram, Bus) — выгодно для 1-2 человек
- **Красные** — такси / Careem / Uber — для групп, ночью, с багажом
- **Оранжевые** — комбо Metro + такси (оптимальное соотношение цена/время)
- **Серые** — примеры конкретных маршрутов с ценами

### Ключевые правила
1. **Ночь (00:00-05:00, Вс до 08:00)** — только такси
2. **Бюджет** — всегда Metro/Bus (Daily Cap 14 AED)
3. **3+ человек** — такси выгоднее (35 AED / 4 = 8.75 AED/чел)
4. **Solo/пара на Metro** — экономия 70-90%
5. **Нет Metro рядом** — комбо Metro + такси последняя миля
