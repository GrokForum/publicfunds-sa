"""Checks for the check-only nightly GitHub Actions workflow (CHG-2026-073)."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

import importlib.util

def _load(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

WORKFLOW = ROOT / ".github" / "workflows" / "nightly-dq-gate.yml"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def test_workflow_is_check_only():
    text = WORKFLOW.read_text(encoding="utf-8")
    data = _workflow()
    on = data.get("on", data.get(True))
    assert on["schedule"][0]["cron"] == "30 2 * * *"
    assert "workflow_dispatch" in on
    assert data["permissions"] == {"contents": "read"}
    assert data["jobs"]["check"]["permissions"] == {"contents": "read"}
    assert "${{ secrets" not in text and "secrets." not in "".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
    assert "pull_request_target" not in text
    assert "write-all" not in text
    assert "publish-public-data" not in text
    assert "git push" not in text
    assert "--push" not in text
    uses = []
    persist = []
    for step in data["jobs"]["check"]["steps"]:
        if "uses" in step:
            action, _, ref = step["uses"].partition("@")
            uses.append((action, ref.split()[0] if ref else ""))
            if action == "actions/checkout":
                persist.append(step.get("with", {}).get("persist-credentials"))
        run = step.get("run", "")
        assert "${{" not in run
    assert uses, "expected pinned actions"
    for action, ref in uses:
        assert SHA_RE.match(ref), f"{action} is not pinned to a 40-hex SHA: {ref!r}"
    assert persist == [False]
    runs = [s["run"] for s in data["jobs"]["check"]["steps"] if "run" in s]
    assert any(r == "uv sync --frozen --group dev" for r in runs)
    assert any(r == "uv run pytest -q" for r in runs)
    assert any("ci_published_dq_gate.py --live" in r for r in runs)
    assert any(r == "python3 scripts/ci_check_live.py" for r in runs)


def _write_published(dir_path: Path, payload: dict, files: dict[str, bytes]) -> None:
    entries = []
    for name, body in files.items():
        (dir_path / name).write_bytes(body)
        entries.append({"name": name, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()})
    manifest = {
        "schema": "publicfunds.public-data/v1",
        "kind": "manifest",
        "build": {"id": "BTEST", "data_quality": payload},
        "files": entries,
    }
    (dir_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    # manifest itself is not in files[] (same as the live export)
    return


def test_published_gate_passes_on_matching_files(tmp_path):
    _dq = _load('ci_published_dq_gate.py')
    check_local, main = _dq.check_local, _dq.main

    data = tmp_path / "v1"
    data.mkdir()
    body = b'{"ok": true}'
    _write_published(data, {"pass": 1, "warn": 0, "fail": 0}, {"prices.json": body})
    assert check_local(data) == []
    assert main(["--data-dir", str(data)]) == 0


def test_published_gate_fails_on_recorded_failure(tmp_path):
    _dq = _load('ci_published_dq_gate.py')
    check_local = _dq.check_local

    data = tmp_path / "v1"
    data.mkdir()
    _write_published(data, {"pass": 0, "warn": 0, "fail": 2}, {"prices.json": b"{}"})
    problems = check_local(data)
    assert any("fail=2" in p for p in problems)


def test_published_gate_fails_on_sha_mismatch(tmp_path):
    _dq = _load('ci_published_dq_gate.py')
    check_local = _dq.check_local

    data = tmp_path / "v1"
    data.mkdir()
    _write_published(data, {"pass": 1, "warn": 0, "fail": 0}, {"prices.json": b'{"a":1}'})
    (data / "prices.json").write_bytes(b'{"a":2}')
    problems = check_local(data)
    assert any("sha256 mismatch" in p for p in problems)


def test_published_gate_fails_on_missing_file(tmp_path):
    _dq = _load('ci_published_dq_gate.py')
    check_local = _dq.check_local

    data = tmp_path / "v1"
    data.mkdir()
    _write_published(data, {"pass": 1, "warn": 0, "fail": 0}, {"prices.json": b"{}"})
    (data / "prices.json").unlink()
    problems = check_local(data)
    assert any("missing published file prices.json" in p for p in problems)


def test_check_live_wrapper_fails_on_breach():
    decide = _load('ci_check_live.py').decide

    assert decide(0, "RESULT: OK\n") == 0
    assert decide(0, "RESULT: WARN (1)\n") == 0
    assert decide(1, "RESULT: BREACH (1)\n") == 1
    assert decide(0, "RESULT: BREACH (1)\n") == 1  # fail closed if exit was wrong
    assert decide(1, "the check itself failed\n") == 1


def test_published_gate_passes_on_repo_export():
    """The committed public-data/v1 export must pass the check-only gate."""
    check_local = _load('ci_published_dq_gate.py').check_local
    problems = check_local(ROOT / "public-data" / "v1")
    assert problems == []
