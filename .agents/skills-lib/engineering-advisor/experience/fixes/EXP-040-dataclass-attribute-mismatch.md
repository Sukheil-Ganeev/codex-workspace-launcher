---
id: EXP-040
date: 2026-02-21
type: fix
severity: critical
tags: [dataclass, AttributeError, PipelineResult, runtime]
project: VoiceTranscriptionBot v4.5.0
---

## Проблема

В `bot/handlers.py` (функция `_handle_vid_action`) использовались несуществующие атрибуты `PipelineResult`:
- `result.text` → правильно: `result.corrected_text or result.transcription`
- `result.summary` → правильно: `result.summary_result.summary if result.summary_result else ""`

Ошибка повторялась в 6 местах (строки 4161, 4164, 4165, 4178, 4449, 4452).

## Контекст

При добавлении видео-транскрипции код был написан по аналогии с другим типом результата (не PipelineResult). Разработчик привык к `.text` и `.summary`, а у PipelineResult поля называются `.transcription` и `.summary_result.summary`.

## Решение

1. Заменить `result.text` → `result.corrected_text or result.transcription`
2. Заменить `result.summary` → `result.summary_result.summary if result.summary_result else ""`
3. Добавить правило: при работе с dataclass — ВСЕГДА сверять имена полей с определением класса

## Урок

**Никогда не угадывай имена полей dataclass.** Перед использованием результата — открыть определение класса и скопировать точные имена. Особенно опасно когда похожие классы имеют разные имена полей (TranscriptionResult.text vs PipelineResult.transcription).

## Правило предотвращения

```
Перед использованием result.X:
1. Найти определение класса (@dataclass)
2. Список ВСЕХ полей
3. Сверить каждое обращение result.X с реальным полем
4. Для вложенных объектов (result.X.Y) — добавить None-проверку
```
