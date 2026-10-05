"""
Webhook обработчик для Yandex SpeechKit (Flask/FastAPI)

Принимает аудио через webhook, транскрибирует и возвращает результат.
Идеально для интеграции с Make.com, Zapier, n8n.

Endpoints:
    POST /transcribe - Транскрипция аудио
    POST /transcribe-url - Транскрипция по URL
    GET /health - Проверка здоровья сервиса

Требования:
    pip install flask requests python-dotenv

Запуск:
    python webhook-handler.py

Для продакшн: gunicorn -w 4 -b 0.0.0.0:5000 webhook-handler:app
"""

import os
import hashlib
import hmac
import requests
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# Загружаем переменные окружения
load_dotenv()

# Константы
SYNC_API_URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
MAX_FILE_SIZE = 1024 * 1024  # 1 МБ
ALLOWED_EXTENSIONS = {'ogg', 'opus', 'mp3', 'wav'}

# Конфигурация Flask
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Yandex Cloud credentials
YANDEX_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY", "PASTE_YANDEX_CLOUD_API_KEY_HERE")
YANDEX_FOLDER_ID = os.getenv("YANDEX_CLOUD_FOLDER_ID", "b1gvu3q8k1kafqd3sk5f")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")  # Секрет для проверки подписи


class TranscriptionService:
    """Сервис транскрипции"""

    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Проверяет допустимость расширения файла"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def get_audio_format(filename: str) -> str:
        """Определяет формат аудио по расширению"""
        ext = filename.rsplit('.', 1)[1].lower()
        format_map = {
            'ogg': 'oggopus',
            'opus': 'oggopus',
            'mp3': 'mp3',
            'wav': 'lpcm'
        }
        return format_map.get(ext, 'oggopus')

    @staticmethod
    def transcribe(
        audio_data: bytes,
        audio_format: str,
        language: str = "ru-RU",
        model: str = "general"
    ) -> Dict[str, Any]:
        """
        Транскрибирует аудио данные

        Args:
            audio_data: Бинарные данные аудио
            audio_format: Формат аудио (oggopus, mp3, lpcm)
            language: Язык распознавания
            model: Модель SpeechKit

        Returns:
            Dict с результатом
        """
        params = {
            'folderId': YANDEX_FOLDER_ID,
            'lang': language,
            'model': model,
            'format': audio_format
        }

        headers = {
            'Authorization': f'Api-Key {YANDEX_API_KEY}'
        }

        try:
            response = requests.post(
                SYNC_API_URL,
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
                    'confidence': result.get('confidence', 0.0)
                }
            else:
                return {
                    'success': False,
                    'error': f"Yandex API error: {response.status_code}",
                    'details': response.text
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def verify_signature(payload: bytes, signature: str) -> bool:
    """
    Проверяет HMAC подпись webhook (опционально)

    Args:
        payload: Тело запроса (bytes)
        signature: Подпись из заголовка

    Returns:
        True если подпись валидна
    """
    if not WEBHOOK_SECRET:
        return True  # Если секрет не настроен, пропускаем проверку

    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)


@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервиса"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'yandex-speechkit-webhook'
    })


