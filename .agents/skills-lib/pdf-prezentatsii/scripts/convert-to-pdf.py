#!/usr/bin/env python3
"""
Конвертация HTML → PDF через Playwright.

Использование:
    python convert-to-pdf.py input.html output.pdf [--format 16:9|4:3|a4]

Примеры:
    python convert-to-pdf.py presentation.html output.pdf
    python convert-to-pdf.py presentation.html output.pdf --format a4
    python convert-to-pdf.py presentation.html output.pdf -f 16:9-4k
"""

import argparse
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright не установлен!")
    print("Установите: pip install playwright && playwright install chromium")
    sys.exit(1)

# Доступные форматы
FORMATS = {
    '16:9': {'width': '1920px', 'height': '1080px'},
    '16:9-4k': {'width': '3840px', 'height': '2160px'},
    '4:3': {'width': '1440px', 'height': '1080px'},
    'a4': {'format': 'A4', 'landscape': True},
    'a4-portrait': {'format': 'A4', 'landscape': False},
}


def html_to_pdf(html_path: str, pdf_path: str, format_name: str = '16:9') -> bool:
    """
    Конвертирует HTML файл в PDF.

    Args:
        html_path: Путь к HTML файлу
        pdf_path: Путь для сохранения PDF
        format_name: Название формата (16:9, 4:3, a4, etc.)

    Returns:
        True если успешно, False при ошибке
    """
    html_file = Path(html_path).resolve()

    if not html_file.exists():
        print(f"Ошибка: Файл не найден: {html_file}")
        return False

    settings = FORMATS.get(format_name.lower(), FORMATS['16:9'])
    print(f"Конвертация: {html_file.name}")
    print(f"Формат: {format_name}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            # Загрузка HTML (file:/// для локальных файлов)
            page.goto(f'file:///{html_file}')

            # Ждать загрузки ресурсов (шрифты, изображения)
            page.wait_for_load_state('networkidle')

            # Конвертация в PDF
            page.pdf(
                path=pdf_path,
                print_background=True,  # КРИТИЧНО для фона!
                margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'},
                **settings
            )

            browser.close()

        # Информация о результате
        pdf_file = Path(pdf_path)
        size_mb = pdf_file.stat().st_size / (1024 * 1024)
        print(f"Создан: {pdf_file.resolve()} ({size_mb:.2f} МБ)")
        return True

    except Exception as e:
        print(f"Ошибка конвертации: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Конвертация HTML презентаций в PDF через Playwright',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Форматы:
  16:9        1920x1080px (по умолчанию, для экранов/проекторов)
  16:9-4k     3840x2160px (высокое разрешение)
  4:3         1440x1080px (старые проекторы)
  a4          A4 альбомная (для печати)
  a4-portrait A4 портретная (документы)

Примеры:
  python convert-to-pdf.py slides.html slides.pdf
  python convert-to-pdf.py slides.html slides.pdf --format a4
        '''
    )

    parser.add_argument('input', help='HTML файл для конвертации')
    parser.add_argument('output', help='Путь для сохранения PDF')
    parser.add_argument(
        '--format', '-f',
        choices=list(FORMATS.keys()),
        default='16:9',
        help='Формат презентации (по умолчанию: 16:9)'
    )

    args = parser.parse_args()

    success = html_to_pdf(args.input, args.output, args.format)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
