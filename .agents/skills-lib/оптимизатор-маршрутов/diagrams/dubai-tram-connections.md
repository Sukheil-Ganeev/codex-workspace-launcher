# Dubai Tram & Connections
> 11 станций Dubai Tram с пересадками на Metro (DMCC, Sobha Realty) и Monorail (Palm Jumeirah)

```mermaid
graph TD
    %% ===== TRAM LOOP =====
    T01["JBR 1<br/>JBR Walk, Ain Dubai"]:::tram
    T02["JBR 2<br/>Bluewaters Island"]:::tram
    T03["JLT"]:::tramtransfer
    T04["Dubai Marina Mall"]:::tram
    T05["Dubai Marina"]:::tramtransfer
    T06["Marina Towers"]:::tram
    T07["Mina Seyahi<br/>Le Meridien"]:::tram
    T08["Media City"]:::tram
    T09["Palm Jumeirah"]:::tramtransfer
    T10["Knowledge Village"]:::tram
    T11["Al Sufouh"]:::tram

    T01 --> T02 --> T03 --> T04 --> T05 --> T06 --> T07 --> T08 --> T09 --> T10 --> T11
    T11 -.->|"Петля"| T01

    %% ===== METRO RED LINE (связанные станции) =====
    M_DMCC["Metro R37 DMCC<br/>Red Line"]:::metro
    M_SOBHA["Metro R36 Sobha Realty<br/>Red Line"]:::metro

    %% ===== PALM MONORAIL =====
    PM_GW["Palm Gateway"]:::monorail
    PM_AI["Al Ittihad Park"]:::monorail
    PM_NK["Nakheel Mall"]:::monorail
    PM_AT["Atlantis Aquaventure"]:::monorail

    PM_GW --> PM_AI --> PM_NK --> PM_AT

    %% ===== CONNECTIONS =====
    T03 <-->|"~5 мин пешком<br/>Tap out/in"| M_DMCC
    T05 <-->|"~5 мин пешком<br/>Tap out/in"| M_SOBHA
    T09 <-->|"ПРИОСТАНОВЛЕН<br/>с дек 2025"| PM_GW

    %% ===== STYLES =====
    classDef tram fill:#0088CC,stroke:#006699,color:#FFFFFF,font-weight:bold
    classDef tramtransfer fill:#00AAEE,stroke:#0088CC,color:#FFFFFF,font-weight:bold,stroke-width:3px
    classDef metro fill:#FF0000,stroke:#CC0000,color:#FFFFFF,font-weight:bold
    classDef monorail fill:#888888,stroke:#666666,color:#FFFFFF,font-weight:bold,stroke-dasharray:5
```

## Легенда
- **Синие узлы** — станции Dubai Tram (11 станций, 10.6 км, Зона nol 2)
- **Синие с толстой обводкой** — пересадочные станции Tram
- **Красные узлы** — станции Metro Red Line (пересадка с Tram)
- **Серые пунктирные узлы** — Palm Monorail (ПРИОСТАНОВЛЕН с декабря 2025)
- Пересадка Metro-Tram: tap out Metro, tap in Tram (в 30 мин = одна поездка)
- Tram работает петлей: Пн-Сб 06:00-01:00, Вс 09:00-01:00, интервал 8-15 мин
