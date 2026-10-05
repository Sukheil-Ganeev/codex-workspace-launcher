from __future__ import annotations

import argparse
import pathlib
import re
import sys


FORBIDDEN_EXTERNAL = (
    "procurement",
    "закуп",
    "sourceoffer",
    "source url",
    "инвестор",
    "наша прибыль",
    "owner profit",
)


def validate(text: str, mode: str, messenger: str, language: str = "ru") -> list[str]:
    errors: list[str] = []
    lowered = text.lower()
    if mode in {"agent", "client"}:
        for word in FORBIDDEN_EXTERNAL:
            if word in lowered:
                errors.append(f"INTERNAL_FIELD_LEAK:{word}")
        if re.search(r"\bSEC[A-Z]{1,3}\d{1,2}[A-Z]?\b|source[_ ]?offer|physical[_ ]?seat[_ ]?key", text, re.IGNORECASE):
            errors.append("RAW_PROVIDER_CODE_LEAK")
    if mode == "client" and re.search(r"\+(10|15|20|30)%|базов\w* цен|наша цена", lowered):
        errors.append("CLIENT_PRICE_LAYER_LEAK")
    if re.search(r"\bпродан[оаы]?\b", lowered) and "explicit sold" in lowered:
        pass
    if "aed" not in lowered and not re.search(r"цена\s+не\s+доказана", lowered):
        errors.append("AED_OR_NO_PRICE_EXPLANATION_REQUIRED")
    if "подтверж" not in lowered and "confirm" not in lowered:
        errors.append("RECHECK_WARNING_REQUIRED")
    if messenger == "whatsapp" and len(text) > 500 and "───────────────" not in text:
        errors.append("WHATSAPP_SEPARATOR_REQUIRED")
    if "official platinum" in lowered and re.search(r"official platinum\s*[—:-]\s*category", lowered):
        errors.append("PLATINUM_IS_NOT_CATEGORY")
    if language == "ru" and len(re.findall(r"[А-Яа-яЁё]", text)) < 10:
        errors.append("RUSSIAN_DEFAULT_REQUIRED")
    if language == "ru" and re.search(r"(?im)^(section|row|seat|price|status)\s*:", text):
        errors.append("RUSSIAN_LABELS_REQUIRED")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=pathlib.Path)
    parser.add_argument("--mode", choices=("internal", "agent", "client"), required=True)
    parser.add_argument("--messenger", choices=("whatsapp", "telegram", "plain"), default="plain")
    parser.add_argument("--language", choices=("ru", "en", "ar"), default="ru")
    args = parser.parse_args()
    errors = validate(args.path.read_text(encoding="utf-8"), args.mode, args.messenger, args.language)
    if errors:
        print("FAIL " + " ".join(errors))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