@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Endpoint для транскрипции загруженного аудио

    Параметры (multipart/form-data):
        - audio: Аудио файл (обязательно)
        - language: Язык (опционально, по умолчанию ru-RU)
        - model: Модель (опционально, по умолчанию general)

    Возвращает:
        JSON с результатом транскрипции
    """
    # Проверка API ключей
    if not YANDEX_API_KEY or not YANDEX_FOLDER_ID:
        return jsonify({
            'success': False,
            'error': 'Yandex Cloud credentials not configured'
        }), 500

    # Проверка подписи (если настроена)
    signature = request.headers.get('X-Webhook-Signature', '')
    if WEBHOOK_SECRET and not verify_signature(request.get_data(), signature):
        return jsonify({
            'success': False,
            'error': 'Invalid signature'
        }), 401

    # Проверка наличия файла
    if 'audio' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No audio file provided'
        }), 400

    file = request.files['audio']

    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'Empty filename'
        }), 400

    # Проверка расширения
    if not TranscriptionService.allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': f'Unsupported file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400

    # Получаем параметры
    language = request.form.get('language', 'ru-RU')
    model = request.form.get('model', 'general')

    # Читаем аудио
    audio_data = file.read()
    audio_format = TranscriptionService.get_audio_format(file.filename)

    # Транскрибируем
    result = TranscriptionService.transcribe(
        audio_data,
        audio_format,
        language,
        model
    )

    # Формируем ответ для Make.com
    if result['success']:
        return jsonify({
            'success': True,
            'text': result['text'],
            'confidence': result['confidence'],
            'metadata': {
                'filename': secure_filename(file.filename),
                'language': language,
                'model': model,
                'timestamp': datetime.now().isoformat()
            }
        })
    else:
        return jsonify(result), 500


@app.route('/transcribe-url', methods=['POST'])
def transcribe_from_url():
    """
    Endpoint для транскрипции аудио по URL

    Параметры (JSON):
        - url: URL аудио файла (обязательно)
        - language: Язык (опционально)
        - model: Модель (опционально)

    Возвращает:
        JSON с результатом транскрипции
    """
    # Проверка API ключей
    if not YANDEX_API_KEY or not YANDEX_FOLDER_ID:
        return jsonify({
            'success': False,
            'error': 'Yandex Cloud credentials not configured'
        }), 500

    # Получаем параметры
    data = request.get_json()

    if not data or 'url' not in data:
        return jsonify({
            'success': False,
            'error': 'No URL provided'
        }), 400

    url = data['url']
    language = data.get('language', 'ru-RU')
    model = data.get('model', 'general')

    try:
        # Скачиваем аудио
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        audio_data = response.content

        # Определяем формат по URL или Content-Type
        content_type = response.headers.get('Content-Type', '')

        if 'ogg' in content_type or url.endswith('.ogg'):
            audio_format = 'oggopus'
        elif 'mp3' in content_type or url.endswith('.mp3'):
            audio_format = 'mp3'
        elif 'wav' in content_type or url.endswith('.wav'):
            audio_format = 'lpcm'
        else:
            audio_format = 'oggopus'  # По умолчанию

        # Транскрибируем
        result = TranscriptionService.transcribe(
            audio_data,
            audio_format,
            language,
            model
        )

        # Формируем ответ
        if result['success']:
            return jsonify({
                'success': True,
                'text': result['text'],
                'confidence': result['confidence'],
                'metadata': {
                    'source_url': url,
                    'language': language,
                    'model': model,
                    'timestamp': datetime.now().isoformat()
                }
            })
        else:
            return jsonify(result), 500

    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Failed to download audio: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(413)
def file_too_large(e):
    """Обработчик ошибки "файл слишком большой" """
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.1f} MB'
    }), 413


@app.errorhandler(500)
def internal_error(e):
    """Обработчик внутренних ошибок"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Проверяем конфигурацию
    if not YANDEX_API_KEY or not YANDEX_FOLDER_ID:
        print("⚠️  ВНИМАНИЕ: Yandex Cloud credentials не настроены!")
        print("   Установите YANDEX_CLOUD_API_KEY и YANDEX_CLOUD_FOLDER_ID в .env")

    if not WEBHOOK_SECRET:
        print("⚠️  ВНИМАНИЕ: WEBHOOK_SECRET не установлен (проверка подписи отключена)")

    print("\n" + "="*60)
    print("🚀 Yandex SpeechKit Webhook Server")
    print("="*60)
    print(f"Endpoints:")
    print(f"  POST /transcribe       - Загрузка аудио файла")
    print(f"  POST /transcribe-url   - Транскрипция по URL")
    print(f"  GET  /health           - Health check")
    print("="*60 + "\n")

    # Запускаем сервер (только для разработки!)
    app.run(host='0.0.0.0', port=5000, debug=True)
