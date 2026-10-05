# Etihad Rail — National Railway UAE
> Национальная железная дорога ОАЭ: 11 станций, до 200 км/ч, запуск 2026

```mermaid
graph LR
    %% ===== MAIN LINE: Abu Dhabi - Dubai - Sharjah - Fujairah =====
    MBZ["Mohammed Bin Zayed City<br/>ABU DHABI"]:::abudhabi
    JGE["Jumeirah Golf Estates<br/>DUBAI"]:::dubai
    UC["University City<br/>SHARJAH"]:::sharjah
    ALHILAL["Al Hilal<br/>FUJAIRAH"]:::fujairah

    MBZ -->|"57 мин"| JGE
    JGE -->|"~15-20 мин"| UC
    UC -->|"~50 мин от Dubai"| ALHILAL

    %% ===== WESTERN LINE =====
    ALSILA["Al Sila<br/>AD запад"]:::west
    ALDH["Al Dhannah<br/>AD запад"]:::west
    ALMIRFA["Al Mirfa<br/>AD запад"]:::west
    MZ["Madinat Zayed<br/>AD запад"]:::west
    MEZ["Mezairaa<br/>AD / Liwa"]:::west

    ALSILA --> ALDH --> ALMIRFA --> MZ --> MEZ

    %% ===== EASTERN BRANCH =====
    ALFAYA["Al Faya<br/>SHJ восток"]:::east
    ALDHAID["Al Dhaid<br/>SHJ центр"]:::east

    ALFAYA --> ALDHAID

    %% ===== CONNECTIONS TO MAIN =====
    MBZ ---|"Западная ветка"| ALSILA
    MBZ ---|"1ч 10м до Al Ruwais"| ALMIRFA
    UC ---|"Восточная ветка"| ALFAYA

    %% ===== FUTURE HIGH-SPEED =====
    HS_AD["Abu Dhabi HS<br/>ПЛАН 2030"]:::future
    HS_DXB["Dubai HS<br/>ПЛАН 2030"]:::future
    HS_AD -.->|"350 км/ч<br/>30 мин"| HS_DXB

    %% ===== STYLES =====
    classDef abudhabi fill:#DAA520,stroke:#B8860B,color:#FFFFFF,font-weight:bold,stroke-width:3px
    classDef dubai fill:#1E90FF,stroke:#1565C0,color:#FFFFFF,font-weight:bold,stroke-width:3px
    classDef sharjah fill:#9370DB,stroke:#7B2D8E,color:#FFFFFF,font-weight:bold,stroke-width:2px
    classDef fujairah fill:#2E8B57,stroke:#1B5E20,color:#FFFFFF,font-weight:bold,stroke-width:2px
    classDef west fill:#CD853F,stroke:#8B6914,color:#FFFFFF,font-weight:bold
    classDef east fill:#5F9EA0,stroke:#2F4F4F,color:#FFFFFF,font-weight:bold
    classDef future fill:#333333,stroke:#555555,color:#AAAAAA,font-weight:bold,stroke-dasharray:5
```

## Легенда
- **Золотой** — Abu Dhabi (Mohammed Bin Zayed City — главная станция)
- **Синий** — Dubai (Jumeirah Golf Estates — рядом с Red Line R73)
- **Фиолетовый** — Sharjah (University City)
- **Зеленый** — Fujairah (Al Hilal)
- **Коричневые** — западная ветка (Al Sila, Al Dhannah, Al Mirfa, Madinat Zayed, Mezairaa)
- **Бирюзовые** — восточная ветка (Al Faya, Al Dhaid)
- **Серые пунктирные** — высокоскоростная линия AD-Dubai (план 2030, 350 км/ч, 30 мин)
- Скорость: до 200 км/ч | Вместимость: ~400 пассажиров | Интеграция с nol Card
