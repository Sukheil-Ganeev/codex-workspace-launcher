---
name: script-writing-guard
description: Use when users ask to write, modify, refactor, optimize, or automate scripts or command-line utilities with meaningful operational risk, especially in PowerShell, Bash, Python, or batch when tasks involve file moves, renames, cleanup, migrations, imports, exports, maintenance jobs, batch operations, or irreversible changes. Also use when a request sounds small but could have outsized side effects, when the agent should first decide Adopt / Extend / Build instead of coding immediately, or when safety boundaries and verification steps must be defined before writing the script.
---

# Script Writing Guard

Use this skill before writing a new script or making a meaningful change to an existing one.

## When to Use

Use this skill when:
- the user asks for a script, utility, automation, or maintenance command;
- the task touches files, folders, names, paths, batch edits, migrations, imports, exports, or cleanup;
- the task could cause accidental overwrites, deletes, or confusing side effects;
- the request sounds simple but the consequences are not simple;
- you need to explain the plan in plain language before coding.

## When NOT to Use

Do not use this skill as the main workflow for:
- a one-line explanation of existing code with no edits;
- pure brainstorming with no script or automation decision yet;
- purely manual steps where the user explicitly does not want automation;
- trivial single-line edits with no file-operation risk and no ambiguity.

For larger product or feature work, pair this skill with a planning or spec workflow instead of letting this skill carry architecture decisions by itself.

## Quick Start

1. Check for project-local instruction files in the current workspace such as `AGENTS.md`, `AGENT.md`, `CLAUDE.md`, or `HOW_TO_WRITE_SCRIPTS.md`.
2. Before coding, explain the situation in plain language using the required template below.
3. Decide whether a new script is truly needed.
4. Define the boundaries: `Always`, `Ask First`, and `Never`.
5. Choose the simplest safe approach that can work.
6. Add preview, dry-run, or small-batch verification before any wider run.
7. Implement the smallest readable solution.
8. Report how to run it, what it changes, and how to verify the result.

## Critical Workflow Stays Inline

Everything needed for the main safety workflow stays in this `SKILL.md`.

Do not move critical instructions such as:
- when to stop and ask;
- how to decide whether a new script is needed;
- how to define risk;
- what must be verified before execution.

Reference files are for optional depth, not for must-do safety steps.

## Why This Skill Exists

Script tasks are dangerous because they often look smaller than they really are.

A short script can still:
- move or rename hundreds of files;
- overwrite existing outputs;
- hide complexity behind "just automate it";
- create confusion if the user cannot easily inspect what it will do.

This skill exists to slow down the risky part, not the useful part.

## Required Output Before Coding

Use this exact structure before implementation:

```text
Проблема:
Вероятная причина:
Что меняю:
Результат:
Риск: LOW / MODERATE / HIGH
Evidence:
Impact:
Action:
```

## Decide If A New Script Is Needed

Before creating or expanding a script, check in this order:

1. Is there already an existing script or command that safely solves the task?
2. Would a tiny edit to an existing script be safer than adding a new one?
3. Would a safe manual step be better than automation for this specific case?
4. Can the task be validated on a tiny sample first?

If the answer suggests "no new script needed," do not create one just because automation feels productive.

## Adopt / Extend / Build

Use this decision order before writing code:

1. **Adopt**
   Reuse an existing safe script, command, or workflow as-is when it already solves the task.
2. **Extend**
   Make the smallest safe change to an existing script when it mostly works and only needs a limited correction.
3. **Build**
   Create a new script only when there is no safe existing path and the workflow is worth automating.

Default preference:

`Adopt` → `Extend` → `Build`

Do not jump to `Build` just because writing a new script feels cleaner.

## Boundaries

Define these boundaries before implementation.

### Always

- Explain the task in plain language first.
- Surface assumptions early instead of hiding them.
- Prefer the simplest workable solution.
- Use clear names, predictable outputs, and readable steps.
- Add preview, dry-run, or a small-batch test when file operations are involved.
- Explain how success will be checked before the user runs anything risky.

### Ask First

- Deleting files or folders.
- Overwriting existing outputs.
- Changing naming rules for many files.
- Adding new dependencies or runtime requirements.
- Changing system configuration, scheduled jobs, or startup behavior.
- Running the script across a large directory tree after only a tiny sample test.

### Never

