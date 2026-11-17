"""CHG-2026-066: the POPIA release check reviews a candidate made with `pf publish-data --out <dir>`.

The nightly skill copies public-data/v1 to data/popia-candidate/v1 and runs `pf publish-data --out` on the copy. The
publish script then runs plain `pf publish-data` (default output public-data/v1). The POPIA review is only worth
something if the two runs write the same bytes. This test runs both commands through the real `pf` entry point on the
synthetic fixture warehouse and compares every file byte for byte.

One field depends on the clock: manifest.json `generated_at_sast` (and the changes.json / feed.json entries made from
it). The nightly makes the two exports some seconds apart, so in real use only that time differs. The test fixes the
clock to one value for both runs, so nothing is excluded from the byte comparison.
"""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

from thusa import publish_data as pdx
from thusa.review import cli
from thusa.settings import REPO_ROOT

FIXED = datetime(2026, 11, 18, 3, 7, 0, tzinfo=timezone.utc)


class _FixedClock(datetime):
    @classmethod
    def now(cls, tz=None):
        return FIXED.astimezone(tz) if tz else FIXED.replace(tzinfo=None)


@pytest.fixture
def fake_repo(tmp_path, monkeypatch, paths, svc):
    """A repo root in tmp: the default output goes to <tmp>/public-data/v1, never to the real public-data/."""
    root = tmp_path / "repo"
    (root / "itil" / "knowledge").mkdir(parents=True)
    shutil.copy(REPO_ROOT / "itil" / "knowledge" / "known-errors.md", root / "itil" / "knowledge" / "known-errors.md")
    monkeypatch.setattr(pdx, "REPO_ROOT", root)
    monkeypatch.setattr(pdx, "datetime", _FixedClock)
    return root


def _files(d: Path) -> dict[str, bytes]:
    return {p.name: p.read_bytes() for p in sorted(d.iterdir())}


def _candidate_and_real(root: Path, tmp_path: Path, seed: bool):
    real = root / "public-data" / "v1"
    assert cli.main(["publish-data"]) == 0                              # last night's publish: the files now live
    ch = json.loads((real / "changes.json").read_text())
    ch["entries"][0]["data_hash"] = "0" * 16                            # last night's data differed from tonight's
    (real / "changes.json").write_text(json.dumps(ch, ensure_ascii=False, indent=1))
    cand = tmp_path / "data" / "popia-candidate" / "v1"
    cand.parent.mkdir(parents=True)
    if seed:
        shutil.copytree(real, cand)                                     # the skill's `cp -a public-data/v1 ...`
    assert cli.main(["publish-data", "--out", str(cand)]) == 0          # the POPIA candidate
    assert cli.main(["publish-data"]) == 0                              # the real publish export
    return _files(cand), _files(real)


def test_candidate_export_is_byte_identical_to_the_real_export(fake_repo, tmp_path, capsys):
    cand, real = _candidate_and_real(fake_repo, tmp_path, seed=True)
    assert set(cand) == set(real) and "manifest.json" in real and "changes.json" in real
    for name in real:
        assert cand[name] == real[name], name


def test_candidate_without_the_copy_is_not_identical(fake_repo, tmp_path, capsys):
    """Must-fail case: without the copy of public-data/v1 the candidate has no change history, so the bytes differ."""
    cand, real = _candidate_and_real(fake_repo, tmp_path, seed=False)
    assert cand["changes.json"] != real["changes.json"]


def test_clock_is_the_only_moving_part(fake_repo, tmp_path, capsys, monkeypatch):
    """Must-fail case for the normalisation: with a different clock for the real export, manifest.json differs."""
    real = fake_repo / "public-data" / "v1"
    assert cli.main(["publish-data"]) == 0
    cand = tmp_path / "cand"
    shutil.copytree(real, cand)
    assert cli.main(["publish-data", "--out", str(cand)]) == 0
    global FIXED
    old, FIXED = FIXED, FIXED.replace(second=42)
    try:
        assert cli.main(["publish-data"]) == 0
    finally:
        FIXED = old
    a, b = _files(cand), _files(real)
    assert a["manifest.json"] != b["manifest.json"]
    assert {n for n in b if a[n] != b[n]} <= {"manifest.json", "changes.json", "feed.json"}


def test_publish_script_and_skill_call_the_same_command():
    script = (REPO_ROOT / "scripts" / "publish-public-data.sh").read_text(encoding="utf-8")
    assert "uv run pf publish-data > data/publish-data.json" in script          # default output, no --out
    master = (REPO_ROOT / "docs" / "bot" / "live-skill" / "publicfunds-refresh.MASTER.md").read_text(encoding="utf-8")
    assert ("cp -a public-data/v1 data/popia-candidate/v1 && uv run pf publish-data --out data/popia-candidate/v1"
            in master)
