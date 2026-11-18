"""scripts/nightly_check_live.py (CHG-2026-061; site push input from CHG-2026-070): exit-code handling with a fake runner.
No network, no git push, no publish."""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("nightly_check_live", ROOT / "scripts" / "nightly_check_live.py")
ncl = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ncl)

HEAD = "a" * 40   # the data commit
OLD = "b" * 40    # origin/main before the data commit
NEW = "c" * 40    # origin/main after the data commit
PUSHED = ("[publish-data 03:20:30 SAST] exported: 4384965 bytes, 19 files\nevidence_guard: pass\n"
          "[publish-data 03:20:45 SAST] committed aaaaaaa\n[publish-data 03:20:50 SAST] pushed to origin/main\n")
COMMITTED_ONLY = ("[publish-data 03:20:30 SAST] exported: 4384965 bytes, 19 files\nevidence_guard: pass\n"
                  "[publish-data 03:20:45 SAST] committed aaaaaaa\n")
NOTHING = "evidence_guard: pass\n[publish-data 03:20:45 SAST] no change in public-data/; nothing to commit\n"
TIMESTAMPS = "evidence_guard: pass\n[publish-data 03:20:45 SAST] only timestamps changed; not committed\n"
OK_OUT = "[OK] home: 200\nRESULT: OK (checked 2026-11-17 03:31 SAST)\n"
WARN_OUT = "[OK] home: 200\n[WARN] manifest age: 31.0 h\nRESULT: WARN (checked 2026-11-17 03:31 SAST)\n"
BREACH_OUT = "[OK] home: 200\n[BREACH] sample municipalities.json: sha256 differs\nRESULT: BREACH (checked 2026-11-17 03:31 SAST)\n"


class FakeRun:
    """Stands in for subprocess.run. Records every command; never starts a process."""

    def __init__(self, check=(0, OK_OUT), remote=HEAD, local=HEAD, healthz=(0, '{"ok": true}'), raise_on=None,
                 ancestors=(), known=None):
        self.check, self.remote, self.local, self.healthz, self.raise_on = check, remote, local, healthz, raise_on
        self.ancestors = set(ancestors)            # (older, newer) pairs for git merge-base --is-ancestor
        self.known = set(known) if known is not None else {HEAD, OLD, NEW}
        self.calls = []

    def __call__(self, cmd, **kw):
        self.calls.append(list(cmd))
        kind = self.kind(cmd)
        if self.raise_on == kind:
            if kind == "check":
                raise subprocess.TimeoutExpired(cmd, kw.get("timeout"))
            raise OSError("boom")
        if kind == "check":
            code, out = self.check
            return subprocess.CompletedProcess(cmd, code, out, "")
        if kind == "healthz":
            return subprocess.CompletedProcess(cmd, self.healthz[0], self.healthz[1], "")
        if kind == "ls-remote":
            return subprocess.CompletedProcess(cmd, 0 if self.remote else 2, f"{self.remote}\trefs/heads/main\n" if self.remote else "", "")
        if kind == "merge-base":
            older, newer = cmd[-2], cmd[-1]
            if older not in self.known or newer not in self.known:
                return subprocess.CompletedProcess(cmd, 128, "", "fatal: Not a valid commit name")
            return subprocess.CompletedProcess(cmd, 0 if (older, newer) in self.ancestors else 1, "", "")
        if kind == "rev-parse":
            return subprocess.CompletedProcess(cmd, 0 if self.local else 1, (self.local or "") + "\n", "")
        raise AssertionError(f"unexpected command {cmd}")

    @staticmethod
    def kind(cmd):
        if cmd[0] == "curl":
            return "healthz"
        if cmd[0] == "git":
            return "ls-remote" if "ls-remote" in cmd else "merge-base" if "merge-base" in cmd else "rev-parse"
        if cmd[1].endswith("check_live.py"):
            return "check"
        return "other"

    def kinds(self):
        return [self.kind(c) for c in self.calls]


SITE_PUSHED = "site_publish: remote tip 0123456789ab accepted (gate 8)\nsite_publish: pushed " + "e" * 40 + "\n"
SITE_NOCHANGE = "site_publish: remote tip 0123456789ab accepted (gate 8)\nsite_publish: no change; nothing pushed\n"
SITE_BLOCKED = "ACTION: site publish blocked (unexpected remote commit)\n"
SITE_FAILED = "ACTION: site publish failed (push refused or failed; nothing changed by this run)\n"


