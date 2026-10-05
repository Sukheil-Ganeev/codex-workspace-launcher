# R103: urlopen() с явным timeout — 5 точек в tests

## Цель

`urllib.request.urlopen()` без `timeout` ждёт завершения запроса бесконечно:
зависший сервер вешает весь тестовый набор без диагностики.

## Сделано

- `tests/test_launcher.py`: 5 вызовов `urlopen(...)` → `timeout=10`
  (локальный сервер picker, 10 с с запасом).
- Пин `tests/test_urlopen_timeout.py`: AST-скан всех tracked .py —
  `urlopen(`/`urlretrieve(` без `timeout=` = красный тест.

## Проверка

`python3 -m unittest tests.test_urlopen_timeout tests.test_launcher` — зелёный.
