"""CHG-2026-057: display formatters (comma thousands, point decimal) and unchanged data files."""
from __future__ import annotations

import csv
import json
import os
import re
import shutil
import subprocess
from decimal import Decimal
from pathlib import Path

import pytest

from thusa.format import (format_amount, format_count, format_pct, format_pct_points, format_rand,
                          format_rand_short, is_count_column)

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
# Owner decisions 13 Nov 2026 19:30 SAST and 14 Nov 2026 16:46 SAST: no rounding in the formatter (source
# precision), money in cents shows two decimals, percentages are not padded, tables full, prose may be short.

@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0"),
        (0.0, "0"),
        (Decimal("0"), "0"),
        (1234, "1,234"),
        (1234.5, "1,234.5"),
        (1234567.89, "1,234,567.89"),
        (1234567890.12, "1,234,567,890.12"),
        (-1234.5, "-1,234.5"),
        (Decimal("-1234.50"), "-1,234.50"),     # a Decimal keeps the digits it holds
        (1.225, "1.225"),                       # no rounding: source precision
        (-1.225, "-1.225"),
        (1.2345678, "1.2345678"),
        (75.7, "75.7"),
        (1000000, "1,000,000"),
    ],
)
def test_format_amount_shows_source_precision(value, expected):
    assert format_amount(value) == expected


@pytest.mark.parametrize(
    "value, places, expected",
    [(75.7, 1, "75.7"), (76.0, 1, "76.0"), (1234.5, 2, "1,234.50"), (1.225, 2, "1.225"), (12.3456, 1, "12.3456")],
)
def test_format_amount_places_only_pads_never_cuts(value, places, expected):
    assert format_amount(value, places) == expected


def test_formatter_adds_no_rounding():
    """Halves are not rounded up or off: every digit the value holds is shown."""
    for v in (Decimal("1.225"), Decimal("-1.225"), Decimal("2.5"), 12.5, -12.5, 0.125):
        shown = format_amount(v).replace(",", "")
        assert Decimal(shown) == Decimal(str(v)), (v, shown)
    assert format_count(12.5) == "12.5" and format_count(-12.5) == "-12.5"


def test_format_signed_zero():
    """Zero is never signed: -0.0 shows as 0.00 for money (and 0 without a precision)."""
    assert format_amount(-0.0, 2) == "0.00"
    assert format_amount(-0.0) == "0"
    assert format_amount(Decimal("-0.00")) == "0.00"
    assert format_count(-0.0) == "0"
    assert format_rand(-0.0) == "R0.00"
    assert format_rand(Decimal("-0")) == "R0.00"
    assert format_rand_short(-0.0) == "R0.00"
    assert format_pct(-0.0) == "0%"
    assert format_pct_points(-0.0, 1) == "0.0%"


@pytest.mark.parametrize("value", [None, float("nan"), float("inf"), float("-inf"), "foo", True, False, object()])
def test_format_amount_and_count_empty_on_invalid(value):
    assert format_amount(value) == ""
    assert format_count(value) == ""


@pytest.mark.parametrize(
    "value, expected",
    [(0, "0"), (8, "8"), (1167, "1,167"), (1285, "1,285"), (1234567, "1,234,567"), (-1167, "-1,167")],
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
        (2345.6, "R23.456"),           # fractional cents: shown, not rounded
    ],
)
def test_format_rand_full_figure_from_cents(cents, expected):
    assert format_rand(cents) == expected


@pytest.mark.parametrize(
    "cents, expected",
    [
        (None, "unknown"),
        (0, "R0.00"),
        (123456, "R1,234.56"),          # under a million: full figure, nothing dropped
        (99999999, "R999,999.99"),
        (100000000, "R1 m"),
        (120000000, "R1.2 m"),
        (125000000, "R1.3 m"),          # short form only: half away from zero (page rule before CHG-2026-057)
        (-129950000, "-R1.3 m"),
        (345000000000, "R3.45 bn"),
        (340000000000, "R3.4 bn"),
        (123456789012, "R1.23 bn"),
    ],
)
def test_format_rand_short_for_prose(cents, expected):
    assert format_rand_short(cents) == expected


def test_format_pct_at_stored_precision():
    assert format_pct(0.9707) == "97.07%"     # tenders-summary shares are stored to 4 decimals
    assert format_pct(0.5) == "50%"           # not padded
    assert format_pct(1.0) == "100%"
    assert format_pct(0.757) == "75.7%"
    assert format_pct(0.57) == "57%"          # exact decimal shift, no float artefact
    assert format_pct(-0.0125) == "-1.25%"
    assert format_pct(None) is None
    assert format_pct(float("nan")) is None


