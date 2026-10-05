# Experience Index — viber-bot-справочник

> Актуально на: 2026-02-27

## Критические уроки (топ-5)

### 1. HMAC ключ = auth_token (НЕ app_secret!)
**Дата:** 2026-02-27 | **Источник:** VIP-DXB-CatalogBot Phase 21
Viber использует `auth_token` как HMAC ключ, а Meta (IG/WA) -- `app_secret`. Заголовок: `X-Viber-Content-Signature` (без `sha256=` prefix). При переносе кода с Meta бота -- обязательно менять ключ.

### 2. conversation_started != subscribed
**Дата:** 2026-02-27 | **Источник:** VIP-DXB-CatalogBot Phase 21
При `conversation_started` пользователь НЕ подписан -- можно отправить только 1 welcome message. Нельзя слать follow-up. Пользователь подписывается только при отправке первого сообщения или нажатии кнопки. Событие `subscribed` сбрасывает tracking_data.

### 3. Hybrid FSM: tracking_data + in-memory fallback
**Дата:** 2026-02-27 | **Источник:** VIP-DXB-CatalogBot Phase 21
tracking_data (до 4096 chars) возвращается с ответом пользователя -- stateless FSM без сервера. Но нужен fallback: текст вводится без кнопки (tracking_data пустой), JSON обрезается, переподписка сбрасывает. Гибридный подход: encode в tracking_data + параллельно сохранять в in-memory dict.

### 4. Viber location = "lon" (не "lng"!)
**Дата:** 2026-02-27 | **Источник:** VIP-DXB-CatalogBot Phase 21
Viber использует `location.lon` для долготы (не `lng` как Google Maps и другие). При обработке геолокации -- обязательно `location.get("lon")`.

### 5. Rich Media PAGE_SIZE = 5 (max ~42 строк)
**Дата:** 2026-02-27 | **Источник:** VIP-DXB-CatalogBot Phase 21
При 8 строках на карточку (image 3 + text 2 + buttons 2x1 + separator 1), максимум ~5 карточек. 5 x 8 = 40 строк. Если больше -- добавлять "More" пагинацию. ButtonsGroupRows определяет группировку в карусели.

## Статистика
- Всего записей: 5
- Последнее обновление: 2026-02-27

## Полные записи

### Phase 21 VIP-DXB-CatalogBot (2026-02-27)
- **Проект:** VIP-DXB-CatalogBot -- Viber Bot для туристического бизнеса ОАЭ
- **Стек:** FastAPI + httpx + SQLite (aiosqlite) + WAL mode
- **Порт:** 8084 (конвенция: IG=8081, WA=8082, FB=8083, Viber=8084)
- **SDK:** НЕ используется viberbot Python SDK (sync, Flask). Прямые HTTP через httpx AsyncClient
- **FSM:** Hybrid tracking_data (stateless) + in-memory fallback с 1h timeout
- **DB:** synthetic_user_id (-3000, -3001...) для переиспользования CatalogDB
- **form_type:** "VB_GT" для Viber bookings
- **Telegram notify:** httpx POST к Bot API (без aiogram в Viber-процессе)
- **Файлы:** viber_bot/ (13 файлов), тесты 146
- **Уроки добавлены в SKILL.md:** секция 17 "Production Implementation Patterns"
