"""CHG-2026-057 / CHG-2026-047: numbers on a public page use a comma thousands separator and a point decimal
(R1,000,000.00 in a table, R1.2 m in prose; 75.7%). JSON, CSV and data files keep plain point decimals with no
thousands separator."""
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
    js = "\n".join([block, _fn("num"), _fn("pct"), _fn("randFull"), _fn("intg"), _fn("randText"), _fn("centsAmount"), _fn("ratioPct"),
                    "console.log(JSON.stringify([num(1000000), randFull(100000000), pct(0.757), intg(1167), intg(1285), num(1234.5),"
                    " randText(75000000), randText(120000000), randText(345000000000), randFull(-123450), centsAmount(2345.6),"
                    " ratioPct(0.12345), ratioPct(-0.0004)]))"])
    out = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)
    assert out == ["1,000,000", "R1,000,000.00", "75.7%", "1,167", "1,285", "1,234.5",
                   "R750,000.00", "R1.2 m", "R3.45 bn", "-R1,234.50", "23.456", "12.3%", "0%"]


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
    assert "90.8% (1,167 of 1,285 municipality-years)" in first
    assert "64.9% (1,167 of 1,799 municipality-years)" in second
    assert dec(1234.56) == "1,234.6" and dec(83.33) == "83.3"


def test_dashboard_check_number_scan():
    spec = importlib.util.spec_from_file_location("dc", ROOT / "scripts" / "dashboard_check.py")
    dc = importlib.util.module_from_spec(spec); spec.loader.exec_module(dc)   # never skips: Playwright is imported inside main()
    ok = "R1,000,000.00 | R1.2 m | 75.7% | 1,167 of 1,285 | 2019/20 | 1 December 2026"
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


# ---- CHG-2026-057 follow-up: no raw percent concat; count cells go through formatCount ----

def test_dashboard_has_no_raw_percent_concatenation():
    """Percent display outside the format and ceiling blocks must use pctPoints or formatPct, not a raw value + percent sign."""
    start, end = PAGE.index("/* format:begin */"), PAGE.index("/* format:end */")
    rest = PAGE[:start] + PAGE[end + len("/* format:end */"):]
    c0, c1 = rest.index("/* ceiling:begin */"), rest.index("/* ceiling:end */")
    rest = rest[:c0] + rest[c1 + len("/* ceiling:end */"):]
    raw = re.findall(r".{0,50}\+\s*\"%\"", rest)
    assert not raw, raw


def test_dashboard_has_no_stale_pct_precision_argument():
    """page-level pct() shows the stored precision; a literal second argument (old rounding) is stale."""
    assert not re.search(r"\bpct\([^)\n]+,\s*\d+\s*\)", PAGE)


def test_table_formats_numeric_count_cells():
    """num: 1 columns with a bare numeric value() are shown with formatCount; CSV still uses the raw value()."""
    assert "function tableCell(c, r)" in PAGE
    assert "formatCount(v)" in PAGE[PAGE.index("function tableCell"): PAGE.index("function table(")]
    assert "c.csvValue ? c.csvValue(r) : (c.value ? c.value(r)" in PAGE   # CSV path unchanged


def test_present_pct_uses_shared_formatter():
    assert "pctPoints(r[1].present_pct, 1)" in PAGE   # stored to one decimal: 81.9%
    assert 'present_pct + "%"' not in PAGE


# ---- CHG-2026-057 owner style decisions (14 Nov 2026 16:46 SAST): tables full, prose short, no padding ----

def test_tables_show_full_rand_figures():
    """A table column with a rand CSV value renders randCell (full figure), never the short rand()."""
    lines = [l for l in PAGE.splitlines() if "render:" in l and "csvValue" in l and re.search(r'_rand"|\(rand\)|known_value_rand', l)]
    assert len(lines) >= 10
    for l in lines:
        assert not re.search(r"(?<![\w.])rand\(", l), l.strip()[:120]
        assert "randCell(" in l, l.strip()[:120]


def test_prose_rand_uses_short_form_with_full_title():
    assert 'function randText(c) { return c == null ? "" : formatRandShort(c); }' in PAGE
    assert 'el("span", {title: randFull(c)}, randText(c))' in PAGE
    assert "function randCell(c) { return c == null ? unknown() : randFull(c); }" in PAGE


def test_coverage_percent_is_not_padded_to_two_decimals():
    assert "pctPoints(c.complete_pct, 1)" in PAGE and "pctPoints(cov.headline.complete_pct, 1)" in PAGE
    assert not re.search(r"pctPoints\([^)]*,\s*2\s*\)", PAGE)
    assert "75.70%" not in PAGE and "81.90%" not in PAGE


def test_report_and_review_app_tables_full_prose_short():
    rep = (ROOT / "thusa" / "report.py").read_text(encoding="utf-8")
    assert "total known value {{ rand_short(aw.total) }}" in rep
    assert "<td>{{ rand(r.orgb) }}</td>" in rep and "rand_short(r." not in rep
    assert "amount(h.complete_pct, 1)" in rep
    from thusa.report import rand, rand_short
    assert rand(120000000) == "R1,200,000.00" and rand_short(120000000) == "R1.2 m (R1,200,000.00)"
    from thusa.review.warehouse import rand as wrand
    assert wrand(120000000) == "R1,200,000.00"      # the review-app rand filter is used in table cells


def test_text_report_short_form_carries_full_figure_in_brackets():
    """Review finding: a text report has no hover title, so every short form carries its full figure."""
    from thusa.report import rand_short
    assert rand_short(120000000) == "R1.2 m (R1,200,000.00)"
    assert rand_short(345000000000) == "R3.45 bn (R3,450,000,000.00)"
    assert rand_short(-129950000) == "-R1.3 m (-R1,299,500.00)"
    assert rand_short(123456) == "R1,234.56"            # nothing shortened: no brackets
    assert rand_short(None) == "unknown"
    assert rand_short(-0.0) == "R0.00"
    src = (ROOT / "thusa" / "report.py").read_text(encoding="utf-8")
    assert src.count("format_rand_short(") == 1         # only through the bracketed helper


def test_rendered_text_report_sentence_has_bracketed_full_figure():
    from jinja2 import Environment
    from thusa import report
    tpl = report.MUNI[report.MUNI.index("<h2>eTenders awards"):report.MUNI.index("</p>", report.MUNI.index("<h2>eTenders awards")) + 4]
    env = Environment(autoescape=True)
    env.globals.update(rand_short=report.rand_short, count=report.format_count)
    out = env.from_string(tpl).render(aw={"n": 1167, "valued": 900, "total": 120000000})
    assert "1,167 award-supplier rows, 900 with a usable value, total known value R1.2 m (R1,200,000.00)." in out
