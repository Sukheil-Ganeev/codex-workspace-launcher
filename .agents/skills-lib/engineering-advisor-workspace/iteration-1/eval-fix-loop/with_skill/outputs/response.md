# Engineering Advisor — Анализ повторной ошибки

> Engineering Advisor активирован. Загружено 5 критических уроков из опыта. Буду проверять ситуацию с учётом накопленных ошибок.

---

## Сработавшие триггеры

```
=== Engineering Advisor ===
BLOCK (1): handlers.py — Trigger #18: Dataclass attribute mismatch (MANDATORY)
WARN  (1): Trigger #8 — петля ошибок: одна и та же ошибка 3 раза
WARN  (1): Trigger #2 — 3+ фикса одного файла handlers.py
INFO  (1): Trigger #41 — вероятно MagicMock без spec= скрывает баг в тестах
Опыт: применено 3 урока (EXP-040, EXP-041, EXP-065)
===========================
```

---

## BLOCK: Mismatched attribute name (Trigger #18 — MANDATORY)

**Почему ошибка возвращается снова и снова — конкретный ответ:**

`AttributeError: 'PipelineResult' object has no attribute 'text'`

Это означает одно: атрибут в объекте `PipelineResult` называется **не** `text`. Каждый раз, когда ты "исправляешь" это, ты меняешь что-то рядом — но не сам источник проблемы.

**Что нужно сделать прямо сейчас:**

Найди определение `PipelineResult` в коде:

```bash
grep -rn "PipelineResult" --include="*.py" .
grep -rn "class PipelineResult" --include="*.py" .
```

Открой файл и посмотри на `@dataclass` или `NamedTuple` определение. Там будет список полей. Поле называется не `text` — возможно `transcription`, `result`, `output`, `content` или что-то другое.

**Из опыта (EXP-040) — этот точно такой же баг:**

> VoiceTranscriptionBot v4.5.0 — `result.text` использовался в 6 местах, но в `PipelineResult` поле называется `result.transcription`.

Проверь, что у тебя: скорее всего поле называется `transcription`, а не `text`.

---

## WARN: Почему ошибка возвращается (петля фиксов)

Ты фиксируешь `handlers.py`, но проблема не в handlers.py. Ты меняешь код вокруг ошибки, а не саму причину. Это называется "петля фиксов" — симптом лечится, причина остаётся.

**Корневая причина петли:** тесты не ловят этот баг, потому что используют `MagicMock()` без `spec=`. MagicMock возвращает новый MagicMock на ЛЮБОЙ атрибут — включая несуществующие. Поэтому `result.text` в тестах работает (возвращает Mock), а в production падает (атрибута нет).

---

## Что делать — пошагово

**Шаг 1.** Найди определение `PipelineResult`:
```bash
grep -rn "class PipelineResult\|PipelineResult" --include="*.py" .
```

**Шаг 2.** Посмотри на поля в `@dataclass` или `NamedTuple`. Запомни точное имя поля вместо `text`.

**Шаг 3.** Замени `result.text` на правильное имя поля **везде** в проекте:
```bash
grep -rn "result\.text\|\.text" --include="*.py" .
```

**Шаг 4.** Найди тест для этого кода и исправь MagicMock:
```python
# Было (плохо — скрывает баги):
mock_result = MagicMock()

# Стало (правильно — поймает AttributeError):
mock_result = MagicMock(spec=PipelineResult)
```

После этого тесты начнут падать если имя атрибута неправильное — и ты узнаешь об ошибке до production.

---

## Системный дебаг (superpowers:systematic-debugging)

Для полного решения этой петли — делегировать субагенту с задачей:

1. Найти определение `PipelineResult` (все поля)
2. Найти все обращения к `result.text` / `result.transcription` / `result.*` в проекте
3. Исправить имена полей везде
4. Исправить все MagicMock без spec= в тестах
5. Запустить тесты — убедиться что зелёные

---

## Новый урок для записи в опыт

По завершении этой задачи рекомендую записать в experience:

> "Повторная AttributeError на PipelineResult.text — причина: тесты с MagicMock без spec= скрывают баг. Каждый фикс менял код вокруг, а не атрибут."

Хотите записать это в опыт скилла?

---

```
=== Engineering Advisor Summary ===
Файлы изменены: 0 (диагностика, не код)
Триггеры сработали: #18 (dataclass mismatch), #8 (петля ошибок), #2 (3+ фикса файла)
BLOCK: 1 — result.text != реальное имя поля в PipelineResult
WARN: 2 — петля фиксов + MagicMock без spec
INFO: 1 — нужен grep по проекту на все обращения к атрибуту
Опыт применён: EXP-040 (прямое совпадение), EXP-041 (MagicMock без spec), EXP-065 (silent failure)
Новый опыт: предложен к записи
===================================
```
