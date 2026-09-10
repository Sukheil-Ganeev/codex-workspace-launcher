# Codex Workspace Launcher

[![test](https://github.com/Sukheil-Ganeev/codex-workspace-launcher/actions/workflows/test.yml/badge.svg)](https://github.com/Sukheil-Ganeev/codex-workspace-launcher/actions)

Выбери проект — и нужный AI-инструмент (Codex, Claude, Muse, Qwen и другие)
откроется сразу в папке этого проекта, с выбранным режимом запуска.

Работает одинаково на **macOS, Linux и Windows**. Только Python 3.8+,
без внешних зависимостей. Каждый коммит автоматически проверяется тестами
на настоящих macOS, Linux и Windows машинах (GitHub Actions).

## Пикер

`codex-workspace pick` открывает в браузере красивую локальную страницу:

- слева — твои проекты с поиском и статусом каждого (готово / папка не найдена);
- справа — все AI-инструменты с версиями и доступностью (CLI / приложение);
- три режима запуска: **Обычный · Без песочницы · Полные права (YOLO)**;
- одна кнопка «Запустить» — инструмент открывается в терминале в папке проекта.

Страница живёт только у тебя на компьютере (127.0.0.1), с одноразовым
токеном в ссылке — другие сайты не могут запустить ничего от твоего имени.
Когда вкладку закрываешь, сервер сам завершается.

Для терминала без браузера есть текстовый пикер: `codex-workspace pick --cli`.

## Установка

| Система | Команда |
|---------|---------|
| macOS   | `bash install/macos-install.sh` |
| Linux   | `bash install/linux-install.sh` |
| Windows | двойной клик по `install\windows-install.bat` |

После установки доступна команда `codex-workspace`. Или запускай напрямую:

```bash
python3 launcher.py pick
```

## Команды

```bash
codex-workspace pick                       # интерактивный пикер (веб)
codex-workspace pick --cli                 # пикер в терминале
codex-workspace list                       # проекты со статусом
codex-workspace list --json                # то же в JSON
codex-workspace add /путь/к/проекту --label "Имя"
codex-workspace rename <id> "Новое имя"    # можно короткий id
codex-workspace remove <id>
codex-workspace open <id>                  # открыть напрямую
codex-workspace open <id> --tool claude --mode safe
codex-workspace open <id> --tool muse --mode yolo --dry-run   # показать план
codex-workspace tools                      # все инструменты с версиями
codex-workspace doctor                     # проверка здоровья проектов
codex-workspace catalog --json             # проекты + инструменты одним документом
```

### Автоподхват проектов

Не хочешь добавлять проекты по одному — укажи родительские папки, лаунчер
сам найдёт все подпапки:

```bash
export CODEX_WORKSPACE_ROOTS=/Users/you/projects:/Users/you/work   # macOS/Linux
set CODEX_WORKSPACE_ROOTS=C:\projects;D:\work                      # Windows
```

## Инструменты

Определяются автоматически (запускается настоящий `--version`):

| CLI-агенты | Приложения (macOS) |
|---|---|
| Codex, Claude, Muse, Qwen, Grok, OpenCode, Gemini, Copilot | Codex App, Claude App |

Если инструмент установлен — он показан как готовый с версией; если нет —
виден в списке с причиной, и запустить его нельзя.

## Режимы запуска

| Режим | Что делает |
|---|---|
| `safe` | обычный запуск инструмента |
| `free` | песочница снята, подтверждения остаются |
| `yolo` | полные права, без подтверждений (осторожно) |

## Как это устроено

```
codex-workspace pick
  → локальная страница (проекты + инструменты + режимы)
  → POST /api/launch (проверка токена и статусов)
  → план запуска: macOS (Terminal.app / iTerm2) · Linux (gnome-terminal /
    kitty / alacritty / wezterm) · Windows (Windows Terminal)
  → инструмент открыт в папке проекта
```

Проекты и настройки хранятся в маленьком JSON-файле в твоём профиле
(пути — только у тебя на машине). Ничего никуда не отправляется.

## Если что-то не работает

| Ситуация | Что делать |
|---|---|
| «Python не найден» | macOS: `brew install python` · Linux: `apt install python3` · Windows: python.org (галочка «Add to PATH») |
| На macOS команда `codex-workspace` не находится | Открой новый терминал (PATH обновился при установке) или проверь строку в `~/.zprofile` |
| macOS: хочу iTerm2 вместо Terminal | Установи iTerm2 — пикер сам его найдёт. Или `export CODEX_TERMINAL=iTerm2` |
| Linux без графики (сервер) | Терминал не найдётся — укажи свой: `export CODEX_TERMINAL=/путь/к/терминалу` |
| Windows: нет Windows Terminal | Откроется обычное окно консоли (cmd) — всё работает |
| Инструмент в списке, но «не запускается» | Он установлен, но сломан. Проверь: `codex-workspace doctor` |
| Инструмента нет в списке | Установи его, и он появится (список строится по реальным программам) |
| Пикер не открылся в браузере | Он печатает ссылку в терминале — открой её вручную. Или `codex-workspace pick --cli` |
| Хочу всё удалить | macOS: `install/macos-uninstall.sh` · Linux: `install/linux-uninstall.sh` · Windows: `install\windows-uninstall.bat` |

## Настройка с нуля через Codex

Хочешь, чтобы всё поставил Codex автоматически? Открой
[`SETUP-PROMPT.md`](SETUP-PROMPT.md) и вставь готовый промт в Codex.

## Структура

```
launcher.py      — CLI (pick, list, add, open, tools, doctor, catalog)
cwl/             — ядро: реестр, инструменты, планы запуска, пикер
install/         — установка под macOS / Linux / Windows
SETUP-PROMPT.md  — промт для Codex
```

## Лицензия

MIT — смотри [`LICENSE`](LICENSE).
