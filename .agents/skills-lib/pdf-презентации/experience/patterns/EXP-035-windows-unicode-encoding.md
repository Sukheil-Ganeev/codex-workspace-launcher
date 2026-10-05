---
id: EXP-035
date: 2026-02-05
type: pattern
severity: medium
category: compatibility
projects: []
related: []
tags: [windows, unicode, encoding, python, utf-8]
status: verified
---

# Windows Unicode Encoding в Python скриптах

## Проблема

Python скрипт с эмодзи в `print()` падает на Windows:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f54c' in position 26
```

## Причина

Windows консоль по умолчанию использует кодировку cp1251 (или cp1252), которая не поддерживает Unicode эмодзи и многие специальные символы.

## Решение 1: Reconfig stdout/stderr (рекомендуется)

```python
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Теперь можно использовать эмодзи
print("🕌 Конвертация завершена!")
print("✅ PDF создан")
```

## Решение 2: ASCII-замены (альтернатива)

Если нужна совместимость со старыми терминалами:

```python
# Вместо эмодзи используем ASCII-маркеры
ICONS = {
    'file': '[FILE]',
    'ok': '[OK]',
    'error': '[ERR]',
    'info': '[INFO]',
    'mosque': '[MOSQUE]',
}

print(f"{ICONS['ok']} Конвертация завершена!")
print(f"{ICONS['file']} PDF создан: output.pdf")
```

## Решение 3: Environment variable

```bash
# В Git Bash или PowerShell
export PYTHONIOENCODING=utf-8
python convert_to_pdf.py
```

## Полный шаблон скрипта

```python
#!/usr/bin/env python3
"""
HTML to PDF converter with Windows compatibility.
"""
import sys
import os

# Windows Unicode fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def main():
    print("=" * 50)
    print("[MOSQUE] Islamic AI Assistants - HTML to PDF Converter")
    print("=" * 50)

    # ... код конвертации ...

    print("[OK] Конвертация завершена!")

if __name__ == '__main__':
    main()
```

## Когда применять

- Любые Python скрипты с выводом в консоль на Windows
- Скрипты конвертации HTML → PDF
- Скрипты с эмодзи, кириллицей, арабскими символами

## Реальный пример

Скрипт `D:/Downloads/Islamic_AI_Presentation_Project/scripts/convert_to_pdf.py` использует ASCII-маркеры `[MOSQUE]`, `[OK]` для совместимости с Windows Git Bash.

## Ссылки

- [Python docs: sys.stdout.reconfigure](https://docs.python.org/3/library/io.html#io.TextIOWrapper.reconfigure)
- [PEP 597 – Add optional EncodingWarning](https://peps.python.org/pep-0597/)
