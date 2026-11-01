"""CHG-2026-046: the projection line carries its label and mark wherever it is shown."""
from __future__ import annotations

import json
import re
from pathlib import Path

from thusa.coverage_ceiling import headline_context_lines

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "apps/public-dashboard/index.html").read_text(encoding="utf-8")
CHECK = (ROOT / "scripts/dashboard_check.py").read_text(encoding="utf-8")
LABEL = "Projection, not data: "


def test_python_projection_line_has_the_label():
    cov = json.loads((ROOT / "public-data/v1/coverage.json").read_text(encoding="utf-8"))
    for line in headline_context_lines(cov):
        if "would fall to about" in line:
            assert line.startswith(LABEL), line


def test_old_label_is_gone():
    assert "Prediction, not a result" not in PAGE


def test_every_gap_note_with_the_projection_gets_the_labelled_lines():
    calls = re.findall(r"gapBox\(coreGapLines\(\w+\), \{[^}]*\}\)", PAGE)
    assert len(calls) == 3, calls
    home = [c for c in calls if "headlineContextLines" in c]
    other = [c for c in calls if "projectionLines(cov)" in c]
    assert len(home) == 1 and len(other) == 2, calls


def test_gap_note_marks_projection_lines():
    assert '"data-kind": l.startsWith(PROJ_LABEL) ? "projection" : null' in PAGE
    assert 'const PROJ_LABEL = "Projection, not data: ";' in PAGE


def test_dashboard_check_checks_all_three_places():
    assert '("home", "#/"), ("coverage", "#/coverage"), ("report-card", "#/m/MUN:BUF/card")' in CHECK
    seg = CHECK[CHECK.index("CHG-2026-046"):]
    assert 'p[data-kind="projection"]' in seg and "if proj != want_proj" in seg
    assert "exp_ctx = want_ctx if where == \"home\" else want_proj" in seg


def _dc():
    import importlib.util
    spec = importlib.util.spec_from_file_location("dashboard_check", ROOT / "scripts" / "dashboard_check.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)          # no Playwright needed: it is imported inside main()
    return m


def test_projection_status_expected_on_real_data_and_never_silent():
    import copy
    dc = _dc()
    cov = json.loads((ROOT / "public-data/v1/coverage.json").read_text(encoding="utf-8"))
    assert dc.projection_status(cov) == (True, "projection line expected")
    nxt = cov["headline"]["fye_max"] + 1
    c2 = copy.deepcopy(cov)
    c2["headline"]["by_year"] = [y for y in c2["headline"]["by_year"] if y["fye"] != nxt]
    ok, why = dc.projection_status(c2)
    assert not ok and why.startswith("SKIP projection check:") and str(nxt) in why
    c3 = copy.deepcopy(cov)
    for y in c3["headline"]["by_year"]:
        if y["fye"] == nxt:
            y["all_core_due"] = True
    ok, why = dc.projection_status(c3)
    assert not ok and "all_core_due=True" in why


def test_dashboard_check_fails_when_expected_line_is_absent():
    seg = CHECK[CHECK.index("def check_gap_lines"):]
    assert 'checks[f"{vname}_projection"] = why' in seg
    assert "but headline_context_lines() gives none" in seg
    assert 'say(where, "projection line expected but not shown")' in seg
    assert "from playwright" not in CHECK.split("def main")[0]
