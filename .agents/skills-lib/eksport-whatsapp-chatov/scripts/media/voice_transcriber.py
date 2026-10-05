#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Транскрибация голосовых сообщений WhatsApp через OpenAI Whisper API.

Обрабатывает ~179k медиафайлов из двух экспортов:
- D:/Downloads/экспорт чатов с ватсапа/
- D:/Downloads/экспорт чатов с ватсап бизнеса/

Результаты:
- voice_transcripts.json: jid -> [{file, text, language, duration}]
- Обновление all_messages.jsonl с транскриптами
- Статистика обработки
"""

import os
import sys
import json
import time
import argparse
import subprocess
import tempfile
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import threading

# Исправление кодировки для Windows
sys.stdout.reconfigure(encoding='utf-8')

# OpenAI API
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("[!] openai не установлен. Установите: pip install openai")

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

# API ключ (из переменной окружения или напрямую)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Модель Whisper API
WHISPER_MODEL = "whisper-1"

# Максимальный размер файла в MB (ограничение OpenAI = 25 MB)
MAX_FILE_SIZE_MB = 25

# Форматы аудио
AUDIO_EXTENSIONS = {".opus", ".ogg", ".m4a", ".mp3", ".wav", ".flac", ".aac", ".wma", ".webm"}

# Форматы, требующие конвертации в MP3 для API
NEEDS_CONVERSION = {".opus", ".ogg", ".webm", ".wma", ".flac", ".aac"}

# Пути
from config import (
    EXPORT_DIRS,
    RAW_DIR,
    JSON_DIR,
    ensure_directories,
)

# Выходные файлы
TRANSCRIPTS_FILE = JSON_DIR / "voice_transcripts.json"
PROGRESS_FILE = JSON_DIR / "voice_transcripts_progress.json"
MESSAGES_FILE = RAW_DIR / "all_messages.jsonl"
UPDATED_MESSAGES_FILE = RAW_DIR / "all_messages_with_voice.jsonl"

# Rate limiting
REQUESTS_PER_MINUTE = 50  # OpenAI Whisper API limit
REQUEST_INTERVAL = 60.0 / REQUESTS_PER_MINUTE

# Retry настройки
MAX_RETRIES = 3
RETRY_DELAY = 5  # секунд

# Параллельная обработка
MAX_WORKERS = 4  # Количество потоков

# Lock для thread-safe операций
api_lock = threading.Lock()
last_request_time = 0


# ═══════════════════════════════════════════════════════════════
# УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════

def get_file_hash(filepath: Path) -> str:
    """Получить MD5 хэш файла для дедупликации."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_file_size_mb(filepath: Path) -> float:
    """Получить размер файла в MB."""
    return filepath.stat().st_size / (1024 * 1024)


def is_audio_file(filepath: Path) -> bool:
    """Проверить, является ли файл аудио."""
    return filepath.suffix.lower() in AUDIO_EXTENSIONS


def is_voice_message(filepath: Path) -> bool:
    """
    Определить, является ли файл голосовым сообщением.
    WhatsApp голосовые обычно называются PTT-* или AUD-* или имеют .opus расширение.
    """
    name_lower = filepath.name.lower()

    # Типичные паттерны голосовых сообщений WhatsApp
    voice_patterns = [
        "ptt-",      # Push-to-talk
        "ptt_",
        "aud-",      # Audio
        "aud_",
        "voice",
        "audio",
        "записи",
    ]

    # .opus файлы почти всегда голосовые
    if filepath.suffix.lower() == ".opus":
        return True

    # Проверка по имени
    for pattern in voice_patterns:
        if pattern in name_lower:
            return True

    return False


def find_ffmpeg() -> Optional[str]:
    """Найти путь к ffmpeg."""
    # Проверяем в PATH
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return "ffmpeg"
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # Типичные пути на Windows
    common_paths = [
        "C:/ffmpeg/bin/ffmpeg.exe",
        "C:/Program Files/ffmpeg/bin/ffmpeg.exe",
        "D:/ffmpeg/bin/ffmpeg.exe",
    ]

    for path in common_paths:
        if Path(path).exists():
            return path

    return None


