"""
Централизованная обработка ошибок для Yandex SpeechKit

Функции:
- Retry с exponential backoff
- Fallback на Whisper (OpenAI)
- Детальное логирование
- Circuit breaker pattern
- Rate limiting

Использование:
    from error_handler import RobustTranscriber

    transcriber = RobustTranscriber()
    result = transcriber.transcribe("audio.ogg")
"""

import os
import time
import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('speechkit_errors.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Константы
YANDEX_SYNC_API = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
OPENAI_API_URL = "https://api.openai.com/v1/audio/transcriptions"
MAX_RETRIES = 3
INITIAL_BACKOFF = 1  # Секунды
MAX_BACKOFF = 16  # Секунды


class CircuitBreaker:
    """Circuit Breaker для предотвращения лавины ошибок"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """
        Args:
            failure_threshold: Количество ошибок для открытия цепи
            timeout: Время в секундах до повторной попытки
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half_open

    def call(self, func: Callable, *args, **kwargs):
        """Вызывает функцию с защитой circuit breaker"""

        if self.state == 'open':
            # Проверяем, не пора ли попробовать снова
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = 'half_open'
                logger.info("Circuit breaker: переход в half_open")
            else:
                raise Exception(f"Circuit breaker открыт. Повтор через {self.timeout} сек")

        try:
            result = func(*args, **kwargs)

            # Успех - сбрасываем счетчик
            if self.state == 'half_open':
                self.state = 'closed'
                self.failures = 0
                logger.info("Circuit breaker: закрыт")

            return result

        except Exception as e:
            self.failures += 1
            self.last_failure_time = datetime.now()

            if self.failures >= self.failure_threshold:
                self.state = 'open'
                logger.warning(f"Circuit breaker: открыт после {self.failures} ошибок")

            raise e


def retry_with_backoff(max_retries: int = MAX_RETRIES, initial_backoff: float = INITIAL_BACKOFF):
    """
    Декоратор для retry с exponential backoff

    Args:
        max_retries: Максимум попыток
        initial_backoff: Начальная задержка
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            backoff = initial_backoff

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    retries += 1

                    if retries >= max_retries:
                        logger.error(f"Все попытки исчерпаны: {e}")
                        raise

                    logger.warning(f"Попытка {retries}/{max_retries} не удалась: {e}")
                    logger.info(f"Повтор через {backoff} сек...")

                    time.sleep(backoff)
                    backoff = min(backoff * 2, MAX_BACKOFF)  # Exponential backoff

            raise Exception("Неожиданный выход из retry loop")

        return wrapper
    return decorator


class RobustTranscriber:
    """Надежный транскрибер с обработкой ошибок и fallback"""

    def __init__(
        self,
        yandex_api_key: Optional[str] = None,
        yandex_folder_id: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        enable_fallback: bool = True
    ):
        """
        Инициализация транскрибера

        Args:
            yandex_api_key: API ключ Yandex Cloud
            yandex_folder_id: ID каталога Yandex Cloud
            openai_api_key: API ключ OpenAI (для fallback)
            enable_fallback: Включить fallback на Whisper
        """
        self.yandex_api_key = yandex_api_key or os.getenv("YANDEX_CLOUD_API_KEY", "PASTE_YANDEX_CLOUD_API_KEY_HERE")
        self.yandex_folder_id = yandex_folder_id or os.getenv("YANDEX_CLOUD_FOLDER_ID", "b1gvu3q8k1kafqd3sk5f")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.enable_fallback = enable_fallback and self.openai_api_key

        if not self.yandex_api_key or not self.yandex_folder_id:
            raise ValueError("Укажите Yandex Cloud credentials")

        # Circuit breaker для Yandex API
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

        # Статистика
        self.stats = {
            'yandex_success': 0,
            'yandex_failed': 0,
            'whisper_fallback': 0,
            'total_failed': 0
        }

    @retry_with_backoff(max_retries=3, initial_backoff=1)
    def _transcribe_yandex(
        self,
        audio_data: bytes,
        audio_format: str,
        language: str = "ru-RU"
    ) -> Dict[str, Any]:
        """
        Транскрипция через Yandex SpeechKit с retry

        Args:
            audio_data: Бинарные данные аудио
            audio_format: Формат (oggopus, mp3, lpcm)
            language: Язык

        Returns:
            Dict с результатом
        """
        params = {
            'folderId': self.yandex_folder_id,
            'lang': language,
            'model': 'general',
            'format': audio_format
        }

        headers = {
            'Authorization': f'Api-Key {self.yandex_api_key}'
        }

        response = requests.post(
            YANDEX_SYNC_API,
            params=params,
            headers=headers,
            data=audio_data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'text': result.get('result', ''),
                'confidence': result.get('confidence', 0.0),
                'provider': 'yandex'
            }
        else:
            error_msg = f"Yandex API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def _transcribe_whisper(
        self,
        audio_path: str,
        language: str = "ru"
    ) -> Dict[str, Any]:
        """
        Fallback транскрипция через OpenAI Whisper

        Args:
            audio_path: Путь к аудио файлу
            language: Язык (ISO 639-1)

        Returns:
            Dict с результатом
        """
        if not self.openai_api_key:
            raise Exception("OpenAI API key не настроен")

        logger.info("Использую fallback: OpenAI Whisper")

        headers = {
            'Authorization': f'Bearer {self.openai_api_key}'
        }

        with open(audio_path, 'rb') as f:
            files = {
                'file': f,
                'model': (None, 'whisper-1'),
                'language': (None, language)
            }

            response = requests.post(
                OPENAI_API_URL,
                headers=headers,
                files=files,
                timeout=60
            )

        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'text': result.get('text', ''),
                'confidence': 1.0,  # Whisper не возвращает confidence
                'provider': 'whisper'
            }
        else:
            error_msg = f"Whisper API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def transcribe(
        self,
        audio_path: str,
        language: str = "ru-RU"
    ) -> Dict[str, Any]:
        """
        Транскрибирует аудио с обработкой ошибок и fallback

        Args:
            audio_path: Путь к аудио файлу
            language: Язык (ru-RU для Yandex, ru для Whisper)

        Returns:
            Dict с результатом транскрипции
        """
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Файл не найден: {audio_path}")

        # Определяем формат
        ext = Path(audio_path).suffix.lower()
        format_map = {
            '.ogg': 'oggopus',
            '.opus': 'oggopus',
            '.mp3': 'mp3',
            '.wav': 'lpcm'
        }
        audio_format = format_map.get(ext, 'oggopus')

        # Читаем аудио
        with open(audio_path, 'rb') as f:
            audio_data = f.read()

        try:
            # Пытаемся через Yandex с circuit breaker
            result = self.circuit_breaker.call(
                self._transcribe_yandex,
                audio_data,
                audio_format,
                language
            )

            self.stats['yandex_success'] += 1
            logger.info(f"✅ Yandex SpeechKit: {audio_path}")
            return result

        except Exception as yandex_error:
            self.stats['yandex_failed'] += 1
            logger.error(f"❌ Yandex failed: {yandex_error}")

            # Пробуем fallback на Whisper
            if self.enable_fallback:
                try:
                    # Конвертируем язык для Whisper (ru-RU → ru)
                    whisper_lang = language.split('-')[0]

                    result = self._transcribe_whisper(audio_path, whisper_lang)
                    self.stats['whisper_fallback'] += 1
                    logger.info(f"✅ Whisper fallback: {audio_path}")
                    return result

                except Exception as whisper_error:
                    logger.error(f"❌ Whisper fallback failed: {whisper_error}")

            # Все методы провалились
            self.stats['total_failed'] += 1
            return {
                'success': False,
                'error': 'Все методы транскрипции провалились',
                'yandex_error': str(yandex_error),
                'text': None,
                'provider': None
            }

    def print_stats(self):
        """Выводит статистику"""
        print("\n" + "="*60)
        print("📊 СТАТИСТИКА ТРАНСКРИПЦИИ")
        print("="*60)
        print(f"✅ Yandex успешно:     {self.stats['yandex_success']}")
        print(f"❌ Yandex ошибки:      {self.stats['yandex_failed']}")
        print(f"🔄 Whisper fallback:   {self.stats['whisper_fallback']}")
        print(f"❌ Полный провал:      {self.stats['total_failed']}")
        print("="*60)


def main():
    """Пример использования"""
    import sys

    if len(sys.argv) < 2:
        print("Использование: python error-handler.py <audio_file>")
        sys.exit(1)

    audio_file = sys.argv[1]

    try:
        transcriber = RobustTranscriber(enable_fallback=True)

        print(f"🎙️ Транскрипция: {audio_file}")
        result = transcriber.transcribe(audio_file)

        if result['success']:
            print("\n" + "="*60)
            print(f"✅ Результат ({result['provider'].upper()}):")
            print("="*60)
            print(result['text'])
            print("="*60)
        else:
            print(f"\n❌ Ошибка: {result['error']}")

        transcriber.print_stats()

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
