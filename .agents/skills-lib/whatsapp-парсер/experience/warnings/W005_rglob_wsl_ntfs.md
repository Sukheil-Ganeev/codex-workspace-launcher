# W005: Python rglob теряет 90% файлов на WSL/NTFS

> Дата: 2026-02-11 | Severity: CRITICAL

---

## Проблема

`pathlib.Path.rglob()` на WSL2 при доступе к NTFS-диску (`/mnt/d/`) **молча пропускает целые поддеревья** при ошибках кодировки (эмодзи, спецсимволы в именах папок).

## Масштаб потерь

| Метод | Найдено файлов |
|-------|---------------|
| Linux `find` | **96,259** |
| Python `rglob` | **7,967** |
| **Потеряно** | **88,292 (92%)** |

## Причина

WhatsApp папки часто содержат эмодзи в именах:
```
Car rental b2b group__⭐️_120363172479925034/
ARABIAN DREAM🤝MLCR_120363400621995910/
```

При обходе через DrvFs (WSL→NTFS), `pathlib.rglob()` получает `OSError: [Errno 5] Input/output error`. Даже с `try/except OSError`, генератор **прекращает обход ВСЕГО поддерева**, а не одного файла. Пойманные ошибки — лишь верхушка айсберга.

## Решение

Использовать `subprocess.run(["find", ...])` вместо `rglob`:

```python
import subprocess

cmd = [
    "find", str(source_dir),
    "(", "-name", "*.jpg", "-o", "-name", "*.png", ")",
    "-size", "+50k", "-size", "-10240k",
]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
paths = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
```

## Почему find работает

`find` — нативная Linux утилита, работает напрямую с VFS ядра. Не использует Python pathlib и его генератор-обход. Обрабатывает ошибки кодировки gracefully — пропускает проблемный файл, а не дерево.

## Правило

**На WSL/NTFS для массового сбора файлов (>1000) ВСЕГДА использовать `find` через subprocess, НЕ rglob.**

Исключение: маленькие директории (<100 файлов) без спецсимволов — rglob безопасен.

---

## Теги

#wsl #ntfs #rglob #find #критический-баг #массовый-сбор
