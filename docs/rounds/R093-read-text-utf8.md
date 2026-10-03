# R093: read_text() с явным UTF-8 — 1 чтение в tests

## Цель

`read_text()` без `encoding=` читает файл под locale машины (на Windows — cp1251).

## Сделано

- `tests/test_launcher.py`: чтение argout-файла → `encoding='utf-8'`.
- Пин `tests/test_read_text_utf8.py`: `read_text(` без `encoding=` = красный тест.

## Проверка

`python3 -m unittest tests.test_read_text_utf8` — зелёный.