def go_full(tmp_path, log, exit_code=0, site=None, **fake):
    """Run the wrapper. `site` is (site exit, site log) or "not-run". By default: not-run after a data publish exit
    other than 0, and a site push with no change after a data exit 0 (so the data result decides, as before)."""
    f = tmp_path / "publish-run.log"
    if log is not None:
        f.write_text(log)
    if site is None:
        site = "not-run" if exit_code != 0 else (0, SITE_NOCHANGE)
    sf = tmp_path / "site-publish.log"
    if site == "not-run":
        site_exit = "not-run"
    else:
        site_exit = str(site[0])
        if site[1] is not None:
            sf.write_text(site[1])
    run, lines = FakeRun(**fake), []
    code = ncl.main(["--publish-exit", str(exit_code), "--publish-log", str(f), "--site-exit", site_exit,
                     "--site-log", str(sf)], run=run, out=lines.append)
    return code, lines, run


def go(tmp_path, log, exit_code=0, **fake):
    """As go_full, with the first line (the site_publish: line) checked and removed."""
    code, lines, run = go_full(tmp_path, log, exit_code, **fake)
    assert lines[0].startswith("site_publish: ")
    return code, lines[1:], run


def test_command_is_the_rfc_command():
    cmd = ncl.check_live_cmd()
    assert cmd[0] == sys.executable and cmd[1] == str(ROOT / "scripts" / "check_live.py")
    assert cmd[2:] == ["--expect-local", "public-data/v1/manifest.json", "--raw-url",
                       "https://raw.githubusercontent.com/GrokForum/publicfunds-site/main/public-data/v1/manifest.json",
                       "--wait", "600"]
    assert ncl.HEALTHZ_CMD == ["curl", "-s", "http://127.0.0.1:8765/healthz"]
    assert ncl.OVERALL_TIMEOUT_S > ncl.WAIT_S


@pytest.mark.parametrize("out", [OK_OUT, WARN_OUT])
def test_exit_0_reports_and_carries_on(tmp_path, out):
    code, lines, run = go(tmp_path, PUSHED, check=(0, out))
    assert code == 0
    assert run.kinds() == ["check"]                       # no healthz, no git call when the script pushed
    assert any(l.startswith("RESULT:") for l in lines)
    assert ("[WARN] manifest age: 31.0 h" in lines) == (out == WARN_OUT)
    assert lines[-1].startswith("NEXT: report any [WARN] lines and carry on")


def test_exit_1_is_a_breach_runs_healthz_then_stops(tmp_path):
    code, lines, run = go(tmp_path, PUSHED, check=(1, BREACH_OUT))
    assert code == 1
    assert run.kinds() == ["check", "healthz"]
    assert "[BREACH] sample municipalities.json: sha256 differs" in lines
    assert any(l.startswith("RESULT: BREACH") for l in lines)
    assert any("breach, not a success" in l for l in lines)
    assert any(l.startswith("healthz: curl exit 0") and '{"ok": true}' in l for l in lines)
    assert lines[-1] == "NEXT: stop. Do not re-publish to fix it. Follow RB-12."
    assert not any("OK" == l.split()[-1] for l in lines)


def test_exit_1_healthz_failure_is_reported(tmp_path):
    code, lines, _ = go(tmp_path, PUSHED, check=(1, BREACH_OUT), healthz=(7, ""))
    assert code == 1 and any(l == "healthz: curl exit 7; body: (empty)" for l in lines)
    code, lines, _ = go(tmp_path, PUSHED, check=(1, BREACH_OUT), raise_on="healthz")
    assert code == 1 and any(l.startswith("healthz: could not run") for l in lines)


def test_exit_2_is_a_failed_check_and_stops(tmp_path):
    code, lines, run = go(tmp_path, PUSHED, check=(2, "usage: check_live.py ...\ncheck_live.py: error: argument --wait: must be at least 0 and at most 3600\n"))
    assert code == 2
    assert run.kinds() == ["check"]                       # RFC: no healthz on exit 2
    assert "check_live: exit 2 (bad command line; nothing was checked)" in lines
    assert any("must be at least 0" in l for l in lines)
    assert lines[-1] == "NEXT: stop. Report this as a failed check, not as OK."


