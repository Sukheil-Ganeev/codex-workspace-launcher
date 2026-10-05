# File Safety Checklist

Use this reference when the script touches files, folders, names, or batch changes.

## 1. Decide the blast radius

Before coding, identify:
- what paths can be read;
- what paths can be written;
- whether the script changes names, contents, locations, or metadata;
- how many files might be affected in the worst case.

If the affected scope is unclear, stop and narrow it first.

## 2. Prefer preview first

The safest order is:
1. preview or dry-run;
2. tiny sample run;
3. review output;
4. wider run.

Good preview output usually includes:
- source path;
- intended destination or new name;
- action type such as `move`, `copy`, `rename`, or `skip`;
- reason for `skip` decisions.

## 3. Handle collisions explicitly

Never rely on "it probably won't collide."

Choose one explicit rule:
- suffix duplicates such as `__dup_001`;
- skip with a log entry;
- ask the human before continuing.

If no collision rule is defined, the script is not ready.

## 4. Prefer inspectable logs

For batch operations, produce a log or report when useful.

Minimum useful fields:
- timestamp;
- source;
- action;
- destination or new name;
- status such as `changed`, `skipped`, `error`;
- reason for skip or error.

## 5. Use the safest default behavior

Default behavior should preserve data.

Prefer:
- `copy` over `move` when uncertainty is high;
- `skip` over `overwrite`;
- `ask first` over assumption;
- narrow scope over recursive whole-drive operations.

## 6. Path discipline

- Prefer workspace-relative thinking over hardcoded absolute paths.
- If absolute paths are necessary, explain why.
- Treat recursive operations as high risk.
- Use literal path handling where the runtime supports it.

## 7. Human-friendly reporting

The user should be able to answer these questions after reading your note:
- What exactly will change?
- What will not change?
- What is the biggest risk?
- How do I test it safely first?
- Where is the evidence that it worked?

## 8. Red flags

Stop and reassess if the script:
- mixes multiple unrelated jobs;
- changes both names and contents and locations in one pass without a strong reason;
- deletes originals before verification;
- relies on undocumented naming assumptions;
- adds dependencies just for convenience;
- cannot explain its own skip logic.
