"""
Базовая транскрибция аудио через Yandex SpeechKit Sync API

Поддерживает: OGG Opus, MP3
Ограничения: до 30 секунд, до 1 МБ

Автор: Шаблон для туристического бизнеса (Сухейль)
"""

import os
import requests
from pathlib import Path
from typing import Optional, Dict
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Константы API
YANDEX_CLOUD_API_KEY = os.getenv('YANDEX_CLOUD_API_KEY', 'PASTE_YANDEX_CLOUD_API_KEY_HERE')
YANDEX_CLOUD_FOLDER_ID = os.getenv('YANDEX_CLOUD_FOLDER_ID', 'b1gvu3q8k1kafqd3sk5f')
STT_API_URL = 'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize'


class SpeechKitTranscriber:
    """Класс для транскрибации аудио через Yandex SpeechKit"""

    def __init__(self, api_key: str, folder_id: str):
        """
        Инициализация транскрайбера

        Args:
            api_key: API ключ Yandex Cloud
            folder_id: ID папки в Yandex Cloud
        """
        self.api_key = api_key
        self.folder_id = folder_id
        self.headers = {
            'Authorization': f'Api-Key {self.api_key}'
        }

    def transcribe(
        self,
        audio_path: str,
        language: str = 'ru-RU',
        model: str = 'general',
        profanity_filter: bool = False,
        format_audio: str = 'oggopus'
    ) -> Dict[str, any]:
        """
        Транскрибирует аудио файл в текст

        Args:
            audio_path: Путь к аудио файлу
            language: Язык распознавания (ru-RU, en-US, ar-AE и др.)
            model: Модель распознавания (general, general:rc, maps)
            profanity_filter: Фильтр нецензурной лексики
            format_audio: Формат аудио (oggopus, lpcm, mp3)

        Returns:
            Dict с результатом:
            {
                'success': bool,
                'text': str,
                'error': str (если success=False)
            }
        """
        try:
            # Проверяем существование файла
            if not os.path.exists(audio_path):
                return {
                    'success': False,
                    'error': f'Файл не найден: {audio_path}'
                }

            # Проверяем размер файла (лимит 1 МБ)
            file_size = os.path.getsize(audio_path)
            if file_size > 1024 * 1024:
                return {
                    'success': False,
                    'error': f'Файл слишком большой: {file_size / 1024 / 1024:.2f} МБ (макс. 1 МБ)'
                }

            # Читаем аудио файл
            with open(audio_path, 'rb') as audio_file:
                audio_data = audio_file.read()

            # Параметры запроса
            params = {
                'folderId': self.folder_id,
                'lang': language,
                'model': model,
                'profanityFilter': str(profanity_filter).lower(),
                'format': format_audio
            }

            # Отправляем запрос
            response = requests.post(
                STT_API_URL,
                headers=self.headers,
                params=params,
                data=audio_data,
                timeout=30
            )

            # Обрабатываем ответ
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'text': result.get('result', ''),
                    'raw_response': result
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Таймаут запроса (>30 сек)'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Неожиданная ошибка: {str(e)}'
            }


def main():
    """Пример использования"""

    # Инициализируем транскрайбер
    transcriber = SpeechKitTranscriber(
        api_key=YANDEX_CLOUD_API_KEY,
        folder_id=YANDEX_CLOUD_FOLDER_ID
    )

    # Путь к аудио файлу (замените на свой)
    audio_file = 'D:/Downloads/voice_message.ogg'

    print(f'Транскрибируем: {audio_file}')

    # Транскрибируем
    result = transcriber.transcribe(
        audio_path=audio_file,
        language='ru-RU',
        model='general',
        format_audio='oggopus'
    )

    # Выводим результат
    if result['success']:
        print(f"\nРезультат:\n{result['text']}")
    else:
        print(f"\nОшибка: {result['error']}")


if __name__ == '__main__':
    main()
