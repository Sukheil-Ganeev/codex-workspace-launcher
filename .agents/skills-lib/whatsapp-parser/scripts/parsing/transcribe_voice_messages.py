#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Транскрипция голосовых сообщений из WhatsApp через Yandex SpeechKit.

Обрабатывает .opus файлы любой длины:
- Короткие (≤29 сек) → прямая транскрипция
- Длинные (>29 сек) → деление на части + склеивание

Требует:
- YANDEX_CLOUD_API_KEY
- YANDEX_CLOUD_FOLDER_ID
- ffmpeg и ffprobe
"""

import json
import os
import sys
import subprocess
import math
import requests
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import argparse


# Yandex Cloud настройки
YANDEX_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_CLOUD_FOLDER_ID", "b1gvu3q8k1kafqd3sk5f")


def get_audio_duration(audio_path: str) -> float:
    """Получить длительность аудио через ffprobe."""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"[ERROR] Cannot get duration for {audio_path}: {e}")
        return 0.0


def transcribe_direct(audio_path: str, lang: str = "ru-RU") -> str:
    """Прямая транскрипция через Sync API (для файлов ≤29 сек)."""
    if not YANDEX_API_KEY:
        raise ValueError("YANDEX_CLOUD_API_KEY not set")

    try:
        with open(audio_path, "rb") as audio_file:
            response = requests.post(
                "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
                params={
                    "folderId": YANDEX_FOLDER_ID,
                    "lang": lang,
                    "format": "oggopus",
                    "sampleRateHertz": 48000
                },
                headers={
                    "Authorization": f"Api-Key {YANDEX_API_KEY}"
                },
                data=audio_file,
                timeout=30
            )

        if response.status_code == 200:
            return response.json().get("result", "")
        else:
            raise Exception(f"SpeechKit error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"[ERROR] Transcription failed for {audio_path}: {e}")
        return ""


def transcribe_with_splitting(audio_path: str, lang: str) -> str:
    """
    Обработка длинных аудио (>29 сек).

    1. Делит на части по 29 сек (без перекодирования!)
    2. Транскрибирует каждую часть
    3. Склеивает текст
    4. Удаляет временные файлы
    """
    duration = get_audio_duration(audio_path)
    num_chunks = math.ceil(duration / 29.0)
    chunks = []

    try:
        # Делим на части
        for i in range(num_chunks):
            chunk_path = f"{audio_path}_chunk_{i:03d}.ogg"
            start_time = i * 29

            # КРИТИЧНО: -c copy (без перекодирования)
            subprocess.run([
                'ffmpeg', '-i', audio_path,
                '-ss', str(start_time),
                '-t', '29',
                '-c', 'copy',
                chunk_path, '-y'
            ], capture_output=True, check=True)

            chunks.append(chunk_path)

        # Транскрибируем каждую часть
        transcripts = []
        for chunk in chunks:
            text = transcribe_direct(chunk, lang)
            if text.strip():
                transcripts.append(text)

        # Склеиваем
        return " ".join(transcripts)

    finally:
        # Cleanup
        for chunk in chunks:
            if os.path.exists(chunk):
                os.remove(chunk)


def transcribe_any_audio(audio_path: str, lang: str = "ru-RU") -> str:
    """
    Универсальная транскрипция — обрабатывает файлы ЛЮБОЙ длины.

    Args:
        audio_path: Путь к .opus файлу
        lang: Язык (ru-RU, en-US, tr-TR)

    Returns:
        str: Транскрибированный текст
    """
    duration = get_audio_duration(audio_path)

    if duration <= 0:
        return ""

    # Порог 29 сек (не 30!) — запас на погрешности
    if duration <= 29.0:
        return transcribe_direct(audio_path, lang)
    else:
        return transcribe_with_splitting(audio_path, lang)


def extract_voice_messages(jsonl_path: str, source_dir: str) -> List[Dict]:
    """
    Извлечь все голосовые сообщения из JSONL.

    Returns:
        List of dicts with: message_id, chat_folder, media_path, full_path
    """
    voice_messages = []

    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                msg = json.loads(line)

                # Проверяем наличие голосового
                if msg.get("media_type") == "голосовое" and msg.get("media_path"):
                    media_path = msg["media_path"]
                    chat_folder = msg.get("chat_folder", "unknown")

                    # Полный путь к файлу
                    full_path = Path(source_dir) / chat_folder / media_path

                    voice_messages.append({
                        "message_id": msg.get("id", f"msg_{line_num}"),
                        "chat_folder": chat_folder,
                        "media_path": media_path,
                        "full_path": str(full_path),
                        "timestamp": msg.get("timestamp", ""),
                        "sender": msg.get("sender", "")
                    })

            except json.JSONDecodeError:
                print(f"[WARNING] Invalid JSON at line {line_num}")
                continue

    return voice_messages


def transcribe_batch(voice_messages: List[Dict], lang: str = "ru-RU") -> Dict:
    """
    Транскрибировать батч голосовых сообщений.

    Returns:
        Dict with transcriptions and stats
    """
    results = {
        "transcriptions": [],
        "stats": {
            "total": len(voice_messages),
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "total_duration": 0.0
        }
    }

    print(f"\n[INFO] Starting transcription of {len(voice_messages)} voice messages...")

    for i, vm in enumerate(voice_messages, 1):
        print(f"[{i}/{len(voice_messages)}] Processing: {vm['media_path']}")

        audio_path = vm["full_path"]

        # Проверка существования файла
        if not os.path.exists(audio_path):
            print(f"  [SKIP] File not found")
            results["stats"]["skipped"] += 1
            continue

        # Получить длительность
        duration = get_audio_duration(audio_path)
        results["stats"]["total_duration"] += duration

        # Транскрибировать
        try:
            text = transcribe_any_audio(audio_path, lang)

            if text:
                results["transcriptions"].append({
                    "message_id": vm["message_id"],
                    "chat_folder": vm["chat_folder"],
                    "media_path": vm["media_path"],
                    "timestamp": vm["timestamp"],
                    "sender": vm["sender"],
                    "duration": round(duration, 2),
                    "transcription": text,
                    "language": lang
                })
                results["stats"]["success"] += 1
                print(f"  [OK] {len(text)} chars, {duration:.1f}s: {text[:50]}...")
            else:
                results["stats"]["failed"] += 1
                print(f"  [FAIL] Empty transcription")

        except Exception as e:
            results["stats"]["failed"] += 1
            print(f"  [ERROR] {e}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Транскрибировать голосовые сообщения WhatsApp"
    )
    parser.add_argument("--input", required=True, help="JSONL файл с сообщениями")
    parser.add_argument("--source-dir", required=True, help="Корневая директория чатов")
    parser.add_argument("--output", required=True, help="Выходной JSON файл")
    parser.add_argument("--lang", default="ru-RU", help="Язык распознавания")
    parser.add_argument("--stats-output", help="Файл для статистики")

    args = parser.parse_args()

    # Проверка API ключа
    if not YANDEX_API_KEY:
        print("[ERROR] YANDEX_CLOUD_API_KEY not set!")
        print("Set it in environment or .env file:")
        print("  export YANDEX_CLOUD_API_KEY=your_api_key")
        sys.exit(1)

    # Проверка ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except Exception:
        print("[ERROR] ffmpeg not found! Install it first:")
        print("  Windows: choco install ffmpeg")
        print("  Linux: apt install ffmpeg")
        sys.exit(1)

    print(f"[INFO] Reading messages from: {args.input}")
    print(f"[INFO] Source directory: {args.source_dir}")

    # Извлечь голосовые
    voice_messages = extract_voice_messages(args.input, args.source_dir)

    if not voice_messages:
        print("[WARNING] No voice messages found in JSONL")
        sys.exit(0)

    print(f"[INFO] Found {len(voice_messages)} voice messages")

    # Транскрибировать
    results = transcribe_batch(voice_messages, args.lang)

    # Сохранить результаты
    output_dir = Path(args.output).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results["transcriptions"], f, ensure_ascii=False, indent=2)

    print(f"\n[INFO] Transcriptions saved to: {args.output}")

    # Статистика
    stats = results["stats"]
    print(f"\n=== STATISTICS ===")
    print(f"Total voice messages: {stats['total']}")
    print(f"Success: {stats['success']}")
    print(f"Failed: {stats['failed']}")
    print(f"Skipped (file not found): {stats['skipped']}")
    print(f"Total duration: {stats['total_duration']:.1f}s ({stats['total_duration']/60:.1f} min)")

    if args.stats_output:
        with open(args.stats_output, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"Stats saved to: {args.stats_output}")


if __name__ == "__main__":
    main()
