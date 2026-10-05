# Опыт: whatsapp-парсер

> Последнее обновление: 2026-02-12

---

## Критические уроки (топ-5)

1. **ЛЮБАЯ долгая операция — append + checkpoint + flush** — транскрипция 7 часов на CPU потеряна из-за записи только в конце. НИКОГДА не копить в памяти. → [W004](warnings/W004_transcription_no_checkpoint.md)

2. **Проверка дубликатов обязательна** — в исходных данных может быть 63% дублей. → [F001](fixes/F001_duplicates_check.md)

3. **JSONL для массового парсинга** — атомарная запись, данные не теряются при падении. → [W001](warnings/W001_json_vs_jsonl.md)

3. **Составной ключ** — (chat_folder, filename, source) для уникальной идентификации. → [P001](patterns/P001_unique_key.md)

4. **Async для API** — 8x прирост скорости при работе с внешними API. → [I001](improvements/I001_async_processing.md)

5. **Мониторинг прогресса** — проверка каждые 3-5 минут при массовой обработке. → [P002](patterns/P002_monitoring.md)

6. **Стандартный экспорт WhatsApp** — формат `[DD/MM/YYYY, HH:MM:SS] Sender: Message`. Вложения: `<прикреплено: filename>`. → [P003](patterns/P003_standard_export.md)

7. **Большие чаты (>6000 строк) ломают general-purpose агентов** — "Prompt is too long". Решение: Bash агент + Python скрипт. → [W003](warnings/W003_large_chats.md)

8. **faster-whisper для коротких аудио** — medium модель на CPU: 90 сек на 10 сек аудио. Ошибается в именах (Сухейль→Сухие). Нужен словарь исправлений. → [P004](patterns/P004_faster_whisper.md)

9. **VIP Transfer Blank парсинг** — regex для извлечения заказов: ORDER DATE, MEETING TIME, TRANSPORT MODEL, FULL NAME. 113 бланков из 3 чатов. → [P005](patterns/P005_vip_blanks.md)

10. **CRM из чатов** — FULL NAME + Contact Number = клиент. Дедупликация по имени, определение страны по +7 9xx/7xx. 55 клиентов из 11K сообщений. → [P006](patterns/P006_crm_extraction.md)

11. **PaddleOCR 3.4 GPU: данные в res.json["res"], НЕ в res.rec_texts** — документация врёт, 4,551 файлов получили пустой текст. Всегда debug-скрипт перед батчем. → [F002](fixes/F002_paddleocr_result_format.md)

12. **rglob на WSL/NTFS теряет 92% файлов** — `find` нашёл 96,259, `rglob` только 7,967. Эмодзи в папках убивают генератор. Всегда `subprocess find` для массового сбора. → [W005](warnings/W005_rglob_wsl_ntfs.md)

13. **PaddleOCR 3.4 GPU батч-OCR** — PP-OCRv5, WSL2 + RTX 3060, 2.5-5 img/s. .webp не поддерживается. Retry для 20% transient-бага. Env vars для подавления логов. → [P007](patterns/P007_paddleocr_gpu_batch.md)

14. **Потоковое чтение JSONL 401 MB** — НИКОГДА не грузить all_messages_enriched.jsonl целиком в память. Читать построчно json.loads(line), batch INSERT для SQLite (5000 за раз). → [P008](patterns/P008_streaming_jsonl.md)

15. **Параллельные агенты для аналитики** — 4 независимых задачи параллельно, зависимые — после завершения зависимостей. Каждый агент: свой скрипт + свои выходные файлы. → [P009](patterns/P009_parallel_agents.md)

16. **NetworkX для графа контактов** — 224K узлов, 235K рёбер. Betweenness centrality с k=500 (sampling). BFS кластеризация. JSON сериализация (не pickle!). → [P010](patterns/P010_networkx_scale.md)

