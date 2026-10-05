"""
Пакетная обработка множества аудио файлов

Функции:
- Обработка всех файлов в папке
- Progress bar (tqdm)
- Параллельная обработка (asyncio)
- Сохранение результатов в JSON/CSV
- Обработка ошибок для каждого файла

Установка зависимостей:
pip install aiohttp aiofiles tqdm pandas python-dotenv
"""

import os
import asyncio
import aiohttp
import aiofiles
import json
import csv
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from tqdm import tqdm
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Константы
YANDEX_CLOUD_API_KEY = os.getenv('YANDEX_CLOUD_API_KEY', 'PASTE_YANDEX_CLOUD_API_KEY_HERE')
YANDEX_CLOUD_FOLDER_ID = os.getenv('YANDEX_CLOUD_FOLDER_ID', 'b1gvu3q8k1kafqd3sk5f')
STT_API_URL = 'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize'

# Поддерживаемые форматы
SUPPORTED_FORMATS = ['.ogg', '.opus', '.mp3', '.wav']


class BatchTranscriber:
    """Класс для пакетной транскрипции аудио файлов"""

    def __init__(self, api_key: str, folder_id: str, max_concurrent: int = 5):
        """
        Инициализация

        Args:
            api_key: API ключ Yandex Cloud
            folder_id: ID папки в Yandex Cloud
            max_concurrent: Максимум одновременных запросов
        """
        self.api_key = api_key
        self.folder_id = folder_id
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.headers = {'Authorization': f'Api-Key {self.api_key}'}

    def find_audio_files(self, directory: str) -> List[str]:
        """
        Находит все аудио файлы в директории

        Args:
            directory: Путь к папке

        Returns:
            Список путей к аудио файлам
        """
        audio_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if Path(file).suffix.lower() in SUPPORTED_FORMATS:
                    audio_files.append(os.path.join(root, file))
        return audio_files

    async def transcribe_file(
        self,
        session: aiohttp.ClientSession,
        file_path: str,
        language: str = 'ru-RU',
        model: str = 'general',
        format_audio: str = 'oggopus'
    ) -> Dict[str, any]:
        """
        Асинхронная транскрипция одного файла

        Args:
            session: aiohttp сессия
            file_path: Путь к файлу
            language: Язык
            model: Модель
            format_audio: Формат

        Returns:
            Dict с результатом
        """
        async with self.semaphore:  # Ограничиваем количество одновременных запросов
            try:
                # Проверяем размер
                file_size = os.path.getsize(file_path)
                if file_size > 1024 * 1024:
                    return {
                        'file': file_path,
                        'success': False,
                        'error': f'Файл слишком большой: {file_size / 1024 / 1024:.2f} МБ'
                    }

                # Читаем файл
                async with aiofiles.open(file_path, 'rb') as f:
                    audio_data = await f.read()

                # Параметры запроса
                params = {
                    'folderId': self.folder_id,
                    'lang': language,
                    'model': model,
                    'format': format_audio
                }

                # Отправляем запрос
                async with session.post(
                    STT_API_URL,
                    headers=self.headers,
                    params=params,
                    data=audio_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            'file': file_path,
                            'success': True,
                            'text': result.get('result', ''),
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        text = await response.text()
                        return {
                            'file': file_path,
                            'success': False,
                            'error': f'HTTP {response.status}: {text}'
                        }

            except asyncio.TimeoutError:
                return {
                    'file': file_path,
                    'success': False,
                    'error': 'Timeout'
                }
            except Exception as e:
                return {
                    'file': file_path,
                    'success': False,
                    'error': str(e)
                }

    async def process_batch(
        self,
        file_paths: List[str],
        language: str = 'ru-RU',
        model: str = 'general',
        format_audio: str = 'oggopus'
    ) -> List[Dict[str, any]]:
        """
        Обрабатывает пакет файлов

        Args:
            file_paths: Список путей к файлам
            language: Язык
            model: Модель
            format_audio: Формат

        Returns:
            Список результатов
        """
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.transcribe_file(session, file_path, language, model, format_audio)
                for file_path in file_paths
            ]

            # Используем tqdm для отображения прогресса
            results = []
            for coro in tqdm(
                asyncio.as_completed(tasks),
                total=len(tasks),
                desc='Транскрибирование',
                unit='файл'
            ):
                result = await coro
                results.append(result)

            return results

    def save_results_json(self, results: List[Dict], output_path: str):
        """
        Сохраняет результаты в JSON

        Args:
            results: Список результатов
            output_path: Путь к выходному файлу
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f'Результаты сохранены в JSON: {output_path}')

    def save_results_csv(self, results: List[Dict], output_path: str):
        """
        Сохраняет результаты в CSV

        Args:
            results: Список результатов
            output_path: Путь к выходному файлу
        """
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['file', 'success', 'text', 'error', 'timestamp']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for result in results:
                writer.writerow({
                    'file': result.get('file', ''),
                    'success': result.get('success', False),
                    'text': result.get('text', ''),
                    'error': result.get('error', ''),
                    'timestamp': result.get('timestamp', '')
                })
        print(f'Результаты сохранены в CSV: {output_path}')

    def print_summary(self, results: List[Dict]):
        """
        Выводит сводку по результатам

        Args:
            results: Список результатов
        """
        total = len(results)
        successful = sum(1 for r in results if r['success'])
        failed = total - successful

        print(f"\n{'='*50}")
        print(f"СВОДКА")
        print(f"{'='*50}")
        print(f"Всего файлов: {total}")
        print(f"Успешно: {successful} ({successful/total*100:.1f}%)")
        print(f"Ошибок: {failed} ({failed/total*100:.1f}%)")
        print(f"{'='*50}\n")


async def main():
    """Пример использования"""

    # Настройки
    input_directory = 'D:/Downloads/audio_files'  # Папка с аудио
    output_json = 'D:/Downloads/transcriptions.json'
    output_csv = 'D:/Downloads/transcriptions.csv'

    print(f'Обрабатываем файлы из: {input_directory}\n')

    # Инициализируем транскрайбер
    transcriber = BatchTranscriber(
        api_key=YANDEX_CLOUD_API_KEY,
        folder_id=YANDEX_CLOUD_FOLDER_ID,
        max_concurrent=5  # Максимум 5 одновременных запросов
    )

    # Находим аудио файлы
    audio_files = transcriber.find_audio_files(input_directory)
    print(f'Найдено файлов: {len(audio_files)}\n')

    if not audio_files:
        print('Аудио файлы не найдены!')
        return

    # Обрабатываем
    results = await transcriber.process_batch(
        file_paths=audio_files,
        language='ru-RU',
        model='general',
        format_audio='oggopus'
    )

    # Сохраняем результаты
    transcriber.save_results_json(results, output_json)
    transcriber.save_results_csv(results, output_csv)

    # Выводим сводку
    transcriber.print_summary(results)

    # Выводим примеры
    print("Примеры транскрипций:\n")
    for i, result in enumerate(results[:3], 1):
        if result['success']:
            filename = Path(result['file']).name
            print(f"{i}. {filename}")
            print(f"   {result['text'][:100]}...\n")


if __name__ == '__main__':
    asyncio.run(main())
