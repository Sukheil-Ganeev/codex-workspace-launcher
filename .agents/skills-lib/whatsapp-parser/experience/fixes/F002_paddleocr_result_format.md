# F002: PaddleOCR 3.4 — данные в res.json["res"], НЕ в res.rec_texts

> Дата: 2026-02-11 | Severity: HIGH

---

## Ошибка

Скрипт проверял `hasattr(res, "rec_texts")` — возвращало `False`. Все 4,551 файлов получили пустой текст (`text: ""`, `confidence: 0.0`).

## Причина

Документация PaddleOCR описывает `res.rec_texts` как прямой атрибут, но реально `OCRResult` хранит данные во вложенном словаре:

```python
# НЕ работает:
res.rec_texts        # AttributeError / не существует
hasattr(res, "rec_texts")  # False

# Работает:
data = res.json.get("res", {})
texts = data.get("rec_texts", [])
scores = data.get("rec_scores", [])
```

## Тип объекта

```
type(res) = paddlex.inference.pipelines.ocr.result.OCRResult
res.json = {"res": {"input_path": ..., "rec_texts": [...], "rec_scores": [...], ...}}
```

## Диагностика

Создали debug-скрипт, который вывел все атрибуты `OCRResult.__dict__` — там только `_save_funcs`, `_json_writer`, `_img_writer`. Полезные данные — в `.json` property.

## Урок

При использовании новых API **всегда** сначала debug-скрипт с выводом `type()`, `dir()`, `.__dict__`, `.json` — НЕ полагаться на документацию.

---

## Теги

#paddleocr #api-ломающее-изменение #debug