def convert_to_mp3(input_path: Path, ffmpeg_path: str) -> Optional[Path]:
    """
    Конвертировать аудио в MP3 для совместимости с API.
    Возвращает путь к временному файлу или None при ошибке.
    """
    try:
        # Создаём временный файл
        temp_dir = tempfile.gettempdir()
        temp_file = Path(temp_dir) / f"whisper_temp_{input_path.stem}.mp3"

        # Конвертация через ffmpeg
        cmd = [
            ffmpeg_path,
            "-i", str(input_path),
            "-vn",                    # Без видео
            "-acodec", "libmp3lame",  # Кодек MP3
            "-ar", "16000",           # Sample rate для Whisper
            "-ac", "1",               # Моно
            "-b:a", "64k",            # Битрейт
            "-y",                     # Перезаписать если есть
            str(temp_file)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0 and temp_file.exists():
            return temp_file
        else:
            print(f"    [!] Ошибка ffmpeg: {result.stderr[:200]}")
            return None

    except Exception as e:
        print(f"    [!] Ошибка конвертации: {e}")
        return None


def get_audio_duration(filepath: Path, ffmpeg_path: str) -> Optional[float]:
    """Получить длительность аудио в секундах через ffprobe."""
    try:
        # Используем ffprobe (часть ffmpeg)
        ffprobe = ffmpeg_path.replace("ffmpeg", "ffprobe")

        cmd = [
            ffprobe,
            "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(filepath)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return float(result.stdout.strip())
    except:
        pass

    return None


# ═══════════════════════════════════════════════════════════════
# ПОИСК ГОЛОСОВЫХ ФАЙЛОВ
# ═══════════════════════════════════════════════════════════════

def scan_voice_files(export_dirs: List[Path]) -> Dict[str, List[Dict]]:
    """
    Сканировать все папки экспорта и найти голосовые файлы.

    Returns:
        Dict: jid -> [{"path": Path, "filename": str, "size_mb": float}]
    """
    voice_files = defaultdict(list)
    total_found = 0
    total_size_mb = 0

    print("\n[СКАНИРОВАНИЕ] Поиск голосовых файлов...")

    for export_dir in export_dirs:
        if not export_dir.exists():
            print(f"  [!] Директория не найдена: {export_dir}")
            continue

        print(f"\n  Сканирование: {export_dir}")
        dir_count = 0

        # Проходим по всем подпапкам чатов
        for chat_folder in export_dir.iterdir():
            if not chat_folder.is_dir():
                continue

            # Ищем папку media
            media_folder = chat_folder / "media"
            if not media_folder.exists():
                continue

            # Извлекаем JID из имени папки
            # Формат: "Имя контакта (971501234567@s.whatsapp.net)" или JID напрямую
            folder_name = chat_folder.name
            jid = None

            if "@" in folder_name:
                # Ищем JID в скобках или берём всё имя
                import re
                jid_match = re.search(r'\(([^)]+@[^)]+)\)', folder_name)
                if jid_match:
                    jid = jid_match.group(1)
                elif "@" in folder_name:
                    jid = folder_name
            else:
                # Используем имя папки как идентификатор
                jid = folder_name

            if not jid:
                jid = folder_name

            # Сканируем файлы в media
            for filepath in media_folder.iterdir():
                if not filepath.is_file():
                    continue

                if not is_audio_file(filepath):
                    continue

                # Проверяем, голосовое ли это
                if not is_voice_message(filepath):
                    continue

                size_mb = get_file_size_mb(filepath)

                voice_files[jid].append({
                    "path": filepath,
                    "filename": filepath.name,
                    "size_mb": size_mb,
                    "chat_folder": chat_folder.name,
                    "source": "whatsapp" if "ватсапа" in str(export_dir) else "wa_business",
                })

                dir_count += 1
                total_size_mb += size_mb

        print(f"    Найдено голосовых: {dir_count}")
        total_found += dir_count

    print(f"\n  ИТОГО: {total_found} голосовых файлов")
    print(f"  Общий размер: {total_size_mb:.1f} MB")
    print(f"  Уникальных контактов: {len(voice_files)}")

    return voice_files


# ═══════════════════════════════════════════════════════════════
# ТРАНСКРИБАЦИЯ ЧЕРЕЗ OPENAI API
# ═══════════════════════════════════════════════════════════════

def rate_limit():
    """Соблюдение rate limit для API."""
    global last_request_time

    with api_lock:
        current_time = time.time()
        time_since_last = current_time - last_request_time

        if time_since_last < REQUEST_INTERVAL:
            sleep_time = REQUEST_INTERVAL - time_since_last
            time.sleep(sleep_time)

        last_request_time = time.time()


def transcribe_file(
    client: "OpenAI",
    filepath: Path,
    ffmpeg_path: Optional[str] = None
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Транскрибировать один аудиофайл через OpenAI Whisper API.

    Returns:
        Tuple: (text, language, error)
    """
    temp_file = None

    try:
        # Проверка размера
        size_mb = get_file_size_mb(filepath)
        if size_mb > MAX_FILE_SIZE_MB:
            return None, None, f"Файл слишком большой: {size_mb:.1f} MB"

        # Нужна ли конвертация?
        file_to_use = filepath

        if filepath.suffix.lower() in NEEDS_CONVERSION:
            if not ffmpeg_path:
                return None, None, "Требуется ffmpeg для конвертации .opus/.ogg"

            temp_file = convert_to_mp3(filepath, ffmpeg_path)
            if not temp_file:
                return None, None, "Ошибка конвертации в MP3"

            file_to_use = temp_file

        # Rate limiting
        rate_limit()

        # Вызов API
        with open(file_to_use, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model=WHISPER_MODEL,
                file=audio_file,
                response_format="verbose_json",  # Для получения языка
            )

        text = response.text.strip() if response.text else ""
        language = getattr(response, 'language', None)

        return text, language, None

    except Exception as e:
        error_msg = str(e)

        # Специфичные ошибки API
        if "rate_limit" in error_msg.lower():
            return None, None, "RATE_LIMIT"
        elif "file_too_large" in error_msg.lower():
            return None, None, f"Файл слишком большой для API"

        return None, None, error_msg

    finally:
        # Удаляем временный файл
        if temp_file and temp_file.exists():
            try:
                temp_file.unlink()
            except:
                pass


def transcribe_with_retry(
    client: "OpenAI",
    filepath: Path,
    ffmpeg_path: Optional[str] = None
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Транскрибация с повторными попытками при ошибках."""

    for attempt in range(MAX_RETRIES):
        text, language, error = transcribe_file(client, filepath, ffmpeg_path)

        if error is None:
            return text, language, None

        if error == "RATE_LIMIT":
            # Увеличиваем задержку при rate limit
            delay = RETRY_DELAY * (attempt + 1) * 2
            print(f"    [!] Rate limit, ожидание {delay}с...")
            time.sleep(delay)
            continue

        if "timeout" in error.lower() or "connection" in error.lower():
            # Сетевые ошибки - повторяем
            time.sleep(RETRY_DELAY * (attempt + 1))
            continue

        # Другие ошибки - не повторяем
        return None, None, error

    return None, None, f"Превышено число попыток ({MAX_RETRIES})"


# ═══════════════════════════════════════════════════════════════
# ОСНОВНАЯ ОБРАБОТКА
# ═══════════════════════════════════════════════════════════════

def load_progress(progress_file: Path) -> Dict:
    """Загрузить прогресс для продолжения."""
    if progress_file.exists():
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"processed": {}, "failed": {}, "stats": {}}


def save_progress(progress_file: Path, progress: Dict):
    """Сохранить прогресс."""
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def process_voice_files(
    voice_files: Dict[str, List[Dict]],
    api_key: str,
    ffmpeg_path: Optional[str],
    max_files: Optional[int] = None,
    skip_processed: bool = True,
) -> Dict[str, Any]:
    """
    Обработка всех голосовых файлов.

    Args:
        voice_files: Словарь jid -> список файлов
        api_key: OpenAI API ключ
        ffmpeg_path: Путь к ffmpeg
        max_files: Максимум файлов для обработки (для тестов)
        skip_processed: Пропускать уже обработанные

    Returns:
        Dict: Результаты транскрибации
    """
    print("\n" + "=" * 60)
    print("ТРАНСКРИБАЦИЯ ГОЛОСОВЫХ СООБЩЕНИЙ")
    print("=" * 60)

    # Инициализация OpenAI клиента
    client = OpenAI(api_key=api_key)

    # Загрузка прогресса
    progress = load_progress(PROGRESS_FILE)
    processed_files = progress.get("processed", {})
    failed_files = progress.get("failed", {})

    # Результаты
    transcripts = {}  # jid -> [transcripts]

    # Статистика
    stats = {
        "total_files": 0,
        "processed": 0,
        "skipped": 0,
        "failed": 0,
        "total_duration": 0,
        "languages": defaultdict(int),
        "errors": defaultdict(int),
    }

    # Подсчёт общего количества
    all_files = []
    for jid, files in voice_files.items():
        for file_info in files:
            all_files.append((jid, file_info))

    stats["total_files"] = len(all_files)

    if max_files:
        all_files = all_files[:max_files]
        print(f"\n[!] Ограничение: обработка только {max_files} файлов")

    print(f"\nФайлов к обработке: {len(all_files)}")
    print(f"Уже обработано: {len(processed_files)}")
    print(f"ffmpeg: {'найден' if ffmpeg_path else 'НЕ НАЙДЕН'}")

    if not ffmpeg_path:
        print("[!] ВНИМАНИЕ: без ffmpeg .opus файлы не будут обработаны")

    start_time = datetime.now()

    # Обработка файлов
    for idx, (jid, file_info) in enumerate(all_files, 1):
        filepath = file_info["path"]
        filename = file_info["filename"]
        file_key = str(filepath)

        # Пропуск уже обработанных
        if skip_processed and file_key in processed_files:
            stats["skipped"] += 1

            # Добавляем из кэша
            if jid not in transcripts:
                transcripts[jid] = []
            transcripts[jid].append(processed_files[file_key])
            continue

        # Пропуск ранее неудачных
        if file_key in failed_files:
            stats["skipped"] += 1
            continue

        # Прогресс
        if idx % 10 == 1 or idx == len(all_files):
            elapsed = (datetime.now() - start_time).total_seconds()
            speed = stats["processed"] / elapsed if elapsed > 0 else 0
            eta = (len(all_files) - idx) / speed / 60 if speed > 0 else 0
            print(f"\n[{idx}/{len(all_files)}] {filename[:50]}")
            print(f"    Скорость: {speed:.1f} файлов/сек, ETA: {eta:.1f} мин")

        # Транскрибация
        text, language, error = transcribe_with_retry(
            client, filepath, ffmpeg_path
        )

        if error:
            stats["failed"] += 1
            stats["errors"][error[:50]] += 1
            failed_files[file_key] = {"error": error, "time": datetime.now().isoformat()}
            print(f"    [X] Ошибка: {error[:80]}")
            continue

        # Успешно
        stats["processed"] += 1

        if language:
            stats["languages"][language] += 1

        # Получение длительности
        duration = None
        if ffmpeg_path:
            duration = get_audio_duration(filepath, ffmpeg_path)
            if duration:
                stats["total_duration"] += duration

        # Сохранение результата
        result = {
            "file": filename,
            "path": str(filepath),
            "text": text,
            "language": language,
            "duration": duration,
            "transcribed_at": datetime.now().isoformat(),
            "chat_folder": file_info.get("chat_folder"),
            "source": file_info.get("source"),
        }

        # Добавление в результаты
        if jid not in transcripts:
            transcripts[jid] = []
        transcripts[jid].append(result)

        # Сохранение в прогресс
        processed_files[file_key] = result

        # Периодическое сохранение прогресса
        if stats["processed"] % 50 == 0:
            progress["processed"] = processed_files
            progress["failed"] = failed_files
            progress["stats"] = dict(stats)
            progress["stats"]["languages"] = dict(stats["languages"])
            progress["stats"]["errors"] = dict(stats["errors"])
            save_progress(PROGRESS_FILE, progress)
            print(f"    [*] Прогресс сохранён")

        # Краткий вывод текста
        if text:
            preview = text[:100] + "..." if len(text) > 100 else text
            print(f"    [{language or '?'}] {preview}")

    # Финальное сохранение прогресса
    progress["processed"] = processed_files
    progress["failed"] = failed_files
    progress["stats"] = dict(stats)
    progress["stats"]["languages"] = dict(stats["languages"])
    progress["stats"]["errors"] = dict(stats["errors"])
    save_progress(PROGRESS_FILE, progress)

    # Итоговая статистика
    elapsed = (datetime.now() - start_time).total_seconds()

    print("\n" + "=" * 60)
    print("СТАТИСТИКА ТРАНСКРИБАЦИИ")
    print("=" * 60)
    print(f"Всего файлов: {stats['total_files']}")
    print(f"Обработано: {stats['processed']}")
    print(f"Пропущено (из кэша): {stats['skipped']}")
    print(f"Ошибок: {stats['failed']}")
    print(f"Время: {elapsed:.1f} сек")
    print(f"Скорость: {stats['processed']/elapsed:.2f} файлов/сек" if elapsed > 0 else "")
    print(f"Общая длительность аудио: {stats['total_duration']/60:.1f} мин")

    if stats["languages"]:
        print("\nЯзыки:")
        for lang, count in sorted(stats["languages"].items(), key=lambda x: -x[1]):
            print(f"  {lang}: {count}")

    if stats["errors"]:
        print("\nОшибки:")
        for err, count in sorted(stats["errors"].items(), key=lambda x: -x[1])[:5]:
            print(f"  {err}: {count}")

    return {
        "transcripts": transcripts,
        "stats": dict(stats),
    }


def save_transcripts(transcripts: Dict[str, List[Dict]], output_file: Path):
    """Сохранить транскрипты в JSON."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    result = {
        "generated_at": datetime.now().isoformat(),
        "total_contacts": len(transcripts),
        "total_transcripts": sum(len(v) for v in transcripts.values()),
        "transcripts": transcripts,
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n[*] Транскрипты сохранены: {output_file}")
    print(f"    Размер: {output_file.stat().st_size / 1024 / 1024:.1f} MB")


def update_messages_with_transcripts(
    messages_file: Path,
    output_file: Path,
    transcripts: Dict[str, List[Dict]]
):
    """
    Обновить all_messages.jsonl, добавив транскрипты к голосовым.

    Ищет сообщения с media типа "ГОЛОСОВОЕ" и добавляет поле voice_text.
    """
    print("\n[ОБНОВЛЕНИЕ] Добавление транскриптов в сообщения...")

    if not messages_file.exists():
        print(f"  [!] Файл сообщений не найден: {messages_file}")
        return

    # Создаём индекс транскриптов по имени файла
    transcript_index = {}
    for jid, trans_list in transcripts.items():
        for trans in trans_list:
            filename = trans.get("file", "")
            if filename:
                transcript_index[filename] = trans

    print(f"  Индекс транскриптов: {len(transcript_index)} записей")

    updated_count = 0
    total_count = 0

    with open(messages_file, 'r', encoding='utf-8') as fin, \
         open(output_file, 'w', encoding='utf-8') as fout:

        for line in fin:
            total_count += 1

            try:
                msg = json.loads(line.strip())
            except json.JSONDecodeError:
                fout.write(line)
                continue

            # Проверяем наличие голосовых в медиа
            media = msg.get("media")
            if media and isinstance(media, list):
                for media_item in media:
                    media_type = media_item.get("type", "").upper()
                    media_path = media_item.get("path", "")

                    if "ГОЛОС" in media_type or "VOICE" in media_type or "PTT" in media_type:
                        # Извлекаем имя файла из пути
                        filename = Path(media_path).name if media_path else ""

                        if filename in transcript_index:
                            trans = transcript_index[filename]
                            media_item["voice_text"] = trans.get("text", "")
                            media_item["voice_language"] = trans.get("language")
                            media_item["voice_duration"] = trans.get("duration")
                            updated_count += 1

            fout.write(json.dumps(msg, ensure_ascii=False) + "\n")

            # Прогресс
            if total_count % 100000 == 0:
                print(f"    Обработано: {total_count:,} сообщений, обновлено: {updated_count}")

    print(f"\n  Всего сообщений: {total_count:,}")
    print(f"  Обновлено с транскриптами: {updated_count}")
    print(f"  Сохранено: {output_file}")


# ═══════════════════════════════════════════════════════════════
# ИНТЕГРАЦИЯ С ПРОФИЛЯМИ
# ═══════════════════════════════════════════════════════════════

def add_transcripts_to_profiles(
    profiles_file: Path,
    transcripts: Dict[str, List[Dict]]
):
    """
    Добавить транскрипты голосовых в профили клиентов.
    Создаёт новое поле voice_summary с анализом голосовых.
    """
    print("\n[ПРОФИЛИ] Добавление транскриптов в профили...")

    if not profiles_file.exists():
        print(f"  [!] Файл профилей не найден: {profiles_file}")
        return

    with open(profiles_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    profiles = data.get("profiles", [])
    updated = 0

    for profile in profiles:
        contact_id = profile.get("contact_id", "")

        # Ищем транскрипты для этого контакта
        contact_transcripts = transcripts.get(contact_id, [])

        if not contact_transcripts:
            # Пробуем поискать по частичному совпадению
            for jid, trans in transcripts.items():
                if contact_id in jid or jid in contact_id:
                    contact_transcripts = trans
                    break

        if contact_transcripts:
            # Собираем все тексты
            all_texts = [t["text"] for t in contact_transcripts if t.get("text")]

            profile["voice_messages"] = {
                "count": len(contact_transcripts),
                "total_duration": sum(t.get("duration", 0) or 0 for t in contact_transcripts),
                "languages": list(set(t.get("language") for t in contact_transcripts if t.get("language"))),
                "sample_texts": all_texts[:5],  # Первые 5 примеров
            }
            updated += 1

    # Сохраняем обновлённые профили
    data["profiles"] = profiles
    data["metadata"]["voice_transcripts_added"] = datetime.now().isoformat()

    with open(profiles_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  Обновлено профилей: {updated}")


# ═══════════════════════════════════════════════════════════════
# ГЛАВНАЯ ФУНКЦИЯ
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Транскрибация голосовых сообщений WhatsApp через OpenAI Whisper API"
    )
    parser.add_argument(
        "--api-key", "-k",
        default=OPENAI_API_KEY,
        help="OpenAI API ключ (или переменная OPENAI_API_KEY)"
    )
    parser.add_argument(
        "--max-files", "-n",
        type=int,
        default=None,
        help="Максимум файлов для обработки (для тестов)"
    )
    parser.add_argument(
        "--no-skip",
        action="store_true",
        help="Не пропускать уже обработанные файлы"
    )
    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="Только сканирование, без транскрибации"
    )
    parser.add_argument(
        "--update-messages",
        action="store_true",
        help="Обновить all_messages.jsonl с транскриптами"
    )
    parser.add_argument(
        "--update-profiles",
        action="store_true",
        help="Добавить транскрипты в профили"
    )
    parser.add_argument(
        "--output", "-o",
        default=str(TRANSCRIPTS_FILE),
        help=f"Выходной файл (default: {TRANSCRIPTS_FILE})"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("VOICE TRANSCRIBER - OpenAI Whisper API")
    print("=" * 60)

    # Проверка зависимостей
    if not OPENAI_AVAILABLE:
        print("\n[!] Установите openai: pip install openai")
        sys.exit(1)

    if not args.api_key and not args.scan_only:
        print("\n[!] Требуется OPENAI_API_KEY!")
        print("    Установите переменную окружения или используйте --api-key")
        sys.exit(1)

    # Создание директорий
    ensure_directories()

    # Поиск ffmpeg
    ffmpeg_path = find_ffmpeg()
    if ffmpeg_path:
        print(f"\n[*] ffmpeg найден: {ffmpeg_path}")
    else:
        print("\n[!] ffmpeg не найден. Конвертация .opus недоступна.")

    # Сканирование файлов
    voice_files = scan_voice_files(EXPORT_DIRS)

    if not voice_files:
        print("\n[!] Голосовые файлы не найдены")
        sys.exit(1)

    if args.scan_only:
        print("\n[*] Режим сканирования. Транскрибация пропущена.")
        return

    # Транскрибация
    results = process_voice_files(
        voice_files=voice_files,
        api_key=args.api_key,
        ffmpeg_path=ffmpeg_path,
        max_files=args.max_files,
        skip_processed=not args.no_skip,
    )

    transcripts = results.get("transcripts", {})

    # Сохранение транскриптов
    output_file = Path(args.output)
    save_transcripts(transcripts, output_file)

    # Обновление сообщений
    if args.update_messages and MESSAGES_FILE.exists():
        update_messages_with_transcripts(
            MESSAGES_FILE,
            UPDATED_MESSAGES_FILE,
            transcripts
        )

    # Обновление профилей
    if args.update_profiles:
        profiles_file = JSON_DIR / "profiles.json"
        if profiles_file.exists():
            add_transcripts_to_profiles(profiles_file, transcripts)

    print("\n" + "=" * 60)
    print("ГОТОВО!")
    print("=" * 60)


if __name__ == "__main__":
    main()
