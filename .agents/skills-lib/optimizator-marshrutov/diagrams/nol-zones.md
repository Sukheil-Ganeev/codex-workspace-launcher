# NOL Zones — Dubai Transit Zones & Tariffs
> 7 зон nol Card с ключевыми станциями и тарифами между зонами

```mermaid
graph TD
    %% ===== ZONE 1 =====
    Z1["ЗОНА 1<br/>Jebel Ali, DIP, Expo"]:::zone1
    Z1_S1["R39 Energy"]:::z1station
    Z1_S2["R40 Danube"]:::z1station
    Z1_S3["R42 Life Pharmacy"]:::z1station
    Z1_S4["R70-R76 Route 2020<br/>Discovery Gardens, Expo City"]:::z1station

    Z1 --- Z1_S1
    Z1 --- Z1_S2
    Z1 --- Z1_S3
    Z1 --- Z1_S4

    %% ===== ZONE 2 =====
    Z2["ЗОНА 2<br/>Marina, JLT, Al Barsha, SZR запад"]:::zone2
    Z2_S1["R32 Mall of the Emirates"]:::z2station
    Z2_S2["R34 Dubai Internet City"]:::z2station
    Z2_S3["R36 Sobha Realty"]:::z2station
    Z2_S4["R37 DMCC"]:::z2station
    Z2_S5["R38 Ibn Battuta"]:::z2station
    Z2_S6["TRAM 11 станций<br/>JBR, Marina, Palm"]:::z2tram

    Z2 --- Z2_S1
    Z2 --- Z2_S2
    Z2 --- Z2_S3
    Z2 --- Z2_S4
    Z2 --- Z2_S5
    Z2 --- Z2_S6

    %% ===== ZONE 5 =====
    Z5["ЗОНА 5<br/>Deira, Airport, Al Qusais"]:::zone5
    Z5_S1["R13-R14 Airport T3/T1"]:::z5station
    Z5_S2["R18 / G20 UNION"]:::z5transfer
    Z5_S3["G22 Gold Souq"]:::z5station
    Z5_S4["G11-G19 Al Qusais..."]:::z5station

    Z5 --- Z5_S1
    Z5 --- Z5_S2
    Z5 --- Z5_S3
    Z5 --- Z5_S4

    %% ===== ZONE 6 =====
    Z6["ЗОНА 6<br/>Bur Dubai, Downtown, DIFC"]:::zone6
    Z6_S1["R25 Burj Khalifa / Dubai Mall"]:::z6station
    Z6_S2["R19 / G26 BURJUMAN"]:::z6transfer
    Z6_S3["G24 Al Ghubaiba"]:::z6station
    Z6_S4["R23 Emirates Towers / DIFC"]:::z6station
    Z6_S5["G30 Creek"]:::z6station

    Z6 --- Z6_S1
    Z6 --- Z6_S2
    Z6 --- Z6_S3
    Z6 --- Z6_S4
    Z6 --- Z6_S5

    %% ===== ZONES 3,4,7 =====
    Z347["ЗОНЫ 3, 4, 7<br/>Только автобусы<br/>и водный транспорт"]:::zonebus

    %% ===== TARIFF CONNECTIONS =====
    Z1 <-->|"1 зона: 3 AED Silver / 6 Gold"| Z2
    Z2 <-->|"1 зона: 3 AED Silver / 6 Gold"| Z6
    Z5 <-->|"1 зона: 3 AED Silver / 6 Gold"| Z6
    Z1 <-->|"2 зоны: 5 AED Silver / 10 Gold"| Z6
    Z2 <-->|"2 зоны: 5 AED Silver / 10 Gold"| Z5
    Z1 <-->|"3+ зон: 7.5 AED Silver / 15 Gold"| Z5

    %% ===== STYLES =====
    classDef zone1 fill:#4A90D9,stroke:#2E6BB0,color:#FFFFFF,font-weight:bold,stroke-width:3px
    classDef zone2 fill:#E67E22,stroke:#C0681C,color:#FFFFFF,font-weight:bold,stroke-width:3px
    classDef zone5 fill:#8E44AD,stroke:#6C3483,color:#FFFFFF,font-weight:bold,stroke-width:3px
    classDef zone6 fill:#27AE60,stroke:#1E8449,color:#FFFFFF,font-weight:bold,stroke-width:3px
    classDef zonebus fill:#95A5A6,stroke:#7F8C8D,color:#FFFFFF,font-weight:bold,stroke-dasharray:5
    classDef z1station fill:#7FB3E0,stroke:#4A90D9,color:#000000
    classDef z2station fill:#F0A86E,stroke:#E67E22,color:#000000
    classDef z2tram fill:#F5C78E,stroke:#E67E22,color:#000000,stroke-width:2px
    classDef z5station fill:#B07CC8,stroke:#8E44AD,color:#000000
    classDef z5transfer fill:#D4A0E8,stroke:#8E44AD,color:#000000,stroke-width:2px
    classDef z6station fill:#6FCF97,stroke:#27AE60,color:#000000
    classDef z6transfer fill:#A3E4BF,stroke:#27AE60,color:#000000,stroke-width:2px
```

## Легенда
- **Синяя (Зона 1)** — Jebel Ali, DIP, Expo City (R39-R76)
- **Оранжевая (Зона 2)** — Marina, JLT, Al Barsha + все 11 станций Tram (R29-R38)
- **Фиолетовая (Зона 5)** — Deira, Airport, Al Qusais, Union (R11-R18, G11-G23)
- **Зеленая (Зона 6)** — Bur Dubai, Downtown, DIFC, Business Bay (R19-R26, G24-G30)
- **Серая (Зоны 3, 4, 7)** — только автобусы и водный транспорт (нет Metro)
- Тарифы: 1 зона = 3/6 AED, 2 зоны = 5/10 AED, 3+ зон = 7.5/15 AED (Silver/Gold)
- Daily Cap: Silver 14 AED, Gold 28 AED (безлимит за день)
