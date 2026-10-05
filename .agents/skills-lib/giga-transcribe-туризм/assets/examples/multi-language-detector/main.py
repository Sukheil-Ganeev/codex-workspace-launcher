#!/usr/bin/env python3
import os
import requests
import concurrent.futures
from dotenv import load_dotenv
import argparse

load_dotenv()

SUPPORTED_LANGUAGES = {
    'ru-RU': 'Russian',
    'en-US': 'English',
    'ar-AE': 'Arabic',
    'tr-TR': 'Turkish'
}

def transcribe_language(audio_data, language):
    """Транскрибировать на конкретном языке"""
    try:
        response = requests.post(
            'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize',
            headers={'Authorization': f'Api-Key {os.getenv("YANDEX_API_KEY")}'},
            params={
                'lang': language,
                'folderId': os.getenv('YANDEX_FOLDER_ID'),
                'format': 'oggopus'
            },
            data=audio_data,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        text = result.get('result', '')

        # Примерная оценка confidence
        confidence = calculate_confidence(text, language)

        return {
            'language': language,
            'language_name': SUPPORTED_LANGUAGES[language],
            'text': text,
            'confidence': confidence,
            'success': True
        }
    except Exception as e:
        return {
            'language': language,
            'language_name': SUPPORTED_LANGUAGES[language],
            'text': '',
            'confidence': 0.0,
            'success': False,
            'error': str(e)
        }

def calculate_confidence(text, language):
    """Оценка уверенности на основе качества текста"""
    if not text or len(text) < 3:
        return 0.0

    # Базовая оценка
    score = 0.5

    # Длина текста (больше = лучше)
    if len(text) > 10:
        score += 0.1
    if len(text) > 30:
        score += 0.1

    # Наличие пробелов (слова)
    words = text.split()
    if len(words) > 2:
        score += 0.1

    # Специфичные слова для языков
    if language == 'ru-RU':
        russian_words = ['экскурсия', 'билет', 'тур', 'хотел', 'сколько', 'цена']
        if any(word in text.lower() for word in russian_words):
            score += 0.2
    elif language == 'en-US':
        english_words = ['tour', 'ticket', 'price', 'want', 'how', 'much']
        if any(word in text.lower() for word in english_words):
            score += 0.2
    elif language == 'ar-AE':
        if any(ord(c) >= 0x0600 and ord(c) <= 0x06FF for c in text):
            score += 0.2

    return min(score, 0.99)

def detect_language(audio_path):
    """Определить язык аудио"""
    with open(audio_path, 'rb') as f:
        audio_data = f.read()

    results = []

    # Параллельная обработка
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(transcribe_language, audio_data, lang): lang
            for lang in SUPPORTED_LANGUAGES.keys()
        }

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)

    # Сортировка по confidence
    results.sort(key=lambda x: x['confidence'], reverse=True)

    return results

def main():
    parser = argparse.ArgumentParser(description='Multi-language audio detector')
    parser.add_argument('--input', required=True, help='Audio file path')
    parser.add_argument('--verbose', action='store_true', help='Show all results')
    args = parser.parse_args()

    print(f"Analyzing audio: {args.input}\n")

    results = detect_language(args.input)

    print("Detected languages:")
    print("-" * 60)

    for result in results:
        if result['success']:
            print(f"  {result['language_name']:10} ({result['language']}): "
                  f"{result['confidence']:.2f}")
            if args.verbose:
                print(f"    Text: {result['text'][:50]}...")
        else:
            print(f"  {result['language_name']:10} ({result['language']}): "
                  f"ERROR - {result.get('error', 'Unknown')}")

    print("-" * 60)

    best = results[0]
    if best['success']:
        print(f"\nBest result: {best['language_name']} "
              f"(confidence: {best['confidence']:.2f})")
        print(f"Text: {best['text']}")
    else:
        print("\nNo successful transcriptions")

if __name__ == '__main__':
    main()
