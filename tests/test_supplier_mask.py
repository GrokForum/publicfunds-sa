"""CHG-2026-067 item 4: supplier values that carry a personal title are masked in the award files.

Rule: after removing outer brackets, a title (Mr, Mrs, Ms, Miss, Mx, Dr, Prof, Adv; any case, optional full stop), a space and
more text, and no organisation word (whole words, case-insensitive; `Inc` does not count when a title leads). Official
municipality names are never masked. The mask is the first letter or digit (upper case), five asterisks, the last letter or
digit (lower case). Masked rows get doc = null and keep ocid, award_id, reference and src. A fail-closed scan in the export
refuses to write if a titled value reaches an award row. All names below are invented.
"""
import json
import shutil

import duckdb
import pytest

from thusa import publish_data as pdx
from thusa.settings import get_paths


# ------------------------------------------------------------------ the rule
@pytest.mark.parametrize("value,mask", [
    ("DR AB Example", "D*****e"),
    ("(DR AB Example)", "D*****e"),
    ("Mrs. Q Z", "M*****z"),
    ("DR AB Example Inc", "D*****c"),           # the Inc exception: a personal-liability company in a practitioner's name
    ("dr ab example inc.", "D*****c"),
    ("Prof X Example", "P*****e"),
    ("Adv. Y Example", "A*****e"),
    ("Mx Z 2", "M*****2"),
    ("[Ms Q Example]", "M*****e"),
])
def test_titled_values_are_masked(value, mask):
    assert pdx.mask_titled_person(value) == mask
    assert len(mask) == 7


@pytest.mark.parametrize("value", [
    "ME Example Builders",                       # invented company name: "ME" is not a title
    "DRYDOCK EXAMPLE TRADING",                   # no title (Dr inside a longer word)
    "Dr Example Local Municipality",             # organisation word
    "Dr Example Holdings",                       # organisation word
    "DR AB Example (Pty) Ltd",
    "Dr Example CC",
    "Mr Example Joint Venture",
    "Dr Example JV",
    "Dr Example t/a Example Services",
    "Dr Example Enterprises",
    "(name withheld)",
    "Dr",                                        # a title with no more text
    "Mrexample Supplies",
    "",
    None,
])
def test_not_masked(value):
    assert pdx.mask_titled_person(value) == value


def test_org_words_match_as_whole_words_case_insensitive():
    assert pdx.is_titled_person("Dr Example Incubator")          # "Inc" inside a longer word is not an organisation word
    assert pdx.is_titled_person("Dr Ccembe Example")              # "CC" inside a longer word
    assert not pdx.is_titled_person("dr example pty ltd")
    assert not pdx.is_titled_person("DR EXAMPLE TRUST")


def test_official_municipality_names_are_not_masked():
    official = frozenset({"dr example", "dr example local municipality"})
    assert pdx.mask_titled_person("Dr Example", official) == "Dr Example"
    assert pdx.mask_titled_person("DR  EXAMPLE", official) == "DR  EXAMPLE"
    assert pdx.mask_titled_person("Dr Other Example", official) == "D*****e"


def test_mask_value_short_stems_and_length():
    assert pdx.mask_value("-") == "*******"
    assert pdx.mask_value("x") == "*******"
    assert pdx.mask_value("") == "*******"
    assert pdx.mask_value("ab") == "A*****b"
    for v in ("ab", "DR AB Example", "Mrs. Q Z", "x"):
        assert len(pdx.mask_value(v)) == 7


# ------------------------------------------------------------------ the export (a copy of the synthetic warehouse)
@pytest.fixture
def mod_paths(synth_root, tmp_path, monkeypatch):
    """A copy of the synthetic warehouse with invented titled suppliers, a district and a municipality whose name begins
    with 'Dr'. The real warehouse is never touched."""
    root = tmp_path / "root"
    (root / "data").mkdir(parents=True)
    shutil.copy(get_paths(synth_root).warehouse, root / "data" / "thusa.duckdb")
    monkeypatch.setenv("THUSA_REVIEW_DB", str(tmp_path / "review.sqlite"))
    monkeypatch.setenv("THUSA_ROOT", str(root))
    con = duckdb.connect(str(root / "data" / "thusa.duckdb"))
    ids = [r[0] for r in con.execute("SELECT award_id FROM curated.award WHERE doc_url IS NOT NULL ORDER BY award_id LIMIT 4").fetchall()]
    for aid, name in zip(ids, ["DR AB Example", "(DR AB Example Two)", "DR AB Example Inc", "ME Example Builders"]):
        con.execute("UPDATE curated.award SET supplier_name = ? WHERE award_id = ?", [name, aid])
    con.execute("UPDATE curated.gov_body SET name = 'Dr Example' WHERE gov_body_id = 'MUN:OLD'")
    con.execute("UPDATE curated.gov_body SET body_type = 'district' WHERE gov_body_id = 'MUN:TS1'")
    oid = con.execute("SELECT award_id FROM curated.award WHERE award_id NOT IN (SELECT unnest(?)) AND doc_url IS NOT NULL "
                      "ORDER BY award_id LIMIT 1", [ids]).fetchone()[0]
    con.execute("UPDATE curated.award SET supplier_name = 'Dr Example' WHERE award_id = ?", [oid])
    con.close()
    return get_paths(root), ids, oid