- Silently delete or overwrite data.
- Guess ambiguous business rules.
- Hide side effects behind vague script names or unclear commands.
- Write a giant "universal" tool for a one-off job.
- Skip safety checks because the task feels obvious.
- Claim success without saying how the result was verified.

## File Operation Safety

When the script touches files, folders, names, or structure:

- verify source paths exist;
- verify destination paths exist or are created safely;
- use literal paths where possible for reliability;
- preserve existing data by default;
- on collisions, create a suffix such as `__dup_001` instead of overwriting;
- route ambiguous cases to manual review rather than guessing;
- log what changed if the action is batch-oriented or hard to inspect manually.

For a deeper checklist, see [references/file-safety-checklist.md](references/file-safety-checklist.md).

## Risk Call Rules

- Default to `LOW` unless there is concrete evidence for `MODERATE` or `HIGH`.
- Do not inflate the risk just because the task feels scary.
- Do not understate the risk just because the script is short.
- Every non-trivial risk call should include:
  - `Evidence`: what specifically supports the concern;
  - `Impact`: what could happen in practical terms;
  - `Action`: how to reduce, test, or unblock the risk.
- If the evidence is incomplete, say what is unknown instead of pretending certainty.

## Writing Style

- Prefer behavioral guidance over long reference dumps.
- Explain why a rule matters, not only what the rule is.
- Use concrete language and direct instructions.
- Keep the code lean. Remove parts that do not pull their weight.
- Comments should explain intent, not narrate obvious syntax.

## Rationalizations To Reject

| Rationalization | Reality |
|---|---|
| "It's just a small script." | Small scripts can still create large damage when run on real folders. |
| "I'll add safety later." | Safety added after the main logic is usually incomplete or forgotten. |
| "We might need this to be generic later." | Premature generality makes one-off automation harder to trust and maintain. |
| "The naming pattern is obvious." | If it matters, define it. If it is ambiguous, ask. |
| "Dry-run is overkill." | Dry-run is cheap compared with cleaning up a wrong batch change. |
| "I'll know if it worked when I look at the folder." | Human inspection alone is unreliable for bulk changes. Add explicit checks. |

## Verification Before Execution

Before the first real run, confirm:

- [ ] The problem and expected result were explained in plain language.
- [ ] Assumptions were stated explicitly.
- [ ] `Always / Ask First / Never` boundaries were defined.
- [ ] The script uses the simplest safe approach.
- [ ] A preview, dry-run, or small-batch test exists for risky operations.
- [ ] Collision handling is defined.
- [ ] The user knows what the script changes and how to stop safely.

## Required Output After Coding

Use this exact structure after implementation:

```text
Файл:
Запуск:
Что меняет:
Риск: LOW / MODERATE / HIGH
Evidence:
Impact:
Action:
Отчет или лог:
```

## Verification Before Completion

Before claiming the work is done, confirm:

- [ ] The script location is explicit.
- [ ] The run command is explicit.
- [ ] Changed scope is explicit.
- [ ] Risk level is explicit.
- [ ] Verification method is explicit.
- [ ] Log or report location is explicit when the task is batch-oriented.

## Examples

### Good trigger examples

- "Напиши PowerShell-скрипт, который безопасно разложит 800 PDF по папкам."
- "Нужен Python-скрипт для переименования файлов по шаблону без потери дублей."
- "Помоги улучшить bash-скрипт миграции, но сначала проверь риски."

### Poor fit examples

- "Просто объясни, что делает эта одна строка grep."
- "Дай идею, как в целом автоматизировать работу, код пока не нужен."

## Test Prompts

Realistic workflow prompts live in [evals/evals.json](evals/evals.json).

Trigger-quality checks live in [evals/trigger-evals.json](evals/trigger-evals.json).

## Portability And Packaging

If this skill needs to be moved to another machine or shared with someone else:

- validate it first;
- package it only after validation passes;
- keep only essential files in the skill folder;
- reject symlinks and broken references;
- avoid hardcoded machine-specific paths in the skill content.

Helper files:

- [references/distribution-and-validation.md](references/distribution-and-validation.md)
- [scripts/validate-skill.ps1](scripts/validate-skill.ps1)
- [scripts/package-skill.ps1](scripts/package-skill.ps1)

## Success Criteria

This skill is working well when it consistently causes the agent to:

- clarify before coding;
- avoid unnecessary new scripts;
- choose `Adopt / Extend / Build` consciously instead of defaulting to new code;
- choose simple and safe implementations;
- add verification before risky execution;
- explain the result in a way a non-programmer can actually use.
