# R123: mkdir/makedirs — exist_ok обязателен

**Статус:** done
**PR:** #14
**Семья:** mkdir-exist-ok

## Дефект

Вызовы `Path.mkdir()` / `os.makedirs()` без `exist_ok=True` — 4 точки в `tests/test_launcher.py`. При повторном прогоне тест падал на существующей папке.

## Исправление

`exist_ok=True` добавлен во все 4 точки. Новый AST-гейт `tests/test_no_unbounded_mkdir.py` запрещает вызовы mkdir/makedirs без `exist_ok` во всех tracked `.py` (`os.mkdir` и `.agents/` исключены).

## Гейт

`python3 -m unittest discover -s tests` — набор зелёный
