"""
WhatsApp Voice Transcriber Class
Обработка голосовых сообщений через Yandex SpeechKit
"""

import os
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests
from pydub import AudioSegment


class WhatsAppTranscriber:
    """Класс для транскрипции WhatsApp голосовых сообщений"""

    # Поддерживаемые форматы
    SUPPORTED_FORMATS = ['.opus', '.ogg', '.m4a', '.mp3', '.wav', '.flac']

    # Лимит для короткого аудио (секунды)
    SHORT_AUDIO_LIMIT = 30

    def __init__(self, api_key: str, folder_id: str, verbose: bool = False):
        """
        Инициализация транскрибера

        Args:
            api_key: Yandex API ключ
            folder_id: Yandex Cloud Folder ID
            verbose: Детальный вывод
        """
        self.api_key = api_key
        self.folder_id = folder_id
        self.verbose = verbose

        # API endpoints
        self.short_audio_url = 'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize'
        self.long_audio_url = 'https://transcribe.api.cloud.yandex.net/speech/stt/v2/longRunningRecognize'

    def _log(self, message: str):
        """Вывод лога если verbose включен"""
        if self.verbose:
            print(f"[LOG] {message}")

    def _check_ffmpeg(self) -> bool:
        """Проверка наличия FFmpeg"""
        try:
            subprocess.run(
                ['ffmpeg', '-version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _convert_to_oggopus(self, input_file: str, output_file: str) -> bool:
        """
        Конвертация аудио в OGG Opus формат

        Args:
            input_file: Исходный файл
            output_file: Выходной файл

        Returns:
            True если успешно
        """
        try:
            self._log(f"Конвертация {input_file} -> {output_file}")

            subprocess.run([
                'ffmpeg', '-i', input_file,
                '-acodec', 'libopus',
                '-ar', '48000',
                '-ac', '1',
                '-b:a', '16k',
                '-y',
                output_file
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            return True

        except subprocess.CalledProcessError as e:
            self._log(f"Ошибка конвертации: {e}")
            return False

    def _get_audio_duration(self, file_path: str) -> float:
        """
        Получение длительности аудио

        Args:
            file_path: Путь к файлу

        Returns:
            Длительность в секундах
        """
        try:
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0
        except Exception as e:
            self._log(f"Ошибка получения длительности: {e}")
            return 0.0

    def _transcribe_short_audio(self, file_path: str, language: str = 'ru-RU') -> Dict[str, Any]:
        """
        Транскрипция короткого аудио (<30 сек)

        Args:
            file_path: Путь к файлу
            language: Язык аудио

        Returns:
            Словарь с результатом
        """
        try:
            with open(file_path, 'rb') as f:
                audio_data = f.read()

            headers = {
                'Authorization': f'Api-Key {self.api_key}'
            }

            params = {
                'lang': language,
                'folderId': self.folder_id,
                'format': 'oggopus',
                'sampleRateHertz': '48000'
            }

            self._log(f"Отправка запроса к SpeechKit (короткое аудио)...")

            response = requests.post(
                self.short_audio_url,
                headers=headers,
                params=params,
                data=audio_data,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            return {
                'text': result.get('result', ''),
                'confidence': 0.95,  # Yandex не всегда возвращает confidence
                'language': language
            }

        except requests.exceptions.RequestException as e:
            self._log(f"Ошибка API запроса: {e}")
            raise

    def _transcribe_long_audio(self, file_path: str, language: str = 'ru-RU') -> Dict[str, Any]:
        """
        Транскрипция длинного аудио (>30 сек) через асинхронный API

        Args:
            file_path: Путь к файлу
            language: Язык аудио

        Returns:
            Словарь с результатом
        """
        # Для production используйте Yandex Object Storage
        # Здесь упрощенная версия с предположением, что файл уже загружен

        self._log("Длинное аудио: используйте Streaming API или загрузите в Object Storage")

        # Fallback: разбиваем на части
        return self._transcribe_by_chunks(file_path, language)

    def _transcribe_by_chunks(self, file_path: str, language: str = 'ru-RU') -> Dict[str, Any]:
        """
        Транскрипция длинного аудио по частям

        Args:
            file_path: Путь к файлу
            language: Язык аудио

        Returns:
            Словарь с результатом
        """
        try:
            audio = AudioSegment.from_file(file_path)
            chunk_length_ms = 25000  # 25 секунд на чанк
            chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

            self._log(f"Разбито на {len(chunks)} частей")

            results = []

            for idx, chunk in enumerate(chunks, 1):
                self._log(f"Обработка части {idx}/{len(chunks)}")

                # Сохраняем временный чанк
                temp_file = f"temp_chunk_{idx}.ogg"
                chunk.export(temp_file, format='ogg', codec='libopus')

                # Транскрибируем
                try:
                    result = self._transcribe_short_audio(temp_file, language)
                    results.append(result['text'])
                finally:
                    # Удаляем временный файл
                    if os.path.exists(temp_file):
                        os.remove(temp_file)

                # Небольшая пауза между запросами
                time.sleep(0.5)

            return {
                'text': ' '.join(results),
                'confidence': 0.90,
                'language': language
            }

        except Exception as e:
            self._log(f"Ошибка обработки по частям: {e}")
            raise

    def transcribe_file(self, file_path: str, language: str = 'ru-RU') -> Dict[str, Any]:
        """
        Транскрипция одного файла

        Args:
            file_path: Путь к файлу
            language: Язык аудио

        Returns:
            Словарь с результатом транскрипции
        """
        start_time = time.time()
        file_path = Path(file_path)

        result = {
            'file': file_path.name,
            'path': str(file_path),
            'timestamp': None,
            'duration_seconds': 0.0,
            'text': '',
            'confidence': 0.0,
            'language': language,
            'status': 'pending'
        }

        try:
            # Проверка формата
            if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
                raise ValueError(f"Неподдерживаемый формат: {file_path.suffix}")

            # Конвертация если нужно
            work_file = file_path
            if file_path.suffix.lower() != '.ogg':
                if not self._check_ffmpeg():
                    raise RuntimeError("FFmpeg не установлен. Требуется для конвертации.")

                temp_file = file_path.with_suffix('.ogg')
                if not self._convert_to_oggopus(str(file_path), str(temp_file)):
                    raise RuntimeError("Ошибка конвертации аудио")
                work_file = temp_file

            # Получение длительности
            duration = self._get_audio_duration(str(work_file))
            result['duration_seconds'] = duration

            self._log(f"Длительность: {duration:.1f} сек")

            # Выбор метода транскрипции
            if duration <= self.SHORT_AUDIO_LIMIT:
                transcription = self._transcribe_short_audio(str(work_file), language)
            else:
                transcription = self._transcribe_long_audio(str(work_file), language)

            result['text'] = transcription['text']
            result['confidence'] = transcription['confidence']
            result['language'] = transcription['language']
            result['status'] = 'success'

            # Удаление временного файла
            if work_file != file_path and work_file.exists():
                work_file.unlink()

        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            self._log(f"Ошибка обработки {file_path.name}: {e}")

        result['processing_time'] = time.time() - start_time

        return result

    def transcribe_folder(self, folder_path: str, language: str = 'ru-RU') -> Dict[str, Any]:
        """
        Транскрипция всех аудио файлов в папке

        Args:
            folder_path: Путь к папке
            language: Язык аудио

        Returns:
            Словарь с результатами
        """
        folder = Path(folder_path)
        audio_files = []

        # Поиск всех аудио файлов
        for ext in self.SUPPORTED_FORMATS:
            audio_files.extend(folder.glob(f"*{ext}"))
            audio_files.extend(folder.glob(f"*{ext.upper()}"))

        if not audio_files:
            return {
                'total_files': 0,
                'successful': 0,
                'failed': 0,
                'total_duration_seconds': 0.0,
                'estimated_cost_rubles': 0.0,
                'transcriptions': []
            }

        self._log(f"Найдено {len(audio_files)} аудио файлов")

        results = {
            'total_files': len(audio_files),
            'successful': 0,
            'failed': 0,
            'total_duration_seconds': 0.0,
            'estimated_cost_rubles': 0.0,
            'transcriptions': []
        }

        for idx, audio_file in enumerate(audio_files, 1):
            print(f"\n[{idx}/{len(audio_files)}] Обработка: {audio_file.name}")

            transcription = self.transcribe_file(str(audio_file), language)
            results['transcriptions'].append(transcription)

            if transcription['status'] == 'success':
                results['successful'] += 1
                results['total_duration_seconds'] += transcription['duration_seconds']
            else:
                results['failed'] += 1

        # Расчет стоимости (примерный)
        # Короткие аудио: 0.2₽/мин, длинные: 0.5₽/мин
        minutes = results['total_duration_seconds'] / 60
        results['estimated_cost_rubles'] = minutes * 0.2  # Усредненный тариф

        return results

    def find_keywords(self, transcriptions: List[Dict[str, Any]], keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Поиск транскрипций с ключевыми словами

        Args:
            transcriptions: Список транскрипций
            keywords: Список ключевых слов

        Returns:
            Отфильтрованный список
        """
        results = []

        for item in transcriptions:
            text_lower = item['text'].lower()
            found_keywords = [kw for kw in keywords if kw.lower() in text_lower]

            if found_keywords:
                item['found_keywords'] = found_keywords
                results.append(item)

        return results
