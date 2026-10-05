# Intercity Bus Network UAE
> Автобусная сеть между 7 эмиратами: маршруты, время в пути и стоимость

```mermaid
graph TD
    %% ===== EMIRATES =====
    DUBAI["DUBAI<br/>Union BS / Al Ghubaiba / Ibn Battuta"]:::dubai
    AD["ABU DHABI<br/>Central BS"]:::abudhabi
    SHJ["SHARJAH<br/>Al Jubail BS"]:::sharjah
    AJM["AJMAN"]:::northern
    RAK["RAS AL KHAIMAH"]:::northern
    FUJ["FUJAIRAH"]:::northern
    ALAIN["AL AIN"]:::abudhabi
    HATTA["HATTA"]:::dubai

    %% ===== DUBAI <-> ABU DHABI =====
    DUBAI -->|"E100 / E101<br/>25 AED, ~2ч"| AD
    AD -->|"E100 / E101<br/>25 AED, ~2ч"| DUBAI

    %% ===== DUBAI <-> SHARJAH =====
    DUBAI -->|"E303<br/>12 AED, 30-40 мин"| SHJ
    SHJ -->|"E303<br/>12 AED, 30-40 мин"| DUBAI

    %% ===== DUBAI <-> AJMAN =====
    DUBAI -->|"E400<br/>15 AED, 40-60 мин"| AJM

    %% ===== DUBAI <-> RAK =====
    DUBAI -->|"RAKTA Bus<br/>25 AED, 1.5-2ч"| RAK

    %% ===== DUBAI <-> FUJAIRAH =====
    DUBAI -->|"E700<br/>25 AED, ~2ч 15м"| FUJ

    %% ===== DUBAI <-> AL AIN =====
    DUBAI -->|"E201<br/>25 AED, ~2ч 15м"| ALAIN

    %% ===== DUBAI <-> HATTA =====
    DUBAI -->|"H02<br/>25 AED, ~90 мин"| HATTA

    %% ===== ABU DHABI <-> AL AIN =====
    AD -->|"X90<br/>25-30 AED, ~2.5ч"| ALAIN

    %% ===== ABU DHABI <-> RAK =====
    AD <-->|"RAKTA<br/>47 AED, ~3-3.5ч<br/>Пт-Вс"| RAK

    %% ===== SHARJAH <-> OTHERS =====
    SHJ -->|"114<br/>5-6 AED, 20-30 мин"| AJM
    SHJ -->|"115<br/>27-30 AED, ~1.5ч"| RAK
    SHJ -->|"116<br/>27-30 AED, ~2ч"| FUJ
    SHJ -->|"117<br/>30-35 AED, ~2.5ч"| AD
    SHJ -->|"118<br/>35 AED, ~1.5-2ч"| ALAIN

    %% ===== STYLES =====
    classDef dubai fill:#1E90FF,stroke:#1565C0,color:#FFFFFF,font-weight:bold,stroke-width:3px
    classDef abudhabi fill:#DAA520,stroke:#B8860B,color:#FFFFFF,font-weight:bold,stroke-width:3px
    classDef sharjah fill:#9370DB,stroke:#7B2D8E,color:#FFFFFF,font-weight:bold,stroke-width:2px
    classDef northern fill:#2E8B57,stroke:#1B5E20,color:#FFFFFF,font-weight:bold
```

## Легенда
- **Синий (Dubai)** — главный хаб: Union BS (E303, E400, E700, RAKTA), Al Ghubaiba (E100, E201), Ibn Battuta (E101)
- **Золотой (Abu Dhabi, Al Ain)** — эмират Abu Dhabi: Central BS, X90 до Al Ain
- **Фиолетовый (Sharjah)** — Al Jubail BS: транзитный хаб для северных эмиратов (114-118)
- **Зеленый** — северные эмираты (Ajman, RAK, Fujairah)
- Оплата: E-маршруты = nol Card, SRTA (114-118) = Sayer Card, RAKTA = Saqr Card, ITC (X90) = Hafilat Card
