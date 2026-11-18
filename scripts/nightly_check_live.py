#!/usr/bin/env python3
"""Nightly after-publish live check (CHG-2026-061, CSI-036, RB-12; site push input from CHG-2026-070).

Run it after `scripts/publish-public-data.sh --push` and then `scripts/publish_site_repo.py`, with both exit codes and
their saved output:

    scripts/publish-public-data.sh --push > data/publish-run.log 2>&1; echo $?
    uv run python scripts/publish_site_repo.py > data/site-publish.log 2>&1; echo $?     (only after a data exit 0)
    python3 scripts/nightly_check_live.py --publish-exit <code> --publish-log data/publish-run.log \
        --site-exit <code, or not-run> --site-log data/site-publish.log

It decides if the data publish pushed, and if the site push pushed. It runs the after-publish command from RB-12
(RAW_URL is the site repository's raw manifest since CHG-2026-070):

    python3 scripts/check_live.py --expect-local public-data/v1/manifest.json \
      --raw-url https://raw.githubusercontent.com/GrokForum/publicfunds-site/main/public-data/v1/manifest.json --wait 600

When it runs check_live (CHG-2026-069 section 4.5):
    - the site push pushed (also on a night when the data publish had nothing to commit);
    - the data publish pushed and the site push had no change;
    - the site push was blocked, failed, did not run after a data exit 0, or gave no known line. check_live still
      runs, so a stale live tree is visible.
    If neither push pushed (data: nothing to commit or only timestamps; site: no change), check_live is skipped.

Exit code of this wrapper, and what the routine does next:
    0 = check_live exit 0 (OK, or WARN only). Report any [WARN] lines and carry on.
    1 = check_live exit 1 (at least one [BREACH]). The wrapper reports it, runs the review-app health check
        (curl -s http://127.0.0.1:8765/healthz) and prints its result. Then stop. Never re-publish. Follow RB-12.
    2 = check failed: check_live exit 2 (bad command line, nothing checked), any other exit code, a crash, or the
        overall time limit. Also exit 2 when the wrapper cannot tell if the data publish pushed (no known log line, an
        unreadable log, an unexpected publish exit code, a git or ls-remote error, or origin/main has moved past
        the data commit), when a site push ran after a refused data publish, and for a bad wrapper command line or
        --help. Report it as a failed check and stop. Never report it as OK.
    3 = skipped: the logs or exit codes show positively that nothing was pushed. Only these cases:
        the data publish refused (exit 3 or 4) and the site push did not run; or the data publish had nothing to
        commit, only timestamps changed, or it committed with no push line and origin/main is still behind that data
        commit (run without --push), and the site push had no change. check_live is not run.
        The publish rules in the refresh skill still apply.

Read-only. Standard library only. It writes nothing, and it never runs the publish scripts or git push.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# CHG-2026-070: the site repository serves the site; its raw manifest is the git-host measuring point.
RAW_URL = "https://raw.githubusercontent.com/GrokForum/publicfunds-site/main/public-data/v1/manifest.json"
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
# Lines printed by scripts/publish_site_repo.py (thusa/site_repo.py), CHG-2026-070.
SITE_PUSHED_RE = re.compile(r"^site_publish: pushed ([0-9a-f]{40})\s*$", re.M)
SITE_NOCHANGE_RE = re.compile(r"^site_publish: no change; nothing pushed\s*$", re.M)
SITE_ACTION_RE = re.compile(r"^ACTION: site publish (?:blocked|failed) \(.*\)\s*$", re.M)
SITE_NOT_RUN = "not-run"


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


def is_ancestor(older: str, newer: str, run=subprocess.run) -> bool | None:
    """git merge-base --is-ancestor (read-only). True or False, or None if git cannot tell (for example an unknown commit)."""
    try:
        p = run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", older, newer], capture_output=True, text=True,
                timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return {0: True, 1: False}.get(p.returncode)


PUSHED, NOT_PUSHED, UNKNOWN = "pushed", "not pushed", "unknown"
# Publish script exit codes that mean a refusal: 3 = export refused, 4 = commit or push refused. Nothing is pushed.
REFUSED_EXITS = (3, 4)


def publish_pushed(exit_code: int, log_text: str | None, run=subprocess.run) -> tuple[str, str]:
    """Did the publish push? Returns (PUSHED | NOT_PUSHED | UNKNOWN, reason).

    NOT_PUSHED only when the exit code or the script's own log lines show it positively. Anything else is UNKNOWN,
    so a change in the log format can never turn the check off without a report.
    """
    if exit_code in REFUSED_EXITS:
        return NOT_PUSHED, f"publish exited {exit_code} (refused); nothing was pushed by the script"
    if exit_code != 0:
        return UNKNOWN, f"publish exited {exit_code}; cannot tell if it pushed"
    if log_text is None:
        return UNKNOWN, "publish output not readable; cannot tell if it pushed"
    if PUSHED_RE.search(log_text):
        return PUSHED, "publish script pushed to origin/main"
    nothing = NOTHING_RE.search(log_text)
    if nothing:
        return NOT_PUSHED, f"publish: {nothing.group(1)}; nothing was pushed"
    m = COMMITTED_RE.search(log_text)
    if not m:
        return UNKNOWN, "no known commit, push or no-change line in the publish output; cannot tell if it pushed"
    short = m.group(1)
    # Committed with no push line: the script ran without --push. Compare origin/main with the data commit.
    full = local_sha(short, run)
    if not full:
        return UNKNOWN, f"publish committed {short}, but git cannot read that commit; cannot tell if it was pushed"
    remote = remote_main_sha(run)
    if not remote:
        return UNKNOWN, f"publish committed {short}, but git ls-remote failed; cannot tell if it was pushed"
    if full == remote:
        return PUSHED, f"publish committed {short} without a push; origin/main equals that commit (pushed outside the script)"
    behind = is_ancestor(remote, full, run)
    if behind is True:
        return NOT_PUSHED, f"publish committed {short} without --push; origin/main is still behind it, so it was not pushed"
    if behind is None:
        return UNKNOWN, f"publish committed {short}; origin/main is a commit git cannot compare; cannot tell if it was pushed"
    if is_ancestor(full, remote, run) is True:
        return UNKNOWN, f"publish committed {short}; origin/main has moved past it; cannot tell if it was pushed"
    return UNKNOWN, f"publish committed {short}; origin/main does not contain it and is not behind it; cannot tell if it was pushed"


SITE_PUSHED, SITE_NO_CHANGE, SITE_NOT_PUSHED, SITE_DID_NOT_RUN = "pushed", "no change", "no push", "did not run"
# publish_site_repo.py exit codes: 0 = pushed or no change, 3 = blocked, 4 = failed (CHG-2026-070).
SITE_BLOCKED_EXIT, SITE_FAILED_EXIT = 3, 4


def site_pushed(site_exit: str, log_text: str | None) -> tuple[str, str]:
    """Did the site push push? Returns (SITE_PUSHED | SITE_NO_CHANGE | SITE_NOT_PUSHED | SITE_DID_NOT_RUN, reason).

    SITE_NOT_PUSHED covers blocked, failed and unknown results: in all of them check_live still runs (section 4.5)."""
    if site_exit == SITE_NOT_RUN:
        return SITE_DID_NOT_RUN, "site push did not run"
    code = int(site_exit)
    action = SITE_ACTION_RE.search(log_text or "")
    action_text = f": {_clip(action.group(0))}" if action else ""
    if code == SITE_BLOCKED_EXIT:
        return SITE_NOT_PUSHED, f"site push exited 3 (blocked; nothing pushed){action_text}"
    if code == SITE_FAILED_EXIT:
        return SITE_NOT_PUSHED, f"site push exited 4 (failed){action_text}"
    if code != 0:
        return SITE_NOT_PUSHED, f"site push exited {code}; cannot tell if it pushed"
    if log_text is None:
        return SITE_NOT_PUSHED, "site push output not readable; cannot tell if it pushed"
    m = SITE_PUSHED_RE.search(log_text)
    if m:
        return SITE_PUSHED, f"site push pushed {m.group(1)[:12]}"
    if SITE_NOCHANGE_RE.search(log_text):
        return SITE_NO_CHANGE, "site push: no change; nothing pushed"
    return SITE_NOT_PUSHED, "no known pushed or no-change line in the site push output; cannot tell if it pushed"


def _site_exit_arg(value: str) -> str:
    if value == SITE_NOT_RUN or re.fullmatch(r"-?\d{1,3}", value or ""):
        return value
    raise argparse.ArgumentTypeError("an exit code or not-run")


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
    ap.add_argument("--site-exit", type=_site_exit_arg, required=True,
                    help="exit code of scripts/publish_site_repo.py, or not-run")
    ap.add_argument("--site-log", type=Path, required=True, help="file with the saved output of the site push")
    try:
        a = ap.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 0:      # --help: nothing was checked, so it must never read as OK
            out("check_live: FAILED CHECK (help shown; nothing checked)")
        else:
            out("check_live: FAILED CHECK (bad command line for the wrapper; nothing checked)")
        out("NEXT: stop. Report this as a failed check, not as OK.")
        return EXIT_FAILED
    try:
        log_text = a.publish_log.read_text(encoding="utf-8", errors="replace")
    except OSError:
        log_text = None
    site_log = None
    if a.site_exit != SITE_NOT_RUN:
        try:
            site_log = a.site_log.read_text(encoding="utf-8", errors="replace")
        except OSError:
            site_log = None
    state, why = publish_pushed(a.publish_exit, log_text, run)
    site_state, site_why = site_pushed(a.site_exit, site_log)
    out(f"site_publish: {site_state} ({site_why})")
    if a.publish_exit != 0 and site_state != SITE_DID_NOT_RUN:
        out(f"check_live: FAILED CHECK (a site push ran after data publish exit {a.publish_exit}; the site push must "
            "run only after a data publish exit 0)")
        out("NEXT: stop. Report this as a failed check, not as OK. Check by hand what went live.")
        return EXIT_FAILED
    # Skip only when neither push pushed: a refused data publish (no site push), or no data push and no site change.
    if state == NOT_PUSHED and (a.publish_exit != 0 or site_state == SITE_NO_CHANGE):
        out(f"check_live: SKIPPED ({why}; {site_why})")
        out("NEXT: check_live not run. Follow the refresh skill for the publish result.")
        return EXIT_SKIPPED
    if state == UNKNOWN:
        out(f"check_live: FAILED CHECK ({why})")
        out("NEXT: stop. Report this as a failed check, not as OK. Check by hand if new data went live.")
        return EXIT_FAILED
    if site_state in (SITE_NOT_PUSHED, SITE_DID_NOT_RUN):
        out(f"check_live: running ({why}; {site_why}; the live check still runs so a stale live tree is visible)")
    else:
        out(f"check_live: running ({why}; {site_why})")
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
