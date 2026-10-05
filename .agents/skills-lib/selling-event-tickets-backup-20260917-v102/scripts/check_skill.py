#!/usr/bin/env python3
"""Static validation for the selling-event-tickets skill package."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SKILL.md",
    "README.md",
    "references/core-context.md",
    "references/rule-registry.md",
    "references/pricing-and-profit.md",
    "references/research-and-sourcing.md",
    "references/partner-communication.md",
    "references/verification-and-risk.md",
    "references/platform-playbooks.md",
    "references/conflicts-and-evolution.md",
    "references/common-ai-mistakes.md",
    "references/source-freshness.md",
    "templates/partner-offer-ru.txt",
    "templates/internal-calculation.md",
    "templates/pre-payment-checklist.md",
    "scripts/calculate_offer.py",
    "scripts/validate_partner_message.py",
]


def main() -> int:
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    missing = [rel for rel in REQUIRED if not (ROOT / rel).is_file()]
    add("required_files", not missing, ", ".join(missing))

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8") if (ROOT / "SKILL.md").is_file() else ""
    frontmatter = skill.split("---", 2)[1] if skill.startswith("---\n") and skill.count("---") >= 2 else ""
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.M)
    desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.M)
    name = name_match.group(1).strip() if name_match else ""
    desc = desc_match.group(1).strip() if desc_match else ""
    add("frontmatter", bool(frontmatter), "frontmatter missing" if not frontmatter else "")
    add("valid_name", bool(re.fullmatch(r"[a-z0-9-]+", name)), name)
    add("description_trigger", desc.startswith("Use when"), desc)
    add("frontmatter_under_1024", len(frontmatter) < 1024, str(len(frontmatter)))
    word_count = len(re.findall(r"\S+", skill))
    add("skill_word_count", word_count <= 900, str(word_count))

    partner_template = ROOT / "templates" / "partner-offer-ru.txt"
    if partner_template.exists():
        text = partner_template.read_text(encoding="utf-8")
        add("partner_template_no_double_bold", "**" not in text)
        add("partner_template_has_age", "Возраст" in text)
        add("partner_template_has_reconfirmation", "повторно подтверд" in text)

    test = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-p", "test_*.py", "-v"],
        text=True,
        capture_output=True,
    )
    add("unit_tests", test.returncode == 0, test.stdout + test.stderr)

    result = {"passed": all(bool(c["passed"]) for c in checks), "checks": checks}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
