---
name: code-refactor-pro
description: "Use when the codebase has technical debt, TODO/FIXME/HACK markers, high cyclomatic complexity, legacy framework versions, outdated dependencies, dead code, AI-generated artifacts, debug statements, or when a framework migration is needed. Also use when regression safety is required before structural changes or when behavior-preserving cleanup is needed after AI-assisted coding sessions."
---
# Code Refactor Pro

## Overview

A full-cycle safe refactoring skill covering tech debt discovery, regression baselining, incremental migration, noise cleanup, and behavior verification. Combines static analysis with git history signals to prioritize debt by actual business impact, not code aesthetics.

## When to Use

**Use this skill when:**
- You see TODO / FIXME / HACK / XXX / WORKAROUND comments in the code
- Functions exceed 50 lines or cyclomatic complexity > 10
- Dependencies are 2+ major versions behind
- A framework migration is needed (JS to TS, React class to hooks, Vue 2 to 3, Python 2 to 3, etc.)
- Code has leftover debug statements, placeholder text, or stub functions from AI sessions
- Test coverage is below 80% and you need to refactor safely
- A "big bang rewrite" is being considered (stop — use this instead)

**Do NOT use this skill when:**
- Code works and nobody touches it (stable legacy = not a priority)
- You only need to add a new feature (use regular coding flow)
- The entire codebase needs a full rewrite in a different language (out of scope)
- You have zero tests and zero time to create a baseline (fix that first)

---

## Modes

### analyze — Tech Debt Scan

**Goal:** Identify what is actually hurting the team, not just what looks messy.

**Step 1 — Static scan**

Scan for these signals:
- Comment markers: `TODO`, `FIXME`, `HACK`, `XXX`, `WORKAROUND`, `TEMP`, `KLUDGE`
- Long functions: > 50 lines
- Deep nesting: > 4 levels of indentation
- Cyclomatic complexity: > 10 branches per function
- Outdated dependencies: check `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml` for major version lag
- Dead code: exported symbols never imported, functions never called
- AI artifacts: `console.log("debug")`, `print("test")`, placeholder strings like `"TODO: implement"`, excessive inline comments explaining obvious code, over-engineered abstractions with no callers

**Step 2 — Git history signals** (run in git repos)

```bash
# Files changed most often in last 90 days (high churn = high risk)
git log --since="90 days ago" --name-only --pretty=format: | sort | uniq -c | sort -rn | head -20

# Files correlated with bug-fix commits
git log --grep="fix\|bug\|hotfix\|patch" --name-only --pretty=format: | sort | uniq -c | sort -rn | head -20

# Files with most contributors (contention)
git log --name-only --pretty=format:"%ae" | awk 'NF{file=$0; next} {print file, $0}' | sort -u | awk '{print $1}' | sort | uniq -c | sort -rn | head -20
```

**Step 3 — Score and prioritize**

For each debt item, compute a composite score (0–10):

