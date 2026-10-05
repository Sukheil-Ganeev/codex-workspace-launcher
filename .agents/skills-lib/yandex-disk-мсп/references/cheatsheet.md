# Cheatsheet — Яндекс Диск MCP

## Быстрые команды MCP

| Задача | Инструмент | Параметры |
|--------|-----------|-----------|
| Инфо о диске | `yandex_disk_info` | — |
| Содержимое папки | `yandex_disk_get_metadata` | `path="disk:/путь/"` |
| Содержимое с пагинацией | `yandex_disk_get_metadata` | `path`, `limit=20`, `offset=0` |
| Список всех файлов | `yandex_disk_list_files` | `limit=100`, `offset=0` |
| Ссылка на скачивание | `yandex_disk_get_download_url` | `path="disk:/путь/файл.jpg"` |
| Ссылка на загрузку | `yandex_disk_get_upload_url` | `path="disk:/путь/новый.jpg"` |
| Создать папку | `yandex_disk_create_folder` | `path="disk:/новая_папка/"` |
| Копировать | `yandex_disk_copy` | `from_path`, `to_path` |
| Переместить | `yandex_disk_move` | `from_path`, `to_path` |
| Удалить | `yandex_disk_delete` | `path` |

## Шаблоны путей

### CRM ОАЭ
```
disk:/CRM системы стран/CRM система (ОАЭ)/БИЛЕТЫ/{название_аттракциона}/
disk:/CRM системы стран/CRM система (ОАЭ)/ГРУППОВЫЕ ЭКСКУРСИИ/{название}/
disk:/CRM системы стран/CRM система (ОАЭ)/ИНДИВИДУАЛЬНЫЕ ЭКСКУРСИИ/{название}/
disk:/CRM системы стран/CRM система (ОАЭ)/ОТЕЛИ/
```

### Яхты
```
disk:/Яхты для PDF/{НАЗВАНИЕ ЯХТЫ} {ДЛИНА} FEET/
disk:/Яхты для PDF/ASTRA 80 FEET/Astra Exterior 1.JPG
disk:/Яхты для PDF/ASTRA 80 FEET/Astra Deck 1.JPG
disk:/Яхты для PDF/ASTRA 80 FEET/Astra Interior 1.JPG
disk:/Яхты (общая папка)/
```

### Машины
```
disk:/Машины PDF/
```

### Брендинг
```
disk:/фирменный стиль Дубаи/
disk:/фирменный стиль Дубаи/Instagram/    # ОСТОРОЖНО: иконки, не фото!
```

### Другие
```
disk:/Загрузки/                            # VK обложки
disk:/CRM системы стран/                   # 81 папка по странам
```

## Типичные сценарии

### Скачать фото для презентации
```
1. get_metadata("disk:/CRM системы стран/CRM система (ОАЭ)/БИЛЕТЫ/")
2. get_metadata("disk:/CRM системы стран/CRM система (ОАЭ)/БИЛЕТЫ/Burj Khalifa/")
3. get_download_url("disk:/CRM системы стран/.../burj_khalifa_01.jpg")
4. curl -L -o "D:/Downloads/Skill_Presentations/images/burj_khalifa.jpg" "URL"
```

### Найти фото яхты (Exterior)
```
1. get_metadata("disk:/Яхты для PDF/")           # список всех яхт
2. get_metadata("disk:/Яхты для PDF/ASTRA 80 FEET/")  # файлы конкретной яхты
3. Ищи файл с "Exterior" в имени
4. get_download_url("disk:/Яхты для PDF/ASTRA 80 FEET/Astra Exterior 1.JPG")
5. curl -L -o "D:/Downloads/yacht_astra.jpg" "URL"
```

### Обзор всех экскурсий
```
1. get_metadata("disk:/CRM системы стран/CRM система (ОАЭ)/ГРУППОВЫЕ ЭКСКУРСИИ/")
2. get_metadata("disk:/CRM системы стран/CRM система (ОАЭ)/ИНДИВИДУАЛЬНЫЕ ЭКСКУРСИИ/")
```

## Python-сниппеты

### Парсинг большого JSON метаданных из temp-файла
```python
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def parse_disk_metadata(filepath):
    """Парсит temp-файл с метаданными Яндекс Диска.

    Формат temp-файла: [{type: "text", text: "json_string"}]
    Внутренний JSON содержит _embedded.items — список файлов/папок.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = json.load(f)

    text_content = raw[0]['text']
    data = json.loads(text_content)
    items = data['_embedded']['items']

    return items


def print_items_table(items):
    """Выводит список элементов в виде таблицы."""
    dirs = [i for i in items if i['type'] == 'dir']
    files = [i for i in items if i['type'] == 'file']

    print(f"Папок: {len(dirs)}, Файлов: {len(files)}\n")

    for item in dirs:
        print(f"  [DIR]  {item['name']}")

    for item in files:
        size_mb = item.get('size', 0) / 1024 / 1024
        print(f"  [FILE] {item['name']}  ({size_mb:.1f} MB)")


def filter_by_name(items, keyword):
    """Фильтрует элементы по ключевому слову в имени."""
    keyword_lower = keyword.lower()
    return [i for i in items if keyword_lower in i['name'].lower()]


# Использование:
# items = parse_disk_metadata('temp_metadata.json')
# print_items_table(items)
# exteriors = filter_by_name(items, 'exterior')
```

### Пакетное скачивание файлов
```python
import subprocess
import time

def download_file(url, local_path):
    """Скачивает файл через curl."""
    result = subprocess.run(
        ['curl', '-L', '-o', local_path, url],
        capture_output=True, text=True
    )
    return result.returncode == 0

# Между скачиваниями делай паузу, чтобы не нагружать API
# time.sleep(1)
```

### Поиск файлов по паттерну в имени
```python
def find_files_by_pattern(items, patterns):
    """Ищет файлы, содержащие любой из паттернов в имени.

    patterns: ['exterior', 'front', 'outside']
    """
    results = []
    for item in items:
        if item['type'] != 'file':
            continue
        name_lower = item['name'].lower()
        for pattern in patterns:
            if pattern.lower() in name_lower:
                results.append(item)
                break
    return results
```

## Памятка по именованию фото яхт

| Ключевое слово в имени | Что на фото | Когда использовать |
|------------------------|------------|-------------------|
| `Exterior` | Внешний вид яхты | Каталоги, карточки, обложки |
| `Deck` | Палуба, зоны отдыха | Описание удобств |
| `Interior` | Салон, каюты | Описание комфорта |

## Размеры файлов (ориентир)

| Тип | Размер | Формат |
|-----|--------|--------|
| Фото яхт (HD) | ~3.5 MB | JPG |
| Topaz-sharpen | ~1-2 MB | JPEG |
| Topaz-upscale-2x | ~1.7 MB | PNG |
| Иконки Instagram | ~50-200 KB | JPG |
| Фото из мессенджеров | ~100-500 KB | JPG |