def _rows(out):
    rows = []
    for p in sorted(out.glob("awards-*.json")):
        f = json.loads(p.read_text())
        assert f["columns"][5] == "supplier" and f["columns"][11] == "doc" and f["columns"][8] == "reference"
        rows += f["rows"]
    return rows


def test_export_masks_rows_drops_doc_and_keeps_ids(mod_paths, tmp_path):
    paths, ids, oid = mod_paths
    out = tmp_path / "pd"
    pdx.export(paths, out)
    rows = {r[1]: r for r in _rows(out)}
    for aid, mask in zip(ids, ["D*****e", "D*****o", "D*****c"]):
        r = rows[aid]
        assert r[5] == mask and r[11] is None, (aid, r)
        assert r[0] and r[1] == aid and r[8] is not None and r[12]          # ocid, award_id, reference and src stay
    assert rows[ids[3]][5] == "ME Example Builders" and rows[ids[3]][11] is not None       # unmasked row keeps doc
    assert rows[oid][5] == "Dr Example" and rows[oid][11] is not None                       # official municipality name
    blob = "\n".join(p.read_text() for p in out.glob("*.json"))
    assert "Example Two" not in blob and "DR AB Example" not in blob
    mun = json.loads((out / "municipalities.json").read_text())
    assert [m["name"] for m in mun["municipalities"] if m["id"] == "MUN:OLD"] == ["Dr Example"]   # never masked


def test_must_fail_export_refuses_when_the_mask_is_a_no_op(mod_paths, tmp_path, monkeypatch):
    paths, _, _ = mod_paths
    out = tmp_path / "pd"
    monkeypatch.setattr(pdx, "mask_titled_person", lambda name, official=frozenset(): name)
    with pytest.raises(pdx.UnsafeExport, match="personal title is not masked"):
        pdx.export(paths, out)
    assert not out.exists() or not list(out.glob("*.json"))             # nothing written


def test_must_fail_scan_refuses_a_masked_row_with_a_doc_link():
    cols = ["ocid", "award_id", "date", "date_basis", "buyer", "supplier", "value", "value_note", "reference", "method",
            "category", "doc", "src"]
    good = {2024: {"columns": cols, "rows": [["o", "a", None, "release", "b", "D*****e", None, None, "r", None, None, None, "s"]]}}
    pdx.assert_no_titled_supplier(good)
    bad = {2024: {"columns": cols, "rows": [["o", "a", None, "release", "b", "D*****e", None, None, "r", None, None, "blob|f", "s"]]}}
    with pytest.raises(pdx.UnsafeExport, match="still has a doc link"):
        pdx.assert_no_titled_supplier(bad)
    titled = {2024: {"columns": cols, "rows": [["o", "a", None, "release", "b", "Dr AB Example", None, None, "r", None, None, None, "s"]]}}
    with pytest.raises(pdx.UnsafeExport, match="personal title is not masked"):
        pdx.assert_no_titled_supplier(titled)


def test_district_profile_and_counts_in_export(mod_paths, tmp_path):
    paths, _, _ = mod_paths
    out = tmp_path / "pd"
    pdx.export(paths, out)
    mun = {m["id"]: m for m in json.loads((out / "municipalities.json").read_text())["municipalities"]}
    assert mun["MUN:TS1"]["profile"] == "https://municipalmoney.gov.za/profiles/district-TS1/"
    assert mun["MUN:TST"]["profile"] == "https://municipalmoney.gov.za/profiles/municipality-TST/"
    man = json.loads((out / "manifest.json").read_text())
    c = man["counts"]
    assert c["municipalities_current"] + c["municipalities_ceased"] == c["municipalities"]
    assert c["municipalities_ceased"] == sum(1 for m in mun.values() if m["exists_to"])
