"""AST-гейт: молчаливый `except` запрещён во всех tracked .py вне тестов.

Тихая подавленность проглатывает ошибки без следа — сбой невозможно
заметить. Запрещены тела из единственного `pass`, `return`, `continue`
или `break` без строки журнала. Разрешённая форма:

    except X as _exc:
        logging.getLogger(__name__).debug("suppressed %s", _exc)
"""

import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PREFIXES = ("tests/", ".agents/")


def _tracked_py() -> list[str]:
    out = subprocess.check_output(
        ["git", "ls-files", "-z", "*.py"], cwd=ROOT, timeout=60
    ).decode().split("\x00")
    return [n for n in out if n and not n.startswith(SKIP_PREFIXES)]


def test_no_silent_except_handlers():
    hits = []
    for name in _tracked_py():
        try:
            tree = ast.parse(
                (ROOT / name).read_text(encoding="utf-8-sig"), filename=name
            )
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ExceptHandler)
                and len(node.body) == 1
                and isinstance(
                    node.body[0],
                    (ast.Pass, ast.Return, ast.Continue, ast.Break),
                )
            ):
                hits.append(f"{name}:{node.lineno}")
    assert not hits, "silent except in live code: " + ", ".join(hits)