17. **Не грузить contact_graph_full.json (151 MB) целиком** — json.load() ~500 MB RAM. Лучше: записывать statistics отдельным файлом при генерации. → [W006](warnings/W006_large_json_memory.md)

18. **SQLite FTS5 для полнотекстового поиска** — 773K записей, индексация ~2 мин, поиск <0.1 сек. WAL mode + batch INSERT по 5000 строк. → [I002](improvements/I002_sqlite_fts5.md)

---

## Статистика

- **Всего записей:** 20
- **Fixes:** 2
- **Improvements:** 2
- **Patterns:** 10
- **Warnings:** 6

---

## Fixes (исправленные ошибки)

| ID | Severity | Описание |
|----|----------|----------|
| [F001](fixes/F001_duplicates_check.md) | HIGH | Дубликаты в исходных данных (63%) |
| [F002](fixes/F002_paddleocr_result_format.md) | HIGH | PaddleOCR 3.4: данные в res.json["res"], НЕ в res.rec_texts |

---

## Improvements (улучшения)

| ID | Impact | Описание |
|----|--------|----------|
| [I001](improvements/I001_async_processing.md) | HIGH | Async для API — 5,000+/час |
| [I002](improvements/I002_sqlite_fts5.md) | HIGH | SQLite FTS5 — 773K записей, поиск <0.1 сек |

---

## Patterns (паттерны)

| ID | Описание |
|----|----------|
| [P001](patterns/P001_unique_key.md) | Составной ключ (chat, file, source) |
| [P002](patterns/P002_monitoring.md) | Мониторинг каждые 3-5 минут |
| [P003](patterns/P003_standard_export.md) | Стандартный ZIP-экспорт WhatsApp (`[DD/MM/YYYY, HH:MM:SS]`) |
| [P004](patterns/P004_faster_whisper.md) | faster-whisper для коротких аудио (medium, CPU) |
| [P005](patterns/P005_vip_blanks.md) | VIP Transfer Blank парсинг (113 заказов) |
| [P006](patterns/P006_crm_extraction.md) | CRM извлечение из чатов (55 клиентов) |
| [P007](patterns/P007_paddleocr_gpu_batch.md) | PaddleOCR 3.4 GPU батч-OCR (96K изображений, RTX 3060) |
| [P008](patterns/P008_streaming_jsonl.md) | Потоковое чтение JSONL 401 MB (batch INSERT 5000) |
| [P009](patterns/P009_parallel_agents.md) | Параллельные агенты для аналитики (A1-A4 + B1-B5) |
| [P010](patterns/P010_networkx_scale.md) | NetworkX граф 224K узлов (betweenness k=500, BFS) |

---

## Warnings (что НЕ делать)

| ID | Severity | Описание |
|----|----------|----------|
| [W001](warnings/W001_json_vs_jsonl.md) | HIGH | JSON теряет данные при падении |
| [W002](warnings/W002_subagents_limit.md) | CRITICAL | Не запускать 50+ субагентов |
| [W003](warnings/W003_large_chats.md) | CRITICAL | Чаты >6000 строк ломают general-purpose агентов |
| [W004](warnings/W004_transcription_no_checkpoint.md) | CRITICAL | Транскрипция без checkpoint — 7 часов потеряно |
| [W005](warnings/W005_rglob_wsl_ntfs.md) | CRITICAL | Python rglob теряет 92% файлов на WSL/NTFS |
| [W006](warnings/W006_large_json_memory.md) | HIGH | Не грузить contact_graph_full.json (151 MB) целиком |

---

## Теги

#парсинг #дубликаты #jsonl #async #мониторинг #массовая-обработка #sqlite #fts5 #networkx #графы #потоковая-обработка #параллельность

---

## Источники

Опыт извлечён из проекта "Туризм-ОАЭ":
- 2,422 чата (Personal + Business, после дедупликации)
- 880,257 сообщений
- 50,430 транскрипций голосовых
- 59,536 OCR-обработок
- 3,220 контактов

Ключевое открытие: 63% записей были дубликатами
