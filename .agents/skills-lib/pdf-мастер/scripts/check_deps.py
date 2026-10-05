#!/usr/bin/env python3
"""Проверка установленных зависимостей PDF-мастер стека."""

import importlib
import shutil
import sys

PACKAGES = [
    ("pypdf", "pypdf", "Слияние, разделение, формы"),
    ("fitz", "PyMuPDF", "Быстрое извлечение, рендеринг"),
    ("reportlab", "ReportLab", "Создание сложных PDF"),
    ("fpdf", "fpdf2", "Быстрое создание простых PDF"),
    ("pdfplumber", "pdfplumber", "Извлечение таблиц"),
    ("pikepdf", "pikepdf", "Ремонт, шифрование"),
    ("weasyprint", "WeasyPrint", "HTML → PDF"),
    ("ocrmypdf", "ocrmypdf", "OCR pipeline"),
    ("pyhanko", "pyHanko", "Цифровые подписи"),
    ("img2pdf", "img2pdf", "Изображения → PDF"),
    ("PyPDFForm", "PyPDFForm", "Заполнение форм"),
    ("pypdfium2", "pypdfium2", "Быстрый текст"),
    ("pdfminer", "pdfminer.six", "Глубокий анализ"),
    ("pptx", "python-pptx", "Презентации"),
    ("docx", "python-docx", "Документы Word"),
    ("pdf2docx", "pdf2docx", "PDF → DOCX"),
    ("PIL", "Pillow", "Изображения"),
    ("jinja2", "Jinja2", "Шаблоны"),
    ("svglib", "svglib", "SVG → ReportLab"),
    ("openpyxl", "openpyxl", "Excel"),
    ("qrcode", "qrcode", "QR-коды"),
    ("barcode", "python-barcode", "Штрих-коды"),
]

SYSTEM_DEPS = [
    ("tesseract", "Tesseract OCR", "ocrmypdf, pytesseract"),
    ("gs", "Ghostscript", "ocrmypdf PDF/A, сжатие"),
    ("gswin64c", "Ghostscript (Win64)", "ocrmypdf PDF/A, сжатие"),
    ("libreoffice", "LibreOffice", "DOCX/PPTX → PDF"),
    ("mutool", "MuPDF Tools", "Ремонт PDF"),
]


def check_packages():
    print("=" * 60)
    print("PYTHON ПАКЕТЫ")
    print("=" * 60)

    installed = 0
    missing = []

    for import_name, pip_name, role in PACKAGES:
        try:
            mod = importlib.import_module(import_name)
            doc = getattr(mod, "__doc__", None)
            version = getattr(mod, "__version__", (doc[:30] if doc else "OK"))
            print(f"  ✅ {pip_name:<20} {str(version):<20} {role}")
            installed += 1
        except ImportError:
            print(f"  ❌ {pip_name:<20} {'НЕ УСТАНОВЛЕН':<20} {role}")
            missing.append(pip_name)
        except OSError as e:
            # WeasyPrint без GTK3 падает с OSError, но pip-пакет установлен
            print(f"  ⚠️  {pip_name:<20} {'УСТАНОВЛЕН (нет GTK3)':<20} {role}")
            installed += 1
        except Exception as e:
            print(f"  ⚠️  {pip_name:<20} {str(e)[:20]:<20} {role}")
            installed += 1

    print(f"\n  Установлено: {installed}/{len(PACKAGES)}")
    if missing:
        print(f"  Установить: pip install {' '.join(missing)}")
    return missing


def check_system():
    print("\n" + "=" * 60)
    print("СИСТЕМНЫЕ ЗАВИСИМОСТИ")
    print("=" * 60)

    found = {}
    for cmd, name, role in SYSTEM_DEPS:
        path = shutil.which(cmd)
        if path:
            print(f"  ✅ {name:<25} {path}")
            found[cmd] = True
        else:
            print(f"  ❌ {name:<25} НЕ НАЙДЕН — нужен для: {role}")

    # Проверка GTK3 для WeasyPrint
    print("\n  GTK3 (для WeasyPrint):")
    try:
        from weasyprint import HTML
        HTML(string="<p>test</p>").write_pdf()
        print("  ✅ GTK3/Cairo/Pango работают")
    except Exception as e:
        print(f"  ❌ GTK3 НЕ РАБОТАЕТ: {e}")

    return found


def main():
    print("\n🔍 PDF-мастер: проверка зависимостей\n")
    missing_pkgs = check_packages()
    found_sys = check_system()

    print("\n" + "=" * 60)
    print("ИТОГ")
    print("=" * 60)

    if not missing_pkgs and "tesseract" in found_sys:
        print("  ✅ Стек готов к работе!")
    else:
        if missing_pkgs:
            print(f"  ⚠️  Не хватает {len(missing_pkgs)} Python пакетов")
        if "gs" not in found_sys and "gswin64c" not in found_sys:
            print("  ⚠️  Ghostscript не установлен (OCR PDF/A недоступен)")
        if "tesseract" not in found_sys:
            print("  ⚠️  Tesseract не установлен (OCR недоступен)")
    print()


if __name__ == "__main__":
    main()
