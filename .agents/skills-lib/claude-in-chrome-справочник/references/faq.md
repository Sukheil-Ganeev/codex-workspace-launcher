ДАННЫЕ АКТУАЛЬНЫ НА: 2026-02-16

# FAQ: Claude in Chrome + Excel + PowerPoint

## Общие вопросы

**Q: Какие браузеры поддерживаются?**
A: Google Chrome и Microsoft Edge. НЕ поддерживаются: Brave, Arc, другие Chromium-браузеры, WSL, мобильные устройства.

**Q: Какой минимальный план нужен?**
A: Claude in Chrome и Claude in Excel: Pro ($17-20/мес) и выше. Claude in PowerPoint: Max ($100/мес) и выше (НЕ Pro!).

**Q: Работает ли через Bedrock/Vertex/Foundry?**
A: Нет. Только прямой аккаунт Anthropic (claude.ai). Если доступ только через третью сторону — нужен отдельный claude.ai аккаунт.

**Q: Какие модели доступны на Pro плане?**
A: Chrome: только Haiku 4.5. Excel/PowerPoint: Sonnet 4.5, Opus 4.6. Max/Team/Enterprise: все модели во всех продуктах.

**Q: Что такое Claude in Chrome vs Chrome DevTools MCP?**
A: Claude in Chrome — расширение Anthropic (18 MCP-инструментов), работает с авторизованной сессией браузера. Chrome DevTools MCP — отдельный MCP-сервер от Google (26 инструментов), больше возможностей для отладки и performance. Можно использовать оба одновременно.

## Chrome-расширение

**Q: Как установить?**
A: Chrome Web Store → поиск "Claude" by Anthropic → Add to Chrome → войти в аккаунт → закрепить расширение.

**Q: Как запустить из CLI?**
A: `claude --chrome` или `/chrome` внутри сессии. Для постоянного включения: `/chrome` → "Enabled by default" (но это +19k токенов контекста).

**Q: Почему первый вызов всегда tabs_context_mcp?**
A: Tab ID из предыдущих сессий невалидны. tabs_context_mcp возвращает свежие ID и при необходимости создает tab group.

**Q: Claude может видеть мои пароли и данные?**
A: Claude использует вашу реальную сессию браузера (cookies, логины). Он видит всё, что видите вы. Используйте только с доверенными сайтами.

**Q: Сохраняется ли контекст между сессиями?**
A: Нет. Chrome-расширение НЕ поддерживает Projects, cross-session memory, внешние MCP connections.

**Q: Что такое шорткаты "/"?**
A: Сохраненные промпты, вызываемые через "/" в чате side panel. 3 способа создания: Save Prompt, Convert to Task, Record Workflow.

**Q: Работают ли scheduled tasks когда Chrome закрыт?**
A: Нет. Chrome ДОЛЖЕН быть открыт для выполнения запланированных задач.

**Q: Claude может решать CAPTCHA?**
A: Нет. Claude останавливается и просит пользователя обработать CAPTCHA и страницы авторизации вручную.

## JavaScript и web-редакторы

**Q: Почему нельзя использовать alert() в JS injection?**
A: alert(), confirm(), prompt() блокируют ВСЕ browser events. Расширение "замирает" до ручного dismiss. Используйте console.log().

**Q: Как работать с contenteditable-элементами?**
A: innerHTML injection через javascript_tool (или evaluate_script) — мгновенная вставка HTML. Затем Selection API для выделения + горячие клавиши для форматирования.

**Q: Почему form_input не работает с web-редакторами?**
A: form_input предназначен для стандартных HTML-элементов (input, select, textarea). Web-редакторы (PuzzleBot, Notion, Google Docs) используют contenteditable, с которым form_input не работает.

**Q: Ctrl+Shift+M не работает в PuzzleBot?**
A: Это известный баг — вводит букву "m" вместо моноширинного форматирования. Решение: кнопка `</>` на панели через screenshot + click.

## Office Add-ins

**Q: Сохраняется ли история чата в Excel/PowerPoint?**
A: Нет. Chat history НЕ сохраняется между сессиями. В Excel можно включить Claude Log Tab — отдельный лист с записью всех действий.

**Q: Есть ли audit logs для add-in?**
A: Нет. Add-in НЕ включены в Enterprise audit logs / Compliance API. Data retention настройки Team/Enterprise тоже НЕ наследуются.

**Q: Какие форматы поддерживает Excel add-in?**
A: Только .xlsx и .xlsm. НЕ .xls, НЕ .csv напрямую.

**Q: PowerPoint доступен для Pro?**
A: Нет. PowerPoint add-in в статусе Research Preview доступен только Max ($100/мес), Team, Enterprise.

**Q: Можно ли использовать VBA/макросы с add-in?**
A: Нет. Excel add-in НЕ поддерживает VBA/macros и Data tables.

**Q: Что такое Template Intelligence в PowerPoint?**
A: Claude читает slide master (layouts, fonts, color schemes) и автоматически соблюдает корпоративный брендинг при генерации слайдов.

**Q: В чем разница между add-in и CLI skill?**
A: Add-in — интерактивный sidebar в Excel/PowerPoint, работает с одним файлом. CLI skill — программный подход через Claude Code, batch-обработка, любое количество файлов.

## Безопасность

**Q: Что такое prompt injection?**
A: Скрытые вредоносные инструкции в содержимом страниц, ячеек Excel или слайдов PowerPoint, которые могут заставить Claude выполнить нежелательные действия.

**Q: Как защититься от prompt injection?**
A: Использовать ТОЛЬКО с доверенными файлами и сайтами. Не открывать файлы из внешних источников. В режиме "Ask before acting" Claude показывает план перед выполнением.

**Q: Какие действия всегда требуют подтверждения?**
A: Покупки, публикации, передача персональных данных. В Excel: WEBSERVICE, DDE, IMPORTDATA и другие опасные функции.

## Troubleshooting

**Q: "Browser extension is not connected" — что делать?**
A: Чеклист: (1) Chrome запущен? (2) Расширение включено? (3) Одна сессия Code? (4) Нет конфликта с Cowork? (5) Один Chrome-профиль? → Перезапуск Chrome + Claude Code.

**Q: Claude "завис" — что делать?**
A: Проверить: нет ли JS-диалога (alert/confirm). Если service worker заснул: `/chrome` → Reconnect. Если rabbit hole: остановить и дать новое направление.

**Q: Как использовать Claude Desktop Cowork и Claude Code одновременно?**
A: НЕЛЬЗЯ. Они конфликтуют за один extension ID. Используйте только одно приложение и отключите native host другого.
