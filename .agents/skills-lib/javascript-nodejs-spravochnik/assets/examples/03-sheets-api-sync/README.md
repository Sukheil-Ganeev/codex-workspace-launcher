# 03 - Google Sheets API Sync

Синхронизация данных между базой данных и Google Sheets в реальном времени.

## Кейсы использования

- Выгрузка бронирований в Sheets для отчётности
- Импорт прайс-листов из Sheets в приложение
- Синхронизация списков гидов и транспорта
- Совместное редактирование через Sheets интерфейс

## Установка

```bash
npm install
```

## Environment Variables

```bash
GOOGLE_SHEETS_ID=xxxxx
GOOGLE_SHEETS_KEY=xxxxx
SYNC_INTERVAL=300000
```

## Features

- ✅ Bidirectional sync (DB ↔ Sheets)
- ✅ Change detection
- ✅ Batch updates
- ✅ Error recovery
- ✅ Scheduled sync

## API Endpoints

- POST /sync/trigger - Запустить синхронизацию
- GET /sync/status - Статус синхронизации
- GET /sync/logs - Логи синхронизации
