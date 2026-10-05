#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
result = subprocess.run(
    [sys.executable, "-m", "unittest", "discover", "-s", str(root / "tests"), "-p", "test_*.py", "-v"]
)
raise SystemExit(result.returncode)
