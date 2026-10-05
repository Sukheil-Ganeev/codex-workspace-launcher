---
name: bankovskie-rekvizity
description: Быстрая выдача банковских реквизитов для оплаты. Используй когда клиент или агент спрашивает реквизиты для оплаты, банковские данные, IBAN, номер карты, куда переводить деньги. Поддерживает ОАЭ (AED) и Россию (RUB). Форматы WhatsApp и Telegram.
---

# Банковские реквизиты

## Алгоритм

1. Определить валюту → AED или RUB
2. Определить мессенджер → WhatsApp или Telegram (если не указан — уточнить)
3. Выдать файл из `assets/`

## Реквизиты

### AED (ОАЭ)

| # | Банк | Получатель | Файл |
|---|------|------------|------|
| 1 | NBD | Gulnaz Undassinova | `01_NBD_Gulnaz_Undassinova.txt` |
| 2 | Mashreq | Gulnaz Undassinova | `02_Mashreq_Gulnaz_Undassinova.txt` |
| 3 | Mashreq | Garnik Bakhshian | `03_Mashreq_Garnik_Bakhshian.txt` |
| 4 | Mashreq | Madina Zhulanova | `04_Mashreq_Madina_Zhulanova.txt` |
| 5 | Mashreq | Sukheil Ganeev | `05_Mashreq_Sukheil_Ganeev.txt` |
| 8 | ADCB | Mohamed Abdelhamid | `08_ADCB_Mohamed_Abdelhamid.txt` |

### RUB (Россия)

| # | Банк | Получатель | Файл |
|---|------|------------|------|
| 6 | Тинькофф | Ландыш Ганеева | `06_Tinkoff_Landysh_Ganeeva.txt` |
| 7 | Сбер | Сухейль Ганеев | `07_Sber_Sukheil_Ganeev.txt` |

## Правила выбора

| Валюта | По умолчанию |
|--------|--------------|
| AED | `05_Mashreq_Sukheil_Ganeev.txt` |
| RUB | `07_Sber_Sukheil_Ganeev.txt` |

## Структура assets/

```
assets/
├── whatsapp/   ← формат *жирный* (одинарные звёздочки)
├── telegram/   ← формат **жирный** (двойные звёздочки)
└── plain/      ← без форматирования
```

## Выдача

1. Определить папку по мессенджеру
2. Выдать содержимое файла клиенту
3. НЕ использовать code block — просто текст

## Пример диалога

**Клиент:** Куда переводить в дирхамах?
**Ответ:** Прочитать `assets/whatsapp/05_Mashreq_Sukheil_Ganeev.txt` и выдать содержимое

**Клиент:** Реквизиты на Сбер
**Ответ:** Прочитать `assets/whatsapp/07_Sber_Sukheil_Ganeev.txt` и выдать содержимое