def test_format_pct_points_coverage():
    assert format_pct_points(75.7, 1) == "75.7%"   # coverage stored to one decimal: 75.7%, not 75.70%
    assert format_pct_points(81.9, 1) == "81.9%"
    assert format_pct_points(76.0, 1) == "76.0%"   # the calculation's one decimal is kept
    assert format_pct_points(None) is None


def test_format_module_has_no_rounding_outside_the_short_form():
    src = (ROOT / "thusa" / "format.py").read_text(encoding="utf-8")
    body = src[src.index("def format_rand_short"):src.index("def format_pct(")]
    rest = src.replace(body, "")
    assert "quantize(Decimal(1).scaleb" in body and "ROUND_HALF_UP" in body
    assert "rounding=" not in rest and "round(" not in rest
    assert "format_pct_parts" not in src


# ---- JS helpers match Python ----------------------------------------------------------------------

def test_js_format_helpers_match_python():
    cases = {
        "amount": [0, 1234.5, 1234567.89, 1234567890.12, -1234.5, 1.225, -1.225, 75.7, 1000000, -0.0, 0.0000001, 1e21],
        "amount2": [0, 1234.5, -0.0, 75.7, 1.225],
        "count": [0, 8, 1167, 1285, 1234567, -1167, 12.5],
        "rand": [0, 75000000, 100000000, 400000000, 123456789012, -123450, 1, -1, -0.0, 2345.6],
        "short": [0, 123456, 99999999, 100000000, 120000000, 125000000, -129950000, 345000000000, 340000000000, 123456789012, -0.0],
        "pct": [0, 0.757, -0.0125, 0.9707, 0.5, 1.0, 0.57, 0.1015, -0.0],
        "points": [75.7, 81.9, 76.0, 8.3, -0.0],
    }
    js = _node(
        "{amount:[" + ",".join(f"formatAmount({v})" for v in cases["amount"]) + "],"
        "amount2:[" + ",".join(f"formatAmount({v}, 2)" for v in cases["amount2"]) + "],"
        "count:[" + ",".join(f"formatCount({v})" for v in cases["count"]) + "],"
        "rand:[" + ",".join(f"formatRand({v})" for v in cases["rand"]) + "],"
        "short:[" + ",".join(f"formatRandShort({v})" for v in cases["short"]) + "],"
        "pct:[" + ",".join(f"formatPct({v})" for v in cases["pct"]) + "],"
        "points:[" + ",".join(f"pctPoints({v}, 1)" for v in cases["points"]) + "],"
        "empty:{amount:formatAmount(null),count:formatCount(null),rand:formatRand(null),short:formatRandShort(null),pct:formatPct(null),"
        "nan:formatAmount(NaN),inf:formatAmount(Infinity)}}"
    )
    assert js["amount"] == [format_amount(v) for v in cases["amount"]]
    assert js["amount2"] == [format_amount(v, 2) for v in cases["amount2"]]
    assert js["count"] == [format_count(v) for v in cases["count"]]
    assert js["rand"] == [format_rand(v) for v in cases["rand"]]
    assert js["short"] == [format_rand_short(v) for v in cases["short"]]
    assert js["pct"] == [format_pct(v) for v in cases["pct"]]
    assert js["points"] == [format_pct_points(v, 1) for v in cases["points"]]
    assert js["empty"] == {"amount": "", "count": "", "rand": "unknown", "short": "unknown", "pct": None, "nan": "", "inf": ""}


def test_page_defines_central_js_helpers():
    assert _BEGIN in PAGE and _END in PAGE
    block = _js_helpers()
    for name in ("formatAmount", "formatCount", "formatRand", "formatRandShort", "formatPct", "pctPoints"):
        assert f"function {name}" in block, name
    assert "formatPctParts" not in PAGE and "_roundHalfUp" not in PAGE


def test_js_format_block_adds_no_rounding_outside_the_short_form():
    block = _js_helpers()
    a = block.index("function _roundAway"); b = block.index("function formatPct(")
    rest = block[:a] + block[b:]
    for bad in ("Math.round", "toFixed", "toLocaleString", "maximumFractionDigits", "toPrecision"):
        assert bad not in rest, bad


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


def test_is_count_column():
    for c in ("awards", "n", "present", "flags", "award_n", "line_count", "n_lines", "n_awards"):
        assert is_count_column(c), c
    for c in ("fye", "flag_id", "score", "value_cents", "sha256", "name", ""):
        assert not is_count_column(c), c
