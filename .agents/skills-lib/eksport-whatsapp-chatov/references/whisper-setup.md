# Настройка OpenAI Whisper

## Системные требования

| Компонент | Минимум | Рекомендуется |
|-----------|---------|---------------|
| Python | 3.8+ | 3.10+ |
| RAM | 4 GB | 16 GB |
| GPU VRAM | - | 6+ GB (NVIDIA) |
| CUDA | - | 11.x+ |

## Установка

```bash
# Создание виртуального окружения
python -m venv whisper_env
whisper_env\Scripts\activate  # Windows

# Установка библиотек
pip install openai-whisper
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# FFmpeg (для работы с opus)
# Скачать с https://ffmpeg.org/ и добавить в PATH
```

## Выбор модели

| Модель | Размер | VRAM | Качество | Рекомендация |
|--------|--------|------|----------|--------------|
| tiny | 39M | ~1GB | Низкое | Тесты |
| base | 74M | ~1GB | Среднее | Черновик |
| small | 244M | ~2GB | Хорошее | Бюджетный GPU |
| **medium** | 769M | ~5GB | **Высокое** | RTX 3060 |
| large-v3 | 1.5G | ~10GB | Лучшее | RTX 4090+ |

## Примеры команд

```bash
# CLI
python -m whisper "file.opus" --language ru --model medium

# Python API
import whisper
model = whisper.load_model("medium", device="cuda")
result = model.transcribe("file.opus", language="ru", fp16=True)
```

## Улучшения medium vs small

| Было (small) | Стало (medium) |
|--------------|----------------|
| "с эмальциками" | "снимаете комиссия" |
| "вытывайся" | "ВТБ" |
| "венефичили" | "бенефициар" |
| "плачешь в Дархамов" | "платёж дирхамов" |
