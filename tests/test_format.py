"""CHG-2026-057: display formatters (comma thousands, point decimal) and unchanged data files."""
from __future__ import annotations

import csv
import json
import math
import os
import re
import shutil
import subprocess
from decimal import Decimal
from pathlib import Path

import pytest

from thusa.format import format_amount, format_count, format_pct, format_pct_parts, format_rand

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "apps/public-dashboard/index.html").read_text(encoding="utf-8")
DATA = ROOT / "public-data" / "v1"

# The page block between format:begin and format:end is the JS source of truth for helpers.
_BEGIN, _END = "/* format:begin */", "/* format:end */"


def _js_helpers() -> str:
    a, b = PAGE.index(_BEGIN), PAGE.index(_END)
    return PAGE[a : b + len(_END)]


def _node(expr: str):
    if not shutil.which("node"):
        if os.environ.get("PF_SKIP_NODE_PARITY") == "1":
            pytest.skip("node not installed and PF_SKIP_NODE_PARITY=1")
        pytest.fail("node is required (set PF_SKIP_NODE_PARITY=1 to opt out)")
    js = _js_helpers() + "\nconsole.log(JSON.stringify(" + expr + "))\n"
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


# ---- Python helpers --------------------------------------------------------------------------------

@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0.00"),
        (0.0, "0.00"),
        (Decimal("0"), "0.00"),
        (1234, "1,234.00"),
        (1234.5, "1,234.50"),
        (1234567.89, "1,234,567.89"),
        (1234567890.12, "1,234,567,890.12"),
        (-1234.5, "-1,234.50"),
        (Decimal("-1234.50"), "-1,234.50"),
        (1.224, "1.22"),
        (1.225, "1.23"),          # ROUND_HALF_UP, not banker's
        (1.235, "1.24"),          # would be 1.24 even under banker's; next case is the tell
        (1.2250, "1.23"),
        (2.5, "2.50"),            # two-decimal already; half-up at 3rd decimal tested above
        (-1.225, "-1.23"),        # half away from zero
        (75.7, "75.70"),
        (1000000, "1,000,000.00"),
    ],
)
def test_format_amount_examples(value, expected):
    assert format_amount(value) == expected


def test_format_amount_bankers_is_not_used():
    # 1.225 to two decimals is 1.23 under ROUND_HALF_UP; ROUND_HALF_EVEN would give 1.22.
    assert format_amount(Decimal("1.225")) == "1.23"
    assert format_amount(Decimal("-1.225")) == "-1.23"


@pytest.mark.parametrize("value", [None, float("nan"), float("inf"), float("-inf"), "foo", True, False, object()])
def test_format_amount_and_count_empty_on_invalid(value):
    assert format_amount(value) == ""
    assert format_count(value) == ""


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0"),
        (8, "8"),
        (1167, "1,167"),
        (1285, "1,285"),
        (1234567, "1,234,567"),
        (-1167, "-1,167"),
        (12.4, "12"),
        (12.5, "13"),             # half-up to a whole number
        (-12.5, "-13"),
    ],
)
def test_format_count_examples(value, expected):
    assert format_count(value) == expected


@pytest.mark.parametrize(
    "cents, expected",
    [
        (None, "unknown"),
        (0, "R0.00"),
        (75000000, "R750,000.00"),
        (100000000, "R1,000,000.00"),
        (400000000, "R4,000,000.00"),
        (123456789012, "R1,234,567,890.12"),
        (-123450, "-R1,234.50"),
        (1, "R0.01"),
        (-1, "-R0.01"),
    ],
)
def test_format_rand_from_cents(cents, expected):
    assert format_rand(cents) == expected


def test_format_pct_two_decimals():
    assert format_pct(0.757) == "75.70%"
    assert format_pct(0) == "0.00%"
    assert format_pct(-0.0125) == "-1.25%"
    assert format_pct(None) is None
    assert format_pct(float("nan")) is None


