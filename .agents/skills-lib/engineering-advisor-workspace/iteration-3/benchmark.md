# Iteration 3 Benchmark — engineering-advisor

**Date:** 2026-03-05
**Model:** claude-sonnet-4-6 (executor + analyzer)
**Evals:** 3, 4, 5 (eval-business-logic-prices, eval-rewrite-from-scratch, eval-env-without-gitignore)

---

## Results by Eval

| Eval | Name | with_skill | without_skill | Delta |
|------|------|-----------|---------------|-------|
| eval-3 | business-logic-prices | 4/4 (100%) | 0/4 (0%) | +100% |
| eval-4 | rewrite-from-scratch | 4/4 (100%) | 0/4 (0%) | +100% |
| eval-5 | env-without-gitignore | 4/4 (100%) | 0/4 (0%) | +100% |

---

## Overall Statistics

| Metric | with_skill | without_skill | Delta |
|--------|-----------|---------------|-------|
| Pass rate (mean) | 1.00 | 0.00 | **+1.00** |
| Pass rate (stddev) | 0.00 | 0.00 | — |
| Time (mean) | 86.7s | 46.1s | +40.6s |
| Tokens (mean) | 42,824 | 21,860 | +20,964 |

---

## Timing Details

| Eval | Config | Time (s) | Tokens |
|------|--------|----------|--------|
| eval-3 (business-logic-prices) | with_skill | 94.9 | 41,035 |
| eval-3 (business-logic-prices) | without_skill | 48.4 | 21,877 |
| eval-4 (rewrite-from-scratch) | with_skill | 82.9 | 46,173 |
| eval-4 (rewrite-from-scratch) | without_skill | 61.2 | 22,673 |
| eval-5 (env-without-gitignore) | with_skill | 82.3 | 41,265 |
| eval-5 (env-without-gitignore) | without_skill | 28.7 | 21,029 |

---

## Key Findings

1. **Perfect score with skill** — all 3 evals passed 4/4 assertions with the skill active (100% pass rate).

2. **Zero score without skill** — without the skill, all 3 evals failed 0/4 (0% pass rate). This is the clearest possible signal of skill impact.

3. **Iteration 3 is strongest so far** — compared to iteration-2 where without_skill had a mean pass rate of 0.35 (some evals partially passed), iteration-3 shows a clean 1.00 vs 0.00 split. The new evals test scenarios where the skill's guidance is absolutely critical.

4. **Token cost is justified** — the skill adds ~2x tokens (~20,964 more per run) but delivers 100% vs 0% pass rate. For financial logic, rewrite warnings, and security checks, this trade-off is clearly worthwhile.

5. **Eval-5 (env-without-gitignore) was most time-efficient** — with_skill took 82.3s vs 28.7s without, while achieving a perfect score vs complete failure. The without_skill response was dangerously brief (252 output chars — just added the line with no safety checks).

6. **Eval-3 (business-logic-prices) without_skill** — the baseline Claude delivered complete financial code in one shot with zero mention of tests, risks, or boundary cases. Exactly the anti-pattern the skill prevents.

7. **Eval-4 (rewrite-from-scratch) without_skill** — the baseline Claude actively encouraged rewriting ("Переписать с чистого листа — это не трусость, это инженерное решение"), which is the opposite of what the skill teaches.

---

## Comparison with Iteration 2

| Metric | Iteration 2 | Iteration 3 |
|--------|-------------|-------------|
| with_skill pass rate | 1.00 | 1.00 |
| without_skill pass rate | 0.35 | 0.00 |
| Delta pass rate | +0.65 | **+1.00** |
| with_skill tokens (mean) | 44,561 | 42,824 |
| without_skill tokens (mean) | 25,472 | 21,860 |

Iteration 3 evals are more discriminating — they target scenarios where without the skill, the model gives actively harmful advice (financial code without tests, encouraging full rewrites, ignoring security in .env files).
