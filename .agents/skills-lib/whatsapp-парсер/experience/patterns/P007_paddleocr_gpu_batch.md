# P007: PaddleOCR 3.4 GPU — батч-OCR ~100K изображений

> Дата: 2026-02-11 | Контекст: OCR всех WhatsApp-изображений через WSL2 + RTX 3060

---

## Задача

Распознать текст на ~96K изображениях из WhatsApp чатов (jpg/png, 50KB-10MB) для категоризации (чеки, паспорта, бронирования).

## Стек

- **OCR:** PaddleOCR 3.4 + PaddlePaddle GPU 3.0.0
- **GPU:** NVIDIA RTX 3060 12GB через WSL2
- **CUDA:** 13.1 (пакет cu126)
- **Python:** 3.12 (WSL Ubuntu)
- **Модели:** PP-OCRv5_server_det + eslav_PP-OCRv5_mobile_rec (русский+английский)

## Установка PaddlePaddle GPU

PaddlePaddle GPU 3.x **НЕ на PyPI** — только на собственном репозитории:

```bash
# Для CUDA 12.6+
python3 -m pip install paddlepaddle-gpu==3.0.0 \
  -i https://www.paddlepaddle.org.cn/packages/stable/cu126/ \
  --break-system-packages

# Для CUDA 11.8
python3 -m pip install paddlepaddle-gpu==3.0.0 \
  -i https://www.paddlepaddle.org.cn/packages/stable/cu118/

pip install paddleocr
```

## API PaddleOCR 3.4 (КРИТИЧНО)

### Инициализация

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang="ru",
    device="gpu:0",
    ocr_version="PP-OCRv5",
    use_doc_orientation_classify=False,  # НЕ нужно для WhatsApp фото
    use_doc_unwarping=False,             # НЕ нужно для плоских фото
    use_textline_orientation=False,      # НЕ нужно для горизонтального текста
    text_det_limit_side_len=960,         # ДЕФОЛТ в 3.x = 64 (!), поднять
    text_det_limit_type="max",           # Ограничить длинную сторону
)
```

### Вызов OCR

```python
# ПРАВИЛЬНО (3.4):
for res in ocr.predict(input=str(file_path)):
    data = res.json.get("res", {})
    texts = data.get("rec_texts", [])     # List[str]
    scores = data.get("rec_scores", [])   # List[float]

# НЕПРАВИЛЬНО (устарело):
# ocr.ocr(path)           # DeprecationWarning
# ocr.ocr(path, cls=True) # TypeError — cls удалён
# res.rec_texts            # AttributeError — нет такого атрибута!
```

### Формат результата

```
res.json = {
    "res": {
        "input_path": "/path/to/image.jpg",
        "rec_texts": ["Текст 1", "Текст 2"],
        "rec_scores": [0.95, 0.87],
        "dt_polys": [...],
        "dt_scores": [...],
        ...
    }
}
```

**ВНИМАНИЕ:** Данные в `res.json["res"]`, НЕ в `res.rec_texts`!

## Переменные окружения

```python
import os
os.environ["DISABLE_MODEL_SOURCE_CHECK"] = "True"           # Убрать 30-сек проверку серверов
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True" # PaddleX fallback
os.environ["GLOG_minloglevel"] = "2"                         # Подавить C++ WARNING
os.environ["FLAGS_call_stack_level"] = "2"                    # Сократить стектрейсы
os.environ["DISABLE_AUTO_LOGGING_CONFIG"] = "1"               # Не перезаписывать логи
```

## Скорость

- Инициализация: ~4-15 сек (с отключёнными doc_orientation/unwarping: 4 сек)
- Обработка: **2.5-5.0 img/sec** на RTX 3060
- 96K файлов ≈ 7-10 часов

## Retry-логика

PaddleOCR имеет ~20% транзиентный баг — выдаёт 1-2 символа вместо полного текста. Решение:

```python
if len(text.strip()) < 4 and file_size > 100_000:
    for _ in range(2):  # retry до 2 раз
        # повторить OCR
        if len(new_text.strip()) >= 4:
            break
```

## .webp не поддерживается

PaddleOCR 3.4 принимает только: jpg, jpeg, png, bmp, pdf. Файлы .webp вызывают ошибку (но не исключение — просто пустой результат).

---

## Связанные записи

- [W005](../warnings/W005_rglob_wsl_ntfs.md) — rglob теряет 90% файлов на WSL
- [W004](../warnings/W004_transcription_no_checkpoint.md) — checkpoint обязателен
