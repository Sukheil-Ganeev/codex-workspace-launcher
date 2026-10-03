# R083 — неверная форма аргументов probe-кэша не должна запускаться

## Цель

При чтении закэшированного `ToolReport` принимать `launch_arguments` только как
последовательность строк. Повреждённый payload должен быть проигнорирован, а
инструмент — проверен заново по своему определению.

## Проблема

`ToolReport.from_dict` применяет `tuple()` к значению без проверки формы.
Строка превращается в кортеж отдельных символов и считается данными готового
кэша; `None` вызывает исключение и прерывает список инструментов.

## Сделано

Добавлена проверка типа аргументов; некорректный кэш отклоняется, а
`probe_tool` продолжает обычную проверку определения.

## Проверка

- RED до исправления: `launch_arguments: "--stale"` возвращал статус `ready`
  и превращался в `('-', '-', 's', 't', 'a', 'l', 'e')`.
- После исправления: `TOOLS: 14 passed, 0 failed`; общий офлайн-набор без HTTP
  picker — `OFFLINE GATES: 62 passed, 0 failed`.
- `python3 -m py_compile cwl/registry.py cwl/tools.py tests/test_launcher.py` —
  код 0; `git diff --check` — код 0.
- `python3 -m unittest discover -s tests` не может открыть HTTP picker из-за
  запрета localhost-сокета в sandbox (`PermissionError: [Errno 1] Operation not
  permitted`); этот тест остаётся непроверенным.
