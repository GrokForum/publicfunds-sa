#!/usr/bin/env python3
"""Nightly after-publish live check (CHG-2026-061, CSI-036, RB-12).

Run it after `scripts/publish-public-data.sh --push`, with that script's exit code and its saved output:

    scripts/publish-public-data.sh --push > data/publish-run.log 2>&1; echo $?
    python3 scripts/nightly_check_live.py --publish-exit <code> --publish-log data/publish-run.log

It decides if the publish pushed. If it did, it runs the after-publish command from RB-12 (unchanged):

    python3 scripts/check_live.py --expect-local public-data/v1/manifest.json \
      --raw-url https://raw.githubusercontent.com/GrokForum/publicfunds-sa/main/public-data/v1/manifest.json --wait 600

Exit code of this wrapper, and what the routine does next:
    0 = check_live exit 0 (OK, or WARN only). Report any [WARN] lines and carry on.
    1 = check_live exit 1 (at least one [BREACH]). The wrapper reports it, runs the review-app health check
        (curl -s http://127.0.0.1:8765/healthz) and prints its result. Then stop. Never re-publish. Follow RB-12.
    2 = check failed: check_live exit 2 (bad command line, nothing checked), any other exit code, a crash, or the
        overall time limit. Report it as a failed check and stop. Never report it as OK.
    3 = skipped: the publish did not push (it exited non-zero, had nothing to commit, or committed without a push).
        check_live is not run. The publish rules in the refresh skill still apply.

Read-only. Standard library only. It writes nothing, and it never runs the publish script or git push.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_URL = "https://raw.githubusercontent.com/GrokForum/publicfunds-sa/main/public-data/v1/manifest.json"
WAIT_S = 600
# RB-12: check_live has no total deadline (the 20 s timeout is per read), so call it under an overall limit.
OVERALL_TIMEOUT_S = WAIT_S + 600
HEALTHZ_CMD = ["curl", "-s", "http://127.0.0.1:8765/healthz"]
HEALTHZ_TIMEOUT_S = 30
MAX_ECHO = 300

EXIT_OK, EXIT_BREACH, EXIT_FAILED, EXIT_SKIPPED = 0, 1, 2, 3

# Lines printed by scripts/publish-public-data.sh (its log() helper).
_LOG = r"^\[publish-data \d\d:\d\d:\d\d SAST\] "
PUSHED_RE = re.compile(_LOG + r"pushed to origin/main\s*$", re.M)
COMMITTED_RE = re.compile(_LOG + r"committed ([0-9a-f]{7,40})\s*$", re.M)
NOTHING_RE = re.compile(_LOG + r"(no change in public-data/; nothing to commit|only timestamps changed; not committed)\s*$", re.M)


def check_live_cmd() -> list[str]:
    """The after-publish command from RB-12 and the CHG-2026-061 RFC, with this Python."""
    return [sys.executable, str(ROOT / "scripts" / "check_live.py"), "--expect-local", "public-data/v1/manifest.json",
            "--raw-url", RAW_URL, "--wait", str(WAIT_S)]


def remote_main_sha(run=subprocess.run) -> str | None:
    """Full SHA of main on origin (git ls-remote, read-only), or None if it cannot be read."""
    try:
        p = run(["git", "-C", str(ROOT), "ls-remote", "origin", "refs/heads/main"], capture_output=True, text=True,
                timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode != 0 or not p.stdout.strip():
        return None
    return p.stdout.split()[0]


def local_sha(short: str, run=subprocess.run) -> str | None:
    """Full SHA of a local commit, or None."""
    try:
        p = run(["git", "-C", str(ROOT), "rev-parse", "--verify", "--quiet", short + "^{commit}"],
                capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return p.stdout.strip() if p.returncode == 0 and p.stdout.strip() else None


def publish_pushed(exit_code: int, log_text: str | None, run=subprocess.run) -> tuple[bool, str]:
    """Did the publish push? Returns (pushed, reason). Fails closed: when in doubt, not pushed."""
    if exit_code != 0:
        return False, f"publish exited {exit_code}; nothing was pushed by the script"
    if log_text is None:
        return False, "publish output not readable; cannot confirm a push"
    if PUSHED_RE.search(log_text):
        return True, "publish script pushed to origin/main"
    if NOTHING_RE.search(log_text):
        return False, "publish had nothing to commit; nothing was pushed"
    m = COMMITTED_RE.search(log_text)
    if not m:
        return False, "no commit or push line in the publish output; cannot confirm a push"
    # Committed but the script did not push (run without --push). If the data commit is on origin/main anyway
    # (pushed outside the script), the live site still serves new data, so the check runs.
    full = local_sha(m.group(1), run)
    remote = remote_main_sha(run)
    if full and remote and full == remote:
        return True, f"publish committed {m.group(1)} without a push; origin/main equals that commit (pushed outside the script)"
    return False, f"publish committed {m.group(1)} but did not push; origin/main does not equal it"


def _clip(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= MAX_ECHO else text[:MAX_ECHO - 3] + "..."


def report_lines(output: str) -> list[str]:
    """The RESULT: line and any [BREACH] / [WARN] lines, for the nightly report."""
    return [l for l in output.splitlines() if l.startswith(("RESULT:", "[BREACH]", "[WARN]"))]


def run_check(run=subprocess.run) -> tuple[int, str]:
    """Run check_live. Returns (exit code, output); the code is -1 on a crash or on the overall time limit."""
    try:
        p = run(check_live_cmd(), cwd=str(ROOT), capture_output=True, text=True, timeout=OVERALL_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return -1, f"check_live did not finish within {OVERALL_TIMEOUT_S} s (overall limit)"
    except (OSError, subprocess.SubprocessError) as exc:
        return -1, f"check_live could not run ({type(exc).__name__})"
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def healthz(run=subprocess.run) -> str:
    try:
        p = run(HEALTHZ_CMD, capture_output=True, text=True, timeout=HEALTHZ_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return f"no answer within {HEALTHZ_TIMEOUT_S} s"
    except (OSError, subprocess.SubprocessError) as exc:
        return f"could not run ({type(exc).__name__})"
    body = _clip(p.stdout or "")
    return f"curl exit {p.returncode}; body: {body or '(empty)'}"


def main(argv: list[str] | None = None, run=subprocess.run, out=print) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], allow_abbrev=False)
    ap.add_argument("--publish-exit", type=int, required=True, help="exit code of the publish step")
    ap.add_argument("--publish-log", type=Path, required=True, help="file with the saved output of that run")
    try:
        a = ap.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 0:      # --help
            return EXIT_OK
        out("check_live: FAILED CHECK (bad command line for the wrapper; nothing checked)")
        out("NEXT: stop. Report this as a failed check, not as OK.")
        return EXIT_FAILED
    try:
        log_text = a.publish_log.read_text(encoding="utf-8", errors="replace")
    except OSError:
        log_text = None
    pushed, why = publish_pushed(a.publish_exit, log_text, run)
    if not pushed:
        out(f"check_live: SKIPPED ({why})")
        out("NEXT: check_live not run. Follow the refresh skill for the publish result.")
        return EXIT_SKIPPED
    out(f"check_live: running ({why})")
    code, output = run_check(run)
    lines = report_lines(output)
    for l in lines:
        out(l)
    if code == 0:
        out("check_live: exit 0 (OK, or WARN only)")
        out("NEXT: report any [WARN] lines and carry on.")
        return EXIT_OK
    if code == 1:
        out("check_live: exit 1 (BREACH). This is a breach, not a success.")
        out(f"healthz: {healthz(run)}")
        out("NEXT: stop. Do not re-publish to fix it. Follow RB-12.")
        return EXIT_BREACH
    if code == 2:
        out("check_live: exit 2 (bad command line; nothing was checked)")
    elif code == -1:
        out(f"check_live: FAILED CHECK ({_clip(output)})")
    else:
        out(f"check_live: FAILED CHECK (unexpected exit {code})")
    if code != -1 and not lines:
        tail = [l for l in output.splitlines() if l.strip()][-3:]
        for l in tail:
            out(f"check_live output: {_clip(l)}")
    out("NEXT: stop. Report this as a failed check, not as OK.")
    return EXIT_FAILED


if __name__ == "__main__":
    sys.exit(main())
