"""
Unit tests for WhatsApp Transcriber
"""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from whatsapp_transcriber import WhatsAppTranscriber


@pytest.fixture
def transcriber():
    """Фикстура для создания транскрибера"""
    return WhatsAppTranscriber(
        api_key="test_api_key",
        folder_id="test_folder_id",
        verbose=False
    )


def test_transcriber_initialization(transcriber):
    """Тест инициализации"""
    assert transcriber.api_key == "test_api_key"
    assert transcriber.folder_id == "test_folder_id"
    assert transcriber.verbose is False


def test_check_ffmpeg(transcriber):
    """Тест проверки FFmpeg"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock()
        result = transcriber._check_ffmpeg()
        assert result is True


def test_supported_formats(transcriber):
    """Тест поддерживаемых форматов"""
    expected_formats = ['.opus', '.ogg', '.m4a', '.mp3', '.wav', '.flac']
    assert transcriber.SUPPORTED_FORMATS == expected_formats


@patch('requests.post')
def test_transcribe_short_audio_success(mock_post, transcriber, tmp_path):
    """Тест успешной транскрипции короткого аудио"""
    # Создаем временный файл
    test_file = tmp_path / "test.ogg"
    test_file.write_bytes(b"fake audio data")

    # Мокаем ответ API
    mock_response = Mock()
    mock_response.json.return_value = {'result': 'Test transcription'}
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response

    result = transcriber._transcribe_short_audio(str(test_file))

    assert result['text'] == 'Test transcription'
    assert result['language'] == 'ru-RU'
    assert result['confidence'] == 0.95


def test_find_keywords(transcriber):
    """Тест поиска по ключевым словам"""
    transcriptions = [
        {'text': 'Сколько стоит экскурсия в Абу-Даби?', 'file': 'test1.opus'},
        {'text': 'Где купить билеты в Бурдж Халифа?', 'file': 'test2.opus'},
        {'text': 'Привет, как дела?', 'file': 'test3.opus'}
    ]

    keywords = ['экскурсия', 'билеты']
    results = transcriber.find_keywords(transcriptions, keywords)

    assert len(results) == 2
    assert results[0]['file'] == 'test1.opus'
    assert results[1]['file'] == 'test2.opus'


def test_transcribe_folder_empty(transcriber, tmp_path):
    """Тест обработки пустой папки"""
    result = transcriber.transcribe_folder(str(tmp_path))

    assert result['total_files'] == 0
    assert result['successful'] == 0
    assert result['failed'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
