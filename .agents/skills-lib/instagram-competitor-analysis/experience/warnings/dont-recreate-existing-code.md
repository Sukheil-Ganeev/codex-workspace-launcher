# Warning: Don't Recreate Existing Code

**Severity:** HIGH
**Частота нарушения:** Medium (если не проверить)

## Проблема

Тратить 30-60 минут на написание кода который УЖЕ существует в `D:/Downloads/instagram_competitor_analysis/`

## Правило

**ПЕРЕД написанием любого кода:**
```bash
# Проверить существует ли проект
ls "D:/Downloads/instagram_competitor_analysis/"
```

**Если проект существует:**
→ Point user to specific folder
→ НЕ recreate from scratch

## Что есть в проекте

```
D:/Downloads/instagram_competitor_analysis/
├── approach_1_instaloader/
│   ├── instagram_analyzer.py      # 300+ строк готового кода
│   ├── config.json                # Шаблон настроек
│   ├── requirements.txt           # Python зависимости
│   └── run.bat                    # Windows автозапуск
│
├── approach_2_cloud_services/
│   └── apify/
│       ├── api_client.py          # 250+ строк API клиента
│       └── config.json            # Apify конфигурация
│
└── approach_3_full_automation/
    ├── claude_api/
    │   ├── analyzer.py            # 200+ строк AI analyzer
    │   └── prompts.json           # Claude промпты
    └── telegram_bot/
        └── report_template.md     # Telegram отчёт шаблон
```

## Примеры

### ❌ Wrong (recreate):

```
User: "Помоги написать Python скрипт для сбора Instagram постов"

Agent: [Starts writing new script from scratch]
```

### ✅ Right (reference existing):

```
User: "Помоги написать Python скрипт для сбора Instagram постов"

Agent: "У вас уже есть готовое решение!

Проверяю...
✓ Найден проект: D:/Downloads/instagram_competitor_analysis/

Готовый скрипт здесь:
→ approach_1_instaloader/instagram_analyzer.py

Что нужно сделать:
1. Открыть config.json
2. Указать ваш Instagram username/password
3. Добавить список конкурентов
4. Запустить: python instagram_analyzer.py

Помочь с настройкой?"
```

## Когда всё же писать новый код

**ТОЛЬКО если:**
- Проект не существует (проверили через ls)
- Существующий код НЕ подходит (другой use case)
- User явно просит "новое решение" (и объяснил почему)

## Чеклист

Перед написанием кода:
- [ ] Проверил существование проекта
- [ ] Проверил все 3 approach папки
- [ ] Если код есть → показал user путь к файлу
- [ ] Если кода нет → OK писать новый

## Экономия времени

**Recreate:** 30-60 мин написания кода
**Reference existing:** 2-3 мин показать путь к файлу

**ROI:** 10-20x время экономии

## См. также

- `SKILL.md` → Integration with Existing Project section
- `README.md` → Project structure
