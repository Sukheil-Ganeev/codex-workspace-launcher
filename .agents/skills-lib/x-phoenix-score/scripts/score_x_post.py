#!/usr/bin/env python3
"""Deterministic Phoenix-style scorer for X post drafts."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


WEIGHTS = {
    "favorite": 1.0,
    "reply": 13.5,
    "repost": 20.0,
    "bookmark": 10.0,
    "profile_click": 12.0,
    "link_click": 11.0,
    "share": 8.0,
    "quote": 15.0,
}

NEGATIVE_WEIGHTS = {
    "not_interested": 18.0,
    "mute_author": 22.0,
    "block_author": 30.0,
    "report": 40.0,
}


@dataclass(frozen=True)
class Features:
    text: str
    chars: int
    words: int
    urls: int
    hashtags: int
    mentions: int
    questions: int
    exclamations: int
    numbers: int
    bullets: int
    has_media_hint: bool
    has_video_hint: bool
    has_thread_hint: bool
    has_proof_hint: bool
    has_spam_hint: bool
    has_controversy_hint: bool


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def sigmoid(value: float) -> float:
    return 1 / (1 + math.exp(-value))


def count(pattern: str, text: str) -> int:
    return len(re.findall(pattern, text, flags=re.IGNORECASE | re.MULTILINE))


def extract_features(text: str) -> Features:
    lower = text.lower()
    return Features(
        text=text.strip(),
        chars=len(text.strip()),
        words=len(re.findall(r"\b[\w'-]+\b", text)),
        urls=count(r"https?://|www\.", text),
        hashtags=count(r"(?<!\w)#\w+", text),
        mentions=count(r"(?<!\w)@\w+", text),
        questions=text.count("?"),
        exclamations=text.count("!"),
        numbers=count(r"\b\d+(?:[.,]\d+)?%?\b", text),
        bullets=count(r"^\s*(?:[-*]|\d+[.)])\s+", text),
        has_media_hint=bool(re.search(r"\b(image|screenshot|chart|graph|video|demo|clip|photo|visual)\b", lower)),
        has_video_hint=bool(re.search(r"\b(video|demo|clip|watch|recording)\b", lower)),
        has_thread_hint=bool(re.search(r"\b(thread|1/)\b", lower)),
        has_proof_hint=bool(re.search(r"\b(proof|data|case study|benchmark|result|results|source|example|template|checklist|framework|steps)\b", lower)),
        has_spam_hint=bool(re.search(r"\b(giveaway|airdrop|free money|follow me|like and repost|100x|guaranteed)\b", lower)),
        has_controversy_hint=bool(re.search(r"\b(scam|fraud|hate|idiot|stupid|never|always|everyone is wrong|destroyed)\b", lower)),
    )


def length_quality(chars: int) -> float:
    if chars == 0:
        return 0.0
    if 90 <= chars <= 220:
        return 1.0
    if 45 <= chars < 90:
        return 0.78
    if 221 <= chars <= 420:
        return 0.82
    if 421 <= chars <= 900:
        return 0.62
    return 0.42


def predict(features: Features) -> dict[str, float]:
    lq = length_quality(features.chars)
    specificity = clamp(0.16 + 0.08 * features.numbers + 0.10 * features.has_proof_hint + 0.04 * features.bullets, 0, 0.55)
    media = 0.12 if features.has_media_hint else 0.0
    url_penalty = 0.12 * features.urls
    hashtag_penalty = max(0, features.hashtags - 1) * 0.04
    spam_penalty = 0.20 if features.has_spam_hint else 0.0
    controversy = 0.14 if features.has_controversy_hint else 0.0

    reply = clamp(0.12 + 0.24 * min(features.questions, 2) + 0.08 * specificity + 0.05 * controversy - spam_penalty)
    repost = clamp(0.16 + 0.18 * specificity + 0.08 * media + 0.08 * lq - url_penalty - hashtag_penalty - spam_penalty)
    bookmark = clamp(0.10 + 0.22 * specificity + 0.07 * features.bullets + 0.08 * features.has_thread_hint - 0.04 * features.questions)
    profile_click = clamp(0.12 + 0.14 * specificity + 0.06 * media + 0.05 * features.mentions - spam_penalty)
    link_click = clamp(0.05 + 0.38 * min(features.urls, 1) + 0.08 * specificity)
    favorite = clamp(0.22 + 0.16 * lq + 0.06 * media + 0.04 * min(features.exclamations, 1) - spam_penalty)
    dwell = clamp(0.16 + 0.22 * lq + 0.12 * specificity + 0.08 * media + 0.05 * features.has_thread_hint)
    vqv = clamp(0.10 + 0.55 * features.has_video_hint)
    share = clamp(0.10 + 0.16 * specificity + 0.10 * media + 0.05 * lq - spam_penalty)
    quote = clamp(0.08 + 0.12 * controversy + 0.12 * specificity + 0.05 * features.questions - spam_penalty)
    follow_author = clamp(0.08 + 0.18 * specificity + 0.10 * media - spam_penalty)

    not_interested = clamp(0.03 + 0.08 * features.has_spam_hint + 0.06 * features.has_controversy_hint + hashtag_penalty)
    mute_author = clamp(0.01 + 0.06 * features.has_spam_hint + 0.06 * features.has_controversy_hint)
    block_author = clamp(0.005 + 0.04 * features.has_spam_hint + 0.07 * features.has_controversy_hint)
    report = clamp(0.002 + 0.02 * features.has_spam_hint + 0.05 * features.has_controversy_hint)

    return {
        "favorite": round(favorite, 3),
        "reply": round(reply, 3),
        "repost": round(repost, 3),
        "bookmark": round(bookmark, 3),
        "profile_click": round(profile_click, 3),
        "link_click": round(link_click, 3),
        "dwell": round(dwell, 3),
        "vqv": round(vqv, 3),
        "share": round(share, 3),
        "quote": round(quote, 3),
        "follow_author": round(follow_author, 3),
        "not_interested": round(not_interested, 3),
        "block_author": round(block_author, 3),
        "mute_author": round(mute_author, 3),
        "report": round(report, 3),
    }


def build_breakdown(predictions: dict[str, float]) -> dict[str, float]:
    negative = sum(predictions[k] * weight for k, weight in NEGATIVE_WEIGHTS.items())
    return {
        "favoriteWeighted": round(predictions["favorite"] * WEIGHTS["favorite"], 3),
        "replyWeighted": round(predictions["reply"] * WEIGHTS["reply"], 3),
        "repostWeighted": round(predictions["repost"] * WEIGHTS["repost"], 3),
        "bookmarkWeighted": round(predictions["bookmark"] * WEIGHTS["bookmark"], 3),
        "profileClickWeighted": round(predictions["profile_click"] * WEIGHTS["profile_click"], 3),
        "linkClickWeighted": round(predictions["link_click"] * WEIGHTS["link_click"], 3),
        "shareWeighted": round(predictions["share"] * WEIGHTS["share"], 3),
        "quoteWeighted": round(predictions["quote"] * WEIGHTS["quote"], 3),
        "negativeTotal": round(negative, 3),
    }


def score(predictions: dict[str, float], breakdown: dict[str, float], features: Features) -> int:
    positive_total = (
        breakdown["favoriteWeighted"]
        + breakdown["replyWeighted"]
        + breakdown["repostWeighted"]
        + breakdown["bookmarkWeighted"]
        + breakdown["profileClickWeighted"]
        + breakdown["linkClickWeighted"]
        + breakdown["shareWeighted"]
        + breakdown["quoteWeighted"]
        + predictions["dwell"] * 8.0
        + predictions["vqv"] * 10.0
        + predictions["follow_author"] * 8.0
    )
    max_positive = sum(WEIGHTS.values()) + 8.0 + 10.0 + 8.0
    base = (positive_total / max_positive) * 100
    penalty = breakdown["negativeTotal"] * 1.6
    if features.urls:
        penalty += 7.0
    if features.hashtags > 2:
        penalty += (features.hashtags - 2) * 2.5
    return int(round(max(0, min(100, base - penalty + 34))))


def verdict(score_value: int) -> str:
    if score_value >= 90:
        return "Exceptional draft with multiple high-weight engagement paths."
    if score_value >= 70:
        return "Strong draft with good weighted engagement potential."
    if score_value >= 50:
        return "Average draft with some useful signals but missing stronger drivers."
    if score_value >= 30:
        return "Below average draft with weak or diluted engagement signals."
    return "Low distribution likely unless the hook and value are strengthened."


def signal(type_: str, label: str, detail: str) -> dict[str, str]:
    return {"type": type_, "label": label, "detail": detail}


def build_signals(features: Features, predictions: dict[str, float], breakdown: dict[str, float]) -> list[dict[str, str]]:
    signals: list[dict[str, str]] = []
    if predictions["repost"] >= 0.32:
        signals.append(signal("positive", "Repost potential", f"Reposts carry 20.0x weight and this post has a self-contained idea or proof signal."))
    if predictions["reply"] >= 0.34:
        signals.append(signal("positive", "Reply driver", "Questions and debate hooks can matter because replies carry 13.5x weight."))
    if predictions["bookmark"] >= 0.28:
        signals.append(signal("positive", "Bookmark value", "Concrete steps, proof, or frameworks improve the 10.0x bookmark path."))
    if features.has_media_hint:
        signals.append(signal("positive", "Media/dwell support", "Native media can lift dwell time and make the post easier to reshare."))
    if features.urls:
        signals.append(signal("warning", "External link drag", "External links can reduce reach by roughly 30-50%; consider putting the link in a reply."))
    if features.hashtags > 2:
        signals.append(signal("warning", "Hashtag clutter", "Many hashtags add little ranking value and can make the post look spammy."))
    if breakdown["negativeTotal"] >= 3:
        signals.append(signal("negative", "Negative-signal risk", "Spammy or inflammatory wording raises Not Interested, mute, block, or report risk."))
    if not signals:
        signals.append(signal("warning", "Weak distinctive signal", "The post needs a clearer reason to reply, repost, bookmark, or click the profile."))
    return signals[:6]


def build_suggestions(features: Features, predictions: dict[str, float]) -> list[str]:
    suggestions: list[str] = []
    if predictions["reply"] < 0.30:
        suggestions.append("Add one specific question or contrast to activate the 13.5x reply path.")
    if predictions["repost"] < 0.30:
        suggestions.append("Make the core idea more self-contained so someone can repost it without extra context.")
    if predictions["bookmark"] < 0.25:
        suggestions.append("Add a small checklist, numbered framework, data point, or reusable template to improve bookmark value.")
    if features.urls:
        suggestions.append("Move the external link to the first reply and keep the main post native.")
    if features.hashtags > 2:
        suggestions.append("Cut hashtags to zero or one highly relevant tag.")
    if features.has_spam_hint or features.has_controversy_hint:
        suggestions.append("Reduce hype or inflammatory wording to lower negative-signal risk.")
    if not features.has_media_hint and features.words > 25:
        suggestions.append("Consider adding a screenshot, chart, or short video to improve dwell and repost clarity.")
    return suggestions[:4]


def analyze(text: str) -> dict[str, Any]:
    features = extract_features(text)
    predictions = predict(features)
    breakdown = build_breakdown(predictions)
    score_value = score(predictions, breakdown, features)
    return {
        "score": score_value,
        "verdict": verdict(score_value),
        "predictions": predictions,
        "breakdown": breakdown,
        "signals": build_signals(features, predictions, breakdown),
        "suggestions": build_suggestions(features, predictions),
        "caveat": "Directional estimate using published/open-source-style weights and heuristics, not X's private production ranking model.",
    }


def format_report(result: dict[str, Any]) -> str:
    lines = [
        f"Score: {result['score']}/100",
        f"Verdict: {result['verdict']}",
        "",
        "Weighted breakdown:",
    ]
    for key, value in result["breakdown"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("Signals:")
    for item in result["signals"]:
        lines.append(f"- {item['type']}: {item['label']} - {item['detail']}")
    lines.append("")
    lines.append("Suggestions:")
    for item in result["suggestions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append(f"Caveat: {result['caveat']}")
    return "\n".join(lines)


def read_input(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if args.file is not None:
        return Path(args.file).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("Provide --text, --file, or stdin.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Score an X post draft using Phoenix-style weights.")
    parser.add_argument("--text", help="Post text to score.")
    parser.add_argument("--file", help="UTF-8 text file containing the post.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a text report.")
    args = parser.parse_args()

    text = read_input(args).strip()
    if re.match(r"^https://(x|twitter)\.com/", text, flags=re.IGNORECASE):
        raise SystemExit("This script scores post text. Extract the primary post body from the URL first.")
    if not text:
        raise SystemExit("Post text is empty.")

    result = analyze(text)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_report(result))


if __name__ == "__main__":
    main()
