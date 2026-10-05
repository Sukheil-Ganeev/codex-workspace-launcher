# Troubleshooting -- PuzzleBot Project

## 1. Whisper не находит CUDA

**Симптомы:** `RuntimeError: CUDA is not available` или fallback на CPU с предупреждением.

**Причины:**
- Не установлен CUDA Toolkit
- Версия PyTorch не совпадает с версией CUDA
- Нет NVIDIA GPU

**Решение:**
```bash
# Проверить CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Установить правильную версию PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Если CUDA недоступна -- переключить на CPU
# В config.py: "whisper_device": "cpu"
```

Скрипт автоматически делает fallback на CPU, но скорость упадёт в ~10 раз.

## 2. SSIM: слишком много кадров

**Симптомы:** На 5-минутном видео извлекается 50+ кадров вместо ожидаемых 10-15.

**Причины:**
- Слишком низкий `ssim_threshold` (много изменений считаются "значимыми")
- Короткий `min_interval` (не фильтруются анимации)
- Видео с частыми переключениями

**Решение:**
```python
# В config.py:
"ssim_threshold": 0.92,    # Повысить (было 0.88)
"min_interval": 3.0,       # Увеличить (было 1.5)
"dedup_threshold": 0.93,   # Агрессивнее дедупликация
```

## 3. SSIM: слишком мало кадров

**Симптомы:** На 5-минутном видео извлекается 2-3 кадра.

**Причины:**
- Слишком высокий `ssim_threshold`
- Видео со статичным экраном (текст набирается медленно)

**Решение:**
```python
# В config.py:
"ssim_threshold": 0.85,    # Понизить (было 0.88)
"max_interval": 10,        # Чаще принудительные кадры (было 20)
```

## 4. Telegram FloodWait

**Симптомы:** Экспорт зависает на 30+ секунд с сообщением `Sleeping for X seconds`.

**Причины:** Telegram rate limiting при массовых запросах.

**Решение:**
- Это нормальное поведение. Telethon автоматически обрабатывает FloodWaitError
- Не прерывайте скрипт -- он продолжит после ожидания
- Для ускорения: экспортируйте по одному топику отдельно

## 5. reply_to == topic_id (ложные цепочки)

**Симптомы:** Одна гигантская цепочка содержит тысячи сообщений. Метрики thread_builder нереалистичны.

**Причины:** Корневые сообщения топика имеют `reply_to` = ID топика. Без фильтрации все они объединяются в одну цепочку.

**Решение:**
Проверка уже есть в `loader.py`:
```python
if raw_reply_to is not None and raw_reply_to in TOPIC_IDS:
    reply_to = None
```
Если проблема вернулась -- проверьте, что все ID топиков указаны в `TOPIC_MAP` (config.py). Новые топики в группе = новые ID для маппинга.

## 6. UTF-8 ошибки в JSON

**Симптомы:** `UnicodeDecodeError` при загрузке `messages.json`.

**Причины:** Telegram Desktop экспорт содержит невалидные символы (эмодзи, специальные Unicode).

**Решение:**
```python
with open(path, "r", encoding="utf-8", errors="replace") as f:
    data = json.load(f)
```
Или пересохраните файл в UTF-8 без BOM.

## 7. Pipeline падает на пустых сообщениях

**Симптомы:** `AttributeError: 'NoneType' object has no attribute 'lower'` или подобные ошибки при обработке текста.

**Причины:** Сообщения без текста (только медиа, стикеры, сервисные).

**Решение:**
`loader.py` уже фильтрует пустые сообщения (`text == ""` и нет медиа). Если ошибка всё же возникает, проверьте кастомные модификации loader. Запустите с `--verbose` для точной диагностики.

## 8. Кириллица в путях (Windows)

**Симптомы:** `cv2.VideoCapture()` возвращает пустой объект. `cv2.imread()` возвращает None.

**Причины:** OpenCV на Windows не поддерживает non-ASCII пути через стандартные функции.

