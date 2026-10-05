"""R103: urlopen()/urlretrieve() — явный timeout (зависший запрос не вешает набор)."""
import ast
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METHODS = {"urlopen", "urlretrieve"}


def _tracked_py():
    out = subprocess.run(
        ["git", "ls-files", "*.py"], cwd=ROOT, capture_output=True,
        text=True, timeout=60,
    )
    if out.returncode != 0:
        raise RuntimeError(f"git ls-files упал: {out.stderr.strip()}")
    return out.stdout.splitlines()


class UrlopenTimeoutTests(unittest.TestCase):
    def test_every_url_call_passes_timeout(self):
        for rel in _tracked_py():
            tree = ast.parse(
                (ROOT / rel).read_text(encoding="utf-8"), filename=rel,
            )
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                func = node.func
                if (
                    isinstance(func, ast.Attribute)
                    and func.attr in METHODS
                    and not any(k.arg == "timeout" for k in node.keywords)
                ):
                    self.fail(f"{rel}:{node.lineno} {func.attr} без timeout")


if __name__ == "__main__":
    unittest.main()
