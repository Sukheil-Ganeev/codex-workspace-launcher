# Cheatsheet: Qwen Relay

## Шаблон вопроса (вставляй свою тему в CAPS)
```text
# QWEN: SHORT-TOPIC (verbatim!)
CONTEXT (5-10 строк фактов: что есть, что проверено, цифры).
TASK: <одно конкретное задание>. Numbered, direct, no fluff.
```

## Разбивка большой темы (урок 524)
- Один вызов = один tight-вопрос, max_tokens ≤ 4000.
- Большую тему дели на части 1/2, 2/2… с явным «part X/Y» в заголовке.
- Каждую часть — отдельным вызовом, ответы склеивай сам.

## Дотягивание оборванного ответа
```text
Continue EXACTLY where you stopped, no repeat, no intro. Last words:
...<последние ~500 символов>
```
Если продолжение уплыло в сторону — выбрось его и переспроси недостающее
новым сфокусированным вопросом (1 тема, max_tokens ≤ 1500).

## Проверка баланса (бесплатно, read-only)
```python
# GET https://api.infron.ai/v1/balance, заголовки: Authorization Bearer + UA
```

## Крошечный probe (проверка живости)
Вопрос `reply with single word: ok`, max_tokens 5–10. Должен вернуть `ok`.

## Мультираунд (план из 3)
1. Валидация: «validate this list, what did we miss?»
2. Решения: «for EACH gap: solution/estimate/depends/done».
3. Приоритеты: «order into phases, top-5 risks, what NOT to do, owner decisions».
Каждый раунд — отдельным вызовом; длинные ответы — по частям.

## Куда сохранять
- Сырой JSON + текст ответа — persistent-путь (проект или $HOME), НЕ /tmp.
- В отчёт: chars, finish_reason, что делал с хвостами.