**Решение:**
```python
# Вместо cv2.imread(path):
img_array = numpy.fromfile(path, dtype=numpy.uint8)
img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

# Вместо cv2.VideoCapture(path) -- переименовать файл в ASCII:
import shutil
temp_path = "temp_video.mp4"
shutil.copy(original_path, temp_path)
cap = cv2.VideoCapture(temp_path)
```

## 9. messages_cache.pkl устарел

**Симптомы:** `UnpicklingError`, `AttributeError` при загрузке, или данные не соответствуют новому JSON.

**Причины:**
- Структура Message dataclass изменилась (добавлены/удалены поля)
- JSON обновлён, но кеш старый

**Решение:**
```bash
# Игнорировать кеш
python run_pipeline.py --skip-cache

# Или удалить кеш вручную
rm output/messages_cache.pkl
```

Loader автоматически инвалидирует кеш, если mtime JSON файла новее кеша. Но при изменении dataclass нужен `--skip-cache`.

## 10. Видео без звука (нет транскрипции)

**Симптомы:** `faster_whisper` выбрасывает исключение при попытке транскрибировать видео без аудиодорожки.

**Причины:** Некоторые скринкасты записаны без микрофона.

**Решение:**
```bash
# Проверить наличие аудио
ffprobe -v quiet -select_streams a -show_entries stream=codec_name video.mp4
```
Если аудио нет -- pipeline пропускает этап транскрипции и генерирует статью только с кадрами и OCR. Это штатное поведение (обработано в `video_to_knowledge.py`).

## 11. ProtocolNotFoundError в WSL

**Симптомы:** `ProtocolNotFoundError` при открытии видеофайла через av.open().

**Причины:** Batch-скрипты передают Windows-пути (D:/Downloads/...) в av.open() в WSL2. Библиотека av не понимает буквы дисков Windows в Linux.

**Решение:**
Функции transcribe_video() и extract_frames() вызывают to_native_path() внутри себя. Но прямые файловые операции в batch-скриптах требуют ручной конвертации. Используйте repair_outputs.py для исправления.

## 12. AV1 codec -- ошибка извлечения кадров

**Симптомы:** cv2.VideoCapture не может декодировать AV1-кодированные .webm файлы.

**Причины:** cv2.VideoCapture не может декодировать AV1-кодированные .webm файлы в WSL2 без аппаратного ускорения.

**Ошибка:** `Your platform doesn't support hardware accelerated AV1 decoding`

**Решение:**
```bash
ffmpeg -i input.webm -c:v libx264 -c:a copy output.mkv
```

## 13. externally-managed-environment (pip install падает в WSL)

**Симптомы:** `error: externally-managed-environment` при попытке pip install.

**Причины:** Ubuntu 24.04 запрещает системные pip-установки (PEP 668).

**Решение:**
```bash
python3 -m venv venv && source venv/bin/activate && pip install ...
```

## 14. metadata.json отсутствует после batch-запуска

**Симптомы:** Папка видео не содержит metadata.json после завершения пакетной обработки.

**Причины:** Batch-скрипты пишут по Windows-пути (D:/...) в WSL, что создаёт относительную директорию вместо записи в /mnt/d/.

**Решение:**
```bash
python3 repair_outputs.py
```
Генерирует metadata.json через ffprobe в правильном расположении.

## 15. frames_transcript.json отсутствует после batch-запуска

**Симптомы:** Папка видео не содержит frames_transcript.json после завершения пакетной обработки.

**Причины:** Та же ошибка WSL-путей, что и с metadata.json.

**Решение:**
```bash
python3 repair_outputs.py
```
Коррелирует существующие кадры с транскрипцией, сохраняет по правильному пути.

## 16. Команда 'python' не найдена в WSL

**Симптомы:** `Command 'python' not found` при запуске скриптов.

**Причины:** WSL Ubuntu не имеет симлинка python, только python3.

**Решение:**
```bash
# Использовать python3
python3 script.py

# Или установить пакет-алиас
sudo apt install python-is-python3
```
