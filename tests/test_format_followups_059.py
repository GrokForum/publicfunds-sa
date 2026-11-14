"""CHG-2026-059: follow-ups to CHG-2026-057 (owner decision, 14 Nov 2026).

1. The review app's share_of_top15 column comes from the shared formatter (42.3%), at the
   calculation's one-decimal rule. The digits do not change.
2. Rand amounts in flag titles and explanations use the report's prose rule: R1 m and over is
   the short form with the full figure in brackets; under R1 m is the full figure with cents.
3. Data stays plain: evidence_json, flag IDs, scores and the public-data field lists do not change.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import duckdb
import pytest

from thusa import detectors
from thusa.format import format_pct_points, format_rand_prose
from thusa.report import rand_short
from thusa.review import workflow as wf
from thusa.review.warehouse import share_pct_1dp
from thusa.settings import load_yaml

ROOT = Path(__file__).resolve().parents[1]
Y = load_yaml("detectors.yaml")
CFG, TH = Y["detectors"], Y["procurement_thresholds"]


def _legacy_rand(cents):                      # the flag-text rule before CHG-2026-059 (whole rand, rounded)
    return "unknown" if cents is None else f"R{cents / 100:,.0f}"


# ---- 2. the prose rule ------------------------------------------------------------------------------------------

@pytest.mark.parametrize("cents, expected", [
    (99_999_999, "R999,999.99"),                          # just under R1 m: full figure with cents, no brackets
    (100_000_000, "R1 m (R1,000,000.00)"),                # exactly R1 m: short form plus full figure
    (120_000_000, "R1.2 m (R1,200,000.00)"),
    (12_345_678, "R123,456.78"),
    (75_000_000, "R750,000.00"),                          # a bidding limit under R1 m
    (203_060_070_500, "R2.03 bn (R2,030,600,705.00)"),
    (-99_999_999, "-R999,999.99"),
    (-120_000_000, "-R1.2 m (-R1,200,000.00)"),
    (0, "R0.00"),
    (-0.0, "R0.00"),                                      # zero is never signed
    (None, "unknown"),
])
def test_flag_text_rand_uses_the_report_prose_rule(cents, expected):
    assert detectors._rand(cents) == expected
    assert format_rand_prose(cents) == expected
    assert rand_short(cents) == expected                  # the text report uses the same shared helper


def test_evidence_value_string_is_unchanged():
    for c in (None, 0, 12_345_678, 99_999_999, 100_000_000, -120_000_000, 29_500_000):
        assert detectors._rand_evidence(c) == _legacy_rand(c)


def _wh(awards):
    con = duckdb.connect()
    con.execute("CREATE SCHEMA curated")
    con.execute("CREATE TABLE curated.gov_body (gov_body_id VARCHAR, body_type VARCHAR)")
    con.executemany("INSERT INTO curated.gov_body VALUES (?, ?)", [("MUN1", "local"), ("DEP1", "department")])
    con.execute("""CREATE TABLE curated.award (ocid VARCHAR, award_id VARCHAR, buyer_id VARCHAR, buyer_name VARCHAR,
        buyer_gov_body_id VARCHAR, supplier_key VARCHAR, supplier_name VARCHAR, n_suppliers INTEGER,
        value_cents BIGINT, value_note VARCHAR, award_date DATE, award_date_basis VARCHAR)""")
    for i, a in enumerate(awards):
        r = {"ocid": f"ocds-{i}", "award_id": "1", "buyer_id": "B1", "buyer_name": "Test LM", "buyer_gov_body_id": "MUN1",
             "supplier_key": "ACME", "supplier_name": "ACME (PTY) LTD", "n_suppliers": 1, "value_cents": None,
             "value_note": None, "award_date": date(2024, 6, 1), "award_date_basis": "contract.dateSigned", **a}
        con.execute("INSERT INTO curated.award VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", list(r.values()))
    return con


def _d(n):
    return date(2024, 6, 1) + timedelta(days=n)


def test_d17_text_under_r1m_shows_full_figures_with_cents():
    con = _wh([{"value_cents": 29_500_001, "award_date": _d(0)}, {"value_cents": 29_900_000, "award_date": _d(40)},
               {"value_cents": 30_000_000, "award_date": _d(80)}])
    f = detectors.d17_just_below_threshold(con, CFG["D17_just_below_threshold"], TH)[0]
    assert "just under the R300,000.00 bidding limit" in f["title"]
    assert f["explanation"].startswith("3 awards between R270,000.00 and R300,000.00 within ")
    ev = json.loads(f["evidence_json"])
    assert [e["value"] for e in ev] == [_legacy_rand(c) for c in (29_500_001, 29_900_000, 30_000_000)]


def test_d16_and_d6_text_at_and_over_r1m_carries_the_full_figure_in_brackets():
    con = _wh([{"value_cents": 40_000_000, "award_date": _d(i * 60)} for i in range(5)])           # 5 x R400k = R2 m
    f = detectors.d16_repeat_awards(con, CFG["D16_repeat_awards"])[0]
    assert "a known total value of R2 m (R2,000,000.00) from this buyer" in f["explanation"]
    con = _wh([{"value_cents": 60_000_000, "award_date": _d(0), "buyer_gov_body_id": "DEP1", "buyer_id": "D"},
               {"value_cents": 50_000_000, "award_date": _d(9), "buyer_gov_body_id": "DEP1", "buyer_id": "D"}])
    f = detectors.d6_threshold_splitting(con, CFG["D6_threshold_splitting"], TH)[0]
    assert "total R1.1 m (R1,100,000.00), above the R1 m (R1,000,000.00) bidding limit" in f["title"]
    assert f["explanation"].startswith("Each award is at or below R1 m (R1,000,000.00), the PFMA")


def test_flag_id_score_and_evidence_do_not_depend_on_the_text():
    con = _wh([{"value_cents": 40_000_000, "award_date": _d(i * 60)} for i in range(5)])
    new = detectors.d16_repeat_awards(con, CFG["D16_repeat_awards"])[0]
    old = detectors._flag("D16_repeat_awards", CFG["D16_repeat_awards"], "buyer_supplier", "MUN1|ACME",
                          "ACME (PTY) LTD", "MUN1", new["period_label"], "low", 5, "old title", "old text",
                          json.loads(new["evidence_json"]), True)
    for k in ("flag_id", "score", "severity", "evidence_json", "names_supplier", "review_status", "detector_version"):
        assert new[k] == old[k], k
    # The review fingerprint covers title and explanation (ADR-0008), so new text gives a new evidence hash.
    assert wf.evidence_hash(new) != wf.evidence_hash(old)


# ---- 1. share_of_top15 ------------------------------------------------------------------------------------------

def test_share_of_top15_digits_match_the_old_string_exactly():
    for total in range(1, 401):
        for part in range(0, total + 1):
            assert format_pct_points(share_pct_1dp(part, total), 1) == f"{part / total:.1%}", (part, total)
    for part, total in ((393_570_966, 929_000_000), (350_834_596, 393_570_966), (1, 10 ** 12)):
        assert format_pct_points(share_pct_1dp(part, total), 1) == f"{part / total:.1%}"


def test_share_of_top15_style():
    assert format_pct_points(share_pct_1dp(423, 1000), 1) == "42.3%"
    assert format_pct_points(share_pct_1dp(1, 2), 1) == "50.0%"            # the calculation's one decimal is kept
    assert format_pct_points(share_pct_1dp(5, 5), 1) == "100.0%"
    assert format_pct_points(share_pct_1dp(0, 5), 1) == "0.0%"
    src = (ROOT / "thusa" / "review" / "warehouse.py").read_text(encoding="utf-8")
    assert "/ tot:.1%}" not in src and "format_pct_points(share_pct_1dp(" in src


# ---- 3. data stays plain ----------------------------------------------------------------------------------------

def test_public_data_field_lists_are_unchanged():
    from thusa.review.service import EXPORT_COLS
    src = (ROOT / "thusa" / "publish_data.py").read_text(encoding="utf-8")
    # flags.json exports title and explanation only for review-confirmed flags; no numeric field is added or changed.
    assert ('("flag_id", "detector_id", "detector_version", "severity", "title", "explanation",\n'
            '                               "gov_body_id", "body_name", "period_label", "confirmed_at_sast", "review_reason",\n'
            '                               "evidence_urls")') in src
    # The review CSV export carries the title but no explanation and no rand column.
    assert "title" in EXPORT_COLS and "explanation" not in EXPORT_COLS
    assert not any("rand" in c or "cents" in c for c in EXPORT_COLS)
    for d in ("D6_threshold_splitting", "D16_repeat_awards", "D17_just_below_threshold"):
        assert d in load_yaml("publication.yaml")["flags"]["never_publish"]
