#!/usr/bin/env python3
"""
WhatsApp Voice Transcriber
Обработка голосовых сообщений из экспорта WhatsApp чатов
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from whatsapp_transcriber import WhatsAppTranscriber

# Загрузка переменных окружения
load_dotenv()


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Транскрипция голосовых сообщений из WhatsApp экспорта',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s --input whatsapp_export/
  %(prog)s --input voice.opus --output result.json
  %(prog)s --input export/ --verbose
        """
    )

    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Путь к папке с экспортом или конкретному файлу'
    )

    parser.add_argument(
        '--output', '-o',
        default='transcriptions.json',
        help='Файл для сохранения результатов (по умолчанию: transcriptions.json)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Детальный вывод процесса'
    )

    parser.add_argument(
        '--format', '-f',
        choices=['json', 'csv', 'txt'],
        default='json',
        help='Формат вывода результатов (по умолчанию: json)'
    )

    return parser.parse_args()


def print_summary(results: Dict[str, Any], verbose: bool = False):
    """Вывод итоговой статистики"""
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТЫ ОБРАБОТКИ")
    print("="*60)

    print(f"\nОбработано файлов: {results['successful']}/{results['total_files']}")

    if results['failed'] > 0:
        print(f"⚠️  Ошибок: {results['failed']}")

    print(f"Общая длительность: {results['total_duration_seconds']:.1f} сек")
    print(f"Примерная стоимость: {results['estimated_cost_rubles']:.2f} ₽")

    if verbose and results['transcriptions']:
        print("\n" + "-"*60)
        print("ТРАНСКРИПЦИИ:")
        print("-"*60)

        for idx, item in enumerate(results['transcriptions'], 1):
            print(f"\n[{idx}] {item['file']}")
            print(f"Время: {item.get('timestamp', 'N/A')}")
            print(f"Длительность: {item['duration_seconds']:.1f} сек")
            print(f"Текст: {item['text']}")
            print(f"Уверенность: {item['confidence']:.2f}")

            if item['status'] != 'success':
                print(f"⚠️  Статус: {item['status']}")


def export_to_csv(results: Dict[str, Any], output_file: str):
    """Экспорт результатов в CSV"""
    import csv

    csv_file = output_file.replace('.json', '.csv')

    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'file', 'timestamp', 'duration_seconds', 'text',
            'confidence', 'language', 'status'
        ])
        writer.writeheader()
        writer.writerows(results['transcriptions'])

    print(f"\n✅ CSV сохранен: {csv_file}")


def export_to_txt(results: Dict[str, Any], output_file: str):
    """Экспорт результатов в текстовый файл"""
    txt_file = output_file.replace('.json', '.txt')

    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("ТРАНСКРИПЦИИ WHATSAPP ГОЛОСОВЫХ\n")
        f.write("="*60 + "\n\n")

        for idx, item in enumerate(results['transcriptions'], 1):
            f.write(f"[{idx}] {item['file']}\n")
            f.write(f"Время: {item.get('timestamp', 'N/A')}\n")
            f.write(f"Текст: {item['text']}\n")
            f.write(f"Уверенность: {item['confidence']:.2f}\n")
            f.write("-"*60 + "\n\n")

    print(f"\n✅ TXT сохранен: {txt_file}")


def main():
    """Основная функция"""
    args = parse_arguments()

    # Проверка наличия API ключей
    api_key = os.getenv('YANDEX_API_KEY')
    folder_id = os.getenv('YANDEX_FOLDER_ID')

    if not api_key or not folder_id:
        print("❌ Ошибка: Не найдены API ключи")
        print("Создайте файл .env и добавьте:")
        print("  YANDEX_API_KEY=your_api_key")
        print("  YANDEX_FOLDER_ID=your_folder_id")
        sys.exit(1)

    # Проверка входного пути
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Ошибка: Путь не найден: {args.input}")
        sys.exit(1)

    # Инициализация транскрибера
    print("🔧 Инициализация Yandex SpeechKit...")
    transcriber = WhatsAppTranscriber(
        api_key=api_key,
        folder_id=folder_id,
        verbose=args.verbose
    )

    # Обработка
    try:
        if input_path.is_file():
            print(f"\n📁 Обработка файла: {input_path.name}")
            results = transcriber.transcribe_file(str(input_path))
            results = {
                'total_files': 1,
                'successful': 1 if results['status'] == 'success' else 0,
                'failed': 0 if results['status'] == 'success' else 1,
                'total_duration_seconds': results['duration_seconds'],
                'estimated_cost_rubles': results['duration_seconds'] * 0.2 / 60,
                'transcriptions': [results]
            }
        else:
            print(f"\n📁 Обработка папки: {input_path}")
            results = transcriber.transcribe_folder(str(input_path))

        # Сохранение результатов
        output_path = Path(args.output)

        # JSON всегда сохраняем
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n✅ JSON сохранен: {output_path}")

        # Дополнительные форматы
        if args.format == 'csv':
            export_to_csv(results, str(output_path))
        elif args.format == 'txt':
            export_to_txt(results, str(output_path))

        # Вывод итоговой статистики
        print_summary(results, args.verbose)

        # Бизнес-аналитика
        if results['transcriptions']:
            print("\n" + "="*60)
            print("АНАЛИЗ ЗАПРОСОВ")
            print("="*60)

            keywords = {
                'экскурсии': ['экскурсия', 'тур', 'сафари'],
                'билеты': ['билет', 'парк', 'достопримечательность'],
                'яхты': ['яхта', 'круиз', 'корабль'],
                'аренда авто': ['аренда', 'машина', 'авто', 'автомобиль'],
                'цены': ['стоимость', 'цена', 'сколько стоит', 'прайс']
            }

            categories = {cat: 0 for cat in keywords}

            for item in results['transcriptions']:
                text_lower = item['text'].lower()
                for category, words in keywords.items():
                    if any(word in text_lower for word in words):
                        categories[category] += 1

            print("\nКатегории запросов:")
            for category, count in categories.items():
                if count > 0:
                    print(f"  {category.capitalize()}: {count}")

        print("\n" + "="*60)
        print("✅ Обработка завершена успешно!")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\n⚠️  Обработка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
