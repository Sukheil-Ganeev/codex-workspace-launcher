#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv
import argparse
from openai import OpenAI

load_dotenv()

def transcribe_yandex(audio_path):
    """Yandex SpeechKit"""
    with open(audio_path, 'rb') as f:
        response = requests.post(
            'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize',
            headers={'Authorization': f'Api-Key {os.getenv("YANDEX_API_KEY")}'},
            params={'lang': 'ru-RU', 'folderId': os.getenv('YANDEX_FOLDER_ID')},
            data=f.read()
        )
    return response.json().get('result', ''), 'ru'

def transcribe_whisper(audio_path):
    """OpenAI Whisper"""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    with open(audio_path, 'rb') as f:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="en"
        )
    return response.text, response.language

def hybrid_transcribe(audio_path, auto_detect=True):
    """Гибридная транскрипция"""
    results = []

    # Попробовать Yandex
    try:
        text_ya, lang_ya = transcribe_yandex(audio_path)
        results.append(('yandex', text_ya, lang_ya, 0.95))
        print(f"[Yandex] {text_ya}")
    except Exception as e:
        print(f"[Yandex Error] {e}")

    # Попробовать Whisper
    try:
        text_w, lang_w = transcribe_whisper(audio_path)
        results.append(('whisper', text_w, lang_w, 0.90))
        print(f"[Whisper] {text_w}")
    except Exception as e:
        print(f"[Whisper Error] {e}")

    # Выбрать лучший
    if not results:
        return None

    # Если русский - предпочтение Yandex
    for engine, text, lang, conf in results:
        if engine == 'yandex' and lang == 'ru':
            return {'engine': 'yandex', 'text': text, 'language': lang}

    # Иначе вернуть Whisper
    for engine, text, lang, conf in results:
        if engine == 'whisper':
            return {'engine': 'whisper', 'text': text, 'language': lang}

    return {'engine': results[0][0], 'text': results[0][1], 'language': results[0][2]}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--auto-detect', action='store_true')
    args = parser.parse_args()

    result = hybrid_transcribe(args.input, args.auto_detect)
    print(f"\n[Result] Engine: {result['engine']}")
    print(f"[Result] Language: {result['language']}")
    print(f"[Result] Text: {result['text']}")
