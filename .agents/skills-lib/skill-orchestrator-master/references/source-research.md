# Source Research Notes

Дата: 2026-05-22

## Подтвержденные идеи

- В Codex skills устанавливаются через каталог, после установки нужен restart/fresh session.
- Для Codex `SKILL.md` frontmatter `name` и `description` являются ключевыми полями для выбора skill.
- Gemini CLI custom commands живут в `~/.gemini/commands` и project `.gemini/commands`; имя команды получается из пути файла.
- В больших библиотеках нужен routing/indexing слой, потому что ручной выбор навыков плохо масштабируется.
- Нужно учитывать supply-chain риск: описание навыка влияет на выбор агента, поэтому нельзя слепо доверять неизвестным skills.

## Использованные источники

- OpenAI skills catalog: https://github.com/openai/skills
- OpenAI Codex skill-creator sample: https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md
- Gemini CLI custom commands: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/custom-commands.md
- Agent Skills Kit: https://github.com/jscraik/Agent-Skills
- dotnet-skills multi-agent paths: https://github.com/managedcode/dotnet-skills
- SkillMesh discussion: https://www.reddit.com/r/ClaudeCode/comments/1rkjp2s/skillmesh_retrievalgated_tool_router_for_claude/
- skill-router discussion: https://www.reddit.com/r/ClaudeAI/comments/1tgnt1b/a_skillrouter_so_you_dont_have_to_remember_which/
- SKILL.md supply-chain paper: https://arxiv.org/abs/2605.11418

## Вывод

Лучшее решение для этой машины: один lightweight meta-skill + deterministic index scripts + thematic plugin packs. Не надо пытаться держать полный текст 1000 skills в одном навыке.
