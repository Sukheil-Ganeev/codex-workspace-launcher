# Проблемы и решения

## Ошибка 1: Whisper не найден в PATH

**Проблема:**
```
'whisper' is not recognized as an internal or external command
```

**Решение:**
```bash
python -m whisper "file.opus" --language ru --model medium
```
Или использовать Python API напрямую.

---

## Ошибка 2: Кракозябры в выводе (Windows)

**Проблема:**
```
├Я├Б├а├м├а├Т вместо кириллицы
```

**Решение:**
```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

---

## Ошибка 3: Файлы с кириллицей не читаются

**Проблема:**
```
File not found: Иванов Иван.vcf
```

**Решение:**
```python
import glob
vcf_files = glob.glob(os.path.join(directory, "*.vcf"))
for filepath in vcf_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
```

---

## Ошибка 4: CUDA out of memory

**Проблема:**
GPU не хватает памяти для модели.

**Решение:**
1. Использовать модель меньше (small вместо medium)
2. Или добавить `fp16=True`
3. Или использовать CPU: `device="cpu"`

---

## Ошибка 5: Перевод по СБП временно недоступен

Это ошибка банка, не связана со скриптом. Попробовать:
- Другой банк получателя
- Перевод по реквизитам вместо СБП

---

## Сводная таблица

| Проблема | Причина | Решение |
|----------|---------|---------|
| whisper не найден | Не в PATH | `python -m whisper` |
| Кракозябры | Кодировка Windows | `sys.stdout.reconfigure(encoding='utf-8')` |
| Файлы не читаются | Unicode в путях | `glob.glob()` + Python `open()` |
| Медленно | CPU вместо GPU | `device="cuda"` |
