#!/usr/bin/env python3
"""Lint a partner-facing WhatsApp offer for common ticketing-business mistakes."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ERROR_PATTERNS = [
    ("DOUBLE_ASTERISK", re.compile(r"\*\*"), "Use one asterisk on each side for WhatsApp bold."),
    (
        "INTERNAL_DATA",
        re.compile(
            r"закупоч|себестоим|наша прибыль|ваша прибыль|прибыль\s*[:=]|для марселя|не отправлять|"
            r"внутренн(?:ий|яя|ее)|bank/?fx reserve|internal reserve|procurement price|source status|supplier link",
            re.I,
        ),
        "Remove procurement, cost, profit, reserve or internal-only information.",
    ),
    ("DIRECT_URL", re.compile(r"https?://|www\.", re.I), "Remove procurement/source URLs unless Marsel explicitly requested them."),
]

WARNING_PATTERNS = [
    ("UNSUPPORTED_GUARANTEE", re.compile(r"гарантирован|100%.*(?:есть|получ)", re.I), "Verify that the guarantee is documented for this exact product."),
    (
        "OFFICIAL_PLATINUM_INCLUSIONS",
        re.compile(r"official platinum[\s\S]{0,240}(?:lounge|питани|напитк|parking|парков|vip entrance)", re.I),
        "Official Platinum is not automatically a hospitality package; verify every inclusion.",
    ),
]


def issue(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def validate(text: str, mode: str = "offer", allow_url: bool = False) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    for code, pattern, message in ERROR_PATTERNS:
        if code == "DIRECT_URL" and allow_url:
            continue
        if pattern.search(text):
            errors.append(issue(code, message))

    if mode == "offer":
        if not re.search(r"стоимост|price", text, re.I):
            errors.append(issue("PRICE_MISSING", "A partner offer should show the final selling price or clearly say price is pending."))
        if not re.search(r"возраст|дет|несовершеннолет|age|adult|требует подтверждения", text, re.I):
            errors.append(issue("AGE_RULE_MISSING", "Add event-specific age/child/accompanying-adult rules or say they require confirmation."))
        if not re.search(r"повторно подтверд|подтвердить.*перед оплат|наличи.{0,80}измен|subject to change|reconfirm", text, re.I | re.S):
            errors.append(issue("RECONFIRMATION_MISSING", "Add live availability/final-price reconfirmation before payment."))

    for code, pattern, message in WARNING_PATTERNS:
        if pattern.search(text):
            warnings.append(issue(code, message))

    return {"passed": not errors, "mode": mode, "errors": errors, "warnings": warnings}


def main() -> int:
    p = argparse.ArgumentParser(description="Validate a partner-facing event-ticket WhatsApp message.")
    p.add_argument("file", type=Path)
    p.add_argument("--mode", choices=("offer", "status"), default="offer")
    p.add_argument("--allow-url", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    try:
        text = args.file.read_text(encoding="utf-8")
    except OSError as exc:
        p.error(str(exc))

    result = validate(text, mode=args.mode, allow_url=args.allow_url)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("PASS" if result["passed"] else "FAIL")
        for item in result["errors"]:
            print(f"ERROR {item['code']}: {item['message']}")
        for item in result["warnings"]:
            print(f"WARN  {item['code']}: {item['message']}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
