"""CHG-2026-057 / CHG-2026-047: numbers on a public page use a comma thousands separator and a point decimal
(1,000,000.00; 75.70%). JSON, CSV and data files keep plain point decimals with no thousands separator."""
from __future__ import annotations

import csv
import importlib.util
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from thusa.coverage_ceiling import dec, headline_context_lines

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "apps/public-dashboard/index.html").read_text(encoding="utf-8")
DATA = ROOT / "public-data" / "v1"


def _fn(name: str) -> str:
    m = re.search(rf"^function {name}\(.*$", PAGE, re.M)
    assert m, name
    return m.group(0)


# ---- rule 1: on screen, comma thousands and point decimal --------------------------------------------------------

def test_page_helpers_show_comma_thousands_and_point_decimal():
    # same node policy as the parity tests: FAIL without node, skip only with PF_SKIP_NODE_PARITY=1 (so the count is stable)
    if not shutil.which("node"):
        if os.environ.get("PF_SKIP_NODE_PARITY") == "1":
            pytest.skip("node not installed and PF_SKIP_NODE_PARITY=1")
        pytest.fail("node is required (set PF_SKIP_NODE_PARITY=1 to opt out)")
    # Wrappers sit after the format:begin/end block and call it; include the block so they run in node.
    a, b = PAGE.index("/* format:begin */"), PAGE.index("/* format:end */")
    block = PAGE[a:b + len("/* format:end */")]
    js = "\n".join([block, _fn("num"), _fn("pct"), _fn("randFull"), _fn("intg"), _fn("randText"),
                    "console.log(JSON.stringify([num(1000000), randFull(100000000), pct(0.757), intg(1167), intg(1285), num(1234.5), randText(75000000)]))"])
    out = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)
    assert out == ["1,000,000.00", "R1,000,000.00", "75.70%", "1,167", "1,285", "1,234.50", "R750,000.00"]


def test_page_has_no_decimal_comma_or_za_number_locale():
    assert 'replace(".", ",")' not in PAGE
    za = [l for l in PAGE.splitlines() if 'toLocaleString("en-ZA"' in l]
    assert all("timeZone" in l for l in za), za          # only the SAST date keeps en-ZA; it shows no decimals
    assert 'const NUM_LOCALE = "en-US";' in PAGE


def test_page_text_has_no_space_thousands():
    body = PAGE[PAGE.index("<script"):]
    assert not re.findall(r"R\d{1,3}(?: \d{3})+\b", body)
    assert "R1,000,000.00" in PAGE and "R750,000.00" in PAGE and "2,500" in PAGE


def test_python_mirror_uses_the_same_format():
    cov = json.loads((DATA / "coverage.json").read_text(encoding="utf-8"))
    first, second = headline_context_lines(cov)[:2]
    assert "90.82% (1,167 of 1,285 municipality-years)" in first
    assert "64.87% (1,167 of 1,799 municipality-years)" in second
    assert dec(1234.56) == "1,234.56" and dec(83.33) == "83.33"


def test_dashboard_check_number_scan():
    spec = importlib.util.spec_from_file_location("dc", ROOT / "scripts" / "dashboard_check.py")
    dc = importlib.util.module_from_spec(spec); spec.loader.exec_module(dc)   # never skips: Playwright is imported inside main()
    ok = "R1,000,000.00 | 75.70% | 1,167 of 1,285 | 2019/20 | 1 December 2026"
    assert dc.number_format_problems(ok, []) == []
    bad = dc.number_format_problems("90,8% | R1 000 000,00 | 1\u00a0285", [])
    assert any("90,8" in b for b in bad) and any("1 000 000" in b for b in bad) and sum(b.startswith("space thousands") for b in bad) == 2
    assert dc.number_format_problems("Source P0151,1 says", ["Source P0151,1 says"]) == []   # verbatim data text is skipped


# ---- rule 2: data files keep plain point decimals, no thousands separator --------------------------------------

NUMLIKE_BAD = re.compile(r"^-?\d{1,3}(?:[ ,\u00a0\u202f]\d{3})+(?:[.,]\d+)?%?$|^-?\d+,\d+%?$")


def _strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from _strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from _strings(v)


def test_json_data_has_plain_numbers():
    files = sorted(DATA.glob("*.json"))
    assert files
    for f in files:
        bad = [s for s in _strings(json.loads(f.read_text(encoding="utf-8"))) if NUMLIKE_BAD.match(s.strip())]
        assert not bad, (f.name, bad[:5])


def test_csv_data_has_plain_numbers():
    for f in sorted(ROOT.glob("public-data/**/*.csv")):
        with f.open(encoding="utf-8-sig", newline="") as h:
            bad = [c for row in csv.reader(h) for c in row if NUMLIKE_BAD.match(c.strip())]
        assert not bad, (f.name, bad[:5])


def test_page_csv_export_does_not_use_screen_format():
    """A table column shown with num/randFull/randText/intg must give the CSV a plain value (csvValue) or be hidden."""
    cols = re.findall(r"\{label: [^{}]*value: r => (?:num|randFull|randText|intg)\([^{}]*\}", PAGE)
    assert all("csvValue" in c for c in cols), [c for c in cols if "csvValue" not in c]


def test_file_sizes_use_comma_thousands():
    assert "toFixed(0)} KB" not in PAGE and "${intg(x.bytes / 1024)} KB" in PAGE
