# W004: Транскрипция без checkpoint = потеря данных

**Severity:** CRITICAL
**Дата:** 2026-02-09
**Контекст:** Батч 1+3 парсинга, 1221 голосовых файлов

---

## Что произошло

Агенты написали скрипт транскрипции (`transcribe_both_cpu.py`) который:
1. Копил ВСЕ результаты в список `results = []` в памяти
2. Записывал файл `transcriptions.jsonl` ТОЛЬКО В КОНЦЕ — `with open(trans_file, "w")`
3. Никакого checkpoint/resume

Пользователь запустил транскрипцию, она работала **7 часов** на CPU (small модель).
Потом выключил компьютер → **ВСЕ результаты потеряны**, 0 файлов сохранено.

## Корневая причина

Агенты проигнорировали собственный урок W001 ("JSONL для массового парсинга — атомарная запись").
Урок был про парсинг сообщений, но та же логика на 100% применима к транскрипции.

Ещё хуже: в SKILL.md явно указано "Checkpoint/resume при прерывании" для транскрипции,
но агенты не реализовали это.

## Правильный подход

```python
# ПРАВИЛЬНО: инкрементальная запись + checkpoint
checkpoint_file = out_dir / "transcription_checkpoint.json"
trans_file = out_dir / "media/transcriptions.jsonl"

# Загрузить checkpoint (уже обработанные файлы)
done_files = set()
if checkpoint_file.exists():
    checkpoint = json.loads(checkpoint_file.read_text())
    done_files = set(checkpoint.get("done_files", []))

# Открыть в режиме APPEND
with open(trans_file, "a", encoding="utf-8") as fout:
    for f in opus_files:
        if f.name in done_files:
            continue  # Пропустить уже обработанные

        result = transcribe(f)

        # Записать СРАЗУ
        fout.write(json.dumps(result, ensure_ascii=False) + "\n")
        fout.flush()  # Принудительно на диск

        # Обновить checkpoint
        done_files.add(f.name)
        checkpoint_file.write_text(json.dumps({
            "done_files": list(done_files),
            "last_updated": datetime.now().isoformat(),
            "total": len(opus_files),
            "completed": len(done_files),
        }, ensure_ascii=False))
```

## Правило

**НИКОГДА не копить результаты долгой операции в памяти.**

Для ЛЮБОЙ задачи длительностью > 5 минут:
1. Открывать выходной файл в режиме `"a"` (append)
2. Записывать каждый результат СРАЗУ + `flush()`
3. Вести checkpoint файл для resume
4. При старте проверять checkpoint и пропускать обработанное

Это касается: транскрипции, OCR, PDF-анализа, любой батч-обработки.

## Дополнительно

- Использовать GPU (RTX 3060, 6GB VRAM) вместо CPU — в 6x быстрее
- Модель large-v3 на GPU лучше small на CPU по качеству и скорости
- 1221 файлов на GPU large-v3 ≈ 1-2 часа вместо 7+ на CPU small

## Теги

#транскрипция #checkpoint #потеря-данных #faster-whisper #критическая-ошибка
