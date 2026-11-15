"""CHG-2026-062 Phase 1: fruitless and wasteful (F&W) expenditure as a share of audited spending.

Tests T1 (share rules), T3 (totals), T4 (no summing), T6 (format), T7 (wording) and T8 (drift) of the RFC. The mart
is run on a small hand-made warehouse, so every expected value here is worked out by hand.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from decimal import Decimal
from pathlib import Path

import duckdb
import pytest

from thusa import dq
from thusa.fw_metric import (FW_FYE_MAX, FW_FYE_MIN, FW_REF_MIN_RATIO, FW_SHARE_FYE_MIN, GUARD_STATUS, NATIONAL_STATUS,
                             SHARE_STATUS)

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "thusa" / "models" / "marts" / "110_fw_metric.sql"
PAGE = (ROOT / "apps" / "public-dashboard" / "index.html").read_text(encoding="utf-8")
SHA = "a" * 64


def _wh(fw: list[tuple], den: list[tuple], bodies=("MUN:AAA", "MUN:BBB", "MUN:CCC")):
    """fw rows: (gov_body_id, fye, amount_cents); den rows: (gov_body_id, fye, total_expenditure_cents)."""
    con = duckdb.connect()
    for s in ("ops", "curated", "marts"):
        con.execute(f"CREATE SCHEMA {s}")
    con.execute("CREATE TABLE ops.raw_file (sha256 VARCHAR)")
    con.execute("INSERT INTO ops.raw_file VALUES (?)", [SHA])
    con.execute("CREATE TABLE curated.gov_body (gov_body_id VARCHAR, name VARCHAR, province VARCHAR, body_type VARCHAR, sphere VARCHAR)")
    for i, b in enumerate(bodies):
        con.execute("INSERT INTO curated.gov_body VALUES (?, ?, 'GT', 'local', 'local')", [b, f"Body {i}"])
    con.execute("INSERT INTO curated.gov_body VALUES ('NAT:dept', 'Dept', NULL, 'department', 'national')")
    lin = "source_id VARCHAR, source_file VARCHAR, source_sha256 VARCHAR, fetched_at_utc TIMESTAMPTZ, source_locator VARCHAR"
    con.execute(f"CREATE TABLE curated.uifw_line (gov_body_id VARCHAR, fye INTEGER, fy_label VARCHAR, uifw_type VARCHAR, "
                f"measure VARCHAR, amount_cents BIGINT, {lin})")
    con.execute(f"CREATE TABLE curated.muni_total (gov_body_id VARCHAR, fye INTEGER, amount_type VARCHAR, "
                f"total_expenditure_cents BIGINT, expenditure_basis VARCHAR, {lin})")
    for b, y, c in fw:
        con.execute("INSERT INTO curated.uifw_line VALUES (?, ?, '', 'fruitless_wasteful', 'reported', ?, 'muni_api', 'f', ?, now(), 'loc')",
                    [b, y, c, SHA])
        # irregular and unauthorised rows must never reach the metric (T4)
        for t in ("irregular", "unauthorised"):
            con.execute("INSERT INTO curated.uifw_line VALUES (?, ?, '', ?, 'reported', 999999999, 'muni_api', 'f', ?, now(), 'loc')",
                        [b, y, t, SHA])
    for b, y, c in den:
        con.execute("INSERT INTO curated.muni_total VALUES (?, ?, 'AUDA', ?, 'published_subtotal', 'muni_api', 'f', ?, now(), 'loc')",
                    [b, y, c, SHA])
        con.execute("INSERT INTO curated.muni_total VALUES (?, ?, 'ORGB', 1, 'published_subtotal', 'muni_api', 'f', ?, now(), 'loc')",
                    [b, y, SHA])
    con.execute("CREATE TABLE curated.agsa_uifw (regime VARCHAR, uifw_type VARCHAR, audit_group VARCHAR, fye INTEGER, "
                "amount_cents BIGINT, gov_body_id VARCHAR)")
    con.execute(SQL.read_text())
    return con


def _row(con, b, y):
    r = con.execute("SELECT share_status, fw_share_pct, fw_cents, denom_cents, fw_prev_cents, fw_change_cents "
                    "FROM marts.fw_metric WHERE gov_body_id = ? AND fye = ?", [b, y]).fetchone()
    return None if r is None else dict(zip(("status", "share", "fw", "denom", "prev", "change"), r))


# ---- T1: share rules -------------------------------------------------------------------------------------------

def test_sql_numbers_match_python_constants():
    sql = SQL.read_text()
    assert sql.count(f"BETWEEN {FW_FYE_MIN} AND {FW_FYE_MAX}") == 2
    assert f"o.fye BETWEEN {FW_SHARE_FYE_MIN} AND {FW_FYE_MAX}" in sql
    assert f"WHEN k.fye < {FW_SHARE_FYE_MIN} THEN 'denominator_incomplete_year'" in sql
    assert f"WHEN fye < {FW_SHARE_FYE_MIN} THEN 'denominator_incomplete_year'" in sql
    assert FW_REF_MIN_RATIO == 0.5 and "WHEN den.denom_cents * 2 < ref.denom_ref_median THEN 'denominator_incomplete'" in sql
    assert (FW_FYE_MIN, FW_SHARE_FYE_MIN, FW_FYE_MAX) == (2018, 2020, 2024)
    for st in re.findall(r"THEN '(\w+)'", sql):
        assert st in SHARE_STATUS or st in NATIONAL_STATUS, st
    assert set(GUARD_STATUS) <= set(SHARE_STATUS)


@pytest.mark.parametrize("fw,den,status,share", [
    (None, 100_00, "fw_unknown", None),
    (5_00, None, "denominator_unknown", None),
    (5_00, 0, "denominator_not_positive", None),            # no divide by zero
    (5_00, -100_00, "denominator_not_positive", None),
    (0, 100_00, "ok", Decimal("0.0000")),                   # a known 0 stays 0
    (1, 3, "ok", Decimal("33.3333")),
    (2, 3, "ok", Decimal("66.6666")),                       # cut, not rounded (rounding gives 66.6667)
    (1, 8, "ok", Decimal("12.5000")),
    (1, 1_600_000, "ok", Decimal("0.0000")),                # 0.0000625: cut to 0.0000 (rounding half up gives 0.0001)
    (1, 2_000_000, "ok", Decimal("0.0000")),                # exactly half of the last place: still cut
    (3, 2_000_000, "ok", Decimal("0.0001")),                # 0.00015: cut to 0.0001, not rounded to 0.0002
    (100, 100, "ok", Decimal("100.0000")),
    (101, 100, "share_over_100", None),                     # fallback: completeness passed, F&W still larger
    (9_000_000_000_000_000, 9_100_000_000_000_000, "ok", Decimal("98.9010")),   # no overflow with very large cents
])
def test_share_status_and_cut_not_rounded(fw, den, status, share):
    # 2021 has the same audited spending, so the completeness check has a reference year and passes
    dens = [] if den is None else [("MUN:AAA", 2020, den)] + ([("MUN:AAA", 2021, den)] if den > 0 else [])
    con = _wh([("MUN:AAA", 2020, fw)], dens)
    r = _row(con, "MUN:AAA", 2020)
    assert r["status"] == status
    assert r["share"] == share
    assert status in SHARE_STATUS


def test_years_outside_2018_2024_and_non_municipal_bodies_are_left_out():
    con = _wh([("MUN:AAA", 2017, 5), ("MUN:AAA", 2018, 5), ("MUN:AAA", 2024, 5), ("MUN:AAA", 2025, 5), ("NAT:dept", 2020, 5)],
              [("MUN:AAA", 2012, 10), ("MUN:AAA", 2025, 10)])
    got = con.execute("SELECT gov_body_id, fye FROM marts.fw_metric ORDER BY fye").fetchall()
    assert got == [("MUN:AAA", 2018), ("MUN:AAA", 2024)]


def test_2018_and_2019_keep_the_amount_but_never_a_share():
    con = _wh([("MUN:AAA", 2018, 5_00), ("MUN:AAA", 2019, 6_00), ("MUN:BBB", 2018, 1_00)],
              [("MUN:AAA", y, 100_00) for y in range(2018, 2025)])
    for y, amt in ((2018, 5_00), (2019, 6_00)):
        r = _row(con, "MUN:AAA", y)
        assert r["status"] == "denominator_incomplete_year" and r["share"] is None and r["fw"] == amt
    assert _row(con, "MUN:BBB", 2018)["status"] == "denominator_unknown"      # a more exact reason wins


def test_no_reference_year_hides_the_share():
    # Kopanong 2023/24 case: the only other year with spending is 2018/19, which is not a reference year
    con = _wh([("MUN:AAA", 2024, 5_00), ("MUN:BBB", 2023, 5_00)],
              [("MUN:AAA", 2024, 100_00), ("MUN:AAA", 2019, 100_00), ("MUN:BBB", 2023, 100_00), ("MUN:BBB", 2022, 0),
               ("MUN:BBB", 2021, -5_00)])                                     # zero or negative years are no reference
    for b, y in (("MUN:AAA", 2024), ("MUN:BBB", 2023)):
        r = _row(con, b, y)
        assert r["status"] == "denominator_no_reference" and r["share"] is None and r["fw"] == 5_00


@pytest.mark.parametrize("dens,year,status", [
    ({2020: 100, 2021: 100, 2022: 100, 2023: 49, 2024: 100}, 2023, "denominator_incomplete"),   # 49 < 50
    ({2020: 100, 2021: 100, 2022: 100, 2023: 50, 2024: 100}, 2023, "ok"),                       # exactly half passes
    ({2020: 100, 2021: 200, 2022: 74}, 2022, "denominator_incomplete"),                          # median 150: 74 < 75
    ({2020: 100, 2021: 200, 2022: 75}, 2022, "ok"),
    ({2020: 1_000, 2021: 1_200, 2022: 43, 2023: 1_100}, 2022, "denominator_incomplete"),         # Merafong-like (4%)
    ({2020: 100, 2021: 10, 2022: 100}, 2020, "ok"),           # one low OTHER year does not hide a normal year
])
def test_completeness_check_against_other_years(dens, year, status):
    con = _wh([("MUN:AAA", y, 1) for y in dens], [("MUN:AAA", y, c * 100_000) for y, c in dens.items()])
    r = _row(con, "MUN:AAA", year)
    assert r["status"] == status and (r["share"] is None) == (status != "ok")


def test_every_former_over_100_case_is_hidden():
    # the eight shares over 100% in the local build were in 2018 (5), 2019 (1), 2022 (1) and 2023 (1); each kind is here
    con = _wh([("MUN:AAA", 2018, 7_789_800), ("MUN:BBB", 2022, 2_884_561_100), ("MUN:CCC", 2023, 101)],
              [("MUN:AAA", 2018, 35_126), ("MUN:AAA", 2021, 3_403_697_970),
               ("MUN:BBB", 2022, 260_222_500), ("MUN:BBB", 2021, 341_757_561_700), ("MUN:BBB", 2023, 361_787_373_300),
               ("MUN:CCC", 2023, 100), ("MUN:CCC", 2024, 100)])
    assert _row(con, "MUN:AAA", 2018)["status"] == "denominator_incomplete_year"
    assert _row(con, "MUN:BBB", 2022)["status"] == "denominator_incomplete"
    assert _row(con, "MUN:CCC", 2023)["status"] == "share_over_100"          # explicit fallback
    assert con.execute("SELECT count(*) FROM marts.fw_metric WHERE fw_share_pct > 100").fetchone()[0] == 0


def test_denominator_only_row_is_kept_with_fw_unknown():
    con = _wh([], [("MUN:BBB", 2021, 1_000_00)])
    r = _row(con, "MUN:BBB", 2021)
    assert r["status"] == "fw_unknown" and r["fw"] is None and r["share"] is None and r["denom"] == 1_000_00


def test_change_uses_the_prior_year_only():
    con = _wh([("MUN:AAA", 2018, 10_00), ("MUN:AAA", 2019, 4_00), ("MUN:AAA", 2021, 7_00)], [])
    assert _row(con, "MUN:AAA", 2018)["change"] is None          # 2017 is out of range
    assert _row(con, "MUN:AAA", 2019)["change"] == -6_00          # negative change is kept as cents
    assert _row(con, "MUN:AAA", 2021)["change"] is None          # 2020 is unknown: no change, never a jump from 0


def test_national_share_leaves_hidden_rows_out_of_both_parts():
    con = _wh([("MUN:AAA", 2020, 1_00), ("MUN:BBB", 2020, 2_00), ("MUN:CCC", 2020, 500_00), ("MUN:AAA", 2019, 9_00)],
              [("MUN:AAA", 2020, 100_00), ("MUN:AAA", 2021, 100_00), ("MUN:AAA", 2019, 100_00),
               ("MUN:BBB", 2020, 300_00), ("MUN:BBB", 2021, 300_00),
               ("MUN:CCC", 2020, 1_00), ("MUN:CCC", 2021, 900_00)])            # CCC 2020: incomplete (1 vs 900)
    cols = ("n_rows", "n_fw_known", "n_share_known", "n_share_hidden", "fw_total_cents", "fw_share_base_cents",
            "denom_share_base_cents", "national_share_status", "national_share_pct")
    n = dict(zip(cols, con.execute(f"SELECT {', '.join(cols)} FROM marts.fw_national WHERE fye = 2020").fetchone()))
    # CCC's R500.00 is in the total, but neither its F&W nor its R1.00 of spending is in the share
    assert n == {"n_rows": 3, "n_fw_known": 3, "n_share_known": 2, "n_share_hidden": 1, "fw_total_cents": 503_00,
                 "fw_share_base_cents": 3_00, "denom_share_base_cents": 400_00, "national_share_status": "ok",
                 "national_share_pct": Decimal("0.7500")}
    y19 = con.execute("SELECT fw_total_cents, national_share_status, national_share_pct, n_share_hidden "
                      "FROM marts.fw_national WHERE fye = 2019").fetchone()
    assert y19 == (9_00, "denominator_incomplete_year", None, 1)


def test_national_share_with_no_base():
    con = _wh([("MUN:AAA", 2022, 5)], [("MUN:AAA", 2022, 100)])               # only row: no reference year
    assert con.execute("SELECT national_share_status, national_share_pct FROM marts.fw_national WHERE fye = 2022").fetchone() \
        == ("no_base", None)


def test_mart_never_reads_irregular_or_unauthorised():
    sql = SQL.read_text()
    assert "uifw_type = 'fruitless_wasteful'" in sql
    assert "'irregular'" not in sql and "'unauthorised'" not in sql
    con = _wh([("MUN:AAA", 2020, 7)], [("MUN:AAA", 2020, 100), ("MUN:AAA", 2021, 100)])
    assert con.execute("SELECT sum(fw_cents) FROM marts.fw_metric").fetchone()[0] == 7


# ---- data-quality checks ---------------------------------------------------------------------------------------

def _dq(con):
    return {n: int(con.execute(sql).fetchone()[0] or 0) for n, _, sql in dq.fw_checks()}


def _clean():
    """Every status at least once: incomplete year, no reference, incomplete, over 100, ok, unknowns, not positive."""
    return _wh([("MUN:AAA", 2019, 0), ("MUN:AAA", 2020, 3), ("MUN:AAA", 2021, 4), ("MUN:AAA", 2022, 1),
                ("MUN:BBB", 2020, None), ("MUN:BBB", 2023, 5), ("MUN:CCC", 2020, 500), ("MUN:CCC", 2022, 1),
                ("MUN:DDD", 2023, 1)],
               [("MUN:AAA", 2019, 50), ("MUN:AAA", 2020, 2_000_000), ("MUN:AAA", 2021, 2_000_000), ("MUN:AAA", 2022, 10),
                ("MUN:BBB", 2020, 10), ("MUN:BBB", 2023, 0), ("MUN:CCC", 2020, 100), ("MUN:CCC", 2021, 100), ("MUN:CCC", 2024, 7),
                ("MUN:DDD", 2023, 100)], bodies=("MUN:AAA", "MUN:BBB", "MUN:CCC", "MUN:DDD"))


def test_dq_checks_pass_on_a_clean_mart():
    con = _clean()
    got = set(r[0] for r in con.execute("SELECT DISTINCT share_status FROM marts.fw_metric").fetchall())
    assert got == set(SHARE_STATUS)
    res = _dq(con)
    info = {"fw_share_guarded_info", "fw_agsa_reconcile_info"}
    assert {k: v for k, v in res.items() if k not in info} == {k: 0 for k in res if k not in info}
    assert res["fw_share_guarded_info"] == con.execute(
        "SELECT count(*) FROM marts.fw_metric WHERE fye >= 2020 AND share_status IN "
        "('denominator_no_reference', 'denominator_incomplete', 'share_over_100')").fetchone()[0] > 0
    sev = {n: s for n, s, _ in dq.fw_checks()}
    assert sev["fw_share_guarded_info"] == "warn" and sev["fw_agsa_reconcile_info"] == "warn"
    assert all(s == "error" for n, s in sev.items() if not n.endswith("_info"))


def test_dq_checks_are_part_of_the_build_suite():
    names = {n for n, _, _ in dq.checks()}
    assert {n for n, _, _ in dq.fw_checks()} <= names
    assert dq.MIN_ROWS["marts.fw_metric"] == 1_000


def test_agsa_check_reports_the_real_mismatch_count():
    bodies = tuple(f"MUN:B{i:02d}" for i in range(60))
    con = _wh([(b, 2024, 100_000_00) for b in bodies], [], bodies=bodies)
    for i, b in enumerate(bodies):
        off = 5_000_001 if i == 0 else (5_000_000 if i == 1 else 0)          # one row just outside R50,000.00, one on the edge
        con.execute("INSERT INTO curated.agsa_uifw VALUES ('MFMA', 'fruitless_wasteful', 'Financial audits (x)', 2024, ?, ?)",
                    [100_000_00 + off, b])
    con.execute("INSERT INTO curated.agsa_uifw VALUES ('MFMA', 'fruitless_wasteful', 'Small auditees', 2024, 1, 'MUN:B02')")
    # 1 of 60 is under the old 2% gate, which reported 0; the check now reports the real count
    assert _dq(con)["fw_agsa_reconcile_info"] == 1


@pytest.mark.parametrize("tamper,check", [
    ("UPDATE marts.fw_metric SET fw_share_pct = fw_share_pct + 0.0001 WHERE share_status = 'ok'", "fw_share_matches_inputs"),
    ("UPDATE marts.fw_metric SET fw_share_pct = 0 WHERE share_status <> 'ok'", "fw_share_only_when_ok"),
    ("UPDATE marts.fw_metric SET fw_cents = fw_cents + 1 WHERE fye = 2020 AND gov_body_id = 'MUN:AAA'", "fw_totals_match_source"),
    ("DELETE FROM marts.fw_metric WHERE gov_body_id = 'MUN:AAA' AND fye = 2020", "fw_rows_complete"),
    ("UPDATE marts.fw_metric SET fye = 2017 WHERE gov_body_id = 'MUN:AAA' AND fye = 2020", "fw_years_in_range"),
    ("UPDATE marts.fw_metric SET share_status = 'unknown'", "fw_share_status_valid"),
    ("UPDATE marts.fw_national SET fw_total_cents = fw_total_cents + 1", "fw_national_matches_metric"),
    ("UPDATE marts.fw_national SET n_share_hidden = n_share_hidden + 1", "fw_national_matches_metric"),
    ("UPDATE marts.fw_national SET national_share_status = 'ok', national_share_pct = 1 WHERE fye = 2019", "fw_national_share_rule"),
    ("UPDATE marts.fw_metric SET source_sha256 = 'b'", "lineage_resolves:fw_metric"),
    ("UPDATE marts.fw_metric SET share_status = 'ok', fw_share_pct = 0 WHERE fye = 2019", "fw_no_share_in_incomplete_years"),
    ("UPDATE marts.fw_metric SET share_status = 'denominator_incomplete' WHERE fye = 2019", "fw_incomplete_year_status"),
    ("UPDATE marts.fw_metric SET share_status = 'ok', fw_share_pct = 0 WHERE share_status = 'denominator_incomplete'",
     "fw_completeness_rule"),
    ("UPDATE marts.fw_metric SET share_status = 'denominator_incomplete', fw_share_pct = NULL WHERE share_status = 'ok'",
     "fw_completeness_rule"),
    ("UPDATE marts.fw_metric SET denom_ref_median = denom_ref_median + 1 WHERE denom_ref_median IS NOT NULL",
     "fw_reference_recomputed"),
])
def test_dq_checks_catch_a_broken_mart(tamper, check):
    con = _wh([("MUN:AAA", 2019, 2), ("MUN:AAA", 2020, 3), ("MUN:AAA", 2021, 4), ("MUN:AAA", 2022, 1)],
              [("MUN:AAA", 2019, 9), ("MUN:AAA", 2020, 2_000_000), ("MUN:AAA", 2021, 2_000_000), ("MUN:AAA", 2022, 10),
               ("MUN:BBB", 2020, None)])
    assert _dq(con)[check] == 0
    con.execute(tamper)
    assert _dq(con)[check] > 0


# ---- synthetic full build and export (T8) ----------------------------------------------------------------------

def test_synthetic_build_has_the_mart_and_passes_dq(paths):
    con = duckdb.connect(str(paths.warehouse), read_only=True)
    try:
        rows = con.execute("SELECT gov_body_id, fye, share_status, fw_share_pct FROM marts.fw_metric ORDER BY 1, 2").fetchall()
        res = {r[0]: r[1] for r in con.execute("SELECT test_name, status FROM ops.dq_result").fetchall()}
    finally:
        con.close()
    assert rows and all(FW_FYE_MIN <= y <= FW_FYE_MAX for _, y, _, _ in rows)
    # synthetic Testville: F&W is 0 in 2021-2024; audited spending only for 2023 and 2024 (each the other's reference)
    tst = {y: (s, p) for b, y, s, p in rows if b == "MUN:TST"}
    assert tst[2021] == ("denominator_unknown", None) and tst[2024][0] == "ok" and tst[2024][1] == 0
    for n, _, _ in dq.fw_checks():
        assert res[n] in ("pass", "warn"), n


def test_export_adds_only_share_status_and_change(paths):
    from thusa import publish_data as pd
    con = duckdb.connect(str(paths.warehouse), read_only=True)
    try:
        mun = pd.municipalities(con, pd.SourceRefs(con))
    finally:
        con.close()
    assert mun["fw_years"] == [FW_FYE_MIN, FW_FYE_MAX]
    assert any("fw (CHG-2026-062)" in a for a in mun["about"])
    assert any("incomplete at the source" in a for a in mun["about"]) and any("Completeness check" in a for a in mun["about"])
    seen = 0
    for m in mun["municipalities"]:
        for y, d in m["years"].items():
            if "fw" in d:
                seen += 1
                assert FW_FYE_MIN <= int(y) <= FW_FYE_MAX
                assert set(d["fw"]) == {"share_pct", "status", "change"}          # T4: no combined UIFW total
                assert d["fw"]["status"] in SHARE_STATUS
                assert (d["fw"]["share_pct"] is None) == (d["fw"]["status"] != "ok")
                assert int(y) >= FW_SHARE_FYE_MIN or d["fw"]["share_pct"] is None
                assert d["fw"]["share_pct"] is None or isinstance(d["fw"]["share_pct"], float)   # a plain number, not a string
    assert seen
    for n in mun["fw_national"]:
        assert set(n) == {"fye", "fy", "fw", "n_fw", "n_share", "n_hidden", "fw_share_base", "exp_share_base", "share_pct", "status"}
        assert n["status"] in NATIONAL_STATUS and (n["share_pct"] is None) == (n["status"] != "ok")
    blob = json.dumps(mun)
    assert not re.search(r'"\d{1,3}(,\d{3})+(\.\d+)?"', blob)                    # data stays plain decimals
    pd.assert_public_safe(mun, set(), "municipalities.json")


# ---- page: T6 format, T7 wording, no ranking -------------------------------------------------------------------

def _fw_block() -> str:
    a, b = PAGE.index("/* fw:begin"), PAGE.index("/* fw:end */")
    return PAGE[a:b]


def test_page_route_nav_and_dashboard_check_mirror():
    assert 'href="#/fw"' in PAGE and "[/^#\\/fw$/, (m, p) => vFw(p)]" in PAGE
    dc = (ROOT / "scripts" / "dashboard_check.py").read_text(encoding="utf-8")
    assert 'r"^#/fw$"' in dc and '("fruitless-wasteful", "#/fw")' in dc
    assert "fwMuniSection(mun, m)," in PAGE


def test_page_list_is_alphabetical_and_not_a_ranking():
    blk = _fw_block()
    sorts = re.findall(r"\.sort\((.*)", blk)
    assert len(sorts) == 1 and "localeCompare" in sorts[0] and "a.m.name" in sorts[0]
    assert "share_pct -" not in blk and "fruitless_wasteful -" not in blk
    low = blk.lower()
    for w in ("largest first", "top 10", "top ten", "worst", "best", "league"):
        assert w not in low, w


def test_page_wording_is_neutral():
    blk = _fw_block()
    assert 'const FW_NOT_THEFT = "It is not proof of theft or corruption.";' in blk
    rest = blk.replace('"It is not proof of theft or corruption."', "").replace("FW_NOT_THEFT", "").replace("It is not a ranking", "").replace("not a ranking", "")
    low = rest.lower()
    for w in ("looted", "stolen", "theft", "corrupt", "fraud", "ranking", "rank"):
        assert w not in low, w


def test_page_never_adds_irregular_or_unauthorised():
    blk = _fw_block()
    assert ".irregular" not in blk and ".unauthorised" not in blk


def test_page_uses_central_formatters_only():
    blk = _fw_block()
    for bad in ("toFixed", "toLocaleString", "Math.round", "toPrecision", '+ "%"'):
        assert bad not in blk, bad
    assert "randCell(" in blk and "pctPoints(" in blk
    assert "rand(" not in re.sub(r"randCell\(|_rand\"", "", blk).replace("fwShareText(", "")


def test_page_states_the_left_out_years():
    blk = _fw_block()
    assert "2017/18 to 2023/24" in blk and "2011/12 to 2016/17" in blk and "not checked" in blk


def _node(expr: str):
    if not shutil.which("node"):
        if os.environ.get("PF_SKIP_NODE_PARITY") == "1":
            pytest.skip("node not installed and PF_SKIP_NODE_PARITY=1")
        pytest.fail("node is required (set PF_SKIP_NODE_PARITY=1 to opt out)")
    a, b = PAGE.index("/* format:begin */"), PAGE.index("/* format:end */")
    js = PAGE[a:b] + "\nconst el = () => null, unknown = () => null;\n" + _fw_block() + "\nconsole.log(JSON.stringify(" + expr + "))\n"
    return json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)


def test_js_share_text():
    got = _node("""[
      fwShareText({fw: {status: "ok", share_pct: 0.187}, uifw: {fruitless_wasteful: 5}}),
      fwShareText({fw: {status: "ok", share_pct: 0}, uifw: {fruitless_wasteful: 0}}),
      fwShareText({fw: {status: "ok", share_pct: 0}, uifw: {fruitless_wasteful: 100}}),
      fwShareText({fw: {status: "denominator_unknown", share_pct: null}, uifw: {fruitless_wasteful: 100}}),
      fwShareText({fw: {status: "ok", share_pct: 1234.5}, uifw: {fruitless_wasteful: 1}}),
      fwShareText({}),
      fwShareCsv({fw: {status: "share_over_100", share_pct: null}}),
      fwStatusCsv({})]""")
    assert got == ["0.187%", "0%", "under 0.0001%", None, "1,234.5%", None, None, "no_data"]


def test_js_axis_ticks_are_clean_multiples():
    got = _node("[0,1,2,3,4].map(k => fwTick(k, fwNiceStep(1.4262))).concat([0,1,2,3].map(k => fwTick(k, fwNiceStep(0.03))))")
    assert got == [0, 0.5, 1, 1.5, 2, 0, 0.01, 0.02, 0.03]


def test_page_explains_every_hidden_share_reason():
    blk = _fw_block()
    keys = set(re.findall(r"\b(\w+): \"", blk[blk.index("const FW_STATUS"):blk.index("const FW_NATIONAL_STATUS")]))
    assert keys == set(SHARE_STATUS) - {"ok"}
    nat = blk[blk.index("const FW_NATIONAL_STATUS"):blk.index("const FW_NOT_THEFT")]
    assert set(re.findall(r"\b(\w+): \"", nat)) == set(NATIONAL_STATUS) - {"ok"}
    assert "For 2017/18 and 2018/19 we show the amounts but no share." in blk
    assert "under half of the usual (median) figure" in blk and "no other year to compare with" in blk
    assert "left out of both parts of the share" in blk
