# F001: UnicodeEncodeError на Windows

**Severity:** MEDIUM
**Дата:** 2026-02-05
**Источник:** Чат 12321212.txt

---

## Проблема

На Windows консоль использует cp1251 по умолчанию, русский текст вызывает:

```
UnicodeEncodeError: 'charmap' codec can't encode characters
```

## Решение

В начале скрипта добавить:

```python
import sys
import io

# Вариант 1: TextIOWrapper
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Вариант 2: reconfigure (Python 3.7+)
sys.stdout.reconfigure(encoding='utf-8')
```

## Для файлов

Всегда явно указывать кодировку:

```python
# ХОРОШО
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# ПЛОХО (зависит от системы)
with open(file_path, 'r') as f:
    content = f.read()
```

## Альтернатива

Если нужна совместимость с консолью Windows — использовать транслитерацию:

```python
# Вместо эмодзи и кириллицы в логах
print("[OK] Test uspeshen!")  # вместо "✅ Тест успешен!"
```

---

**Теги:** #windows #кодировка #utf8 #unicode
