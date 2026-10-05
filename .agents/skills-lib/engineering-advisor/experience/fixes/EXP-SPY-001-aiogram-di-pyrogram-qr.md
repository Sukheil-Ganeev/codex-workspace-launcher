# EXP-SPY-001: aiogram 3.25 DI + Pyrogram QR Auth + Race Conditions

**Дата:** 2026-02-19
**Проект:** MLCR Spy Bot (ContentFactory)

## Проблема 1: aiogram 3.25 bot["db"] устарел
- `bot["db"]` больше не работает в aiogram 3.25
- **Решение:** Proper dependency injection через middleware

## Проблема 2: TgCrypto не компилируется на MS Store Python
- pip install tgcrypto падает без C compiler
- **Решение:** Батник с vcvarsall.bat из Visual Studio Build Tools

## Проблема 3: Pyrogram SMS flood protection
- send_code() возвращает flood wait при частых попытках
- **Решение:** QR-код авторизация как fallback

## Проблема 4: Race condition при инициализации
- asyncio.gather запускал компоненты до готовности БД
- **Решение:** await db.init() ПЕРЕД asyncio.gather()

## Паттерн
- Всегда инициализировать shared resources до параллельного запуска
- Для userbot авторизации: сначала SMS, если flood → QR
- aiogram DI > прямой доступ через bot[]