| Signal | Weight |
|--------|--------|
| Change frequency (last 90d) | 30% |
| Bug-fix commit correlation | 30% |
| Developer contention (# authors) | 20% |
| Cyclomatic complexity | 20% |

**Priority tiers:**

| Tier | Score | Action |
|------|-------|--------|
| P0 | >= 8.0 | Fix immediately — blocking quality or velocity |
| P1 | 5.0–7.9 | Schedule this quarter |
| P2 | < 5.0 | Monitor only — do not touch unless forced to |

**Output format:**

```
TECH DEBT REPORT
================
P0 (fix now):
  [file:line] pattern — reason — score: X.X

P1 (schedule):
  [file:line] pattern — reason — score: X.X

P2 (monitor):
  [file:line] pattern — reason — score: X.X

Summary: X P0, Y P1, Z P2 items found.
Recommended first target: [file] — highest combined score.
```

---

### snapshot — Regression Baseline

**Goal:** Capture current behavior before touching anything. This is the safety net.

**Step 1 — Run existing tests**

```bash
# Python
pytest --tb=short -q 2>&1 | tee baseline_test_output.txt

# Node / JS / TS
npm test -- --passWithNoTests 2>&1 | tee baseline_test_output.txt

# Go
go test ./... 2>&1 | tee baseline_test_output.txt
```

Record: total tests, passed, failed, coverage %.

**Step 2 — Identify uncovered behavior**

For each function/module being refactored, check:
- Are inputs and outputs tested?
- Are error paths tested?
- Are boundary conditions tested (empty input, null, extreme values)?
- Are side effects tested (DB writes, HTTP calls, file I/O)?

**Step 3 — Write characterization tests (golden-master)**

For any untested critical behavior, write tests that capture current output — even if that output is technically wrong. These tests exist only to detect *unexpected change*, not to validate correctness.

```python
# Example: characterization test pattern
def test_legacy_price_calculation_snapshot():
    """Characterization test — captures current behavior as baseline.
    Do not assert correctness, only that behavior does not change during refactor."""
    result = calculate_price(item_id=42, quantity=3, discount_code="VIP10")
    assert result == 127.50  # current output as of [date]
```

**Step 4 — Record the snapshot**

Create a brief note (can be a code comment or a local file):
```
BASELINE SNAPSHOT — [date]
File(s) targeted: [list]
Tests passing: X / Y
Coverage: Z%
Key behaviors captured:
  - [function]: [expected output for key inputs]
  - [function]: [error behavior]
Baseline commit: [git SHA]
```

**Step 5 — Set up feature flag (for large migrations)**

For changes affecting live traffic, introduce a feature flag before migrating:
```python
USE_NEW_IMPL = os.getenv("USE_NEW_IMPL", "false") == "true"

def process(data):
    if USE_NEW_IMPL:
        return new_process(data)
    return legacy_process(data)
```

Start at 0% traffic. Shift to 5% → 25% → 50% → 100% as confidence grows.

---

### refactor — Safe Migration

**Goal:** Transform the code incrementally without breaking behavior.

**Core rule: one file or module at a time. Never attempt a big-bang rewrite.**

**Step 1 — Pick the first target**

Start with the highest P0 item from `analyze`, or the file with the highest churn + complexity. Do not start with the largest file.

**Step 2 — Incremental migration loop**

For each file or module:

1. Read the file. Understand what it does before touching it.
2. Make one logical change (rename, extract function, convert syntax, update import).
3. Run the baseline tests. If any fail — stop and diagnose before continuing.
4. Commit with a clear message: `refactor: [what changed] in [file]`
5. Move to the next change.

**Common migration patterns:**

**JavaScript to TypeScript**
- Add `tsconfig.json` with `strict: false` and `allowJs: true` first
- Rename `.js` to `.ts` one file at a time
- Add type annotations incrementally
- Tighten `strict` mode after all files are converted

**React class components to hooks**
```jsx
// Before
class Counter extends React.Component {
  state = { count: 0 };
  increment = () => this.setState({ count: this.state.count + 1 });
  render() { return <button onClick={this.increment}>{this.state.count}</button>; }
}

// After
function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}
```

**Vue 2 Options API to Vue 3 Composition API**
```js
// Before (Options API)
export default { data() { return { count: 0 }; }, methods: { inc() { this.count++; } } }

// After (Composition API)
import { ref } from 'vue';
export default { setup() { const count = ref(0); return { count, inc: () => count.value++ }; } }
```

**Strangler fig pattern (for large legacy systems)**

Wrap the legacy component, route new traffic to the new implementation, keep the old path as fallback:
```python
class PaymentService:
    def charge(self, amount, method):
        if feature_flag("new_payment_engine"):
            return self._new_charge(amount, method)   # new path
        return self._legacy_charge(amount, method)    # old path still works
```

**Step 3 — For migrations > 100 files**

Break into multiple PRs. Each PR should be independently reviewable and deployable. Suggested groupings:
- PR 1: Config + types + utilities
- PR 2: Data layer
- PR 3: Business logic
- PR 4: API / handlers
- PR 5: UI / templates

**Step 4 — Update dependencies after code changes**

After all code changes pass tests, update dependencies:
```bash
# Node
npx npm-check-updates -u && npm install && npm test

# Python
pip list --outdated && pip install --upgrade [package] && pytest
```

Update one dependency at a time. Run tests after each.

---

### cleanup — Remove Noise

**Goal:** Remove debug statements, AI-generated artifacts, dead code, and TODO drift without changing behavior.

**Phase 1 — Debug and placeholder removal (HIGH certainty, auto-fixable)**

Patterns to find and remove:
```
# Debug statements
console.log(...)       # JS/TS
print("debug", ...)    # Python
fmt.Println("debug")   # Go
debugger;              # JS breakpoints
pdb.set_trace()        # Python debugger

# Placeholder text
"TODO: implement"
"FIXME: placeholder"
"test123", "foo", "bar" as production values
pass  # Python stubs with no docstring

# Temporary scaffolding
# TEMP:, # HACK:, # KLUDGE: markers with no ticket reference
```

For each HIGH-certainty find: remove the line, run tests, commit.

**Phase 2 — Excessive comment cleanup (MEDIUM certainty, review required)**

Remove comments that:
- Restate what the code obviously does: `i += 1  # increment i by 1`
- Are commented-out code blocks older than 30 days (check git blame)
- Are section dividers with no content: `#######################`

Keep comments that:
- Explain *why*, not *what*
- Document non-obvious business rules
- Reference external specs, tickets, or known gotchas

**Phase 3 — Dead code removal (MEDIUM certainty)**

```bash
# Python: find unused imports
python -m pyflakes . 2>&1 | grep "imported but unused"

# JS/TS: find unused exports
npx ts-prune  # or: npx unimported

# Go
go vet ./...
```

For each dead code candidate:
1. Confirm with `git log --all -S "function_name"` — has it been used recently?
2. Search entire codebase for string-based dispatch (plugin systems, dynamic loading)
3. Only then remove

**Phase 4 — Over-engineering patterns (LOW certainty, context-dependent)**

Review but do not auto-remove:
- Abstractions with only one implementation and no planned second
- Factory patterns wrapping a single class
- Dependency injection containers for 3-file projects
- Configuration systems more complex than the code they configure

Flag these for team discussion, not silent deletion.

**Cleanup commit convention:**

Use separate commits from refactor commits:
```
cleanup: remove debug console.log statements in payments/
cleanup: delete commented-out legacy auth code (unused since 2024)
cleanup: remove placeholder TODO stubs in catalog handlers
```

---

### verify — Confirm Nothing Broke

**Goal:** Confirm that refactored code behavior is identical to the baseline snapshot.

**Step 1 — Run full test suite**

```bash
# Run same command used in snapshot step
pytest --tb=short -q         # Python
npm test                      # Node
go test ./...                 # Go
```

Compare result against baseline:
- Same number of tests passing? (or more — new tests added during refactor are fine)
- No previously-passing tests now failing?
- Coverage equal or higher?

**Step 2 — Run type checker and linter**

```bash
# TypeScript
npx tsc --noEmit

# Python
mypy . --ignore-missing-imports
flake8 . --max-line-length=120

# Go
go vet ./...
golint ./...
```

Zero new errors introduced.

**Step 3 — Behavior equivalence check**

For any function that was structurally changed, run a side-by-side comparison:

```python
# Temporarily run both old and new, assert equal output
def test_refactored_fn_matches_original():
    inputs = [(1, "test"), (0, ""), (999, "edge")]
    for args in inputs:
        assert new_fn(*args) == old_fn(*args), f"Diverged on input {args}"
```

**Step 4 — Integration smoke test**

If the refactored module has external integrations (DB, API, queue):
- Run a manual smoke test against a staging environment
- Confirm no new errors in logs for 5 minutes of synthetic traffic

**Step 5 — Feature flag rollout (if applicable)**

If using the strangler fig + feature flag pattern from `refactor` mode:
- 5% traffic → monitor for 24h → no errors → proceed
- 25% → 50% → 100% → retire legacy path after one full release cycle at 100%

**Step 6 — Final report**

```
VERIFY REPORT
=============
Baseline:   X tests passed, Y% coverage
After:      X+ tests passed, Y%+ coverage
Type errors: 0 new
Lint errors: 0 new
Behavior:   All characterization tests pass
Feature flag: [N/A | at X% traffic, stable for Yh]
Status: SAFE TO MERGE
```

---

## Quick Reference

| Mode | When to use | Key output |
|------|------------|-----------|
| `analyze` | Start of any refactor session | P0/P1/P2 debt report with scores |
| `snapshot` | Before touching any code | Baseline test results + characterization tests |
| `refactor` | During migration or modernization | Incremental commits, one file at a time |
| `cleanup` | After AI coding sessions or before PR | Removed debug/dead/placeholder code |
| `verify` | After refactor, before merge | Green tests, zero new errors, behavior confirmed |

**Recommended sequence for a safe refactor:**
```
analyze -> snapshot -> refactor (small steps) -> cleanup -> verify
```

**For emergency tech debt in production:**
```
snapshot -> refactor (P0 only) -> verify -> cleanup (separate PR)
```

---

## Common Mistakes

| Mistake | Why it's dangerous | Correct approach |
|---------|--------------------|-----------------|
| Starting refactor without a snapshot | No safety net; behavioral regressions go undetected | Always run `snapshot` first |
| Refactoring + adding features in the same PR | Impossible to review; breaks bisectability | Separate PRs: refactor-only, then feature |
| Removing "unused" code without checking dynamic dispatch | Code called via reflection or plugin systems will break silently | Search for string references before deletion |
| Updating all dependencies at once | One breaking change hides another | Update one dependency -> test -> commit -> repeat |
| Deleting commented-out code without git blame | Code may be temporarily disabled, not abandoned | Check git blame age; if < 30 days, ask first |
| Big-bang migration of 100+ files | Merge conflicts, untraceable regressions, review fatigue | Break into 5–10 file batches per PR |
| Scoring debt by complexity alone | Stable complex code is fine; unstable simple code is not | Weight churn and bug correlation equally |
| Applying cleanup to MEDIUM/LOW items automatically | Context-dependent patterns need human review | Only auto-fix HIGH certainty items |
| Retiring legacy path immediately after 100% cutover | Race conditions and edge cases surface over time | Wait one full release cycle at 100% before retiring |
| Fixing P2 items first because they look easiest | P2 items rarely improve velocity; P0 items block the team | Always start with highest score, not lowest effort |
