ДАННЫЕ АКТУАЛЬНЫ НА: 2026-02-16

# Troubleshooting: Claude in Chrome + Extensions

## Сводная таблица ошибок

| # | Ошибка / Проблема | Причина | Решение | Серьезность |
|---|-------------------|---------|---------|-------------|
| 1 | "Browser extension is not connected" | Native messaging host не достигает расширения | Перезапустить Chrome + Claude Code, `/chrome` → reconnect | Критическая |
| 2 | "Extension not detected" | Расширение не установлено / отключено | Установить/включить в `chrome://extensions`, перезапустить Chrome | Критическая |
| 3 | "No tab available" | Claude действовал до готовности вкладки | `tabs_create_mcp(url="about:blank")` | Средняя |
| 4 | "Receiving end does not exist" | Service worker заснул (~30 сек idle, Chrome MV3) | `/chrome` → "Reconnect extension" | Высокая |
| 5 | Named pipe EADDRINUSE (Windows) | Конфликт процессов за один named pipe | Закрыть другие сессии Claude Code, перезапустить | Высокая |
| 6 | Native messaging host crashes (Win) | Поврежденная конфигурация host | Переустановить Claude Code для регенерации | Средняя |
| 7 | Named pipe не создается (Win) | Extension не инициирует native messaging | Проверить registry, перезапустить Chrome, расширение >= 1.0.36 | Средняя |
| 8 | Cowork + Code конфликт | Два native host для одного extension ID (fcoeoab...) | Отключить native host неиспользуемого приложения | Критическая |
| 9 | Конфликт Chrome-профилей | Расширение в нескольких профилях = конфликт сокетов | Расширение только в 1 профиле | Высокая |
| 10 | Конфликт сессий Claude Code | Несколько сессий с --chrome | Работать с одной сессией, `/mcp` после закрытия других | Высокая |
| 11 | Ctrl+Shift+M вводит "m" | Баг перехвата горячей клавиши в PuzzleBot | Кнопка `</>` на панели вместо шортката | Специфическая |
| 12 | {{переменные}} ломаются | PuzzleBot span-elements при посимвольном вводе | innerHTML injection через JS | Специфическая |
| 13 | Alert блокирует расширение | JS alert/confirm/prompt блокируют browser events | Не использовать alert(); dismiss вручную; DevTools: handle_dialog | Критическая |
| 14 | Координаты кнопки "плавают" | Floating toolbar позиционируется по выделению | Screenshot перед КАЖДЫМ кликом по панели | Средняя |
| 15 | Страница не загрузилась | Действие до полной загрузки | Таймаут в промпте, retry, DevTools: wait_for | Средняя |
| 16 | Tab ID невалиден | ID из прошлой сессии | `tabs_context_mcp` для свежих ID | Средняя |
| 17 | MCP tools не загружаются | Version mismatch, баг конфигурации | `claude doctor`, `--mcp-debug`, `claude mcp list` | Критическая |
| 18 | Tab groups накапливаются | Не удаляются после сессии Claude Code | Закрывать вручную: правый клик → Close group | Низкая |
| 19 | Claude уходит в rabbit hole | Бесконечные retry одного подхода | Остановить вручную, дать новое направление. Правило 2-3 попыток | Средняя |
| 20 | Страница перенаправляет неожиданно | Redirect после действия | Проверить URL после navigate, retry если нужно | Средняя |

## Подробные решения

### "Browser extension is not connected" — чеклист

1. Chrome запущен?
2. Расширение включено? (`chrome://extensions`)
3. Версия расширения >= 1.0.36?
4. Версия Claude Code >= 2.0.73? (`claude --version`)
5. Только одна сессия Claude Code с Chrome?
6. Нет конфликта с Claude Desktop Cowork?
7. Один Chrome-профиль с расширением?
8. Проверить native messaging host:
   - **Windows Chrome:** `HKCU\Software\Google\Chrome\NativeMessagingHosts\com.anthropic.claude_code_browser_extension`
   - **Windows Edge:** `HKCU\Software\Microsoft\Edge\NativeMessagingHosts\com.anthropic.claude_code_browser_extension`
   - **macOS Chrome:** `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json`
   - **Linux Chrome:** `~/.config/google-chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json`

### Конфликт Claude Desktop Cowork и Claude Code

**Симптомы:** Все выглядит работающим — расширение установлено, native host запущен, сокет существует — но "Browser extension is not connected".

**Причина:** Claude Desktop Cowork и Claude Code регистрируют native messaging host для ОДНОГО extension ID (`fcoeoabgfenejglbffodgkkbkcdhcgfn`), но используют несовместимые форматы сокетов.

**Решение macOS:**
```bash
mv ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_browser_extension.json \
   ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_browser_extension.json.disabled
# ОБЯЗАТЕЛЬНО перезапустить Chrome и Claude Code!
```

**Решение Windows:** Найти конфликтующий ключ в реестре и переименовать для неиспользуемого приложения.

### Anti-rabbit-hole паттерн

```
Попытка 1: Основной подход
  ↓ (не сработало)
Попытка 2: Альтернативный подход
  ↓ (не сработало)
Попытка 3: Еще один подход
  ↓ (не сработало)
СТОП → Отчет пользователю:
  - Что пытался
  - Что не получилось
  - Варианты дальнейших действий
```

### Диагностические команды

```bash
claude doctor                  # общая проверка установки
claude doctor --verbose        # детальное логирование
claude doctor --mcp-debug      # диагностика MCP-серверов
claude mcp list                # проверка подключенных серверов
/chrome                        # переподключение / статус
/mcp                           # список MCP и их статус
```

## Проблемы с вводом в web-редакторах

| Проблема | Причина | Решение |
|----------|---------|---------|
| `form_input` не работает | contenteditable элементы | `javascript_tool` (innerHTML injection) |
| Текст вставляется без форматирования | `computer(type)` не сохраняет HTML | innerHTML injection |
| {{переменные}} ломаются | PuzzleBot span-elements | innerHTML injection с полной HTML-структурой |
| Ctrl+Shift+M = "m" | Баг PuzzleBot | Кнопка `</>` через screenshot + click |
| Панель форматирования "плавает" | Floating toolbar | Screenshot перед каждым кликом |
| Emoji ломают выделение | Selection API не учитывает emoji | Контроль через indexOf + length |

## Windows-специфические проблемы

| Проблема | Причина | Решение |
|----------|---------|---------|
| EADDRINUSE | Named pipe конфликт | Закрыть все сессии Claude Code, перезапустить |
| Native host crash | Поврежденный config | Переустановить Claude Code |
| Named pipe не создается | Extension не инициирует connection | Проверить registry, перезапустить Chrome |
| Реестр NativeMessagingHosts | Неверный путь | Проверить `HKCU\Software\Google\Chrome\NativeMessagingHosts\` |

## Office Add-in проблемы

| Проблема | Решение |
|----------|---------|
| Add-in не появляется в Excel | Insert → Get Add-ins → поиск "Claude by Anthropic" |
| Sidebar не открывается | Ctrl+Alt+C (Win) / Ctrl+Option+C (Mac) |
| Chat history пропала | Это ожидаемо — history НЕ сохраняется между сессиями. Включите Claude Log Tab |
| PowerPoint недоступен | Проверить план: нужен Max/Team/Enterprise (НЕ Pro) |
| Подозрительная формула | Pop-up подтверждения — это защита от prompt injection |
