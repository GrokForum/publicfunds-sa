#!/usr/bin/env python3
"""Check-only data-quality gate against published public-data/v1 files.

Fails the process when the recorded warehouse gate reports a failure, when a
listed published file is missing or does not match its manifest size or sha256,
or when the live manifest (optional --live) records a gate failure.

This script does not ingest, publish, or push. Standard library only for the
live fetch. Writes nothing in the repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_DATA = Path("public-data/v1")
DEFAULT_LIVE = "https://publicfunds.grokforum.site/public-data/v1/manifest.json"
USER_AGENT = "publicfunds-ci-dq/1"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read manifest {path.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("manifest is not a JSON object")
    return data


def recorded_gate_failures(manifest: dict) -> int:
    build = manifest.get("build")
    if not isinstance(build, dict):
        raise ValueError("manifest has no build object")
    dq = build.get("data_quality")
    if not isinstance(dq, dict) or "fail" not in dq:
        raise ValueError("manifest has no build.data_quality.fail")
    try:
        return int(dq["fail"])
    except (TypeError, ValueError) as exc:
        raise ValueError("build.data_quality.fail is not an integer") from exc


def check_local(data_dir: Path) -> list[str]:
    problems: list[str] = []
    manifest_path = data_dir / "manifest.json"
    if not manifest_path.is_file():
        return [f"missing {manifest_path}"]
    try:
        manifest = load_manifest(manifest_path)
        fails = recorded_gate_failures(manifest)
    except ValueError as exc:
        return [str(exc)]
    if fails != 0:
        problems.append(f"recorded data-quality gate fail={fails}")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        problems.append("manifest.files is missing or empty")
        return problems
    seen: set[str] = set()
    for entry in files:
        if not isinstance(entry, dict) or not entry.get("name"):
            problems.append("manifest.files has an entry without a name")
            continue
        name = entry["name"]
        if name in seen:
            problems.append(f"duplicate manifest file {name}")
        seen.add(name)
        if "/" in name or name.startswith(".") or name != Path(name).name:
            problems.append(f"unsafe published file name {name!r}")
            continue
        path = data_dir / name
        if not path.is_file():
            problems.append(f"missing published file {name}")
            continue
        size = path.stat().st_size
        if "bytes" in entry and size != int(entry["bytes"]):
            problems.append(f"{name} size {size} != manifest {entry['bytes']}")
        if "sha256" in entry:
            got = _sha256(path)
            if got != entry["sha256"]:
                problems.append(f"{name} sha256 mismatch")
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"{name} is not valid JSON: {exc}")
    return problems


def fetch_live_manifest(url: str, timeout: float = 20.0) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("live manifest is not a JSON object")
    return data


def check_live_manifest(url: str) -> list[str]:
    try:
        manifest = fetch_live_manifest(url)
        fails = recorded_gate_failures(manifest)
    except (ValueError, json.JSONDecodeError, urllib.error.URLError, TimeoutError, OSError) as exc:
        return [f"live manifest: {type(exc).__name__}: {exc}"]
    if fails != 0:
        return [f"live recorded data-quality gate fail={fails}"]
    return []


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    ap.add_argument("--live", action="store_true", help="also check the live published manifest")
    ap.add_argument("--live-url", default=DEFAULT_LIVE)
    args = ap.parse_args(argv)
    problems = check_local(args.data_dir)
    if args.live:
        problems.extend(check_live_manifest(args.live_url))
    if problems:
        print("PUBLISHED DATA-QUALITY GATE FAILED", file=sys.stderr)
        for p in problems:
            print(p, file=sys.stderr)
        return 1
    print("PUBLISHED DATA-QUALITY GATE PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
