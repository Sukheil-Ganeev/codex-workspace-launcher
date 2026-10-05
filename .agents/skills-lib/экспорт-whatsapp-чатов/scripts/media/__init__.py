"""
Модуль работы с медиафайлами WhatsApp.

Скрипты:
- organize_media: Организация медиафайлов
- voice_transcriber: Транскрибация голосовых
- transcribe_whisper: Транскрибация через Whisper
- whisper_postprocess: Постобработка Whisper
- document_ocr: OCR документов
- image_analyzer: Анализ изображений
"""

from pathlib import Path
import sys

# Добавляем корень scripts в путь для импорта config
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
