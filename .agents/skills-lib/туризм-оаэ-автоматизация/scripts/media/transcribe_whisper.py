#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт расшифровки голосовых сообщений WhatsApp
Использует OpenAI Whisper для speech-to-text
"""

import sys
import os
import glob
import argparse

# Исправление кодировки для Windows
sys.stdout.reconfigure(encoding='utf-8')

import whisper

def transcribe_voice_messages(directory, output_file, model_name="medium", device="cuda"):
    """
    Расшифровывает все .opus файлы в директории

    Args:
        directory: путь к папке с аудиофайлами
        output_file: путь к файлу для сохранения результатов
        model_name: модель Whisper (tiny/base/small/medium/large)
        device: устройство (cuda/cpu)
    """
    print(f"Загрузка модели Whisper ({model_name}) на {device}...")
    model = whisper.load_model(model_name, device=device)

    # Поиск всех opus файлов
    opus_files = sorted(glob.glob(os.path.join(directory, "*.opus")))
    print(f"Найдено {len(opus_files)} голосовых сообщений")

    results = []

    for i, filepath in enumerate(opus_files, 1):
        filename = os.path.basename(filepath)
        print(f"[{i}/{len(opus_files)}] Обработка: {filename}")

        try:
            result = model.transcribe(
                filepath,
                language="ru",
                fp16=(device == "cuda")
            )
            text = result["text"].strip()
            results.append(f"=== {filename} ===\n{text}\n")
            print(f"    OK: {text[:50]}...")
        except Exception as e:
            results.append(f"=== {filename} ===\n[Ошибка расшифровки: {e}]\n")
            print(f"    ОШИБКА: {e}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(results))

    print(f"\nРезультаты сохранены в: {output_file}")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Расшифровка голосовых сообщений WhatsApp")
    parser.add_argument("directory", help="Папка с аудиофайлами")
    parser.add_argument("-o", "--output", default=None, help="Файл для сохранения")
    parser.add_argument("-m", "--model", default="medium", help="Модель Whisper")
    parser.add_argument("-d", "--device", default="cuda", help="Устройство (cuda/cpu)")

    args = parser.parse_args()

    output_file = args.output or os.path.join(args.directory, "transcripts.txt")
    transcribe_voice_messages(args.directory, output_file, args.model, args.device)
