# Insights for docs-optimizer Iteration 2

**Source:** Iteration 1 benchmark (2026-03-12)
**Project tested:** TouristBotEcosystem
**Results:** with_skill 97% vs without_skill 90% (delta +7%)

---

## Problem 1: Assertions too weak — baseline scores 90%

The without_skill baseline achieved 90% pass rate, making the delta only +7%. This means the current assertions test "did something useful" rather than "followed the skill's methodology."

**Fix:** Add structural assertions that only pass if the skill's specific framework is used:
- Require AP-XX anti-pattern codes (AP-01, AP-16, etc.) — baseline never produces these
- Require tier names: "Essential", "On-demand", "Archive" (exact strings)
- Require N/5 score format (not N/10 or other scales)
- Require SSOT violation table with DUP-XX codes
- Require token count estimates per file (not just totals)

**Expected impact:** Baseline should drop to ~40-50%, widening the delta to +40-50%.

## Problem 2: Content drift not detected (Eval 6)

In Eval 6 (freshness), without_skill outperformed with_skill:
- with_skill: used git log dates -> all 39 files "active" (7-10 days < 14 day threshold)
- without_skill: checked content references -> found docs/ARCHITECTURE.md references v4.0 while project is v5.9.0

**Fix:** Add content drift detection to SKILL.md methodology:
- Compare version numbers mentioned in docs vs current project version
- Flag docs referencing outdated deployment targets (e.g., Oracle Cloud when project is on GCP)
- Cross-reference feature lists in docs against actual codebase

## Problem 3: CLAUDE.md threshold ambiguity (Eval 1)

Eval 1 assertion expected 557-line CLAUDE.md to be flagged as critical. The with_skill agent reported it as "below critical" because it measured TOKENS (~2,228 < 4,000 token threshold) while the assertion expected LINE COUNT evaluation (557 > 400 = CRITICAL).

**Fix:** Clarify in SKILL.md:
- Lines threshold: >400 lines = HIGH, >300 lines = MEDIUM
- Tokens threshold: >4,000 tokens = CRITICAL
- Both thresholds must be checked independently
- If EITHER exceeds its limit, flag the higher severity

## Problem 4: Parent-directory CLAUDE.md not analyzed

Eval 7 without_skill discovered that `D:/Downloads/CLAUDE.md` (~9,647 tokens) is auto-loaded for ALL projects under Downloads/. The skill currently only analyzes the project's own CLAUDE.md.

**Fix:** Add parent-directory CLAUDE.md scanning:
- Walk up from project root checking for CLAUDE.md at each level up to ~/.claude/CLAUDE.md
- Report total auto-load cost across all levels
- Flag parent CLAUDE.md if it's larger than the project's own

## Problem 5: with_skill is slower (+103s average)

with_skill averages 354s vs 251s for baseline (+41% slower). The skill methodology adds overhead by requiring structured output, AP-code classification, and tier analysis.

**Consideration:** This may be acceptable if output quality justifies the time. But for iteration 2, consider whether the SKILL.md can be made more concise to reduce agent reading/processing time.

---

## Summary of Changes for Iteration 2

| Area | Action | Priority |
|------|--------|----------|
| Assertions | Add structural checks (AP-codes, tier names, DUP-codes) | HIGH |
| SKILL.md | Add content drift detection methodology | HIGH |
| SKILL.md | Clarify line/token dual threshold for CLAUDE.md | MEDIUM |
| SKILL.md | Add parent-directory CLAUDE.md scanning | MEDIUM |
| SKILL.md | Optimize length to reduce agent processing time | LOW |
