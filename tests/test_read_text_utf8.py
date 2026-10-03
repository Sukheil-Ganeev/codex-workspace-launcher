"""R093: read_text() — явный encoding (не locale машины)."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
READERS = ["tests/test_launcher.py"]


class ReadTextUtf8Tests(unittest.TestCase):
    def test_every_read_text_passes_encoding(self):
        for rel in READERS:
            for i, line in enumerate(
                (ROOT / rel).read_text(encoding="utf-8").splitlines(), 1
            ):
                if "read_text(" in line and "encoding=" not in line:
                    self.fail(f"{rel}:{i} read_text без encoding: {line.strip()}")


if __name__ == "__main__":
    unittest.main()
