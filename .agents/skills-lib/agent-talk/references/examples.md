---
name: agent-talk-examples
description: Примеры естественных команд и их перевод в tmux-bridge
---

# Примеры использования Agent Talk

## Базовые примеры

### Пользователь: "codex: проверь этот код"

Claude выполняет:
```bash
tmux-bridge list                    # проверить что codex есть
tmux-bridge read codex 20           # прочитать состояние
tmux-bridge message codex "Review the code in the current directory and report any issues or improvements"
tmux-bridge read codex 5            # проверить доставку
tmux-bridge keys codex Enter        # отправить
```

Claude отвечает: "Отправил кодексу задачу на ревью кода. Ответ придёт сюда."

---

### Пользователь: "спроси кодекс что с тестами"

Claude выполняет:
```bash
tmux-bridge read codex 20
tmux-bridge message codex "What is the current test coverage? Run tests and report results."
tmux-bridge read codex 5
tmux-bridge keys codex Enter
```

Claude отвечает: "Спросил кодекс про тесты. Жди ответ."

---

### Пользователь: "что делает codex?"

Claude выполняет:
```bash
tmux-bridge read codex 30
```

Claude интерпретирует вывод и отвечает:
- "Codex свободен — ждёт ввода"
- "Codex работает — пишет файл auth.ts"
- "Codex спрашивает разрешение на запись файла"

---

### Пользователь: "стоп кодекс" или "останови кодекс"

Claude выполняет:
```bash
tmux-bridge read codex 5
tmux-bridge keys codex C-c
```

Claude отвечает: "Отправил Ctrl+C в панель кодекса."

---

### Пользователь: "напиши всем проверить свои тесты"

Claude выполняет для каждого агента из tmux-bridge list:
```bash
# для codex
tmux-bridge read codex 20
tmux-bridge message codex "Run your tests and report results"
tmux-bridge read codex 5
tmux-bridge keys codex Enter

# для gemini
tmux-bridge read gemini 20
tmux-bridge message gemini "Run your tests and report results"
tmux-bridge read gemini 5
tmux-bridge keys gemini Enter
```

---

## Перевод русских команд в English

| Русский запрос | English сообщение агенту |
|---|---|
| проверь код | Review the code and report issues |
| сделай ревью | Do a code review and provide feedback |
| что с тестами | Run tests and report coverage and failures |
| исправь баг | Fix the bug and explain what you changed |
| напиши тесты | Write tests for the current module |
| оптимизируй | Optimize for performance and explain changes |
| объясни | Explain how this code works |
| рефакторинг | Refactor this code for better readability |

---

## Работа с ответами

Когда в панели Claude появляется:
```
[tmux-bridge from:codex pane:%5 at:1:0.1] Test coverage is 87%. Missing tests for OAuth refresh token handler.
```

Claude показывает пользователю:
"Кодекс ответил: покрытие тестами 87%. Не хватает тестов для OAuth refresh token handler."

И спрашивает: "Хочешь чтобы я попросил его написать недостающие тесты?"
