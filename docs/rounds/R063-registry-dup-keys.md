# R063 — registry.json с повторными ключами = corrupt-путь (dup-keys)

## Цель

`cwl/registry.py::_load` читает `registry.json` голым `json.loads`:
повторный ключ в одном объекте (напр. два `"workspaces"`) сворачивается
молча — теряется рабочее пространство без следа.

## Проблема

Существующий контракт: нечитаемый реестр → `.corrupt`-копия + warning +
свежие данные. Дубль ключа — семантически битый JSON — обязан идти тем же
путём, а не проскакивать как последняя копия значения.

## Сделано

- `cwl/registry.py`: `object_pairs_hook` в `_load`, отклоняющий повторные
  ключи через `json.JSONDecodeError`-совместимый `ValueError`; пойман
  существующей веткой corrupt-пути.

## Проверка

- `python3 -m unittest tests.test_launcher` — зелёный.
- Новый тест: registry с дублем ключа → данные сброшены, файл сохранён
  как `.corrupt`, warning в stderr.
