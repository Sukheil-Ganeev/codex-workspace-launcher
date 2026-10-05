#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсер VCF (vCard) контактов
"""

import sys
import os
import glob
import re
import argparse

sys.stdout.reconfigure(encoding='utf-8')

def parse_vcf_files(directory, output_file):
    """
    Читает все VCF файлы и извлекает контактные данные
    """
    vcf_files = glob.glob(os.path.join(directory, "*.vcf"))
    print(f"Найдено {len(vcf_files)} VCF файлов")

    results = []

    for filepath in vcf_files:
        filename = os.path.basename(filepath)
        print(f"Обработка: {filename}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(filepath, 'r', encoding='cp1251') as f:
                    content = f.read()
            except:
                results.append(f"=== {filename} ===\n[Ошибка чтения файла]\n")
                continue

        # Парсинг vCard
        name = re.search(r'FN:(.+)', content)
        phone = re.search(r'TEL[^:]*:(.+)', content)
        email = re.search(r'EMAIL[^:]*:(.+)', content)
        org = re.search(r'ORG:(.+)', content)

        contact_info = f"=== {filename} ===\n"
        contact_info += f"Имя: {name.group(1).strip() if name else 'Не указано'}\n"
        contact_info += f"Телефон: {phone.group(1).strip() if phone else 'Не указан'}\n"
        if email:
            contact_info += f"Email: {email.group(1).strip()}\n"
        if org:
            contact_info += f"Организация: {org.group(1).strip()}\n"

        results.append(contact_info)
        print(f"    OK: {name.group(1).strip() if name else filename}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(results))

    print(f"\nРезультаты сохранены в: {output_file}")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Парсинг VCF контактов")
    parser.add_argument("directory", help="Папка с VCF файлами")
    parser.add_argument("-o", "--output", default=None, help="Файл для сохранения")

    args = parser.parse_args()

    output_file = args.output or os.path.join(args.directory, "vcf_analysis.txt")
    parse_vcf_files(args.directory, output_file)