@pytest.mark.parametrize("check", [(3, ""), (-9, ""), (120, "Traceback ...\n")])
def test_other_exit_codes_are_failed_checks(tmp_path, check):
    code, lines, _ = go(tmp_path, PUSHED, check=check)
    assert code == 2 and any(f"unexpected exit {check[0]}" in l for l in lines)


def test_time_limit_is_a_failed_check(tmp_path):
    code, lines, _ = go(tmp_path, PUSHED, raise_on="check")
    assert code == 2 and any("did not finish within" in l for l in lines)


@pytest.mark.parametrize("exit_code", [3, 4])
def test_publish_refused_skips(tmp_path, exit_code):
    code, lines, run = go(tmp_path, PUSHED, exit_code=exit_code)
    assert code == 3 and run.calls == []
    assert lines[0] == f"check_live: SKIPPED (publish exited {exit_code} (refused); nothing was pushed by the script; site push did not run)"


@pytest.mark.parametrize("exit_code", [1, 2, 5, 127, -1])
def test_unexpected_publish_exit_is_a_failed_check(tmp_path, exit_code):
    code, lines, run = go(tmp_path, PUSHED, exit_code=exit_code)
    assert code == 2 and run.calls == []
    assert lines[0].startswith("check_live: FAILED CHECK (") and "cannot tell" in lines[0]
    assert lines[-1].startswith("NEXT: stop. Report this as a failed check, not as OK.")


@pytest.mark.parametrize("log,word", [(NOTHING, "nothing to commit"), (TIMESTAMPS, "only timestamps changed")])
def test_nothing_committed_skips(tmp_path, log, word):
    code, lines, run = go(tmp_path, log)
    assert code == 3 and run.calls == [] and word in lines[0] and lines[0].startswith("check_live: SKIPPED")


def test_committed_without_push_and_origin_behind_skips(tmp_path):
    code, lines, run = go(tmp_path, COMMITTED_ONLY, remote=OLD, ancestors={(OLD, HEAD)})
    assert code == 3 and "check" not in run.kinds()
    assert lines[0].startswith("check_live: SKIPPED") and "origin/main is still behind it" in lines[0]


def test_unreadable_log_is_a_failed_check(tmp_path):
    code, lines, run = go(tmp_path, None)
    assert code == 2 and run.calls == [] and "not readable" in lines[0]


@pytest.mark.parametrize("log", [
    "",                                                                           # empty
    "evidence_guard: pass\n",                                                    # no publish line at all
    "[publish-data 03:20 SAST] pushed to origin/main\n",                         # changed time format
    "[publish 03:20:50 SAST] pushed to origin/main\n",                           # changed prefix
    "[publish-data 03:20:50 SAST] pushed to origin main\n",                      # changed wording
    "evidence_guard:   pushed to origin/main\npushed to origin/main\n",         # forged, not the script's own form
])
def test_no_known_log_line_is_a_failed_check(tmp_path, log):
    code, lines, run = go(tmp_path, log)
    assert code == 2 and run.calls == []
    assert lines[0].startswith("check_live: FAILED CHECK (no known commit, push or no-change line")


@pytest.mark.parametrize("fake,word", [
    ({"local": None}, "git cannot read that commit"),
    ({"remote": None}, "ls-remote failed"),
    ({"raise_on": "ls-remote"}, "ls-remote failed"),
    ({"raise_on": "rev-parse"}, "git cannot read that commit"),
    ({"remote": NEW, "raise_on": "merge-base"}, "git cannot compare"),
    ({"remote": "d" * 40}, "git cannot compare"),                         # origin/main not known locally
])
def test_git_errors_are_failed_checks(tmp_path, fake, word):
    code, lines, run = go(tmp_path, COMMITTED_ONLY, **fake)
    assert code == 2 and "check" not in run.kinds()
    assert lines[0].startswith("check_live: FAILED CHECK") and word in lines[0]


def test_origin_moved_past_the_data_commit_is_a_failed_check(tmp_path):
    code, lines, run = go(tmp_path, COMMITTED_ONLY, remote=NEW, ancestors={(HEAD, NEW)})
    assert code == 2 and "check" not in run.kinds()
    assert "origin/main has moved past it" in lines[0]


