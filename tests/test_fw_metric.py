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
from thusa.fw_metric import FW_FYE_MAX, FW_FYE_MIN, SHARE_STATUS

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

def test_sql_year_range_matches_python_constants():
    sql = SQL.read_text()
    assert sql.count(f"BETWEEN {FW_FYE_MIN} AND {FW_FYE_MAX}") == 2
    assert (FW_FYE_MIN, FW_FYE_MAX) == (2018, 2024)


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
    (101, 100, "share_over_100", None),                     # F&W larger than spending: not shown
    (9_000_000_000_000_000, 9_100_000_000_000_000, "ok", Decimal("98.9010")),   # no overflow with very large cents
])
def test_share_status_and_cut_not_rounded(fw, den, status, share):
    con = _wh([("MUN:AAA", 2020, fw)] if fw is not None else [("MUN:AAA", 2020, None)],
              [("MUN:AAA", 2020, den)] if den is not None else [])
    r = _row(con, "MUN:AAA", 2020)
    assert r["status"] == status
    assert r["share"] == share
    assert status in SHARE_STATUS


def test_years_outside_2018_2024_and_non_municipal_bodies_are_left_out():
    con = _wh([("MUN:AAA", 2017, 5), ("MUN:AAA", 2018, 5), ("MUN:AAA", 2024, 5), ("MUN:AAA", 2025, 5), ("NAT:dept", 2020, 5)],
              [("MUN:AAA", 2012, 10), ("MUN:AAA", 2025, 10)])
    got = con.execute("SELECT gov_body_id, fye FROM marts.fw_metric ORDER BY fye").fetchall()
    assert got == [("MUN:AAA", 2018), ("MUN:AAA", 2024)]


def test_denominator_only_row_is_kept_with_fw_unknown():
    con = _wh([], [("MUN:BBB", 2021, 1_000_00)])
    r = _row(con, "MUN:BBB", 2021)
    assert r["status"] == "fw_unknown" and r["fw"] is None and r["share"] is None and r["denom"] == 1_000_00


def test_change_uses_the_prior_year_only():
    con = _wh([("MUN:AAA", 2018, 10_00), ("MUN:AAA", 2019, 4_00), ("MUN:AAA", 2021, 7_00)], [])
    assert _row(con, "MUN:AAA", 2018)["change"] is None          # 2017 is out of range
    assert _row(con, "MUN:AAA", 2019)["change"] == -6_00          # negative change is kept as cents
    assert _row(con, "MUN:AAA", 2021)["change"] is None          # 2020 is unknown: no change, never a jump from 0


def test_national_view_sums_and_share():
    con = _wh([("MUN:AAA", 2020, 1_00), ("MUN:BBB", 2020, 2_00), ("MUN:CCC", 2020, 500_00)],
              [("MUN:AAA", 2020, 100_00), ("MUN:BBB", 2020, 300_00), ("MUN:CCC", 2020, 100_00)])   # CCC: share over 100
    n = con.execute("SELECT n_rows, n_fw_known, n_share_known, fw_total_cents, fw_share_base_cents, denom_share_base_cents, "
                    "national_share_pct FROM marts.fw_national WHERE fye = 2020").fetchone()
    assert n == (3, 3, 2, 503_00, 3_00, 400_00, Decimal("0.7500"))


def test_mart_never_reads_irregular_or_unauthorised():
    sql = SQL.read_text()
    assert "uifw_type = 'fruitless_wasteful'" in sql
    assert "'irregular'" not in sql and "'unauthorised'" not in sql
    con = _wh([("MUN:AAA", 2020, 7)], [("MUN:AAA", 2020, 100)])
    assert con.execute("SELECT sum(fw_cents) FROM marts.fw_metric").fetchone()[0] == 7


# ---- data-quality checks ---------------------------------------------------------------------------------------

def _dq(con):
    return {n: int(con.execute(sql).fetchone()[0] or 0) for n, _, sql in dq.fw_checks()}


def test_dq_checks_pass_on_a_clean_mart():
    con = _wh([("MUN:AAA", 2019, 0), ("MUN:AAA", 2020, 3), ("MUN:BBB", 2020, None), ("MUN:CCC", 2020, 500)],
              [("MUN:AAA", 2020, 2_000_000), ("MUN:BBB", 2020, 10), ("MUN:CCC", 2020, 100), ("MUN:CCC", 2021, 0)])
    res = _dq(con)
    assert {k: v for k, v in res.items() if k != "fw_share_over_100_info"} == {k: 0 for k in res if k != "fw_share_over_100_info"}
    assert res["fw_share_over_100_info"] == 1
    sev = {n: s for n, s, _ in dq.fw_checks()}
    assert sev["fw_share_over_100_info"] == "warn" and sev["fw_agsa_reconcile_info"] == "warn"
    assert all(s == "error" for n, s in sev.items() if not n.endswith("_info"))


def test_dq_checks_are_part_of_the_build_suite():
    names = {n for n, _, _ in dq.checks()}
    assert {n for n, _, _ in dq.fw_checks()} <= names
    assert dq.MIN_ROWS["marts.fw_metric"] == 1_000


@pytest.mark.parametrize("tamper,check", [
    ("UPDATE marts.fw_metric SET fw_share_pct = fw_share_pct + 0.0001 WHERE share_status = 'ok'", "fw_share_matches_inputs"),
    ("UPDATE marts.fw_metric SET fw_share_pct = 0 WHERE share_status = 'denominator_unknown'", "fw_share_only_when_ok"),
    ("UPDATE marts.fw_metric SET fw_cents = fw_cents + 1 WHERE fye = 2020 AND gov_body_id = 'MUN:AAA'", "fw_totals_match_source"),
    ("DELETE FROM marts.fw_metric WHERE gov_body_id = 'MUN:AAA' AND fye = 2020", "fw_rows_complete"),
    ("UPDATE marts.fw_metric SET fye = 2017 WHERE gov_body_id = 'MUN:AAA' AND fye = 2020", "fw_years_in_range"),
    ("UPDATE marts.fw_metric SET share_status = 'unknown'", "fw_share_status_valid"),
    ("UPDATE marts.fw_national SET fw_total_cents = fw_total_cents + 1", "fw_national_matches_metric"),
    ("UPDATE marts.fw_metric SET source_sha256 = 'b'", "lineage_resolves:fw_metric"),
])
def test_dq_checks_catch_a_broken_mart(tamper, check):
    con = _wh([("MUN:AAA", 2020, 3), ("MUN:AAA", 2021, 4)],
              [("MUN:AAA", 2020, 2_000_000), ("MUN:BBB", 2020, None)])
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
    # synthetic Testville: F&W is 0 in 2021-2024; audited spending only for 2023 and 2024
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
    seen = 0
    for m in mun["municipalities"]:
        for y, d in m["years"].items():
            if "fw" in d:
                seen += 1
                assert FW_FYE_MIN <= int(y) <= FW_FYE_MAX
                assert set(d["fw"]) == {"share_pct", "status", "change"}          # T4: no combined UIFW total
                assert d["fw"]["status"] in SHARE_STATUS
                assert (d["fw"]["share_pct"] is None) == (d["fw"]["status"] != "ok")
                assert d["fw"]["share_pct"] is None or isinstance(d["fw"]["share_pct"], float)   # a plain number, not a string
    assert seen
    for n in mun["fw_national"]:
        assert set(n) == {"fye", "fy", "fw", "n_fw", "n_share", "fw_share_base", "exp_share_base", "share_pct"}
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
