# Platform Format Matrix

Дата: 2026-05-22

## Главный принцип

Canonical source должен быть один: нормальная skill-папка с `SKILL.md`, `references/`, `scripts/`, `assets/`, `agents/`. Остальные платформы получают adapter/projection, а не ручную копию без учета происхождения.

## Codex

- Глобальный путь: `C:\Users\londo\.codex\skills\<skill>\SKILL.md`
- Плагины: `C:\Users\londo\plugins\<plugin>\.codex-plugin\plugin.json`
- Marketplace: `C:\Users\londo\.agents\plugins\marketplace.json`
- Важный trigger: frontmatter `description`.
- После установки новых skills лучше перезапустить Codex или открыть свежий чат.

## Claude

- Глобальный путь: `C:\Users\londo\.claude\skills\<skill>\SKILL.md`
- Формат близок к Codex: `SKILL.md` с frontmatter.
- Лучше держать body компактным, подробности выносить в `references/`.

## Gemini

- Skills mirror: `C:\Users\londo\.gemini\skills\<skill>\SKILL.md`
- Практичный command wrapper: `C:\Users\londo\.gemini\commands\<namespace>\<command>.toml`
- TOML должен иметь `prompt`, опционально `description`.
- После изменения команд: `/commands reload`.

## Cursor

- Использовать как future adapter target.
- Сейчас безопаснее хранить инструкции как markdown/rules/commands отдельно, не смешивая с canonical skill.

## Grok

- Использовать как future adapter target.
- Пока держать `references/grok-port-notes.md` или отдельный prompt-pack, потому что единый локальный skill format не подтвержден.

## OpenClaw / Hermes

- Считать mirror/runtime projection, а не главным источником.
- При большой библиотеке проверять лимиты discovery и registry health.
- Не редактировать runtime projection вручную, если есть canonical source.