def test_origin_diverged_is_a_failed_check(tmp_path):
    code, lines, run = go(tmp_path, COMMITTED_ONLY, remote=NEW)
    assert code == 2 and "check" not in run.kinds()
    assert "does not contain it and is not behind it" in lines[0]


def test_committed_then_pushed_outside_the_script_runs_the_check(tmp_path):
    code, lines, run = go(tmp_path, COMMITTED_ONLY)
    assert code == 0 and run.kinds() == ["rev-parse", "ls-remote", "check"]
    assert "pushed outside the script" in lines[0]


def test_help_is_never_ok(capsys):
    lines = []
    assert ncl.main(["--help"], run=FakeRun(), out=lines.append) == 2
    assert lines == ["check_live: FAILED CHECK (help shown; nothing checked)",
                     "NEXT: stop. Report this as a failed check, not as OK."]


def test_help_from_the_command_line_exits_2():
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "nightly_check_live.py"), "--help"],
                       capture_output=True, text=True, timeout=60)
    assert p.returncode == 2 and "FAILED CHECK (help shown" in p.stdout


def test_bad_wrapper_command_line_is_a_failed_check(capsys):
    lines = []
    assert ncl.main(["--publish-exit", "x", "--publish-log", "f"], run=FakeRun(), out=lines.append) == 2
    assert lines[-1] == "NEXT: stop. Report this as a failed check, not as OK."
    for argv in (["--publish-exit", "0", "--publish-log", "f"],                                   # no site input
                 ["--publish-exit", "0", "--publish-log", "f", "--site-exit", "0"],               # no site log
                 ["--publish-exit", "0", "--publish-log", "f", "--site-exit", "pushed", "--site-log", "g"]):
        lines = []
        assert ncl.main(argv, run=FakeRun(), out=lines.append) == 2
        assert lines[0].startswith("check_live: FAILED CHECK (bad command line")


def test_script_never_publishes_or_pushes():
    text = (ROOT / "scripts" / "nightly_check_live.py").read_text()
    code = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
    body = code.split('"""', 2)[2]                        # skip the docstring, which names the publish command
    assert "publish-public-data.sh" not in body
    assert '"push"' not in body and "'push'" not in body


def _free_port():
    import socket
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.mark.parametrize("extra,want", [(["--wait", "3601"], 2), (None, 1)])
def test_real_check_live_exit_codes_no_network(tmp_path, monkeypatch, extra, want):
    """Real check_live, real subprocess, no outside network: a bad flag exits 2; a closed local port is a BREACH (1)."""
    script = str(ROOT / "scripts" / "check_live.py")
    if extra is None:
        extra = ["--site", f"http://127.0.0.1:{_free_port()}", "--retries", "0", "--wait", "0"]
    monkeypatch.setattr(ncl, "check_live_cmd", lambda: [sys.executable, script, *extra])
    monkeypatch.setattr(ncl, "HEALTHZ_CMD", [sys.executable, "-c", "print('healthz-stub')"])
    f = tmp_path / "publish-run.log"
    f.write_text(PUSHED)
    sf = tmp_path / "site-publish.log"
    sf.write_text(SITE_PUSHED)
    lines = []
    code = ncl.main(["--publish-exit", "0", "--publish-log", str(f), "--site-exit", "0", "--site-log", str(sf)],
                    out=lines.append)
    assert code == want
    if want == 1:
        assert any(l.startswith("[BREACH]") for l in lines) and any(l.startswith("RESULT: BREACH") for l in lines)
        assert "healthz: curl exit 0; body: healthz-stub" in lines
    else:
        assert "check_live: exit 2 (bad command line; nothing was checked)" in lines


# CHG-2026-070 (CHG-2026-069 section 4.5): the site push result is an input; the live check runs whenever the site
# pushed, and also after a failed or blocked site push, so a stale live tree is visible.

def test_raw_url_is_the_site_repository_manifest():
    from thusa import site_repo
    assert ncl.RAW_URL == site_repo.SITE_RAW_MANIFEST
    assert ncl.RAW_URL == "https://raw.githubusercontent.com/GrokForum/publicfunds-site/main/public-data/v1/manifest.json"
    assert "publicfunds-sa" not in ncl.RAW_URL


