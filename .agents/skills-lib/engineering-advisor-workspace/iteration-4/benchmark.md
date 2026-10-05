# Engineering Advisor — Iteration 4 Benchmark

**Date:** 2026-03-05
**Evals run:** 6 (eval-n-plus-one), 7 (eval-api-endpoint), 8 (eval-new-dependency)
**Model:** claude-sonnet-4-6
**Runs per configuration:** 1

---

## Per-Eval Results

| Eval | Name | With Skill | Without Skill | Delta |
|------|------|-----------|---------------|-------|
| 6 | eval-n-plus-one | 100% (4/4) | 100% (4/4) | 0% |
| 7 | eval-api-endpoint | 100% (4/4) | 0% (0/4) | +100% |
| 8 | eval-new-dependency | 100% (4/4) | 75% (3/4) | +25% |

---

## Overall Stats

| Metric | With Skill | Without Skill | Delta |
|--------|-----------|---------------|-------|
| Mean pass rate | 100% | 58.3% | +41.7% |
| StdDev pass rate | 0.0 | 0.412 | — |
| Mean time | 81.4s | 26.1s | +55.3s |
| Mean tokens | 42,014 | 18,259 | +23,755 |

---

## Key Findings

### eval-n-plus-one (eval_id=6) — Non-discriminating

Both with_skill and without_skill achieve 100% (4/4). Base Claude correctly:
- Identifies N+1 (SELECT in a loop)
- Explains the scaling risk with concrete numbers (500 tourists = 501 queries)
- Proposes joinedload as the fix
- Keeps N+1 as the primary focus rather than answering only about formatting

**Conclusion:** N+1 detection is within base Claude competence. This eval does not discriminate between skill and no-skill. Criteria should be tightened — e.g., require mention of subqueryload as alternative, explain WHY N+1 happens (lazy loading pattern), or require explicit trigger numbering.

### eval-api-endpoint (eval_id=7) — Maximum discrimination

With skill: 100% (4/4). Without skill: 0% (0/4). Complete failure on all assertions.

Without the skill, base Claude:
- Ignores authorization entirely (no mention of open POST endpoint)
- Keeps `data: dict` without any comment about missing validation
- Provides no explicit advisory level (no "Recommended" / "MANDATORY" label)
- Delivers working code (db.refresh + try/except) without any security warning

With the skill, the response leads with a full security analysis section ("What Is Wrong With the Current Code") covering authorization absence, missing Pydantic validation, and rate limiting — before providing any code fix.

**Conclusion:** This is the highest-value eval. Security-first behavior on API endpoints is entirely skill-dependent.

### eval-new-dependency (eval_id=8) — Partial discrimination

With skill: 100% (4/4). Without skill: 75% (3/4). Single failure: D1 (requirements.txt update).

Base Claude correctly handles:
- D2: Detects synchronous requests in async function (blocks event loop)
- D3: Proposes httpx.AsyncClient with await
- D4: Does not naively rename import without async transition

Base Claude misses:
- D1: Mentions only `pip install httpx`, never references requirements.txt or `pip freeze > requirements.txt`

**Conclusion:** Base Claude knows async/blocking patterns well. The skill adds requirements.txt discipline — a real-world step that's easy to forget.

---

## Comparison with Previous Iterations

| Iteration | Evals | With Skill Mean | Without Skill Mean | Delta |
|-----------|-------|----------------|-------------------|-------|
| Iteration 3 | 3, 4, 5 | 100% | 0% | +100% |
| Iteration 4 | 6, 7, 8 | 100% | 58.3% | +41.7% |

**Interpretation:** Iteration 3 had maximum discrimination across all 3 evals (without_skill: 0% on every eval). Iteration 4 shows a more nuanced picture — base Claude is fully capable on N+1 queries and partially capable on async/blocking patterns. The skill provides decisive value specifically on security-critical patterns (API authorization, Pydantic validation) where base Claude defaults to "helpful assistant" mode and skips security warnings.

The reduced overall delta (+41.7% vs +100%) does NOT indicate skill regression — it indicates the eval suite now includes a non-discriminating eval (N+1) and a partially-discriminating eval (new-dependency). The skill's strongest value remains demonstrated by eval-api-endpoint, where the gap is 100%.

---

## Recommendations

1. **Replace or harden eval-n-plus-one** — current criteria are met by base Claude without skill. Add requirements: explicit trigger number in response, mention of lazy-loading as root cause, subqueryload as alternative to joinedload.

2. **Keep eval-api-endpoint as anchor eval** — maximum discrimination, directly validates the core skill behavior (security-first on API write endpoints).

3. **Consider splitting eval-new-dependency** into two separate evals: one for async/blocking detection (where base Claude is strong), one specifically for dependency management (requirements.txt, pinning versions) where the skill adds clear value.
