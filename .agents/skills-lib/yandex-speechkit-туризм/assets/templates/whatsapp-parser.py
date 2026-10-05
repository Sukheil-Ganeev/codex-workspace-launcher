"""
Парсер WhatsApp экспорта с транскрипцией аудио

Функции:
- Парсинг WhatsApp экспорта чата
- Извлечение аудио файлов
- Транскрипция каждого аудио
- Замена <прикреплено: аудио> на текст
- Экспорт в новый текстовый файл

Использование:
    python whatsapp-parser.py /path/to/whatsapp/export

Структура экспорта WhatsApp:
    WhatsApp Chat with Name/
    ├── _chat.txt
    ├── PTT-20240115-WA0001.opus
    ├── PTT-20240115-WA0002.opus
    └── ...
"""

import os
import re
import sys
import requests
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Константы
SYNC_API_URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
AUDIO_PATTERNS = [
    r'PTT-\d+-WA\d+\.opus',  # WhatsApp голосовые (OPUS)
    r'AUD-\d+-WA\d+\.opus',  # WhatsApp аудио (OPUS)
    r'.*\.opus',
    r'.*\.ogg',
    r'.*\.mp3'
]


class WhatsAppTranscriber:
    """Транскрибер WhatsApp экспорта"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        folder_id: Optional[str] = None
    ):
        """
        Инициализация транскрибера

        Args:
            api_key: API ключ Yandex Cloud
            folder_id: ID каталога Yandex Cloud
        """
        self.api_key = api_key or os.getenv("YANDEX_CLOUD_API_KEY", "PASTE_YANDEX_CLOUD_API_KEY_HERE")
        self.folder_id = folder_id or os.getenv("YANDEX_CLOUD_FOLDER_ID", "b1gvu3q8k1kafqd3sk5f")

        if not self.api_key or not self.folder_id:
            raise ValueError("Укажите YANDEX_CLOUD_API_KEY и YANDEX_CLOUD_FOLDER_ID")

        # Статистика
        self.stats = {
            'total_messages': 0,
            'audio_messages': 0,
            'transcribed': 0,
            'failed': 0
        }

    def find_audio_files(self, export_dir: str) -> Dict[str, str]:
        """
        Находит все аудио файлы в директории экспорта

        Args:
            export_dir: Путь к директории экспорта WhatsApp

        Returns:
            Dict {filename: full_path}
        """
        audio_files = {}
        export_path = Path(export_dir)

        # Ищем по всем паттернам
        for pattern in AUDIO_PATTERNS:
            for file_path in export_path.glob('*'):
                if re.match(pattern, file_path.name, re.IGNORECASE):
                    audio_files[file_path.name] = str(file_path)

        return audio_files

    def transcribe_audio(self, audio_path: str) -> Dict[str, any]:
        """
        Транскрибирует аудио файл

        Args:
            audio_path: Путь к аудио файлу

        Returns:
            Dict с результатом
        """
        # Определяем формат
        ext = Path(audio_path).suffix.lower()
        format_map = {
            '.opus': 'oggopus',
            '.ogg': 'oggopus',
            '.mp3': 'mp3'
        }
        audio_format = format_map.get(ext, 'oggopus')

        try:
            # Читаем файл
            with open(audio_path, 'rb') as f:
                audio_data = f.read()

            # Проверяем размер
            file_size_mb = len(audio_data) / (1024 * 1024)
            if file_size_mb > 1.0:
                return {
                    'success': False,
                    'text': f'[Аудио слишком большое: {file_size_mb:.2f} МБ]'
                }

            # Параметры запроса
            params = {
                'folderId': self.folder_id,
                'lang': 'ru-RU',
                'model': 'general',
                'format': audio_format
            }

            headers = {
                'Authorization': f'Api-Key {self.api_key}'
            }

            # Отправляем запрос
            response = requests.post(
                SYNC_API_URL,
                params=params,
                headers=headers,
                data=audio_data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                text = result.get('result', '')

                self.stats['transcribed'] += 1

                return {
                    'success': True,
                    'text': text if text else '[Не удалось распознать]'
                }
            else:
                self.stats['failed'] += 1
                return {
                    'success': False,
                    'text': f'[Ошибка API: {response.status_code}]'
                }

        except Exception as e:
            self.stats['failed'] += 1
            return {
                'success': False,
                'text': f'[Ошибка: {str(e)}]'
            }

    def parse_chat_file(self, chat_file: str) -> List[str]:
        """
        Парсит файл чата WhatsApp

        Args:
            chat_file: Путь к _chat.txt

        Returns:
            Список строк чата
        """
        with open(chat_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        self.stats['total_messages'] = len(lines)
        return lines

    def process_chat(
        self,
        export_dir: str,
        output_file: Optional[str] = None
    ) -> str:
        """
        Обрабатывает экспорт WhatsApp: парсит чат и транскрибирует аудио

        Args:
            export_dir: Директория экспорта WhatsApp
            output_file: Путь к выходному файлу (опционально)

        Returns:
            Путь к обработанному файлу
        """
        export_path = Path(export_dir)

        # Ищем файл чата
        chat_file = export_path / '_chat.txt'
        if not chat_file.exists():
            raise FileNotFoundError(f"Файл чата не найден: {chat_file}")

        print(f"📂 Обработка экспорта: {export_dir}")

        # Находим аудио файлы
        print("🔍 Поиск аудио файлов...")
        audio_files = self.find_audio_files(export_dir)
        print(f"✅ Найдено аудио: {len(audio_files)}")

        # Парсим чат
        print("📖 Чтение чата...")
        lines = self.parse_chat_file(chat_file)

        # Обрабатываем каждую строку
        print("🎙️ Транскрипция аудио...")
        processed_lines = []

        for i, line in enumerate(lines, 1):
            # Ищем упоминания аудио файлов
            audio_match = None
            for pattern in AUDIO_PATTERNS:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    audio_match = match.group(0)
                    break

            if audio_match and audio_match in audio_files:
                self.stats['audio_messages'] += 1

                # Транскрибируем аудио
                audio_path = audio_files[audio_match]
                result = self.transcribe_audio(audio_path)

                # Заменяем в строке
                transcription = f"[🎙️ Голосовое: {result['text']}]"
                processed_line = line.replace(audio_match, transcription)
                processed_lines.append(processed_line)

                print(f"  {i}/{len(lines)}: {audio_match} → транскрибировано")
            else:
                processed_lines.append(line)

        # Сохраняем результат
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = export_path / f"chat_transcribed_{timestamp}.txt"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(processed_lines)

        print(f"\n✅ Обработано! Результат: {output_file}")
        return str(output_file)

    def print_stats(self):
        """Выводит статистику обработки"""
        print("\n" + "="*60)
        print("📊 СТАТИСТИКА")
        print("="*60)
        print(f"Всего сообщений:       {self.stats['total_messages']}")
        print(f"Голосовых сообщений:   {self.stats['audio_messages']}")
        print(f"✅ Транскрибировано:   {self.stats['transcribed']}")
        print(f"❌ Ошибки:             {self.stats['failed']}")
        print("="*60)


def main():
    """Точка входа CLI"""

    if len(sys.argv) < 2:
        print("Использование: python whatsapp-parser.py <whatsapp_export_dir>")
        print("\nПример:")
        print("  python whatsapp-parser.py \"WhatsApp Chat with John\"")
        print("\nСтруктура экспорта должна содержать:")
        print("  • _chat.txt")
        print("  • PTT-*.opus (голосовые)")
        sys.exit(1)

    export_dir = sys.argv[1]

    if not Path(export_dir).exists():
        print(f"❌ Директория не найдена: {export_dir}")
        sys.exit(1)

    try:
        transcriber = WhatsAppTranscriber()

        output_file = transcriber.process_chat(export_dir)
        transcriber.print_stats()

        print(f"\n🎉 Готово! Откройте файл: {output_file}")

    except FileNotFoundError as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        print("\nУстановите переменные окружения:")
        print("  YANDEX_CLOUD_API_KEY")
        print("  YANDEX_CLOUD_FOLDER_ID")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