@pytest.mark.parametrize("log", [NOTHING, TIMESTAMPS])
def test_site_pushed_on_a_night_with_no_data_commit_runs_the_check(tmp_path, log):
    code, lines, run = go_full(tmp_path, log, site=(0, SITE_PUSHED))
    assert code == 0 and run.kinds() == ["check"]
    assert lines[0] == "site_publish: pushed (site push pushed eeeeeeeeeeee)"
    assert lines[1].startswith("check_live: running (publish: ") and "site push pushed" in lines[1]


def test_data_and_site_pushed_runs_the_check(tmp_path):
    code, lines, run = go_full(tmp_path, PUSHED, site=(0, SITE_PUSHED))
    assert code == 0 and run.kinds() == ["check"]


def test_data_pushed_and_site_no_change_runs_the_check(tmp_path):
    code, lines, run = go_full(tmp_path, PUSHED, site=(0, SITE_NOCHANGE))
    assert code == 0 and run.kinds() == ["check"]


@pytest.mark.parametrize("log", [NOTHING, TIMESTAMPS])
def test_neither_push_pushed_skips(tmp_path, log):
    code, lines, run = go_full(tmp_path, log, site=(0, SITE_NOCHANGE))
    assert code == 3 and run.calls == []
    assert lines[1].startswith("check_live: SKIPPED") and "site push: no change" in lines[1]


@pytest.mark.parametrize("data_log", [PUSHED, NOTHING, TIMESTAMPS])
@pytest.mark.parametrize("site,word", [
    ((3, SITE_BLOCKED), "site push exited 3 (blocked; nothing pushed): ACTION: site publish blocked (unexpected remote commit)"),
    ((4, SITE_FAILED), "site push exited 4 (failed): ACTION: site publish failed"),
    ((1, "Traceback ...\n"), "site push exited 1; cannot tell if it pushed"),
    ((0, ""), "no known pushed or no-change line"),
    ((0, "site_publish: pushed eeee\n"), "no known pushed or no-change line"),          # not a full commit id
    ((0, None), "site push output not readable"),
    ("not-run", "site push did not run"),
])
def test_failed_blocked_or_unknown_site_push_still_runs_the_check(tmp_path, data_log, site, word):
    code, lines, run = go_full(tmp_path, data_log, site=site)
    assert code == 0 and run.kinds() == ["check"]
    assert word in lines[0]
    assert lines[1].startswith("check_live: running (") and "a stale live tree is visible" in lines[1]


def test_failed_site_push_with_a_breach_reports_the_breach(tmp_path):
    code, lines, run = go_full(tmp_path, PUSHED, site=(3, SITE_BLOCKED), check=(1, BREACH_OUT))
    assert code == 1 and run.kinds() == ["check", "healthz"]
    assert lines[-1] == "NEXT: stop. Do not re-publish to fix it. Follow RB-12."


@pytest.mark.parametrize("exit_code", [3, 4, 5])
@pytest.mark.parametrize("site", [(0, SITE_PUSHED), (0, SITE_NOCHANGE), (3, SITE_BLOCKED)])
def test_site_push_after_a_failed_data_publish_is_a_failed_check(tmp_path, exit_code, site):
    code, lines, run = go_full(tmp_path, PUSHED, exit_code=exit_code, site=site)
    assert code == 2 and run.calls == []
    assert lines[1].startswith("check_live: FAILED CHECK (a site push ran after data publish exit")


@pytest.mark.parametrize("log", ["", "evidence_guard: pass\n"])
def test_unknown_data_result_is_still_a_failed_check_when_the_site_pushed(tmp_path, log):
    code, lines, run = go_full(tmp_path, log, site=(0, SITE_PUSHED))
    assert code == 2 and "check" not in run.kinds()
    assert lines[1].startswith("check_live: FAILED CHECK (no known commit, push or no-change line")


def test_script_never_runs_the_site_publish():
    text = (ROOT / "scripts" / "nightly_check_live.py").read_text()
    code = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
    body = code.split('"""', 2)[2]                        # skip the docstring and comments, which name the helper
    assert "import" not in body.replace("from __future__ import annotations", "").replace("import argparse", "") \
        .replace("import re", "").replace("import subprocess", "").replace("import sys", "") \
        .replace("from pathlib import Path", "")
    assert '"git", "push"' not in body and "publish_site_repo.py\"" not in body
