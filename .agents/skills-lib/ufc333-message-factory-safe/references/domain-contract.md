# UFC333 domain contract

## Событие

- UFC 333
- 24 октября 2026
- 17:00
- Etihad Arena, Yas Island, Abu Dhabi
- Card, наличие и цены могут меняться; card указывать только из свежего подтверждённого источника.

## Официальные категории Etihad, VAT включён

| Категория | Regular AED | Aisle AED | Наша доказанная Aisle цена |
|---|---:|---:|---:|
| Category 1 | 32,000 | не доказана отдельная | — |
| Category 2 | 25,000 | не доказана отдельная | — |
| Category 3 | 18,000 | отдельная доплата не доказана | — |
| Category 4 | 6,595 | 6,695 | 6,795 |
| Category 5 | 2,595 | 2,695 | 2,795 |
| Category 6 | 1,595 | 1,695 | 1,795 |
| Category 7 | 795 | 895 | 995 |
| Category 8 | 495 | 595 | 695 |

Эта таблица не означает, что любое место с буквой `A` автоматически получает цену. Для конкретного предложения должны быть доказаны regular base и Aisle purchase с разницей ровно 100 AED.

Live offer может отличаться от официальной базы. Например, сохранённый Cat 8 offer был 1,580 AED; его нельзя заменить на 595/695 без доказательства конкретного места.

## Категория места

- Floor A/B/C/E/F/G/H может содержать Category 1–4: нужен ряд/место.
- Sections 101–116 могут содержать Category 5–7: нужен ряд/место.
- Sections 301–315 относятся к Category 8 по общей схеме, но конкретное предложение всё равно подтверждается live.
- Окончательный mapper: Section + Row + Seat → Category evidence.
- Не классифицировать Ticketmaster Official Platinum по цене.

## Источники и комиссии

- Etihad: опубликованная цена включает VAT. В сохранённом checkout дополнительный service fee не был доказан.
- Ticketmaster: 5.25% был измерен на сохранённых примерах. Это snapshot-правило, а не вечная гарантия; перед оплатой recheck.
- Provider inventory требует recheck перед оплатой.
- Owned/investor-managed inventory не зависит от исчезновения provider offer.

## Наша цена

`full procurement cost + owner-approved fixed profit for cost range = agent base price`.

Точная ladder по диапазонам ещё не передана: `config/ufc333-owner-price-ladder.pending.json`. Пока она отсутствует, обычные позиции без другой доказанной owner price не публиковать.

Клиентская цена: agent base + фиксированный tier 10/15/20/30%, округление вверх до 10 AED. Клиенту не называть tier и base.

## Статусы

- `available` → Доступно; повторно подтвердить перед оплатой.
- `reappeared` → Снова доступно.
- `explicit_sold` / owned sold → Продано.
- `silent_disappeared`, stale, unknown, held, withdrawn → Сейчас нет в продаже (если нет более точного публичного статуса).

## Hospitality

- Etihad иногда публикует Suite/Loge цену прямо на странице.
- Tarkan example: Suite 212 = 50,000 AED; Loge 108 = 45,000 AED. Это не UFC333 pricing.
- Для UFC333 Suite 217 и Loge 108/inclusions известны; официальная опубликованная цена не доказана.
- 140,000 USD — неподтверждённое коммерческое предложение, не официальная цена, пока нет official/written evidence.

## Возраст

- Минимальный возраст не установлен в сохранённой информации.
- До 16 лет — с сопровождающим 21+.
- До 2 лет — без отдельного билета только на коленях у взрослого.

