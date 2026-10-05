#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
from tqdm import tqdm
import requests
from dotenv import load_dotenv
import csv
import json

load_dotenv()

def transcribe_file(file_path, api_key, folder_id):
    """Транскрибировать один файл"""
    with open(file_path, 'rb') as f:
        audio = f.read()

    response = requests.post(
        'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize',
        headers={'Authorization': f'Api-Key {api_key}'},
        params={'lang': 'ru-RU', 'folderId': folder_id, 'format': 'oggopus'},
        data=audio
    )
    return response.json().get('result', '')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default='results.csv')
    parser.add_argument('--format', choices=['csv', 'json'], default='csv')
    args = parser.parse_args()

    api_key = os.getenv('YANDEX_API_KEY')
    folder_id = os.getenv('YANDEX_FOLDER_ID')

    audio_files = list(Path(args.input).glob('*.ogg'))
    results = []

    for file in tqdm(audio_files, desc="Processing"):
        text = transcribe_file(file, api_key, folder_id)
        results.append({'file': file.name, 'text': text})

    if args.format == 'csv':
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['file', 'text'])
            writer.writeheader()
            writer.writerows(results)
    else:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nProcessed {len(results)} files → {args.output}")

if __name__ == '__main__':
    main()
