# R001 — unittest discover больше не даёт ложный зелёный

## Зазор

`python3 -m unittest discover -s tests` выдаёт `Ran 0 tests — OK`:
набор в `tests/test_launcher.py` — самодельный раннер (`main()` зовёт
`test_*` функции с tmp-фикстурой), unittest не видит ни одного кейса.
Стандартная точка входа выдаёт ложный PASS на пустом наборе — ловушка
для любого агента/CI, кто гоняет discover вместо
документированного `python tests/test_launcher.py`.

## CHECK / EXPECT

- CHECK: `python3 -m unittest discover -s tests` прогоняет реальный набор
  и падает, если упал внутренний чек.
- CHECK: `python tests/test_launcher.py` (штатный вход, зеркалит CI) —
  поведение не изменилось, `==== 47 passed ====` как было.
- EXPECT: discover → `Ran 1 test` + OK; при сломанном продуктовом коде
  discover → FAIL (не тихий 0).

## План минимальной правки

`load_tests(loader, tests, pattern)` в конце test_launcher.py: оборачивает
`main()` в один `unittest.FunctionTestCase`, rc≠0 → AssertionError со
списком FAILURES. Чисто аддитивно, импортируется unittest.

## EVIDENCE

```
$ python3 -m unittest discover -s tests
Ran 1 test in 1.721s — OK   # внутри прогнан весь набор (47 checks)
$ python3 tests/test_launcher.py
==== 47 passed, 0 failed ====
```

До правки: `Ran 0 tests in 0.000s — OK` (ложный зелёный).
