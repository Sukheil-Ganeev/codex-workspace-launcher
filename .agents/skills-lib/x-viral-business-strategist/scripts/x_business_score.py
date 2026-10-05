#!/usr/bin/env python3
"""Business-aware X/Twitter post scorer.

This helper is intentionally simple and local. It estimates whether a draft has
clear business value, proof, a reply/repost reason, and low negative-signal risk.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Result:
    viral_score: int
    business_score: int
    risk: str
    confidence: str
    positives: list[str]
    risks: list[str]
    suggestions: list[str]


def has(pattern: str, text: str) -> bool:
    return re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE) is not None


def count(pattern: str, text: str) -> int:
    return len(re.findall(pattern, text, flags=re.IGNORECASE | re.MULTILINE))


def clamp(value: int, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, value))


def analyze(text: str) -> Result:
    body = text.strip()
    words = len(re.findall(r"\b[\w'-]+\b", body))
    urls = count(r"https?://|www\.", body)
    questions = body.count("?")
    numbers = count(r"\b\d+(?:[.,]\d+)?%?\b", body)
    bullets = count(r"^\s*(?:[-*]|\d+[.)])\s+", body)
    has_proof = has(r"\b(proof|result|results|case|benchmark|data|source|example|screenshot|demo|built|shipped|tested|learned)\b", body)
    has_value = has(r"\b(checklist|template|framework|guide|steps|how to|mistake|lesson|playbook|system|process)\b", body)
    has_offer = has(r"\b(help|book|dm|audit|call|buy|sell|lead|client|customer|offer|service|tool)\b", body)
    has_spam = has(r"\b(guaranteed|100x|free money|airdrop|follow me|like and repost|secret nobody knows)\b", body)
    has_attack = has(r"\b(idiot|stupid|scam|fraud|hate|destroyed|everyone is wrong)\b", body)
    has_media_hint = has(r"\b(video|screenshot|chart|image|demo|screen recording|photo)\b", body)

    viral = 35
    business = 30
    positives: list[str] = []
    risks: list[str] = []
    suggestions: list[str] = []

    if 60 <= len(body) <= 280:
        viral += 10
        positives.append("Core length is feed-friendly.")
    elif len(body) > 600:
        viral -= 10
        risks.append("Long post may hide the payoff; consider a thread.")

    if questions:
        viral += min(14, 7 * questions)
        positives.append("Question can trigger replies.")
    else:
        suggestions.append("Add one specific question or contrast to invite replies.")

    if numbers:
        viral += min(10, 4 * numbers)
        business += min(10, 4 * numbers)
        positives.append("Numbers increase specificity.")

    if bullets or has_value:
        viral += 8
        business += 14
        positives.append("Reusable value improves bookmark/repost potential.")
    else:
        suggestions.append("Add a tiny checklist, framework, or concrete lesson.")

    if has_proof:
        viral += 8
        business += 18
        positives.append("Proof/result signal supports trust.")
    else:
        suggestions.append("Add proof: result, artifact, screenshot, benchmark, or concrete example.")

    if has_offer:
        business += 12
        positives.append("Business intent is visible.")
    else:
        suggestions.append("Clarify the business outcome or who this helps.")

    if has_media_hint:
        viral += 8
        positives.append("Media hint can improve dwell and clarity.")

    if urls:
        viral -= 10
        risks.append("External link in the main post can reduce native distribution.")
        suggestions.append("Move external links to a reply or profile when possible.")

    if has_spam:
        viral -= 14
        business -= 12
        risks.append("Spam-like wording can trigger negative signals.")

    if has_attack:
        viral -= 8
        business -= 10
        risks.append("Aggressive wording may create mute/block/report risk.")

    if words < 8:
        viral -= 10
        business -= 8
        risks.append("Draft is too thin to carry trust or context.")

    risk_count = len(risks)
    risk = "low" if risk_count == 0 else "medium" if risk_count <= 2 else "high"
    confidence = "medium" if len(body) >= 40 else "low"

    return Result(
        viral_score=clamp(viral),
        business_score=clamp(business),
        risk=risk,
        confidence=confidence,
        positives=positives[:6],
        risks=risks[:6],
        suggestions=suggestions[:6],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", default="")
    parser.add_argument("--file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    text = args.text
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    result = analyze(text)
    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
        return

    print(f"Viral score: {result.viral_score}/100")
    print(f"Business score: {result.business_score}/100")
    print(f"Risk: {result.risk}")
    print(f"Confidence: {result.confidence}")
    if result.positives:
        print("\nPositive signals:")
        for item in result.positives:
            print(f"- {item}")
    if result.risks:
        print("\nRisks:")
        for item in result.risks:
            print(f"- {item}")
    if result.suggestions:
        print("\nSuggestions:")
        for item in result.suggestions:
            print(f"- {item}")


if __name__ == "__main__":
    main()
