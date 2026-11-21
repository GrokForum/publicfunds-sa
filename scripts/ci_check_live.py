#!/usr/bin/env python3
"""Run scripts/check_live.py and fail the process on a BREACH or a non-zero exit.

Check-only. Does not publish or push. Standard library only.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK_LIVE = ROOT / "scripts" / "check_live.py"


def decide(exit_code: int, output: str) -> int:
    """Return 1 when check_live failed or the output reports a BREACH."""
    if exit_code != 0 or "BREACH" in output:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    extra = list(sys.argv[1:] if argv is None else argv)
    proc = subprocess.run(
        [sys.executable, str(CHECK_LIVE), *extra],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    if out:
        sys.stdout.write(out if out.endswith("\n") else out + "\n")
    code = decide(proc.returncode, out)
    if code != 0 and "BREACH" not in out and proc.returncode == 0:
        print("LIVE CHECK FAILED (BREACH marker missing but treated as failure)", file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
