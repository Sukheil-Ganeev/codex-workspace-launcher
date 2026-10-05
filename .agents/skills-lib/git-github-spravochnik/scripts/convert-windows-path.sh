#!/bin/bash
# Windows Path Converter for Git Bash
# Конвертирует Windows пути (D:\folder\file) в Git Bash формат (/d/folder/file)
#
# Использование:
#   ./convert-windows-path.sh "D:\Downloads\project"
#   ./convert-windows-path.sh "C:\Users\londo\Documents"
#
# Результат выводится в stdout, можно использовать в других командах:
#   cd $(./convert-windows-path.sh "D:\Downloads\project")

# Проверка наличия аргумента
if [ -z "$1" ]; then
    echo "Ошибка: не указан путь для конвертации" >&2
    echo "Использование: $0 \"D:\\Downloads\\project\"" >&2
    exit 1
fi

path="$1"

# Удаление кавычек если они есть
path="${path%\"}"
path="${path#\"}"

# Проверка что путь похож на Windows путь (содержит :\ или :/)
if [[ ! "$path" =~ ^[A-Za-z]:[/\\] ]]; then
    echo "Ошибка: путь не похож на Windows путь (должен начинаться с C:\\ или D:\\ и т.д.)" >&2
    echo "Получен: $path" >&2
    exit 1
fi

# Извлечение буквы диска (первый символ)
drive_letter="${path:0:1}"
# Перевод в нижний регистр
drive_letter=$(echo "$drive_letter" | tr '[:upper:]' '[:lower:]')

# Удаление буквы диска и двоеточия из пути
rest_of_path="${path:2}"

# Замена обратных слешей на прямые
rest_of_path="${rest_of_path//\\//}"

# Удаление начального слеша если он есть (чтобы не получилось /d//folder)
rest_of_path="${rest_of_path#/}"

# Формирование финального пути
if [ -z "$rest_of_path" ]; then
    # Если путь был просто "D:\", результат будет "/d"
    result="/$drive_letter"
else
    result="/$drive_letter/$rest_of_path"
fi

# Вывод результата
echo "$result"

# Опционально: вывод команды cd для удобства
if [ "$2" = "--cd" ]; then
    echo "cd \"$result\""
fi
