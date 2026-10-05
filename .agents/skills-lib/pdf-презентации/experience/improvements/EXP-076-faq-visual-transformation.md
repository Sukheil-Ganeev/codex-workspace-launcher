# EXP-076: Визуальная трансформация FAQ-слайдов (VIP-DXB)

## Контекст
9 слайдов FAQ_50_ВОПРОСОВ: Виза, Транспорт, Деньги, Климат, Безопасность, Связь, Услуги. Каждый содержал 3-4 Q&A пары в плоском текстовом формате.

## Результат
837 строк HTML → 1463 строки. Каждый слайд стал визуально богатым с уникальным оформлением.

## Техники по темам

### Виза — Metric-блоки + Price Rows
- Числовые данные (90 дней, 30 дней) → metric-cards с зелёным/синим градиентом
- Стоимость виз → price rows: label слева, colored tag справа
- Типы виз → tag strip (tourist/transit/work)
- Штрафы → red tags, легальные опции → green tags

### Транспорт — Icon-Cards + Warning Boxes
- Виды транспорта (taxi/metro/bus) → 3 icon-cards с иконками и ценами
- Правила вождения → red warning box ("Rights not accepted")
- Промо услуги → green promo box ("МВУ от Марселя")

### Деньги — Currency Metrics + Payment Grid
- Валюта/курсы → 3 metric-cards (AED, USD=3.67, 100AED~27$)
- Методы оплаты → 2x2 или 2x3 grid mini-cards с цветными фонами
- Статус платёжных систем → status table (Visa=✅, Мир=❌)

### Климат — Season Cards + Dress Code Icons
- 4 сезона → 4 карточки в ряд: иконка погоды, температура крупно, рекомендация tag
- Дресс-код → icon-based список (mall/beach/mosque) с venue иконками
- Red warning box для ограничений

### Безопасность — ЗАПРЕЩЕНО/НУЖНО + Side-by-Side
- TOP-3 metric (безопасность = TOP-3 в мире)
- ЗАПРЕЩЕНО: red X marks + penalty tags (штраф 500-5000 AED)
- НУЖНО: green checkmarks
- Алкоголь/Фото: can/cannot side-by-side blocks (green/red)

### Связь — Provider Cards + Availability Grid
- 2 провайдера → side-by-side cards (Etisalat blue, du purple)
- Wi-Fi → 2x3 grid с checkmarks (Hotels✅, Metro~, Parks~)
- Мессенджеры → status table (WhatsApp=text✅, calls❌, BOTIM=50AED)

### Услуги — Service Cards + Channel Rows
- 4 категории услуг → icon-cards (Городские, Приключения, Билеты, Водные)
- Каналы бронирования → icon rows с описаниями
- Методы оплаты → 3x2 grid
- Скидки → colored discount tags

## Переиспользуемые компоненты

### Price Row
```html
<div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.06);">
  <span style="font-size:15px;">Tourist Visa (30 дней)</span>
  <span class="tag tag-yellow">350 AED</span>
</div>
```

### Icon-Card (3 в ряд)
```html
<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:12px;">
  <div class="card" style="padding:16px; text-align:center; border-top:3px solid var(--accent-1);">
    <div style="font-size:24px;">🚕</div>
    <h4>Taxi</h4>
    <p>Start: <span class="tag tag-green">12 AED</span></p>
  </div>
</div>
```

### Status Table
```html
<table class="styled-table">
  <tr><td>Visa/MC</td><td><span class="tag tag-green">Везде</span></td></tr>
  <tr><td>МИР</td><td><span class="tag tag-red">Не работают</span></td></tr>
</table>
```

### Can/Cannot Side-by-Side
```html
<div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
  <div style="padding:12px; border-left:3px solid #10B981; background:rgba(16,185,129,0.05);">
    <strong style="color:#10B981;">✓ Можно</strong>
    <ul>...</ul>
  </div>
  <div style="padding:12px; border-left:3px solid #EF4444; background:rgba(239,68,68,0.05);">
    <strong style="color:#EF4444;">✕ Нельзя</strong>
    <ul>...</ul>
  </div>
</div>
```

### Season Card
```html
<div class="card" style="padding:16px; text-align:center; background:linear-gradient(135deg, rgba(59,130,246,0.08), transparent);">
  <div style="font-size:24px;">❄️</div>
  <h4>Зима</h4>
  <div style="font-size:28px; font-weight:700; color:#3B82F6;">20-25°C</div>
  <span class="tag tag-green">Лучший сезон</span>
</div>
```

## Тэги
#improvement #faq #visual #transformation #components #vip-dxb
