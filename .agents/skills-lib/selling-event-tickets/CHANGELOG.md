# Changelog

## 1.0.6 — 2026-09-17

- R032: stale term `MASTER` replaced with neutral wording (no meaning change).
- `validate_partner_message.py`: UNSUPPORTED_GUARANTEE now also warns on `90%`
  (R068 forbids “90% точно”). No new test count (case added to existing test).
- Redeploy pending.

## 1.0.5 — 2026-09-17

- `internal-calculation.md`: added missing `Payment cost` row (FULL COST formula
  completeness) and a compact `Market` section (comparable listing + verdict).
- `advertising-pack.md`: added `Lead intake` line (playbook item 9).
- Template review: other 7 templates consistent with rules, no changes.
- No code or pricing-rule changes. Redeploy pending.

## 1.0.4 — 2026-09-17

- `validate_partner_message.py`: INTERNAL_DATA now catches markup/reserve/margin
  jargon (`наценк`, `чистая/чистой прибыли`, bare `резерв`, `марж`) with a word
  boundary so legitimate «зарезервировать» still passes; UNSUPPORTED_GUARANTEE
  now warns on any `гарант*`, bare `100%`, `у нас/билеты на руках` (but not
  «ребёнок на руках») and `официальный партнёр`.
- Tests: 21 → 24 (internal-jargon errors, forbidden-claim warnings,
  legitimate-phrase negatives). Partner template still fully clean.
- No change to pricing rules or process. Redeploy pending.

## 1.0.3 — 2026-09-17

- `calculate_offer.py`: non-finite inputs (inf/nan) are now rejected with a clean
  usage error (exit 2) instead of an unhandled traceback; `--bank-reserve-percent`
  help points at R010/R011 (caller-owned decision, 5% non-AED only).
- Tests: 15 → 21 (non-finite rejection, rounding edge, conversion direction,
  explicit --allow-combined, delivery allocation, zero-base guard). Misleading
  `test_aed_markup_...` renamed: the 5% there is mechanics input, not an AED rule.
- No change to pricing rules, templates, or process. Redeploy to AI environments
  and server copies is still pending.

## 1.0.2 — 2026-09-03

- Backfilled from the source knowledge-base archive: event-and-platform index, RU/EN operator prompts, machine-readable rule registry CSV, source manifest and metadata JSON. Source-integrity record extended with validation fields.

## 1.0.1 — 2026-09-03

- Step 3 now requires live internet search, always and as much as needed: never quote tickets, prices or availability from memory.

## 1.0.0 — 2026-09-02

- Initial skill built from ten internal ticketing/event sales conversations.
- Added 70-rule registry, platform and event playbooks, templates and source evidence.
- Added FULL COST calculator and partner-message validator.
- Added historical baseline failures and behavioral pressure scenarios.
