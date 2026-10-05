# EXP-072: Function parameter name colliding with template placeholder kwargs

- **Дата:** 2026-03-01
- **Severity:** high
- **Тип:** warning
- **Проект:** VIP-DXB-CatalogBot (7 platforms, Python)

## Проблема
Функция `t(key, lang, **kwargs)` принимает `lang` как позиционный параметр. Locale JSON содержит шаблон `{lang}` как placeholder для отображения языка. Вызов:
```python
t('lang.changed', lang, lang=lang_display)
```
передаёт `lang` дважды — как позиционный аргумент И как keyword аргумент. Python выбрасывает:
```
TypeError: t() got multiple values for argument 'lang'
```

## Почему опасно
- Ошибка не видна при чтении кода — выглядит корректно
- Тесты могут не покрывать конкретный locale key с placeholder `{lang}`
- Функция работает для ВСЕХ ключей без `{lang}` в шаблоне — баг проявляется только при определённых ключах

## Корневая причина
Имя параметра функции (`lang`) совпало с именем placeholder в шаблоне (`{lang}`). При попытке передать значение для placeholder через `**kwargs`, Python интерпретирует это как повторную передачу позиционного параметра.

## Правило
НИКОГДА не использовать одинаковые имена для:
1. Параметров функции (`def t(key, lang, **kwargs)`)
2. Placeholder-ов в template strings (`{lang}`)

**Решения:**
- Переименовать параметр: `def t(key, lang_code, **kwargs)` — тогда `t('key', lang_code, lang=display_name)` работает
- Переименовать placeholder: `{language}` вместо `{lang}` в locale JSON
- Передавать через промежуточный dict: `t('key', lang, **{"lang": display_name})` — НЕ решает проблему, та же ошибка

## Grep-паттерн для аудита
```bash
# Найти все placeholders в locale файлах
grep -oP '\{(\w+)\}' locales/*.json | sort -u

# Сравнить с параметрами функции t()
grep -n "def t(" */i18n.py core/i18n.py
```

Если пересечение найдено — это потенциальный баг.

## times_applied: 1
