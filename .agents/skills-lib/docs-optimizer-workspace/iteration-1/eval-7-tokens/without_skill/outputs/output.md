# Token Cost at Session Start — TouristBotEcosystem

**Project:** `D:/Downloads/TouristBotEcosystem/`
**Measured:** 2026-03-12
**Model:** claude-sonnet-4-6 (200,000 token context window)

---

## Which Files Are Loaded Automatically

Claude Code reads `CLAUDE.md` files walking up the directory tree from the working directory, plus the global user config. For this project (cwd = `D:/Downloads/TouristBotEcosystem/`):

| # | File | Location | Purpose |
|---|------|----------|---------|
| 1 | Global CLAUDE.md | `C:/Users/londo/.claude/CLAUDE.md` | User-level instructions (applies to all projects) |
| 2 | Parent CLAUDE.md | `D:/Downloads/CLAUDE.md` | Downloads-level project context (WhatsApp exports, CRM, etc.) |
| 3 | Project CLAUDE.md | `D:/Downloads/TouristBotEcosystem/CLAUDE.md` | Project-specific instructions, architecture, commands |
| 4 | System overhead | injected by Claude Code | Git status, env info, current date, wrapper tags |

No `MEMORY.md` file exists in the project — not loaded.

---

## Token Estimate Per File

### Methodology

- **ASCII characters** (code, paths, English): ~4 chars per token
- **Cyrillic characters** (Russian text): ~1.5 chars per token (each Cyrillic char = 2 UTF-8 bytes, roughly 1 token per 1.5 chars)
- **Other Unicode** (emojis, box-drawing): ~2 chars per token
- Margin of error: ±15-20% depending on actual tokenizer boundaries

### Results

| File | Size (bytes) | Lines | ASCII chars | Cyrillic chars | Estimated tokens |
|------|-------------|-------|-------------|----------------|-----------------|
| `~/.claude/CLAUDE.md` | 7,965 | 139 | 2,332 | 2,759 | **~2,441** |
| `D:/Downloads/CLAUDE.md` | 23,549 | 659 | 14,429 | 8,881 | **~9,647** |
| `TouristBotEcosystem/CLAUDE.md` | 39,824 | 557 | 26,126 | 4,308 | **~10,158** |
| System overhead (git, env, date) | — | ~30 | — | — | **~500** |
| **TOTAL** | **71,338** | **1,385** | | | **~22,746** |

---

## Summary

```
Global CLAUDE.md (~/.claude/):       2,441 tokens   (11%)
Parent CLAUDE.md (D:/Downloads/):    9,647 tokens   (42%)
Project CLAUDE.md (TouristBotEcosystem/): 10,158 tokens  (45%)
System overhead:                       500 tokens    (2%)
─────────────────────────────────────────────────────
TOTAL:                               22,746 tokens

Context window: 200,000 tokens
Occupied at session start: ~11.4%
```

---

## Key Observations

1. **The project CLAUDE.md is the largest single file** (557 lines, ~10,158 tokens) — dominated by the detailed architecture tree (lines 37–352) listing every file with descriptions.

2. **The parent D:/Downloads/CLAUDE.md is nearly as large** (~9,647 tokens) — it contains the full WhatsApp data schema, all project descriptions, Tourism CRM details, Kaggle notes, and integration tables.

3. **Cyrillic text costs more tokens** — Russian text uses roughly 2.5x more tokens per character than equivalent ASCII. The global CLAUDE.md is mostly Russian (2,759 Cyrillic vs 2,332 ASCII chars) which inflates its token count relative to its byte size.

4. **22,746 tokens is 11.4% of the context window** — this is the baseline "tax" paid before any user message or code is read. In a long session with large file reads, this overhead is manageable but not negligible.

5. **Largest contributor to bloat:** The architecture tree in `TouristBotEcosystem/CLAUDE.md` (lines 37–352 = 315 lines of file listing) accounts for roughly 5,000–6,000 tokens alone — more than 2x the entire global CLAUDE.md.

---

## Cost Estimate (if pricing applies)

At Claude API pricing for input tokens (claude-sonnet-4-6: $3/1M input tokens):

| Scenario | Tokens | Cost per session |
|----------|--------|-----------------|
| Session start overhead only | 22,746 | $0.068 |
| Typical session (+ 50K tokens conversation) | 72,746 | $0.218 |
| Heavy session (+ 150K tokens) | 172,746 | $0.518 |

Note: Claude Code (the CLI tool) is priced per token through your Anthropic API account.
