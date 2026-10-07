"""AST-гейт: mkdir/makedirs обязан иметь exist_ok=True во всех tracked .py."""
import ast
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _is_mkdir_call(node: ast.Call) -> bool:
    if isinstance(node.func, ast.Name) and node.func.id == "makedirs":
        return True
    if isinstance(node.func, ast.Attribute) and node.func.attr in ("mkdir", "makedirs"):
        if node.func.attr == "mkdir" and isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
            return False  # os.mkdir не принимает exist_ok
        return True
    return False


class TestNoUnboundedMkdir(unittest.TestCase):
    def test_mkdir_calls_use_exist_ok(self):
        files = subprocess.run(
            ["git", "ls-files", "-z", "*.py"],
            cwd=ROOT,
            capture_output=True,
            timeout=60,
        ).stdout.decode("utf-8").split("\0")
        hits = []
        for rel in files:
            if not rel or rel.startswith(".agents/"):
                continue
            path = ROOT / rel
            tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=rel)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and _is_mkdir_call(node):
                    if not any(kw.arg == "exist_ok" for kw in node.keywords):
                        hits.append(f"{rel}:{node.lineno}")
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