def test_format_pct_parts_half_up_integer_arithmetic():
    assert format_pct_parts(1167, 1285) == "90.82"
    assert format_pct_parts(1167, 1799) == "64.87"
    assert [format_pct_parts(c, a) for c, a in ((1, 8), (1, 16), (2, 3), (0, 5), (5, 5))] == [
        "12.50", "6.25", "66.67", "0.00", "100.00",
    ]
    assert format_pct_parts(0, 0) == ""
    assert format_pct_parts(None, 10) == ""


# ---- JS helpers match Python ----------------------------------------------------------------------

def test_js_format_helpers_match_python():
    cases = {
        "amount": [0, 1234.5, 1234567.89, 1234567890.12, -1234.5, 1.225, -1.225, 75.7, 1000000],
        "count": [0, 8, 1167, 1285, 1234567, -1167, 12.5, -12.5],
        "rand": [0, 75000000, 100000000, 400000000, 123456789012, -123450, 1, -1],
        "pct": [0, 0.757, -0.0125],
    }
    js = _node(
        "{amount:[" + ",".join(f"formatAmount({v})" for v in cases["amount"]) + "],"
        "count:[" + ",".join(f"formatCount({v})" for v in cases["count"]) + "],"
        "rand:[" + ",".join(f"formatRand({v})" for v in cases["rand"]) + "],"
        "pct:[" + ",".join(f"formatPct({v})" for v in cases["pct"]) + "],"
        "empty:{amount:formatAmount(null),count:formatCount(null),rand:formatRand(null),pct:formatPct(null),"
        "nan:formatAmount(NaN),inf:formatAmount(Infinity)}}"
    )
    assert js["amount"] == [format_amount(v) for v in cases["amount"]]
    assert js["count"] == [format_count(v) for v in cases["count"]]
    assert js["rand"] == [format_rand(v) for v in cases["rand"]]
    assert js["pct"] == [format_pct(v) for v in cases["pct"]]
    assert js["empty"]["amount"] == ""
    assert js["empty"]["count"] == ""
    assert js["empty"]["rand"] == "unknown"
    assert js["empty"]["pct"] is None
    assert js["empty"]["nan"] == ""
    assert js["empty"]["inf"] == ""


def test_js_pct_parts_match_python():
    pairs = [(1167, 1285), (1167, 1799), (1, 8), (1, 16), (2, 3), (0, 5), (5, 5)]
    js = _node("[" + ",".join(f"formatPctParts({c},{a})" for c, a in pairs) + "]")
    assert js == [format_pct_parts(c, a) for c, a in pairs]


def test_page_defines_central_js_helpers():
    assert _BEGIN in PAGE and _END in PAGE
    block = _js_helpers()
    for name in ("formatAmount", "formatCount", "formatRand", "formatPct", "formatPctParts", "_roundHalfUp"):
        assert f"function {name}" in block, name


# ---- data files stay plain decimals ---------------------------------------------------------------

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


def test_public_data_json_still_plain_decimals():
    files = sorted(DATA.glob("*.json"))
    assert files
    for f in files:
        bad = [s for s in _strings(json.loads(f.read_text(encoding="utf-8"))) if NUMLIKE_BAD.match(s.strip())]
        assert not bad, (f.name, bad[:5])


def test_public_data_csv_still_plain_decimals():
    for f in sorted(ROOT.glob("public-data/**/*.csv")):
        with f.open(encoding="utf-8-sig", newline="") as h:
            bad = [c for row in csv.reader(h) for c in row if NUMLIKE_BAD.match(c.strip())]
        assert not bad, (f.name, bad[:5])


def test_publish_data_module_does_not_import_display_formatters():
    src = (ROOT / "thusa" / "publish_data.py").read_text(encoding="utf-8")
    assert "thusa.format" not in src and "format_amount" not in src and "format_rand" not in src
