---
id: EXP-042
date: 2026-02-21
type: fix
severity: high
tags: [testing, integration, coverage, process_video_for_transcription]
project: VoiceTranscriptionBot v4.5.0
---

## Проблема

Функция `process_video_for_transcription()` вызывалась из 2 мест в `bot/handlers.py`, но НЕ ИМЕЛА НИ ОДНОГО ТЕСТА. При этом:
- `process_voice()` — покрыта тестами (11 тестов в test_pipeline.py)
- `process_image()` — покрыта тестами
- `process_video_for_transcription()` — 0 тестов

Баг с `result.text` жил в коде неделю и был обнаружен только при реальном использовании.

## Контекст

Новая функция была добавлена, но тесты для неё — нет. Unit-тесты в test_callbacks.py мокали `process_video_for_transcription` целиком, поэтому никогда не проверяли что она реально возвращает.

## Решение

1. Для КАЖДОЙ новой функции в pipeline — обязательный тест
2. Интеграционные тесты должны проверять реальные типы возвращаемых объектов
3. Code coverage на CI: `--fail-under=90`

## Урок

**Нет теста = нет гарантии.** Если функция вызывается из хендлера, она ДОЛЖНА иметь свой тест. Мокание вызывающего кода не заменяет тест самой функции.

## Правило предотвращения

Перед мержем: `grep` все функции в handlers.py → проверить что каждая вызываемая функция имеет тест.
