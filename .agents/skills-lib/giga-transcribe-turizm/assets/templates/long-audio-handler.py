"""
Обработчик длинных аудио файлов для Yandex SpeechKit

Автоматически:
1. Определяет длительность аудио (ffprobe)
2. Делит на части по 29 секунд (ffmpeg -c copy)
3. Транскрибирует каждую часть
4. Склеивает результаты
5. Удаляет временные файлы

Требования: ffmpeg, ffprobe в PATH
"""

import os
import subprocess
import tempfile
import shutil
import requests
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Константы
YANDEX_CLOUD_API_KEY = os.getenv('YANDEX_CLOUD_API_KEY', 'PASTE_YANDEX_CLOUD_API_KEY_HERE')
YANDEX_CLOUD_FOLDER_ID = os.getenv('YANDEX_CLOUD_FOLDER_ID', 'b1gvu3q8k1kafqd3sk5f')
STT_API_URL = 'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize'
CHUNK_DURATION = 29  # секунд (лимит API - 30 сек)


class LongAudioHandler:
    """Класс для обработки длинных аудио файлов"""

    def __init__(self, api_key: str, folder_id: str):
        """
        Инициализация обработчика

        Args:
            api_key: API ключ Yandex Cloud
            folder_id: ID папки в Yandex Cloud
        """
        self.api_key = api_key
        self.folder_id = folder_id
        self.headers = {'Authorization': f'Api-Key {self.api_key}'}
        self.temp_dir = None

    def get_audio_duration(self, audio_path: str) -> Optional[float]:
        """
        Получает длительность аудио файла через ffprobe

        Args:
            audio_path: Путь к аудио файлу

        Returns:
            Длительность в секундах или None при ошибке
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except Exception as e:
            print(f'Ошибка получения длительности: {e}')
            return None

    def split_audio(self, audio_path: str, output_dir: str) -> List[str]:
        """
        Разбивает аудио на части по CHUNK_DURATION секунд

        Args:
            audio_path: Путь к исходному аудио
            output_dir: Папка для сохранения частей

        Returns:
            Список путей к частям
        """
        duration = self.get_audio_duration(audio_path)
        if duration is None:
            raise ValueError('Не удалось определить длительность аудио')

        print(f'Длительность аудио: {duration:.1f} сек')

        # Вычисляем количество частей
        num_chunks = int(duration / CHUNK_DURATION) + 1
        print(f'Разбиваем на {num_chunks} частей по {CHUNK_DURATION} сек')

        chunks = []
        file_ext = Path(audio_path).suffix

        for i in range(num_chunks):
            start_time = i * CHUNK_DURATION
            output_file = os.path.join(output_dir, f'chunk_{i:03d}{file_ext}')

            # Используем -c copy для быстрой нарезки без перекодирования
            cmd = [
                'ffmpeg',
                '-i', audio_path,
                '-ss', str(start_time),
                '-t', str(CHUNK_DURATION),
                '-c', 'copy',
                '-y',
                output_file
            ]

            try:
                subprocess.run(cmd, capture_output=True, check=True)
                chunks.append(output_file)
                print(f'Создан chunk {i+1}/{num_chunks}: {output_file}')
            except subprocess.CalledProcessError as e:
                print(f'Ошибка создания chunk {i}: {e}')

        return chunks

    def transcribe_chunk(
        self,
        chunk_path: str,
        language: str = 'ru-RU',
        model: str = 'general',
        format_audio: str = 'oggopus'
    ) -> Optional[str]:
        """
        Транскрибирует одну часть аудио

        Args:
            chunk_path: Путь к части аудио
            language: Язык распознавания
            model: Модель распознавания
            format_audio: Формат аудио

        Returns:
            Текст транскрипции или None при ошибке
        """
        try:
            with open(chunk_path, 'rb') as audio_file:
                audio_data = audio_file.read()

            params = {
                'folderId': self.folder_id,
                'lang': language,
                'model': model,
                'format': format_audio
            }

            response = requests.post(
                STT_API_URL,
                headers=self.headers,
                params=params,
                data=audio_data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('result', '')
            else:
                print(f'Ошибка API: {response.status_code} - {response.text}')
                return None

        except Exception as e:
            print(f'Ошибка транскрипции chunk: {e}')
            return None

    def process_long_audio(
        self,
        audio_path: str,
        language: str = 'ru-RU',
        model: str = 'general',
        format_audio: str = 'oggopus'
    ) -> Dict[str, any]:
        """
        Полный процесс обработки длинного аудио

        Args:
            audio_path: Путь к аудио файлу
            language: Язык распознавания
            model: Модель распознавания
            format_audio: Формат аудио

        Returns:
            Dict с результатом
        """
        try:
            # Создаём временную папку
            self.temp_dir = tempfile.mkdtemp(prefix='speechkit_')
            print(f'Временная папка: {self.temp_dir}')

            # Разбиваем на части
            chunks = self.split_audio(audio_path, self.temp_dir)

            if not chunks:
                return {
                    'success': False,
                    'error': 'Не удалось разбить аудио на части'
                }

            # Транскрибируем каждую часть
            transcripts = []
            for i, chunk in enumerate(chunks):
                print(f'Транскрибируем часть {i+1}/{len(chunks)}...')
                text = self.transcribe_chunk(chunk, language, model, format_audio)

                if text is not None:
                    transcripts.append(text)
                else:
                    print(f'Ошибка транскрипции части {i+1}')

            # Склеиваем результаты
            full_text = ' '.join(transcripts)

            return {
                'success': True,
                'text': full_text,
                'chunks_processed': len(transcripts),
                'chunks_total': len(chunks)
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка обработки: {str(e)}'
            }

        finally:
            # Удаляем временные файлы
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f'Временные файлы удалены')


def main():
    """Пример использования"""

    # Инициализируем обработчик
    handler = LongAudioHandler(
        api_key=YANDEX_CLOUD_API_KEY,
        folder_id=YANDEX_CLOUD_FOLDER_ID
    )

    # Путь к длинному аудио (замените на свой)
    audio_file = 'D:/Downloads/long_audio.ogg'

    print(f'Обрабатываем длинное аудио: {audio_file}\n')

    # Обрабатываем
    result = handler.process_long_audio(
        audio_path=audio_file,
        language='ru-RU',
        model='general',
        format_audio='oggopus'
    )

    # Выводим результат
    if result['success']:
        print(f"\n{'='*50}")
        print(f"Обработано частей: {result['chunks_processed']}/{result['chunks_total']}")
        print(f"{'='*50}")
        print(f"\nРезультат:\n{result['text']}")
    else:
        print(f"\nОшибка: {result['error']}")


if __name__ == '__main__':
    main()
